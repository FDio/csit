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

"""VPP Configuration File Generator library."""

import re
import time

from robot.api import logger

from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import NodeType
from resources.libraries.python.topology import Topology

__all__ = ['VppConfigGenerator']

class VppConfigGenerator(object):
    """VPP Configuration File Generator."""

    def __init__(self):
        # VPP node to apply configuration on
        self._node = ''
        # VPP hostname
        self._hostname = ''
        # VPP Configuration
        self._nodeconfig = {'unix': {'nodaemon': '',
                                     'log': '/tmp/vpe.log'}}
        # Serialized VPP Configuration
        self._vpp_config = ''
        # VPP service name
        self._vpp_service_name = 'vpp'
        # VPP configuration file path
        self._vpp_config_filename = '/etc/vpp/startup.conf'


    def set_node(self, node):
        """Set DUT node.

        :param node: Node to store configuration on.
        :type node: dict
        :raises RuntimeError: If Node type is not DUT.
        """

        if node['type'] != NodeType.DUT:
            raise RuntimeError('Node type is not DUT.')
        self._node = node
        self._hostname = Topology.get_node_hostname(node)

    def dump_config(self, obj, level=-1):
        """Dump the node configuration into VPP config format.

        :param obj: Python Object to print.
        :param nested_level: Nested level for indentation.
        :type obj: Obj
        :type nested_level: int
        :returns: nothing
        """
        indent = '  '
        if level >= 0:
            self._vpp_config += '{}{{\n'.format((level) * indent)
        if isinstance(obj, dict):
            for key, val in obj.items():
                if hasattr(val, '__iter__'):
                    self._vpp_config += '{}{}\n'.format((level + 1) * indent,
                                                        key)
                    self.dump_config(val, level + 1)
                else:
                    self._vpp_config += '{}{} {}\n'.format((level + 1) * indent,
                                                           key, val)
        else:
            for val in obj:
                self._vpp_config += '{}{}\n'.format((level + 1) * indent, val)
        if level >= 0:
            self._vpp_config += '{}}}\n'.format(level * indent)

    def add_config_item(self, config, path, value):
        """Add configuration item for node.

        :param config: Configuration of node.
        :param path: Path where to insert item.
        :param value: Value to insert.
        :type config: dict
        :type path: list
        :type value: str
        """

        if len(path) == 1:
            config[path[0]] = value
            return
        if not config.has_key(path[0]):
            config[path[0]] = {}
        self.add_config_item(config[path[0]], path[1:], value)

    def add_pci_all_devices(self):
        """Add all PCI devices from topology file to startup config."""

        for port in self._node['interfaces'].keys():
            pci_addr = Topology.get_interface_pci_addr(self._node, port)
            if pci_addr:
                self.add_pci_device(pci_addr)

    def add_pci_device(self, *pci_devices):
        """Add PCI device configuration for node.

        :param pci_devices: PCI devices (format 0000:00:00.0)
        :type pci_devices: tuple
        """

        pattern = re.compile("^[0-9A-Fa-f]{4}:[0-9A-Fa-f]{2}:"
                             "[0-9A-Fa-f]{2}\\.[0-9A-Fa-f]$")
        for pci_device in pci_devices:
            if not pattern.match(pci_device):
                raise ValueError('PCI address {} to be added to host {} '
                                 'is not in valid format xxxx:xx:xx.x'.
                                 format(pci_device, self._hostname))
            path = ['dpdk', 'dev {0}'.format(pci_device)]
            self.add_config_item(self._nodeconfig, path, '')

    def add_default_rxq_config(self, value):
        """Add Dev default rxq configuration for node.

        :param value: Dev default rxq configuration option, as a string.
        :type value: str
        """

        path = ['dpdk', 'dev default', 'rxqueuesconfig']
        self.add_config_item(self._nodeconfig, path, value)

    def add_default_txq_config(self, value):
        """Add Dev default txq configuration for node.

        :param value: Dev default txq configuration option, as a string.
        :type value: str
        """

        path = ['dpdk', 'dev default', 'txqueuesconfig']
        self.add_config_item(self._nodeconfig, path, value)

    def add_socketmem_config(self, value):
        """Add Socket Memory configuration for node.

        :param value: Socket Memory configuration option, as a string.
        :type value: str
        """

        path = ['dpdk', 'socket-mem']
        self.add_config_item(self._nodeconfig, path, value)

    def add_main_core_config(self, value):
        """Add CPU main core configuration for node.

        :param value: Main core CPU configuration option, as a string.
        :type value: str
        """

        path = ['cpu', 'main-core']
        self.add_config_item(self._nodeconfig, path, value)

    def add_workers_config(self, value):
        """Add CPU corelist-workers configuration for node.

        :param value: Main core CPU configuration option, as a string.
        :type value: str
        """
        path = ['cpu', 'corelist-workers']
        self.add_config_item(self._nodeconfig, path, value)

    def add_heapsize_config(self, value):
        """Add Heapsize configuration for node.

        :param value: Heapsize configuration option, as a string.
        :type value: str
        """
        path = ['heapsize']
        self.add_config_item(self._nodeconfig, path, value)

    def add_api_trace_config(self):
        """Add API trace configuration for node."""
        path = ['api-trace', 'on']
        self.add_config_item(self._nodeconfig, path, '')

    def add_ip6_hash_buckets_config(self, value):
        """Add IP6 hash buckets configuration for node.

        :param value: IP6 hash buckets configuration option, as a string.
        :type value: str
        """
        path = ['ip6', 'hash-buckets']
        self.add_config_item(self._nodeconfig, path, value)

    def add_ip6_heap_size_config(self, value):
        """Add IP6 heap-size configuration for node.

        :param value: IP6 heap-size configuration option, as a string.
        :type value: str
        """
        path = ['ip6', 'heap-size']
        self.add_config_item(self._nodeconfig, path, value)

    def add_no_multi_seg_config(self):
        """Add no-multi-seg configuration for node."""
        path = ['dpdk', 'no-multi-seg']
        self.add_config_item(self._nodeconfig, path, '')

    def add_snat_config(self):
        """Add SNAT configuration for node."""
        path = ['snat']
        self.add_config_item(self._nodeconfig, path, 'deterministic')

    def add_cryptodev_config(self, count):
        """Add cryptodev configuration for node.

        :param count: Number of crypto devices to add.
        :type count: int
        """
        cryptodev = Topology.get_cryptodev(self._node)
        for i in range(count):
            cryptodev_config = 'dev {0}'.format(
                re.sub(r'\d.\d$', '1.'+str(i), cryptodev))
            path = ['dpdk', cryptodev_config]
            self.add_config_item(self._nodeconfig, path, '')

        path = ['uio-driver']
        self.add_config_item(self._nodeconfig, path, 'igb_uio')

    def apply_config(self, waittime=5, retries=12):
        """Generate and apply VPP configuration for node.

        Use data from calls to this class to form a startup.conf file and
        replace /etc/vpp/startup.conf with it on node.

        :param waittime: Time to wait for VPP to restart (default 5 seconds).
        :param retries: Number of times (default 12) to re-try waiting.
        :type waittime: int
        :type retries: int
        :raises RuntimeError: If writing config file failed, or restarting of
        VPP failed.
        """
        self.dump_config(self._nodeconfig)

        ssh = SSH()
        ssh.connect(self._node)

        # We're using this "| sudo tee" construct because redirecting
        # a sudo'd outut ("sudo echo xxx > /path/to/file") does not
        # work on most platforms...
        (ret, _, _) = \
            ssh.exec_command('echo "{0}" | sudo tee {1}'.
                             format(self._vpp_config,
                                    self._vpp_config_filename))

        if ret != 0:
            raise RuntimeError('Writing config file failed to node {}'.
                               format(self._hostname))

        # Instead of restarting, we'll do separate start and stop
        # actions. This way we don't care whether VPP was running
        # to begin with.
        ssh.exec_command('sudo service {} stop'
                         .format(self._vpp_service_name))
        (ret, _, _) = \
            ssh.exec_command('sudo service {} start'
                             .format(self._vpp_service_name))
        if ret != 0:
            raise RuntimeError('Restarting VPP failed on node {}'.
                               format(self._hostname))

        # Sleep <waittime> seconds, up to <retry> times,
        # and verify if VPP is running.
        vpp_is_running = False
        retries_left = retries
        while (not vpp_is_running) and (retries_left > 0):
            time.sleep(waittime)
            retries_left -= 1
            (ret, _, _) = \
                ssh.exec_command('echo show hardware-interfaces | '
                                 'nc 0 5002')
            if ret == 0:
                vpp_is_running = True
            else:
                logger.debug('VPP not yet running, {} retries left'.
                             format(retries_left))
        if retries_left == 0:
            raise RuntimeError('VPP failed to restart on node {}'.
                               format(self._hostname))
