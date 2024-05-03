# Copyright (c) 2024 Cisco and/or its affiliates.
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

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType
from resources.libraries.python.topology import Topology
from resources.libraries.python.VPPUtil import VPPUtil

__all__ = ["VppConfigGenerator", "VppInitConfig"]


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
        # DUT Node to apply VPP configuration on
        self._node = ""
        # Topology node key
        self._node_key = ""
        # VPP Configuration
        self._nodeconfig = dict()
        # Serialized VPP Configuration
        self._vpp_config = ""
        # VPP Service name
        self._vpp_service_name = "vpp"
        # VPP Startup config location
        self._vpp_startup_conf = "/etc/vpp/startup.conf"

    def set_node(self, node, node_key=None):
        """Set DUT node.

        :param node: Node to store configuration on.
        :param node_key: Topology node key.
        :type node: dict
        :type node_key: str
        :raises RuntimeError: If Node type is not DUT.
        """
        if node["type"] != NodeType.DUT:
            raise RuntimeError(
                "Startup config can only be applied to DUTnode."
            )
        self._node = node
        self._node_key = node_key

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
            config[path[0]] = dict() if config[path[0]] == "" \
                else {config[path[0]]: ""}
        self.add_config_item(config[path[0]], value, path[1:])

    def dump_config(self, obj, level=-1):
        """Dump the startup configuration in VPP config format.

        :param obj: Python Object to print.
        :param level: Nested level for indentation.
        :type obj: Obj
        :type level: int
        :returns: nothing
        """
        indent = "  "
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

    def add_unix_log(self, value="/var/log/vpp/vpp.log"):
        """Add UNIX log configuration.

        :param value: Log file.
        :type value: str
        """
        path = ["unix", "log"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_unix_cli_listen(self, value="/run/vpp/cli.sock"):
        """Add UNIX cli-listen configuration.

        :param value: CLI listen address and port or path to CLI socket.
        :type value: str
        """
        path = ["unix", "cli-listen"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_unix_cli_no_pager(self):
        """Add UNIX cli-no-pager configuration."""
        path = ["unix", "cli-no-pager"]
        self.add_config_item(self._nodeconfig, "", path)

    def add_unix_gid(self, value="vpp"):
        """Add UNIX gid configuration.

        :param value: Gid.
        :type value: str
        """
        path = ["unix", "gid"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_unix_nodaemon(self):
        """Add UNIX nodaemon configuration."""
        path = ["unix", "nodaemon"]
        self.add_config_item(self._nodeconfig, "", path)

    def add_unix_coredump(self):
        """Add UNIX full-coredump configuration."""
        path = ["unix", "full-coredump"]
        self.add_config_item(self._nodeconfig, "", path)

    def add_unix_exec(self, value):
        """Add UNIX exec configuration."""
        path = ["unix", "exec"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_socksvr(self, socket=Constants.SOCKSVR_PATH):
        """Add socksvr configuration."""
        path = ["socksvr", "socket-name"]
        self.add_config_item(self._nodeconfig, socket, path)

    def add_graph_node_variant(self, variant=Constants.GRAPH_NODE_VARIANT):
        """Add default graph node variant.

        :param value: Graph node variant default value.
        :type value: str
        """
        if variant == "":
            return
        variant_list = ["hsw", "skx", "icl"]
        if variant not in variant_list:
            raise ValueError("Invalid graph node variant value")
        path = ["node", "default", "variant"]
        self.add_config_item(self._nodeconfig, variant, path)

    def add_api_segment_gid(self, value="vpp"):
        """Add api-segment gid configuration.

        :param value: Gid.
        :type value: str
        """
        path = ["api-segment", "gid"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_api_segment_global_size(self, value):
        """Add api-segment global-size configuration.

        :param value: Global size.
        :type value: str
        """
        path = ["api-segment", "global-size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_api_segment_prefix(self, value="vpp"):
        """Add api-segment prefix configuration.

        :param value: Gid.
        :type value: str
        """
        path = ["api-segment", "prefix"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_api_segment_api_size(self, value):
        """Add api-segment api-size configuration.

        :param value: API size.
        :type value: str
        """
        path = ["api-segment", "api-size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_buffers_per_numa(self, value):
        """Increase number of buffers allocated.

        :param value: Number of buffers allocated.
        :type value: int
        """
        path = ["buffers", "buffers-per-numa"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_buffers_default_data_size(self, value):
        """Increase buffers data-size allocated.

        :param value: Buffers data-size allocated.
        :type value: int
        """
        path = ["buffers", "default data-size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_dev(self, *devices):
        """Add DPDK PCI device configuration.

        :param devices: PCI device(s) (format xxxx:xx:xx.x)
        :type devices: tuple
        """
        for device in devices:
            if pci_dev_check(device):
                path = ["dpdk", f"dev {device}"]
                self.add_config_item(self._nodeconfig, "", path)

    def add_dpdk_cryptodev(self, count, num_rx_queues=1):
        """Add DPDK Crypto PCI device configuration.

        :param count: Number of HW crypto devices to add.
        :param num_rx_queues: Number of RX queues per QAT interface.
        :type count: int
        :type num_rx_queues: int
        """
        cryptodevs = Topology.get_cryptodev(self._node)
        for device in cryptodevs.values():
            for i in range(int(count/len(cryptodevs))):
                numvfs = device["numvfs"]
                computed = f"{(i+1)//numvfs}.{(i+1)%numvfs}"
                addr = re.sub(r"\d.\d$", computed, device["pci_address"])
                path = ["dpdk", f"dev {addr}", "num-rx-queues"]
                self.add_config_item(self._nodeconfig, num_rx_queues, path)
        self.add_dpdk_uio_driver("vfio-pci")

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
            path = ["dpdk", cryptodev_config]
            self.add_config_item(self._nodeconfig, "", path)

    def add_dpdk_dev_default_rxq(self, value):
        """Add DPDK dev default rxq configuration.

        :param value: Default number of rxqs.
        :type value: str
        """
        path = ["dpdk", "dev default", "num-rx-queues"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_dev_default_txq(self, value):
        """Add DPDK dev default txq configuration.

        :param value: Default number of txqs.
        :type value: str
        """
        path = ["dpdk", "dev default", "num-tx-queues"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_dev_default_rxd(self, value):
        """Add DPDK dev default rxd configuration.

        :param value: Default number of rxds.
        :type value: str
        """
        path = ["dpdk", "dev default", "num-rx-desc"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_dev_default_txd(self, value):
        """Add DPDK dev default txd configuration.

        :param value: Default number of txds.
        :type value: str
        """
        path = ["dpdk", "dev default", "num-tx-desc"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_dev_default_tso(self):
        """Add DPDK dev default tso configuration."""
        path = [u"dpdk", u"dev default", u"tso"]
        self.add_config_item(self._nodeconfig, "on", path)

    def add_dpdk_log_level(self, value):
        """Add DPDK log-level configuration.

        :param value: Log level.
        :type value: str
        """
        path = ["dpdk", "log-level"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_no_pci(self):
        """Add DPDK no-pci."""
        path = ["dpdk", "no-pci"]
        self.add_config_item(self._nodeconfig, "", path)

    def add_dpdk_uio_driver(self, value=None):
        """Add DPDK uio-driver configuration.

        :param value: DPDK uio-driver configuration. By default, driver will be
            loaded automatically from Topology file, still leaving option
            to manually override by parameter.
        :type value: str
        """
        if value is None:
            value = Topology.get_uio_driver(self._node)
        path = ["dpdk", "uio-driver"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_max_simd_bitwidth(self, variant=Constants.GRAPH_NODE_VARIANT):
        """Add DPDK max-simd-bitwidth configuration.

        :param value: Graph node variant default value.
        :type value: str
        """
        if variant == "icl":
            value = 512
        elif variant in ["skx", "hsw"]:
            value = 256
        else:
            return

        path = ["dpdk", "max-simd-bitwidth"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_dpdk_enable_tcp_udp_checksum(self):
        """Add DPDK enable-tcp-udp-checksum configuration."""
        path = [u"dpdk", u"enable-tcp-udp-checksum"]
        self.add_config_item(self._nodeconfig, u"", path)

    def add_cpu_main_core(self, value):
        """Add CPU main core configuration.

        :param value: Main core option.
        :type value: str
        """
        path = ["cpu", "main-core"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_cpu_corelist_workers(self, value):
        """Add CPU corelist-workers configuration.

        :param value: Corelist-workers option.
        :type value: str
        """
        path = ["cpu", "corelist-workers"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_main_heap_size(self, value):
        """Add Main Heap Size configuration.

        :param value: Amount of heap.
        :type value: str
        """
        path = ["memory", "main-heap-size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_main_heap_page_size(self, value):
        """Add Main Heap Page Size configuration.

        :param value: Heap page size.
        :type value: str
        """
        path = ["memory", "main-heap-page-size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_default_hugepage_size(self, value=Constants.DEFAULT_HUGEPAGE_SIZE):
        """Add Default Hugepage Size configuration.

        :param value: Hugepage size.
        :type value: str
        """
        path = ["memory", "default-hugepage-size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_api_trace(self):
        """Add API trace configuration."""
        path = ["api-trace", "on"]
        self.add_config_item(self._nodeconfig, "", path)

    def add_ip6_hash_buckets(self, value):
        """Add IP6 hash buckets configuration.

        :param value: Number of IP6 hash buckets.
        :type value: str
        """
        path = ["ip6", "hash-buckets"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_ip6_heap_size(self, value):
        """Add IP6 heap-size configuration.

        :param value: IP6 Heapsize amount.
        :type value: str
        """
        path = ["ip6", "heap-size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_ipsec_spd_flow_cache_ipv4_inbound(self, value):
        """Add IPsec spd flow cache for IP4 inbound.

        :param value: "on" to enable spd flow cache.
        :type value: str
        """
        path = ["ipsec", "ipv4-inbound-spd-flow-cache"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_ipsec_spd_flow_cache_ipv4_outbound(self, value):
        """Add IPsec spd flow cache for IP4 outbound.

        :param value: "on" to enable spd flow cache.
        :type value: str
        """
        path = ["ipsec", "ipv4-outbound-spd-flow-cache"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_ipsec_spd_fast_path_ipv4_inbound(self, value):
        """Add IPsec spd fast path for IP4 inbound.

        :param value: "on" to enable spd fast path.
        :type value: str
        """
        path = [u"ipsec", u"ipv4-inbound-spd-fast-path"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_ipsec_spd_fast_path_ipv4_outbound(self, value):
        """Add IPsec spd fast path for IP4 outbound.

        :param value: "on" to enable spd fast path.
        :type value: str
        """
        path = ["ipsec", "ipv4-outbound-spd-fast-path"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_ipsec_spd_fast_path_num_buckets(self, value):
        """Add num buckets for IPsec spd fast path.

        :param value: Number of buckets.
        :type value: int
        """
        path = ["ipsec", "spd-fast-path-num-buckets"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_statseg_size(self, value):
        """Add Stats Heap Size configuration.

        :param value: Stats heapsize amount.
        :type value: str
        """
        path = ["statseg", "size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_statseg_page_size(self, value):
        """Add Stats Heap Page Size configuration.

        :param value: Stats heapsize amount.
        :type value: str
        """
        path = ["statseg", "page-size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_statseg_per_node_counters(self, value):
        """Add stats per-node-counters configuration.

        :param value: "on" to switch the counters on.
        :type value: str
        """
        path = ["statseg", "per-node-counters"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_plugin(self, state, *plugins):
        """Add plugin section for specific plugin(s).

        :param state: State of plugin [enable|disable].
        :param plugins: Plugin(s) to disable.
        :type state: str
        :type plugins: list
        """
        for plugin in plugins:
            path = ["plugins", f"plugin {plugin}", state]
            self.add_config_item(self._nodeconfig, " ", path)

    def add_dpdk_no_multi_seg(self):
        """Add DPDK no-multi-seg configuration."""
        path = ["dpdk", "no-multi-seg"]
        self.add_config_item(self._nodeconfig, "", path)

    def add_dpdk_no_tx_checksum_offload(self):
        """Add DPDK no-tx-checksum-offload configuration."""
        path = ["dpdk", "no-tx-checksum-offload"]
        self.add_config_item(self._nodeconfig, "", path)

    def add_nat(self, value="deterministic"):
        """Add NAT mode configuration.

        :param value: NAT mode.
        :type value: str
        """
        path = ["nat", value]
        self.add_config_item(self._nodeconfig, "", path)

    def add_nat_max_translations_per_thread(self, value):
        """Add NAT max. translations per thread number configuration.

        :param value: NAT mode.
        :type value: str
        """
        path = ["nat", "max translations per thread"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_nsim_poll_main_thread(self):
        """Add NSIM poll-main-thread configuration."""
        path = ["nsim", "poll-main-thread"]
        self.add_config_item(self._nodeconfig, "", path)

    def add_tcp_congestion_control_algorithm(self, value="cubic"):
        """Add TCP congestion control algorithm.

        :param value: The congestion control algorithm to use. Example: cubic
        :type value: str
        """
        path = ["tcp", "cc-algo"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_tcp_preallocated_connections(self, value):
        """Add TCP pre-allocated connections.

        :param value: The number of pre-allocated connections.
        :type value: int
        """
        path = ["tcp", "preallocated-connections"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_tcp_preallocated_half_open_connections(self, value):
        """Add TCP pre-allocated half open connections.

        :param value: The number of pre-allocated half open connections.
        :type value: int
        """
        path = ["tcp", "preallocated-half-open-connections"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_tcp_tso(self):
        """Add TCP tso configuration."""
        path = [u"tcp", u"tso"]
        self.add_config_item(self._nodeconfig, u"", path)

    def add_session_enable(self):
        """Add session enable."""
        path = ["session", "enable"]
        self.add_config_item(self._nodeconfig, "", path)

    def add_session_app_socket_api(self):
        """Use session app socket api."""
        path = ["session", "use-app-socket-api"]
        self.add_config_item(self._nodeconfig, "", path)

    def add_session_event_queues_memfd_segment(self):
        """Add session event queue memfd segment."""
        path = ["session", "evt_qs_memfd_seg"]
        self.add_config_item(self._nodeconfig, "", path)

    def add_session_event_queue_length(self, value):
        """Add session event queue length.

        :param value: Session event queue length.
        :type value: int
        """
        path = ["session", "event-queue-length"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_event_queues_segment_size(self, value):
        """Add session event queue length.

        :param value: Session event queue segment size.
        :type value: str
        """
        path = ["session", "evt_qs_seg_size"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_preallocated_sessions(self, value):
        """Add the number of pre-allocated sessions.

        :param value: Number of pre-allocated sessions.
        :type value: int
        """
        path = ["session", "preallocated-sessions"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_v4_session_table_buckets(self, value):
        """Add number of v4 session table buckets to the config.

        :param value: Number of v4 session table buckets.
        :type value: int
        """
        path = ["session", "v4-session-table-buckets"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_v4_session_table_memory(self, value):
        """Add the size of v4 session table memory.

        :param value: Size of v4 session table memory.
        :type value: str
        """
        path = ["session", "v4-session-table-memory"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_v4_halfopen_table_buckets(self, value):
        """Add the number of v4 halfopen table buckets.

        :param value: Number of v4 halfopen table buckets.
        :type value: int
        """
        path = ["session", "v4-halfopen-table-buckets"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_v4_halfopen_table_memory(self, value):
        """Add the size of v4 halfopen table memory.

        :param value: Size of v4 halfopen table memory.
        :type value: str
        """
        path = ["session", "v4-halfopen-table-memory"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_local_endpoints_table_buckets(self, value):
        """Add the number of local endpoints table buckets.

        :param value: Number of local endpoints table buckets.
        :type value: int
        """
        path = ["session", "local-endpoints-table-buckets"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_local_endpoints_table_memory(self, value):
        """Add the size of local endpoints table memory.

        :param value: Size of local endpoints table memory.
        :type value: str
        """
        path = ["session", "local-endpoints-table-memory"]
        self.add_config_item(self._nodeconfig, value, path)

    def add_session_use_dma(self):
        """Add session use-dma configuration."""
        path = [u"session", u"use-dma"]
        self.add_config_item(self._nodeconfig, u"", path)

    def add_dma_dev(self, devices):
        """Add DMA devices configuration.

        :param devices: DMA devices or work queues.
        :type devices: list
        """
        for device in devices:
            path = ["dsa", f"dev {device}"]
            self.add_config_item(self._nodeconfig, "", path)

    def add_logging_default_syslog_log_level(self, value="debug"):
        """Add default logging level for syslog.

        :param value: Log level.
        :type value: str
        """
        path = ["logging", "default-syslog-log-level"]
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

        cmd = f"echo \"{self._vpp_config}\" | sudo tee {filename}"
        exec_cmd_no_error(
            self._node, cmd, message="Writing config file failed!"
        )

    def apply_vpp_config(self, filename=None, verify_vpp=True, api_trace=True):
        """Generate and write VPP startup configuration to file and restart VPP.

        Use data from calls to this class to form a startup.conf file and
        replace /etc/vpp/startup.conf with it on topology node.

        :param filename: Startup configuration file name.
        :param verify_vpp: Verify VPP is running after restart.
        :param api_trace: False if this VPP instance is not the tested one.
        :type filename: str
        :type verify_vpp: bool
        :type api_trace: bool
        """
        self.write_config(filename=filename)

        VPPUtil.restart_vpp_service(self._node, self._node_key)
        if verify_vpp:
            VPPUtil.verify_vpp(self._node, api_trace=api_trace)


class VppInitConfig:
    """VPP Initial Configuration."""
    @staticmethod
    def init_vpp_startup_configuration_on_all_duts(nodes):
        """Apply initial VPP startup configuration on all DUTs.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        huge_size = Constants.DEFAULT_HUGEPAGE_SIZE
        for node in nodes.values():
            if node["type"] == NodeType.DUT:
                vpp_config = VppConfigGenerator()
                vpp_config.set_node(node)
                vpp_config.add_unix_log()
                vpp_config.add_unix_cli_listen()
                vpp_config.add_unix_cli_no_pager()
                vpp_config.add_unix_gid()
                vpp_config.add_unix_coredump()
                vpp_config.add_socksvr(socket=Constants.SOCKSVR_PATH)
                vpp_config.add_main_heap_size("2G")
                vpp_config.add_main_heap_page_size(huge_size)
                vpp_config.add_default_hugepage_size(huge_size)
                vpp_config.add_statseg_size("2G")
                vpp_config.add_statseg_page_size(huge_size)
                vpp_config.add_statseg_per_node_counters("on")
                vpp_config.add_plugin("disable", "default")
                vpp_config.add_plugin("enable", "dpdk_plugin.so")
                vpp_config.add_dpdk_dev(
                    *[node["interfaces"][interface].get("pci_address") \
                        for interface in node["interfaces"]]
                )
                vpp_config.add_ip6_hash_buckets(2000000)
                vpp_config.add_ip6_heap_size("4G")
                # The VPP instance we will ultimately test is not this one,
                # so do not attempt to enable API trace yet.
                vpp_config.apply_vpp_config(api_trace=False)
