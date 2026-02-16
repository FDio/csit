# Copyright (c) 2026 Cisco and/or its affiliates.
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


import logging

from io import StringIO
from time import monotonic, sleep

from paramiko import RSAKey, SSHClient, AutoAddPolicy
from paramiko.ssh_exception import SSHException, NoValidConnectionsError


__all__ = [
    "exec_cmd", "exec_cmd_no_error", "SSH", "SSHTimeout"
]


class SSHTimeout(Exception):
    """This exception is raised when a timeout occurs."""


class SSH:
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
        return hash(frozenset([node["host"], node["port"]]))

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
                logging.debug(f"Reusing SSH: {self._ssh}")
            else:
                if attempts > 0:
                    self._reconnect(attempts-1)
                else:
                    raise IOError(f"Cannot connect to {node['host']}")
        else:
            try:
                start = monotonic()
                pkey = None
                if "priv_key" in node:
                    pkey = RSAKey.from_private_key(StringIO(node["priv_key"]))

                self._ssh = SSHClient()
                self._ssh.set_missing_host_key_policy(AutoAddPolicy())

                self._ssh.connect(
                    node["host"], username=node["username"],
                    password=node.get("password"), pkey=pkey,
                    port=node["port"]
                )

                self._ssh.get_transport().set_keepalive(10)

                SSH.__existing_connections[node_hash] = self._ssh
                logging.debug(
                    f"New SSH to {self._ssh.get_transport().getpeername()} "
                    f"took {monotonic() - start} seconds: {self._ssh}"
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
            logging.debug(
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
        logging.debug(
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
            Needed for calls outside Robot (e.g. from reservation script).
        :type cmd: str
        :type timeout: int
        :type log_stdout_err: bool
        :returns: return_code, stdout, stderr
        :rtype: tuple(int, str, str)
        :raises SSHTimeout: If command is not finished in timeout time.
        """

        cmd = str(cmd)
        stdout = ""
        stderr = ""
        try:
            chan = self._ssh.get_transport().open_session(timeout=5)
            peer = self._ssh.get_transport().getpeername()
        except (AttributeError, SSHException):
            self._reconnect()
            chan = self._ssh.get_transport().open_session(timeout=5)
            peer = self._ssh.get_transport().getpeername()
        chan.settimeout(timeout)

        logging.debug(f"exec_command on {peer} with timeout {timeout}: {cmd}")

        start = monotonic()
        chan.exec_command(cmd)
        while not chan.exit_status_ready() and timeout is not None:
            if chan.recv_ready():
                s_out = chan.recv(self.__MAX_RECV_BUF)
                stdout += s_out.decode(encoding=u'utf-8', errors=u'ignore') \
                    if isinstance(s_out, bytes) else s_out

            if chan.recv_stderr_ready():
                s_err = chan.recv_stderr(self.__MAX_RECV_BUF)
                stderr += s_err.decode(encoding=u'utf-8', errors=u'ignore') \
                    if isinstance(s_err, bytes) else s_err

            duration = monotonic() - start
            if duration > timeout:
                raise SSHTimeout(
                    f"Timeout exception during execution of command: {cmd}\n"
                    f"Current contents of stdout buffer: "
                    f"{stdout}\n"
                    f"Current contents of stderr buffer: "
                    f"{stderr}\n"
                )

            sleep(0.1)
        return_code = chan.recv_exit_status()

        while chan.recv_ready():
            s_out = chan.recv(self.__MAX_RECV_BUF)
            stdout += s_out.decode(encoding=u'utf-8', errors=u'ignore') \
                if isinstance(s_out, bytes) else s_out

        while chan.recv_stderr_ready():
            s_err = chan.recv_stderr(self.__MAX_RECV_BUF)
            stderr += s_err.decode(encoding=u'utf-8', errors=u'ignore') \
                if isinstance(s_err, bytes) else s_err

        duration = monotonic() - start
        logging.debug(f"exec_command on {peer} took {duration} seconds")

        logging.debug(f"return RC {return_code}")
        if log_stdout_err or int(return_code):
            logging.debug(
                f"return STDOUT {stdout}"
            )
            logging.debug(
                f"return STDERR {stderr}"
            )
        return return_code, stdout, stderr

    def exec_command_sudo(
            self, cmd, cmd_input=None, timeout=30, log_stdout_err=True):
        """Execute SSH command with sudo on a new channel on the connected Node.

        :param cmd: Command to be executed.
        :param cmd_input: Input redirected to the command.
        :param timeout: Timeout.
        :param log_stdout_err: If True, stdout and stderr are logged.
            Needed for calls outside Robot (e.g. from reservation script).
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
        >>> ssh.exec_command_sudo("ifconfig eth0 down")
        >>> # Execute command with input (sudo -S cmd <<< 'input')
        >>> ssh.exec_command_sudo("vpp_api_test", "dump_interface_table")
        """
        if cmd_input is None:
            command = f"sudo -E -S {cmd}"
        else:
            command = f"sudo -E -S {cmd} <<< \"{cmd_input}\""
        return self.exec_command(
            command, timeout, log_stdout_err=log_stdout_err
        )


def exec_cmd(
        node, cmd, timeout=600, sudo=False, disconnect=False,
        log_stdout_err=True
    ):
    """Convenience function to ssh/exec/return rc, out & err.

    Returns (rc, stdout, stderr).

    :param node: The node to execute command on.
    :param cmd: Command to execute.
    :param timeout: Timeout value in seconds. Default: 600.
    :param sudo: Sudo privilege execution flag. Default: False.
    :param disconnect: Close the opened SSH connection if True.
    :param log_stdout_err: If True, stdout and stderr are logged. stdout
        and stderr are logged also if the return code is not zero
        independently of the value of log_stdout_err.
        Needed for calls outside Robot (e.g. from reservation script).
    :type node: dict
    :type cmd: str
    :type timeout: int
    :type sudo: bool
    :type disconnect: bool
    :type log_stdout_err: bool
    :returns: RC, Stdout, Stderr.
    :rtype: Tuple[int, str, str]
    """
    if node is None:
        raise TypeError("Node parameter is None")
    if cmd is None:
        raise TypeError("Command parameter is None")
    if not cmd:
        raise ValueError("Empty command parameter")

    ssh = SSH()

    try:
        ssh.connect(node)
    except SSHException as err:
        logging.error(f"Failed to connect to node {node[u'host']}\n{err!r}")
        return None, None, None

    try:
        if not sudo:
            ret_code, stdout, stderr = ssh.exec_command(
                cmd, timeout=timeout, log_stdout_err=log_stdout_err
            )
        else:
            ret_code, stdout, stderr = ssh.exec_command_sudo(
                cmd, timeout=timeout, log_stdout_err=log_stdout_err
            )
    except SSHException as err:
        logging.error(repr(err))
        return None, None, None
    finally:
        if disconnect:
            ssh.disconnect()

    return ret_code, stdout, stderr
