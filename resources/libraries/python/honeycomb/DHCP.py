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

"""Keywords to manipulate NAT configuration using Honeycomb REST API."""

from resources.libraries.python.HTTPRequest import HTTPCodes
from resources.libraries.python.honeycomb.HoneycombSetup import HoneycombError
from resources.libraries.python.honeycomb.HoneycombUtil \
    import DataRepresentation
from resources.libraries.python.honeycomb.HoneycombUtil \
    import HoneycombUtil as HcUtil


class DHCPRelayKeywords(object):
    """Keywords for NAT configuration."""

    def __init__(self):
        pass

    @staticmethod
    def _set_dhcp_relay_properties(node, path, data=None):
        """Set DHCP relay properties and check the return code.

        :param node: Honeycomb node.
        :param path: Path which is added to the base path to identify the data.
        :param data: The new data to be set. If None, the item will be removed.
        :type node: dict
        :type path: str
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response is not
        200 = OK or 201 = ACCEPTED.
        """

        if data:
            status_code, resp = HcUtil. \
                put_honeycomb_data(node, "config_dhcp_relay", data, path,
                                   data_representation=DataRepresentation.JSON)
        else:
            status_code, resp = HcUtil. \
                delete_honeycomb_data(node, "config_dhcp_relay", path)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "The configuration of DHCP relay was not successful. "
                "Status code: {0}.".format(status_code))
        return resp

    @staticmethod
    def add_dhcp_relay(node, data, ip_version, entry_id):
        """Add a DHCP relay entry to the list on entries.

        :param node: Honeycomb node.
        :param data: Configuration for the relay entry.
        :param ip_version: IP protocol version, ipv4 or ipv6.
        :param entry_id: Numeric ID.
        :type node: dict
        :type data: dict
        :type ip_version: str
        :type entry_id: int
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/relay/dhcp:{0}/{1}".format(ip_version, entry_id)

        return DHCPRelayKeywords._set_dhcp_relay_properties(node, path, data)

    @staticmethod
    def clear_dhcp_relay_configuration(node):
        """Remove all DHCP relay configuration from the node.

        :param node: Honeycomb node.
        :type node: dict
        :returns: Content of response.
        :rtype: bytearray
        """
        return DHCPRelayKeywords._set_dhcp_relay_properties(node, "")

    @staticmethod
    def get_dhcp_relay_oper_data(node):
        """Get operational data about the DHCP relay feature.

        :param node: Honeycomb node.
        :type node: dict
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response is not 200 = OK.
        """

        status_code, resp = HcUtil. \
            get_honeycomb_data(node, "config_dhcp_relay")

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Could not retrieve DHCP relay configuration. "
                "Status code: {0}.".format(status_code))
        return resp
