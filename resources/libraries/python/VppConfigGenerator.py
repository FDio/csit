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

import re
import time

from robot.api import logger

from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import NodeType
from resources.libraries.python.topology import Topology

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
DEFAULT_SOCKETMEM_CONFIG = "1024,1024"
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
{heapsizeconfig}
cpu {{
{cpuconfig}
}}

dpdk {{
  socket-mem {socketmemconfig}
  dev default {{
  {rxqueuesconfig}
  {txqueuesconfig}
  }}
{pciconfig}
{nomultiseg}
{enablevhostuser}
}}
"""
# End VPP configuration template.


class VppConfigGenerator(object):
    """VPP Configuration File Generator"""

    def __init__(self):
        self._nodeconfig = {}

    def add_pci_all_devices(self, node):
        """Add all PCI devices from topology file to startup config

        :param node: DUT node
        :type node: dict
        :return: nothing
        """
        for port in node['interfaces'].keys():
            pci_addr = Topology.get_interface_pci_addr(node, port)
            if pci_addr:
                self.add_pci_device(node, pci_addr)


    def add_pci_device(self, node, *pci_devices):
        """Add PCI device configuration for node.

        :param node: DUT node.
        :param pci_device: PCI devices (format 0000:00:00.0 or 00:00.0)
        :type node: dict
        :type pci_devices: tuple
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')

        # Specific device was given.
        hostname = Topology.get_node_hostname(node)

        pattern = re.compile("^[0-9A-Fa-f]{4}:[0-9A-Fa-f]{2}:"
                             "[0-9A-Fa-f]{2}\\.[0-9A-Fa-f]$")
        for pci_device in pci_devices:
            if not pattern.match(pci_device):
                raise ValueError('PCI address {} to be added to host {} '
                                 'is not in valid format xxxx:xx:xx.x'.
                                 format(pci_device, hostname))

            if hostname not in self._nodeconfig:
                self._nodeconfig[hostname] = {}
            if 'pci_addrs' not in self._nodeconfig[hostname]:
                self._nodeconfig[hostname]['pci_addrs'] = []
            self._nodeconfig[hostname]['pci_addrs'].append(pci_device)
            logger.debug('Adding PCI device {1} to {0}'.format(hostname,
                                                               pci_device))

    def add_cpu_config(self, node, cpu_config):
        """Add CPU configuration for node.

        :param node: DUT node.
        :param cpu_config: CPU configuration option, as a string.
        :type node: dict
        :type cpu_config: str
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if hostname not in self._nodeconfig:
            self._nodeconfig[hostname] = {}
        if 'cpu_config' not in self._nodeconfig[hostname]:
            self._nodeconfig[hostname]['cpu_config'] = []
        self._nodeconfig[hostname]['cpu_config'].append(cpu_config)
        logger.debug('Adding {} to hostname {} CPU config'.format(hostname,
                                                                  cpu_config))

    def add_socketmem_config(self, node, socketmem_config):
        """Add Socket Memory configuration for node.

        :param node: DUT node.
        :param socketmem_config: Socket Memory configuration option,
        as a string.
        :type node: dict
        :type socketmem_config: str
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if hostname not in self._nodeconfig:
            self._nodeconfig[hostname] = {}
        self._nodeconfig[hostname]['socketmem_config'] = socketmem_config
        logger.debug('Setting hostname {} Socket Memory config to {}'.
                     format(hostname, socketmem_config))

    def add_heapsize_config(self, node, heapsize_config):
        """Add Heap Size configuration for node.

        :param node: DUT node.
        :param heapsize_config: Heap Size configuration, as a string.
        :type node: dict
        :type heapsize_config: str
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if hostname not in self._nodeconfig:
            self._nodeconfig[hostname] = {}
        self._nodeconfig[hostname]['heapsize_config'] = heapsize_config
        logger.debug('Setting hostname {} Heap Size config to {}'.
                     format(hostname, heapsize_config))

    def add_rxqueues_config(self, node, rxqueues_config):
        """Add Rx Queues configuration for node.

        :param node: DUT node.
        :param rxqueues_config: Rxqueues configuration, as a string.
        :type node: dict
        :type rxqueues_config: str
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if not hostname in self._nodeconfig:
            self._nodeconfig[hostname] = {}
        if not 'rxqueues_config' in self._nodeconfig[hostname]:
            self._nodeconfig[hostname]['rxqueues_config'] = []
        self._nodeconfig[hostname]['rxqueues_config'].append(rxqueues_config)
        logger.debug('Setting hostname {} rxqueues config to {}'.\
            format(hostname, rxqueues_config))

    def add_no_multi_seg_config(self, node):
        """Add No Multi Seg configuration for node.

        :param node: DUT node.
        :type node: dict
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if not hostname in self._nodeconfig:
            self._nodeconfig[hostname] = {}
        if not 'no_multi_seg_config' in self._nodeconfig[hostname]:
            self._nodeconfig[hostname]['no_multi_seg_config'] = []
        self._nodeconfig[hostname]['no_multi_seg_config'].append(
            "no-multi-seg")
        logger.debug('Setting hostname {} config with {}'.\
            format(hostname, "no-multi-seg"))

    def add_enable_vhost_user_config(self, node):
        """Add enable-vhost-user configuration for node.

        :param node: DUT node.
        :type node: dict
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if not hostname in self._nodeconfig:
            self._nodeconfig[hostname] = {}
        if not 'enable_vhost_user' in self._nodeconfig[hostname]:
            self._nodeconfig[hostname]['enable_vhost_user'] = []
        self._nodeconfig[hostname]['enable_vhost_user'].append(
            "enable-vhost-user")
        logger.debug('Setting hostname {} config with {}'.\
            format(hostname, "enable-vhost-user"))

    def remove_all_pci_devices(self, node):
        """Remove PCI device configuration from node.

        :param node: DUT node.
        :type node: dict
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if hostname in self._nodeconfig:
            self._nodeconfig[hostname]['pci_addrs'] = []
        logger.debug('Clearing all PCI devices for hostname {}.'.
                     format(hostname))

    def remove_all_cpu_config(self, node):
        """Remove CPU configuration from node.

        :param node: DUT node.
        :type node: dict
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if hostname in self._nodeconfig:
            self._nodeconfig[hostname]['cpu_config'] = []
        logger.debug('Clearing all CPU config for hostname {}.'.
                     format(hostname))

    def remove_socketmem_config(self, node):
        """Remove Socket Memory configuration from node.

        :param node: DUT node.
        :type node: dict
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if hostname in self._nodeconfig:
            self._nodeconfig[hostname].pop('socketmem_config', None)
        logger.debug('Clearing Socket Memory config for hostname {}.'.
                     format(hostname))

    def remove_heapsize_config(self, node):
        """Remove Heap Size configuration from node.

        :param node: DUT node.
        :type node: dict
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if hostname in self._nodeconfig:
            self._nodeconfig[hostname].pop('heapsize_config', None)
        logger.debug('Clearing Heap Size config for hostname {}.'.
                     format(hostname))

    def remove_rxqueues_config(self, node):
        """Remove Rxqueues configuration from node.

        :param node: DUT node.
        :type node: dict
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if hostname in self._nodeconfig:
            self._nodeconfig[hostname]['rxqueues_config'] = []
        logger.debug('Clearing rxqueues config for hostname {}.'.\
            format(hostname))

    def remove_no_multi_seg_config(self, node):
        """Remove No Multi Seg configuration from node.

        :param node: DUT node.
        :type node: dict
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if hostname in self._nodeconfig:
            self._nodeconfig[hostname]['no_multi_seg_config'] = []
        logger.debug('Clearing No Multi Seg config for hostname {}.'.\
            format(hostname))

    def remove_enable_vhost_user_config(self, node):
        """Remove enable-vhost-user configuration from node.

        :param node: DUT node.
        :type node: dict
        :return: nothing
        """
        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)
        if hostname in self._nodeconfig:
            self._nodeconfig[hostname]['enable_vhost_user'] = []
        logger.debug('Clearing enable-vhost-user config for hostname {}.'.\
            format(hostname))

    def apply_config(self, node, waittime=5, retries=12):
        """Generate and apply VPP configuration for node.

        Use data from calls to this class to form a startup.conf file and
        replace /etc/vpp/startup.conf with it on node.

        :param node: DUT node.
        :param waittime: Time to wait for VPP to restart (default 5 seconds).
        :param retries: Number of times (default 12) to re-try waiting.
        :type node: dict
        :type waittime: int
        :type retries: int
        """

        if node['type'] != NodeType.DUT:
            raise ValueError('Node type is not a DUT')
        hostname = Topology.get_node_hostname(node)

        cpuconfig = ""
        pciconfig = ""
        socketmemconfig = DEFAULT_SOCKETMEM_CONFIG
        heapsizeconfig = ""
        rxqueuesconfig = ""
        txqueuesconfig = ""
        nomultiseg = ""
        enablevhostuser = ""

        if hostname in self._nodeconfig:
            cfg = self._nodeconfig[hostname]
            if 'cpu_config' in cfg:
                cpuconfig = "  " + "\n  ".join(cfg['cpu_config'])

            if 'pci_addrs' in cfg:
                pciconfig = "  dev " + "\n  dev ".join(cfg['pci_addrs'])

            if 'socketmem_config' in cfg:
                socketmemconfig = cfg['socketmem_config']

            if 'heapsize_config' in cfg:
                heapsizeconfig = "\nheapsize {}\n".\
                    format(cfg['heapsize_config'])

            if 'rxqueues_config' in cfg:
                rxqueuesconfig = "  " + "\n  ".join(cfg['rxqueues_config'])

            if 'no_multi_seg_config' in cfg:
                nomultiseg = "  " + "\n  ".join(cfg['no_multi_seg_config'])

            if 'enable_vhost_user' in cfg:
                enablevhostuser = "  " + "\n  ".join(cfg['enable_vhost_user'])

        vppconfig = VPP_CONFIG_TEMPLATE.format(cpuconfig=cpuconfig,
                                               pciconfig=pciconfig,
                                               socketmemconfig=socketmemconfig,
                                               rxqueuesconfig=rxqueuesconfig,
                                               txqueuesconfig=txqueuesconfig,
                                               nomultiseg=nomultiseg,
                                               enablevhostuser=enablevhostuser)

        logger.debug('Writing VPP config to host {}: "{}"'.format(hostname,
                                                                  vppconfig))

        ssh = SSH()
        ssh.connect(node)

        # We're using this "| sudo tee" construct because redirecting
        # a sudo'd outut ("sudo echo xxx > /path/to/file") does not
        # work on most platforms...
        (ret, stdout, stderr) = \
            ssh.exec_command('echo "{0}" | sudo tee {1}'.
                             format(vppconfig, VPP_CONFIG_FILENAME))

        if ret != 0:
            logger.debug('Writing config file failed to node {}'.
                         format(hostname))
            logger.debug('stdout: {}'.format(stdout))
            logger.debug('stderr: {}'.format(stderr))
            raise RuntimeError('Writing config file failed to node {}'.
                               format(hostname))

        # Instead of restarting, we'll do separate start and stop
        # actions. This way we don't care whether VPP was running
        # to begin with.
        ssh.exec_command('sudo initctl stop {}'.format(VPP_SERVICE_NAME))
        (ret, stdout, stderr) = \
            ssh.exec_command('sudo initctl start {}'.format(VPP_SERVICE_NAME))
        if ret != 0:
            logger.debug('Restarting VPP failed on node {}'.
                         format(hostname))
            logger.debug('stdout: {}'.format(stdout))
            logger.debug('stderr: {}'.format(stderr))
            raise RuntimeError('Restarting VPP failed on node {}'.
                               format(hostname))

        # Sleep <waittime> seconds, up to <retry> times,
        # and verify if VPP is running.
        vpp_is_running = False
        retries_left = retries
        while (not vpp_is_running) and (retries_left > 0):
            time.sleep(waittime)
            retries_left -= 1

            # FIXME: Need to find a good way to check if VPP is operational.
            #
            # If VatTerminal/VatExecutor is anything like vppctl or
            # vpp_api_test, then in case VPP is NOT running it will block for
            # 30 seconds or so and not even return if VPP becomes alive during
            # that time. This makes it unsuitable in this case. We either need
            # a call that returns immediately, indicating whether VPP is
            # healthy or not, or a call that waits (up to a defined length
            # of time) and returns immediately if VPP is or becomes healthy.
            (ret, stdout, stderr) = \
                ssh.exec_command('echo show hardware-interfaces | '
                                 'nc 0 5002')

            if ret == 0:
                vpp_is_running = True
            else:
                logger.debug('VPP not yet running, {} retries left'.
                             format(retries_left))
        if retries_left == 0:
            raise RuntimeError('VPP failed to restart on node {}'.
                               format(hostname))
        logger.debug('VPP interfaces found on node {}'.
                     format(stdout))
