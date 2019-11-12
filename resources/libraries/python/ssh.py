# Copyright (c) 2019 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Library for SSH connection management."""


import socket

from io import StringIO, BytesIO
from time import time, sleep

from paramiko import RSAKey, SSHClient, AutoAddPolicy
from paramiko.ssh_exception import SSHException, NoValidConnectionsError
from robot.api import logger
from scp import SCPClient, SCPException

from resources.libraries.python.OptionString import OptionString

__all__ = [
    u"exec_cmd", u"exec_cmd_no_error", u"SSH", u"SSHTimeout", u"scp_node"
]

# TODO: load priv key


class SSHTimeout(Exception):
    """This exception is raised when a timeout occurs."""
    pass


class SSH(object):
    """Contains methods for managing and using SSH connections."""

    __MAX_RECV_BUF = 10 * 1024 * 1024
    __existing_connections = dict()

    def __init__(self):
        self._ssh = None
        self._node = None

    @staticmethod
    def _node_hash(node):
        """Get IP address and port hash from node dictionary.

        :param node: Node in topology.
        :type node: dict
        :returns: IP address and port for the specified node.
        :rtype: int
        """

        return hash(frozenset([node[u"host"], node[u"port"]]))

    def connect(self, node, attempts=5):
        """Connect to node prior to running exec_command or scp.

        If there already is a connection to the node, this method reuses it.

        :param node: Node in topology.
        :param attempts: Number of reconnect attempts.
        :type node: dict
        :type attempts: int
        :raises IOError: If cannot connect to host.
        """
        self._node = node
        node_hash = self._node_hash(node)
        if node_hash in SSH.__existing_connections:
            self._ssh = SSH.__existing_connections[node_hash]
            if self._ssh.get_transport().is_active():
                logger.debug(f"Reusing SSH: {self._ssh}")
            else:
                if attempts > 0:
                    self._reconnect(attempts-1)
                else:
                    raise IOError(f"Cannot connect to {node['host']}")
        else:
            try:
                start = time()
                pkey = None
                if u"priv_key" in node:
                    pkey = RSAKey.from_private_key(StringIO(node[u"priv_key"]))

                self._ssh = SSHClient()
                self._ssh.set_missing_host_key_policy(AutoAddPolicy())

                self._ssh.connect(
                    node[u"host"], username=node[u"username"],
                    password=node.get(u"password"), pkey=pkey,
                    port=node[u"port"]
                )

                self._ssh.get_transport().set_keepalive(10)

                SSH.__existing_connections[node_hash] = self._ssh
                logger.debug(
                    f"New SSH to {self._ssh.get_transport().getpeername()} "
                    f"took {time() - start} seconds: {self._ssh}"
                )
            except SSHException as exc:
                raise IOError(f"Cannot connect to {node[u'host']}") from exc
            except NoValidConnectionsError as err:
                raise IOError(
                        f"Unable to connect to port {node[u'port']} on "
                        f"{node[u'host']}"
                    ) from err

    def disconnect(self, node=None):
        """Close SSH connection to the node.

        :param node: The node to disconnect from. None means last connected.
        :type node: dict or None
        """
        if node is None:
            node = self._node
        if node is None:
            return
        node_hash = self._node_hash(node)
        if node_hash in SSH.__existing_connections:
            logger.debug(
                f"Disconnecting peer: {node[u'host']}, {node[u'port']}"
            )
            ssh = SSH.__existing_connections.pop(node_hash)
            ssh.close()

    def _reconnect(self, attempts=0):
        """Close the SSH connection and open it again.

        :param attempts: Number of reconnect attempts.
        :type attempts: int
        """
        node = self._node
        self.disconnect(node)
        self.connect(node, attempts)
        logger.debug(
            f"Reconnecting peer done: {node[u'host']}, {node[u'port']}"
        )

    def exec_command(self, cmd, timeout=10, log_stdout_err=True):
        """Execute SSH command on a new channel on the connected Node.

        :param cmd: Command to run on the Node.
        :param timeout: Maximal time in seconds to wait until the command is
            done. If set to None then wait forever.
        :param log_stdout_err: If True, stdout and stderr are logged. stdout
            and stderr are logged also if the return code is not zero
            independently of the value of log_stdout_err.
        :type cmd: str or OptionString
        :type timeout: int
        :type log_stdout_err: bool
        :returns: return_code, stdout, stderr
        :rtype: tuple(int, str, str)
        :raises SSHTimeout: If command is not finished in timeout time.
        """
        if isinstance(cmd, (list, tuple)):
            cmd = OptionString(cmd)
        cmd = str(cmd)
        stdout = StringIO()
        stderr = StringIO()
        try:
            chan = self._ssh.get_transport().open_session(timeout=5)
            peer = self._ssh.get_transport().getpeername()
        except (AttributeError, SSHException):
            self._reconnect()
            chan = self._ssh.get_transport().open_session(timeout=5)
            peer = self._ssh.get_transport().getpeername()
        chan.settimeout(timeout)

        logger.trace(f"exec_command on {peer} with timeout {timeout}: {cmd}")

        start = time()
        chan.exec_command(cmd)
        while not chan.exit_status_ready() and timeout is not None:
            if chan.recv_ready():
                stdout.write(chan.recv(self.__MAX_RECV_BUF).decode(encoding='utf-16'))

            if chan.recv_stderr_ready():
                stderr.write(chan.recv_stderr(self.__MAX_RECV_BUF).decode(encoding='utf-16'))

            if time() - start > timeout:
                raise SSHTimeout(
                    f"Timeout exception during execution of command: {cmd}\n"
                    f"Current contents of stdout buffer: "
                    f"{stdout.getvalue()}\n"
                    f"Current contents of stderr buffer: "
                    f"{stderr.getvalue()}\n"
                )

            sleep(0.1)
        return_code = chan.recv_exit_status()

        while chan.recv_ready():
            stdout.write(chan.recv(self.__MAX_RECV_BUF).decode(encoding='utf-16'))

        while chan.recv_stderr_ready():
            stderr.write(chan.recv_stderr(self.__MAX_RECV_BUF).decode(encoding='utf-16'))

        end = time()
        logger.trace(f"exec_command on {peer} took {end-start} seconds")

        logger.trace(f"return RC {return_code}")
        if log_stdout_err or int(return_code):
            logger.trace(
                f"return STDOUT {stdout.getvalue()}"
            )
            logger.trace(
                f"return STDERR {stderr.getvalue()}"
            )
        return return_code, stdout.getvalue(), stderr.getvalue()

    def exec_command_sudo(
            self, cmd, cmd_input=None, timeout=30, log_stdout_err=True):
        """Execute SSH command with sudo on a new channel on the connected Node.

        :param cmd: Command to be executed.
        :param cmd_input: Input redirected to the command.
        :param timeout: Timeout.
        :param log_stdout_err: If True, stdout and stderr are logged.
        :type cmd: str
        :type cmd_input: str
        :type timeout: int
        :type log_stdout_err: bool
        :returns: return_code, stdout, stderr
        :rtype: tuple(int, str, str)

        :Example:

        >>> from ssh import SSH
        >>> ssh = SSH()
        >>> ssh.connect(node)
        >>> # Execute command without input (sudo -S cmd)
        >>> ssh.exec_command_sudo(u"ifconfig eth0 down")
        >>> # Execute command with input (sudo -S cmd <<< 'input')
        >>> ssh.exec_command_sudo(u"vpp_api_test", u"dump_interface_table")
        """
        if isinstance(cmd, (list, tuple)):
            cmd = OptionString(cmd)
        if cmd_input is None:
            command = f"sudo -E -S {cmd}"
        else:
            command = f"sudo -E -S {cmd} <<< \"{cmd_input}\""
        return self.exec_command(
            command, timeout, log_stdout_err=log_stdout_err
        )

    def exec_command_lxc(
            self, lxc_cmd, lxc_name, lxc_params=u"", sudo=True, timeout=30):
        """Execute command in LXC on a new SSH channel on the connected Node.

        :param lxc_cmd: Command to be executed.
        :param lxc_name: LXC name.
        :param lxc_params: Additional parameters for LXC attach.
        :param sudo: Run in privileged LXC mode. Default: privileged
        :param timeout: Timeout.
        :type lxc_cmd: str
        :type lxc_name: str
        :type lxc_params: str
        :type sudo: bool
        :type timeout: int
        :returns: return_code, stdout, stderr
        """
        command = f"lxc-attach {lxc_params} --name {lxc_name} -- /bin/sh " \
            f"-c \"{lxc_cmd}\""

        if sudo:
            command = f"sudo -E -S {command}"
        return self.exec_command(command, timeout)

    def interactive_terminal_open(self, time_out=45):
        """Open interactive terminal on a new channel on the connected Node.

        :param time_out: Timeout in seconds.
        :returns: SSH channel with opened terminal.

        .. warning:: Interruptingcow is used here, and it uses
           signal(SIGALRM) to let the operating system interrupt program
           execution. This has the following limitations: Python signal
           handlers only apply to the main thread, so you cannot use this
           from other threads. You must not use this in a program that
           uses SIGALRM itself (this includes certain profilers)
        """
        chan = self._ssh.get_transport().open_session()
        chan.get_pty()
        chan.invoke_shell()
        chan.settimeout(int(time_out))
        chan.set_combine_stderr(True)

        buf = u""
        while not buf.endswith((u":~# ", u":~$ ", u"~]$ ", u"~]# ")):
            try:
                chunk = chan.recv(self.__MAX_RECV_BUF)
                if not chunk:
                    break
                buf += chunk
                if chan.exit_status_ready():
                    logger.error(u"Channel exit status ready")
                    break
            except socket.timeout as exc:
                raise Exception(f"Socket timeout: {buf}") from exc
        return chan

    def interactive_terminal_exec_command(self, chan, cmd, prompt):
        """Execute command on interactive terminal.

        interactive_terminal_open() method has to be called first!

        :param chan: SSH channel with opened terminal.
        :param cmd: Command to be executed.
        :param prompt: Command prompt, sequence of characters used to
        indicate readiness to accept commands.
        :returns: Command output.

        .. warning:: Interruptingcow is used here, and it uses
           signal(SIGALRM) to let the operating system interrupt program
           execution. This has the following limitations: Python signal
           handlers only apply to the main thread, so you cannot use this
           from other threads. You must not use this in a program that
           uses SIGALRM itself (this includes certain profilers)
        """
        chan.sendall(f"{cmd}\n")
        buf = u""
        while not buf.endswith(prompt):
            try:
                chunk = chan.recv(self.__MAX_RECV_BUF)
                if not chunk:
                    break
                buf += chunk
                if chan.exit_status_ready():
                    logger.error(u"Channel exit status ready")
                    break
            except socket.timeout as exc:
                raise Exception(
                        f"Socket timeout during execution of command: {cmd}\n"
                        f"Buffer content:\n{buf}"
                    ) from exc
        tmp = buf.replace(cmd.replace(u"\n", u""), u"")
        for item in prompt:
            tmp.replace(item, u"")
        return tmp

    @staticmethod
    def interactive_terminal_close(chan):
        """Close interactive terminal SSH channel.

        :param chan: SSH channel to be closed.
        """
        chan.close()

    def scp(
            self, local_path, remote_path, get=False, timeout=30,
            wildcard=False):
        """Copy files from local_path to remote_path or vice versa.

        connect() method has to be called first!

        :param local_path: Path to local file that should be uploaded; or
        path where to save remote file.
        :param remote_path: Remote path where to place uploaded file; or
        path to remote file which should be downloaded.
        :param get: scp operation to perform. Default is put.
        :param timeout: Timeout value in seconds.
        :param wildcard: If path has wildcard characters. Default is false.
        :type local_path: str
        :type remote_path: str
        :type get: bool
        :type timeout: int
        :type wildcard: bool
        """
        if not get:
            logger.trace(
                f"SCP {local_path} to "
                f"{self._ssh.get_transport().getpeername()}:{remote_path}"
            )
        else:
            logger.trace(
                f"SCP {self._ssh.get_transport().getpeername()}:{remote_path} "
                f"to {local_path}"
            )
        # SCPCLient takes a paramiko transport as its only argument
        if not wildcard:
            scp = SCPClient(self._ssh.get_transport(), socket_timeout=timeout)
        else:
            scp = SCPClient(
                self._ssh.get_transport(), sanitize=lambda x: x,
                socket_timeout=timeout
            )
        start = time()
        if not get:
            scp.put(local_path, remote_path)
        else:
            scp.get(remote_path, local_path)
        scp.close()
        end = time()
        logger.trace(f"SCP took {end-start} seconds")


def exec_cmd(node, cmd, timeout=600, sudo=False, disconnect=False):
    """Convenience function to ssh/exec/return rc, out & err.

    Returns (rc, stdout, stderr).

    :param node: The node to execute command on.
    :param cmd: Command to execute.
    :param timeout: Timeout value in seconds. Default: 600.
    :param sudo: Sudo privilege execution flag. Default: False.
    :param disconnect: Close the opened SSH connection if True.
    :type node: dict
    :type cmd: str or OptionString
    :type timeout: int
    :type sudo: bool
    :type disconnect: bool
    :returns: RC, Stdout, Stderr.
    :rtype: tuple(int, str, str)
    """
    if node is None:
        raise TypeError(u"Node parameter is None")
    if cmd is None:
        raise TypeError(u"Command parameter is None")
    if not cmd:
        raise ValueError(u"Empty command parameter")

    ssh = SSH()

    try:
        ssh.connect(node)
    except SSHException as err:
        logger.error(f"Failed to connect to node {node[u'host']}\n{err!r}")
        return None, None, None

    try:
        if not sudo:
            ret_code, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        else:
            ret_code, stdout, stderr = ssh.exec_command_sudo(
                cmd, timeout=timeout
            )
    except SSHException as err:
        logger.error(repr(err))
        return None, None, None
    finally:
        if disconnect:
            ssh.disconnect()

    return ret_code, stdout, stderr


def exec_cmd_no_error(
        node, cmd, timeout=600, sudo=False, message=None, disconnect=False,
        retries=0, include_reason=False):
    """Convenience function to ssh/exec/return out & err.

    Verifies that return code is zero.
    Supports retries, timeout is related to each try separately then. There is
    sleep(1) before each retry.
    Disconnect (if enabled) is applied after each try.

    :param node: DUT node.
    :param cmd: Command to be executed.
    :param timeout: Timeout value in seconds. Default: 600.
    :param sudo: Sudo privilege execution flag. Default: False.
    :param message: Error message in case of failure. Default: None.
    :param disconnect: Close the opened SSH connection if True.
    :param retries: How many times to retry on failure.
    :param include_reason: Whether default info should be appended to message.
    :type node: dict
    :type cmd: str or OptionString
    :type timeout: int
    :type sudo: bool
    :type message: str
    :type disconnect: bool
    :type retries: int
    :type include_reason: bool
    :returns: Stdout, Stderr.
    :rtype: tuple(str, str)
    :raises RuntimeError: If bash return code is not 0.
    """
    for _ in range(retries + 1):
        ret_code, stdout, stderr = exec_cmd(
            node, cmd, timeout=timeout, sudo=sudo, disconnect=disconnect
        )
        if ret_code == 0:
            break
        sleep(1)
    else:
        msg = f"Command execution failed: '{cmd}'\nRC: {ret_code}\n{stderr}"
        logger.info(msg)
        if message:
            msg = f"{message}\n{msg}" if include_reason else message
        raise RuntimeError(msg)

    return stdout, stderr


def scp_node(
        node, local_path, remote_path, get=False, timeout=30, disconnect=False):
    """Copy files from local_path to remote_path or vice versa.

    :param node: SUT node.
    :param local_path: Path to local file that should be uploaded; or
        path where to save remote file.
    :param remote_path: Remote path where to place uploaded file; or
        path to remote file which should be downloaded.
    :param get: scp operation to perform. Default is put.
    :param timeout: Timeout value in seconds.
    :param disconnect: Close the opened SSH connection if True.
    :type node: dict
    :type local_path: str
    :type remote_path: str
    :type get: bool
    :type timeout: int
    :type disconnect: bool
    :raises RuntimeError: If SSH connection failed or SCP transfer failed.
    """
    ssh = SSH()

    try:
        ssh.connect(node)
    except SSHException as exc:
        raise RuntimeError(f"Failed to connect to {node[u'host']}!") from exc
    try:
        ssh.scp(local_path, remote_path, get, timeout)
    except SCPException as exc:
        raise RuntimeError(f"SCP execution failed on {node[u'host']}!") from exc
    finally:
        if disconnect:
            ssh.disconnect()
