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

"""VPP Configuration File Generator library"""

from robot.api import logger

from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import NodeType
from resources.libraries.python.topology import Topology

import re
import time

__all__ = ['VppConfigGenerator']

#
# VPP configuration template.
# TODO: Do we need a better place for this? Somewhere in an external
# (template) file?
# Note: We're going to pass this through Python string Formatter, so
# any literal curly braces need to be escaped.
#
VPP_SERVICE_NAME = "vpp"
VPP_CONFIG_FILENAME = "/etc/vpp/startup.conf"
VPP_CONFIG_TEMPLATE = """
unix {{
  nodaemon
  log /tmp/vpe.log
  cli-listen localhost:5002
  full-coredump
}}

api-trace {{
  on
}}

cpu {{
{cpuconfig}
}}

dpdk {{
  socket-mem 1024,1024
{pciconfig}
}}
"""
# End VPP configuration template.


class VppConfigGenerator(object):
    """VPP Configuration File Generator"""

    def __init__(self):
        self._nodeconfig = {}

    def add_pci_device(self, node, pci_device=None):
        """Add PCI device to node.
        :param node: DUT node
        :type node: dict
        :param pci_device: PCI device (format 0000:00:00.0 or 00:00.0).
        If none given, all PCI devices for this node as per topology will be
        added.
        :type pci_device: string
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise Exception('Node type is not a DUT')

        if pci_device is None:
            # No PCI device was given. Add all device from topology.
            for port in node['interfaces'].values():
                port_name = port.get('name')
                pci_addr = Topology.get_interface_pci_addr(node, port_name)
                if pci_addr:
                    self.add_pci_device(node, pci_addr)
        else:
            # Specific device was given.
            hostname = Topology.get_node_hostname(node)

            pattern = re.compile("^[0-9A-Fa-f]{4}:[0-9A-Fa-f]{2}:"\
                "[0-9A-Fa-f]{2}\\.[0-9A-Fa-f]$")
            if not pattern.match(pci_device):
                raise Exception('PCI address {} to be added to host {} '\
                    'is not in valid format xxxx:xx:xx.x'.\
                    format(pci_device, hostname))

            if not hostname in self._nodeconfig:
                self._nodeconfig[hostname] = {}
            if not 'pci_addrs' in self._nodeconfig[hostname]:
                self._nodeconfig[hostname]['pci_addrs'] = []
            self._nodeconfig[hostname]['pci_addrs'].append(pci_device)
            logger.debug('Adding PCI device {1} to {0}'.format(hostname,\
               pci_device))

    def add_cpu_config(self, node, cpu_config):
        """Add CPU configuration to node.
        :param node: DUT node
        :type node: dict
        :param cpu_config: CPU configuration option, as a string
        :type cpu_config: string
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise Exception('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if not hostname in self._nodeconfig:
            self._nodeconfig[hostname] = {}
        if not 'cpu_config' in self._nodeconfig[hostname]:
            self._nodeconfig[hostname]['cpu_config'] = []
        self._nodeconfig[hostname]['cpu_config'].append(cpu_config)
        logger.debug('Adding {} to hostname {} CPU config'.format(hostname, \
            cpu_config))

    def remove_all_pci_devices(self, node):
        """Remove PCI device configuration from node.
        :param node: DUT node
        :type: node: dict
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise Exception('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if hostname in self._nodeconfig:
            self._nodeconfig[hostname]['pci_addrs'] = []
        logger.debug('Clearing all PCI devices for hostname {}.'.\
            format(hostname))

    def remove_all_cpu_config(self, node):
        """Remove CPU configuration from node.
        :param node: DUT node
        :type: node: dict
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise Exception('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if hostname in self._nodeconfig:
            self._nodeconfig[hostname]['cpu_config'] = []
        logger.debug('Clearing all CPU config for hostname {}.'.\
            format(hostname))

    def apply_config(self, node, waittime=5, retries=12):
        """Apply PCI and CPU configuration to node
        by generating VPP startup.conf file.
        :param node: DUT node
        :type node: dict
        :param waittime: time to wait for VPP to restart
        :type waittime: int
        :param retries: number of times to re-try waiting <waittime>
        :type retries: int
        """

        if node['type'] != NodeType.DUT:
            raise Exception('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)

        cpuconfig = ""
        if hostname in self._nodeconfig and \
            'cpu_config' in self._nodeconfig[hostname]:
            cpuconfig = "  " + \
                "\n  ".join(self._nodeconfig[hostname]['cpu_config'])
        pciconfig = ""
        if hostname in self._nodeconfig and \
            'pci_addrs' in self._nodeconfig[hostname]:
            pciconfig = "  dev " + \
                "\n  dev ".join(self._nodeconfig[hostname]['pci_addrs'])
        vppconfig = VPP_CONFIG_TEMPLATE.format(cpuconfig=cpuconfig, \
            pciconfig=pciconfig)

        logger.debug('Writing VPP config to host {}: "{}"'.format(hostname,\
               vppconfig))

        ssh = SSH()
        ssh.connect(node)

        # We're using this "| sudo tee" construct because redirecting
        # a sudo'd outut ("sudo echo xxx > /path/to/file") does not
        # work on most platforms...
        (ret, stdout, stderr) = \
            ssh.exec_command('echo "{0}" | sudo tee {1}'.\
            format(vppconfig, VPP_CONFIG_FILENAME))

        if ret != 0:
            logger.debug('Writing config file failed to node {}'.\
                format(hostname))
            logger.debug('stdout: {}'.format(stdout))
            logger.debug('stderr: {}'.format(stderr))
            raise Exception('Writing config file failed to node {}'.\
                format(hostname))

        # Instead of restarting, we'll do separate start and stop
        # actions. This way we don't care whether VPP was running
        # to begin with.
        ssh.exec_command('sudo initctl stop {}'.format(VPP_SERVICE_NAME))
        (ret, stdout, stderr) = \
            ssh.exec_command('sudo initctl start {}'.format(VPP_SERVICE_NAME))
        if ret != 0:
            logger.debug('Restarting VPP failed on node {}'.\
                format(hostname))
            logger.debug('stdout: {}'.format(stdout))
            logger.debug('stderr: {}'.format(stderr))
            raise Exception('Restarting VPP failed on node {}'.\
                format(hostname))

        # Sleep <waittime> seconds, up to <retry> times,
        # and verify if VPP is running.
        vpp_is_running = False
        retries_left = retries
        while (not vpp_is_running) and (retries_left > 0):
            time.sleep(waittime)
            retries_left -= 1
            (ret, stdout, stderr) = \
                ssh.exec_command('echo show hardware-interfaces | '\
                    'nc 0 5002')
            if ret == 0:
                vpp_is_running = True
            else:
                logger.debug('VPP not yet running, {} retries left'.\
                    format(retries_left))
        if retries_left == 0:
            raise Exception('VPP failed to restart on node {}'.\
                format(hostname))
        logger.debug('VPP interfaces found on node {}'.\
           format(stdout))
