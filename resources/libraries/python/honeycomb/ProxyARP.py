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

"""This module implements keywords to configure proxyARP using Honeycomb
REST API."""

from resources.libraries.python.HTTPRequest import HTTPCodes
from resources.libraries.python.honeycomb.HoneycombSetup import HoneycombError
from resources.libraries.python.honeycomb.HoneycombUtil \
    import HoneycombUtil as HcUtil
from resources.libraries.python.honeycomb.HoneycombUtil \
    import DataRepresentation
from resources.libraries.python.topology import Topology


class ProxyARPKeywords(object):
    """Implementation of keywords which make it possible to:
    - configure proxyARP behaviour
    - enable/disable proxyARP on individual interfaces
    """

    def __init__(self):
        """Initializer."""
        pass

    @staticmethod
    def configure_proxyarp(node, data):
        """Configure the proxyARP feature and check the return code.

        :param node: Honeycomb node.
        :param data: Configuration to use.
        :type node: dict
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response to PUT is not
            200 = OK or 201 = ACCEPTED.
        """

        data = {
            "proxy-ranges": {
                "proxy-range": [
                    data,
                ]
            }
        }

        status_code, resp = HcUtil.\
            put_honeycomb_data(node, "config_proxyarp_ranges", data,
                               data_representation=DataRepresentation.JSON)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "proxyARP configuration unsuccessful. "
                "Status code: {0}.".format(status_code))
        else:
            return resp

    @staticmethod
    def remove_proxyarp_configuration(node):
        """Delete the proxyARP node, removing all of its configuration.

        :param node: Honeycomb node.
        :type node: dict
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response is not 200 = OK.
        """

        status_code, resp = HcUtil. \
            delete_honeycomb_data(node, "config_proxyarp_ranges")

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "proxyARP removal unsuccessful. "
                "Status code: {0}.".format(status_code))
        else:
            return resp

    @staticmethod
    def get_proxyarp_operational_data(node):
        """Retrieve proxyARP properties from Honeycomb operational data.
        Note: The proxyARP feature has no operational data available.

        :param node: Honeycomb node.
        :type node: dict
        :returns: proxyARP operational data.
        :rtype: bytearray
        """

        raise NotImplementedError("Not supported in VPP.")

    @staticmethod
    def set_proxyarp_interface_config(node, interface, state):
        """Enable or disable the proxyARP feature on the specified interface.

        :param node: Honeycomb node.
        :param interface: Name or sw_if_index of an interface on the node.
        :param state: Desired proxyARP state: enable, disable.
        :type node: dict
        :type interface: str
        :type state: str
        :raises ValueError: If the state argument is incorrect.
        :raises HoneycombError: If the status code in response is not
            200 = OK or 201 = ACCEPTED.
        """

        interface = Topology.convert_interface_reference(
            node, interface, "name")
        interface = interface.replace("/", "%2F")

        path = "/interface/{0}/proxy-arp".format(interface)

        if state == "disable":
            status_code, _ = HcUtil.delete_honeycomb_data(
                node, "config_vpp_interfaces", path)
        elif state == "enable":
            data = {"proxy-arp": {}}
            status_code, _ = HcUtil.put_honeycomb_data(
                node, "config_vpp_interfaces", data, path)
        else:
            raise ValueError("State argument has to be enable or disable.")

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "Interface proxyARP configuration on node {0} was not"
                " successful.".format(node["host"]))

    @staticmethod
    def get_proxyarp_interface_assignment(node, interface):
        """Read the status of proxyARP feature on the specified interface.
        Note: The proxyARP feature has no operational data available.

        :param node: Honeycomb node.
        :param interface: Name or sw_if_index of an interface on the node.
        :type node: dict
        :type interface: str
        :returns: Content of response.
        :rtype: bytearray
        """

        raise NotImplementedError("Not supported in VPP.")


class IPv6NDProxyKeywords(object):
    """Keywords for IPv6 Neighbor Discovery proxy configuration."""

    def __init__(self):
        pass

    @staticmethod
    def configure_ipv6nd(node, interface, addresses=None):
        """Configure IPv6 Neighbor Discovery proxy on the specified interface,
        or remove/replace an existing configuration.

        :param node: Honeycomb node.
        :param interface: Name of an interface on the node.
        :param addresses: IPv6 addresses to configure ND proxy with. If no
            address is provided, ND proxy configuration will be removed.
        :type node: dict
        :type interface: str
        :type addresses: list
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the operation fails.
        """

        interface = Topology.convert_interface_reference(
            node, interface, "name")
        interface = interface.replace("/", "%2F")

        path = "/interface/{0}/ietf-ip:ipv6/nd-proxies".format(interface)

        if addresses is None:
            status_code, resp = HcUtil. \
                delete_honeycomb_data(node, "config_vpp_interfaces", path)
        else:
            data = {
                "nd-proxies": {
                    "nd-proxy": [{"address": x} for x in addresses]
                }
            }

            status_code, resp = HcUtil. \
                put_honeycomb_data(node, "config_vpp_interfaces", data, path,
                                   data_representation=DataRepresentation.JSON)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "IPv6 ND proxy configuration unsuccessful. "
                "Status code: {0}.".format(status_code))
        else:
            return resp

    @staticmethod
    def get_ipv6nd_configuration(node, interface):
        """Read IPv6 Neighbor Discovery proxy configuration on the specified
        interface.

        :param node: Honeycomb node.
        :param interface: Name of an interface on the node.
        :type node: dict
        :type interface: str
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the configuration could not be read.
        """

        interface = Topology.convert_interface_reference(
            node, interface, "name")
        interface = interface.replace("/", "%2F")

        path = "/interface/{0}/ietf-ip:ipv6/nd-proxies".format(interface)

        status_code, resp = HcUtil.get_honeycomb_data(
            node, "config_vpp_interfaces", path)
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Could not read IPv6 ND proxy configuration. "
                "Status code: {0}.".format(status_code))
        else:
            return resp
