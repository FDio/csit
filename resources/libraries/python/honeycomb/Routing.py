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

"""This module implements keywords to manipulate routing tables using
Honeycomb REST API."""

from robot.api import logger

from resources.libraries.python.topology import Topology
from resources.libraries.python.HTTPRequest import HTTPCodes
from resources.libraries.python.honeycomb.HoneycombSetup import HoneycombError
from resources.libraries.python.honeycomb.HoneycombUtil \
    import HoneycombUtil as HcUtil
from resources.libraries.python.honeycomb.HoneycombUtil \
    import DataRepresentation
from resources.libraries.python.VatExecutor import VatTerminal


class RoutingKeywords(object):
    """Implementation of keywords which make it possible to:
    - add/remove routing tables,
    - add/remove routing table entries
    - get operational data about routing tables,
    """

    def __init__(self):
        pass

    @staticmethod
    def _set_routing_table_properties(node, path, data=None):
        """Set routing table properties and check the return code.

        :param node: Honeycomb node.
        :param path: Path which is added to the base path to identify the data.
        :param data: The new data to be set. If None, the item will be removed.
        :type node: dict
        :type path: str
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response is not
        200 = OK.
        """

        if data:
            status_code, resp = HcUtil.\
                put_honeycomb_data(node, "config_routing_table", data, path,
                                   data_representation=DataRepresentation.JSON)
        else:
            status_code, resp = HcUtil.\
                delete_honeycomb_data(node, "config_routing_table", path)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            if data is None and '"error-tag":"data-missing"' in resp:
                logger.debug("data does not exist in path.")
            else:
                raise HoneycombError(
                    "The configuration of routing table was not successful. "
                    "Status code: {0}.".format(status_code))
        return resp

    @staticmethod
    def configure_routing_table(node, name, ip_version, data, vrf=1,
                                special=False):
        """Configure a routing table according to the data provided.

        :param node: Honeycomb node.
        :param name: Name for the table.
        :param ip_version: IP protocol version, ipv4 or ipv6.
        :param data: Route configuration that should be set.
        :param vrf: vrf-id to attach configuration to.
        :param special: Must be True if the configuration is a special route.
        :type node: dict
        :type name: str
        :type ip_version: str
        :type data: dict
        :type vrf: int
        :type special: bool
        :returns: Content of response.
        :rtype: bytearray
        """
        if special:
            ip_version = "hc2vpp-ietf-{0}-unicast-routing:{0}".format(
                ip_version)
            protocol = "vpp-routing:vpp-protocol-attributes"
        else:
            ip_version = ip_version
            protocol = "vpp-protocol-attributes"

        full_data = {
            "control-plane-protocol": [
                {
                    "name": name,
                    "description": "hc2vpp-csit test route",
                    "type": "static",
                    protocol: {
                        "primary-vrf": vrf
                    },
                    "static-routes": {
                        ip_version: {
                            "route": data
                        }
                    }
                }
            ]
        }

        path = "/control-plane-protocol/hc2vpp-ietf-routing:static/{0}".format(name)
        return RoutingKeywords._set_routing_table_properties(
            node, path, full_data)

    @staticmethod
    def delete_routing_table(node, name):
        """Delete the specified routing table from configuration data.

        :param node: Honeycomb node.
        :param name: Name of the table.
        :type node: dict
        :type name: str
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/control-plane-protocol/hc2vpp-ietf-routing:static/{0}".format(name)
        return RoutingKeywords._set_routing_table_properties(node, path)

    @staticmethod
    def get_routing_table_oper(node, name, ip_version):
        """Retrieve operational data about the specified routing table.

        :param node: Honeycomb node.
        :param name: Name of the routing table.
        :param ip_version: IP protocol version, ipv4 or ipv6.
        :type node: dict
        :type name: str
        :type ip_version: str
        :returns: Routing table operational data.
        :rtype: list
        :raises HoneycombError: If the operation fails.
        """

        path = "/control-plane-protocol/hc2vpp-ietf-routing:static/{0}".format(name)
        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "oper_routing_table", path)

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get operational information about the "
                "routing tables. Status code: {0}.".format(status_code))

        data = RoutingKeywords.clean_routing_oper_data(
            resp['control-plane-protocol'][0]['static-routes']
            ['hc2vpp-ietf-{0}-unicast-routing:{0}'.format(ip_version)]['route'])

        return data

    @staticmethod
    def clean_routing_oper_data(data):
        """Prepare received routing operational data to be verified against
         expected data.

        :param data: Routing operational data.
        :type data: list
        :returns: Routing operational data without entry ID numbers.
        :rtype: list
        """

        for item in data:
            # ID values are auto-incremented based on existing routes in VPP
            item.pop("id", None)
            if "next-hop-list" in item.keys():
                for item2 in item["next-hop-list"]["next-hop"]:
                    item2.pop("id", None)

            if "next-hop-list" in item.keys():
                # List items come in random order
                item["next-hop-list"]["next-hop"].sort()

        return data

    @staticmethod
    def log_routing_configuration(node):
        """Retrieve route configuration using VAT and print the response
         to robot log.

         :param node: VPP node.
         :type node: dict
         """

        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd("ip_fib_dump")

    @staticmethod
    def configure_interface_slaac(node, interface, slaac_data=None):
        """Configure SLAAC on the specified interfaces.

        :param node: Honeycomb node.
        :param interface: Interface to configure SLAAC.
        :param slaac_data: Dictionary of configurations to apply. \
        If it is None then the existing configuration is removed.
        :type node: dict
        :type interface: str
        :type slaac_data: dict of dicts
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If RA could not be configured.
        """

        interface = Topology.convert_interface_reference(
            node, interface, 'name')
        interface_orig = interface
        interface = interface.replace('/', '%2F')
        path = 'interface/' + interface

        if not slaac_data:
            status_code, _ = HcUtil.delete_honeycomb_data(
                node, 'config_slaac', path)
        else:
            data = {
                'interface': [
                    {
                        'name': interface_orig,
                        'ipv6-router-advertisements': slaac_data
                    }
                ]
            }

            status_code, _ = HcUtil.put_honeycomb_data(
                node, 'config_slaac', data, path)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                'Configuring SLAAC failed. Status code:{0}'.format(status_code))

    @staticmethod
    def get_interface_slaac_oper_data(node, interface):
        """Get operational data about SLAAC table present on the node.

        :param node: Honeycomb node.
        :param interface: Interface SLAAC data are retrieved from.
        :type node: dict
        :type interface: str
        :returns: dict of SLAAC operational data.
        :rtype: dict
        :raises HoneycombError: If status code differs from successful.
        """
        interface = Topology.convert_interface_reference(
            node, interface, 'name')
        interface = interface.replace('/', '%2F')
        path = 'interface/' + interface

        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "config_slaac", path)

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get operational information about SLAAC. "
                "Status code: {0}.".format(status_code))
        try:
            dict_of_str = resp['interface'][0][
                'hc2vpp-ietf-ipv6-unicast-routing:ipv6-router-advertisements']
            return {k: str(v) for k, v in dict_of_str.items()}
        except (KeyError, TypeError):
            return {}

    @staticmethod
    def configure_policer(node, policy_name, policer_data=None):
        """Configure Policer on the specified node.

        :param node: Honeycomb node.
        :param policer_data: Dictionary of configurations to apply. \
        If it is None then the existing configuration is removed.
        :type node: dict
        :type policer_data: dict
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If policer could not be configured.
        """

        path = '/' + policy_name

        if not policer_data:
            status_code, _ = HcUtil.delete_honeycomb_data(
                node, 'config_policer', path)
        else:
            data = {
                'policer': policer_data
            }

            status_code, _ = HcUtil.put_honeycomb_data(
                node, 'config_policer', data, path)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                'Configuring policer failed. Status code:{0}'\
                    .format(status_code))

    @staticmethod
    def get_policer_oper_data(node, policy_name):
        """Get operational data about Policer on the node.

        :param node: Honeycomb node.
        :type node: dict
        :returns: dict of Policer operational data.
        :rtype: dict
        :raises HoneycombError: If status code differs from successful.
        """

        path = '/' + policy_name

        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "oper_policer", path)

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get operational information about Policer. "
                "Status code: {0}.".format(status_code))
        try:
            return resp['policer']
        except (KeyError, TypeError):
            return {}
