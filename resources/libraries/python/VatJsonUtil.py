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
    """Utilities to work with JSON data format from VAT."""

    @staticmethod
    def _convert_mac_to_number_list(mac_address):
        """Convert MAC address string to list of decimal numbers.

        Converts a ":" separated MAC address to decimal number list as used
        in JSON interface dump.

        :param mac_address: MAC address.
        :type mac_address: str
        :return: List representation of MAC address.
        :rtype: list
        """
        list_mac = []
        for num in mac_address.split(":"):
            list_mac.append(int(num, 16))
        return list_mac

    @staticmethod
    def get_vpp_interface_by_mac(interfaces_list, mac_address):
        """Return interface dictionary from interface_list by MAC address.

        Extracts interface dictionary from all of the interfaces in interfaces
        list parsed from JSON according to mac_address of the interface.

        :param interfaces_list: Interfaces parsed from JSON.
        :param mac_address: MAC address of interface we are looking for.
        :type interfaces_list: list
        :type mac_address: str
        :return: Interface from JSON.
        :rtype: dict
        """
        interface_dict = {}
        list_mac_address = VatJsonUtil._convert_mac_to_number_list(mac_address)
        logger.trace("MAC address {0} converted to list {1}."
                     .format(mac_address, list_mac_address))
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

    @staticmethod
    def update_vpp_interface_data_from_json(node, interface_dump_json):
        """Update vpp node data in node__DICT from JSON interface dump.

        This method updates vpp interface names and sw if indexes according to
        interface MAC addresses found in interface_dump_json.

        :param node: Node dictionary.
        :param interface_dump_json: JSON output from dump_interface_list VAT
        command.
        :type node: dict
        :type interface_dump_json: str
        """
        interface_list = JsonParser().parse_data(interface_dump_json)
        for ifc in node['interfaces'].values():
            if_mac = ifc['mac_address']
            interface_dict = VatJsonUtil.get_vpp_interface_by_mac(
                interface_list, if_mac)
            if not interface_dict:
                logger.trace('Interface {0} not found by MAC {1}'
                             .format(ifc, if_mac))
                continue
            ifc['name'] = interface_dict["interface_name"]
            ifc['vpp_sw_index'] = interface_dict["sw_if_index"]
            ifc['mtu'] = interface_dict["mtu"]

    @staticmethod
    def get_interface_sw_index_from_json(interface_dump_json, interface_name):
        """Get sw_if_index from given JSON output by interface name.

        :param interface_dump_json: JSON output from dump_interface_list VAT
        command.
        :param interface_name: Interface name.
        :type interface_dump_json: str
        :type interface_name: str
        :return: SW interface index.
        :rtype: int
        :raises ValueError: If interface not found in interface_dump_json.
        """
        logger.trace(interface_dump_json)
        interface_list = JsonParser().parse_data(interface_dump_json)
        for interface in interface_list:
            try:
                if interface['interface_name'] == interface_name:
                    index = interface['sw_if_index']
                    logger.debug('Interface with name {} has sw_if_index {}.'
                                 .format(interface_name, index))
                    return index
            except KeyError:
                pass
        raise ValueError('Interface with name {} not found.'
                         .format(interface_name))

    @staticmethod
    def get_interface_name_from_json(interface_dump_json, sw_if_index):
        """Get interface name from given JSON output by sw_if_index.

        :param interface_dump_json: JSON output from dump_interface_list VAT
        command.
        :param sw_if_index: SW interface index.
        :type interface_dump_json: str
        :type sw_if_index: int
        :return: Interface name.
        :rtype: str
        :raises ValueError: If interface not found in interface_dump_json.
        """
        logger.trace(interface_dump_json)
        interface_list = JsonParser().parse_data(interface_dump_json)
        for interface in interface_list:
            try:
                if interface['sw_if_index'] == sw_if_index:
                    interface_name = interface['interface_name']
                    logger.debug('Interface with name {} has sw_if_index {}.'
                                 .format(interface_name, sw_if_index))
                    return interface_name
            except KeyError:
                pass
        raise ValueError('Interface with sw_if_index {} not found.'
                         .format(sw_if_index))

    @staticmethod
    def verify_vat_retval(vat_out, exp_retval=0, err_msg='VAT cmd failed'):
        """Verify return value of VAT command.

        VAT command JSON output should be object (dict in python) or array. We
        are looking for something like this: { "retval": 0 }. Verification is
        skipped if VAT output does not contain return value element or root
        element is array.

        :param vat_out: VAT command output in python representation of JSON.
        :param exp_retval: Expected return value (default 0).
        :err_msg: Message to be displayed in case of error (optional).
        :type vat_out: dict or list
        :type exp_retval: int
        :type err_msg: str
        :raises RuntimeError: If VAT command return value is incorrect.
        """
        if isinstance(vat_out, dict):
            retval = vat_out.get('retval')
            if retval is not None:
                if retval != exp_retval:
                    raise RuntimeError(err_msg)
