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


import StringIO
from time import time, sleep
try:
    from shlex import quote
except ImportError:
    # TODO python < 3.3 compatibility
    from pipes import quote

import pexpect
from paramiko import RSAKey, SSHClient, AutoAddPolicy
from paramiko.ssh_exception import SSHException, NoValidConnectionsError
from robot.api import logger
from scp import SCPClient, SCPException

from resources.libraries.python.OptionString import OptionString
from resources.libraries.python.PythonThree import raise_from

__all__ = ["exec_cmd", "exec_cmd_no_error", "scp_node", "disconnect_node"]

# TODO: load priv key


class SSHTimeout(Exception):
    """This exception is raised when a timeout occurs."""
    pass


class SSH(object):
    """Contains methods for managing and using SSH connections.

    Connection instances are maintained to specific nodes, identified by
    a host and port pairing, which are attributes of the target node.

    Presence of a host_port attribute in the node indicates that host_port
    should be treated as the public port to be contacted from the current
    running environment. An SSH tunnel needs to be built to reach the final
    port for ssh. A helper ssh process is spawned to provide the tunnel.


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
            self._tunnel = None

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
        return node['host'], node['port'], node.get('host_port')

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
            logger.debug('Disconnecting peer: {host}, {port}'.
                         format(host=node['host'], port=node['port']))
            self._client.close()
            self._client = None
        self._destroy_tunnel()

    def _reconnect(self, attempts=1):
        """Reconnect to node if necessary, including the first time.

        If there already is a connection to the node, this method reuses it.

        :param attempts: Number of connect attempts.
        :type attempts: int
        :raises IOError: If cannot connect to host.
        """
        if self.is_active():
            logger.debug('Reusing SSH: {client}'.format(client=self._client))
            return

        node = self._node
        while True:
            try:
                self.disconnect()
                start = time()
                self._create_tunnel()
                pkey = None
                if 'priv_key' in node:
                    pkey = RSAKey.from_private_key(
                        StringIO.StringIO(node['priv_key']))

                self._client = SSHClient()
                self._client.set_missing_host_key_policy(AutoAddPolicy())

                self._client.connect(
                    '127.0.0.1' if self._tunnel else node['host'],
                    username=node['username'],
                    password=node.get('password'),
                    pkey=pkey,
                    port=node['port'])

                self._client.get_transport().set_keepalive(10)
                peer = self._client.get_transport().getpeername()
            except SSHException as exc:
                raise_from(IOError('Cannot connect to {host}'.format(
                    host=node['host'])), exc)
            except NoValidConnectionsError as exc:
                raise_from(IOError(
                    'Unable to connect to port {port} on {host}'.format(
                        port=node['port'], host=node['host'])), exc)

            if self.is_active():
                logger.debug('New SSH to {peer} took {total} seconds: {client}'
                             .format(
                                 peer=peer,
                                 total=(time() - start),
                                 client=self._client))
                break
            elif attempts > 0:
                sleep(0.1)
                attempts -= 1
            else:
                raise IOError('Cannot connect to {host}'.format(
                    host=node['host']))

    def _create_tunnel(self):
        """Create a forwarding SSH process for tunneled connections

        :raises IOError: if tunnel cannot be created
        """
        if self._tunnel is not None:
            if self._tunnel.isalive():
                return
            self._destroy_tunnel()

        node = self._node
        if node.get('host_port') is None:
            return

        options = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
        tnl = '-L {port}:127.0.0.1:{port}'.format(port=node['port'])
        ssh_cmd = 'ssh {tnl} {op} {user}@{host} -p {host_port}'.format(
            tnl=tnl, op=options, user=node['host_username'],
            host=node['host'], host_port=node['host_port'])
        logger.debug('Initializing local port forwarding:\n{ssh_cmd}'.format(
            ssh_cmd=ssh_cmd))
        tunnel = pexpect.spawn(ssh_cmd)
        try:
            tunnel.expect('.* password: ')
            logger.trace(tunnel.after)
            tunnel.sendline(node['host_password'])
            tunnel.expect('Welcome .*')
            logger.trace(tunnel.after)
        except (pexpect.EOF, pexpect.TIMEOUT) as exc:
            raise_from(IOError(
                'Failed to open ssh tunnel to {host} on port {port}'.format(
                    host=node['host'], port=node['port'])), exc)
        logger.debug('Pid {pid} forwarding {port} for node {host}.'.format(
            port=node['port'], host=node['host'], pid=tunnel.pid))
        self._tunnel = tunnel

    def _destroy_tunnel(self):
        """Destroy tunnel for this ssh connection"""
        if self._tunnel is not None:
            logger.debug('Closing SSH tunnel pid {pid}'.format(
                pid=self._tunnel.pid))
            self._tunnel.close(force=True)
            self._tunnel = None

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
        if sudo:
            cmd = "sudo -E bash -c {cmd}".format(cmd=quote(cmd))

        stdout = StringIO.StringIO()
        stderr = StringIO.StringIO()
        try:
            chan = self._client.get_transport().open_session(timeout=5)
            peer = self._client.get_transport().getpeername()
        except (AttributeError, SSHException):
            self._reconnect()
            chan = self._client.get_transport().open_session(timeout=5)
            peer = self._client.get_transport().getpeername()
        chan.settimeout(timeout)

        logger.trace('exec_command on {peer} with timeout {timeout}: {cmd}'
                     .format(peer=peer, timeout=timeout, cmd=cmd))

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
                stdout.write(chan.recv(self.__MAX_RECV_BUF))

            if chan.recv_stderr_ready():
                stderr.write(chan.recv_stderr(self.__MAX_RECV_BUF))

            if time() - start > timeout:
                raise SSHTimeout(
                    'Timeout exception during execution of command: {cmd}\n'
                    'Current contents of stdout buffer: {stdout}\n'
                    'Current contents of stderr buffer: {stderr}\n'
                    .format(cmd=cmd, stdout=stdout.getvalue(),
                            stderr=stderr.getvalue())
                )

            sleep(0.1)
        return_code = chan.recv_exit_status()

        while chan.recv_ready():
            stdout.write(chan.recv(self.__MAX_RECV_BUF))

        while chan.recv_stderr_ready():
            stderr.write(chan.recv_stderr(self.__MAX_RECV_BUF))

        end = time()
        logger.trace('exec_command on {peer} took {total} seconds'.
                     format(peer=peer, total=end-start))

        logger.trace('return RC {rc}'.format(rc=return_code))
        if log_stdout_err or int(return_code):
            logger.trace('return STDOUT {stdout}'.
                         format(stdout=stdout.getvalue()))
            logger.trace('return STDERR {stderr}'.
                         format(stderr=stderr.getvalue()))
        return return_code, stdout.getvalue(), stderr.getvalue()

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
            logger.trace('SCP {0} to {1}:{2}'.format(
                local_path, transport.getpeername(), remote_path))
        else:
            logger.trace('SCP {0}:{1} to {2}'.format(
                transport.getpeername(), remote_path, local_path))
        if not wildcard:
            scp = SCPClient(transport, socket_timeout=timeout)
        else:
            scp = SCPClient(
                transport, socket_timeout=timeout, sanitize=lambda x: x)
        start = time()
        try:
            if not get:
                scp.put(local_path, remote_path)
            else:
                scp.get(remote_path, local_path)
        finally:
            scp.close()
        end = time()
        logger.trace('SCP took {0} seconds'.format(end-start))


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
        raise TypeError('Node parameter is None')
    if cmd is None:
        raise TypeError('Command parameter is None')
    if not cmd:
        raise ValueError('Empty command parameter')

    ssh = SSH(node)
    try:
        ssh.connect()
    except SSHException as err:
        logger.error("Failed to connect to node" + repr(err))
        return None, None, None

    try:
        (ret_code, stdout, stderr) = ssh.exec_command(
            cmd,
            timeout=timeout,
            log_stdout_err=log_stdout_err,
            sudo=sudo,
            stdin=stdin)
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
            node,
            cmd,
            timeout=timeout,
            sudo=sudo,
            stdin=stdin)
        if ret_code == 0:
            return stdout, stderr
        sleep(1)

    reason = 'Command execution failed: "{cmd}"\nRC: {rc}\n{stderr}'.format(
        cmd=cmd, rc=ret_code, stderr=stderr)
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
    except IOError as exc:
        raise_from(RuntimeError(
            'Failed to connect to {host}!'.format(host=node['host'])), exc)
    try:
        ssh.scp(local_path, remote_path, get, timeout, wildcard=wildcard)
    except SCPException as exc:
        raise_from(RuntimeError(
            'SCP execution failed on {host}!'.format(host=node['host'])), exc)


def disconnect_node(node):
    """Ensure any existing connection to node is disconnected

    :param node: node which is to be disconnected
    :type node: dict
    """
    SSH.clear_ssh_connection(node)
