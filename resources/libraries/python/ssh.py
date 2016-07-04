# Copyright (c) 2016 Cisco and/or its affiliates.
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

import StringIO
from time import time

import socket
import paramiko
from paramiko import RSAKey
from scp import SCPClient
from interruptingcow import timeout
from robot.api import logger
from robot.utils.asserts import assert_equal

__all__ = ["exec_cmd", "exec_cmd_no_error"]

# TODO: load priv key


class SSH(object):

    __MAX_RECV_BUF = 10*1024*1024
    __existing_connections = {}

    def __init__(self):
        self._ssh = None

    @staticmethod
    def _node_hash(node):
        return hash(frozenset([node['host'], node['port']]))

    def connect(self, node):
        """Connect to node prior to running exec_command or scp.

        If there already is a connection to the node, this method reuses it.
        """
        node_hash = self._node_hash(node)
        if node_hash in SSH.__existing_connections:
            self._ssh = SSH.__existing_connections[node_hash]
            logger.debug('reusing ssh: {0}'.format(self._ssh))
        else:
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

            SSH.__existing_connections[node_hash] = self._ssh

            logger.trace('connect took {} seconds'.format(time() - start))
            logger.debug('new ssh: {0}'.format(self._ssh))

        logger.debug('Connect peer: {0}'.
                     format(self._ssh.get_transport().getpeername()))
        logger.debug('Connections: {0}'.format(str(SSH.__existing_connections)))

    def disconnect(self, node):
        """Close SSH connection to the node.

        :param node: The node to disconnect from.
        :type node: dict
        """
        node_hash = self._node_hash(node)
        if node_hash in SSH.__existing_connections:
            ssh = SSH.__existing_connections.pop(node_hash)
            ssh.close()

    def exec_command(self, cmd, timeout=10):
        """Execute SSH command on a new channel on the connected Node.

        Returns (return_code, stdout, stderr).
        """
        logger.trace('exec_command on {0}: {1}'
                     .format(self._ssh.get_transport().getpeername(), cmd))
        start = time()
        chan = self._ssh.get_transport().open_session()
        if timeout is not None:
            chan.settimeout(int(timeout))
        chan.exec_command(cmd)
        end = time()
        logger.trace('exec_command on {0} took {1} seconds'.format(
            self._ssh.get_transport().getpeername(), end-start))

        stdout = ""
        try:
            while True:
                buf = chan.recv(self.__MAX_RECV_BUF)
                stdout += buf
                if not buf:
                    break
        except socket.timeout:
            logger.error('Caught timeout exception, current contents '
                         'of buffer: {0}'.format(stdout))
            raise

        stderr = ""
        while True:
            buf = chan.recv_stderr(self.__MAX_RECV_BUF)
            stderr += buf
            if not buf:
                break

        return_code = chan.recv_exit_status()
        logger.trace('chan_recv/_stderr took {} seconds'.format(time()-end))

        logger.trace('return RC {}'.format(return_code))
        logger.trace('return STDOUT {}'.format(stdout))
        logger.trace('return STDERR {}'.format(stderr))
        return return_code, stdout, stderr

    def exec_command_sudo(self, cmd, cmd_input=None, timeout=10):
        """Execute SSH command with sudo on a new channel on the connected Node.

        :param cmd: Command to be executed.
        :param cmd_input: Input redirected to the command.
        :param timeout: Timeout.
        :return: return_code, stdout, stderr

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

    def interactive_terminal_open(self, time_out=10):
        """Open interactive terminal on a new channel on the connected Node.

        :param time_out: Timeout in seconds.
        :return: SSH channel with opened terminal.

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
        try:
            with timeout(time_out, exception=RuntimeError):
                while not buf.endswith(':~$ ') and self.channel.recv_ready():
                    try:
                        chunk = self.channel.recv(size)
                        if not chunk:
                            break
                        reply += chunk
                        if chan.exit_status_ready():
                            logger.error('Channel exit status ready')
                            break
                    except socket.timeout:
                        logger.error('Caught socket timeout exception, current '
                                     'contents of buffer: {0}'.format(buf))
                        raise
        except RuntimeError:
            raise Exception('Open interactive terminal timeout.')
        return chan

    def interactive_terminal_exec_command(self, chan, cmd, prompt,
                                          time_out=10):
        """Execute command on interactive terminal.

        interactive_terminal_open() method has to be called first!

        :param chan: SSH channel with opened terminal.
        :param cmd: Command to be executed.
        :param prompt: Command prompt, sequence of characters used to
        indicate readiness to accept commands.
        :param time_out: Timeout in seconds.
        :return: Command output.

        .. warning:: Interruptingcow is used here, and it uses
           signal(SIGALRM) to let the operating system interrupt program
           execution. This has the following limitations: Python signal
           handlers only apply to the main thread, so you cannot use this
           from other threads. You must not use this in a program that
           uses SIGALRM itself (this includes certain profilers)
        """
        chan.sendall('{c}\n'.format(c=cmd))
        buf = ''
        try:
            with timeout(time_out, exception=RuntimeError):
                while not buf.endswith(prompt) and self.channel.recv_ready():
                    try:
                        chunk = self.channel.recv(size)
                        if not chunk:
                            break
                        reply += chunk
                        if chan.exit_status_ready():
                            logger.error('Channel exit status ready')
                            break
                    except socket.timeout:
                        logger.error('Caught socket timeout exception, current '
                                     'contents of buffer: {0}'.format(buf))
                        raise
        except RuntimeError:
            raise Exception("Exec '{c}' timeout.".format(c=cmd))
        tmp = buf.replace(cmd.replace('\n', ''), '')
        return tmp.replace(prompt, '')

    @staticmethod
    def interactive_terminal_close(chan):
        """Close interactive terminal SSH channel.

        :param: chan: SSH channel to be closed.
        """
        chan.close()

    def scp(self, local_path, remote_path):
        """Copy files from local_path to remote_path.

        connect() method has to be called first!
        """
        logger.trace('SCP {0} to {1}:{2}'.format(
            local_path, self._ssh.get_transport().getpeername(), remote_path))
        # SCPCLient takes a paramiko transport as its only argument
        scp = SCPClient(self._ssh.get_transport())
        start = time()
        scp.put(local_path, remote_path)
        scp.close()
        end = time()
        logger.trace('SCP took {0} seconds'.format(end-start))


def exec_cmd(node, cmd, timeout=None, sudo=False):
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
    except Exception, e:
        logger.error("Failed to connect to node" + str(e))
        return None

    try:
        if not sudo:
            (ret_code, stdout, stderr) = ssh.exec_command(cmd, timeout=timeout)
        else:
            (ret_code, stdout, stderr) = ssh.exec_command_sudo(cmd,
                                                               timeout=timeout)
    except Exception, e:
        logger.error(e)
        return None

    return ret_code, stdout, stderr


def exec_cmd_no_error(node, cmd, timeout=None, sudo=False):
    """Convenience function to ssh/exec/return out & err.

    Verifies that return code is zero.

    Returns (stdout, stderr).
    """
    (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=timeout, sudo=sudo)
    assert_equal(rc, 0, 'Command execution failed: "{}"\n{}'.
                 format(cmd, stderr))
    return stdout, stderr

