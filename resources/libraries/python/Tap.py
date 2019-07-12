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


from resources.libraries.python.Constants import Constants
from resources.libraries.python.L2Util import L2Util
from resources.libraries.python.VatExecutor import VatTerminal
from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.topology import Topology


class Tap(object):
    """Tap utilities."""

    @staticmethod
    def add_tap_interface(node, tap_name, mac=None):
        """Add tap interface with name and optionally with MAC.

        :param node: Node to add tap on.
        :param tap_name: Tap interface name for linux tap.
        :param mac: Optional MAC address for VPP tap.
        :type node: dict
        :type tap_name: str
        :type mac: str
        :returns: Returns a interface index.
        :rtype: int
        """
        cmd = 'tap_create_v2'
        args = dict(
            id=Constants.BITWISE_NON_ZERO,
            use_random_mac=0 if mac else 1,
            mac_address=L2Util.mac_to_bin(mac) if mac else 6 * '\x00',
            host_if_name_set=1,
            host_if_name=tap_name + (64 - len(tap_name)) * b'\x00',
        )
        err_msg = 'Failed to create tap interface {tap} on host {host}'.format(
            tap=tap_name, host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        if_key = Topology.add_new_port(node, 'tap')
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)
        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)
        if mac is None:
            mac = InterfaceUtil.vpp_get_interface_mac(node, sw_if_index)
        Topology.update_interface_mac_address(node, if_key, mac)
        Topology.update_interface_tap_dev_name(node, if_key, tap_name)

        return sw_if_index

    @staticmethod
    def vpp_get_tap_interface_name(node, sw_if_index):
        """Get VPP tap interface name from hardware interfaces dump.

        :param node: DUT node.
        :param sw_if_index: DUT node.
        :type node: dict
        :type sw_if_index: int
        :returns: VPP tap interface name.
        :rtype: str
        """
        with VatTerminal(node, json_param=False) as vat:
            response = vat.vat_terminal_exec_cmd_from_template(
                'show_hardware_detail.vat')

        for line in str(response[0]).splitlines():
            if line.startswith('tap-'):
                line_split = line.split()
                if line_split[1] == sw_if_index:
                    return line_split[0]

        return None

    @staticmethod
    def vpp_get_tap_interface_mac(node, sw_if_index):
        """Get tap interface MAC address from hardware interfaces dump.

        :param node: DUT node.
        :param sw_if_index: DUT node.
        :type node: dict
        :type sw_if_index: int
        :returns: Tap interface MAC address.
        :rtype: str
        """
        with VatTerminal(node, json_param=False) as vat:
            response = vat.vat_terminal_exec_cmd_from_template(
                'show_hardware_detail.vat')

        tap_if_match = False
        for line in str(response[0]).splitlines():
            if tap_if_match:
                line_split = line.split()
                return line_split[-1]
            if line.startswith('tap-'):
                line_split = line.split()
                if line_split[1] == sw_if_index:
                    tap_if_match = True

        return None
