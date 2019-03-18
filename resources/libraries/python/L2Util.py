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

"""L2 Utilities Library."""

import binascii
from textwrap import wrap

from enum import IntEnum

from resources.libraries.python.Constants import Constants
from resources.libraries.python.PapiExecutor import PapiExecutor
from resources.libraries.python.topology import Topology
from resources.libraries.python.ssh import exec_cmd_no_error


class L2VtrOp(IntEnum):
    """VLAN tag rewrite operation."""
    L2_VTR_DISABLED = 0
    L2_VTR_PUSH_1 = 1
    L2_VTR_PUSH_2 = 2
    L2_VTR_POP_1 = 3
    L2_VTR_POP_2 = 4
    L2_VTR_TRANSLATE_1_1 = 5
    L2_VTR_TRANSLATE_1_2 = 6
    L2_VTR_TRANSLATE_2_1 = 7
    L2_VTR_TRANSLATE_2_2 = 8


class L2Util(object):
    """Utilities for l2 configuration."""

    @staticmethod
    def mac_to_int(mac_str):
        """Convert MAC address from string format (e.g. 01:02:03:04:05:06) to
        integer representation (1108152157446).

        :param mac_str: MAC address in string representation.
        :type mac_str: str
        :returns: Integer representation of MAC address.
        :rtype: int
        """
        return int(mac_str.replace(':', ''), 16)

    @staticmethod
    def int_to_mac(mac_int):
        """Convert MAC address from integer representation (e.g. 1108152157446)
        to string format (01:02:03:04:05:06).

        :param mac_int: MAC address in integer representation.
        :type mac_int: int
        :returns: String representation of MAC address.
        :rtype: str
        """
        return ':'.join(wrap("{:012x}".format(mac_int), width=2))

    @staticmethod
    def mac_to_bin(mac_str):
        """Convert MAC address from string format (e.g. 01:02:03:04:05:06) to
        binary representation (\x01\x02\x03\x04\x05\x06).

        :param mac_str: MAC address in string representation.
        :type mac_str: str
        :returns: Binary representation of MAC address.
        :rtype: binary
        """
        return binascii.unhexlify(mac_str.replace(':', ''))

    @staticmethod
    def bin_to_mac(mac_bin):
        """Convert MAC address from binary representation
        (\x01\x02\x03\x04\x05\x06) to string format (e.g. 01:02:03:04:05:06).

        :param mac_bin: MAC address in binary representation.
        :type mac_bin: binary
        :returns: String representation of MAC address.
        :rtype: str
        """
        mac_str = ':'.join(binascii.hexlify(mac_bin)[i:i + 2]
                           for i in range(0, 12, 2))
        return str(mac_str.decode('ascii'))

    @staticmethod
    def vpp_add_l2fib_entry(node, mac, interface, bd_id, static_mac=1,
                            filter_mac=0, bvi_mac=0):
        """ Create a static L2FIB entry on a VPP node.

        :param node: Node to add L2FIB entry on.
        :param mac: Destination mac address in string format 01:02:03:04:05:06.
        :param interface: Interface name or sw_if_index.
        :param bd_id: Bridge domain index.
        :param static_mac: Set to 1 to create static MAC entry.
            (Default value = 1)
        :param filter_mac: Set to 1 to drop packet that's source or destination
            MAC address contains defined MAC address. (Default value = 0)
        :param bvi_mac: Set to 1 to create entry that points to BVI interface.
            (Default value = 0)
        :type node: dict
        :type mac: str
        :type interface: str or int
        :type bd_id: int or str
        :type static_mac: int or str
        :type filter_mac: int or str
        :type bvi_mac: int or str
        """

        if isinstance(interface, basestring):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        else:
            sw_if_index = interface

        cmd = 'l2fib_add_del'
        err_msg = 'Failed to add L2FIB entry on host {host}'.format(
            host=node['host'])
        args = dict(mac=L2Util.mac_to_bin(mac),
                    bd_id=int(bd_id),
                    sw_if_index=sw_if_index,
                    is_add=1,
                    static_mac=int(static_mac),
                    filter_mac=int(filter_mac),
                    bvi_mac=int(bvi_mac))
        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_replies(err_msg).\
                verify_reply(err_msg=err_msg)

    @staticmethod
    def create_l2_bd(node, bd_id, flood=1, uu_flood=1, forward=1, learn=1,
                     arp_term=0):
        """Create an L2 bridge domain on a VPP node.

        :param node: Node where we wish to crate the L2 bridge domain.
        :param bd_id: Bridge domain index.
        :param flood: Enable/disable bcast/mcast flooding in the BD.
            (Default value = 1)
        :param uu_flood: Enable/disable unknown unicast flood in the BD.
            (Default value = 1)
        :param forward: Enable/disable forwarding on all interfaces in
            the BD. (Default value = 1)
        :param learn: Enable/disable MAC learning on all interfaces in the BD.
            (Default value = 1)
        :param arp_term: Enable/disable arp termination in the BD.
            (Default value = 1)
        :type node: dict
        :type bd_id: int or str
        :type flood: int or str
        :type uu_flood: int or str
        :type forward: int or str
        :type learn: int or str
        :type arp_term: int or str
        """

        cmd = 'bridge_domain_add_del'
        err_msg = 'Failed to create L2 bridge domain on host {host}'.format(
            host=node['host'])
        args = dict(bd_id=int(bd_id),
                    flood=int(flood),
                    uu_flood=int(uu_flood),
                    forward=int(forward),
                    learn=int(learn),
                    arp_term=int(arp_term),
                    is_add=1)
        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_replies(err_msg).\
                verify_reply(err_msg=err_msg)

    @staticmethod
    def add_interface_to_l2_bd(node, interface, bd_id, shg=0, port_type=0):
        """Add an interface to the L2 bridge domain.

        Get SW IF ID and add it to the bridge domain.

        :param node: Node where we want to execute the command that does this.
        :param interface: Interface name.
        :param bd_id: Bridge domain index.
        :param shg: Split-horizon group index. (Default value = 0)
        :param port_type: Port mode: 0 - normal, 1 - BVI, 2 - UU_FWD.
            (Default value = 0)
        :type node: dict
        :type interface: str
        :type bd_id: int or str
        :type shg: int or str
        :type port_type: int or str
        """

        sw_if_index = Topology.get_interface_sw_index(node, interface)

        cmd = 'sw_interface_set_l2_bridge'
        err_msg = 'Failed to add interface {ifc} to L2 bridge domain on host ' \
                  '{host}'.format(ifc=interface, host=node['host'])
        args = dict(rx_sw_if_index=sw_if_index,
                    bd_id=int(bd_id),
                    shg=int(shg),
                    port_type=int(port_type),
                    enable=1)
        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_replies(err_msg).\
                verify_reply(err_msg=err_msg)

    @staticmethod
    def vpp_add_l2_bridge_domain(node, bd_id, port_1, port_2, learn=True):
        """Add L2 bridge domain with 2 interfaces to the VPP node.

        :param node: Node to add L2BD on.
        :param bd_id: Bridge domain ID.
        :param port_1: First interface name added to L2BD.
        :param port_2: Second interface name added to L2BD.
        :param learn: Enable/disable MAC learn.
        :type node: dict
        :type bd_id: int
        :type port_1: str
        :type port_2: str
        :type learn: bool
        """

        sw_if_index1 = Topology.get_interface_sw_index(node, port_1)
        sw_if_index2 = Topology.get_interface_sw_index(node, port_2)
        learn_int = 1 if learn else 0

        cmd1 = 'bridge_domain_add_del'
        args1 = dict(bd_id=int(bd_id),
                     flood=1,
                     uu_flood=1,
                     forward=1,
                     learn=learn_int,
                     arp_term=0,
                     is_add=1)

        cmd2 = 'sw_interface_set_l2_bridge'
        args2 = dict(rx_sw_if_index=sw_if_index1,
                     bd_id=int(bd_id),
                     shg=0,
                     port_type=0,
                     enable=1)

        args3 = dict(rx_sw_if_index=sw_if_index2,
                     bd_id=int(bd_id),
                     shg=0,
                     port_type=0,
                     enable=1)

        err_msg = 'Failed to add L2 bridge domain with 2 interfaces on host' \
                  ' {host}'.format(host=node['host'])

        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd1, **args1).add(cmd2, **args2).add(cmd2, **args3).\
                get_replies(err_msg).verify_replies(err_msg=err_msg)

    @staticmethod
    def vpp_setup_bidirectional_cross_connect(node, interface1, interface2):
        """Create bidirectional cross-connect between 2 interfaces on vpp node.

        :param node: Node to add bidirectional cross-connect.
        :param interface1: First interface name or sw_if_index.
        :param interface2: Second interface name or sw_if_index.
        :type node: dict
        :type interface1: str or int
        :type interface2: str or int
        """

        if isinstance(interface1, basestring):
            sw_iface1 = Topology().get_interface_sw_index(node, interface1)
        else:
            sw_iface1 = interface1

        if isinstance(interface2, basestring):
            sw_iface2 = Topology().get_interface_sw_index(node, interface2)
        else:
            sw_iface2 = interface2

        cmd = 'sw_interface_set_l2_xconnect'
        args1 = dict(rx_sw_if_index=sw_iface1,
                     tx_sw_if_index=sw_iface2,
                     enable=1)
        args2 = dict(rx_sw_if_index=sw_iface2,
                     tx_sw_if_index=sw_iface1,
                     enable=1)

        err_msg = 'Failed to add L2 cross-connect between two interfaces on' \
                  ' host {host}'.format(host=node['host'])

        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args1).add(cmd, **args2).get_replies(err_msg).\
                verify_replies(err_msg=err_msg)

    @staticmethod
    def vpp_setup_bidirectional_l2_patch(node, interface1, interface2):
        """Create bidirectional l2 patch between 2 interfaces on vpp node.

        :param node: Node to add bidirectional l2 patch.
        :param interface1: First interface name or sw_if_index.
        :param interface2: Second interface name or sw_if_index.
        :type node: dict
        :type interface1: str or int
        :type interface2: str or int
        """

        if isinstance(interface1, basestring):
            sw_iface1 = Topology().get_interface_sw_index(node, interface1)
        else:
            sw_iface1 = interface1

        if isinstance(interface2, basestring):
            sw_iface2 = Topology().get_interface_sw_index(node, interface2)
        else:
            sw_iface2 = interface2

        cmd = 'l2_patch_add_del'
        args1 = dict(rx_sw_if_index=sw_iface1,
                     tx_sw_if_index=sw_iface2,
                     is_add=1)
        args2 = dict(rx_sw_if_index=sw_iface2,
                     tx_sw_if_index=sw_iface1,
                     is_add=1)

        err_msg = 'Failed to add L2 patch between two interfaces on' \
                  ' host {host}'.format(host=node['host'])

        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args1).add(cmd, **args2).get_replies(err_msg).\
                verify_replies(err_msg=err_msg)

    @staticmethod
    def linux_add_bridge(node, br_name, if_1, if_2, set_up=True):
        """Bridge two interfaces on linux node.

        :param node: Node to add bridge on.
        :param br_name: Bridge name.
        :param if_1: First interface to be added to the bridge.
        :param if_2: Second interface to be added to the bridge.
        :param set_up: Change bridge interface state to up after create bridge.
            Optional. Default: True.
        :type node: dict
        :type br_name: str
        :type if_1: str
        :type if_2: str
        :type set_up: bool
        """

        cmd = 'brctl addbr {0}'.format(br_name)
        exec_cmd_no_error(node, cmd, sudo=True)
        cmd = 'brctl addif {0} {1}'.format(br_name, if_1)
        exec_cmd_no_error(node, cmd, sudo=True)
        cmd = 'brctl addif {0} {1}'.format(br_name, if_2)
        exec_cmd_no_error(node, cmd, sudo=True)
        if set_up:
            cmd = 'ip link set dev {0} up'.format(br_name)
            exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def linux_del_bridge(node, br_name, set_down=True):
        """Delete bridge from linux node.

        ..note:: The network interface corresponding to the bridge must be
            down before it can be deleted!

        :param node: Node to delete bridge from.
        :param br_name: Bridge name.
        :param set_down: Change bridge interface state to down before delbr
            command. Optional. Default: True.
        :type node: dict
        :type br_name: str
        :type set_down: bool
        """

        if set_down:
            cmd = 'ip link set dev {0} down'.format(br_name)
            exec_cmd_no_error(node, cmd, sudo=True)
        cmd = 'brctl delbr {0}'.format(br_name)
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def vpp_get_bridge_domain_data(node, bd_id=0xffffffff):
        """Get all bridge domain data from a VPP node. If a domain ID number is
        provided, return only data for the matching bridge domain.

        :param node: VPP node to get bridge domain data from.
        :param bd_id: Numeric ID of a specific bridge domain.
        :type node: dict
        :type bd_id: int
        :returns: List of dictionaries containing data for each bridge domain,
            or a single dictionary for the specified bridge domain.
        :rtype: list or dict
        """

        cmd = 'bridge_domain_dump'
        cmd_reply = 'bridge_domain_details'
        args = dict(bd_id=int(bd_id))
        err_msg = 'Failed to get L2FIB dump on host {host}'.format(
            host=node['host'])
        with PapiExecutor(node) as papi_exec:
            papi_resp = papi_exec.add(cmd, **args).get_dump(err_msg)

        data = papi_resp.reply[0]['api_reply']

        bd_data = list() if bd_id == Constants.BITWISE_NON_ZERO else dict()
        for bridge_domain in data:
            if bd_id == Constants.BITWISE_NON_ZERO:
                bd_data.append(bridge_domain[cmd_reply])
            else:
                if bridge_domain[cmd_reply]['bd_id'] == bd_id:
                    return bridge_domain[cmd_reply]

        return bd_data

    @staticmethod
    def l2_vlan_tag_rewrite(node, interface, tag_rewrite_method,
                            push_dot1q=True, tag1_id=None, tag2_id=None):
        """Rewrite tags in ethernet frame.

        :param node: Node to rewrite tags.
        :param interface: Interface on which rewrite tags.
        :param tag_rewrite_method: Method of tag rewrite.
        :param push_dot1q: Optional parameter to disable to push dot1q tag
            instead of dot1ad.
        :param tag1_id: Optional tag1 ID for VLAN.
        :param tag2_id: Optional tag2 ID for VLAN.
        :type node: dict
        :type interface: str or int
        :type tag_rewrite_method: str
        :type push_dot1q: bool
        :type tag1_id: int
        :type tag2_id: int
        """

        tag1_id = int(tag1_id) if tag1_id else 0
        tag2_id = int(tag2_id) if tag2_id else 0

        vtr_oper = getattr(L2VtrOp, 'L2_VTR_{}'.format(
            tag_rewrite_method.replace('-', '_').upper()))

        if isinstance(interface, basestring):
            iface_key = Topology.get_interface_by_name(node, interface)
            sw_if_index = Topology.get_interface_sw_index(node, iface_key)
        else:
            sw_if_index = interface

        cmd = 'l2_interface_vlan_tag_rewrite'
        args = dict(sw_if_index=sw_if_index,
                    vtr_op=int(vtr_oper),
                    push_dot1q=int(push_dot1q),
                    tag1=tag1_id,
                    tag2=tag2_id)
        err_msg = 'Failed to set VLAN TAG rewrite on host {host}'.format(
            host=node['host'])
        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_replies(err_msg).\
                verify_reply(err_msg=err_msg)

    @staticmethod
    def get_l2_fib_table(node, bd_id):
        """Retrieves the L2 FIB table.

        :param node: VPP node.
        :param bd_id: Index of the bridge domain.
        :type node: dict
        :type bd_id: int
        :returns: L2 FIB table.
        :rtype: list
        """

        cmd = 'l2_fib_table_dump'
        cmd_reply = 'l2_fib_table_details'
        args = dict(bd_id=int(bd_id))
        err_msg = 'Failed to get L2FIB dump on host {host}'.format(
            host=node['host'])
        with PapiExecutor(node) as papi_exec:
            papi_resp = papi_exec.add(cmd, **args).get_dump(err_msg)

        data = papi_resp.reply[0]['api_reply']

        fib_data = list()
        for fib in data:
            fib_item = fib[cmd_reply]
            fib_item['mac'] = L2Util.bin_to_mac(fib_item['mac'])
            fib_data.append(fib_item)

        return fib_data

    @staticmethod
    def get_l2_fib_entry_by_mac(node, bd_index, mac):
        """Retrieves the L2 FIB entry specified by MAC address using PAPI.

        :param node: VPP node.
        :param bd_index: Index of the bridge domain.
        :param mac: MAC address used as the key in L2 FIB data structure.
        :type node: dict
        :type bd_index: int
        :type mac: str
        :returns: L2 FIB entry
        :rtype: dict
        """

        bd_data = L2Util.vpp_get_bridge_domain_data(node)
        bd_id = bd_data[bd_index-1]['bd_id']

        table = L2Util.get_l2_fib_table(node, bd_id)

        for entry in table:
            if entry['mac'] == mac:
                return entry
        return {}
