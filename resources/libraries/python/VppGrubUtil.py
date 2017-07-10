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

"""VPP Grub Utility Library."""

import re

from robot.api import logger
from resources.libraries.python.ssh import SSH

__all__ = ['VppGrubUtil']


class VppGrubUtil(object):
    """ VPP Grub Utilities."""

    def _get_actual_cmdline(self):

        ssh = SSH()
        ssh.connect(self._node)

        # Get the memory information using /proc/meminfo
        (ret, stdout, stderr) = \
            ssh.exec_command('sudo cat /proc/cmdline')
        if ret != 0:
            logger.debug('Writing config file failed to node {}'.
                         format(self._node['host']))
            logger.debug('stdout: {}'.format(stdout))
            logger.debug('stderr: {}'.format(stderr))
            raise RuntimeError('Failed to get Grub cmdline on node {}'.
                               format(self._node['host']))

        self._actual_cmdline = stdout.strip('\n')

    def get_actual_cmdline(self):
        return self._actual_cmdline

    def create_cmdline(self, isolated_cpu_list):

        cmdline = self._actual_cmdline
        iommu = re.findall(r'iommu=\w+', cmdline)
        if not iommu:
            cmdline = "{} iommu=pt".format(cmdline)
        else:
            cmdline = re.sub(r'iommu=w+', 'iommu=pt', cmdline)
        iommu = re.findall(r'intel_iommu=\w+', cmdline)
        if not iommu:
            cmdline = "{} intel_iommu=on".format(cmdline)
        else:
            cmdline = re.sub(r'intel_iommu=w+', 'intel_iommu=on', cmdline)
        isolcpus = re.findall(r'isolcpus=\w+', cmdline)
        if not isolcpus:
            cmdline = "{} isolcpus={}".format(cmdline, isolated_cpu_list)
        else:
            cmdline = re.sub(r'isolcpus=w+', 'isolcpus={}'.format(isolated_cpu_list), cmdline)

        self._vpp_cmdline = cmdline

        return self._vpp_cmdline

    def apply_cmdline(self, default_grub_config_filename):

        isolated_cpus = self._node['cpu']['list']
        vpp_cmdline = self.create_cmdline(isolated_cpus)
        self._vpp_cmdline = vpp_cmdline

        # Update grub
        # jadfix need to make this work for remote nodes
        # Save the original file
        ofilename = default_grub_config_filename + '.orig'
        filename = default_grub_config_filename

        ssh = SSH()
        ssh.connect(self._node)

        # Write the output file
        # Does a copy of the original file exist, if not create one
        (ret, stdout, stderr) = \
            ssh.exec_command('ls {}'.format(ofilename))
        if ret != 0:
            logger.debug(stderr)
        if stdout.strip('\n') != ofilename:
            (ret, stdout, stderr) = \
                ssh.exec_command('sudo cp {} {}'.format(filename, ofilename))
            if ret != 0:
                raise RuntimeError('Executing cp command failed to node {}'.
                                   format(self._node['host']))

        # Get the contents of the current grub config file
        (ret, stdout, stderr) = \
            ssh.exec_command('cat {}'.format(filename))
        if ret != 0:
            raise RuntimeError('Executing cat command failed to node {}'.
                               format(self._node['host']))

        # Write the new contents
        default_cmdline = 'GRUB_CMDLINE_LINUX_DEFAULT="{}"'.format(vpp_cmdline)
        content = re.sub(r'GRUB_CMDLINE_LINUX_DEFAULT=.+', default_cmdline, stdout.rstrip('\n'))
        content = content.replace("`", "\`")
        cmd = "sudo cat > {0} << EOF\n{1}\n".format(filename, content)
        (ret, stdout, stderr) = \
            ssh.exec_command(cmd)
        if ret != 0:
            raise RuntimeError('Writing config failed to node {}'.
                               format(self._node['host']))

        # Update Grub
        cmd = "sudo update-grub"
        (ret, stdout, stderr) = \
            ssh.exec_command(cmd)
        if ret != 0:
            raise RuntimeError('Executing update-grub failed to node {}'.
                               format(self._node['host']))

        return self._vpp_cmdline

    def __init__(self, node):
        self._node = node
        self._actual_cmdline = ""
        self._vpp_cmdline = ""
        self._get_actual_cmdline()
