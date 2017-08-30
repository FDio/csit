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

"""VPP util library"""
import logging
import re

from resources.libraries.python.ssh import SSH


class VPPUtil(object):
    """General class for any VPP related methods/functions."""

    @staticmethod
    def _install_vpp_pkg(node, ssh, pkg):
        """
        Install the VPP packages

        :param node: Node dictionary
        :param ssh: ssh class
        :param pkg: The vpp packages
        :type node: dict
        :type ssh: class
        :type pkg: string
        """

        cmd = 'apt-get install {}'.format(pkg)
        (ret, stdout, stderr) = ssh.exec_command(cmd)
        if ret != 0:
            raise RuntimeError('{} failed on node {} {} {}'.format(
                cmd, node['host'], stdout, stderr))

    def install_vpp_ubuntu(self, node, fdio_release='1707',
                           ubuntu_version='xenial'):
        """
        Install the VPP packages

        :param node: Node dictionary with cpuinfo.
        :param fdio_release: VPP release number
        :param ubuntu_version: Ubuntu Version
        :type node: dict
        :type fdio_release: string
        :type ubuntu_version: string
        """

        ofile = '/etc/apt/sources.list.d/99fd.io.list.orig'  # Original file
        nfile = '/etc/apt/sources.list.d/99fd.io.list'  # New file
        ofile_exists = False
        nfile_exists = False

        ssh = SSH()
        ssh.connect(node)

        # Save the original file, then write a new one
        # Does a copy of the original file exist
        (ret, stdout, stderr) = ssh.exec_command('ls {}'.format(ofile))
        if ret != 0:
            logging.debug(stderr)
        if stdout.strip('\n') == ofile:
            ofile_exists = True

        # Does a copy of the original file exist
        (ret, stdout, stderr) = ssh.exec_command('ls {}'.format(nfile))
        if ret != 0:
            logging.debug(stderr)
        if stdout.strip('\n') == nfile:
            nfile_exists = True

        # Make a copy of the original file
        if (nfile_exists is True) and (ofile_exists is not True):
            cmd = 'sudo cp {} {}'.format(nfile, ofile)
            (ret, stdout, stderr) = ssh.exec_command(cmd)
            if ret != 0:
                raise RuntimeError('{} command failed on node {} {}'.format(
                    cmd,
                    node['host'],
                    stderr))

        # Remove the current file
        if nfile_exists is True:
            cmd = 'rm {}'.format(nfile)
            (ret, stdout, stderr) = ssh.exec_command(cmd)
            if ret != 0:
                raise RuntimeError('{} failed on node {} {}'.format(
                    cmd,
                    node['host'],
                    stderr))

        reps = 'deb [trusted=yes] https://nexus.fd.io/content/repositories/\
fd.io.stable.{}.ubuntu.{}.main/ ./\n'.format(fdio_release, ubuntu_version)

        cmd = 'echo "{0}" | sudo tee {1}'.format(reps, nfile)
        (ret, stdout, stderr) = ssh.exec_command(cmd)
        if ret != 0:
            raise RuntimeError('{} failed on node {} {}'.format(
                cmd,
                node['host'],
                stderr))

        # Install the package
        cmd = 'apt-get update'
        (ret, stdout, stderr) = ssh.exec_command(cmd)
        if ret != 0:
            raise RuntimeError('{} apt-get update failed on node {} {}'.format(
                cmd,
                node['host'],
                stderr))

        self._install_vpp_pkg(node, ssh, 'vpp-lib')
        self._install_vpp_pkg(node, ssh, 'vpp')
        self._install_vpp_pkg(node, ssh, 'vpp-plugins')
        self._install_vpp_pkg(node, ssh, 'vpp-dpdk-dkms')
        self._install_vpp_pkg(node, ssh, 'vpp-dpdk-dev')
        self._install_vpp_pkg(node, ssh, 'vpp-api-python')
        self._install_vpp_pkg(node, ssh, 'vpp-api-java')
        self._install_vpp_pkg(node, ssh, 'vpp-api-lua')
        self._install_vpp_pkg(node, ssh, 'vpp-nsh-plugin-dbg')
        self._install_vpp_pkg(node, ssh, 'vpp-nsh-plugin-dev')
        self._install_vpp_pkg(node, ssh, 'vpp-nsh-plugin')
        self._install_vpp_pkg(node, ssh, 'vpp-dev')
        self._install_vpp_pkg(node, ssh, 'vpp-dbg')

    @staticmethod
    def _uninstall_vpp_pkg(node, ssh, pkg):
        """
        Uninstall the VPP packages

        :param node: Node dictionary
        :param ssh: ssh class
        :param pkg: The vpp packages
        :type node: dict
        :type ssh: class
        :type pkg: string
        """
        cmd = 'dpkg --purge {}'.format(pkg)
        (ret, stdout, stderr) = ssh.exec_command(cmd)
        if ret != 0:
            raise RuntimeError('{} failed on node {} {} {}'.format(
                cmd, node['host'], stdout, stderr))

    def uninstall_vpp_ubuntu(self, node):
        """
        Uninstall the VPP packages

        :param node: Node dictionary with cpuinfo.
        :type node: dict
        """

        ssh = SSH()
        ssh.connect(node)

        cmd = 'dpkg -l | grep vpp'
        (ret, stdout, stderr) = ssh.exec_command(cmd)
        if ret != 0:
            raise RuntimeError('{} failed on node {} {} {}'.format(
                cmd, node['host'], stdout, stderr))

        self._uninstall_vpp_pkg(node, ssh, 'vpp-api-python')
        self._uninstall_vpp_pkg(node, ssh, 'vpp-api-java')
        self._uninstall_vpp_pkg(node, ssh, 'vpp-api-lua')
        self._uninstall_vpp_pkg(node, ssh, 'vpp-nsh-plugin-dbg')
        self._uninstall_vpp_pkg(node, ssh, 'vpp-nsh-plugin-dev')
        self._uninstall_vpp_pkg(node, ssh, 'vpp-nsh-plugin')
        self._uninstall_vpp_pkg(node, ssh, 'vpp-plugins')
        self._uninstall_vpp_pkg(node, ssh, 'vpp-dpdk-dev')
        self._uninstall_vpp_pkg(node, ssh, 'vpp-dpdk-dkms')
        self._uninstall_vpp_pkg(node, ssh, 'vpp-dev')
        self._uninstall_vpp_pkg(node, ssh, 'vpp-dbg')
        self._uninstall_vpp_pkg(node, ssh, 'vpp')
        self._uninstall_vpp_pkg(node, ssh, 'vpp-lib')

    @staticmethod
    def show_vpp_settings(node, *additional_cmds):
        """
        Print default VPP settings. In case others are needed, can be
        accepted as next parameters (each setting one parameter), preferably
        in form of a string.

        :param node: VPP node.
        :param additional_cmds: Additional commands that the vpp should print
        settings for.
        :type node: dict
        :type additional_cmds: tuple
        """
        def_setting_tb_displayed = {
            'IPv6 FIB': 'ip6 fib',
            'IPv4 FIB': 'ip fib',
            'Interface IP': 'int addr',
            'Interfaces': 'int',
            'ARP': 'ip arp',
            'Errors': 'err'
        }

        if additional_cmds:
            for cmd in additional_cmds:
                def_setting_tb_displayed['Custom Setting: {}'.format(cmd)]\
                    = cmd

                ssh = SSH()
                ssh.connect(node)
                for _, value in def_setting_tb_displayed.items():
                    ssh.exec_command_sudo('vppctl sh {}'.format(value))

    @staticmethod
    def get_hardware(node):
        """
        Get the VPP hardware information and return it in a
        dictionary

        :param node: VPP node.
        :type node: dict
        :returns: Dictionary containing improtant VPP information
        :rtype: dictionary
        """

        ssh = SSH()
        ssh.connect(node)

        cmd = 'vppctl show hard'
        (ret, stdout, stderr) = ssh.exec_command(cmd)
        if ret != 0:
            raise RuntimeError('{} failed on node {} {} {}'.
                               format(cmd, node['host'],
                                      stdout, stderr))

        lines = stdout.split('\n')
        interfaces = {}
        if len(lines[0]) is not 0:
            if lines[0].split(' ')[0] == 'FileNotFoundError':
                return interfaces

        for line in lines:
            if len(line) is 0:
                continue

            # If the first character is not whitespace
            # create a new interface
            if len(re.findall(r'\s', line[0])) is 0:
                spl = line.split()
                name = spl[0]
                interfaces[name] = {}
                interfaces[name]['index'] = spl[1]
                interfaces[name]['state'] = spl[2]

            # Ethernet address
            rfall = re.findall(r'Ethernet address', line)
            if len(rfall):
                spl = line.split()
                interfaces[name]['mac'] = spl[2]

            # Carrier
            rfall = re.findall(r'carrier', line)
            if len(rfall):
                spl = line.split('carrier ')
                interfaces[name]['carrier'] = spl[1]

            # Socket
            rfall = re.findall(r'cpu socket', line)
            if len(rfall):
                spl = line.split('cpu socket ')
                interfaces[name]['cpu socket'] = spl[1]

            # Queues and Descriptors
            rfall = re.findall(r'rx queues', line)
            if len(rfall):
                spl = line.split(',')
                interfaces[name]['rx queues'] = spl[0].lstrip(' ').split(' ')[2]
                interfaces[name]['rx descs'] = spl[1].split(' ')[3]
                interfaces[name]['tx queues'] = spl[2].split(' ')[3]
                interfaces[name]['tx descs'] = spl[3].split(' ')[3]

        return interfaces
