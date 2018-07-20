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

"""VPP Configuration File Generator library."""

import re
import time

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.topology import NodeType
from resources.libraries.python.topology import Topology

__all__ = ['VppConfigGenerator']


def pci_dev_check(pci_dev):
    """Check if provided PCI address is in correct format.

    :param pci_dev: PCI address (expected format: xxxx:xx:xx.x).
    :type pci_dev: str
    :returns: True if PCI address is in correct format.
    :rtype: bool
    :raises ValueError: If PCI address is in incorrect format.
    """
    pattern = re.compile("^[0-9A-Fa-f]{4}:[0-9A-Fa-f]{2}:"
                         "[0-9A-Fa-f]{2}\\.[0-9A-Fa-f]$")
    if not pattern.match(pci_dev):
        raise ValueError('PCI address {addr} is not in valid format '
                         'xxxx:xx:xx.x'.format(addr=pci_dev))
    return True


class VppConfigGenerator(object):
    """VPP Configuration File Generator."""

    def __init__(self):
        """Initialize library."""
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
        # VPP Logfile location
        self._vpp_logfile = '/tmp/vpe.log'
        # VPP Startup config location
        self._vpp_startup_conf = '/etc/vpp/startup.conf'
        # VPP Startup config backup location
        self._vpp_startup_conf_backup = None

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

    def set_vpp_logfile(self, logfile):
        """Set VPP logfile location.

        :param logfile: VPP logfile location.
        :type logfile: str
        """
        self._vpp_logfile = logfile

    def set_vpp_startup_conf_backup(self, backup='/etc/vpp/startup.backup'):
        """Set VPP startup configuration backup.

        :param backup: VPP logfile location.
        :type backup: str
        """
        self._vpp_startup_conf_backup = backup

    def get_config_str(self):
        """Get dumped startup configuration in VPP config format.

        :returns: Startup configuration in VPP config format.
        :rtype: str
        """
        self.dump_config(self._nodeconfig)
        return self._vpp_config

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
        if path[0] not in config:
            config[path[0]] = {}
        elif isinstance(config[path[0]], str):
            config[path[0]] = {} if config[path[0]] == '' \
                else {config[path[0]]: ''}
        self.add_config_item(config[path[0]], value, path[1:])

    def dump_config(self, obj, level=-1):
        """Dump the startup configuration in VPP config format.

        :param obj: Python Object to print.
        :param level: Nested level for indentation.
        :type obj: Obj
        :type level: int
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

    def add_unix_log(self, value=None):
        """Add UNIX log configuration.

        :param value: Log file.
        :type value: str
        """
        path = ['unix', 'log']
        if value is None:
            value = self._vpp_logfile
        self.add_config_item(self._nodeconfig, value, path)

    def add_unix_cli_listen(self, value='/run/vpp/cli.sock'):
        """Add UNIX cli-listen configuration.

        :param value: CLI listen address and port or path to CLI socket.
        :type value: str
        """
        path = ['unix', 'cli-listen']
        self.add_config_item(self._nodeconfig, value, path)

    def add_unix_gid(self, value='vpp'):
        """Add UNIX gid configuration.

        :param value: Gid.
        :type value: str
        """
        path = ['unix', 'gid']
        self.add_config_item(self._nodeconfig, value, path)

    def add_unix_nodaemon(self):
        """Add UNIX nodaemon configuration."""
        path = ['unix', 'nodaemon']
        self.add_config_item(self._nodeconfig, '', path)

    def add_unix_coredump(self):
        """Add UNIX full-coredump configuration."""
        path = ['unix', 'full-coredump']
        self.add_config_item(self._nodeconfig, '', path)

    def add_unix_exec(self, value):
        """Add UNIX exec configuration."""
        path = ['unix', 'exec']
        self.add_config_item(self._nodeconfig, value, path)

    def add_api_segment_gid(self, value='vpp'):
        """Add API-SEGMENT gid configuration.

        :param value: Gid.
        :type value: str
        """
        path = ['api-segment', 'gid']
        self.add_config_item(self._nodeconfig, value, path)

    def add_api_segment_global_size(self, value):
        """Add API-SEGMENT global-size configuration.

        :param value: Global size.
        :type value: str
        """
        path = ['api-segment', 'global-size']
        self.add_config_item(self._nodeconfig, value, path)

    def add_api_segment_api_size(self, value):
        """Add API-SEGMENT api-size configuration.

        :param value: API size.
        :type value: str
        """
        path = ['api-segment', 'api-size']
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_dev(self, *devices):
        """Add DPDK PCI device configuration.

        :param devices: PCI device(s) (format xxxx:xx:xx.x)
        :type devices: tuple
        """
        for device in devices:
            if pci_dev_check(device):
                path = ['dpdk', 'dev {0}'.format(device)]
                self.add_config_item(self._nodeconfig, '', path)

    def add_dpdk_dev_parameter(self, device, parameter, value):
        """Add parameter for DPDK device.

        :param device: PCI device (format xxxx:xx:xx.x).
        :param parameter: Parameter name.
        :param value: Parameter value.
        :type device: str
        :type parameter: str
        :type value: str
        """
        if pci_dev_check(device):
            path = ['dpdk', 'dev {0}'.format(device), parameter]
            self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_cryptodev(self, count):
        """Add DPDK Crypto PCI device configuration.

        :param count: Number of HW crypto devices to add.
        :type count: int
        """
        cryptodev = Topology.get_cryptodev(self._node)
        for i in range(count):
            cryptodev_config = 'dev {0}'.format(
                re.sub(r'\d.\d$', '1.'+str(i), cryptodev))
            path = ['dpdk', cryptodev_config]
            self.add_config_item(self._nodeconfig, '', path)
        self.add_dpdk_uio_driver('igb_uio')

    def add_dpdk_sw_cryptodev(self, sw_pmd_type, socket_id, count):
        """Add DPDK SW Crypto device configuration.

        :param sw_pmd_type: Type of SW crypto device PMD to add.
        :param socket_id: Socket ID.
        :param count: Number of SW crypto devices to add.
        :type sw_pmd_type: str
        :type socket_id: int
        :type count: int
        """
        for _ in range(count):
            cryptodev_config = 'vdev cryptodev_{0}_pmd,socket_id={1}'.\
                format(sw_pmd_type, str(socket_id))
            path = ['dpdk', cryptodev_config]
            self.add_config_item(self._nodeconfig, '', path)

    def add_dpdk_eth_bond_dev(self, ethbond_id, mode, xmit_policy, *slaves):
        """Add DPDK Eth_bond device configuration.

        :param ethbond_id: Eth_bond device ID.
        :param mode: Link bonding mode.
        :param xmit_policy: Transmission policy.
        :param slaves: PCI device(s) to be bonded (format xxxx:xx:xx.x).
        :type ethbond_id: str or int
        :type mode: str or int
        :type xmit_policy: str
        :type slaves: list
        """
        slaves_config = ',slave=' + \
                        ',slave='.join(slave if pci_dev_check(slave) else ''
                                       for slave in slaves)
        ethbond_config = 'vdev eth_bond{id},mode={mode}{slaves},' \
                         'xmit_policy={xmit_pol}'.format(id=ethbond_id,
                                                         mode=mode,
                                                         slaves=slaves_config,
                                                         xmit_pol=xmit_policy)
        path = ['dpdk', ethbond_config]
        self.add_config_item(self._nodeconfig, '', path)

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

    def add_dpdk_dev_default_rxd(self, value):
        """Add DPDK dev default rxd configuration.

        :param value: Default number of rxds.
        :type value: str
        """
        path = ['dpdk', 'dev default', 'num-rx-desc']
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_dev_default_txd(self, value):
        """Add DPDK dev default txd configuration.

        :param value: Default number of txds.
        :type value: str
        """
        path = ['dpdk', 'dev default', 'num-tx-desc']
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_log_level(self, value):
        """Add DPDK log-level configuration.

        :param value: Log level.
        :type value: str
        """
        path = ['dpdk', 'log-level']
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_socketmem(self, value):
        """Add DPDK socket memory configuration.

        :param value: Socket memory size.
        :type value: str
        """
        path = ['dpdk', 'socket-mem']
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_num_mbufs(self, value):
        """Add DPDK number of I/O buffers.

        :param value: Number of I/O buffers.
        :type value: int
        """
        path = ['dpdk', 'num-mbufs']
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_no_pci(self):
        """Add DPDK no-pci."""
        path = ['dpdk', 'no-pci']
        self.add_config_item(self._nodeconfig, '', path)

    def add_dpdk_uio_driver(self, value=None):
        """Add DPDK uio-driver configuration.

        :param value: DPDK uio-driver configuration. By default, driver will be
                      loaded automatically from Topology file, still leaving
                      option to manually override by parameter.
        :type value: str
        """
        if value is None:
            value = Topology.get_uio_driver(self._node)
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

    def add_ip_heap_size(self, value):
        """Add IP heap-size configuration.

        :param value: IP Heapsize amount.
        :type value: str
        """
        path = ['ip', 'heap-size']
        self.add_config_item(self._nodeconfig, value, path)

    def add_statseg_size(self, value):
        """Add stats segment heap size configuration.

        :param value: Stats heapsize amount.
        :type value: str
        """
        path = ['statseg', 'size']
        self.add_config_item(self._nodeconfig, value, path)

    def add_plugin(self, state, *plugins):
        """Add plugin section for specific plugin(s).

        :param state: State of plugin [enable|disable].
        :param plugins: Plugin(s) to disable.
        :type state: str
        :type plugins: list
        """
        for plugin in plugins:
            path = ['plugins', 'plugin {0}'.format(plugin), state]
            self.add_config_item(self._nodeconfig, ' ', path)

    def add_dpdk_no_multi_seg(self):
        """Add DPDK no-multi-seg configuration."""
        path = ['dpdk', 'no-multi-seg']
        self.add_config_item(self._nodeconfig, '', path)

    def add_dpdk_no_tx_checksum_offload(self):
        """Add DPDK no-tx-checksum-offload configuration."""
        path = ['dpdk', 'no-tx-checksum-offload']
        self.add_config_item(self._nodeconfig, '', path)

    def add_nat(self, value='deterministic'):
        """Add NAT configuration.

        :param value: NAT mode.
        :type value: str
        """
        path = ['nat']
        self.add_config_item(self._nodeconfig, value, path)

    def add_tcp_preallocated_connections(self, value):
        """Add TCP pre-allocated connections.

        :param value: The number of pre-allocated connections.
        :type value: int
        """
        path = ['tcp', 'preallocated-connections']
        self.add_config_item(self._nodeconfig, value, path)

    def add_tcp_preallocated_half_open_connections(self, value):
        """Add TCP pre-allocated half open connections.

        :param value: The number of pre-allocated half open connections.
        :type value: int
        """
        path = ['tcp', 'preallocated-half-open-connections']
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_event_queue_length(self, value):
        """Add session event queue length.

        :param value: Session event queue length.
        :type value: int
        """
        path = ['session', 'event-queue-length']
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_preallocated_sessions(self, value):
        """Add the number of pre-allocated sessions.

        :param value: Number of pre-allocated sessions.
        :type value: int
        """
        path = ['session', 'preallocated-sessions']
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_v4_session_table_buckets(self, value):
        """Add number of v4 session table buckets to the config.

        :param value: Number of v4 session table buckets.
        :type value: int
        """
        path = ['session', 'v4-session-table-buckets']
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_v4_session_table_memory(self, value):
        """Add the size of v4 session table memory.

        :param value: Size of v4 session table memory.
        :type value: str
        """
        path = ['session', 'v4-session-table-memory']
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_v4_halfopen_table_buckets(self, value):
        """Add the number of v4 halfopen table buckets.

        :param value: Number of v4 halfopen table buckets.
        :type value: int
        """
        path = ['session', 'v4-halfopen-table-buckets']
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_v4_halfopen_table_memory(self, value):
        """Add the size of v4 halfopen table memory.

        :param value: Size of v4 halfopen table memory.
        :type value: str
        """
        path = ['session', 'v4-halfopen-table-memory']
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_local_endpoints_table_buckets(self, value):
        """Add the number of local endpoints table buckets.

        :param value: Number of local endpoints table buckets.
        :type value: int
        """
        path = ['session', 'local-endpoints-table-buckets']
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_local_endpoints_table_memory(self, value):
        """Add the size of local endpoints table memory.

        :param value: Size of local endpoints table memory.
        :type value: str
        """
        path = ['session', 'local-endpoints-table-memory']
        self.add_config_item(self._nodeconfig, value, path)

    def apply_config(self, filename=None, retries=60, restart_vpp=True):
        """Generate and apply VPP configuration for node.

        Use data from calls to this class to form a startup.conf file and
        replace /etc/vpp/startup.conf with it on node.

        :param filename: Startup configuration file name.
        :param retries: Number of times (default 60) to re-try waiting.
        :param restart_vpp: Whether to restart VPP.
        :type filename: str
        :type retries: int
        :type restart_vpp: bool.
        :raises RuntimeError: If writing config file failed or restart of VPP
            failed or backup of VPP startup.conf failed.
        """
        self.dump_config(self._nodeconfig)

        ssh = SSH()
        ssh.connect(self._node)

        if filename is None:
            filename = self._vpp_startup_conf

        if self._vpp_startup_conf_backup is not None:
            ret, _, _ = \
                ssh.exec_command('sudo cp {src} {dest}'.
                                 format(src=self._vpp_startup_conf,
                                        dest=self._vpp_startup_conf_backup))
            if ret != 0:
                raise RuntimeError('Backup of config file failed on node '
                                   '{name}'.format(name=self._hostname))

        ret, _, _ = \
            ssh.exec_command('echo "{config}" | sudo tee {filename}'.
                             format(config=self._vpp_config,
                                    filename=filename))

        if ret != 0:
            raise RuntimeError('Writing config file failed to node {name}'.
                               format(name=self._hostname))

        if restart_vpp:
            DUTSetup.start_service(self._node, Constants.VPP_UNIT)

            # Sleep <waittime> seconds, up to <retry> times,
            # and verify if VPP is running.
            for _ in range(retries):
                time.sleep(1)
                ret, stdout, _ = \
                    ssh.exec_command_sudo('vppctl show pci')
                if ret == 0 and 'Connection refused' not in stdout:
                    break
            else:
                raise RuntimeError('VPP failed to restart on node {name}'.
                                   format(name=self._hostname))

    def restore_config(self):
        """Restore VPP startup.conf from backup.

        :raises RuntimeError: When restoration of startup.conf file failed.
        """

        ssh = SSH()
        ssh.connect(self._node)

        ret, _, _ = ssh.exec_command('sudo cp {src} {dest}'.
                                     format(src=self._vpp_startup_conf_backup,
                                            dest=self._vpp_startup_conf))
        if ret != 0:
            raise RuntimeError('Restoration of config file failed on node '
                               '{name}'.format(name=self._hostname))
