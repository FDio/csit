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

"""This module implements keywords to manipulate LISP data structures using
Honeycomb REST API."""

from resources.libraries.python.HTTPRequest import HTTPCodes
from resources.libraries.python.honeycomb.HoneycombSetup import HoneycombError
from resources.libraries.python.honeycomb.HoneycombUtil \
    import HoneycombUtil as HcUtil
from resources.libraries.python.honeycomb.HoneycombUtil \
    import DataRepresentation
from resources.libraries.python.topology import Topology


class LispKeywords(object):
    """Implementation of keywords which make it possible to:
    - enable/disable LISP feature
    - configure LISP mappings
    - configure locator sets
    - configure map resolver
    - configure LISP PITR feature
    - read operational data for all of the above
    """

    def __init__(self):
        """Initializer."""
        pass

    @staticmethod
    def _set_lisp_properties(node, path, data=None):
        """Set LISP properties and check the return code.

        :param node: Honeycomb node.
        :param path: Path which is added to the base path to identify the data.
        :param data: The new data to be set. If None, the item will be removed.
        :type node: dict
        :type path: str
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response to PUT is not
            200 = OK or 201 = ACCEPTED.
        """

        if data:
            status_code, resp = HcUtil.\
                put_honeycomb_data(node, "config_lisp", data, path,
                                   data_representation=DataRepresentation.JSON)
        else:
            status_code, resp = HcUtil.\
                delete_honeycomb_data(node, "config_lisp", path)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "Lisp configuration unsuccessful. "
                "Status code: {0}.".format(status_code))
        else:
            return resp

    @staticmethod
    def get_lisp_operational_data(node):
        """Retrieve Lisp properties from Honeycomb operational data.

        :param node: Honeycomb node.
        :type node: dict
        :returns: List operational data.
        :rtype: bytearray
        """

        status_code, resp = HcUtil.get_honeycomb_data(node, "oper_lisp")

        if status_code != HTTPCodes.OK:
            raise HoneycombError("Could not retrieve LISP operational data."
                                 "Status code: {0}.".format(status_code))
        else:
            # get rid of empty vni-table entry
            resp["lisp-state"]["lisp-feature-data"]["eid-table"][
                "vni-table"].remove(
                    {
                        "virtual-network-identifier": 0,
                        "vrf-subtable": {"table-id": 0}
                    }
                )
            return resp

    @staticmethod
    def verify_map_server_data_from_honeycomb(data, ip_addresses):
        """Verify whether MAP server data from Honeycomb is correct.

        :param data: LISP operational data containing map server IP addresses.
        :param ip_addresses: IP addresses to verify map server data against.
        :type data: dict
        :type ip_addresses: list
        :returns: Boolean Value indicating equality of IP Lists.
        :rtype: bool
        """

        data =\
            data['lisp-state']['lisp-feature-data']['map-servers']['map-server']

        data = sorted([entry['ip-address'] for entry in data])
        ip_addresses.sort()

        return data == ip_addresses

    @staticmethod
    def verify_map_server_data_from_vat(data, ip_addresses):
        """Verify whether MAP server data from VAT is correct.

        :param data: LISP operational data containing map server IP addresses.
        :param ip_addresses: IP addresses to verify map server data against.
        :type data: dict
        :type ip_addresses: list
        :returns: Boolean Value indicating equality of IP Lists.
        :rtype: bool
        """

        data = sorted([entry['map-server'] for entry in data])
        ip_addresses.sort()

        return data == ip_addresses

    @staticmethod
    def set_lisp_state(node, state=True):
        """Enable or disable the LISP feature.

        :param node: Honeycomb node.
        :param state: Enable or disable LISP.
        :type node: dict
        :type state: bool
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the return code is not 200:OK
            or 404:NOT FOUND.
        """

        ret_code, data = HcUtil.get_honeycomb_data(node, "config_lisp")
        if ret_code == HTTPCodes.OK:
            data["lisp"]["enable"] = bool(state)
        elif ret_code == HTTPCodes.NOT_FOUND:
            data = {"lisp": {"enable": bool(state)}}
        else:
            raise HoneycombError("Unexpected return code when getting existing"
                                 " LISP configuration.")

        return LispKeywords._set_lisp_properties(node, '', data)

    @staticmethod
    def set_rloc_probe_state(node, state=False):
        """Enable or disable the Routing Locator probe.

        :param node: Honeycomb node.
        :param state: Enable or Disable the Rloc probe.
        :type node: dict
        :type state: bool
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/lisp-feature-data/rloc-probe"

        data = {
            "rloc-probe": {
                "enabled": bool(state)
            }
        }

        return LispKeywords._set_lisp_properties(node, path, data)

    @staticmethod
    def add_locator(node, interface, locator_set, priority=1, weight=1):
        """Configure a new LISP locator set.

        :param node: Honeycomb node.
        :param interface: An interface on the node.
        :param locator_set: Name for the new locator set.
        :param priority: Priority parameter for the locator.
        :param weight: Weight parameter for the locator.
        :type node: dict
        :type interface: str
        :type locator_set: str
        :type priority: int
        :type weight: int
        :returns: Content of response.
        :rtype: bytearray
        """

        interface = Topology.convert_interface_reference(
            node, interface, "name")

        path = "/lisp-feature-data/locator-sets/locator-set" \
               "/{0}".format(locator_set)

        data = {
            "locator-set": {
                "name": locator_set,
                "interface": {
                    "interface-ref": interface,
                    "priority": priority,
                    "weight": weight
                }
            }
        }

        return LispKeywords._set_lisp_properties(node, path, data)

    @staticmethod
    def configure_lisp_mapping(node, data):
        """Modify eid-table configuration to the data provided.

        :param node: Honeycomb node.
        :param data: Settings for the LISP mappings.
        :type node: dict
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/lisp-feature-data/eid-table"
        return LispKeywords._set_lisp_properties(node, path, data)

    @staticmethod
    def configure_lisp_map_request_mode(node, option):
        """Modify LISP Map Request Mode configuration to the data provided.

        :param node: Honeycomb node.
        :param option: Settings for the LISP map request mode.
        :type node: dict
        :type option: str
        :returns: Content of response.
        :rtype: bytearray
        """

        data = {
            "map-request-mode": {
                "mode": option
            }
        }

        path = "/lisp-feature-data/map-request-mode"
        return LispKeywords._set_lisp_properties(node, path, data)

    @staticmethod
    def add_lisp_adjacency(node, vni_id, map_name, adjacency_name, data):
        """Add an adjacency to an existing LISP mapping.

        :param node: Honeycomb node.
        :param vni_id: vni_id of the mapping.
        :param map_name: Name of the mapping.
        :param adjacency_name: Name for the new adjacency.
        :param data: Adjacency settings.
        :type node: dict
        :type vni_id: int
        :type map_name: str
        :type adjacency_name: str
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        """

        path = (
            "/lisp-feature-data/eid-table/vni-table/{vni_id}/"
            "vrf-subtable/remote-mappings/remote-mapping/{map_name}/"
            "adjacencies/adjacency/{adjacency_name}"
        )
        path = path.format(
            vni_id=vni_id,
            map_name=map_name,
            adjacency_name=adjacency_name
        )

        return LispKeywords._set_lisp_properties(node, path, data)

    @staticmethod
    def add_map_resolver(node, ip_address):
        """Configure map resolver with the specified IP address.

        :param node: Honeycomb node.
        :param ip_address: IP address to configure map resolver with.
        :type node: dict
        :type ip_address: str
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/lisp-feature-data/map-resolvers/map-resolver/{0}".format(
            ip_address)

        data = {
            "map-resolver": {
                "ip-address": ip_address
            }
        }

        return LispKeywords._set_lisp_properties(node, path, data)

    @staticmethod
    def set_map_register(node, map_register=False):
        """Configure Map Register.

        :param node: Honeycomb node.
        :param map_register: Enable or disable Map Register.
        :type node: dict
        :type map_register: bool
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/lisp-feature-data/map-register"

        data = {
            "map-register": {
                "enabled": bool(map_register)
            }
        }

        return LispKeywords._set_lisp_properties(node, path, data)

    @staticmethod
    def set_map_request_mode(node, src_dst=False):
        """Configure Map Request Mode.

        :param node: Honeycomb node.
        :param src_dst: Configure Map Request Mode with source destination.
        :type node: dict
        :type src_dst: bool
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/lisp-feature-data/map-request-mode"

        data = {
            "map-request-mode": {
                "mode": "source-destination" if src_dst
                        else "target-destination"
            }
        }

        return LispKeywords._set_lisp_properties(node, path, data)

    @staticmethod
    def delete_map_resolver(node):
        """Delete an existing map resolver.

        :param node: Honeycomb node
        :type node: dict
        :returns: Content of response
        :rtype: bytearray
        """

        path = "/lisp-feature-data/map-resolvers"

        return LispKeywords._set_lisp_properties(node, path)

    @staticmethod
    def add_map_server(node, *ip_addresses):
        """Configure map server with the specified IP addresses.

        :param node: Honeycomb node.
        :param ip_addresses: IP addresses to configure map server with.
        :type node: dict
        :type ip_addresses: list
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/lisp-feature-data/map-servers"

        data = {
            "map-servers": {
                "map-server": [
                    {"ip-address": ip_address} for ip_address in ip_addresses
                ]
            }
        }

        return LispKeywords._set_lisp_properties(node, path, data)

    @staticmethod
    def delete_map_server(node):
        """Delete all map servers.

        :param node: Honeycomb node
        :type node: dict
        :returns: Content of response
        :rtype: bytearray
        """

        path = "/lisp-feature-data/map-servers"

        return LispKeywords._set_lisp_properties(node, path)

    @staticmethod
    def configure_pitr(node, locator_set=None):
        """Configure PITR feature with the specified locator set. If not locator
        set is specified, disable PITR instead.

        :param node: Honeycomb node.
        :param locator_set: Name of a locator set. Optional.
        :type node: dict
        :type locator_set: str
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/lisp-feature-data/pitr-cfg"

        if locator_set:
            data = {
                "pitr-cfg": {
                    "locator-set": locator_set
                }
            }
        else:
            data = None

        return LispKeywords._set_lisp_properties(node, path, data)

    @staticmethod
    def configure_petr(node, ip_address):
        """Configure PETR feature with the specified IP. If no IP
        specified, disable PETR instead.

        :param node: Honeycomb node.
        :param ip_address: IPv6 address.
        :type node: dict
        :type ip_address: str
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/lisp-feature-data/petr-cfg"

        if ip_address:
            data = {
                "petr-cfg": {
                    "petr-address": ip_address
                }
            }
        else:
            data = None

        return LispKeywords._set_lisp_properties(node, path, data)

    @staticmethod
    def disable_lisp(node):
        """Remove all LISP settings on the node.

        :param node: Honeycomb node.
        :type node: dict
        :returns: Content of response.
        :rtype: bytearray
        """

        return LispKeywords._set_lisp_properties(node, "")


class LispGPEKeywords(object):
    """Implementation of keywords which make it possible to:
    - enable/disable LISP GPE feature
    - configure LISP GPE forwarding entries
    - read operational data for all of the above
    """

    def __init__(self):
        """Initializer."""
        pass

    @staticmethod
    def _set_lispgpe_properties(node, path, data=None):
        """Set LISP GPE properties and check the return code.

        :param node: Honeycomb node.
        :param path: Path which is added to the base path to identify the data.
        :param data: The new data to be set. If None, the item will be removed.
        :type node: dict
        :type path: str
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response to PUT is not
            200 = OK or 201 = ACCEPTED.
        """

        if data:
            status_code, resp = HcUtil.\
                put_honeycomb_data(node, "config_lisp_gpe", data, path,
                                   data_representation=DataRepresentation.JSON)
        else:
            status_code, resp = HcUtil.\
                delete_honeycomb_data(node, "config_lisp_gpe", path)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "Lisp GPE configuration unsuccessful. "
                "Status code: {0}.".format(status_code))
        else:
            return resp

    @staticmethod
    def get_lispgpe_operational_data(node):
        """Retrieve LISP GPE properties from Honeycomb operational data.

        :param node: Honeycomb node.
        :type node: dict
        :returns: LISP GPE operational data.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response to GET is not
            200 = OK.
        """

        status_code, resp = HcUtil.get_honeycomb_data(node, "oper_lisp_gpe")

        if status_code != HTTPCodes.OK:
            raise HoneycombError("Could not retrieve Lisp GPE operational data."
                                 "Status code: {0}.".format(status_code))
        else:
            return resp

    @staticmethod
    def get_lispgpe_mapping(node, name):
        """Retrieve LISP GPE operational data and parse for a specific mapping.

        :param node: Honeycomb node.
        :param name: Name of the mapping to look for.
        :type node: dict
        :type name: str
        :returns: LISP GPE mapping.
        :rtype: dict
        :raises HoneycombError: If the mapping is not present in operational
            data.
        """

        data = LispGPEKeywords.get_lispgpe_operational_data(node)
        try:
            data = data["gpe-state"]["gpe-feature-data"]["gpe-entry-table"] \
                ["gpe-entry"]
        except KeyError:
            raise HoneycombError("No mappings present in operational data.")
        for item in data:
            if item["id"] == name:
                mapping = item
                break
        else:
            raise HoneycombError("Mapping with name {name} not found in "
                                 "operational data.".format(name=name))

        return mapping

    @staticmethod
    def get_lispgpe_config_data(node):
        """Retrieve LISP GPE properties from Honeycomb config data.

        :param node: Honeycomb node.
        :type node: dict
        :returns: LISP GPE config data.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response to GET is not
            200 = OK.
        """

        status_code, resp = HcUtil.get_honeycomb_data(node, "config_lisp_gpe")

        if status_code != HTTPCodes.OK:
            raise HoneycombError("Could not retrieve Lisp GPE config data."
                                 "Status code: {0}.".format(status_code))
        else:
            return resp

    @staticmethod
    def set_lispgpe_state(node, state=True):
        """Enable or disable the LISP GPE feature.

        :param node: Honeycomb node.
        :param state: Enable or disable LISP.
        :type node: dict
        :type state: bool
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the return code is not 200:OK
            or 404:NOT FOUND.
        """

        ret_code, data = HcUtil.get_honeycomb_data(node, "config_lisp_gpe")
        if ret_code == HTTPCodes.OK:
            data["gpe"]["gpe-feature-data"]["enable"] = bool(state)
        elif ret_code == HTTPCodes.NOT_FOUND:
            data = {"gpe": {"gpe-feature-data": {"enable": bool(state)}}}
        else:
            raise HoneycombError("Unexpected return code when getting existing"
                                 " Lisp GPE configuration.")

        return LispGPEKeywords._set_lispgpe_properties(node, '', data)

    @staticmethod
    def configure_lispgpe_mapping(node, data=None):
        """Modify LISP GPE mapping configuration to the data provided.

        :param node: Honeycomb node.
        :param data: Settings for the LISP GPE mappings.
        :type node: dict
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/gpe-feature-data/gpe-entry-table"
        if data:
            data = {"gpe-entry-table": {"gpe-entry": data}}
            return LispGPEKeywords._set_lispgpe_properties(node, path, data)
        else:
            return LispGPEKeywords._set_lispgpe_properties(node, path)

    @staticmethod
    def add_lispgpe_mapping(node, name, data):
        """Add the specified LISP GPE mapping.

        :param node: Honeycomb node.
        :param name: Name for the mapping.
        :param data: Mapping details.
        :type node: dict
        :type name: str
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/gpe-feature-data/gpe-entry-table/gpe-entry/{name}".format(
            name=name)

        data = {"gpe-entry": data}
        return LispGPEKeywords._set_lispgpe_properties(node, path, data)

    @staticmethod
    def delete_lispgpe_mapping(node, mapping):
        """Delete the specified LISP GPE mapping from configuration.

        :param node: Honeycomb node.
        :param mapping: Name of the mapping to remove.
        :type node: dict
        :type mapping: str
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/gpe-feature-data/gpe-entry-table/gpe-entry/{0}".format(mapping)
        return LispGPEKeywords._set_lispgpe_properties(node, path)

    @staticmethod
    def disable_lispgpe(node):
        """Remove all LISP GPE settings on the node.

        :param node: Honeycomb node.
        :type node: dict
        :returns: Content of response.
        :rtype: bytearray
        """

        return LispGPEKeywords._set_lispgpe_properties(node, "")
