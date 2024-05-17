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

"""Interface util library."""

from json import loads
from time import sleep
from enum import IntEnum

from ipaddress import ip_address
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.Constants import Constants
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.IPAddress import IPAddress
from resources.libraries.python.L2Util import L2Util
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import SSH, exec_cmd, exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.VPPUtil import VPPUtil


class InterfaceStatusFlags(IntEnum):
    """Interface status flags."""
    IF_STATUS_API_FLAG_ADMIN_UP = 1
    IF_STATUS_API_FLAG_LINK_UP = 2


class MtuProto(IntEnum):
    """MTU protocol."""
    MTU_PROTO_API_L3 = 0
    MTU_PROTO_API_IP4 = 1
    MTU_PROTO_API_IP6 = 2
    MTU_PROTO_API_MPLS = 3
    MTU_PROTO_API_N = 4


class LinkDuplex(IntEnum):
    """Link duplex"""
    LINK_DUPLEX_API_UNKNOWN = 0
    LINK_DUPLEX_API_HALF = 1
    LINK_DUPLEX_API_FULL = 2


class SubInterfaceFlags(IntEnum):
    """Sub-interface flags."""
    SUB_IF_API_FLAG_NO_TAGS = 1
    SUB_IF_API_FLAG_ONE_TAG = 2
    SUB_IF_API_FLAG_TWO_TAGS = 4
    SUB_IF_API_FLAG_DOT1AD = 8
    SUB_IF_API_FLAG_EXACT_MATCH = 16
    SUB_IF_API_FLAG_DEFAULT = 32
    SUB_IF_API_FLAG_OUTER_VLAN_ID_ANY = 64
    SUB_IF_API_FLAG_INNER_VLAN_ID_ANY = 128
    SUB_IF_API_FLAG_DOT1AH = 256


class RxMode(IntEnum):
    """RX mode"""
    RX_MODE_API_UNKNOWN = 0
    RX_MODE_API_POLLING = 1
    RX_MODE_API_INTERRUPT = 2
    RX_MODE_API_ADAPTIVE = 3
    RX_MODE_API_DEFAULT = 4


class IfType(IntEnum):
    """Interface type"""
    # A hw interface
    IF_API_TYPE_HARDWARE = 0
    # A sub-interface
    IF_API_TYPE_SUB = 1
    IF_API_TYPE_P2P = 2
    IF_API_TYPE_PIPE = 3


class LinkBondLoadBalanceAlgo(IntEnum):
    """Link bonding load balance algorithm."""
    BOND_API_LB_ALGO_L2 = 0
    BOND_API_LB_ALGO_L34 = 1
    BOND_API_LB_ALGO_L23 = 2
    BOND_API_LB_ALGO_RR = 3
    BOND_API_LB_ALGO_BC = 4
    BOND_API_LB_ALGO_AB = 5


class LinkBondMode(IntEnum):
    """Link bonding mode."""
    BOND_API_MODE_ROUND_ROBIN = 1
    BOND_API_MODE_ACTIVE_BACKUP = 2
    BOND_API_MODE_XOR = 3
    BOND_API_MODE_BROADCAST = 4
    BOND_API_MODE_LACP = 5


class RdmaMode(IntEnum):
    """RDMA interface mode."""
    RDMA_API_MODE_AUTO = 0
    RDMA_API_MODE_IBV = 1
    RDMA_API_MODE_DV = 2


class AfXdpMode(IntEnum):
    """AF_XDP interface mode."""
    AF_XDP_API_MODE_AUTO = 0
    AF_XDP_API_MODE_COPY = 1
    AF_XDP_API_MODE_ZERO_COPY = 2


class InterfaceUtil:
    """General utilities for managing interfaces"""

    @staticmethod
    def pci_to_int(pci_str):
        """Convert PCI address from string format (0000:18:0a.0) to
        integer representation (169345024).

        :param pci_str: PCI address in string representation.
        :type pci_str: str
        :returns: Integer representation of PCI address.
        :rtype: int
        """
        pci = list(pci_str.split(u":")[0:2])
        pci.extend(pci_str.split(u":")[2].split(u"."))

        return (int(pci[0], 16) | int(pci[1], 16) << 16 |
                int(pci[2], 16) << 24 | int(pci[3], 16) << 29)

    @staticmethod
    def pci_to_eth(node, pci_str):
        """Convert PCI address on DUT to Linux ethernet name.

        :param node: DUT node
        :param pci_str: PCI address.
        :type node: dict
        :type pci_str: str
        :returns: Ethernet name.
        :rtype: str
        """
        cmd = f"basename /sys/bus/pci/devices/{pci_str}/net/*"
        try:
            stdout, _ = exec_cmd_no_error(node, cmd)
        except RuntimeError:
            raise RuntimeError(f"Cannot convert {pci_str} to ethernet name!")

        return stdout.strip()

    @staticmethod
    def get_interface_index(node, interface):
        """Get interface sw_if_index from topology file.

        :param node: Node where the interface is.
        :param interface: Numeric index or name string of a specific interface.
        :type node: dict
        :type interface: str or int
        :returns: SW interface index.
        :rtype: int
        """
        try:
            sw_if_index = int(interface)
        except ValueError:
            sw_if_index = Topology.get_interface_sw_index(node, interface)
            if sw_if_index is None:
                sw_if_index = \
                    Topology.get_interface_sw_index_by_name(node, interface)
        except TypeError as err:
            raise TypeError(f"Wrong interface format {interface}") from err

        return sw_if_index

    @staticmethod
    def set_interface_state(node, interface, state, if_type=u"key"):
        """Set interface state on a node.

        Function can be used for DUTs as well as for TGs.

        :param node: Node where the interface is.
        :param interface: Interface key or sw_if_index or name.
        :param state: One of 'up' or 'down'.
        :param if_type: Interface type
        :type node: dict
        :type interface: str or int
        :type state: str
        :type if_type: str
        :returns: Nothing.
        :raises ValueError: If the interface type is unknown.
        :raises ValueError: If the state of interface is unexpected.
        :raises ValueError: If the node has an unknown node type.
        """
        if if_type == u"key":
            if isinstance(interface, str):
                sw_if_index = Topology.get_interface_sw_index(node, interface)
                iface_name = Topology.get_interface_name(node, interface)
            else:
                sw_if_index = interface
        elif if_type == u"name":
            iface_key = Topology.get_interface_by_name(node, interface)
            if iface_key is not None:
                sw_if_index = Topology.get_interface_sw_index(node, iface_key)
            iface_name = interface
        else:
            raise ValueError(f"Unknown if_type: {if_type}")

        if node[u"type"] == NodeType.DUT:
            if sw_if_index is None:
                raise ValueError(
                    f"Interface index for {interface} not assigned by VPP."
                )
            if state == u"up":
                flags = InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value
            elif state == u"down":
                flags = 0
            else:
                raise ValueError(f"Unexpected interface state: {state}")
            cmd = u"sw_interface_set_flags"
            err_msg = f"Failed to set interface state on host {node[u'host']}"
            args = dict(
                sw_if_index=int(sw_if_index),
                flags=flags
            )
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
        elif node[u"type"] == NodeType.TG or node[u"type"] == NodeType.VM:
            cmd = f"ip link set {iface_name} {state}"
            exec_cmd_no_error(node, cmd, sudo=True)
        else:
            raise ValueError(
                f"Node {node[u'host']} has unknown NodeType: {node[u'type']}"
            )

    @staticmethod
    def set_interface_state_pci(
            node, pf_pcis, namespace=None, state=u"up"):
        """Set operational state for interface specified by PCI address.

        :param node: Topology node.
        :param pf_pcis: List of node's interfaces PCI addresses.
        :param namespace: Exec command in namespace. (Optional, Default: none)
        :param state: Up/Down. (Optional, default: up)
        :type nodes: dict
        :type pf_pcis: list
        :type namespace: str
        :type state: str
        """
        for pf_pci in pf_pcis:
            pf_eth = InterfaceUtil.pci_to_eth(node, pf_pci)
            InterfaceUtil.set_linux_interface_state(
                node, pf_eth, namespace=namespace, state=state
            )

    @staticmethod
    def set_interface_mtu(node, pf_pcis, mtu=9200):
        """Set Ethernet MTU for specified interfaces.

        :param node: Topology node.
        :param pf_pcis: List of node's interfaces PCI addresses.
        :param mtu: MTU to set. Default: 9200.
        :type nodes: dict
        :type pf_pcis: list
        :type mtu: int
        :raises RuntimeError: If failed to set MTU on interface.
        """
        for pf_pci in pf_pcis:
            pf_eth = InterfaceUtil.pci_to_eth(node, pf_pci)
            cmd = f"ip link set {pf_eth} mtu {mtu}"
            exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def set_interface_channels(
            node, pf_pcis, num_queues=1, channel=u"combined"):
        """Set interface channels for specified interfaces.

        :param node: Topology node.
        :param pf_pcis: List of node's interfaces PCI addresses.
        :param num_queues: Number of channels. (Optional, Default: 1)
        :param channel: Channel type. (Optional, Default: combined)
        :type nodes: dict
        :type pf_pcis: list
        :type num_queues: int
        :type channel: str
        """
        for pf_pci in pf_pcis:
            pf_eth = InterfaceUtil.pci_to_eth(node, pf_pci)
            cmd = f"ethtool --set-channels {pf_eth} {channel} {num_queues}"
            exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def set_interface_xdp_off(node, pf_pcis):
        """Detaches any currently attached XDP/BPF program from the specified
        interfaces.

        :param node: Topology node.
        :param pf_pcis: List of node's interfaces PCI addresses.
        :type nodes: dict
        :type pf_pcis: list
        """
        for pf_pci in pf_pcis:
            pf_eth = InterfaceUtil.pci_to_eth(node, pf_pci)
            cmd = f"ip link set dev {pf_eth} xdp off"
            exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def set_interface_flow_control(node, pf_pcis, rxf=u"off", txf=u"off"):
        """Set Ethernet flow control for specified interfaces.

        :param node: Topology node.
        :param pf_pcis: List of node's interfaces PCI addresses.
        :param rxf: RX flow. (Optional, Default: off).
        :param txf: TX flow. (Optional, Default: off).
        :type nodes: dict
        :type pf_pcis: list
        :type rxf: str
        :type txf: str
        """
        for pf_pci in pf_pcis:
            pf_eth = InterfaceUtil.pci_to_eth(node, pf_pci)
            cmd = f"ethtool -A {pf_eth} rx {rxf} tx {txf}"
            ret_code, _, _ = exec_cmd(node, cmd, sudo=True)
            if int(ret_code) not in (0, 78):
                raise RuntimeError("Failed to set flow control on {pf_eth}!")

    @staticmethod
    def set_pci_parameter(node, pf_pcis, key, value):
        """Set PCI parameter for specified interfaces.

        :param node: Topology node.
        :param pf_pcis: List of node's interfaces PCI addresses.
        :param key: Key to set.
        :param value: Value to set.
        :type nodes: dict
        :type pf_pcis: list
        :type key: str
        :type value: str
        """
        for pf_pci in pf_pcis:
            cmd = f"setpci -s {pf_pci} {key}={value}"
            exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def vpp_set_interface_mtu(node, interface, mtu):
        """Apply new MTU value to a VPP hardware interface.

        The interface should be down when this is called.

        :param node: VPP node.
        :param interface: Interface to set MTU on.
        :param mtu: Ethernet MTU size in Bytes.
        :type node: dict
        :type interface: str or int
        :type mtu: int
        """
        if isinstance(interface, str):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        else:
            sw_if_index = interface
        cmd = u"hw_interface_set_mtu"
        err_msg = f"Failed to set interface MTU on host {node[u'host']}"
        args = dict(sw_if_index=sw_if_index, mtu=int(mtu))
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_node_interfaces_ready_wait(node, retries=15):
        """Wait until all interfaces with admin-up are in link-up state.

        :param node: Node to wait on.
        :param retries: Number of retries to check interface status (optional,
            default 15).
        :type node: dict
        :type retries: int
        :returns: Nothing.
        :raises RuntimeError: If any interface is not in link-up state after
            defined number of retries.
        """
        for _ in range(0, retries):
            not_ready = list()
            out = InterfaceUtil.vpp_get_interface_data(node)
            for interface in out:
                if interface.get(u"flags") == 1:
                    not_ready.append(interface.get(u"interface_name"))
            if not_ready:
                logger.debug(
                    f"Interfaces still not in link-up state:\n{not_ready}"
                )
                sleep(1)
            else:
                break
        else:
            err = f"Timeout, interfaces not up:\n{not_ready}" \
                if u"not_ready" in locals() else u"No check executed!"
            raise RuntimeError(err)

    @staticmethod
    def all_vpp_interfaces_ready_wait(nodes, retries=15):
        """Wait until all interfaces with admin-up are in link-up state for all
        nodes in the topology.

        :param nodes: Nodes in the topology.
        :param retries: Number of retries to check interface status (optional,
            default 15).
        :type nodes: dict
        :type retries: int
        :returns: Nothing.
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                InterfaceUtil.vpp_node_interfaces_ready_wait(node, retries)

    @staticmethod
    def vpp_get_interface_data(node, interface=None):
        """Get all interface data from a VPP node. If a name or
        sw_interface_index is provided, return only data for the matching
        interface(s).

        :param node: VPP node to get interface data from.
        :param interface: Numeric index or name string of a specific interface.
        :type node: dict
        :type interface: int or str
        :returns: List of dictionaries containing data for each interface, or a
            single dictionary for the specified interface.
        :rtype: list or dict
        :raises TypeError: if the data type of interface is neither basestring
            nor int.
        """
        def process_if_dump(if_dump):
            """Process interface dump.

            :param if_dump: Interface dump.
            :type if_dump: dict
            :returns: Processed interface dump.
            :rtype: dict
            """
            if_dump[u"l2_address"] = str(if_dump[u"l2_address"])
            if_dump[u"b_dmac"] = str(if_dump[u"b_dmac"])
            if_dump[u"b_smac"] = str(if_dump[u"b_smac"])
            if_dump[u"flags"] = if_dump[u"flags"].value
            if_dump[u"type"] = if_dump[u"type"].value
            if_dump[u"link_duplex"] = if_dump[u"link_duplex"].value
            if_dump[u"sub_if_flags"] = if_dump[u"sub_if_flags"].value \
                if hasattr(if_dump[u"sub_if_flags"], u"value") \
                else int(if_dump[u"sub_if_flags"])

            return if_dump

        if interface is not None:
            if isinstance(interface, str):
                param = u"interface_name"
            elif isinstance(interface, int):
                param = u"sw_if_index"
            else:
                raise TypeError(f"Wrong interface format {interface}")
        else:
            param = u""

        cmd = u"sw_interface_dump"
        args = dict(
            name_filter_valid=False,
            name_filter=u""
        )
        err_msg = f"Failed to get interface dump on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, **args).get_details(err_msg)
        logger.debug(f"Received data:\n{details!r}")

        data = list() if interface is None else dict()
        for dump in details:
            if interface is None:
                data.append(process_if_dump(dump))
            elif str(dump.get(param)).rstrip(u"\x00") == str(interface):
                data = process_if_dump(dump)
                break

        logger.debug(f"Interface data:\n{data}")
        return data

    @staticmethod
    def vpp_get_interface_name(node, sw_if_index):
        """Get interface name for the given SW interface index from actual
        interface dump.

        :param node: VPP node to get interface data from.
        :param sw_if_index: SW interface index of the specific interface.
        :type node: dict
        :type sw_if_index: int
        :returns: Name of the given interface.
        :rtype: str
        """
        if_data = InterfaceUtil.vpp_get_interface_data(node, sw_if_index)
        if if_data[u"sup_sw_if_index"] != if_data[u"sw_if_index"]:
            if_data = InterfaceUtil.vpp_get_interface_data(
                node, if_data[u"sup_sw_if_index"]
            )

        return if_data.get(u"interface_name")

    @staticmethod
    def vpp_get_interface_sw_index(node, interface_name):
        """Get interface name for the given SW interface index from actual
        interface dump.

        :param node: VPP node to get interface data from.
        :param interface_name: Interface name.
        :type node: dict
        :type interface_name: str
        :returns: Name of the given interface.
        :rtype: str
        """
        if_data = InterfaceUtil.vpp_get_interface_data(node, interface_name)

        return if_data.get(u"sw_if_index")

    @staticmethod
    def vpp_get_interface_mac(node, interface):
        """Get MAC address for the given interface from actual interface dump.

        :param node: VPP node to get interface data from.
        :param interface: Numeric index or name string of a specific interface.
        :type node: dict
        :type interface: int or str
        :returns: MAC address.
        :rtype: str
        """
        if_data = InterfaceUtil.vpp_get_interface_data(node, interface)
        if if_data[u"sup_sw_if_index"] != if_data[u"sw_if_index"]:
            if_data = InterfaceUtil.vpp_get_interface_data(
                node, if_data[u"sup_sw_if_index"])

        return if_data.get(u"l2_address")

    @staticmethod
    def vpp_set_interface_mac(node, interface, mac):
        """Set MAC address for the given interface.

        :param node: VPP node to set interface MAC.
        :param interface: Numeric index or name string of a specific interface.
        :param mac: Required MAC address.
        :type node: dict
        :type interface: int or str
        :type mac: str
        """
        cmd = u"sw_interface_set_mac_address"
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            mac_address=L2Util.mac_to_bin(mac)
        )
        err_msg = f"Failed to set MAC address of interface {interface}" \
            f"on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def tg_set_interface_driver(node, pci_addr, driver):
        """Set interface driver on the TG node.

        :param node: Node to set interface driver on (must be TG node).
        :param pci_addr: PCI address of the interface.
        :param driver: Driver name.
        :type node: dict
        :type pci_addr: str
        :type driver: str
        :raises RuntimeError: If unbinding from the current driver fails.
        :raises RuntimeError: If binding to the new driver fails.
        """
        old_driver = InterfaceUtil.tg_get_interface_driver(node, pci_addr)
        if old_driver == driver:
            return

        ssh = SSH()
        ssh.connect(node)

        # Unbind from current driver
        if old_driver is not None:
            cmd = f"sh -c \"echo {pci_addr} > " \
                f"/sys/bus/pci/drivers/{old_driver}/unbind\""
            ret_code, _, _ = ssh.exec_command_sudo(cmd)
            if int(ret_code) != 0:
                raise RuntimeError(f"'{cmd}' failed on '{node[u'host']}'")

        # Bind to the new driver
        cmd = f"sh -c \"echo {pci_addr} > /sys/bus/pci/drivers/{driver}/bind\""
        ret_code, _, _ = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise RuntimeError(f"'{cmd}' failed on '{node[u'host']}'")

    @staticmethod
    def tg_get_interface_driver(node, pci_addr):
        """Get interface driver from the TG node.

        :param node: Node to get interface driver on (must be TG node).
        :param pci_addr: PCI address of the interface.
        :type node: dict
        :type pci_addr: str
        :returns: Interface driver or None if not found.
        :rtype: str
        :raises RuntimeError: If PCI rescan or lspci command execution failed.
        """
        return DUTSetup.get_pci_dev_driver(node, pci_addr)

    @staticmethod
    def tg_set_interfaces_default_driver(node):
        """Set interfaces default driver specified in topology yaml file.

        :param node: Node to setup interfaces driver on (must be TG node).
        :type node: dict
        """
        for interface in node[u"interfaces"].values():
            InterfaceUtil.tg_set_interface_driver(
                node, interface[u"pci_address"], interface[u"driver"]
            )

    @staticmethod
    def update_vpp_interface_data_on_node(node):
        """Update vpp generated interface data for a given node in DICT__nodes.

        Updates interface names, software if index numbers and any other details
        generated specifically by vpp that are unknown before testcase run.
        It does this by dumping interface list from all devices using python
        api, and pairing known information from topology (mac address) to state
        from VPP.

        :param node: Node selected from DICT__nodes.
        :type node: dict
        """
        interface_list = InterfaceUtil.vpp_get_interface_data(node)
        interface_dict = dict()
        for ifc in interface_list:
            interface_dict[ifc[u"l2_address"]] = ifc

        for if_name, if_data in node[u"interfaces"].items():
            ifc_dict = interface_dict.get(if_data[u"mac_address"])
            if ifc_dict is not None:
                if_data[u"name"] = ifc_dict[u"interface_name"]
                if_data[u"vpp_sw_index"] = ifc_dict[u"sw_if_index"]
                if_data[u"mtu"] = ifc_dict[u"mtu"][0]
                logger.trace(
                    f"Interface {if_name} found by MAC "
                    f"{if_data[u'mac_address']}"
                )
            else:
                logger.trace(
                    f"Interface {if_name} not found by MAC "
                    f"{if_data[u'mac_address']}"
                )
                if_data[u"vpp_sw_index"] = None

    @staticmethod
    def update_nic_interface_names(node):
        """Update interface names based on nic type and PCI address.

        This method updates interface names in the same format as VPP does.

        :param node: Node dictionary.
        :type node: dict
        """
        for ifc in node[u"interfaces"].values():
            if_pci = ifc[u"pci_address"].replace(u".", u":").split(u":")
            loc = f"{int(if_pci[1], 16):x}/{int(if_pci[2], 16):x}/" \
                f"{int(if_pci[3], 16):x}"
            if ifc[u"model"] == u"Intel-XL710":
                ifc[u"name"] = f"FortyGigabitEthernet{loc}"
            elif ifc[u"model"] == u"Intel-X710":
                ifc[u"name"] = f"TenGigabitEthernet{loc}"
            elif ifc[u"model"] == u"Intel-X520-DA2":
                ifc[u"name"] = f"TenGigabitEthernet{loc}"
            elif ifc[u"model"] == u"Cisco-VIC-1385":
                ifc[u"name"] = f"FortyGigabitEthernet{loc}"
            elif ifc[u"model"] == u"Cisco-VIC-1227":
                ifc[u"name"] = f"TenGigabitEthernet{loc}"
            else:
                ifc[u"name"] = f"UnknownEthernet{loc}"

    @staticmethod
    def update_nic_interface_names_on_all_duts(nodes):
        """Update interface names based on nic type and PCI address on all DUTs.

        This method updates interface names in the same format as VPP does.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                InterfaceUtil.update_nic_interface_names(node)

    @staticmethod
    def update_tg_interface_data_on_node(node):
        """Update interface name for TG/linux node in DICT__nodes.

        .. note::
            # for dev in `ls /sys/class/net/`;
            > do echo "\"`cat /sys/class/net/$dev/address`\": \"$dev\""; done
            "52:54:00:9f:82:63": "eth0"
            "52:54:00:77:ae:a9": "eth1"
            "52:54:00:e1:8a:0f": "eth2"
            "00:00:00:00:00:00": "lo"

        :param node: Node selected from DICT__nodes.
        :type node: dict
        :raises RuntimeError: If getting of interface name and MAC fails.
        """
        # First setup interface driver specified in yaml file
        InterfaceUtil.tg_set_interfaces_default_driver(node)

        # Get interface names
        ssh = SSH()
        ssh.connect(node)

        cmd = u'for dev in `ls /sys/class/net/`; do echo "\\"`cat ' \
              u'/sys/class/net/$dev/address`\\": \\"$dev\\""; done;'

        ret_code, stdout, _ = ssh.exec_command(cmd)
        if int(ret_code) != 0:
            raise RuntimeError(u"Get interface name and MAC failed")

        interfaces = loads("{" + stdout.rstrip().replace("\n", ",") + "}")
        for interface in node[u"interfaces"].values():
            name = interfaces.get(interface[u"mac_address"])
            if name is None:
                continue
            interface[u"name"] = name

    @staticmethod
    def iface_update_numa_node(node):
        """For all interfaces from topology file update numa node based on
           information from the node.

        :param node: Node from topology.
        :type node: dict
        :returns: Nothing.
        :raises ValueError: If numa node ia less than 0.
        :raises RuntimeError: If update of numa node failed.
        """
        ssh = SSH()
        for if_key in Topology.get_node_interfaces(node):
            if_pci = Topology.get_interface_pci_addr(node, if_key)
            ssh.connect(node)
            cmd = f"cat /sys/bus/pci/devices/{if_pci}/numa_node"
            for _ in range(3):
                ret, out, _ = ssh.exec_command(cmd)
                if ret == 0:
                    try:
                        numa_node = 0 if int(out) < 0 else int(out)
                    except ValueError:
                        logger.trace(
                            f"Reading numa location failed for: {if_pci}"
                        )
                    else:
                        Topology.set_interface_numa_node(
                            node, if_key, numa_node
                        )
                        break
            else:
                raise RuntimeError(f"Update numa node failed for: {if_pci}")

    @staticmethod
    def update_all_interface_data_on_all_nodes(
            nodes, skip_tg=False, skip_vpp=False):
        """Update interface names on all nodes in DICT__nodes.

        This method updates the topology dictionary by querying interface lists
        of all nodes mentioned in the topology dictionary.

        :param nodes: Nodes in the topology.
        :param skip_tg: Skip TG node.
        :param skip_vpp: Skip VPP node.
        :type nodes: dict
        :type skip_tg: bool
        :type skip_vpp: bool
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT and not skip_vpp:
                InterfaceUtil.update_vpp_interface_data_on_node(node)
            elif node[u"type"] == NodeType.TG and not skip_tg:
                InterfaceUtil.update_tg_interface_data_on_node(node)
            InterfaceUtil.iface_update_numa_node(node)

    @staticmethod
    def create_vlan_subinterface(node, interface, vlan):
        """Create VLAN sub-interface on node.

        :param node: Node to add VLAN subinterface on.
        :param interface: Interface name or index on which create VLAN
            subinterface.
        :param vlan: VLAN ID of the subinterface to be created.
        :type node: dict
        :type interface: str on int
        :type vlan: int
        :returns: Name and index of created subinterface.
        :rtype: tuple
        :raises RuntimeError: if it is unable to create VLAN subinterface on the
            node or interface cannot be converted.
        """
        sw_if_index = InterfaceUtil.get_interface_index(node, interface)

        cmd = u"create_vlan_subif"
        args = dict(
            sw_if_index=sw_if_index,
            vlan_id=int(vlan)
        )
        err_msg = f"Failed to create VLAN sub-interface on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        if_key = Topology.add_new_port(node, u"vlan_subif")
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)
        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)

        return f"{interface}.{vlan}", sw_if_index

    @staticmethod
    def create_vxlan_interface(node, vni, source_ip, destination_ip):
        """Create VXLAN interface and return sw if index of created interface.

        :param node: Node where to create VXLAN interface.
        :param vni: VXLAN Network Identifier.
        :param source_ip: Source IP of a VXLAN Tunnel End Point.
        :param destination_ip: Destination IP of a VXLAN Tunnel End Point.
        :type node: dict
        :type vni: int
        :type source_ip: str
        :type destination_ip: str
        :returns: SW IF INDEX of created interface.
        :rtype: int
        :raises RuntimeError: if it is unable to create VxLAN interface on the
            node.
        """
        cmd = u"vxlan_add_del_tunnel_v3"
        args = dict(
            is_add=True,
            instance=Constants.BITWISE_NON_ZERO,
            src_address=IPAddress.create_ip_address_object(
                ip_address(source_ip)
            ),
            dst_address=IPAddress.create_ip_address_object(
                ip_address(destination_ip)
            ),
            mcast_sw_if_index=Constants.BITWISE_NON_ZERO,
            encap_vrf_id=0,
            decap_next_index=Constants.BITWISE_NON_ZERO,
            vni=int(vni)
        )
        err_msg = f"Failed to create VXLAN tunnel interface " \
            f"on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        if_key = Topology.add_new_port(node, u"vxlan_tunnel")
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)
        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)

        return sw_if_index

    @staticmethod
    def set_vxlan_bypass(node, interface=None):
        """Add the 'ip4-vxlan-bypass' graph node for a given interface.

        By adding the IPv4 vxlan-bypass graph node to an interface, the node
        checks for and validate input vxlan packet and bypass ip4-lookup,
        ip4-local, ip4-udp-lookup nodes to speedup vxlan packet forwarding.
        This node will cause extra overhead to for non-vxlan packets which is
        kept at a minimum.

        :param node: Node where to set VXLAN bypass.
        :param interface: Numeric index or name string of a specific interface.
        :type node: dict
        :type interface: int or str
        :raises RuntimeError: if it failed to set VXLAN bypass on interface.
        """
        sw_if_index = InterfaceUtil.get_interface_index(node, interface)

        cmd = u"sw_interface_set_vxlan_bypass"
        args = dict(
            is_ipv6=False,
            sw_if_index=sw_if_index,
            enable=True
        )
        err_msg = f"Failed to set VXLAN bypass on interface " \
            f"on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vxlan_dump(node, interface=None):
        """Get VxLAN data for the given interface.

        :param node: VPP node to get interface data from.
        :param interface: Numeric index or name string of a specific interface.
            If None, information about all VxLAN interfaces is returned.
        :type node: dict
        :type interface: int or str
        :returns: Dictionary containing data for the given VxLAN interface or if
            interface=None, the list of dictionaries with all VxLAN interfaces.
        :rtype: dict or list
        :raises TypeError: if the data type of interface is neither basestring
            nor int.
        """
        def process_vxlan_dump(vxlan_dump):
            """Process vxlan dump.

            :param vxlan_dump: Vxlan interface dump.
            :type vxlan_dump: dict
            :returns: Processed vxlan interface dump.
            :rtype: dict
            """
            vxlan_dump[u"src_address"] = str(vxlan_dump[u"src_address"])
            vxlan_dump[u"dst_address"] = str(vxlan_dump[u"dst_address"])
            return vxlan_dump

        if interface is not None:
            sw_if_index = InterfaceUtil.get_interface_index(node, interface)
        else:
            sw_if_index = int(Constants.BITWISE_NON_ZERO)

        cmd = u"vxlan_tunnel_dump"
        args = dict(
            sw_if_index=sw_if_index
        )
        err_msg = f"Failed to get VXLAN dump on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, **args).get_details(err_msg)

        data = list() if interface is None else dict()
        for dump in details:
            if interface is None:
                data.append(process_vxlan_dump(dump))
            elif dump[u"sw_if_index"] == sw_if_index:
                data = process_vxlan_dump(dump)
                break

        logger.debug(f"VXLAN data:\n{data}")
        return data

    @staticmethod
    def create_subinterface(
            node, interface, sub_id, outer_vlan_id=None, inner_vlan_id=None,
            type_subif=None):
        """Create sub-interface on node. It is possible to set required
        sub-interface type and VLAN tag(s).

        :param node: Node to add sub-interface.
        :param interface: Interface name on which create sub-interface.
        :param sub_id: ID of the sub-interface to be created.
        :param outer_vlan_id: Optional outer VLAN ID.
        :param inner_vlan_id: Optional inner VLAN ID.
        :param type_subif: Optional type of sub-interface. Values supported by
            VPP: [no_tags] [one_tag] [two_tags] [dot1ad] [exact_match]
            [default_sub]
        :type node: dict
        :type interface: str or int
        :type sub_id: int
        :type outer_vlan_id: int
        :type inner_vlan_id: int
        :type type_subif: str
        :returns: Name and index of created sub-interface.
        :rtype: tuple
        :raises RuntimeError: If it is not possible to create sub-interface.
        """
        subif_types = type_subif.split()

        flags = 0
        if u"no_tags" in subif_types:
            flags = flags | SubInterfaceFlags.SUB_IF_API_FLAG_NO_TAGS
        if u"one_tag" in subif_types:
            flags = flags | SubInterfaceFlags.SUB_IF_API_FLAG_ONE_TAG
        if u"two_tags" in subif_types:
            flags = flags | SubInterfaceFlags.SUB_IF_API_FLAG_TWO_TAGS
        if u"dot1ad" in subif_types:
            flags = flags | SubInterfaceFlags.SUB_IF_API_FLAG_DOT1AD
        if u"exact_match" in subif_types:
            flags = flags | SubInterfaceFlags.SUB_IF_API_FLAG_EXACT_MATCH
        if u"default_sub" in subif_types:
            flags = flags | SubInterfaceFlags.SUB_IF_API_FLAG_DEFAULT
        if type_subif == u"default_sub":
            flags = flags | SubInterfaceFlags.SUB_IF_API_FLAG_INNER_VLAN_ID_ANY\
                    | SubInterfaceFlags.SUB_IF_API_FLAG_OUTER_VLAN_ID_ANY

        cmd = u"create_subif"
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            sub_id=int(sub_id),
            sub_if_flags=flags.value if hasattr(flags, u"value")
            else int(flags),
            outer_vlan_id=int(outer_vlan_id) if outer_vlan_id else 0,
            inner_vlan_id=int(inner_vlan_id) if inner_vlan_id else 0
        )
        err_msg = f"Failed to create sub-interface on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        if_key = Topology.add_new_port(node, u"subinterface")
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)
        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)

        return f"{interface}.{sub_id}", sw_if_index

    @staticmethod
    def create_gre_tunnel_interface(node, source_ip, destination_ip):
        """Create GRE tunnel interface on node.

        :param node: VPP node to add tunnel interface.
        :param source_ip: Source of the GRE tunnel.
        :param destination_ip: Destination of the GRE tunnel.
        :type node: dict
        :type source_ip: str
        :type destination_ip: str
        :returns: Name and index of created GRE tunnel interface.
        :rtype: tuple
        :raises RuntimeError: If unable to create GRE tunnel interface.
        """
        cmd = u"gre_tunnel_add_del"
        tunnel = dict(
            type=0,
            instance=Constants.BITWISE_NON_ZERO,
            src=str(source_ip),
            dst=str(destination_ip),
            outer_fib_id=0,
            session_id=0
        )
        args = dict(
            is_add=1,
            tunnel=tunnel
        )
        err_msg = f"Failed to create GRE tunnel interface " \
            f"on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        if_key = Topology.add_new_port(node, u"gre_tunnel")
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)
        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)

        return ifc_name, sw_if_index

    @staticmethod
    def create_gtpu_tunnel_interface(node, teid, source_ip, destination_ip):
        """Create GTPU interface and return sw if index of created interface.

        :param node: Node where to create GTPU interface.
        :param teid: GTPU Tunnel Endpoint Identifier.
        :param source_ip: Source IP of a GTPU Tunnel End Point.
        :param destination_ip: Destination IP of a GTPU Tunnel End Point.
        :type node: dict
        :type teid: int
        :type source_ip: str
        :type destination_ip: str
        :returns: SW IF INDEX of created interface.
        :rtype: int
        :raises RuntimeError: if it is unable to create GTPU interface on the
            node.
        """
        cmd = u"gtpu_add_del_tunnel_v2"
        args = dict(
            is_add=True,
            src_address=IPAddress.create_ip_address_object(
                ip_address(source_ip)
            ),
            dst_address=IPAddress.create_ip_address_object(
                ip_address(destination_ip)
            ),
            mcast_sw_if_index=Constants.BITWISE_NON_ZERO,
            encap_vrf_id=0,
            decap_next_index=2,  # ipv4
            teid=teid,
            # pdu_extension: Unused, false by default.
            # qfi: Irrelevant when pdu_extension is not used.
        )
        err_msg = f"Failed to create GTPU tunnel interface " \
            f"on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        if_key = Topology.add_new_port(node, u"gtpu_tunnel")
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)
        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)

        return sw_if_index

    @staticmethod
    def vpp_enable_gtpu_offload_rx(node, interface, gtpu_if_index):
        """Enable GTPU offload RX onto interface.

        :param node: Node to run command on.
        :param interface: Name of the specific interface.
        :param gtpu_if_index: Index of GTPU tunnel interface.

        :type node: dict
        :type interface: str
        :type gtpu_interface: int
        """
        sw_if_index = Topology.get_interface_sw_index(node, interface)

        cmd = u"gtpu_offload_rx"
        args = dict(
            hw_if_index=sw_if_index,
            sw_if_index=gtpu_if_index,
            enable=True
        )

        err_msg = f"Failed to enable GTPU offload RX on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_create_loopback(node, mac=None):
        """Create loopback interface on VPP node.

        :param node: Node to create loopback interface on.
        :param mac: Optional MAC address for loopback interface.
        :type node: dict
        :type mac: str
        :returns: SW interface index.
        :rtype: int
        :raises RuntimeError: If it is not possible to create loopback on the
            node.
        """
        cmd = u"create_loopback_instance"
        args = dict(
            mac_address=L2Util.mac_to_bin(mac) if mac else 0,
            is_specified=False,
            user_instance=0,
        )
        err_msg = f"Failed to create loopback interface on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        if_key = Topology.add_new_port(node, u"loopback")
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)
        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)
        if mac:
            mac = InterfaceUtil.vpp_get_interface_mac(node, ifc_name)
            Topology.update_interface_mac_address(node, if_key, mac)

        return sw_if_index

    @staticmethod
    def vpp_create_bond_interface(
            node, mode, load_balance=None, mac=None, gso=False):
        """Create bond interface on VPP node.

        :param node: DUT node from topology.
        :param mode: Link bonding mode.
        :param load_balance: Load balance (optional, valid for xor and lacp
            modes, otherwise ignored). Default: None.
        :param mac: MAC address to assign to the bond interface (optional).
            Default: None.
        :param gso: Enable GSO support (optional). Default: False.
        :type node: dict
        :type mode: str
        :type load_balance: str
        :type mac: str
        :type gso: bool
        :returns: Interface key (name) in topology.
        :rtype: str
        :raises RuntimeError: If it is not possible to create bond interface on
            the node.
        """
        cmd = u"bond_create2"
        args = dict(
            id=int(Constants.BITWISE_NON_ZERO),
            use_custom_mac=bool(mac is not None),
            mac_address=L2Util.mac_to_bin(mac) if mac else None,
            mode=getattr(
                LinkBondMode,
                f"BOND_API_MODE_{mode.replace(u'-', u'_').upper()}"
            ).value,
            lb=0 if load_balance is None else getattr(
                LinkBondLoadBalanceAlgo,
                f"BOND_API_LB_ALGO_{load_balance.upper()}"
            ).value,
            numa_only=False,
            enable_gso=gso
        )
        err_msg = f"Failed to create bond interface on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        InterfaceUtil.add_eth_interface(
            node, sw_if_index=sw_if_index, ifc_pfx=u"eth_bond"
        )
        if_key = Topology.get_interface_by_sw_index(node, sw_if_index)

        return if_key

    @staticmethod
    def add_eth_interface(
            node, ifc_name=None, sw_if_index=None, ifc_pfx=None,
            host_if_key=None):
        """Add ethernet interface to current topology.

        :param node: DUT node from topology.
        :param ifc_name: Name of the interface.
        :param sw_if_index: SW interface index.
        :param ifc_pfx: Interface key prefix.
        :param host_if_key: Host interface key from topology file.
        :type node: dict
        :type ifc_name: str
        :type sw_if_index: int
        :type ifc_pfx: str
        :type host_if_key: str
        """
        if_key = Topology.add_new_port(node, ifc_pfx)

        if ifc_name and sw_if_index is None:
            sw_if_index = InterfaceUtil.vpp_get_interface_sw_index(
                node, ifc_name)
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)
        if sw_if_index and ifc_name is None:
            ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)
        ifc_mac = InterfaceUtil.vpp_get_interface_mac(node, sw_if_index)
        Topology.update_interface_mac_address(node, if_key, ifc_mac)
        if host_if_key is not None:
            Topology.set_interface_numa_node(
                node, if_key, Topology.get_interface_numa_node(
                    node, host_if_key
                )
            )
            Topology.update_interface_pci_address(
                node, if_key, Topology.get_interface_pci_addr(node, host_if_key)
            )

    @staticmethod
    def vpp_create_avf_interface(
            node, if_key, num_rx_queues=None, rxq_size=0, txq_size=0):
        """Create AVF interface on VPP node.

        :param node: DUT node from topology.
        :param if_key: Interface key from topology file of interface
            to be bound to i40evf driver.
        :param num_rx_queues: Number of RX queues.
        :param rxq_size: Size of RXQ (0 = Default API; 512 = Default VPP).
        :param txq_size: Size of TXQ (0 = Default API; 512 = Default VPP).
        :type node: dict
        :type if_key: str
        :type num_rx_queues: int
        :type rxq_size: int
        :type txq_size: int
        :returns: AVF interface key (name) in topology.
        :rtype: str
        :raises RuntimeError: If it is not possible to create AVF interface on
            the node.
        """
        PapiSocketExecutor.run_cli_cmd(
            node, u"set logging class avf level debug"
        )

        cmd = u"avf_create"
        vf_pci_addr = Topology.get_interface_pci_addr(node, if_key)
        args = dict(
            pci_addr=InterfaceUtil.pci_to_int(vf_pci_addr),
            enable_elog=0,
            rxq_num=int(num_rx_queues) if num_rx_queues else 0,
            rxq_size=rxq_size,
            txq_size=txq_size
        )
        err_msg = f"Failed to create AVF interface on host {node[u'host']}"

        # FIXME: Remove once the fw/driver is upgraded.
        for _ in range(10):
            with PapiSocketExecutor(node) as papi_exec:
                try:
                    sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(
                        err_msg
                    )
                    break
                except AssertionError:
                    logger.error(err_msg)
        else:
            raise AssertionError(err_msg)

        InterfaceUtil.add_eth_interface(
            node, sw_if_index=sw_if_index, ifc_pfx=u"eth_avf",
            host_if_key=if_key
        )

        return Topology.get_interface_by_sw_index(node, sw_if_index)

    @staticmethod
    def vpp_create_af_xdp_interface(
            node, if_key, num_rx_queues=None, rxq_size=0, txq_size=0,
            mode=u"auto"):
        """Create AF_XDP interface on VPP node.

        :param node: DUT node from topology.
        :param if_key: Physical interface key from topology file of interface
            to be bound to compatible driver.
        :param num_rx_queues: Number of RX queues. (Optional, Default: none)
        :param rxq_size: Size of RXQ (0 = Default API; 512 = Default VPP).
        :param txq_size: Size of TXQ (0 = Default API; 512 = Default VPP).
        :param mode: AF_XDP interface mode. (Optional, Default: auto).
        :type node: dict
        :type if_key: str
        :type num_rx_queues: int
        :type rxq_size: int
        :type txq_size: int
        :type mode: str
        :returns: Interface key (name) in topology file.
        :rtype: str
        :raises RuntimeError: If it is not possible to create AF_XDP interface
            on the node.
        """
        PapiSocketExecutor.run_cli_cmd(
            node, u"set logging class af_xdp level debug"
        )

        cmd = u"af_xdp_create_v3"
        pci_addr = Topology.get_interface_pci_addr(node, if_key)
        args = dict(
            name=InterfaceUtil.pci_to_eth(node, pci_addr),
            host_if=InterfaceUtil.pci_to_eth(node, pci_addr),
            rxq_num=int(num_rx_queues) if num_rx_queues else 0,
            rxq_size=rxq_size,
            txq_size=txq_size,
            mode=getattr(AfXdpMode, f"AF_XDP_API_MODE_{mode.upper()}").value
        )
        err_msg = f"Failed to create AF_XDP interface on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        InterfaceUtil.vpp_set_interface_mac(
            node, sw_if_index, Topology.get_interface_mac(node, if_key)
        )
        InterfaceUtil.add_eth_interface(
            node, sw_if_index=sw_if_index, ifc_pfx=u"eth_af_xdp",
            host_if_key=if_key
        )

        return Topology.get_interface_by_sw_index(node, sw_if_index)

    @staticmethod
    def vpp_create_rdma_interface(
            node, if_key, num_rx_queues=None, rxq_size=0, txq_size=0,
            mode=u"auto"):
        """Create RDMA interface on VPP node.

        :param node: DUT node from topology.
        :param if_key: Physical interface key from topology file of interface
            to be bound to rdma-core driver.
        :param num_rx_queues: Number of RX queues.
        :param rxq_size: Size of RXQ (0 = Default API; 512 = Default VPP).
        :param txq_size: Size of TXQ (0 = Default API; 512 = Default VPP).
        :param mode: RDMA interface mode - auto/ibv/dv.
        :type node: dict
        :type if_key: str
        :type num_rx_queues: int
        :type rxq_size: int
        :type txq_size: int
        :type mode: str
        :returns: Interface key (name) in topology file.
        :rtype: str
        :raises RuntimeError: If it is not possible to create RDMA interface on
            the node.
        """
        PapiSocketExecutor.run_cli_cmd(
            node, u"set logging class rdma level debug"
        )

        cmd = u"rdma_create_v4"
        pci_addr = Topology.get_interface_pci_addr(node, if_key)
        args = dict(
            name=InterfaceUtil.pci_to_eth(node, pci_addr),
            host_if=InterfaceUtil.pci_to_eth(node, pci_addr),
            rxq_num=int(num_rx_queues) if num_rx_queues else 0,
            rxq_size=rxq_size,
            txq_size=txq_size,
            mode=getattr(RdmaMode, f"RDMA_API_MODE_{mode.upper()}").value,
            # Note: Set True for non-jumbo packets.
            no_multi_seg=False,
            max_pktlen=0,
            # TODO: Apply desired RSS flags.
            # rss4 kept 0 (auto) as API default.
            # rss6 kept 0 (auto) as API default.
        )
        err_msg = f"Failed to create RDMA interface on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        InterfaceUtil.vpp_set_interface_mac(
            node, sw_if_index, Topology.get_interface_mac(node, if_key)
        )
        InterfaceUtil.add_eth_interface(
            node, sw_if_index=sw_if_index, ifc_pfx=u"eth_rdma",
            host_if_key=if_key
        )

        return Topology.get_interface_by_sw_index(node, sw_if_index)

    @staticmethod
    def vpp_add_bond_member(node, interface, bond_if):
        """Add member interface to bond interface on VPP node.

        :param node: DUT node from topology.
        :param interface: Physical interface key from topology file.
        :param bond_if: Load balance
        :type node: dict
        :type interface: str
        :type bond_if: str
        :raises RuntimeError: If it is not possible to add member to bond
            interface on the node.
        """
        cmd = u"bond_add_member"
        args = dict(
            sw_if_index=Topology.get_interface_sw_index(node, interface),
            bond_sw_if_index=Topology.get_interface_sw_index(node, bond_if),
            is_passive=False,
            is_long_timeout=False
        )
        err_msg = f"Failed to add member {interface} to bond interface " \
            f"{bond_if} on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_show_bond_data_on_node(node, verbose=False):
        """Show (detailed) bond information on VPP node.

        :param node: DUT node from topology.
        :param verbose: If detailed information is required or not.
        :type node: dict
        :type verbose: bool
        """
        cmd = u"sw_bond_interface_dump"
        err_msg = f"Failed to get bond interface dump on host {node[u'host']}"

        data = f"Bond data on node {node[u'host']}:\n"
        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd).get_details(err_msg)

        for bond in details:
            data += f"{bond[u'interface_name']}\n"
            data += u"  mode: {m}\n".format(
                m=bond[u"mode"].name.replace(u"BOND_API_MODE_", u"").lower()
            )
            data += u"  load balance: {lb}\n".format(
                lb=bond[u"lb"].name.replace(u"BOND_API_LB_ALGO_", u"").lower()
            )
            data += f"  number of active members: {bond[u'active_members']}\n"
            if verbose:
                member_data = InterfaceUtil.vpp_bond_member_dump(
                    node, Topology.get_interface_by_sw_index(
                        node, bond[u"sw_if_index"]
                    )
                )
                for member in member_data:
                    if not member[u"is_passive"]:
                        data += f"    {member[u'interface_name']}\n"
            data += f"  number of members: {bond[u'members']}\n"
            if verbose:
                for member in member_data:
                    data += f"    {member[u'interface_name']}\n"
            data += f"  interface id: {bond[u'id']}\n"
            data += f"  sw_if_index: {bond[u'sw_if_index']}\n"
        logger.info(data)

    @staticmethod
    def vpp_bond_member_dump(node, interface):
        """Get bond interface slave(s) data on VPP node.

        :param node: DUT node from topology.
        :param interface: Physical interface key from topology file.
        :type node: dict
        :type interface: str
        :returns: Bond slave interface data.
        :rtype: dict
        """
        cmd = u"sw_member_interface_dump"
        args = dict(
            sw_if_index=Topology.get_interface_sw_index(node, interface)
        )
        err_msg = f"Failed to get slave dump on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, **args).get_details(err_msg)

        logger.debug(f"Member data:\n{details}")
        return details

    @staticmethod
    def vpp_show_bond_data_on_all_nodes(nodes, verbose=False):
        """Show (detailed) bond information on all VPP nodes in DICT__nodes.

        :param nodes: Nodes in the topology.
        :param verbose: If detailed information is required or not.
        :type nodes: dict
        :type verbose: bool
        """
        for node_data in nodes.values():
            if node_data[u"type"] == NodeType.DUT:
                InterfaceUtil.vpp_show_bond_data_on_node(node_data, verbose)

    @staticmethod
    def vpp_enable_input_acl_interface(
            node, interface, ip_version, table_index):
        """Enable input acl on interface.

        :param node: VPP node to setup interface for input acl.
        :param interface: Interface to setup input acl.
        :param ip_version: Version of IP protocol.
        :param table_index: Classify table index.
        :type node: dict
        :type interface: str or int
        :type ip_version: str
        :type table_index: int
        """
        cmd = u"input_acl_set_interface"
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            ip4_table_index=table_index if ip_version == u"ip4"
            else Constants.BITWISE_NON_ZERO,
            ip6_table_index=table_index if ip_version == u"ip6"
            else Constants.BITWISE_NON_ZERO,
            l2_table_index=table_index if ip_version == u"l2"
            else Constants.BITWISE_NON_ZERO,
            is_add=1)
        err_msg = f"Failed to enable input acl on interface {interface}"
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def get_interface_classify_table(node, interface):
        """Get name of classify table for the given interface.

        TODO: Move to Classify.py.

        :param node: VPP node to get data from.
        :param interface: Name or sw_if_index of a specific interface.
        :type node: dict
        :type interface: str or int
        :returns: Classify table name.
        :rtype: str
        """
        if isinstance(interface, str):
            sw_if_index = InterfaceUtil.get_sw_if_index(node, interface)
        else:
            sw_if_index = interface

        cmd = u"classify_table_by_interface"
        args = dict(
            sw_if_index=sw_if_index
        )
        err_msg = f"Failed to get classify table name by interface {interface}"
        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        return reply

    @staticmethod
    def get_sw_if_index(node, interface_name):
        """Get sw_if_index for the given interface from actual interface dump.

        FIXME: Delete and redirect callers to vpp_get_interface_sw_index.

        :param node: VPP node to get interface data from.
        :param interface_name: Name of the specific interface.
        :type node: dict
        :type interface_name: str
        :returns: sw_if_index of the given interface.
        :rtype: str
        """
        interface_data = InterfaceUtil.vpp_get_interface_data(
            node, interface=interface_name
        )
        return interface_data.get(u"sw_if_index")

    @staticmethod
    def vxlan_gpe_dump(node, interface_name=None):
        """Get VxLAN GPE data for the given interface.

        :param node: VPP node to get interface data from.
        :param interface_name: Name of the specific interface. If None,
            information about all VxLAN GPE interfaces is returned.
        :type node: dict
        :type interface_name: str
        :returns: Dictionary containing data for the given VxLAN GPE interface
            or if interface=None, the list of dictionaries with all VxLAN GPE
            interfaces.
        :rtype: dict or list
        """
        def process_vxlan_gpe_dump(vxlan_dump):
            """Process vxlan_gpe dump.

            :param vxlan_dump: Vxlan_gpe nterface dump.
            :type vxlan_dump: dict
            :returns: Processed vxlan_gpe interface dump.
            :rtype: dict
            """
            if vxlan_dump[u"is_ipv6"]:
                vxlan_dump[u"local"] = ip_address(vxlan_dump[u"local"])
                vxlan_dump[u"remote"] = ip_address(vxlan_dump[u"remote"])
            else:
                vxlan_dump[u"local"] = ip_address(vxlan_dump[u"local"][0:4])
                vxlan_dump[u"remote"] = ip_address(vxlan_dump[u"remote"][0:4])
            return vxlan_dump

        if interface_name is not None:
            sw_if_index = InterfaceUtil.get_interface_index(
                node, interface_name
            )
        else:
            sw_if_index = int(Constants.BITWISE_NON_ZERO)

        cmd = u"vxlan_gpe_tunnel_dump"
        args = dict(
            sw_if_index=sw_if_index
        )
        err_msg = f"Failed to get VXLAN-GPE dump on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, **args).get_details(err_msg)

        data = list() if interface_name is None else dict()
        for dump in details:
            if interface_name is None:
                data.append(process_vxlan_gpe_dump(dump))
            elif dump[u"sw_if_index"] == sw_if_index:
                data = process_vxlan_gpe_dump(dump)
                break

        logger.debug(f"VXLAN-GPE data:\n{data}")
        return data

    @staticmethod
    def assign_interface_to_fib_table(node, interface, table_id, ipv6=False):
        """Assign VPP interface to specific VRF/FIB table.

        :param node: VPP node where the FIB and interface are located.
        :param interface: Interface to be assigned to FIB.
        :param table_id: VRF table ID.
        :param ipv6: Assign to IPv6 table. Default False.
        :type node: dict
        :type interface: str or int
        :type table_id: int
        :type ipv6: bool
        """
        cmd = u"sw_interface_set_table"
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            is_ipv6=ipv6,
            vrf_id=int(table_id)
        )
        err_msg = f"Failed to assign interface {interface} to FIB table"
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def set_linux_interface_mac(
            node, interface, mac, namespace=None, vf_id=None):
        """Set MAC address for interface in linux.

        :param node: Node where to execute command.
        :param interface: Interface in namespace.
        :param mac: MAC to be assigned to interface.
        :param namespace: Execute command in namespace. Optional
        :param vf_id: Virtual Function id. Optional
        :type node: dict
        :type interface: str
        :type mac: str
        :type namespace: str
        :type vf_id: int
        """
        mac_str = f"vf {vf_id} mac {mac}" if vf_id is not None \
            else f"address {mac}"
        ns_str = f"ip netns exec {namespace}" if namespace else u""

        cmd = f"{ns_str} ip link set {interface} {mac_str}"
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def set_linux_interface_promisc(
            node, interface, namespace=None, vf_id=None, state=u"on"):
        """Set promisc state for interface in linux.

        :param node: Node where to execute command.
        :param interface: Interface in namespace.
        :param namespace: Exec command in namespace. (Optional, Default: None)
        :param vf_id: Virtual Function id. (Optional, Default: None)
        :param state: State of feature. (Optional, Default: on)
        :type node: dict
        :type interface: str
        :type namespace: str
        :type vf_id: int
        :type state: str
        """
        promisc_str = f"vf {vf_id} promisc {state}" if vf_id is not None \
            else f"promisc {state}"
        ns_str = f"ip netns exec {namespace}" if namespace else u""

        cmd = f"{ns_str} ip link set dev {interface} {promisc_str}"
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def set_linux_interface_trust_on(
            node, interface, namespace=None, vf_id=None):
        """Set trust on (promisc) for interface in linux.

        :param node: Node where to execute command.
        :param interface: Interface in namespace.
        :param namespace: Execute command in namespace. Optional
        :param vf_id: Virtual Function id. Optional
        :type node: dict
        :type interface: str
        :type namespace: str
        :type vf_id: int
        """
        trust_str = f"vf {vf_id} trust on" if vf_id is not None else u"trust on"
        ns_str = f"ip netns exec {namespace}" if namespace else u""

        cmd = f"{ns_str} ip link set dev {interface} {trust_str}"
        exec_cmd_no_error(node, cmd, sudo=True)
        cmd = f"{ns_str} ethtool --help"
        exec_cmd(node, cmd, sudo=True)
        cmd = f"{ns_str} ethtool -x {interface}"
        exec_cmd(node, cmd, sudo=True)
        cmd = f"{ns_str} ethtool -n {interface}"
        exec_cmd(node, cmd, sudo=True)
        cmd = f"{ns_str} ethtool -n {interface} rx-flow-hash ether"
        exec_cmd(node, cmd, sudo=True)
        cmd = f"{ns_str} ethtool -n {interface} rx-flow-hash tcp4"
        exec_cmd(node, cmd, sudo=True)
        cmd = f"{ns_str} ethtool -n {interface} rx-flow-hash udp4"
        exec_cmd(node, cmd, sudo=True)
        cmd = f"{ns_str} ethtool -n {interface} rx-flow-hash esp4"
        exec_cmd(node, cmd, sudo=True)
        cmd = f"{ns_str} ethtool -n {interface} rx-flow-hash tcp6"
        exec_cmd(node, cmd, sudo=True)
        cmd = f"{ns_str} ethtool -n {interface} rx-flow-hash udp6"
        exec_cmd(node, cmd, sudo=True)
        cmd = f"{ns_str} ethtool -n {interface} rx-flow-hash esp6"
        exec_cmd(node, cmd, sudo=True)
        cmd = f"{ns_str} ethtool -N {interface} rx-flow-hash esp4 sd"
        exec_cmd(node, cmd, sudo=True)
        cmd = f"{ns_str} ethtool -N {interface} rx-flow-hash udp4 sdfn"
        exec_cmd(node, cmd, sudo=True)
        cmd = f"{ns_str} ethtool -n {interface} rx-flow-hash esp4"
        exec_cmd(node, cmd, sudo=True)
        cmd = f"{ns_str} ethtool -n {interface} rx-flow-hash udp4"
        exec_cmd(node, cmd, sudo=True)

    @staticmethod
    def set_linux_interface_spoof_off(
            node, interface, namespace=None, vf_id=None):
        """Set spoof off for interface in linux.

        :param node: Node where to execute command.
        :param interface: Interface in namespace.
        :param namespace: Execute command in namespace. Optional
        :param vf_id: Virtual Function id. Optional
        :type node: dict
        :type interface: str
        :type namespace: str
        :type vf_id: int
        """
        spoof_str = f"vf {vf_id} spoof off" if vf_id is not None \
            else u"spoof off"
        ns_str = f"ip netns exec {namespace}" if namespace else u""

        cmd = f"{ns_str} ip link set dev {interface} {spoof_str}"
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def set_linux_interface_state(
            node, interface, namespace=None, state=u"up"):
        """Set operational state for interface in linux.

        :param node: Node where to execute command.
        :param interface: Interface in namespace.
        :param namespace: Execute command in namespace. Optional
        :param state: Up/Down.
        :type node: dict
        :type interface: str
        :type namespace: str
        :type state: str
        """
        ns_str = f"ip netns exec {namespace}" if namespace else u""

        cmd = f"{ns_str} ip link set dev {interface} {state}"
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def init_interface(node, ifc_key, driver, numvfs=0, osi_layer=u"L2", strict=True):
        """Init PCI device. Check driver compatibility and bind to proper
        drivers. Optionally create NIC VFs.

        :param node: DUT node.
        :param ifc_key: Interface key from topology file.
        :param driver: Base driver to use.
        :param numvfs: Number of VIFs to initialize, 0 - disable the VIFs.
        :param osi_layer: OSI Layer type to initialize TG with.
            Default value "L2" sets linux interface spoof off.
        :type node: dict
        :type ifc_key: str
        :type driver: str
        :type numvfs: int
        :type osi_layer: str
        :returns: Virtual Function topology interface keys.
        :rtype: list
        :raises RuntimeError: If a reason preventing initialization is found.
        """
        kernel_driver = Topology.get_interface_driver(node, ifc_key)
        vf_keys = []
        if driver == u"avf":
            if kernel_driver not in (
                    u"ice", u"iavf", u"i40e", u"i40evf"):
                raise RuntimeError(
                    f"AVF needs ice or i40e compatible driver, not "
                    f"{kernel_driver} at node {node[u'host']} ifc {ifc_key}"
                )
            vf_keys = InterfaceUtil.init_generic_interface(
                node, ifc_key, numvfs=numvfs, osi_layer=osi_layer, strict=strict,
            )
        elif driver == u"af_xdp":
            if kernel_driver not in (
                    u"ice", u"iavf", u"i40e", u"i40evf", u"mlx5_core",
                    u"ixgbe"):
                raise RuntimeError(
                    f"AF_XDP needs ice/i40e/rdma/ixgbe compatible driver, not "
                    f"{kernel_driver} at node {node[u'host']} ifc {ifc_key}"
                )
            vf_keys = InterfaceUtil.init_generic_interface(
                node, ifc_key, numvfs=numvfs, osi_layer=osi_layer, strict=strict,
            )
        elif driver == u"rdma-core":
            vf_keys = InterfaceUtil.init_generic_interface(
                node, ifc_key, numvfs=numvfs, osi_layer=osi_layer, strict=strict,
            )
        return vf_keys

    @staticmethod
    def init_generic_interface(node, ifc_key, numvfs=0, osi_layer=u"L2", strict=True):
        """Init PCI device. Bind to proper drivers. Optionally create NIC VFs.

        :param node: DUT node.
        :param ifc_key: Interface key from topology file.
        :param numvfs: Number of VIFs to initialize, 0 - disable the VIFs.
        :param osi_layer: OSI Layer type to initialize TG with.
            Default value "L2" sets linux interface spoof off.
        :type node: dict
        :type ifc_key: str
        :type numvfs: int
        :type osi_layer: str
        :returns: Virtual Function topology interface keys.
        :rtype: list
        :raises RuntimeError: If a reason preventing initialization is found.
        """
        # Read PCI address and driver.
        pf_pci_addr = Topology.get_interface_pci_addr(node, ifc_key)
        pf_mac_addr = Topology.get_interface_mac(node, ifc_key).split(":")
        uio_driver = Topology.get_uio_driver(node)
        kernel_driver = Topology.get_interface_driver(node, ifc_key)
        current_driver = DUTSetup.get_pci_dev_driver(
            node, pf_pci_addr.replace(u":", r"\:"))
        pf_dev = f"`basename /sys/bus/pci/devices/{pf_pci_addr}/net/*`"

        # Stop VPP to prevent deadlock.
        VPPUtil.stop_vpp_service(node)
        if current_driver != kernel_driver and strict:
            raise RuntimeError(f"Suite setup did not set {kernel_driver}")
        if not strict:
            # Not strict means suite setup.
            # Rebind even is driver matches, we do not trust previous suite.

            # PCI device must be re-bound to kernel driver before creating VFs.
            DUTSetup.verify_kernel_module(node, kernel_driver, force_load=True)
            # Unbind from current driver if bound.
            if current_driver:
                DUTSetup.pci_driver_unbind(node, pf_pci_addr)
            # Bind to kernel driver.
            DUTSetup.pci_driver_bind(node, pf_pci_addr, kernel_driver)

        # Initialize PCI VFs.
        DUTSetup.set_sriov_numvfs(node, pf_pci_addr, numvfs=numvfs)

        if not numvfs:
            if osi_layer == u"L2":
                InterfaceUtil.set_linux_interface_promisc(node, pf_dev)

        vf_ifc_keys = []
        # Set MAC address and bind each virtual function to uio driver.
        for vf_id in range(numvfs):
            vf_mac_addr = u":".join(
                [pf_mac_addr[0], pf_mac_addr[2], pf_mac_addr[3], pf_mac_addr[4],
                 pf_mac_addr[5], f"{vf_id:02x}"
                 ]
            )

            InterfaceUtil.set_linux_interface_trust_on(
                node, pf_dev, vf_id=vf_id
            )
            if osi_layer == u"L2":
                InterfaceUtil.set_linux_interface_spoof_off(
                    node, pf_dev, vf_id=vf_id
                )
            InterfaceUtil.set_linux_interface_mac(
                node, pf_dev, vf_mac_addr, vf_id=vf_id
            )
            InterfaceUtil.set_linux_interface_state(
                node, pf_dev, state=u"up"
            )

            vf_pci_addr = DUTSetup.get_virtfn_pci_addr(node, pf_pci_addr, vf_id)
            current_driver = DUTSetup.get_pci_dev_driver(
                node, vf_pci_addr.replace(":", r"\:")
            )
            if current_driver:
                DUTSetup.pci_vf_driver_unbind(
                    node, pf_pci_addr, vf_id
                )
            DUTSetup.pci_vf_driver_bind(
                node, pf_pci_addr, vf_id, uio_driver
            )

            # Add newly created ports into topology file
            vf_ifc_name = f"{ifc_key}_vif"
            vf_ifc_key = Topology.add_new_port(node, vf_ifc_name)
            Topology.update_interface_name(
                node, vf_ifc_key, vf_ifc_name+str(vf_id+1)
            )
            Topology.update_interface_mac_address(node, vf_ifc_key, vf_mac_addr)
            Topology.update_interface_pci_address(node, vf_ifc_key, vf_pci_addr)
            Topology.set_interface_numa_node(
                node, vf_ifc_key, Topology.get_interface_numa_node(
                    node, ifc_key
                )
            )
            vf_ifc_keys.append(vf_ifc_key)

        return vf_ifc_keys

    @staticmethod
    def vpp_sw_interface_rx_placement_dump(node):
        """Dump VPP interface RX placement on node.

        :param node: Node to run command on.
        :type node: dict
        :returns: Thread mapping information as a list of dictionaries.
        :rtype: list
        """
        cmd = u"sw_interface_rx_placement_dump"
        err_msg = f"Failed to run '{cmd}' PAPI command on host {node[u'host']}!"
        with PapiSocketExecutor(node) as papi_exec:
            for ifc in node[u"interfaces"].values():
                if ifc[u"vpp_sw_index"] is not None:
                    papi_exec.add(cmd, sw_if_index=ifc[u"vpp_sw_index"])
            details = papi_exec.get_details(err_msg)
        return sorted(details, key=lambda k: k[u"sw_if_index"])

    @staticmethod
    def vpp_sw_interface_rx_placement_dump_on_all_duts(nodes):
        """Dump VPP interface RX placement on all given nodes.

        :param nodes: Nodes to run command on.
        :type nodes: dict
        :returns: Thread mapping information as a list of dictionaries.
        :rtype: list
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                InterfaceUtil.vpp_sw_interface_rx_placement_dump(node)

    @staticmethod
    def vpp_sw_interface_set_rx_placement(
            node, sw_if_index, queue_id, worker_id):
        """Set interface RX placement to worker on node.

        :param node: Node to run command on.
        :param sw_if_index: VPP SW interface index.
        :param queue_id: VPP interface queue ID.
        :param worker_id: VPP worker ID (indexing from 0).
        :type node: dict
        :type sw_if_index: int
        :type queue_id: int
        :type worker_id: int
        :raises RuntimeError: If failed to run command on host or if no API
            reply received.
        """
        cmd = u"sw_interface_set_rx_placement"
        err_msg = f"Failed to set interface RX placement to worker " \
            f"on host {node[u'host']}!"
        args = dict(
            sw_if_index=sw_if_index,
            queue_id=queue_id,
            worker_id=worker_id,
            is_main=False
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_round_robin_rx_placement(
            node, prefix, workers=None):
        """Set Round Robin interface RX placement on all worker threads
        on node.

        If specified, workers limits the number of physical cores used
        for data plane I/O work. Other cores are presumed to do something else,
        e.g. asynchronous crypto processing.
        None means all workers are used for data plane work.

        :param node: Topology nodes.
        :param prefix: Interface name prefix.
        :param workers: Comma separated worker index numbers intended for
            dataplane work.
        :type node: dict
        :type prefix: str
        :type workers: str
        """
        thread_data = VPPUtil.vpp_show_threads(node)
        worker_cnt = len(thread_data) - 1
        if not worker_cnt:
            return
        worker_ids = list()
        if workers:
            for item in thread_data:
                if str(item.cpu_id) in workers.split(u","):
                    worker_ids.append(item.id)
        else:
            for item in thread_data:
                if u"vpp_main" not in item.name:
                    worker_ids.append(item.id)

        worker_idx = 0
        for placement in InterfaceUtil.vpp_sw_interface_rx_placement_dump(node):
            for interface in node[u"interfaces"].values():
                if placement[u"sw_if_index"] == interface[u"vpp_sw_index"] \
                    and prefix in interface[u"name"]:
                    InterfaceUtil.vpp_sw_interface_set_rx_placement(
                        node, placement[u"sw_if_index"], placement[u"queue_id"],
                        worker_ids[worker_idx % len(worker_ids)] - 1
                    )
                    worker_idx += 1

    @staticmethod
    def vpp_round_robin_rx_placement_on_all_duts(
            nodes, prefix, use_dp_cores=False):
        """Set Round Robin interface RX placement on worker threads
        on all DUTs.

        If specified, workers limits the number of physical cores used
        for data plane I/O work. Other cores are presumed to do something else,
        e.g. asynchronous crypto processing.
        None means all cores are used for data plane work.

        :param nodes: Topology nodes.
        :param prefix: Interface name prefix.
        :param use_dp_cores: Limit to dataplane cores.
        :type nodes: dict
        :type prefix: str
        :type use_dp_cores: bool
        """
        for node_name, node in nodes.items():
            if node["type"] == NodeType.DUT:
                workers = None
                if use_dp_cores:
                    workers = BuiltIn().get_variable_value(
                        f"${{{node_name}_cpu_dp}}"
                    )
                InterfaceUtil.vpp_round_robin_rx_placement(
                    node, prefix, workers
                )
