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

"""Utilities to work with JSON data format from VAT."""

from robot.api import logger

from resources.libraries.python.parsers.JsonParser import JsonParser


class VatJsonUtil(object):

    @staticmethod
    def _convert_mac_to_number_list(mac_address):
        """Convert mac address string to list of decimal numbers.

        Converts a ":" separated mac address to decimal number list as used
        in JSON interface dump.

        :param mac_address: MAC address
        :type mac_address: str
        :return: list representation of MAC address
        :rtype: list
        """
        list_mac = []
        for num in mac_address.split(":"):
            list_mac.append(int(num, 16))
        return list_mac

    @staticmethod
    def get_vpp_interface_by_mac(interfaces_list, mac_address):
        """Return interface dictionary from interface_list by mac address.

        Extracts interface dictionary from all of the interfaces in interfaces
        list parsed from json according to mac_address of the interface.

        :param interfaces_list: Interfaces parsed from JSON.
        :param mac_address: MAC address of interface we are looking for.
        :type interfaces_list: dict
        :type mac_address: str
        :return: Interface from JSON.
        :rtype: dict
        """
        interface_dict = {}
        list_mac_address = VatJsonUtil._convert_mac_to_number_list(mac_address)
        logger.trace(str(list_mac_address))
        for interface in interfaces_list:
            # TODO: create vat json integrity checking and move there
            if "l2_address" not in interface:
                raise KeyError(
                    "key l2_address not found in interface dict."
                    "Probably input list is not parsed from correct VAT "
                    "json output.")
            if "l2_address_length" not in interface:
                raise KeyError(
                    "key l2_address_length not found in interface "
                    "dict. Probably input list is not parsed from correct "
                    "VAT json output.")
            mac_from_json = interface["l2_address"][:6]
            if mac_from_json == list_mac_address:
                if interface["l2_address_length"] != 6:
                    raise ValueError("l2_address_length value is not 6.")
                interface_dict = interface
                break
        return interface_dict

    # @staticmethod
    # def get_vpp_interface_name_from_json_by_mac(json_data, mac_address):
    #     """Return VPP interface name string from VAT interface dump JSON output.
    #
    #     Extracts the name given to an interface by VPP.
    #     These interface names differ from what you would see if you
    #     used the ifconfig or similar command.
    #     Required JSON data can be obtained by calling:
    #     VatExecutor.execute_script_json_out("dump_interfaces.vat", node)
    #
    #     :param json_data: JSON data from sw_interface_dump VAT command.
    #     :param mac_address: MAC address of interface whose VPP name we wish
    #     to discover.
    #     :type json_data: str
    #     :type mac_address: str
    #     :return: VPP interface name.
    #     :rtype: str
    #     """
    #     interfaces_list = JsonParser().parse_data(json_data)
    #     # TODO: checking if json data is parsed correctly
    #     interface_dict = VatJsonUtil.get_vpp_interface_by_mac(interfaces_list,
    #                                                           mac_address)
    #     interface_name = interface_dict["interface_name"]
    #     return interface_name

    @staticmethod
    def update_vpp_interface_data_from_json(node, interface_dump_json):
        """Update vpp node data in node__DICT from json interface dump.

        This method updates vpp interface names and sw if indexes according to
        interface mac addresses found in interface_dump_json
        :param node: node dictionary
        :param interface_dump_json: json output from dump_interface_list VAT
        command
        """
        interface_list = JsonParser().parse_data(interface_dump_json)
        for ifc in node['interfaces'].values():
            if_mac = ifc['mac_address']
            interface_dict = VatJsonUtil.get_vpp_interface_by_mac(
                interface_list, if_mac)
            if not interface_dict:
                raise Exception('Interface {0} not found by MAC {1}'
                                .format(ifc, if_mac))
            ifc['name'] = interface_dict["interface_name"]
            ifc['vpp_sw_index'] = interface_dict["sw_if_index"]
            ifc['mtu'] = interface_dict["mtu"]
