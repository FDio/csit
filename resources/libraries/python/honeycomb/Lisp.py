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

"""This module implements keywords to manipulate Lisp data structures using
Honeycomb REST API."""

from resources.libraries.python.HTTPRequest import HTTPCodes
from resources.libraries.python.honeycomb.HoneycombSetup import HoneycombError
from resources.libraries.python.honeycomb.HoneycombUtil \
    import HoneycombUtil as HcUtil
from resources.libraries.python.honeycomb.HoneycombUtil \
    import DataRepresentation


class LispKeywords(object):
    """Implementation of keywords which make it possible to:
    - enable/disable Lisp feature
    -
    -
    -
    """

    def __init__(self):
        """Initializer."""
        pass

    @staticmethod
    def _set_lisp_properties(node, path, data=None):
        """Set Lisp properties and check the return code.

        :param node: Honeycomb node.
        :param path: Path which is added to the base path to identify the data.
        :param data: The new data to be set. If None, the item will be removed.
        :type node: dict
        :type path: str
        :type data: dict
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response to PUT is not
        200 = OK.
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
        :return: List operational data.
        :rtype: bytearray
        """

        status_code, resp = HcUtil.get_honeycomb_data(node, "oper_lisp")

        if status_code != HTTPCodes.OK:
            raise HoneycombError("Could not retrieve Lisp operational data."
                                 "Status code: {0}.".format(status_code))
        else:
            # get rid of empty vni-table entry
            # TODO: remove once the bug is fixed
            resp["lisp-state"]["lisp-feature-data"]["eid-table"][
                "vni-table"].remove(
                {
                    "virtual-network-identifier": 0,
                    "vrf-subtable": {"table-id": 0}
                }
            )
            return resp

    @staticmethod
    def set_lisp_state(node, state):
        """Enable or disable the Lisp feature.

        :param node: Honeycomb node.
        :param state: Desired Lisp state, enable or disable.
        :type node: dict
        :type state: str
        :return: Content of response.
        :rtype: bytearray
        """

        data = {
            "lisp": {
                "enable": True if state.lower() == "enable" else False
            }
        }

        return LispKeywords._set_lisp_properties(node, '', data)

    @staticmethod
    def add_locator(node, interface, locator_set, priority=1, weight=1):
        """Configure a new Lisp locator set.

        :param node: Honeycomb node.
        :param interface: An interface on the node.
        :param locator_set: Name for the new locator set.
        :param priority: Priority parameter for the locator.
        :param weight. Weight parameter for the locator.
        :type node: dict
        :type interface: str
        :type locator_set: str
        :type priority: int
        :type weight: int
        :return: Content of response.
        :rtype: bytearray
        """

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
        :param data: Settings for the Lisp mappings.
        :type node: dict
        :type data: dict
        :return: Content of response.
        :rtype: bytearray
        """

        path = "/lisp-feature-data/eid-table"
        return LispKeywords._set_lisp_properties(node, path, data)

    @staticmethod
    def add_lisp_adjacency(node, vni_id, map_name, adjacency_name, data):
        """Add an adjacency to an existing Lisp mapping.

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
        :return: Content of response.
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
        :return: Content of response.
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
    def delete_map_resolver(node):
        """Delete an existing map resolver.

        :param node: Honeycomb node
        :type node: dict
        :return: Content of response
        :rtype: bytearray
        """

        path = "/lisp-feature-data/map-resolvers"

        return LispKeywords._set_lisp_properties(node, path)

    @staticmethod
    def configure_pitr(node, locator_set=None):
        """Configure PITR feature with the specified locator set. If not locator
        set is specified, disable PITR instead.

        :param node: Honeycomb node.
        :param locator_set: Name of a locator set. Optional.
        :type node: dict
        :type locator_set: str
        :return: Content of response.
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
    def disable_lisp(node):
        """Remove all Lisp settings on the node.

        :param node: Honeycomb node.
        :type node: dict
        :return: Content of response.
        :rtype: bytearray
        """

        #paths = [
            #"/lisp-feature-data/eid-table",
            # "/lisp-feature-data/locator-sets",
            # "/lisp-feature-data/pitr-cfg",
            # "/lisp-feature-data/map-resolvers"
        #]

        #for path in paths:
        #    LispKeywords._set_lisp_properties(node, path)
        return LispKeywords._set_lisp_properties(node, "")
