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

from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import NodeType
from resources.libraries.python.topology import Topology

__all__ = ['VppConfigGenerator']

class VppConfigGenerator(object):
    """VPP Configuration File Generator."""

    def __init__(self):
        # VPP Node to apply configuration on
        self._node = ''
        # VPP Hostname
        self._hostname = ''
        # VPP Configuration
        self._nodeconfig = {}
        # Serialized VPP Configuration
        self._vpp_config = ''
        # VPP Service name
        self._vpp_service_name = 'vpp'
        # VPP Configuration file path
        self._vpp_config_filename = '/etc/vpp/startup.conf'

    def set_node(self, node):
        """Set DUT node.

        :param node: Node to store configuration on.
        :type node: dict
        :raises RuntimeError: If Node type is not DUT.
        """

        if node['type'] != NodeType.DUT:
            raise RuntimeError('Startup config can only be applied to DUT'
                               'node.')
        self._node = node
        self._hostname = Topology.get_node_hostname(node)

    def set_config_filename(self, filename):
        """Set startup configuration filename.

        :param filename: Startup configuration filename.
        :type filename: str
        """
        self._vpp_config_filename = filename

    def add_config_item(self, config, value, path):
        """Add startup configuration item.

        :param config: Startup configuration of node.
        :param value: Value to insert.
        :param path: Path where to insert item.
        :type config: dict
        :type value: str
        :type path: list
        """

        if len(path) == 1:
            config[path[0]] = value
            return
        if not config.has_key(path[0]):
            config[path[0]] = {}
        self.add_config_item(config[path[0]], value, path[1:])

    def dump_config(self, obj, level=-1):
        """Dump the startup configuration in VPP config format.

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

    def add_unix_log(self, value='/tmp/vpe.log'):
        """Add UNIX log configuration.

        :param value: Log file.
        :type value: str
        """
        path = ['unix', 'log']
        self.add_config_item(self._nodeconfig, value, path)

    def add_unix_cli_listen(self, value='localhost:5002'):
        """Add UNIX cli-listen configuration.

        :param value: CLI listen address and port.
        :type value: str
        """
        path = ['unix', 'cli-listen']
        self.add_config_item(self._nodeconfig, value, path)

    def add_unix_nodaemon(self):
        """Add UNIX nodaemon configuration."""
        path = ['unix', 'nodaemon']
        self.add_config_item(self._nodeconfig, '', path)

    def add_dpdk_dev(self, *devices):
        """Add DPDK PCI device configuration.

        :param devices: PCI device(s) (format xxxx:xx:xx.x)
        :type devices: tuple
        :raises ValueError: If PCI address format is not valid.
        """

        pattern = re.compile("^[0-9A-Fa-f]{4}:[0-9A-Fa-f]{2}:"
                             "[0-9A-Fa-f]{2}\\.[0-9A-Fa-f]$")
        for device in devices:
            if not pattern.match(device):
                raise ValueError('PCI address {} to be added to host {} '
                                 'is not in valid format xxxx:xx:xx.x'.
                                 format(device, self._hostname))
            path = ['dpdk', 'dev {0}'.format(device)]
            self.add_config_item(self._nodeconfig, '', path)

    def add_dpdk_cryptodev(self, count):
        """Add DPDK Crypto PCI device configuration.

        :param count: Number of crypto devices to add.
        :type count: int
        """
        cryptodev = Topology.get_cryptodev(self._node)
        for i in range(count):
            cryptodev_config = 'dev {0}'.format(
                re.sub(r'\d.\d$', '1.'+str(i), cryptodev))
            path = ['dpdk', cryptodev_config]
            self.add_config_item(self._nodeconfig, '', path)
        self.add_dpdk_uio_driver('igb_uio')

    def add_dpdk_dev_default_rxq(self, value):
        """Add DPDK dev default rxq configuration.

        :param value: Default number of rxqs.
        :type value: str
        """
        path = ['dpdk', 'dev default', 'num-rx-queues']
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_dev_default_txq(self, value):
        """Add DPDK dev default txq configuration.

        :param value: Default number of txqs.
        :type value: str
        """
        path = ['dpdk', 'dev default', 'num-tx-queues']
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_socketmem(self, value):
        """Add DPDK socket memory configuration.

        :param value: Socket memory size.
        :type value: str
        """
        path = ['dpdk', 'socket-mem']
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_uio_driver(self, value):
        """Add DPDK uio-driver configuration.

        :param value: DPDK uio-driver configuration.
        :type value: str
        """
        path = ['dpdk', 'uio-driver']
        self.add_config_item(self._nodeconfig, value, path)

    def add_cpu_main_core(self, value):
        """Add CPU main core configuration.

        :param value: Main core option.
        :type value: str
        """
        path = ['cpu', 'main-core']
        self.add_config_item(self._nodeconfig, value, path)

    def add_cpu_corelist_workers(self, value):
        """Add CPU corelist-workers configuration.

        :param value: Corelist-workers option.
        :type value: str
        """
        path = ['cpu', 'corelist-workers']
        self.add_config_item(self._nodeconfig, value, path)

    def add_heapsize(self, value):
        """Add Heapsize configuration.

        :param value: Amount of heapsize.
        :type value: str
        """
        path = ['heapsize']
        self.add_config_item(self._nodeconfig, value, path)

    def add_api_trace(self):
        """Add API trace configuration."""
        path = ['api-trace', 'on']
        self.add_config_item(self._nodeconfig, '', path)

    def add_ip6_hash_buckets(self, value):
        """Add IP6 hash buckets configuration.

        :param value: Number of IP6 hash buckets.
        :type value: str
        """
        path = ['ip6', 'hash-buckets']
        self.add_config_item(self._nodeconfig, value, path)

    def add_ip6_heap_size(self, value):
        """Add IP6 heap-size configuration.

        :param value: IP6 Heapsize amount.
        :type value: str
        """
        path = ['ip6', 'heap-size']
        self.add_config_item(self._nodeconfig, value, path)

    def add_plugin_disable(self, *plugins):
        """Add plugin disable for specific plugin.

        :param plugins: Plugin(s) to disable.
        :type plugins: list
        """
        for plugin in plugins:
            path = ['plugins', 'plugin {0}'.format(plugin), 'disable']
            self.add_config_item(self._nodeconfig, ' ', path)

    def add_dpdk_no_multi_seg(self):
        """Add DPDK no-multi-seg configuration."""
        path = ['dpdk', 'no-multi-seg']
        self.add_config_item(self._nodeconfig, '', path)

    def add_snat(self, value='deterministic'):
        """Add SNAT configuration.

        :param value: SNAT mode.
        :type value: str
        """
        path = ['snat']
        self.add_config_item(self._nodeconfig, value, path)

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
        # a sudo's output ("sudo echo xxx > /path/to/file") does not
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
        for _ in range(retries):
            time.sleep(waittime)
            (ret, _, _) = \
                ssh.exec_command('echo show hardware-interfaces | '
                                 'nc 0 5002 || echo "VPP not yet running"')
            if ret == 0:
                break
        else:
            raise RuntimeError('VPP failed to restart on node {}'.
                               format(self._hostname))

    def apply_config_lxc(self, lxc_name, waittime=5, retries=12):
        """Generate and apply VPP configuration for node in a container.

        Use data from calls to this class to form a startup.conf file and
        replace /etc/vpp/startup.conf with it on node inside a container.

        :param lxc_name: LXC container name.
        :param waittime: Time to wait for VPP to restart (default 5 seconds).
        :param retries: Number of times (default 12) to re-try waiting.
        :type lxc_name: str
        :type waittime: int
        :type retries: int
        :raises RuntimeError: If writing config file failed, or restarting of
        VPP failed.
        """
        self.dump_config(self._nodeconfig)

        ssh = SSH()
        ssh.connect(self._node)

        # We're using this "| sudo tee" construct because redirecting
        # a sudo's output ("sudo echo xxx > /path/to/file") does not
        # work on most platforms...
        (ret, _, _) = \
            ssh.exec_command_lxc('echo "{0}" | sudo tee {1}'.
                                 format(self._vpp_config,
                                        self._vpp_config_filename), lxc_name)

        if ret != 0:
            raise RuntimeError('Writing config file failed in {0} to node {1}'.
                               format(lxc_name, self._hostname))

        # Instead of restarting, we'll do separate start and stop
        # actions. This way we don't care whether VPP was running
        # to begin with.
        ssh.exec_command_lxc('service {0} stop'.
                             format(self._vpp_service_name), lxc_name)
        (ret, _, _) = \
            ssh.exec_command_lxc('service {0} start'.
                                 format(self._vpp_service_name), lxc_name)
        if ret != 0:
            raise RuntimeError('Restarting VPP failed in {0} on node {1}'.
                               format(lxc_name, self._hostname))

        # Sleep <waittime> seconds, up to <retry> times,
        # and verify if VPP is running.
        for _ in range(retries):
            time.sleep(waittime)
            (ret, _, _) = \
                ssh.exec_command_lxc('echo show hardware-interfaces | '
                                     'nc 0 5002 || echo "VPP not yet running"',
                                     lxc_name)
            if ret == 0:
                break
        else:
            raise RuntimeError('VPP failed to restart in {0} on node {1}'.
                               format(self._hostname))