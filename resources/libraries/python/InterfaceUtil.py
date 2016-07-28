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

"""Interface util library"""

from time import time, sleep

from robot.api import logger

from resources.libraries.python.ssh import SSH
from resources.libraries.python.IPUtil import convert_ipv4_netmask_prefix
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal
from resources.libraries.python.VatJsonUtil import VatJsonUtil
from resources.libraries.python.parsers.JsonParser import JsonParser


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
        :return: nothing
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
                state = 'admin-up'
            elif state == 'down':
                state = 'admin-down'
            else:
                raise ValueError('Unexpected interface state: {}'.format(state))
            VatExecutor.cmd_from_template(node, 'set_if_state.vat',
                                          sw_if_index=sw_if_index, state=state)
        elif node['type'] == NodeType.TG or node['type'] == NodeType.VM:
            cmd = 'ip link set {} {}'.format(iface_name, state)
            exec_cmd_no_error(node, cmd, sudo=True)
        else:
            raise Exception('Node {} has unknown NodeType: "{}"'.
                            format(node['host'], node['type']))

    @staticmethod
    def set_interface_ethernet_mtu(node, iface_key, mtu):
        """Set Ethernet MTU for specified interface.

        Function can be used only for TGs.

        :param node: Node where the interface is.
        :param interface: Interface key from topology file.
        :param mtu: MTU to set.
        :type node: dict
        :type iface_key: str
        :type mtu: int
        :return: nothing
        """
        if node['type'] == NodeType.DUT:
            ValueError('Node {}: Setting Ethernet MTU for interface '
                       'on DUT nodes not supported', node['host'])
        elif node['type'] == NodeType.TG:
            iface_name = Topology.get_interface_name(node, iface_key)
            cmd = 'ip link set {} mtu {}'.format(iface_name, mtu)
            exec_cmd_no_error(node, cmd, sudo=True)
        else:
            raise ValueError('Node {} has unknown NodeType: "{}"'.
                             format(node['host'], node['type']))

    @staticmethod
    def set_default_ethernet_mtu_on_all_interfaces_on_node(node):
        """Set default Ethernet MTU on all interfaces on node.

        Function can be used only for TGs.

        :param node: Node where to set default MTU.
        :type node: dict
        :return: nothing
        """
        for ifc in node['interfaces']:
            InterfaceUtil.set_interface_ethernet_mtu(node, ifc, 1500)

    @staticmethod
    def vpp_node_interfaces_ready_wait(node, timeout=10):
        """Wait until all interfaces with admin-up are in link-up state.

        :param node: Node to wait on.
        :param timeout: Waiting timeout in seconds (optional, default 10s).
        :type node: dict
        :type timeout: int
        :raises: RuntimeError if the timeout period value has elapsed.
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
    def vpp_nodes_interfaces_ready_wait(nodes, timeout=10):
        """Wait until all interfaces with admin-up are in link-up state for
        listed nodes.

        :param nodes: List of nodes to wait on.
        :param timeout: Seconds to wait per node for all interfaces to come up.
        :type nodes: list
        :type timeout: int
        :raises: RuntimeError if the timeout period value has elapsed.
        """
        for node in nodes:
            InterfaceUtil.vpp_node_interfaces_ready_wait(node, timeout)

    @staticmethod
    def all_vpp_interfaces_ready_wait(nodes, timeout=10):
        """Wait until all interfaces with admin-up are in link-up state for all
        nodes in the topology.

        :param nodes: Nodes in the topology.
        :param timeout: Seconds to wait per node for all interfaces to come up.
        :type nodes: dict
        :type timeout: int
        :raises: RuntimeError if the timeout period value has elapsed.
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
        :return: List of dictionaries containing data for each interface, or a
        single dictionary for the specified interface.
        :rtype: list or dict
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
    def vpp_get_interface_ip_addresses(node, interface, ip_version):
        """Get list of IP addresses from an interface on a VPP node.

         :param node: VPP node to get data from.
         :param interface: Name of an interface on the VPP node.
         :param ip_version: IP protocol version (ipv4 or ipv6).
         :type node: dict
         :type interface: str
         :type ip_version: str
         :return: List of dictionaries, each containing IP address, subnet
         prefix length and also the subnet mask for ipv4 addresses.
         Note: A single interface may have multiple IP addresses assigned.
         :rtype: list
        """
        sw_if_index = InterfaceUtil.get_sw_if_index(node, interface)

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
        """
        old_driver = InterfaceUtil.tg_get_interface_driver(node, pci_addr)
        if old_driver == driver:
            return

        ssh = SSH()
        ssh.connect(node)

        # Unbind from current driver
        if old_driver is not None:
            cmd = 'sh -c "echo {0} > /sys/bus/pci/drivers/{1}/unbind"'.format(
                pci_addr, old_driver)
            (ret_code, _, _) = ssh.exec_command_sudo(cmd)
            if int(ret_code) != 0:
                raise Exception("'{0}' failed on '{1}'".format(cmd,
                                                               node['host']))

        # Bind to the new driver
        cmd = 'sh -c "echo {0} > /sys/bus/pci/drivers/{1}/bind"'.format(
            pci_addr, driver)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise Exception("'{0}' failed on '{1}'".format(cmd, node['host']))

    @staticmethod
    def tg_get_interface_driver(node, pci_addr):
        """Get interface driver from the TG node.

        :param node: Node to get interface driver on (must be TG node).
        :param pci_addr: PCI address of the interface.
        :type node: dict
        :type pci_addr: str
        :return: Interface driver or None if not found.
        :rtype: str

        .. note::
            # lspci -vmmks 0000:00:05.0
            Slot:   00:05.0
            Class:  Ethernet controller
            Vendor: Red Hat, Inc
            Device: Virtio network device
            SVendor:        Red Hat, Inc
            SDevice:        Device 0001
            PhySlot:        5
            Driver: virtio-pci
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = 'lspci -vmmks {0}'.format(pci_addr)

        (ret_code, stdout, _) = ssh.exec_command(cmd)
        if int(ret_code) != 0:
            raise Exception("'{0}' failed on '{1}'".format(cmd, node['host']))

        for line in stdout.splitlines():
            if len(line) == 0:
                continue
            (name, value) = line.split("\t", 1)
            if name == 'Driver:':
                return value

        return None

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
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = 'rm -f {0}'.format(InterfaceUtil.__UDEV_IF_RULES_FILE)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise Exception("'{0}' failed on '{1}'".format(cmd, node['host']))

        for interface in node['interfaces'].values():
            rule = 'SUBSYSTEM==\\"net\\", ACTION==\\"add\\", ATTR{address}' + \
                   '==\\"' + interface['mac_address'] + '\\", NAME=\\"' + \
                   interface['name'] + '\\"'
            cmd = 'sh -c "echo \'{0}\' >> {1}"'.format(
                rule, InterfaceUtil.__UDEV_IF_RULES_FILE)
            (ret_code, _, _) = ssh.exec_command_sudo(cmd)
            if int(ret_code) != 0:
                raise Exception("'{0}' failed on '{1}'".format(cmd,
                                                               node['host']))

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
    def update_tg_interface_data_on_node(node):
        """Update interface name for TG/linux node in DICT__nodes.

        :param node: Node selected from DICT__nodes.
        :type node: dict

        .. note::
            # for dev in `ls /sys/class/net/`;
            > do echo "\"`cat /sys/class/net/$dev/address`\": \"$dev\""; done
            "52:54:00:9f:82:63": "eth0"
            "52:54:00:77:ae:a9": "eth1"
            "52:54:00:e1:8a:0f": "eth2"
            "00:00:00:00:00:00": "lo"

        .. todo:: parse lshw -json instead
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
            raise Exception('Get interface name and MAC failed')
        tmp = "{" + stdout.rstrip().replace('\n', ',') + "}"
        interfaces = JsonParser().parse_data(tmp)
        for interface in node['interfaces'].values():
            name = interfaces.get(interface['mac_address'])
            if name is None:
                continue
            interface['name'] = name

        # Set udev rules for interfaces
        InterfaceUtil.tg_set_interfaces_udev_rules(node)

    @staticmethod
    def update_all_interface_data_on_all_nodes(nodes, skip_tg=False):
        """Update interface names on all nodes in DICT__nodes.

        This method updates the topology dictionary by querying interface lists
        of all nodes mentioned in the topology dictionary.

        :param nodes: Nodes in the topology.
        :param skip_tg: Skip TG node
        :type nodes: dict
        :type skip_tg: bool
        """
        for node_data in nodes.values():
            if node_data['type'] == NodeType.DUT:
                InterfaceUtil.update_vpp_interface_data_on_node(node_data)
            elif node_data['type'] == NodeType.TG and not skip_tg:
                InterfaceUtil.update_tg_interface_data_on_node(node_data)

    @staticmethod
    def create_vlan_subinterface(node, interface, vlan):
        """Create VLAN subinterface on node.

        :param node: Node to add VLAN subinterface on.
        :param interface: Interface name on which create VLAN subinterface.
        :param vlan: VLAN ID of the subinterface to be created.
        :type node: dict
        :type interface: str
        :type vlan: int
        :return: Name and index of created subinterface.
        :rtype: tuple
        """
        iface_key = Topology.get_interface_by_name(node, interface)
        sw_if_index = Topology.get_interface_sw_index(node, iface_key)

        output = VatExecutor.cmd_from_template(node, "create_vlan_subif.vat",
                                               sw_if_index=sw_if_index,
                                               vlan=vlan)
        if output[0]["retval"] == 0:
            sw_subif_index = output[0]["sw_if_index"]
            logger.trace('VLAN subinterface with sw_if_index {} and VLAN ID {} '
                         'created on node {}'.format(sw_subif_index,
                                                     vlan, node['host']))
        else:
            raise RuntimeError('Unable to create VLAN subinterface on node {}'
                               .format(node['host']))

        with VatTerminal(node, False) as vat:
            vat.vat_terminal_exec_cmd('exec show interfaces')

        return '{}.{}'.format(interface, vlan), sw_subif_index

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
        :return: SW IF INDEX of created interface.
        :rtype: int
        """
        output = VatExecutor.cmd_from_template(node, "vxlan_create.vat",
                                               src=source_ip,
                                               dst=destination_ip,
                                               vni=vni)
        output = output[0]

        if output["retval"] == 0:
            return output["sw_if_index"]
        else:
            raise RuntimeError('Unable to create VXLAN interface on node {0}'
                               .format(node))

    @staticmethod
    def vxlan_dump(node, interface=None):
        """Get VxLAN data for the given interface.

        :param node: VPP node to get interface data from.
        :param interface: Numeric index or name string of a specific interface.
        If None, information about all VxLAN interfaces is returned.
        :type node: dict
        :type interface: int or str
        :return: Dictionary containing data for the given VxLAN interface or if
        interface=None, the list of dictionaries with all VxLAN interfaces.
        :rtype: dict or list
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
            raise Exception("Wrong interface format {0}".format(interface))

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
        :return: List of dictionaries with all vhost-user interfaces.
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
        :return: Dictionary of information about a specific TAP interface, or
        a List of dictionaries containing all TAP data for the given node.
        :rtype: dict or list
        """
        with VatTerminal(node) as vat:
            response = vat.vat_terminal_exec_cmd_from_template(
                "tap_dump.vat")
        if name is None:
            return response[0]
        else:
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
        VPP: [no_tags] [one_tag] [two_tags] [dot1ad] [exact_match] [default_sub]
        :type node: dict
        :type interface: str or int
        :type sub_id: int
        :type outer_vlan_id: int
        :type inner_vlan_id: int
        :type type_subif: str
        :return: Name and index of created sub-interface.
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
            sw_subif_index = output[0]["sw_if_index"]
            logger.trace('Created subinterface with index {}'
                         .format(sw_subif_index))
        else:
            raise RuntimeError('Unable to create sub-interface on node {}'
                               .format(node['host']))

        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd('exec show interfaces')

        name = '{}.{}'.format(interface, sub_id)
        return name, sw_subif_index

    @staticmethod
    def create_gre_tunnel_interface(node, source_ip, destination_ip):
        """Create GRE tunnel interface on node.

        :param node: VPP node to add tunnel interface.
        :param source_ip: Source of the GRE tunnel.
        :param destination_ip: Destination of the GRE tunnel.
        :type node: dict
        :type source_ip: str
        :type destination_ip: str
        :return: Name and index of created GRE tunnel interface.
        :rtype: tuple
        :raises RuntimeError: If unable to create GRE tunnel interface.
        """
        output = VatExecutor.cmd_from_template(node, "create_gre.vat",
                                               src=source_ip,
                                               dst=destination_ip)
        output = output[0]

        if output["retval"] == 0:
            sw_if_index = output["sw_if_index"]

            vat_executor = VatExecutor()
            vat_executor.execute_script_json_out("dump_interfaces.vat", node)
            interface_dump_json = vat_executor.get_script_stdout()
            name = VatJsonUtil.get_interface_name_from_json(
                interface_dump_json, sw_if_index)
            return name, sw_if_index
        else:
            raise RuntimeError('Unable to create GRE tunnel on node {}.'
                               .format(node))

    @staticmethod
    def vpp_create_loopback(node):
        """Create loopback interface on VPP node.

        :param node: Node to create loopback interface on.
        :type node: dict
        :return: SW interface index.
        :rtype: int
        """
        out = VatExecutor.cmd_from_template(node, "create_loopback.vat")
        if out[0].get('retval') == 0:
            return out[0].get('sw_if_index')
        else:
            raise RuntimeError('Create loopback failed on node "{}"'
                               .format(node['host']))

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
        :return: Classify table name.
        :rtype: str
        """
        if isinstance(interface, basestring):
            sw_if_index = InterfaceUtil.get_sw_if_index(node, interface)
        else:
            sw_if_index = interface

        with VatTerminal(node) as vat:
            data = vat.vat_terminal_exec_cmd_from_template(
                "classify_interface_table.vat",
                sw_if_index=sw_if_index
            )
        return data[0]

    @staticmethod
    def get_sw_if_index(node, interface_name):
        """Get sw_if_index for the given interface from actual interface dump.

        :param node: VPP node to get interface data from.
        :param interface_name: Name of the specific interface.
        :type node: dict
        :type interface_name: str
        :return: sw_if_index of the given interface.
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
        :return: Dictionary containing data for the given VxLAN GPE interface or
        if interface=None, the list of dictionaries with all VxLAN GPE
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
            vat.vat_terminal_exec_cmd_from_template("set_fib_to_interface.vat",
                                                    sw_index=sw_if_index,
                                                    vrf=table_id,
                                                    ipv6=ipv6)

    @staticmethod
    def set_linux_interface_mac(node, interface, mac, namespace=None):
        """Set MAC address for interface in linux.

        :param node: Node where to execute command.
        :param interface: Interface in namespace.
        :param mac: MAC to be assigned to interface.
        :param namespace: Execute command in namespace. Optional
        :type node: dict
        :type interface: str
        :type mac: str
        :type namespace: str
        """
        if namespace is not None:
            cmd = 'ip netns exec {} ip link set {} address {}'.format(
                namespace, interface, mac)
        else:
            cmd = 'ip link set {} address {}'.format(interface, mac)
        exec_cmd_no_error(node, cmd, sudo=True)
