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

from resources.libraries.python.ssh import SSH


class VPPUtil(object):
    """General class for any VPP related methods/functions."""

    @staticmethod
    def _install_vpp_pkg(node, ssh, pkg):

        (ret, stdout, stderr) = ssh.exec_command('apt-get install {}'.format(pkg))
        if ret != 0:
            logging.debug(stderr)
            raise RuntimeError('apt-get install on node {}'.format(node['host']))
        logging.debug(stdout)

    def install_vpp_ubuntu(self, node, fdio_release='1707', ubuntu_version='xenial'):
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
            (ret, stdout, stderr) = ssh.exec_command('sudo cp {} {}'.format(nfile, ofile))
            if ret != 0:
                logging.debug(stderr)
                raise RuntimeError('cp command failed on node {}'.format(node['host']))

        # Remove the current file
        if nfile_exists is True:
            (ret, stdout, stderr) = ssh.exec_command('rm {}'.format(nfile))
        if ret != 0:
            logging.debug(stderr)
            raise RuntimeError('rm command failed on node {}'.format(node['host']))

        s = 'deb [trusted=yes] https://nexus.fd.io/content/repositories/fd.io.stable.{}.ubuntu.{}.main/ ./\n'. \
            format(fdio_release, ubuntu_version)

        (ret, stdout, stderr) = ssh.exec_command('echo "{0}" | sudo tee {1}'.format(s, nfile))
        if ret != 0:
            logging.debug(stderr)
            raise RuntimeError('Writing config file failed to node {}'.format(node['host']))

        # Install the package
        (ret, stdout, stderr) = ssh.exec_command('apt-get update'.format(s, nfile))
        if ret != 0:
            logging.debug(stderr)
            raise RuntimeError('apt-get update failed on node {}'.format(node['host']))

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

        (ret, stdout, stderr) = ssh.exec_command('dpkg --purge {}'.format(pkg))
        if ret != 0:
            logging.debug(stderr)
            raise RuntimeError('dpkg --purge failed on node {}'.format(node['host']))
        logging.debug(stdout)

    def uninstall_vpp_ubuntu(self, node):

        ssh = SSH()
        ssh.connect(node)

        (ret, stdout, stderr) = ssh.exec_command('dpkg -l | grep vpp')
        if ret != 0:
            logging.debug(stderr)
            return

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
        """Print default VPP settings. In case others are needed, can be
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
                def_setting_tb_displayed['Custom Setting: {}'.format(cmd)] = cmd
        ssh = SSH()
        ssh.connect(node)
        for _, value in def_setting_tb_displayed.items():
            ssh.exec_command_sudo('vppctl sh {}'.format(value))
