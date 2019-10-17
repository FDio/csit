# Copyright (c) 2020 Cisco and/or its affiliates.
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

from io import StringIO
from time import time, sleep
from shlex import quote

from paramiko import RSAKey, SSHClient, AutoAddPolicy
from paramiko.ssh_exception import SSHException, NoValidConnectionsError
from robot.api import logger
from scp import SCPClient, SCPException

from resources.libraries.python.OptionString import OptionString

__all__ = [
    u"exec_cmd", u"exec_cmd_no_error", u"scp_node", u"disconnect_node",
    u"SSHTimeout",
]

# TODO: load priv key


class SSHTimeout(Exception):
    """This exception is raised when a timeout occurs."""


class SSH:
    """Contains methods for managing and using SSH connections.

    Connection instances are maintained to specific nodes, identified by
    a host and port pairing, which are attributes of the target node.
    """

    __MAX_RECV_BUF = 10 * 1024 * 1024
    __instances = {}
    _initialized = False

    def __new__(cls, node):
        """Produce SSH instance for given node, keeping one for each."""
        key = cls._node_key(node)
        instance = cls.__instances.get(key)
        if instance is None:
            instance = super(SSH, cls).__new__(cls)
            cls.__instances[key] = instance
        return instance

    def __init__(self, node):
        """Initialize an SSH object for a node on first use"""
        if not self._initialized:
            self._initialized = True
            self._node = node
            self._client = None

    @classmethod
    def clear_ssh_connection(cls, node):
        """Disconnect and destroy connection to the node if it exists

        :param node: Topology node to disconnect
        :type node: dict
        """
        instance = cls.__instances.pop(cls._node_key(node), None)
        if instance is not None:
            instance.disconnect()

    @classmethod
    def clear_all_ssh_connections(cls):
        """Clear all existing ssh connections to any nodes

        Used in cases where stale connections may interfere with testing.
        """
        for instance in cls.__instances.values():
            instance.disconnect()
        cls.__instances.clear()

    @staticmethod
    def _node_key(node):
        """Get key for identifying a node by target connection.

        :param node: Node in topology.
        :type node: dict
        :returns: IP address and port for the specified node.
        :rtype: tuple
        """
        return node[u'host'], node[u'port']

    def is_active(self):
        """Check if SSH client is actively connected to the target node

        :returns: Whether client is actively connected.
        :rtype: bool
        """
        if self._client is None:
            return False
        transport = self._client.get_transport()
        if transport is None:
            return False
        return transport.is_active()

    def connect(self, attempts=5):
        """Make a connection to the target node.

        If there already is a connection to the node, this method reuses it.

        :param attempts: Number of connect attempts.
        :type attempts: int
        :raises IOError: If cannot connect to host.
        """
        self._reconnect(attempts=attempts)

    def disconnect(self):
        """Close SSH connection to the node if one is open."""
        node = self._node
        if self.is_active():
            logger.debug(f"Disconnecting peer: {node[u'host']}:{node[u'port']}")
            self._client.close()
            self._client = None

    def _reconnect(self, attempts=1):
        """Reconnect to node if necessary, including the first time.

        If there already is a connection to the node, this method reuses it.

        :param attempts: Number of connect attempts.
        :type attempts: int
        :raises IOError: If cannot connect to host.
        """
        if self.is_active():
            logger.debug(f'Reusing SSH: {self._client}')
            return

        node = self._node
        while True:
            try:
                self.disconnect()
                start = time()
                pkey = None
                if u"priv_key" in node:
                    pkey = RSAKey.from_private_key(StringIO(node[u"priv_key"]))

                self._client = SSHClient()
                self._client.set_missing_host_key_policy(AutoAddPolicy())

                self._client.connect(
                    node[u'host'],
                    username=node[u'username'],
                    password=node.get(u'password'),
                    pkey=pkey,
                    port=node[u'port'])

                self._client.get_transport().set_keepalive(10)
                peer = self._client.get_transport().getpeername()
            except SSHException as exc:
                raise IOError(f"Cannot connect to {node[u'host']}") from exc
            except NoValidConnectionsError as exc:
                raise IOError(
                    f"Cannot connect to port {node[u'port']} on {node[u'host']}"
                ) from exc

            if self.is_active():
                total = time() - start
                logger.debug(
                    f'New SSH to {peer} took {total} seconds: {self._client}'
                )
                break

            if attempts > 0:
                sleep(0.1)
                attempts -= 1
            else:
                raise IOError(f"Cannot connect to {node[u'host']}")

    def exec_command(self, cmd, timeout=10, sudo=False,
                     log_stdout_err=True, stdin=None):
        """Execute SSH command on a new channel on the connected Node.

        :param cmd: Command to run on the Node.
        :param timeout: Maximal time in seconds to wait until the command is
            done. If set to None then wait forever.
        :param sudo: execute privileged command via sudo utility
        :param log_stdout_err: If True, stdout and stderr are logged. stdout
            and stderr are logged also if the return code is not zero
            independently of the value of log_stdout_err.
        :param stdin: put string into command's standard input
        :type cmd: str or OptionString
        :type timeout: int
        :type sudo: bool
        :type log_stdout_err: bool
        :type stdin: str
        :returns: return_code, stdout, stderr
        :rtype: tuple(int, str, str)
        :raises SSHTimeout: If command is not finished in timeout time.
        """
        if isinstance(cmd, (list, tuple)):
            cmd = OptionString(cmd)
        cmd = str(cmd)
        stdout = u""
        stderr = u""
        if sudo:
            cmd = quote(cmd)
            cmd = f'sudo -E bash -c {cmd}'

        try:
            chan = self._client.get_transport().open_session(timeout=5)
            peer = self._client.get_transport().getpeername()
        except (AttributeError, SSHException):
            self._reconnect()
            chan = self._client.get_transport().open_session(timeout=5)
            peer = self._client.get_transport().getpeername()
        chan.settimeout(timeout)

        logger.trace(f"exec_command on {peer} with timeout {timeout}: {cmd}")

        start = time()
        chan.exec_command(cmd)
        while not chan.exit_status_ready() and timeout is not None:
            if stdin is not None and chan.send_ready():
                sent = chan.send(stdin)
                if sent == len(stdin):
                    stdin = None
                    chan.shutdown_write()
                else:
                    stdin = stdin[sent:]

            if chan.recv_ready():
                s_out = chan.recv(self.__MAX_RECV_BUF)
                stdout += s_out.decode(encoding=u'utf-8', errors=u'ignore') \
                    if isinstance(s_out, bytes) else s_out

            if chan.recv_stderr_ready():
                s_err = chan.recv_stderr(self.__MAX_RECV_BUF)
                stderr += s_err.decode(encoding=u'utf-8', errors=u'ignore') \
                    if isinstance(s_err, bytes) else s_err

            if time() - start > timeout:
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

        end = time()
        logger.trace(f"exec_command on {peer} took {end-start} seconds")

        logger.trace(f"return RC {return_code}")
        if log_stdout_err or int(return_code):
            logger.trace(
                f"return STDOUT {stdout}"
            )
            logger.trace(
                f"return STDERR {stderr}"
            )
        return return_code, stdout, stderr

    def scp(self, local_path, remote_path, get=False, timeout=30,
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
        transport = self._client.get_transport()
        if not get:
            logger.trace(
                f"SCP {local_path} to {transport.getpeername()}:{remote_path}"
            )
        else:
            logger.trace(
                f"SCP {transport.getpeername()}:{remote_path} to {local_path}"
            )
        # SCPCLient takes a paramiko transport as its only argument
        if not wildcard:
            scp = SCPClient(transport, socket_timeout=timeout)
        else:
            scp = SCPClient(
                transport, socket_timeout=timeout, sanitize=lambda x: x
            )
        start = time()
        try:
            if not get:
                scp.put(local_path, remote_path)
            else:
                scp.get(remote_path, local_path)
        finally:
            scp.close()
        end = time()
        logger.trace(f"SCP took {end-start} seconds")


def exec_cmd(node, cmd, timeout=600, sudo=False,
             log_stdout_err=True, stdin=None):
    """Convenience function to ssh/exec/return rc, out & err.

    Returns (rc, stdout, stderr).

    :param node: The node to execute command on.
    :param cmd: Command to execute.
    :param timeout: Timeout value in seconds. Default: 600.
    :param sudo: Sudo privilege execution flag. Default: False.
    :param log_stdout_err: Log the executed command's outputs.
    :param stdin: Standard input for command
    :type node: dict
    :type cmd: str or OptionString
    :type timeout: int
    :type sudo: bool
    :type log_stdout_err: bool
    :type stdin: str
    :returns: RC, Stdout, Stderr.
    :rtype: tuple(int, str, str)
    """
    if node is None:
        raise TypeError(u"Node parameter is None")
    if cmd is None:
        raise TypeError(u"Command parameter is None")
    if not cmd:
        raise ValueError(u"Empty command parameter")

    ssh = SSH(node)
    try:
        ssh.connect()
    except SSHException as err:
        logger.error(f"Failed to connect to node {node[u'host']}\n{err!r}")
        return None, None, None

    try:
        (ret_code, stdout, stderr) = ssh.exec_command(
            cmd,
            timeout=timeout,
            log_stdout_err=log_stdout_err,
            sudo=sudo,
            stdin=stdin
        )
    except SSHException as err:
        logger.error(repr(err))
        return None, None, None

    return ret_code, stdout, stderr


def exec_cmd_no_error(node, cmd, timeout=600, sudo=False,
                      message=None, retries=0, stdin=None,
                      include_reason=False):
    """Convenience function to ssh/exec/return out & err.

    Verifies that return code is zero.
    Supports retries, timeout is related to each try separately then. There is
    sleep(1) before each retry.

    :param node: DUT node.
    :param cmd: Command to be executed.
    :param timeout: Timeout value in seconds. Default: 600.
    :param sudo: Sudo privilege execution flag. Default: False.
    :param message: Error message in case of failure instead of a generated one
    :param retries: How many times to retry on failure.
    :param stdin: Standard input for command
    :param include_reason: Append generated default message to message
    :type node: dict
    :type cmd: str or OptionString
    :type timeout: int
    :type sudo: bool
    :type message: str
    :type retries: int
    :type stdin: str
    :type include_reason: bool
    :returns: Stdout, Stderr.
    :rtype: tuple(str, str)
    :raises RuntimeError: If bash return code is not 0.
    """
    for _ in range(retries + 1):
        ret_code, stdout, stderr = exec_cmd(
            node, cmd, timeout=timeout, sudo=sudo, stdin=stdin
        )
        if ret_code == 0:
            return stdout, stderr
        sleep(1)

    reason = f'Command execution failed: "{cmd}"\nRC: {ret_code}\n{stderr}'
    logger.info(reason)
    if not message:
        message = reason
    elif include_reason:
        message += '\n' + reason
    raise RuntimeError(message)


def scp_node(
        node, local_path, remote_path, get=False, timeout=30, wildcard=False):
    """Copy files from local_path to remote_path or vice versa.

    :param node: SUT node.
    :param local_path: Path to local file that should be uploaded; or
        path where to save remote file.
    :param remote_path: Remote path where to place uploaded file; or
        path to remote file which should be downloaded.
    :param get: scp operation to perform. Default is put.
    :param timeout: Timeout value in seconds.
    :param wildcard: Assume path has wildcard characters and a glob is needed.
    :type node: dict
    :type local_path: str
    :type remote_path: str
    :type get: bool
    :type timeout: int
    :type wildcard: bool
    :raises RuntimeError: If SSH connection failed or SCP transfer failed.
    """
    ssh = SSH(node)
    try:
        ssh.connect()
    except SSHException as exc:
        raise RuntimeError(f"Failed to connect to {node[u'host']}!") from exc
    try:
        ssh.scp(local_path, remote_path, get, timeout, wildcard=wildcard)
    except SCPException as exc:
        raise RuntimeError(f"SCP execution failed on {node[u'host']}!") from exc


def disconnect_node(node):
    """Ensure any existing connection to node is disconnected

    :param node: node which is to be disconnected
    :type node: dict
    """
    SSH.clear_ssh_connection(node)
