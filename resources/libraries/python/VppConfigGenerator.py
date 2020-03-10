# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""VPP Configuration File Generator library.

TODO: Support initialization with default values,
so that we do not need to have block of 6 "Add Unix" commands
in 7 various places of CSIT code.
"""

import re

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType
from resources.libraries.python.topology import Topology
from resources.libraries.python.VPPUtil import VPPUtil

__all__ = [u"VppConfigGenerator"]


def pci_dev_check(pci_dev):
    """Check if provided PCI address is in correct format.

    :param pci_dev: PCI address (expected format: xxxx:xx:xx.x).
    :type pci_dev: str
    :returns: True if PCI address is in correct format.
    :rtype: bool
    :raises ValueError: If PCI address is in incorrect format.
    """
    pattern = re.compile(
        r"^[0-9A-Fa-f]{4}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}\.[0-9A-Fa-f]$"
    )
    if not re.match(pattern, pci_dev):
        raise ValueError(
            f"PCI address {pci_dev} is not in valid format xxxx:xx:xx.x"
        )
    return True


class VppConfigGenerator:
    """VPP Configuration File Generator."""

    def __init__(self):
        """Initialize library."""
        # VPP Node to apply configuration on
        self._node = u""
        # Topology node key
        self._node_key = u""
        # VPP Configuration
        self._nodeconfig = dict()
        # Serialized VPP Configuration
        self._vpp_config = u""
        # VPP Service name
        self._vpp_service_name = u"vpp"
        # VPP Logfile location
        self._vpp_logfile = u"/tmp/vpe.log"
        # VPP Startup config location
        self._vpp_startup_conf = u"/etc/vpp/startup.conf"
        # VPP Startup config backup location
        self._vpp_startup_conf_backup = None

    def set_node(self, node, node_key=None):
        """Set DUT node.

        :param node: Node to store configuration on.
        :param node_key: Topology node key.
        :type node: dict
        :type node_key: str
        :raises RuntimeError: If Node type is not DUT.
        """
        if node[u"type"] != NodeType.DUT:
            raise RuntimeError(
                u"Startup config can only be applied to DUTnode."
            )
        self._node = node
        self._node_key = node_key

    def set_vpp_logfile(self, logfile):
        """Set VPP logfile location.

        :param logfile: VPP logfile location.
        :type logfile: str
        """
        self._vpp_logfile = logfile

    def set_vpp_startup_conf_backup(self, backup=u"/etc/vpp/startup.backup"):
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
            config[path[0]] = dict()
        elif isinstance(config[path[0]], str):
            config[path[0]] = dict() if config[path[0]] == u"" \
                else {config[path[0]]: u""}
        self.add_config_item(config[path[0]], value, path[1:])

    def dump_config(self, obj, level=-1):
        """Dump the startup configuration in VPP config format.

        :param obj: Python Object to print.
        :param level: Nested level for indentation.
        :type obj: Obj
        :type level: int
        :returns: nothing
        """
        indent = u"  "
        if level >= 0:
            self._vpp_config += f"{level * indent}{{\n"
        if isinstance(obj, dict):
            for key, val in obj.items():
                if hasattr(val, u"__iter__") and not isinstance(val, str):
                    self._vpp_config += f"{(level + 1) * indent}{key}\n"
                    self.dump_config(val, level + 1)
                else:
                    self._vpp_config += f"{(level + 1) * indent}{key} {val}\n"
        else:
            for val in obj:
                self._vpp_config += f"{(level + 1) * indent}{val}\n"
        if level >= 0:
            self._vpp_config += f"{level * indent}}}\n"

    def add_unix_log(self, value=None):
        """Add UNIX log configuration.

        :param value: Log file.
        :type value: str
        """
        path = [u"unix", u"log"]
        if value is None:
            value = self._vpp_logfile
        self.add_config_item(self._nodeconfig, value, path)

    def add_unix_cli_listen(self, value=u"/run/vpp/cli.sock"):
        """Add UNIX cli-listen configuration.

        :param value: CLI listen address and port or path to CLI socket.
        :type value: str
        """
        path = [u"unix", u"cli-listen"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_unix_gid(self, value=u"vpp"):
        """Add UNIX gid configuration.

        :param value: Gid.
        :type value: str
        """
        path = [u"unix", u"gid"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_unix_nodaemon(self):
        """Add UNIX nodaemon configuration."""
        path = [u"unix", u"nodaemon"]
        self.add_config_item(self._nodeconfig, u"", path)

    def add_unix_coredump(self):
        """Add UNIX full-coredump configuration."""
        path = [u"unix", u"full-coredump"]
        self.add_config_item(self._nodeconfig, u"", path)

    def add_unix_exec(self, value):
        """Add UNIX exec configuration."""
        path = [u"unix", u"exec"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_socksvr(self, socket=Constants.SOCKSVR_PATH):
        """Add socksvr configuration."""
        path = [u"socksvr", u"socket-name"]
        self.add_config_item(self._nodeconfig, socket, path)

    def add_api_segment_gid(self, value=u"vpp"):
        """Add API-SEGMENT gid configuration.

        :param value: Gid.
        :type value: str
        """
        path = [u"api-segment", u"gid"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_api_segment_global_size(self, value):
        """Add API-SEGMENT global-size configuration.

        :param value: Global size.
        :type value: str
        """
        path = [u"api-segment", u"global-size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_api_segment_api_size(self, value):
        """Add API-SEGMENT api-size configuration.

        :param value: API size.
        :type value: str
        """
        path = [u"api-segment", u"api-size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_buffers_per_numa(self, value):
        """Increase number of buffers allocated.

        :param value: Number of buffers allocated.
        :type value: int
        """
        path = [u"buffers", u"buffers-per-numa"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_buffers_default_data_size(self, value):
        """Increase buffers data-size allocated.

        :param value: Buffers data-size allocated.
        :type value: int
        """
        path = [u"buffers", u"default data-size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_dev(self, *devices):
        """Add DPDK PCI device configuration.

        :param devices: PCI device(s) (format xxxx:xx:xx.x)
        :type devices: tuple
        """
        for device in devices:
            if pci_dev_check(device):
                path = [u"dpdk", f"dev {device}"]
                self.add_config_item(self._nodeconfig, u"", path)

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
            path = [u"dpdk", f"dev {device}", parameter]
            self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_cryptodev(self, count):
        """Add DPDK Crypto PCI device configuration.

        :param count: Number of HW crypto devices to add.
        :type count: int
        """
        cryptodev = Topology.get_cryptodev(self._node)
        for i in range(count):
            cryptodev_config = re.sub(r"\d.\d$", f"1.{str(i)}", cryptodev)
            path = [u"dpdk", f"dev {cryptodev_config}"]
            self.add_config_item(self._nodeconfig, u"", path)
        self.add_dpdk_uio_driver(u"vfio-pci")

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
            cryptodev_config = f"vdev cryptodev_{sw_pmd_type}_pmd," \
                f"socket_id={str(socket_id)}"
            path = [u"dpdk", cryptodev_config]
            self.add_config_item(self._nodeconfig, u"", path)

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
        slaves_config = u"slave=" + u",slave=".join(
            slave if pci_dev_check(slave) else u"" for slave in slaves
        )
        ethbond_config = f"vdev eth_bond{ethbond_id}," \
            f"mode={mode}{slaves_config},xmit_policy={xmit_policy}"
        path = [u"dpdk", ethbond_config]
        self.add_config_item(self._nodeconfig, u"", path)

    def add_dpdk_dev_default_rxq(self, value):
        """Add DPDK dev default rxq configuration.

        :param value: Default number of rxqs.
        :type value: str
        """
        path = [u"dpdk", u"dev default", u"num-rx-queues"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_dev_default_txq(self, value):
        """Add DPDK dev default txq configuration.

        :param value: Default number of txqs.
        :type value: str
        """
        path = [u"dpdk", u"dev default", u"num-tx-queues"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_dev_default_rxd(self, value):
        """Add DPDK dev default rxd configuration.

        :param value: Default number of rxds.
        :type value: str
        """
        path = [u"dpdk", u"dev default", u"num-rx-desc"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_dev_default_txd(self, value):
        """Add DPDK dev default txd configuration.

        :param value: Default number of txds.
        :type value: str
        """
        path = [u"dpdk", u"dev default", u"num-tx-desc"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_log_level(self, value):
        """Add DPDK log-level configuration.

        :param value: Log level.
        :type value: str
        """
        path = [u"dpdk", u"log-level"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_vdev(self, count):
        """Add DPDK netsvc device configuration.

        :param count: Number of netsvc devices to add.
        :type count: int
        """
        for i in range(count):
            netsvcdev = f"vdev net_vdev_netvsc{str(i)},iface=eth{str(i+1)}"
            path = [u"dpdk", netsvcdev]
            self.add_config_item(self._nodeconfig, u"", path)

    def add_dpdk_no_pci(self):
        """Add DPDK no-pci."""
        path = [u"dpdk", u"no-pci"]
        self.add_config_item(self._nodeconfig, u"", path)

    def add_dpdk_uio_driver(self, value=None):
        """Add DPDK uio-driver configuration.

        :param value: DPDK uio-driver configuration. By default, driver will be
            loaded automatically from Topology file, still leaving option
            to manually override by parameter.
        :type value: str
        """
        if value is None:
            value = Topology.get_uio_driver(self._node)
        path = [u"dpdk", u"uio-driver"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_cpu_main_core(self, value):
        """Add CPU main core configuration.

        :param value: Main core option.
        :type value: str
        """
        path = [u"cpu", u"main-core"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_cpu_corelist_workers(self, value):
        """Add CPU corelist-workers configuration.

        :param value: Corelist-workers option.
        :type value: str
        """
        path = [u"cpu", u"corelist-workers"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_heapsize(self, value):
        """Add Heapsize configuration.

        :param value: Amount of heapsize.
        :type value: str
        """
        path = [u"heapsize"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_api_trace(self):
        """Add API trace configuration."""
        path = [u"api-trace", u"on"]
        self.add_config_item(self._nodeconfig, u"", path)

    def add_ip6_hash_buckets(self, value):
        """Add IP6 hash buckets configuration.

        :param value: Number of IP6 hash buckets.
        :type value: str
        """
        path = [u"ip6", u"hash-buckets"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_ip6_heap_size(self, value):
        """Add IP6 heap-size configuration.

        :param value: IP6 Heapsize amount.
        :type value: str
        """
        path = [u"ip6", u"heap-size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_ip_heap_size(self, value):
        """Add IP heap-size configuration.

        :param value: IP Heapsize amount.
        :type value: str
        """
        path = [u"ip", u"heap-size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_statseg_size(self, value):
        """Add stats segment heap size configuration.

        :param value: Stats heapsize amount.
        :type value: str
        """
        path = [u"statseg", u"size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_statseg_per_node_counters(self, value):
        """Add stats per-node-counters configuration.

        :param value: "on" to switch the counters on.
        :type value: str
        """
        path = [u"statseg", u"per-node-counters"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_plugin(self, state, *plugins):
        """Add plugin section for specific plugin(s).

        :param state: State of plugin [enable|disable].
        :param plugins: Plugin(s) to disable.
        :type state: str
        :type plugins: list
        """
        for plugin in plugins:
            path = [u"plugins", f"plugin {plugin}", state]
            self.add_config_item(self._nodeconfig, u" ", path)

    def add_dpdk_no_multi_seg(self):
        """Add DPDK no-multi-seg configuration."""
        path = [u"dpdk", u"no-multi-seg"]
        self.add_config_item(self._nodeconfig, u"", path)

    def add_dpdk_no_tx_checksum_offload(self):
        """Add DPDK no-tx-checksum-offload configuration."""
        path = [u"dpdk", u"no-tx-checksum-offload"]
        self.add_config_item(self._nodeconfig, u"", path)

    def add_nat(self, value=u"deterministic"):
        """Add NAT configuration.

        :param value: NAT mode.
        :type value: str
        """
        path = [u"nat"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_nsim_poll_main_thread(self):
        """Add NSIM poll-main-thread configuration."""
        path = [u"nsim", u"poll-main-thread"]
        self.add_config_item(self._nodeconfig, u"", path)

    def add_tcp_congestion_control_algorithm(self, value=u"cubic"):
        """Add TCP congestion control algorithm.

        :param value: The congestion control algorithm to use. Example: cubic
        :type value: str
        """
        path = [u"tcp", u"cc-algo"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_tcp_preallocated_connections(self, value):
        """Add TCP pre-allocated connections.

        :param value: The number of pre-allocated connections.
        :type value: int
        """
        path = [u"tcp", u"preallocated-connections"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_tcp_preallocated_half_open_connections(self, value):
        """Add TCP pre-allocated half open connections.

        :param value: The number of pre-allocated half open connections.
        :type value: int
        """
        path = [u"tcp", u"preallocated-half-open-connections"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_enable(self):
        """Add session enable."""
        path = [u"session", u"enable"]
        self.add_config_item(self._nodeconfig, u"", path)

    def add_session_event_queues_memfd_segment(self):
        """Add session event queue memfd segment."""
        path = [u"session", u"evt_qs_memfd_seg"]
        self.add_config_item(self._nodeconfig, u"", path)

    def add_session_event_queue_length(self, value):
        """Add session event queue length.

        :param value: Session event queue length.
        :type value: int
        """
        path = [u"session", u"event-queue-length"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_event_queues_segment_size(self, value):
        """Add session event queue length.

        :param value: Session event queue segment size.
        :type value: str
        """
        path = [u"session", u"evt_qs_seg_size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_preallocated_sessions(self, value):
        """Add the number of pre-allocated sessions.

        :param value: Number of pre-allocated sessions.
        :type value: int
        """
        path = [u"session", u"preallocated-sessions"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_v4_session_table_buckets(self, value):
        """Add number of v4 session table buckets to the config.

        :param value: Number of v4 session table buckets.
        :type value: int
        """
        path = [u"session", u"v4-session-table-buckets"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_v4_session_table_memory(self, value):
        """Add the size of v4 session table memory.

        :param value: Size of v4 session table memory.
        :type value: str
        """
        path = [u"session", u"v4-session-table-memory"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_v4_halfopen_table_buckets(self, value):
        """Add the number of v4 halfopen table buckets.

        :param value: Number of v4 halfopen table buckets.
        :type value: int
        """
        path = [u"session", u"v4-halfopen-table-buckets"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_v4_halfopen_table_memory(self, value):
        """Add the size of v4 halfopen table memory.

        :param value: Size of v4 halfopen table memory.
        :type value: str
        """
        path = [u"session", u"v4-halfopen-table-memory"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_local_endpoints_table_buckets(self, value):
        """Add the number of local endpoints table buckets.

        :param value: Number of local endpoints table buckets.
        :type value: int
        """
        path = [u"session", u"local-endpoints-table-buckets"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_local_endpoints_table_memory(self, value):
        """Add the size of local endpoints table memory.

        :param value: Size of local endpoints table memory.
        :type value: str
        """
        path = [u"session", u"local-endpoints-table-memory"]
        self.add_config_item(self._nodeconfig, value, path)

    def write_config(self, filename=None):
        """Generate and write VPP startup configuration to file.

        Use data from calls to this class to form a startup.conf file and
        replace /etc/vpp/startup.conf with it on topology node.

        :param filename: Startup configuration file name.
        :type filename: str
        """
        self.dump_config(self._nodeconfig)

        if filename is None:
            filename = self._vpp_startup_conf

        if self._vpp_startup_conf_backup is not None:
            cmd = f"cp {self._vpp_startup_conf} {self._vpp_startup_conf_backup}"
            exec_cmd_no_error(
                self._node, cmd, sudo=True, message=u"Copy config file failed!"
            )

        cmd = f"echo \"{self._vpp_config}\" | sudo tee {filename}"
        exec_cmd_no_error(
            self._node, cmd, message=u"Writing config file failed!"
        )

    def apply_config(self, filename=None, verify_vpp=True):
        """Generate and write VPP startup configuration to file and restart VPP.

        Use data from calls to this class to form a startup.conf file and
        replace /etc/vpp/startup.conf with it on topology node.

        :param filename: Startup configuration file name.
        :param verify_vpp: Verify VPP is running after restart.
        :type filename: str
        :type verify_vpp: bool
        """
        self.write_config(filename=filename)

        VPPUtil.restart_vpp_service(self._node, self._node_key)
        if verify_vpp:
            VPPUtil.verify_vpp(self._node)

    def restore_config(self):
        """Restore VPP startup.conf from backup."""
        cmd = f"cp {self._vpp_startup_conf_backup} {self._vpp_startup_conf}"
        exec_cmd_no_error(
            self._node, cmd, sudo=True, message=u"Copy config file failed!"
        )
