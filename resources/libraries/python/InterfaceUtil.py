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
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal
from resources.libraries.python.VatJsonUtil import VatJsonUtil
from resources.libraries.python.parsers.JsonParser import JsonParser


class InterfaceUtil(object):
    """General utilities for managing interfaces"""

    __UDEV_IF_RULES_FILE = '/etc/udev/rules.d/10-network.rules'

    @staticmethod
    def set_interface_state(node, interface, state):
        """Set interface state on a node.

        Function can be used for DUTs as well as for TGs.

        :param node: node where the interface is
        :param interface: interface name or sw_if_index
        :param state: one of 'up' or 'down'
        :type node: dict
        :type interface: str or int
        :type state: str
        :return: nothing
        """
        if node['type'] == NodeType.DUT:
            if state == 'up':
                state = 'admin-up'
            elif state == 'down':
                state = 'admin-down'
            else:
                raise ValueError('Unexpected interface state: {}'.format(state))

            if isinstance(interface, basestring):
                sw_if_index = Topology.get_interface_sw_index(node, interface)
            else:
                sw_if_index = interface

            VatExecutor.cmd_from_template(node, 'set_if_state.vat',
                                          sw_if_index=sw_if_index, state=state)

        elif node['type'] == NodeType.TG or node['type'] == NodeType.VM:
            cmd = 'ip link set {} {}'.format(interface, state)
            exec_cmd_no_error(node, cmd, sudo=True)
        else:
            raise Exception('Node {} has unknown NodeType: "{}"'.
                            format(node['host'], node['type']))

    @staticmethod
    def set_interface_ethernet_mtu(node, interface, mtu):
        """Set Ethernet MTU for specified interface.

        Function can be used only for TGs.

        :param node: node where the interface is
        :param interface: interface name
        :param mtu: MTU to set
        :type node: dict
        :type interface: str
        :type mtu: int
        :return: nothing
        """
        if node['type'] == NodeType.DUT:
            ValueError('Node {}: Setting Ethernet MTU for interface '
                       'on DUT nodes not supported', node['host'])
        elif node['type'] == NodeType.TG:
            cmd = 'ip link set {} mtu {}'.format(interface, mtu)
            exec_cmd_no_error(node, cmd, sudo=True)
        else:
            raise ValueError('Node {} has unknown NodeType: "{}"'.
                             format(node['host'], node['type']))

    @staticmethod
    def set_default_ethernet_mtu_on_all_interfaces_on_node(node):
        """Set default Ethernet MTU on all interfaces on node.

        Function can be used only for TGs.

        :param node: node where to set default MTU
        :type node: dict
        :return: nothing
        """
        for ifc in node['interfaces'].values():
            InterfaceUtil.set_interface_ethernet_mtu(node, ifc['name'], 1500)

    @staticmethod
    def vpp_node_interfaces_ready_wait(node, timeout=10):
        """Wait until all interfaces with admin-up are in link-up state.

        :param node: Node to wait on.
        :param timeout: Waiting timeout in seconds (optional, default 10s)
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
                sw_if_index = Topology.get_interface_sw_index(node, interface)
            else:
                sw_if_index = interface

            for data_if in data:
                if data_if["sw_if_index"] == sw_if_index:

                    return data_if

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
        """Update vpp generated interface data for a given node in DICT__nodes

        Updates interface names, software if index numbers and any other details
        generated specifically by vpp that are unknown before testcase run.
        It does this by dumping interface list to JSON output from all
        devices using vpp_api_test, and pairing known information from topology
        (mac address/pci address of interface) to state from VPP.

        :param node: Node selected from DICT__nodes
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
    def update_all_interface_data_on_all_nodes(nodes):
        """Update interface names on all nodes in DICT__nodes.

        This method updates the topology dictionary by querying interface lists
        of all nodes mentioned in the topology dictionary.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node_data in nodes.values():
            if node_data['type'] == NodeType.DUT:
                InterfaceUtil.update_vpp_interface_data_on_node(node_data)
            elif node_data['type'] == NodeType.TG:
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
        sw_if_index = Topology.get_interface_sw_index(node, interface)

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
            raise RuntimeError('Unable to create VXLAN interface on node {}'
                               .format(node))
