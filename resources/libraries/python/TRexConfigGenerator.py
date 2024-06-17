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

"""TRex Configuration File Generator library."""

import re
import yaml

from resources.libraries.python.Constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType, NodeSubTypeTG
from resources.libraries.python.topology import Topology


__all__ = ["TrexConfigGenerator", "TrexConfig"]

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


class TrexConfigGenerator:
    """TRex Startup Configuration File Generator."""

    def __init__(self):
        """Initialize library.
        """
        self._node = ""
        self._node_key = ""
        self._node_config = dict()
        self._node_serialized_config = ""
        self._startup_configuration_path = "/etc/trex_cfg.yaml"

    def set_node(self, node, node_key=None):
        """Set topology node.

        :param node: Node to store configuration on.
        :param node_key: Topology node key.
        :type node: dict
        :type node_key: str
        :raises RuntimeError: If Node type is not TG and subtype is not TREX.
        """
        if node.get("type") is None:
            msg = "Node type is not defined!"
        elif node["type"] != NodeType.TG:
            msg = f"Node type is {node['type']!r}, not a TG!"
        elif node.get("subtype") is None:
            msg = "TG subtype is not defined"
        elif node["subtype"] != NodeSubTypeTG.TREX:
            msg = f"TG subtype {node['subtype']!r} is not supported"
        else:
            self._node = node
            self._node_key = node_key
            return
        raise RuntimeError(msg)

    def get_serialized_config(self):
        """Get serialized startup configuration in YAML format.

        :returns: Startup configuration in YAML format.
        :rtype: str
        """
        self.serialize_config(self._node_config)
        return self._node_serialized_config

    def serialize_config(self, obj):
        """Serialize the startup configuration in YAML format.

        :param obj: Python Object to print.
        :type obj: Obj
        """
        self._node_serialized_config = yaml.dump([obj], default_style=None)

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

    def add_version(self, value=2):
        """Add config file version.

        :param value: Version of configuration file.
        :type value: int
        """
        path = ["version"]
        self.add_config_item(self._node_config, value, path)

    def add_c(self, value):
        """Add core count.

        :param value: Core count.
        :type value: int
        """
        path = ["c"]
        self.add_config_item(self._node_config, value, path)

    def add_limit_memory(self, value):
        """Add memory limit.

        :param value: Memory limit.
        :type value: str
        """
        path = ["limit_memory"]
        self.add_config_item(self._node_config, value, path)

    def add_interfaces(self, devices):
        """Add PCI device configuration.

        :param devices: PCI device(s) (format xxxx:xx:xx.x).
        :type devices: list(str)
        """
        for device in devices:
            pci_dev_check(device)

        path = ["interfaces"]
        self.add_config_item(self._node_config, devices, path)

    def add_rx_desc(self, value):
        """Add RX descriptors.

        :param value: RX descriptors count.
        :type value: int
        """
        path = ["rx_desc"]
        self.add_config_item(self._node_config, value, path)

    def add_tx_desc(self, value):
        """Add TX descriptors.

        :param value: TX descriptors count.
        :type value: int
        """
        path = ["tx_desc"]
        self.add_config_item(self._node_config, value, path)

    def add_port_info(self, value):
        """Add port information configuration.

        :param value: Port information configuration.
        :type value: list(dict)
        """
        path = ["port_info"]
        self.add_config_item(self._node_config, value, path)

    def add_port_mtu(self, value):
        """Add port MTU configuration.

        :param value: Port MTU configuration.
        :type value: int
        """
        path = ["port_mtu"]
        self.add_config_item(self._node_config, value, path)

    def add_platform_master_thread_id(self, value):
        """Add platform master thread ID.

        :param value: Master thread ID.
        :type value: int
        """
        path = ["platform", "master_thread_id"]
        self.add_config_item(self._node_config, value, path)

    def add_platform_latency_thread_id(self, value):
        """Add platform latency thread ID.

        :param value: Latency thread ID.
        :type value: int
        """
        path = ["platform", "latency_thread_id"]
        self.add_config_item(self._node_config, value, path)

    def add_platform_dual_if(self, value):
        """Add platform dual interface configuration.

        :param value: Dual interface configuration.
        :type value: list(dict)
        """
        path = ["platform", "dual_if"]
        self.add_config_item(self._node_config, value, path)

    def write_config(self, path=None):
        """Generate and write TRex startup configuration to file.

        :param path: Override startup configuration path.
        :type path: str
        """
        self.serialize_config(self._node_config)

        if path is None:
            path = self._startup_configuration_path

        command = f"echo \"{self._node_serialized_config}\" | sudo tee {path}"
        message = "Writing TRex startup configuration failed!"
        exec_cmd_no_error(self._node, command, message=message)


class TrexConfig:
    """TRex Configuration Class.
    """
    @staticmethod
    def add_startup_configuration(node, tg_topology):
        """Apply TRex startup configuration.

        :param node: TRex node in the topology.
        :param tg_topology: Ordered TRex links.
        :type node: dict
        :type tg_topology: list(dict)
        """
        pci_addresses = list()
        dual_if = list()
        port_info = list()
        master_thread_id = None
        latency_thread_id = None
        cores = None
        sockets = list()

        for idx, link in enumerate(tg_topology):
            pci_addresses.append(
                Topology().get_interface_pci_addr(node, link["interface"])
            )
            if len(tg_topology) > 2:
                # Multiple dual_ifs must not share the cores.
                tg_dtc = Constants.TREX_CORE_COUNT_MULTI
                tg_dtc_offset = Constants.TREX_CORE_COUNT_MULTI * (idx // 2)
            else:
                # Single dual_if can share cores.
                tg_dtc = Constants.TREX_CORE_COUNT
                tg_dtc_offset = 0
            master_thread_id, latency_thread_id, socket, threads = \
                CpuUtils.get_affinity_trex(
                    node, link["interface"], tg_dtc=tg_dtc,
                    tg_dtc_offset=tg_dtc_offset
                )
            dual_if.append(dict(socket=socket, threads=threads))
            cores = len(threads)
            port_info.append(
                dict(
                    src_mac=Topology().get_interface_mac(
                        node, link["interface"]
                    ),
                    dest_mac=link["dst_mac"]
                )
            )
            sockets.append(socket)

        limit_memory = f"{Constants.TREX_LIMIT_MEMORY}"
        if len(tg_topology) <= 2 and 0 in sockets and 1 in sockets:
            limit_memory = (
                f"{Constants.TREX_LIMIT_MEMORY},{Constants.TREX_LIMIT_MEMORY}"
            )
        if len(tg_topology) > 2:
            limit_memory = (
                f"{Constants.TREX_LIMIT_MEMORY_MULTI}"
            )

        trex_config = TrexConfigGenerator()
        trex_config.set_node(node)
        trex_config.add_version()
        trex_config.add_interfaces(pci_addresses)
        trex_config.add_c(cores)
        trex_config.add_limit_memory(limit_memory)
        trex_config.add_port_info(port_info)
        trex_config.add_port_mtu(9000)
        if Constants.TREX_RX_DESCRIPTORS_COUNT != 0:
            trex_config.add_rx_desc(Constants.TREX_RX_DESCRIPTORS_COUNT)
        if Constants.TREX_TX_DESCRIPTORS_COUNT != 0:
            trex_config.add_rx_desc(Constants.TREX_TX_DESCRIPTORS_COUNT)
        trex_config.add_platform_master_thread_id(int(master_thread_id))
        trex_config.add_platform_latency_thread_id(int(latency_thread_id))
        trex_config.add_platform_dual_if(dual_if)
        trex_config.write_config()
