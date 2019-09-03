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

"""Tap utilities library."""
from enum import IntEnum

from ipaddress import ip_address
from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.L2Util import L2Util
from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.topology import Topology


class TapFlags(IntEnum):
    """TAP interface flags."""
    TAP_FLAG_GSO = 1


class Tap(object):
    """Tap utilities."""

    @staticmethod
    def add_tap_interface(node, tap_name, mac=None):
        """Add tap interface with name and optionally with MAC.

        :param node: Node to add tap on.
        :param tap_name: Tap interface name for linux tap.
        :param mac: Optional MAC address for VPP tap.
        :type node: dict
        :type tap_name: str or unicode
        :type mac: str
        :returns: Returns a interface index.
        :rtype: int
        """
        if isinstance(tap_name, unicode):
            tap_name = str(tap_name)
        cmd = 'tap_create_v2'
        args = dict(
            id=Constants.BITWISE_NON_ZERO,
            use_random_mac=False if mac else True,
            mac_address=L2Util.mac_to_bin(mac) if mac else None,
            host_mtu_set=False,
            host_mac_addr_set=False,
            # host_mac_addr=6 * b'\x00',
            host_ip4_prefix_set=False,
            # host_ip4_prefix=4 * b'\x00',
            host_ip6_prefix_set=False,
            # host_ip6_prefix=16 * b'\x00',
            host_ip4_gw_set=False,
            # host_ip4_gw=4 * b'\x00',
            host_ip6_gw_set=False,
            # host_ip6_gw=16 * b'\x00',
            tap_flags=TapFlags.TAP_FLAG_GSO.value,
            host_namespace_set=False,
            host_if_name_set=True,
            host_bridge_set=False,
            # host_namespace=64 * b'\x00',
            host_if_name=tap_name,
            # host_bridge=64 * b'\x00',
            # tag=y
        )
        err_msg = 'Failed to create tap interface {tap} on host {host}'.format(
            tap=tap_name, host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        if_key = Topology.add_new_port(node, 'tap')
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)
        Topology.update_interface_name(node, if_key, tap_name)
        if mac is None:
            mac = Tap.vpp_get_tap_interface_mac(node, tap_name)
        Topology.update_interface_mac_address(node, if_key, mac)
        tap_dev_name = Tap.vpp_get_tap_dev_name(node, tap_name)
        Topology.update_interface_tap_dev_name(node, if_key, tap_dev_name)

        return sw_if_index

    @staticmethod
    def vpp_get_tap_dev_name(node, host_if_name):
        """Get VPP tap interface name from hardware interfaces dump.

        :param node: DUT node.
        :param host_if_name: Tap host interface name.
        :type node: dict
        :type host_if_name: str
        :returns: VPP tap interface dev_name.
        :rtype: str
        """
        return Tap.tap_dump(node, host_if_name).get('dev_name')

    @staticmethod
    def vpp_get_tap_interface_mac(node, interface_name):
        """Get tap interface MAC address from interfaces dump.

        :param node: DUT node.
        :param interface_name: Tap interface name.
        :type node: dict
        :type interface_name: str
        :returns: Tap interface MAC address.
        :rtype: str
        """
        return InterfaceUtil.vpp_get_interface_mac(node, interface_name)

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
        def process_tap_dump(tap_dump):
            """Process tap dump.

            :param tap_dump: Tap interface dump.
            :type tap_dump: dict
            :returns: Processed tap interface dump.
            :rtype: dict
            """
            # tap_dump['dev_name'] = tap_dump['dev_name'].rstrip('\x00')
            # tap_dump['host_if_name'] = tap_dump['host_if_name'].rstrip('\x00')
            # tap_dump['host_namespace'] = \
            #     tap_dump['host_namespace'].rstrip('\x00')
            tap_dump['host_mac_addr'] = str(tap_dump['host_mac_addr'])
            tap_dump['host_ip4_addr'] = ip_address(tap_dump['host_ip4_addr'])
            tap_dump['host_ip6_addr'] = ip_address(tap_dump['host_ip6_addr'])
            return tap_dump

        cmd = 'sw_interface_tap_v2_dump'
        err_msg = 'Failed to get TAP dump on host {host}'.format(
            host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd).get_details(err_msg)

        data = list() if name is None else dict()
        for dump in details:
            if name is None:
                data.append(process_tap_dump(dump))
            elif dump.get('host_if_name') == name:
                data = process_tap_dump(dump)
                break

        logger.debug('TAP data:\n{tap_data}'.format(tap_data=data))
        return data
