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

"""Interface util library."""

from time import time, sleep

from robot.api import logger

from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.PapiExecutor import PapiExecutor
from resources.libraries.python.PapiErrors import PapiError
from resources.libraries.python.IPUtil import convert_ipv4_netmask_prefix
from resources.libraries.python.IPUtil import IPUtil
from resources.libraries.python.parsers.JsonParser import JsonParser
from resources.libraries.python.ssh import SSH, exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal
from resources.libraries.python.VatJsonUtil import VatJsonUtil
from resources.libraries.python.VPPUtil import VPPUtil


class InterfaceUtil(object):
    """General utilities for managing interfaces"""

    __UDEV_IF_RULES_FILE = '/etc/udev/rules.d/10-network.rules'

    @staticmethod
    def set_interface_state(node, interface, state, if_type="key"):
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

        if if_type == "key":
            if isinstance(interface, basestring):
                sw_if_index = Topology.get_interface_sw_index(node, interface)
                iface_name = Topology.get_interface_name(node, interface)
            else:
                sw_if_index = interface
        elif if_type == "name":
            iface_key = Topology.get_interface_by_name(node, interface)
            if iface_key is not None:
                sw_if_index = Topology.get_interface_sw_index(node, iface_key)
            iface_name = interface
        else:
            raise ValueError("if_type unknown: {}".format(if_type))

        if node['type'] == NodeType.DUT:
            if state == 'up':
                state = 'admin-up link-up'
            elif state == 'down':
                state = 'admin-down link-down'
            else:
                raise ValueError('Unexpected interface state: {}'.format(state))
            VatExecutor.cmd_from_template(node, 'set_if_state.vat',
                                          sw_if_index=sw_if_index, state=state)
        elif node['type'] == NodeType.TG or node['type'] == NodeType.VM:
            cmd = 'ip link set {} {}'.format(iface_name, state)
            exec_cmd_no_error(node, cmd, sudo=True)
        else:
            raise ValueError('Node {} has unknown NodeType: "{}"'
                             .format(node['host'], node['type']))

    @staticmethod
    def set_interface_ethernet_mtu(node, iface_key, mtu):
        """Set Ethernet MTU for specified interface.

        Function can be used only for TGs.

        :param node: Node where the interface is.
        :param iface_key: Interface key from topology file.
        :param mtu: MTU to set.
        :type node: dict
        :type iface_key: str
        :type mtu: int
        :returns: Nothing.
        :raises ValueError: If the node type is "DUT".
        :raises ValueError: If the node has an unknown node type.
        """
        if node['type'] == NodeType.DUT:
            raise ValueError('Node {}: Setting Ethernet MTU for interface '
                             'on DUT nodes not supported', node['host'])
        elif node['type'] == NodeType.TG:
            iface_name = Topology.get_interface_name(node, iface_key)
            cmd = 'ip link set {} mtu {}'.format(iface_name, mtu)
            exec_cmd_no_error(node, cmd, sudo=True)
        else:
            raise ValueError('Node {} has unknown NodeType: "{}"'
                             .format(node['host'], node['type']))

    @staticmethod
    def set_default_ethernet_mtu_on_all_interfaces_on_node(node):
        """Set default Ethernet MTU on all interfaces on node.

        Function can be used only for TGs.

        :param node: Node where to set default MTU.
        :type node: dict
        :returns: Nothing.
        """
        for ifc in node['interfaces']:
            InterfaceUtil.set_interface_ethernet_mtu(node, ifc, 1500)

    @staticmethod
    def vpp_set_interface_mtu(node, interface, mtu=9200):
        """Set Ethernet MTU on interface.

        :param node: VPP node.
        :param interface: Interface to setup MTU. Default: 9200.
        :param mtu: Ethernet MTU size in Bytes.
        :type node: dict
        :type interface: str or int
        :type mtu: int
        """
        if isinstance(interface, basestring):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        else:
            sw_if_index = interface

        if sw_if_index:
            with VatTerminal(node, json_param=False) as vat:
                vat.vat_terminal_exec_cmd_from_template(
                    "hw_interface_set_mtu.vat", sw_if_index=sw_if_index,
                    mtu=mtu)

    @staticmethod
    def vpp_set_interfaces_mtu_on_node(node, mtu=9200):
        """Set Ethernet MTU on all interfaces.

        :param node: VPP node.
        :param mtu: Ethernet MTU size in Bytes. Default: 9200.
        :type node: dict
        :type mtu: int
        """
        for interface in node['interfaces']:
            InterfaceUtil.vpp_set_interface_mtu(node, interface, mtu)

    @staticmethod
    def vpp_set_interfaces_mtu_on_all_duts(nodes, mtu=9200):
        """Set Ethernet MTU on all interfaces on all DUTs.

        :param nodes: VPP nodes.
        :param mtu: Ethernet MTU size in Bytes. Default: 9200.
        :type nodes: dict
        :type mtu: int
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                InterfaceUtil.vpp_set_interfaces_mtu_on_node(node, mtu)

    @staticmethod
    def vpp_node_interfaces_ready_wait(node, timeout=30):
        """Wait until all interfaces with admin-up are in link-up state.

        :param node: Node to wait on.
        :param timeout: Waiting timeout in seconds (optional, default 10s).
        :type node: dict
        :type timeout: int
        :returns: Nothing.
        :raises RuntimeError: If the timeout period value has elapsed.
        """
        if_ready = False
        not_ready = []
        start = time()
        while not if_ready:
            out = InterfaceUtil.vpp_get_interface_data(node)
            if time() - start > timeout:
                for interface in out:
                    if interface.get('admin_up_down') == 1:
                        if interface.get('link_up_down') != 1:
                            logger.debug('{0} link-down'.format(
                                interface.get('interface_name')))
                raise RuntimeError('timeout, not up {0}'.format(not_ready))
            not_ready = []
            for interface in out:
                if interface.get('admin_up_down') == 1:
                    if interface.get('link_up_down') != 1:
                        not_ready.append(interface.get('interface_name'))
            if not not_ready:
                if_ready = True
            else:
                logger.debug('Interfaces still in link-down state: {0}, '
                             'waiting...'.format(not_ready))
                sleep(1)

    @staticmethod
    def vpp_nodes_interfaces_ready_wait(nodes, timeout=30):
        """Wait until all interfaces with admin-up are in link-up state for
        listed nodes.

        :param nodes: List of nodes to wait on.
        :param timeout: Seconds to wait per node for all interfaces to come up.
        :type nodes: list
        :type timeout: int
        :returns: Nothing.
        """
        for node in nodes:
            InterfaceUtil.vpp_node_interfaces_ready_wait(node, timeout)

    @staticmethod
    def all_vpp_interfaces_ready_wait(nodes, timeout=30):
        """Wait until all interfaces with admin-up are in link-up state for all
        nodes in the topology.

        :param nodes: Nodes in the topology.
        :param timeout: Seconds to wait per node for all interfaces to come up.
        :type nodes: dict
        :type timeout: int
        :returns: Nothing.
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                InterfaceUtil.vpp_node_interfaces_ready_wait(node, timeout)

    @staticmethod
    def vpp_get_interface_data(node, interface=None):
        """Get all interface data from a VPP node. If a name or
        sw_interface_index is provided, return only data for the matching
        interface.

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
        with VatTerminal(node) as vat:
            response = vat.vat_terminal_exec_cmd_from_template(
                "interface_dump.vat")

        data = response[0]

        if interface is not None:
            if isinstance(interface, basestring):
                param = "interface_name"
            elif isinstance(interface, int):
                param = "sw_if_index"
            else:
                raise TypeError
            for data_if in data:
                if data_if[param] == interface:
                    return data_if
            return dict()
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
        if if_data['sup_sw_if_index'] != if_data['sw_if_index']:
            if_data = InterfaceUtil.vpp_get_interface_data(
                node, if_data['sup_sw_if_index'])
        try:
            if_name = if_data["interface_name"]
        except KeyError:
            if_name = None
        return if_name

    @staticmethod
    def vpp_get_interface_mac(node, interface=None):
        """Get MAC address for the given interface from actual interface dump.

        :param node: VPP node to get interface data from.
        :param interface: Numeric index or name string of a specific interface.
        :type node: dict
        :type interface: int or str
        :returns: MAC address.
        :rtype: str
        """

        if_data = InterfaceUtil.vpp_get_interface_data(node, interface)
        if if_data['sup_sw_if_index'] != if_data['sw_if_index']:
            if_data = InterfaceUtil.vpp_get_interface_data(
                node, if_data['sup_sw_if_index'])
        mac_data = [str(hex(item))[2:] for item in if_data['l2_address'][:6]]
        mac_data_nice = []
        for item in mac_data:
            if len(item) == 1:
                item = '0' + item
            mac_data_nice.append(item)
        mac = ":".join(mac_data_nice)
        return mac

    @staticmethod
    def vpp_get_interface_ip_addresses(node, interface, ip_version):
        """Get list of IP addresses from an interface on a VPP node.

         :param node: VPP node to get data from.
         :param interface: Name of an interface on the VPP node.
         :param ip_version: IP protocol version (ipv4 or ipv6).
         :type node: dict
         :type interface: str
         :type ip_version: str
         :returns: List of dictionaries, each containing IP address, subnet
            prefix length and also the subnet mask for ipv4 addresses.
            Note: A single interface may have multiple IP addresses assigned.
         :rtype: list
        """

        try:
            sw_if_index = Topology.convert_interface_reference(
                node, interface, "sw_if_index")
        except RuntimeError:
            if isinstance(interface, basestring):
                sw_if_index = InterfaceUtil.get_sw_if_index(node, interface)
            else:
                raise

        with VatTerminal(node) as vat:
            response = vat.vat_terminal_exec_cmd_from_template(
                "ip_address_dump.vat", ip_version=ip_version,
                sw_if_index=sw_if_index)

        data = response[0]

        if ip_version == "ipv4":
            for item in data:
                item["netmask"] = convert_ipv4_netmask_prefix(
                    item["prefix_length"])
        return data

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
            cmd = 'sh -c "echo {0} > /sys/bus/pci/drivers/{1}/unbind"'\
                .format(pci_addr, old_driver)
            (ret_code, _, _) = ssh.exec_command_sudo(cmd)
            if int(ret_code) != 0:
                raise RuntimeError("'{0}' failed on '{1}'"
                                   .format(cmd, node['host']))

        # Bind to the new driver
        cmd = 'sh -c "echo {0} > /sys/bus/pci/drivers/{1}/bind"'\
            .format(pci_addr, driver)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise RuntimeError("'{0}' failed on '{1}'"
                               .format(cmd, node['host']))

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
    def tg_set_interfaces_udev_rules(node):
        """Set udev rules for interfaces.

        Create udev rules file in /etc/udev/rules.d where are rules for each
        interface used by TG node, based on MAC interface has specific name.
        So after unbind and bind again to kernel driver interface has same
        name as before. This must be called after TG has set name for each
        port in topology dictionary.
        udev rule example
        SUBSYSTEM=="net", ACTION=="add", ATTR{address}=="52:54:00:e1:8a:0f",
        NAME="eth1"

        :param node: Node to set udev rules on (must be TG node).
        :type node: dict
        :raises RuntimeError: If setting of udev rules fails.
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = 'rm -f {0}'.format(InterfaceUtil.__UDEV_IF_RULES_FILE)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise RuntimeError("'{0}' failed on '{1}'"
                               .format(cmd, node['host']))

        for interface in node['interfaces'].values():
            rule = 'SUBSYSTEM==\\"net\\", ACTION==\\"add\\", ATTR{address}' + \
                   '==\\"' + interface['mac_address'] + '\\", NAME=\\"' + \
                   interface['name'] + '\\"'
            cmd = 'sh -c "echo \'{0}\' >> {1}"'.format(
                rule, InterfaceUtil.__UDEV_IF_RULES_FILE)
            (ret_code, _, _) = ssh.exec_command_sudo(cmd)
            if int(ret_code) != 0:
                raise RuntimeError("'{0}' failed on '{1}'"
                                   .format(cmd, node['host']))

        cmd = '/etc/init.d/udev restart'
        ssh.exec_command_sudo(cmd)

    @staticmethod
    def tg_set_interfaces_default_driver(node):
        """Set interfaces default driver specified in topology yaml file.

        :param node: Node to setup interfaces driver on (must be TG node).
        :type node: dict
        """
        for interface in node['interfaces'].values():
            InterfaceUtil.tg_set_interface_driver(node,
                                                  interface['pci_address'],
                                                  interface['driver'])

    @staticmethod
    def update_vpp_interface_data_on_node(node):
        """Update vpp generated interface data for a given node in DICT__nodes.

        Updates interface names, software if index numbers and any other details
        generated specifically by vpp that are unknown before testcase run.
        It does this by dumping interface list to JSON output from all
        devices using vpp_api_test, and pairing known information from topology
        (mac address/pci address of interface) to state from VPP.

        :param node: Node selected from DICT__nodes.
        :type node: dict
        """
        vat_executor = VatExecutor()
        vat_executor.execute_script_json_out("dump_interfaces.vat", node)
        interface_dump_json = vat_executor.get_script_stdout()
        VatJsonUtil.update_vpp_interface_data_from_json(node,
                                                        interface_dump_json)

    @staticmethod
    def update_nic_interface_names(node):
        """Update interface names based on nic type and PCI address.

        This method updates interface names in the same format as VPP does.

        :param node: Node dictionary.
        :type node: dict
        """
        for ifc in node['interfaces'].values():
            if_pci = ifc['pci_address'].replace('.', ':').split(':')
            bus = '{:x}'.format(int(if_pci[1], 16))
            dev = '{:x}'.format(int(if_pci[2], 16))
            fun = '{:x}'.format(int(if_pci[3], 16))
            loc = '{bus}/{dev}/{fun}'.format(bus=bus, dev=dev, fun=fun)
            if ifc['model'] == 'Intel-XL710':
                ifc['name'] = 'FortyGigabitEthernet{loc}'.format(loc=loc)
            elif ifc['model'] == 'Intel-X710':
                ifc['name'] = 'TenGigabitEthernet{loc}'.format(loc=loc)
            elif ifc['model'] == 'Intel-X520-DA2':
                ifc['name'] = 'TenGigabitEthernet{loc}'.format(loc=loc)
            elif ifc['model'] == 'Cisco-VIC-1385':
                ifc['name'] = 'FortyGigabitEthernet{loc}'.format(loc=loc)
            elif ifc['model'] == 'Cisco-VIC-1227':
                ifc['name'] = 'TenGigabitEthernet{loc}'.format(loc=loc)
            else:
                ifc['name'] = 'UnknownEthernet{loc}'.format(loc=loc)

    @staticmethod
    def update_nic_interface_names_on_all_duts(nodes):
        """Update interface names based on nic type and PCI address on all DUTs.

        This method updates interface names in the same format as VPP does.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                InterfaceUtil.update_nic_interface_names(node)

    @staticmethod
    def update_tg_interface_data_on_node(node, skip_tg_udev=False):
        """Update interface name for TG/linux node in DICT__nodes.

        .. note::
            # for dev in `ls /sys/class/net/`;
            > do echo "\"`cat /sys/class/net/$dev/address`\": \"$dev\""; done
            "52:54:00:9f:82:63": "eth0"
            "52:54:00:77:ae:a9": "eth1"
            "52:54:00:e1:8a:0f": "eth2"
            "00:00:00:00:00:00": "lo"

        :param node: Node selected from DICT__nodes.
        :param skip_tg_udev: Skip udev rename on TG node.
        :type node: dict
        :type skip_tg_udev: bool
        :raises RuntimeError: If getting of interface name and MAC fails.
        """
        # First setup interface driver specified in yaml file
        InterfaceUtil.tg_set_interfaces_default_driver(node)

        # Get interface names
        ssh = SSH()
        ssh.connect(node)

        cmd = ('for dev in `ls /sys/class/net/`; do echo "\\"`cat '
               '/sys/class/net/$dev/address`\\": \\"$dev\\""; done;')

        (ret_code, stdout, _) = ssh.exec_command(cmd)
        if int(ret_code) != 0:
            raise RuntimeError('Get interface name and MAC failed')
        tmp = "{" + stdout.rstrip().replace('\n', ',') + "}"
        interfaces = JsonParser().parse_data(tmp)
        for interface in node['interfaces'].values():
            name = interfaces.get(interface['mac_address'])
            if name is None:
                continue
            interface['name'] = name

        # Set udev rules for interfaces
        if not skip_tg_udev:
            InterfaceUtil.tg_set_interfaces_udev_rules(node)

    @staticmethod
    def iface_update_numa_node(node):
        """For all interfaces from topology file update numa node based on
           information from the node.

        :param node: Node from topology.
        :type node: dict
        :returns: Nothing.
        :raises ValueError: If numa node ia less than 0.
        :raises RuntimeError: If update of numa node failes.
        """
        ssh = SSH()
        for if_key in Topology.get_node_interfaces(node):
            if_pci = Topology.get_interface_pci_addr(node, if_key)
            ssh.connect(node)
            cmd = "cat /sys/bus/pci/devices/{}/numa_node".format(if_pci)
            for _ in range(3):
                (ret, out, _) = ssh.exec_command(cmd)
                if ret == 0:
                    try:
                        numa_node = int(out)
                        if numa_node < 0:
                            if CpuUtils.cpu_node_count(node) == 1:
                                numa_node = 0
                            else:
                                raise ValueError
                    except ValueError:
                        logger.trace('Reading numa location failed for: {0}'
                                     .format(if_pci))
                    else:
                        Topology.set_interface_numa_node(node, if_key,
                                                         numa_node)
                        break
            else:
                raise RuntimeError('Update numa node failed for: {0}'
                                   .format(if_pci))

    @staticmethod
    def update_all_numa_nodes(nodes, skip_tg=False):
        """For all nodes and all their interfaces from topology file update numa
        node information based on information from the node.

        :param nodes: Nodes in the topology.
        :param skip_tg: Skip TG node
        :type nodes: dict
        :type skip_tg: bool
        :returns: Nothing.
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                InterfaceUtil.iface_update_numa_node(node)
            elif node['type'] == NodeType.TG and not skip_tg:
                InterfaceUtil.iface_update_numa_node(node)

    @staticmethod
    def update_all_interface_data_on_all_nodes(nodes, skip_tg=False,
                                               skip_tg_udev=False,
                                               numa_node=False):
        """Update interface names on all nodes in DICT__nodes.

        This method updates the topology dictionary by querying interface lists
        of all nodes mentioned in the topology dictionary.

        :param nodes: Nodes in the topology.
        :param skip_tg: Skip TG node.
        :param skip_tg_udev: Skip udev rename on TG node.
        :param numa_node: Retrieve numa_node location.
        :type nodes: dict
        :type skip_tg: bool
        :type skip_tg_udev: bool
        :type numa_node: bool
        """
        for node_data in nodes.values():
            if node_data['type'] == NodeType.DUT:
                InterfaceUtil.update_vpp_interface_data_on_node(node_data)
            elif node_data['type'] == NodeType.TG and not skip_tg:
                InterfaceUtil.update_tg_interface_data_on_node(
                    node_data, skip_tg_udev)

            if numa_node:
                if node_data['type'] == NodeType.DUT:
                    InterfaceUtil.iface_update_numa_node(node_data)
                elif node_data['type'] == NodeType.TG and not skip_tg:
                    InterfaceUtil.iface_update_numa_node(node_data)

    @staticmethod
    def create_vlan_subinterface(node, interface, vlan):
        """Create VLAN subinterface on node.

        :param node: Node to add VLAN subinterface on.
        :param interface: Interface name on which create VLAN subinterface.
        :param vlan: VLAN ID of the subinterface to be created.
        :type node: dict
        :type interface: str
        :type vlan: int
        :returns: Name and index of created subinterface.
        :rtype: tuple
        :raises RuntimeError: if it is unable to create VLAN subinterface on the
            node.
        """
        iface_key = Topology.get_interface_by_name(node, interface)
        sw_if_index = Topology.get_interface_sw_index(node, iface_key)

        output = VatExecutor.cmd_from_template(node, "create_vlan_subif.vat",
                                               sw_if_index=sw_if_index,
                                               vlan=vlan)
        if output[0]["retval"] == 0:
            sw_vlan_idx = output[0]["sw_if_index"]
            logger.trace('VLAN subinterface with sw_if_index {} and VLAN ID {} '
                         'created on node {}'.format(sw_vlan_idx,
                                                     vlan, node['host']))
            if_key = Topology.add_new_port(node, "vlan_subif")
            Topology.update_interface_sw_if_index(node, if_key, sw_vlan_idx)
            ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_vlan_idx)
            Topology.update_interface_name(node, if_key, ifc_name)
        else:
            raise RuntimeError('Unable to create VLAN subinterface on node {}'
                               .format(node['host']))

        with VatTerminal(node, False) as vat:
            vat.vat_terminal_exec_cmd('exec show interfaces')

        return '{}.{}'.format(interface, vlan), sw_vlan_idx

    @staticmethod
    def create_vxlan_interface(node, vni, source_ip, destination_ip):
        """Create VXLAN interface and return sw if index of created interface.

        Executes "vxlan_add_del_tunnel src {src} dst {dst} vni {vni}" VAT
        command on the node.

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
        output = VatExecutor.cmd_from_template(node, "vxlan_create.vat",
                                               src=source_ip,
                                               dst=destination_ip,
                                               vni=vni)
        output = output[0]

        if output["retval"] == 0:
            sw_if_idx = output["sw_if_index"]
            if_key = Topology.add_new_port(node, "vxlan_tunnel")
            Topology.update_interface_sw_if_index(node, if_key, sw_if_idx)
            ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_idx)
            Topology.update_interface_name(node, if_key, ifc_name)
            return sw_if_idx
        else:
            raise RuntimeError("Unable to create VXLAN interface on node {0}"
                               .format(node))

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
        param = "sw_if_index"
        if interface is None:
            param = ''
            sw_if_index = ''
        elif isinstance(interface, basestring):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        elif isinstance(interface, int):
            sw_if_index = interface
        else:
            raise TypeError("Wrong interface format {0}".format(interface))

        with VatTerminal(node) as vat:
            response = vat.vat_terminal_exec_cmd_from_template(
                "vxlan_dump.vat", param=param, sw_if_index=sw_if_index)

        if sw_if_index:
            for vxlan in response[0]:
                if vxlan["sw_if_index"] == sw_if_index:
                    return vxlan
            return {}
        return response[0]

    @staticmethod
    def vhost_user_dump(node):
        """Get vhost-user data for the given node.

        :param node: VPP node to get interface data from.
        :type node: dict
        :returns: List of dictionaries with all vhost-user interfaces.
        :rtype: list
        """
        with VatTerminal(node) as vat:
            response = vat.vat_terminal_exec_cmd_from_template(
                "vhost_user_dump.vat")

        return response[0]

    @staticmethod
    def tap_dump(node, name=None):
        """Get all TAP interface data from the given node, or data about
        a specific TAP interface.

        :param node: VPP node to get data from.
        :param name: Optional name of a specific TAP interface.
        :type node: dict
        :type name: str
        :returns: Dictionary of information about a specific TAP interface, or
            a List of dictionaries containing all TAP data for the given node.
        :rtype: dict or list
        """
        with VatTerminal(node) as vat:
            response = vat.vat_terminal_exec_cmd_from_template(
                "tap_dump.vat")
        if name is None:
            return response[0]
        for item in response[0]:
            if name == item['dev_name']:
                return item
        return {}

    @staticmethod
    def create_subinterface(node, interface, sub_id, outer_vlan_id=None,
                            inner_vlan_id=None, type_subif=None):
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

        outer_vlan_id = 'outer_vlan_id {0}'.format(outer_vlan_id)\
            if outer_vlan_id else ''

        inner_vlan_id = 'inner_vlan_id {0}'.format(inner_vlan_id)\
            if inner_vlan_id else ''

        if type_subif is None:
            type_subif = ''

        if isinstance(interface, basestring):
            iface_key = Topology.get_interface_by_name(node, interface)
            sw_if_index = Topology.get_interface_sw_index(node, iface_key)
        else:
            sw_if_index = interface

        output = VatExecutor.cmd_from_template(node, "create_sub_interface.vat",
                                               sw_if_index=sw_if_index,
                                               sub_id=sub_id,
                                               outer_vlan_id=outer_vlan_id,
                                               inner_vlan_id=inner_vlan_id,
                                               type_subif=type_subif)

        if output[0]["retval"] == 0:
            sw_vlan_idx = output[0]["sw_if_index"]
            logger.trace('Created subinterface with index {}'
                         .format(sw_vlan_idx))
            if_key = Topology.add_new_port(node, "subinterface")
            Topology.update_interface_sw_if_index(node, if_key, sw_vlan_idx)
            ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_vlan_idx)
            Topology.update_interface_name(node, if_key, ifc_name)
        else:
            raise RuntimeError('Unable to create sub-interface on node {}'
                               .format(node['host']))

        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd('exec show interfaces')

        name = '{}.{}'.format(interface, sub_id)
        return name, sw_vlan_idx

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
        output = VatExecutor.cmd_from_template(node, "create_gre.vat",
                                               src=source_ip,
                                               dst=destination_ip)
        output = output[0]

        if output["retval"] == 0:
            sw_if_idx = output["sw_if_index"]

            vat_executor = VatExecutor()
            vat_executor.execute_script_json_out("dump_interfaces.vat", node)
            interface_dump_json = vat_executor.get_script_stdout()
            name = VatJsonUtil.get_interface_name_from_json(
                interface_dump_json, sw_if_idx)

            if_key = Topology.add_new_port(node, "gre_tunnel")
            Topology.update_interface_sw_if_index(node, if_key, sw_if_idx)
            Topology.update_interface_name(node, if_key, name)

            return name, sw_if_idx
        else:
            raise RuntimeError('Unable to create GRE tunnel on node {}.'
                               .format(node))

    @staticmethod
    def vpp_create_loopback(node):
        """Create loopback interface on VPP node.

        :param node: Node to create loopback interface on.
        :type node: dict
        :returns: SW interface index.
        :rtype: int
        :raises RuntimeError: If it is not possible to create loopback on the
            node.
        """
        out = VatExecutor.cmd_from_template(node, "create_loopback.vat")
        if out[0].get('retval') == 0:
            sw_if_idx = out[0].get('sw_if_index')
            if_key = Topology.add_new_port(node, "loopback")
            Topology.update_interface_sw_if_index(node, if_key, sw_if_idx)
            ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_idx)
            Topology.update_interface_name(node, if_key, ifc_name)
            return sw_if_idx
        else:
            raise RuntimeError('Create loopback failed on node "{}"'
                               .format(node['host']))

    @staticmethod
    def vpp_create_bond_interface(node, mode, load_balance=None, mac=None):
        """Create bond interface on VPP node.

        :param node: DUT node from topology.
        :param mode: Link bonding mode.
        :param load_balance: Load balance (optional, valid for xor and lacp
            modes, otherwise ignored).
        :param mac: MAC address to assign to the bond interface (optional).
        :type node: dict
        :type mode: str
        :type load_balance: str
        :type mac: str
        :returns: Interface key (name) in topology.
        :rtype: str
        :raises RuntimeError: If it is not possible to create bond interface on
            the node.
        """
        hw_addr = '' if mac is None else 'hw-addr {mac}'.format(mac=mac)
        ldb = '' if load_balance is None \
            else 'lb {ldb}'.format(ldb=load_balance)

        output = VatExecutor.cmd_from_template(
            node, 'create_bond_interface.vat', mode=mode, lb=ldb, mac=hw_addr)

        if output[0].get('retval') == 0:
            sw_if_idx = output[0].get('sw_if_index')
            InterfaceUtil.add_eth_interface(node, sw_if_idx=sw_if_idx,
                                            ifc_pfx='eth_bond')
            if_key = Topology.get_interface_by_sw_index(node, sw_if_idx)
            return if_key
        else:
            raise RuntimeError('Create bond interface failed on "{host}"'.
                               format(host=node['host']))

    @staticmethod
    def add_eth_interface(node, ifc_name=None, sw_if_idx=None, ifc_pfx=None):
        """Add ethernet interface to current topology.

        :param node: DUT node from topology.
        :param ifc_name: Name of the interface.
        :param sw_if_idx: SW interface index.
        :param ifc_pfx: Interface key prefix.
        :type node: dict
        :type ifc_name: str
        :type sw_if_idx: int
        :type ifc_pfx: str
        """
        if_key = Topology.add_new_port(node, ifc_pfx)

        vat_executor = VatExecutor()
        vat_executor.execute_script_json_out("dump_interfaces.vat", node)
        interface_dump_json = vat_executor.get_script_stdout()

        if ifc_name and sw_if_idx is None:
            sw_if_idx = VatJsonUtil.get_interface_sw_index_from_json(
                interface_dump_json, ifc_name)
        Topology.update_interface_sw_if_index(node, if_key, sw_if_idx)
        if sw_if_idx and ifc_name is None:
            ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_idx)
        Topology.update_interface_name(node, if_key, ifc_name)
        ifc_mac = VatJsonUtil.get_interface_mac_from_json(
            interface_dump_json, sw_if_idx)
        Topology.update_interface_mac_address(node, if_key, ifc_mac)

    @staticmethod
    def vpp_create_avf_interface(node, vf_pci_addr, num_rx_queues=None):
        """Create AVF interface on VPP node.

        :param node: DUT node from topology.
        :param vf_pci_addr: Virtual Function PCI address.
        :param num_rx_queues: Number of RX queues.
        :type node: dict
        :type vf_pci_addr: str
        :type num_rx_queues: int
        :returns: Interface key (name) in topology.
        :rtype: str
        :raises RuntimeError: If it is not possible to create AVF interface on
            the node.
        """
        num_rx_queues = 'num-rx-queues {num_rx_queues}'\
            .format(num_rx_queues=num_rx_queues) if num_rx_queues else ''

        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template('create_avf_interface.vat',
                                                    vf_pci_addr=vf_pci_addr,
                                                    num_rx_queues=num_rx_queues)
            output = vat.vat_stdout

        if output is not None:
            sw_if_idx = int(output.split()[4])
            InterfaceUtil.add_eth_interface(node, sw_if_idx=sw_if_idx,
                                            ifc_pfx='eth_avf')
            if_key = Topology.get_interface_by_sw_index(node, sw_if_idx)
            return if_key
        else:
            raise RuntimeError('Create AVF interface failed on {host}'.
                               format(host=node['host']))

    @staticmethod
    def vpp_enslave_physical_interface(node, interface, bond_interface):
        """Enslave physical interface to bond interface on VPP node.

        :param node: DUT node from topology.
        :param interface: Physical interface key from topology file.
        :param bond_interface: Load balance
        :type node: dict
        :type interface: str
        :type bond_interface: str
        :raises RuntimeError: If it is not possible to enslave physical
            interface to bond interface on the node.
        """
        ifc = Topology.get_interface_sw_index(node, interface)
        bond_ifc = Topology.get_interface_sw_index(node, bond_interface)

        output = VatExecutor.cmd_from_template(
            node, 'enslave_physical_interface.vat', p_int=ifc, b_int=bond_ifc)

        retval = output[0].get('retval', None)
        if retval is None or int(retval) != 0:
            raise RuntimeError('Enslave physical interface {ifc} to bond '
                               'interface {bond} failed on node "{n}"'
                               .format(ifc=interface, bond=bond_interface,
                                       n=node['host']))

    @staticmethod
    def vpp_show_bond_data_on_node(node, details=False):
        """Show (detailed) bond information on VPP node.

        :param node: DUT node from topology.
        :param details: If detailed information is required or not.
        :type node: dict
        :type details: bool
        """
        cmd = 'exec show bond details' if details else 'exec show bond'
        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd(cmd)

    @staticmethod
    def vpp_show_bond_data_on_all_nodes(nodes, details=False):
        """Show (detailed) bond information on all VPP nodes in DICT__nodes.

        :param nodes: Nodes in the topology.
        :param details: If detailed information is required or not.
        :type nodes: dict
        :type details: bool
        """
        for node_data in nodes.values():
            if node_data['type'] == NodeType.DUT:
                InterfaceUtil.vpp_show_bond_data_on_node(node_data, details)

    @staticmethod
    def vpp_enable_input_acl_interface(node, interface, ip_version,
                                       table_index):
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
        if isinstance(interface, basestring):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        else:
            sw_if_index = interface

        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template("input_acl_int.vat",
                                                    sw_if_index=sw_if_index,
                                                    ip_version=ip_version,
                                                    table_index=table_index)

    @staticmethod
    def get_interface_classify_table(node, interface):
        """Get name of classify table for the given interface.

        :param node: VPP node to get data from.
        :param interface: Name or sw_if_index of a specific interface.
        :type node: dict
        :type interface: str or int
        :returns: Classify table name.
        :rtype: str
        """
        if isinstance(interface, basestring):
            sw_if_index = InterfaceUtil.get_sw_if_index(node, interface)
        else:
            sw_if_index = interface

        with VatTerminal(node) as vat:
            data = vat.vat_terminal_exec_cmd_from_template(
                "classify_interface_table.vat",
                sw_if_index=sw_if_index)
        return data[0]

    @staticmethod
    def get_interface_vrf_table(node, interface):
        """Get vrf ID for the given interface.

        :param node: VPP node.
        :param interface: Name or sw_if_index of a specific interface.
        :type node: dict
        :type interface: str or int
        :returns: vrf ID of the specified interface.
        :rtype: int
        """

        if isinstance(interface, basestring):
            sw_if_index = InterfaceUtil.get_sw_if_index(node, interface)
        else:
            sw_if_index = interface

        with VatTerminal(node) as vat:
            data = vat.vat_terminal_exec_cmd_from_template(
                "interface_vrf_dump.vat",
                sw_if_index=sw_if_index)
        return data[0]["vrf_id"]

    @staticmethod
    def get_sw_if_index(node, interface_name):
        """Get sw_if_index for the given interface from actual interface dump.

        :param node: VPP node to get interface data from.
        :param interface_name: Name of the specific interface.
        :type node: dict
        :type interface_name: str
        :returns: sw_if_index of the given interface.
        :rtype: str
        """

        with VatTerminal(node) as vat:
            if_data = vat.vat_terminal_exec_cmd_from_template(
                "interface_dump.vat")
        for interface in if_data[0]:
            if interface["interface_name"] == interface_name:
                return interface["sw_if_index"]

        return None

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

        with VatTerminal(node) as vat:
            vxlan_gpe_data = vat.vat_terminal_exec_cmd_from_template(
                "vxlan_gpe_dump.vat")

        if interface_name:
            sw_if_index = InterfaceUtil.get_sw_if_index(node, interface_name)
            if sw_if_index:
                for vxlan_gpe in vxlan_gpe_data[0]:
                    if vxlan_gpe["sw_if_index"] == sw_if_index:
                        return vxlan_gpe
            return {}

        return vxlan_gpe_data[0]

    @staticmethod
    def vpp_proxy_arp_interface_enable(node, interface):
        """Enable proxy ARP on interface.

        :param node: VPP node to enable proxy ARP on interface.
        :param interface: Interface to enable proxy ARP.
        :type node: dict
        :type interface: str or int
        """
        if isinstance(interface, basestring):
            sw_if_index = InterfaceUtil.get_sw_if_index(node, interface)
        else:
            sw_if_index = interface

        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template(
                "proxy_arp_intfc_enable.vat",
                sw_if_index=sw_if_index)

    @staticmethod
    def vpp_ip_source_check_setup(node, interface):
        """Setup Reverse Path Forwarding source check on interface.

        :param node: Node to setup RPF source check.
        :param interface: Interface name to setup RPF source check.
        :type node: dict
        :type interface: str
        """
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template("ip_source_check.vat",
                                                    interface_name=interface)

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
        if isinstance(interface, basestring):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        else:
            sw_if_index = interface

        ipv6 = 'ipv6' if ipv6 else ''

        with VatTerminal(node) as vat:
            ret = vat.vat_terminal_exec_cmd_from_template(
                "set_fib_to_interface.vat",
                sw_index=sw_if_index, vrf=table_id, ipv6=ipv6)

        if ret[0]["retval"] != 0:
            raise RuntimeError('Unable to assign interface to FIB node {}.'
                               .format(node))

    @staticmethod
    def set_linux_interface_mac(node, interface, mac, namespace=None,
                                vf_id=None):
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
        mac_str = 'vf {vf_id} mac {mac}'.format(vf_id=vf_id, mac=mac) \
            if vf_id is not None else 'address {mac}'.format(mac=mac)
        ns_str = 'ip netns exec {ns}'.format(ns=namespace) if namespace else ''

        cmd = ('{ns} ip link set {interface} {mac}'.
               format(ns=ns_str, interface=interface, mac=mac_str))
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def set_linux_interface_trust_on(node, interface, namespace=None,
                                     vf_id=None):
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
        trust_str = 'vf {vf_id} trust on'.format(vf_id=vf_id) \
            if vf_id is not None else 'trust on'
        ns_str = 'ip netns exec {ns}'.format(ns=namespace) if namespace else ''

        cmd = ('{ns} ip link set dev {interface} {trust}'.
               format(ns=ns_str, interface=interface, trust=trust_str))
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def set_linux_interface_spoof_off(node, interface, namespace=None,
                                      vf_id=None):
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
        spoof_str = 'vf {vf_id} spoof off'.format(vf_id=vf_id) \
            if vf_id is not None else 'spoof off'
        ns_str = 'ip netns exec {ns}'.format(ns=namespace) if namespace else ''

        cmd = ('{ns} ip link set dev {interface} {spoof}'.
               format(ns=ns_str, interface=interface, spoof=spoof_str))
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def init_avf_interface(node, ifc_key, numvfs=1, topology_type='L2'):
        """Init PCI device by creating VFs and bind them to vfio-pci for AVF
        driver testing on DUT.

        :param node: DUT node.
        :param ifc_key: Interface key from topology file.
        :param numvfs: Number of VFs to initialize, 0 - disable the VFs.
        :param topology_type: Topology type.
        :type node: dict
        :type ifc_key: str
        :type numvfs: int
        :type topology_type: str
        :returns: Virtual Function topology interface keys.
        :rtype: list
        """
        ssh = SSH()
        ssh.connect(node)

        # Read PCI address and driver.
        pf_pci_addr = Topology.get_interface_pci_addr(node, ifc_key)
        pf_mac_addr = Topology.get_interface_mac(node, ifc_key).split(":")
        uio_driver = Topology.get_uio_driver(node)
        kernel_driver = Topology.get_interface_driver(node, ifc_key)
        current_driver = DUTSetup.get_pci_dev_driver(
            node, pf_pci_addr.replace(':', r'\:'))

        VPPUtil.stop_vpp_service(node)
        if current_driver != kernel_driver:
            # PCI device must be re-bound to kernel driver before creating VFs.
            DUTSetup.verify_kernel_module(node, kernel_driver, force_load=True)
            # Stop VPP to prevent deadlock.
            # Unbind from current driver.
            DUTSetup.pci_driver_unbind(node, pf_pci_addr)
            # Bind to kernel driver.
            DUTSetup.pci_driver_bind(node, pf_pci_addr, kernel_driver)

        # Initialize PCI VFs
        DUTSetup.set_sriov_numvfs(node, pf_pci_addr, numvfs)

        vf_ifc_keys = []
        # Set MAC address and bind each virtual function to uio driver.
        for vf_id in range(numvfs):
            vf_mac_addr = ":".join([pf_mac_addr[0], pf_mac_addr[2],
                                    pf_mac_addr[3], pf_mac_addr[4],
                                    pf_mac_addr[5], "{:02x}".format(vf_id)])

            pf_dev = '`basename /sys/bus/pci/devices/{pci}/net/*`'.\
                format(pci=pf_pci_addr)
            InterfaceUtil.set_linux_interface_trust_on(node, pf_dev,
                                                       vf_id=vf_id)
            if topology_type == 'L2':
                InterfaceUtil.set_linux_interface_spoof_off(node, pf_dev,
                                                            vf_id=vf_id)
            InterfaceUtil.set_linux_interface_mac(node, pf_dev, vf_mac_addr,
                                                  vf_id=vf_id)

            DUTSetup.pci_vf_driver_unbind(node, pf_pci_addr, vf_id)
            DUTSetup.pci_vf_driver_bind(node, pf_pci_addr, vf_id, uio_driver)

            # Add newly created ports into topology file
            vf_ifc_name = '{pf_if_key}_vf'.format(pf_if_key=ifc_key)
            vf_pci_addr = DUTSetup.get_virtfn_pci_addr(node, pf_pci_addr, vf_id)
            vf_ifc_key = Topology.add_new_port(node, vf_ifc_name)
            Topology.update_interface_name(node, vf_ifc_key,
                                           vf_ifc_name+str(vf_id+1))
            Topology.update_interface_mac_address(node, vf_ifc_key, vf_mac_addr)
            Topology.update_interface_pci_address(node, vf_ifc_key, vf_pci_addr)
            vf_ifc_keys.append(vf_ifc_key)

        return vf_ifc_keys

    @staticmethod
    def vpp_create_multiple_vxlan_ipv4_tunnels(
            node, node_vxlan_if, node_vlan_if, op_node, op_node_if,
            n_tunnels, vni_start, src_ip_start, dst_ip_start, ip_step, ip_limit,
            bd_id_start):
        """Create multiple VXLAN tunnel interfaces and VLAN sub-interfaces on
        VPP node.

        Put each pair of VXLAN tunnel interface and VLAN sub-interface to
        separate bridge-domain.

        :param node: VPP node to create VXLAN tunnel interfaces.
        :param node_vxlan_if: VPP node interface key to create VXLAN tunnel
            interfaces.
        :param node_vlan_if: VPP node interface key to create VLAN
            sub-interface.
        :param op_node: Opposite VPP node for VXLAN tunnel interfaces.
        :param op_node_if: Opposite VPP node interface key for VXLAN tunnel
            interfaces.
        :param n_tunnels: Number of tunnel interfaces to create.
        :param vni_start: VNI start ID.
        :param src_ip_start: VXLAN tunnel source IP address start.
        :param dst_ip_start: VXLAN tunnel destination IP address start.
        :param ip_step: IP address incremental step.
        :param ip_limit: IP address limit.
        :param bd_id_start: Bridge-domain ID start.
        :type node: dict
        :type node_vxlan_if: str
        :type node_vlan_if: str
        :type op_node: dict
        :type op_node_if: str
        :type n_tunnels: int
        :type vni_start: int
        :type src_ip_start: str
        :type dst_ip_start: str
        :type ip_step: int
        :type ip_limit: str
        :type bd_id_start: int
        """
        # configure IPs, create VXLAN interfaces and VLAN sub-interfaces
        vxlan_count = InterfaceUtil.vpp_create_vxlan_and_vlan_interfaces(
            node, node_vxlan_if, node_vlan_if, n_tunnels, vni_start,
            src_ip_start, dst_ip_start, ip_step, ip_limit)

        # update topology with VXLAN interfaces and VLAN sub-interfaces data
        # and put interfaces up
        InterfaceUtil.vpp_put_vxlan_and_vlan_interfaces_up(
            node, vxlan_count, node_vlan_if)

        # configure bridge domains, ARPs and routes
        InterfaceUtil.vpp_put_vxlan_and_vlan_interfaces_to_bridge_domain(
            node, node_vxlan_if, vxlan_count, op_node, op_node_if, dst_ip_start,
            ip_step, bd_id_start)

    @staticmethod
    def vpp_create_vxlan_and_vlan_interfaces(
            node, node_vxlan_if, node_vlan_if, vxlan_count, vni_start,
            src_ip_start, dst_ip_start, ip_step, ip_limit):
        """
        Configure IPs, create VXLAN interfaces and VLAN sub-interfaces on VPP
        node.

        :param node: VPP node.
        :param node_vxlan_if: VPP node interface key to create VXLAN tunnel
            interfaces.
        :param node_vlan_if: VPP node interface key to create VLAN
            sub-interface.
        :param vxlan_count: Number of tunnel interfaces to create.
        :param vni_start: VNI start ID.
        :param src_ip_start: VXLAN tunnel source IP address start.
        :param dst_ip_start: VXLAN tunnel destination IP address start.
        :param ip_step: IP address incremental step.
        :param ip_limit: IP address limit.
        :type node: dict
        :type node_vxlan_if: str
        :type node_vlan_if: str
        :type vxlan_count: int
        :type vni_start: int
        :type src_ip_start: str
        :type dst_ip_start: str
        :type ip_step: int
        :type ip_limit: str
        :returns: Number of created VXLAN interfaces.
        :rtype: int
        """
        commands = list()

        src_ip_start_int = IPUtil.ip_to_int(src_ip_start)
        dst_ip_start_int = IPUtil.ip_to_int(dst_ip_start)
        ip_limit_int = IPUtil.ip_to_int(ip_limit)

        tmp_fn = '/tmp/create_vxlan_interfaces.config'
        for i in range(0, vxlan_count):
            src_ip_int = src_ip_start_int + i * ip_step
            dst_ip_int = dst_ip_start_int + i * ip_step
            if src_ip_int > ip_limit_int or dst_ip_int > ip_limit_int:
                logger.warn("Can't do more iterations - IPv4 address limit "
                            "has been reached.")
                vxlan_count = i
                break
            src_ip = IPUtil.int_to_ip(src_ip_int)
            dst_ip = IPUtil.int_to_ip(dst_ip_int)
            commands.append(
                'sw_interface_add_del_address sw_if_index {sw_idx} {ip}/32\n'
                .format(sw_idx=Topology.get_interface_sw_index(
                    node, node_vxlan_if), ip=src_ip))
            commands.append(
                'vxlan_add_del_tunnel src {src_ip} dst {dst_ip} vni {vni}\n'
                .format(src_ip=src_ip, dst_ip=dst_ip, vni=vni_start+i))
            commands.append(
                'create_vlan_subif sw_if_index {sw_idx} vlan {vlan}\n'
                .format(sw_idx=Topology.get_interface_sw_index(
                    node, node_vlan_if), vlan=i+1))

        VatExecutor().write_and_execute_script(node, tmp_fn, commands)

        return vxlan_count

    @staticmethod
    def vpp_put_vxlan_and_vlan_interfaces_up(node, vxlan_count, node_vlan_if):
        """
        Update topology with VXLAN interfaces and VLAN sub-interfaces data
        and put interfaces up.

        :param node: VPP node.
        :param vxlan_count: Number of tunnel interfaces.
        :param node_vlan_if: VPP node interface key where VLAN sub-interfaces
            have been created.
        :type node: dict
        :type vxlan_count: int
        :type node_vlan_if: str
        """
        with VatTerminal(node) as vat_ter:
            if_data = vat_ter.vat_terminal_exec_cmd_from_template(
                'interface_dump.vat')[0]

        tmp_fn = '/tmp/put_subinterfaces_up.config'
        commands = list()
        for i in range(0, vxlan_count):
            vxlan_subif_key = Topology.add_new_port(node, 'vxlan_tunnel')
            vxlan_subif_name = 'vxlan_tunnel{nr}'.format(nr=i)
            vxlan_found = False
            vxlan_subif_idx = None
            vlan_subif_key = Topology.add_new_port(node, 'vlan_subif')
            vlan_subif_name = '{if_name}.{vlan}'.format(
                if_name=Topology.get_interface_name(
                    node, node_vlan_if), vlan=i+1)
            vlan_found = False
            vlan_idx = None
            for data in if_data:
                if_name = data['interface_name']
                if not vxlan_found and if_name == vxlan_subif_name:
                    vxlan_subif_idx = data['sw_if_index']
                    vxlan_found = True
                elif not vlan_found and if_name == vlan_subif_name:
                    vlan_idx = data['sw_if_index']
                    vlan_found = True
                if vxlan_found and vlan_found:
                    break
            Topology.update_interface_sw_if_index(
                node, vxlan_subif_key, vxlan_subif_idx)
            Topology.update_interface_name(
                node, vxlan_subif_key, vxlan_subif_name)
            commands.append(
                'sw_interface_set_flags sw_if_index {sw_idx} admin-up link-up\n'
                .format(sw_idx=vxlan_subif_idx))
            Topology.update_interface_sw_if_index(
                node, vlan_subif_key, vlan_idx)
            Topology.update_interface_name(
                node, vlan_subif_key, vlan_subif_name)
            commands.append(
                'sw_interface_set_flags sw_if_index {sw_idx} admin-up link-up\n'
                .format(sw_idx=vlan_idx))

        VatExecutor().write_and_execute_script(node, tmp_fn, commands)

    @staticmethod
    def vpp_put_vxlan_and_vlan_interfaces_to_bridge_domain(
            node, node_vxlan_if, vxlan_count, op_node, op_node_if, dst_ip_start,
            ip_step, bd_id_start):
        """
        Configure ARPs and routes for VXLAN interfaces and put each pair of
        VXLAN tunnel interface and VLAN sub-interface to separate bridge-domain.

        :param node: VPP node.
        :param node_vxlan_if: VPP node interface key where VXLAN tunnel
            interfaces have been created.
        :param vxlan_count: Number of tunnel interfaces.
        :param op_node: Opposite VPP node for VXLAN tunnel interfaces.
        :param op_node_if: Opposite VPP node interface key for VXLAN tunnel
            interfaces.
        :param dst_ip_start: VXLAN tunnel destination IP address start.
        :param ip_step: IP address incremental step.
        :param bd_id_start: Bridge-domain ID start.
        :type node: dict
        :type node_vxlan_if: str
        :type vxlan_count: int
        :type op_node: dict
        :type op_node_if:
        :type dst_ip_start: str
        :type ip_step: int
        :type bd_id_start: int
        """
        sw_idx_vxlan = Topology.get_interface_sw_index(node, node_vxlan_if)

        dst_ip_start_int = IPUtil.ip_to_int(dst_ip_start)

        tmp_fn = '/tmp/configure_routes_and_bridge_domains.config'
        commands = list()
        for i in range(0, vxlan_count):
            dst_ip = IPUtil.int_to_ip(dst_ip_start_int + i * ip_step)
            commands.append(
                'ip_neighbor_add_del sw_if_index {sw_idx} dst {ip} mac {mac}\n'
                .format(sw_idx=sw_idx_vxlan, ip=dst_ip,
                        mac=Topology.get_interface_mac(op_node, op_node_if)))
            commands.append(
                'ip_add_del_route {ip}/32 via {ip} sw_if_index {sw_idx}'
                ' resolve-attempts 10 count 1\n'.format(
                    ip=dst_ip, sw_idx=sw_idx_vxlan))
            bd_id = bd_id_start + i
            subif_id = i + 1
            commands.append(
                'sw_interface_set_l2_bridge sw_if_index {sw_idx} bd_id {bd_id} '
                'shg 0 enable\n'.format(sw_idx=Topology.get_interface_sw_index(
                    node, 'vxlan_tunnel{nr}'.format(nr=subif_id)), bd_id=bd_id))
            commands.append(
                'sw_interface_set_l2_bridge sw_if_index {sw_idx} bd_id {bd_id} '
                'shg 0 enable\n'.format(sw_idx=Topology.get_interface_sw_index(
                    node, 'vlan_subif{nr}'.format(nr=subif_id)), bd_id=bd_id))

        VatExecutor().write_and_execute_script(node, tmp_fn, commands)

    @staticmethod
    def vpp_sw_interface_rx_placement_dump(node):
        """Dump VPP interface RX placement on node.

        :param node: Node to run command on.
        :type node: dict
        :returns: Thread mapping information as a list of dictionaries.
        :rtype: list
        :raises RuntimeError: If failed to run command on host.
        :raises PapiError: If no API reply received.
        """
        api_data = list()
        for ifc in node['interfaces'].values():
            if ifc['vpp_sw_index'] is not None:
                api = dict(api_name='sw_interface_rx_placement_dump')
                api_args = dict(sw_if_index=ifc['vpp_sw_index'])
                api['api_args'] = api_args
                api_data.append(api)

        with PapiExecutor(node) as papi_executor:
            papi_executor.execute_papi(api_data)
            try:
                papi_executor.papi_should_have_passed()
                api_reply = papi_executor.get_papi_reply()
            except AssertionError:
                raise RuntimeError('Failed to run {api_name} on host '
                                   '{host}!'.format(host=node['host'], **api))

        if api_reply:
            thr_mapping = [s['sw_interface_rx_placement_details'] \
                for r in api_reply for s in r['api_reply']]
            return sorted(thr_mapping, key=lambda k: k['sw_if_index'])
        else:
            raise PapiError('No reply received for {api_name} on host {host}!'.
                            format(host=node['host'], **api))

    @staticmethod
    def vpp_sw_interface_set_rx_placement(node, sw_if_index, queue_id,
                                          worker_id):
        """Set interface RX placement to worker on node.

        :param node: Node to run command on.
        :param sw_if_index: VPP SW interface index.
        :param queue_id: VPP interface queue ID.
        :param worker_id: VPP worker ID (indexing from 0).
        :type node: dict
        :type sw_if_index: int
        :type queue_id: int
        :type worker_id: int
        :raises RuntimeError: If failed to run command on host.
        :raises PapiError: If no API reply received.
        """
        api_data = list()
        api = dict(api_name='sw_interface_set_rx_placement')
        api_args = dict(sw_if_index=sw_if_index, queue_id=queue_id,
                        worker_id=worker_id)
        api['api_args'] = api_args
        api_data.append(api)

        with PapiExecutor(node) as papi_executor:
            papi_executor.execute_papi(api_data)
            try:
                papi_executor.papi_should_have_passed()
                api_reply = papi_executor.get_papi_reply()
            except AssertionError:
                raise RuntimeError('Failed to run {api_name} on host '
                                   '{host}!'.format(host=node['host'], **api))

        if not api_reply:
            raise PapiError('No reply received for {api_name} on host {host}!'.
                            format(host=node['host'], **api))

    @staticmethod
    def vpp_round_robin_rx_placement(node, prefix):
        """Set Round Robin interface RX placement on all worker threads
        on node.

        :param node: Topology nodes.
        :param prefix: Interface name prefix.
        :type node: dict
        :type prefix: str
        """
        worker_id = 0
        worker_cnt = len(VPPUtil.vpp_show_threads(node)) - 1
        for placement in InterfaceUtil.vpp_sw_interface_rx_placement_dump(node):
            for interface in node['interfaces'].values():
                if placement['sw_if_index'] == interface['vpp_sw_index'] \
                    and prefix in interface['name']:
                    InterfaceUtil.vpp_sw_interface_set_rx_placement(
                        node, placement['sw_if_index'], placement['queue_id'],
                        worker_id % worker_cnt)
                    worker_id += 1

    @staticmethod
    def vpp_round_robin_rx_placement_on_all_duts(nodes, prefix):
        """Set Round Robin interface RX placement on all worker threads
        on all DUTs.

        :param nodes: Topology nodes.
        :param prefix: Interface name prefix.
        :type nodes: dict
        :type prefix: str
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                InterfaceUtil.vpp_round_robin_rx_placement(node, prefix)
