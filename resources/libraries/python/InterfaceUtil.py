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

"""Interface util library."""

from time import sleep

from enum import IntEnum
from ipaddress import ip_address
from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.L2Util import L2Util
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.parsers.JsonParser import JsonParser
from resources.libraries.python.ssh import SSH, exec_cmd_no_error, exec_cmd
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.VPPUtil import VPPUtil


class InterfaceStatusFlags(IntEnum):
    """Interface status falgs."""
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


# pylint: disable=invalid-name
class LinkBondLoadBalance(IntEnum):
    """Link bonding load balance."""
    L2 = 0  # pylint: disable=invalid-name
    L34 = 1
    L23 = 2


class LinkBondMode(IntEnum):
    """Link bonding load balance."""
    ROUND_ROBIN = 1
    ACTIVE_BACKUP = 2
    XOR = 3
    BROADCAST = 4
    LACP = 5


class InterfaceUtil(object):
    """General utilities for managing interfaces"""

    __UDEV_IF_RULES_FILE = '/etc/udev/rules.d/10-network.rules'

    @staticmethod
    def pci_to_int(pci_str):
        """Convert PCI address from string format (0000:18:0a.0) to
        integer representation (169345024).

        :param pci_str: PCI address in string representation.
        :type pci_str: str
        :returns: Integer representation of PCI address.
        :rtype: int
        """
        pci = list(pci_str.split(':')[0:2])
        pci.extend(pci_str.split(':')[2].split('.'))

        return (int(pci[0], 16) | int(pci[1], 16) << 16 |
                int(pci[2], 16) << 24 | int(pci[3], 16) << 29)

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
            raise TypeError('Wrong interface format {ifc}: {err}'.format(
                ifc=interface, err=err.message))

        return sw_if_index

    @staticmethod
    def set_interface_state(node, interface, state, if_type='key'):
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
        if if_type == 'key':
            if isinstance(interface, basestring):
                sw_if_index = Topology.get_interface_sw_index(node, interface)
                iface_name = Topology.get_interface_name(node, interface)
            else:
                sw_if_index = interface
        elif if_type == 'name':
            iface_key = Topology.get_interface_by_name(node, interface)
            if iface_key is not None:
                sw_if_index = Topology.get_interface_sw_index(node, iface_key)
            iface_name = interface
        else:
            raise ValueError('Unknown if_type: {type}'.format(type=if_type))

        if node['type'] == NodeType.DUT:
            if state == 'up':
                flags = InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value
            elif state == 'down':
                flags = 0
            else:
                raise ValueError('Unexpected interface state: {state}'.format(
                    state=state))
            cmd = 'sw_interface_set_flags'
            err_msg = 'Failed to set interface state on host {host}'.format(
                host=node['host'])
            args = dict(
                sw_if_index=sw_if_index,
                flags=flags)
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
        elif node['type'] == NodeType.TG or node['type'] == NodeType.VM:
            cmd = 'ip link set {ifc} {state}'.format(
                ifc=iface_name, state=state)
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

        cmd = 'hw_interface_set_mtu'
        err_msg = 'Failed to set interface MTU on host {host}'.format(
            host=node['host'])
        args = dict(sw_if_index=sw_if_index,
                    mtu=int(mtu))
        try:
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
        except AssertionError as err:
            # TODO: Make failure tolerance optional.
            logger.debug("Setting MTU failed. Expected?\n{err}".format(
                err=err))

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
        for _ in xrange(0, retries):
            not_ready = list()
            out = InterfaceUtil.vpp_get_interface_data(node)
            for interface in out:
                if interface.get('flags') == 1:
                    not_ready.append(interface.get('interface_name'))
            if not not_ready:
                break
            else:
                logger.debug('Interfaces still not in link-up state:\n{ifs} '
                             '\nWaiting...'.format(ifs=not_ready))
                sleep(1)
        else:
            err = 'Timeout, interfaces not up:\n{ifs}'.format(ifs=not_ready) \
                if 'not_ready' in locals() else 'No check executed!'
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
            if node['type'] == NodeType.DUT:
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
            if_dump['l2_address'] = str(if_dump['l2_address'])
            if_dump['b_dmac'] = str(if_dump['b_dmac'])
            if_dump['b_smac'] = str(if_dump['b_smac'])
            if_dump['flags'] = if_dump['flags'].value
            if_dump['type'] = if_dump['type'].value
            if_dump['link_duplex'] = if_dump['link_duplex'].value
            if_dump['sub_if_flags'] = if_dump['sub_if_flags'].value \
                if hasattr(if_dump['sub_if_flags'], 'value') \
                else int(if_dump['sub_if_flags'])

            return if_dump

        if interface is not None:
            if isinstance(interface, basestring):
                param = 'interface_name'
            elif isinstance(interface, int):
                param = 'sw_if_index'
            else:
                raise TypeError('Wrong interface format {ifc}'.format(
                    ifc=interface))
        else:
            param = ''

        cmd = 'sw_interface_dump'
        args = dict(
            name_filter_valid=False,
            name_filter=''
        )
        err_msg = 'Failed to get interface dump on host {host}'.format(
            host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, **args).get_details(err_msg)
        logger.debug('Received data:\n{d!r}'.format(d=details))

        data = list() if interface is None else dict()
        for dump in details:
            if interface is None:
                data.append(process_if_dump(dump))
            elif str(dump.get(param)).rstrip('\x00') == str(interface):
                data = process_if_dump(dump)
                break

        logger.debug('Interface data:\n{if_data}'.format(if_data=data))
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

        return if_data.get('interface_name')

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

        return if_data.get('sw_if_index')

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
        if if_data['sup_sw_if_index'] != if_data['sw_if_index']:
            if_data = InterfaceUtil.vpp_get_interface_data(
                node, if_data['sup_sw_if_index'])

        return if_data.get('l2_address')

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
        It does this by dumping interface list from all devices using python
        api, and pairing known information from topology (mac address) to state
        from VPP.

        :param node: Node selected from DICT__nodes.
        :type node: dict
        """
        interface_list = InterfaceUtil.vpp_get_interface_data(node)
        interface_dict = dict()
        for ifc in interface_list:
            interface_dict[ifc['l2_address']] = ifc

        for if_name, if_data in node['interfaces'].items():
            ifc_dict = interface_dict.get(if_data['mac_address'])
            if ifc_dict is not None:
                if_data['name'] = ifc_dict['interface_name']
                if_data['vpp_sw_index'] = ifc_dict['sw_if_index']
                if_data['mtu'] = ifc_dict['mtu'][0]
                logger.trace('Interface {ifc} found by MAC {mac}'.format(
                    ifc=if_name, mac=if_data['mac_address']))
            else:
                logger.trace('Interface {ifc} not found by MAC {mac}'.format(
                    ifc=if_name, mac=if_data['mac_address']))
                if_data['vpp_sw_index'] = None

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

        cmd = 'create_vlan_subif'
        args = dict(
            sw_if_index=sw_if_index,
            vlan_id=int(vlan)
        )
        err_msg = 'Failed to create VLAN sub-interface on host {host}'.format(
            host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        if_key = Topology.add_new_port(node, 'vlan_subif')
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)
        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)

        return '{ifc}.{vlan}'.format(ifc=interface, vlan=vlan), sw_if_index

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
        src_address = ip_address(unicode(source_ip))
        dst_address = ip_address(unicode(destination_ip))

        cmd = 'vxlan_add_del_tunnel'
        args = dict(is_add=1,
                    is_ipv6=1 if src_address.version == 6 else 0,
                    instance=Constants.BITWISE_NON_ZERO,
                    src_address=src_address.packed,
                    dst_address=dst_address.packed,
                    mcast_sw_if_index=Constants.BITWISE_NON_ZERO,
                    encap_vrf_id=0,
                    decap_next_index=Constants.BITWISE_NON_ZERO,
                    vni=int(vni))
        err_msg = 'Failed to create VXLAN tunnel interface on host {host}'.\
            format(host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        if_key = Topology.add_new_port(node, 'vxlan_tunnel')
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

        cmd = 'sw_interface_set_vxlan_bypass'
        args = dict(is_ipv6=0,
                    sw_if_index=sw_if_index,
                    enable=1)
        err_msg = 'Failed to set VXLAN bypass on interface on host {host}'.\
            format(host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_replies(err_msg)

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
            if vxlan_dump['is_ipv6']:
                vxlan_dump['src_address'] = \
                    ip_address(unicode(vxlan_dump['src_address']))
                vxlan_dump['dst_address'] = \
                    ip_address(unicode(vxlan_dump['dst_address']))
            else:
                vxlan_dump['src_address'] = \
                    ip_address(unicode(vxlan_dump['src_address'][0:4]))
                vxlan_dump['dst_address'] = \
                    ip_address(unicode(vxlan_dump['dst_address'][0:4]))
            return vxlan_dump

        if interface is not None:
            sw_if_index = InterfaceUtil.get_interface_index(node, interface)
        else:
            sw_if_index = int(Constants.BITWISE_NON_ZERO)

        cmd = 'vxlan_tunnel_dump'
        args = dict(sw_if_index=sw_if_index)
        err_msg = 'Failed to get VXLAN dump on host {host}'.format(
            host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, **args).get_details(err_msg)

        data = list() if interface is None else dict()
        for dump in details:
            if interface is None:
                data.append(process_vxlan_dump(dump))
            elif dump['sw_if_index'] == sw_if_index:
                data = process_vxlan_dump(dump)
                break

        logger.debug('VXLAN data:\n{vxlan_data}'.format(vxlan_data=data))
        return data

    @staticmethod
    def vhost_user_dump(node):
        """Get vhost-user data for the given node.

        TODO: Move to VhostUser.py

        :param node: VPP node to get interface data from.
        :type node: dict
        :returns: List of dictionaries with all vhost-user interfaces.
        :rtype: list
        """
        def process_vhost_dump(vhost_dump):
            """Process vhost dump.

            :param vhost_dump: Vhost interface dump.
            :type vhost_dump: dict
            :returns: Processed vhost interface dump.
            :rtype: dict
            """
            vhost_dump['interface_name'] = \
                vhost_dump['interface_name'].rstrip('\x00')
            vhost_dump['sock_filename'] = \
                vhost_dump['sock_filename'].rstrip('\x00')
            return vhost_dump

        cmd = 'sw_interface_vhost_user_dump'
        err_msg = 'Failed to get vhost-user dump on host {host}'.format(
            host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd).get_details(err_msg)

        for dump in details:
            # In-place edits.
            process_vhost_dump(dump)

        logger.debug('Vhost-user details:\n{vhost_details}'.format(
            vhost_details=details))
        return details

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
        subif_types = type_subif.split()

        flags = 0
        if 'no_tags' in subif_types:
            flags = flags | SubInterfaceFlags.SUB_IF_API_FLAG_NO_TAGS
        if 'one_tag' in subif_types:
            flags = flags | SubInterfaceFlags.SUB_IF_API_FLAG_ONE_TAG
        if 'two_tags' in subif_types:
            flags = flags | SubInterfaceFlags.SUB_IF_API_FLAG_TWO_TAGS
        if 'dot1ad' in subif_types:
            flags = flags | SubInterfaceFlags.SUB_IF_API_FLAG_DOT1AD
        if 'exact_match' in subif_types:
            flags = flags | SubInterfaceFlags.SUB_IF_API_FLAG_EXACT_MATCH
        if 'default_sub' in subif_types:
            flags = flags | SubInterfaceFlags.SUB_IF_API_FLAG_DEFAULT
        if type_subif == 'default_sub':
            flags = flags | SubInterfaceFlags.SUB_IF_API_FLAG_INNER_VLAN_ID_ANY\
                    | SubInterfaceFlags.SUB_IF_API_FLAG_OUTER_VLAN_ID_ANY

        cmd = 'create_subif'
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            sub_id=int(sub_id),
            sub_if_flags=flags.value if hasattr(flags, 'value') else int(flags),
            outer_vlan_id=int(outer_vlan_id) if outer_vlan_id else 0,
            inner_vlan_id=int(inner_vlan_id) if inner_vlan_id else 0
        )
        err_msg = 'Failed to create sub-interface on host {host}'.format(
            host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        if_key = Topology.add_new_port(node, 'subinterface')
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)
        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)

        return '{ifc}.{s_id}'.format(ifc=interface, s_id=sub_id), sw_if_index

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
        cmd = 'gre_tunnel_add_del'
        tunnel = dict(type=0,
                      instance=Constants.BITWISE_NON_ZERO,
                      src=str(source_ip),
                      dst=str(destination_ip),
                      outer_fib_id=0,
                      session_id=0)
        args = dict(is_add=1,
                    tunnel=tunnel)
        err_msg = 'Failed to create GRE tunnel interface on host {host}'.format(
            host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        if_key = Topology.add_new_port(node, 'gre_tunnel')
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)
        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)

        return ifc_name, sw_if_index

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
        cmd = 'create_loopback'
        args = dict(mac_address=L2Util.mac_to_bin(mac) if mac else 0)
        err_msg = 'Failed to create loopback interface on host {host}'.format(
            host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        if_key = Topology.add_new_port(node, 'loopback')
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)
        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)
        if mac:
            mac = InterfaceUtil.vpp_get_interface_mac(node, ifc_name)
            Topology.update_interface_mac_address(node, if_key, mac)

        return sw_if_index

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
        cmd = 'bond_create'
        args = dict(id=int(Constants.BITWISE_NON_ZERO),
                    use_custom_mac=0 if mac is None else 1,
                    mac_address=0 if mac is None else L2Util.mac_to_bin(mac),
                    mode=getattr(LinkBondMode, '{md}'.format(
                        md=mode.replace('-', '_').upper())).value,
                    lb=0 if load_balance is None else getattr(
                        LinkBondLoadBalance, '{lb}'.format(
                            lb=load_balance.upper())).value)
        err_msg = 'Failed to create bond interface on host {host}'.format(
            host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        InterfaceUtil.add_eth_interface(node, sw_if_index=sw_if_index,
                                        ifc_pfx='eth_bond')
        if_key = Topology.get_interface_by_sw_index(node, sw_if_index)

        return if_key

    @staticmethod
    def add_eth_interface(node, ifc_name=None, sw_if_index=None, ifc_pfx=None):
        """Add ethernet interface to current topology.

        :param node: DUT node from topology.
        :param ifc_name: Name of the interface.
        :param sw_if_index: SW interface index.
        :param ifc_pfx: Interface key prefix.
        :type node: dict
        :type ifc_name: str
        :type sw_if_index: int
        :type ifc_pfx: str
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
        cmd = 'avf_create'
        args = dict(pci_addr=InterfaceUtil.pci_to_int(vf_pci_addr),
                    enable_elog=0,
                    rxq_num=int(num_rx_queues) if num_rx_queues else 0,
                    rxq_size=0,
                    txq_size=0)
        err_msg = 'Failed to create AVF interface on host {host}'.format(
            host=node['host'])
        try:
            with PapiSocketExecutor(node) as papi_exec:
                sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)
        except AssertionError:
            exec_cmd(node, 'dmesg', sudo=True)

        InterfaceUtil.add_eth_interface(node, sw_if_index=sw_if_index,
                                        ifc_pfx='eth_avf')
        if_key = Topology.get_interface_by_sw_index(node, sw_if_index)

        return if_key

    @staticmethod
    def vpp_enslave_physical_interface(node, interface, bond_if):
        """Enslave physical interface to bond interface on VPP node.

        :param node: DUT node from topology.
        :param interface: Physical interface key from topology file.
        :param bond_if: Load balance
        :type node: dict
        :type interface: str
        :type bond_if: str
        :raises RuntimeError: If it is not possible to enslave physical
            interface to bond interface on the node.
        """
        cmd = 'bond_enslave'
        args = dict(
            sw_if_index=Topology.get_interface_sw_index(node, interface),
            bond_sw_if_index=Topology.get_interface_sw_index(node, bond_if),
            is_passive=0,
            is_long_timeout=0)
        err_msg = 'Failed to enslave physical interface {ifc} to bond ' \
                  'interface {bond} on host {host}'.format(ifc=interface,
                                                           bond=bond_if,
                                                           host=node['host'])
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
        cmd = 'sw_interface_bond_dump'
        err_msg = 'Failed to get bond interface dump on host {host}'.format(
            host=node['host'])

        data = ('Bond data on node {host}:\n'.format(host=node['host']))
        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd).get_details(err_msg)

        for bond in details:
            data += ('{b}\n'.format(b=bond['interface_name'].rstrip('\x00')))
            data += ('  mode: {m}\n'.format(m=bond['mode']).lower())
            data += ('  load balance: {lb}\n'.format(lb=bond['lb']).lower())
            data += ('  number of active slaves: {n}\n'.format(
                n=bond['active_slaves']))
            if verbose:
                slave_data = InterfaceUtil.vpp_bond_slave_dump(
                    node, Topology.get_interface_by_sw_index(
                        node, bond['sw_if_index']))
                for slave in slave_data:
                    if not slave['is_passive']:
                        data += ('    {s}\n'.format(s=slave['interface_name']))
            data += ('  number of slaves: {n}\n'.format(n=bond['slaves']))
            if verbose:
                for slave in slave_data:
                    data += ('    {s}\n'.format(s=slave['interface_name']))
            data += ('  interface id: {i}\n'.format(i=bond['id']))
            data += ('  sw_if_index: {i}\n'.format(i=bond['sw_if_index']))
        logger.info(data)

    @staticmethod
    def vpp_bond_slave_dump(node, interface):
        """Get bond interface slave(s) data on VPP node.

        :param node: DUT node from topology.
        :param interface: Physical interface key from topology file.
        :type node: dict
        :type interface: str
        :returns: Bond slave interface data.
        :rtype: dict
        """
        def process_slave_dump(slave_dump):
            """Process slave dump.

            :param slave_dump: Slave interface dump.
            :type slave_dump: dict
            :returns: Processed slave interface dump.
            :rtype: dict
            """
            slave_dump['interface_name'] = slave_dump['interface_name'].\
                rstrip('\x00')
            return slave_dump

        cmd = 'sw_interface_slave_dump'
        args = dict(sw_if_index=Topology.get_interface_sw_index(
            node, interface))
        err_msg = 'Failed to get slave dump on host {host}'.format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, **args).get_details(err_msg)

        for dump in details:
            # In-place edits.
            process_slave_dump(dump)

        logger.debug('Slave data:\n{slave_data}'.format(slave_data=details))
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
            if node_data['type'] == NodeType.DUT:
                InterfaceUtil.vpp_show_bond_data_on_node(node_data, verbose)

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
        cmd = 'input_acl_set_interface'
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            ip4_table_index=table_index if ip_version == 'ip4'
            else Constants.BITWISE_NON_ZERO,
            ip6_table_index=table_index if ip_version == 'ip6'
            else Constants.BITWISE_NON_ZERO,
            l2_table_index=table_index if ip_version == 'l2'
            else Constants.BITWISE_NON_ZERO,
            is_add=1)
        err_msg = 'Failed to enable input acl on interface {ifc}'.format(
            ifc=interface)
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
        if isinstance(interface, basestring):
            sw_if_index = InterfaceUtil.get_sw_if_index(node, interface)
        else:
            sw_if_index = interface

        cmd = 'classify_table_by_interface'
        args = dict(sw_if_index=sw_if_index)
        err_msg = 'Failed to get classify table name by interface {ifc}'.format(
            ifc=interface)
        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        return reply

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
        interface_data = InterfaceUtil.vpp_get_interface_data(
            node, interface=interface_name)
        return interface_data.get('sw_if_index')

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
            if vxlan_dump['is_ipv6']:
                vxlan_dump['local'] = \
                    ip_address(unicode(vxlan_dump['local']))
                vxlan_dump['remote'] = \
                    ip_address(unicode(vxlan_dump['remote']))
            else:
                vxlan_dump['local'] = \
                    ip_address(unicode(vxlan_dump['local'][0:4]))
                vxlan_dump['remote'] = \
                    ip_address(unicode(vxlan_dump['remote'][0:4]))
            return vxlan_dump

        if interface_name is not None:
            sw_if_index = InterfaceUtil.get_interface_index(
                node, interface_name)
        else:
            sw_if_index = int(Constants.BITWISE_NON_ZERO)

        cmd = 'vxlan_gpe_tunnel_dump'
        args = dict(sw_if_index=sw_if_index)
        err_msg = 'Failed to get VXLAN-GPE dump on host {host}'.format(
            host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, **args).get_details(err_msg)

        data = list() if interface_name is None else dict()
        for dump in details:
            if interface_name is None:
                data.append(process_vxlan_gpe_dump(dump))
            elif dump['sw_if_index'] == sw_if_index:
                data = process_vxlan_gpe_dump(dump)
                break

        logger.debug('VXLAN-GPE data:\n{vxlan_gpe_data}'.format(
            vxlan_gpe_data=data))
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
        cmd = 'sw_interface_set_table'
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            is_ipv6=ipv6,
            vrf_id=int(table_id))
        err_msg = 'Failed to assign interface {ifc} to FIB table'.format(
            ifc=interface)
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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
    def init_avf_interface(node, ifc_key, numvfs=1, osi_layer='L2'):
        """Init PCI device by creating VIFs and bind them to vfio-pci for AVF
        driver testing on DUT.

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
        if kernel_driver not in ("i40e", "i40evf"):
            raise RuntimeError(
                "AVF needs i40e-compatible driver, not {driver} at node {host}"
                " ifc {ifc}".format(
                    driver=kernel_driver, host=node["host"], ifc=ifc_key))
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

        # Initialize PCI VFs.
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
            if osi_layer == 'L2':
                InterfaceUtil.set_linux_interface_spoof_off(node, pf_dev,
                                                            vf_id=vf_id)
            InterfaceUtil.set_linux_interface_mac(node, pf_dev, vf_mac_addr,
                                                  vf_id=vf_id)

            DUTSetup.pci_vf_driver_unbind(node, pf_pci_addr, vf_id)
            DUTSetup.pci_vf_driver_bind(node, pf_pci_addr, vf_id, uio_driver)

            # Add newly created ports into topology file
            vf_ifc_name = '{pf_if_key}_vif'.format(pf_if_key=ifc_key)
            vf_pci_addr = DUTSetup.get_virtfn_pci_addr(node, pf_pci_addr, vf_id)
            vf_ifc_key = Topology.add_new_port(node, vf_ifc_name)
            Topology.update_interface_name(node, vf_ifc_key,
                                           vf_ifc_name+str(vf_id+1))
            Topology.update_interface_mac_address(node, vf_ifc_key, vf_mac_addr)
            Topology.update_interface_pci_address(node, vf_ifc_key, vf_pci_addr)
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
        cmd = 'sw_interface_rx_placement_dump'
        err_msg = "Failed to run '{cmd}' PAPI command on host {host}!".format(
            cmd=cmd, host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            for ifc in node['interfaces'].values():
                if ifc['vpp_sw_index'] is not None:
                    papi_exec.add(cmd, sw_if_index=ifc['vpp_sw_index'])
            details = papi_exec.get_details(err_msg)
        return sorted(details, key=lambda k: k['sw_if_index'])

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
        :raises RuntimeError: If failed to run command on host or if no API
            reply received.
        """
        cmd = 'sw_interface_set_rx_placement'
        err_msg = "Failed to set interface RX placement to worker on host " \
                  "{host}!".format(host=node['host'])
        args = dict(
            sw_if_index=sw_if_index,
            queue_id=queue_id,
            worker_id=worker_id,
            is_main=False
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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
        if not worker_cnt:
            return
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
