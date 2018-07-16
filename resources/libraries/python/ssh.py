# Copyright (c) 2018 Cisco and/or its affiliates.
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

import socket
import paramiko
from paramiko import RSAKey
from paramiko.ssh_exception import SSHException
from scp import SCPClient
from robot.api import logger
from robot.utils.asserts import assert_equal

__all__ = ["exec_cmd", "exec_cmd_no_error"]

# TODO: load priv key


class SSHTimeout(Exception):
    """This exception is raised when a timeout occurs."""
    pass


class SSH(object):
    """Contains methods for managing and using SSH connections."""

    __MAX_RECV_BUF = 10*1024*1024
    __existing_connections = {}

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

        return hash(frozenset([node['host'], node['port']]))

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
                logger.debug('Reusing SSH: {ssh}'.format(ssh=self._ssh))
            else:
                if attempts > 0:
                    self._reconnect(attempts-1)
                else:
                    raise IOError('Cannot connect to {host}'.
                                  format(host=node['host']))
        else:
            try:
                start = time()
                pkey = None
                if 'priv_key' in node:
                    pkey = RSAKey.from_private_key(
                        StringIO.StringIO(node['priv_key']))

                self._ssh = paramiko.SSHClient()
                self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                self._ssh.connect(node['host'], username=node['username'],
                                  password=node.get('password'), pkey=pkey,
                                  port=node['port'])

                self._ssh.get_transport().set_keepalive(10)

                SSH.__existing_connections[node_hash] = self._ssh
                logger.debug('New SSH to {peer} took {total} seconds: {ssh}'.
                             format(
                                 peer=self._ssh.get_transport().getpeername(),
                                 total=(time() - start),
                                 ssh=self._ssh))
            except SSHException:
                raise IOError('Cannot connect to {host}'.
                              format(host=node['host']))

    def disconnect(self, node):
        """Close SSH connection to the node.

        :param node: The node to disconnect from.
        :type node: dict
        """
        node_hash = self._node_hash(node)
        if node_hash in SSH.__existing_connections:
            logger.debug('Disconnecting peer: {host}, {port}'.
                         format(host=node['host'], port=node['port']))
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
        logger.debug('Reconnecting peer done: {host}, {port}'.
                     format(host=node['host'], port=node['port']))

    def exec_command(self, cmd, timeout=10):
        """Execute SSH command on a new channel on the connected Node.

        :param cmd: Command to run on the Node.
        :param timeout: Maximal time in seconds to wait until the command is
        done. If set to None then wait forever.
        :type cmd: str
        :type timeout: int
        :return return_code, stdout, stderr
        :rtype: tuple(int, str, str)
        :raise SSHTimeout: If command is not finished in timeout time.
        """
        stdout = StringIO.StringIO()
        stderr = StringIO.StringIO()
        try:
            chan = self._ssh.get_transport().open_session(timeout=5)
            peer = self._ssh.get_transport().getpeername()
        except AttributeError:
            self._reconnect()
            chan = self._ssh.get_transport().open_session(timeout=5)
            peer = self._ssh.get_transport().getpeername()
        except SSHException:
            self._reconnect()
            chan = self._ssh.get_transport().open_session(timeout=5)
            peer = self._ssh.get_transport().getpeername()
        chan.settimeout(timeout)

        logger.trace('exec_command on {peer} with timeout {timeout}: {cmd}'
                     .format(peer=peer, timeout=timeout, cmd=cmd))

        start = time()
        chan.exec_command(cmd)
        while not chan.exit_status_ready() and timeout is not None:
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
        logger.trace('return STDOUT {stdout}'.format(stdout=stdout.getvalue()))
        logger.trace('return STDERR {stderr}'.format(stderr=stderr.getvalue()))
        return return_code, stdout.getvalue(), stderr.getvalue()

    def exec_command_sudo(self, cmd, cmd_input=None, timeout=30):
        """Execute SSH command with sudo on a new channel on the connected Node.

        :param cmd: Command to be executed.
        :param cmd_input: Input redirected to the command.
        :param timeout: Timeout.
        :returns: return_code, stdout, stderr

        :Example:

        >>> from ssh import SSH
        >>> ssh = SSH()
        >>> ssh.connect(node)
        >>> # Execute command without input (sudo -S cmd)
        >>> ssh.exec_command_sudo("ifconfig eth0 down")
        >>> # Execute command with input (sudo -S cmd <<< "input")
        >>> ssh.exec_command_sudo("vpp_api_test", "dump_interface_table")
        """
        if cmd_input is None:
            command = 'sudo -S {c}'.format(c=cmd)
        else:
            command = 'sudo -S {c} <<< "{i}"'.format(c=cmd, i=cmd_input)
        return self.exec_command(command, timeout)

    def exec_command_lxc(self, lxc_cmd, lxc_name, lxc_params='', sudo=True,
                         timeout=30):
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
        command = "lxc-attach {p} --name {n} -- /bin/sh -c '{c}'"\
            .format(p=lxc_params, n=lxc_name, c=lxc_cmd)

        if sudo:
            command = 'sudo -S {c}'.format(c=command)
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

        buf = ''
        while not buf.endswith((":~$ ", "~]$ ", "~]# ")):
            try:
                chunk = chan.recv(self.__MAX_RECV_BUF)
                if not chunk:
                    break
                buf += chunk
                if chan.exit_status_ready():
                    logger.error('Channel exit status ready')
                    break
            except socket.timeout:
                logger.error('Socket timeout: {0}'.format(buf))
                raise Exception('Socket timeout: {0}'.format(buf))
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
        chan.sendall('{c}\n'.format(c=cmd))
        buf = ''
        while not buf.endswith(prompt):
            try:
                chunk = chan.recv(self.__MAX_RECV_BUF)
                if not chunk:
                    break
                buf += chunk
                if chan.exit_status_ready():
                    logger.error('Channel exit status ready')
                    break
            except socket.timeout:
                logger.error('Socket timeout during execution of command: '
                             '{0}\nBuffer content:\n{1}'.format(cmd, buf))
                raise Exception('Socket timeout during execution of command: '
                                '{0}\nBuffer content:\n{1}'.format(cmd, buf))
        tmp = buf.replace(cmd.replace('\n', ''), '')
        for item in prompt:
            tmp.replace(item, '')
        return tmp

    @staticmethod
    def interactive_terminal_close(chan):
        """Close interactive terminal SSH channel.

        :param: chan: SSH channel to be closed.
        """
        chan.close()

    def scp(self, local_path, remote_path, get=False, timeout=30):
        """Copy files from local_path to remote_path or vice versa.

        connect() method has to be called first!

        :param local_path: Path to local file that should be uploaded; or
        path where to save remote file.
        :param remote_path: Remote path where to place uploaded file; or
        path to remote file which should be downloaded.
        :param get: scp operation to perform. Default is put.
        :param timeout: Timeout value in seconds.
        :type local_path: str
        :type remote_path: str
        :type get: bool
        :type timeout: int
        """
        if not get:
            logger.trace('SCP {0} to {1}:{2}'.format(
                local_path, self._ssh.get_transport().getpeername(),
                remote_path))
        else:
            logger.trace('SCP {0}:{1} to {2}'.format(
                self._ssh.get_transport().getpeername(), remote_path,
                local_path))
        # SCPCLient takes a paramiko transport as its only argument
        scp = SCPClient(self._ssh.get_transport(), socket_timeout=timeout)
        start = time()
        if not get:
            scp.put(local_path, remote_path)
        else:
            scp.get(remote_path, local_path)
        scp.close()
        end = time()
        logger.trace('SCP took {0} seconds'.format(end-start))


def exec_cmd(node, cmd, timeout=600, sudo=False):
    """Convenience function to ssh/exec/return rc, out & err.

    Returns (rc, stdout, stderr).
    """
    if node is None:
        raise TypeError('Node parameter is None')
    if cmd is None:
        raise TypeError('Command parameter is None')
    if len(cmd) == 0:
        raise ValueError('Empty command parameter')

    ssh = SSH()
    try:
        ssh.connect(node)
    except SSHException as err:
        logger.error("Failed to connect to node" + str(err))
        return None, None, None

    try:
        if not sudo:
            (ret_code, stdout, stderr) = ssh.exec_command(cmd, timeout=timeout)
        else:
            (ret_code, stdout, stderr) = ssh.exec_command_sudo(cmd,
                                                               timeout=timeout)
    except SSHException as err:
        logger.error(err)
        return None, None, None

    return ret_code, stdout, stderr


def exec_cmd_no_error(node, cmd, timeout=600, sudo=False):
    """Convenience function to ssh/exec/return out & err.

    Verifies that return code is zero.

    Returns (stdout, stderr).
    """
    (ret_code, stdout, stderr) = exec_cmd(node, cmd, timeout=timeout, sudo=sudo)
    assert_equal(ret_code, 0, 'Command execution failed: "{}"\n{}'.
                 format(cmd, stderr))
    return stdout, stderr
