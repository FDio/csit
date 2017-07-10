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

"""VPP Huge Page Utilities"""

import re

from robot.api import logger

from resources.libraries.python.ssh import SSH

# VPP Huge page File
DEFAULT_VPP_HUGE_PAGE_CONFIG_FILENAME = "/etc/vpp/80-vpp.conf"
VPP_HUGEPAGE_CONFIG = """
vm.nr_hugepages={nr_hugepages}
vm.max_map_count={max_map_count}
vm.hugetlb_shm_group=0
kernel.shmmax={shmmax}
"""


class VppHugePageUtil(object):

    def hugepage_apply_config(self):

        node = self._node
        host = node['host']

        vpp_hugepage_config = VPP_HUGEPAGE_CONFIG.format(nr_hugepages=self._total,
                                                         max_map_count=self._max_map_count,
                                                         shmmax=self._shmmax)

        try:
            filename = node['hugepages']['hugepage_config_file']
        except:
            filename = DEFAULT_VPP_HUGE_PAGE_CONFIG_FILENAME

        logger.debug('Writing VPP huge page config to host {}: "{}"'.format(host,
                                                                            vpp_hugepage_config))

        ssh = SSH()
        ssh.connect(node)

        # We're using this "| sudo tee" construct because redirecting
        # a sudo'd outut ("sudo echo xxx > /path/to/file") does not
        # work on most platforms...
        (ret, stdout, stderr) = \
            ssh.exec_command('echo "{0}" | sudo tee {1}'.format(vpp_hugepage_config, filename))

        if ret != 0:
            logger.debug('Writing config file failed to node {}'.
                         format(host))
            logger.debug('stdout: {}'.format(stdout))
            logger.debug('stderr: {}'.format(stderr))
            raise RuntimeError('Writing config file failed to node {}'.
                               format(host))

        # Make the new huge page config permanent
        cmd = "sudo sysctl -p {}".format(filename)
        (ret, stdout, stderr) = ssh.exec_command(cmd)
        if ret != 0:
            logger.debug('Sysctl command failed to node {}'.format(host))
            logger.debug('stdout: {}'.format(stdout))
            logger.debug('stderr: {}'.format(stderr))
            raise RuntimeError('Sysctl command failed to node {}'.
                               format(host))

    def get_actual_huge_pages(self):

        ssh = SSH()
        ssh.connect(self._node)

        # Get the memory information using /proc/meminfo
        (ret, stdout, stderr) = \
            ssh.exec_command('sudo cat /proc/meminfo')
        if ret != 0:
            logger.debug('Writing config file failed to node {}'.
                         format(self._node['host']))
            logger.debug('stdout: {}'.format(stdout))
            logger.debug('stderr: {}'.format(stderr))
            raise RuntimeError('Failed to get Huge Page informantion on node {}'.
                               format(self._node['host']))

        total = re.findall(r'HugePages_Total:\s+\w+', stdout)
        free = re.findall(r'HugePages_Free:\s+\w+', stdout)
        size = re.findall(r'Hugepagesize:\s+\w+\s+\w+', stdout)

        self._hugepagetotal = total[0].split(':')[1].lstrip()
        self._hugepagefree = free[0].split(':')[1].lstrip()
        self._hugepagesize = size[0].split(':')[1].lstrip()

    def show_huge_pages(self):

        self.get_actual_huge_pages()
        print("Huge Page Infomation on Node {}:".format(self._node['host']))
        print("  {:15}: {}".format("Huge Page Total", self._hugepagetotal))
        print("  {:15}: {}".format("Huge Page Free", self._hugepagefree))
        print("  {:15}: {}".format("Huge Page Size", self._hugepagesize))

    def get_huge_page_config(self):
        return self._total, self._max_map_count, self._shmmax

    def __init__(self, node):
        self._node = node
        self._hugepagetotal = ""
        self._hugepagefree = ""
        self._hugepagesize = ""
        self._total = self._node['hugepages']['total']
        self._max_map_count = int(self._total) * 2 + 1024
        self._shmmax = int(self._total) * 2 * 1024 * 1024
