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

"""This module implements keywords to manipulate ACL data structures using
Honeycomb REST API."""

from resources.libraries.python.topology import Topology
from resources.libraries.python.HTTPRequest import HTTPCodes
from resources.libraries.python.honeycomb.HoneycombSetup import HoneycombError
from resources.libraries.python.honeycomb.HoneycombUtil \
    import HoneycombUtil as HcUtil
from resources.libraries.python.honeycomb.HoneycombUtil \
    import DataRepresentation


class ACLKeywords(object):
    """Implementation of keywords which make it possible to:
    - add classify table(s),
    - remove classify table(s),
    - get operational data about classify table(s),
    - add classify session(s),
    - remove classify session(s),
    - get operational data about classify sessions(s).
    """

    def __init__(self):
        pass

    @staticmethod
    def _set_classify_table_properties(node, path, data=None):
        """Set classify table properties and check the return code.

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
                put_honeycomb_data(node, "config_classify_table", data, path,
                                   data_representation=DataRepresentation.JSON)
        else:
            status_code, resp = HcUtil.\
                delete_honeycomb_data(node, "config_classify_table", path)

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "The configuration of classify table was not successful. "
                "Status code: {0}.".format(status_code))
        return resp

    @staticmethod
    def add_classify_table(node, table):
        """Add a classify table to the list of classify tables. The keyword does
        not validate given data.

        :param node: Honeycomb node.
        :param table: Classify table to be added.
        :type node: dict
        :type table: dict
        :return: Content of response.
        :rtype: bytearray
        """

        path = "/classify-table/" + table["name"]
        data = {"classify-table": [table, ]}
        return ACLKeywords._set_classify_table_properties(node, path, data)

    @staticmethod
    def remove_all_classify_tables(node):
        """Remove all classify tables defined on the node.

        :param node: Honeycomb node.
        :type node: dict
        :return: Content of response.
        :rtype: bytearray
        """

        return ACLKeywords._set_classify_table_properties(node, path="")

    @staticmethod
    def remove_classify_table(node, table_name):
        """Remove the given classify table.

        :param node: Honeycomb node.
        :param table_name: Name of the classify table to be removed.
        :type node: dict
        :type table_name: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = "/classify-table/" + table_name
        return ACLKeywords._set_classify_table_properties(node, path)

    @staticmethod
    def get_all_classify_tables_oper_data(node):
        """Get operational data about all classify tables present on the node.

        :param node: Honeycomb node.
        :type node: dict
        :return: List of classify tables.
        :rtype: list
        """

        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "oper_classify_table")

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get operational information about the "
                "classify tables. Status code: {0}.".format(status_code))
        try:
            return resp["vpp-classifier"]["classify-table"]
        except (KeyError, TypeError):
            return []

    @staticmethod
    def get_classify_table_oper_data(node, table_name):
        """Get operational data about the given classify table.

        :param node: Honeycomb node.
        :param table_name: Name of the classify table.
        :type node: dict
        :type table_name: str
        :return: Operational data about the given classify table.
        :rtype: dict
        """

        path = "/classify-table/" + table_name
        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "oper_classify_table", path)

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get operational information about the "
                "classify tables. Status code: {0}.".format(status_code))
        try:
            return resp["classify-table"][0]
        except (KeyError, TypeError):
            return []

    @staticmethod
    def get_all_classify_tables_cfg_data(node):
        """Get configuration data about all classify tables present on the node.

        :param node: Honeycomb node.
        :type node: dict
        :return: List of classify tables.
        :rtype: list
        """

        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "config_classify_table")

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get operational information about the "
                "classify tables. Status code: {0}.".format(status_code))
        try:
            return resp["vpp-classifier"]["classify-table"]
        except (KeyError, TypeError):
            return []

    @staticmethod
    def add_classify_session(node, table_name, session):
        """Add a classify session to the classify table.

        :param node: Honeycomb node.
        :param table_name: Name of the classify table.
        :param session: Classify session to be added to the classify table.
        :type node: dict
        :type table_name: str
        :type session: dict
        :return: Content of response.
        :rtype: bytearray
        """

        path = "/classify-table/" + table_name + \
               "/classify-session/" + session["match"]
        data = {"classify-session": [session, ]}
        return ACLKeywords._set_classify_table_properties(node, path, data)

    @staticmethod
    def remove_classify_session(node, table_name, session_match):
        """Remove the given classify session from the classify table.

        :param node: Honeycomb node.
        :param table_name: Name of the classify table.
        :param session_match: Classify session match.
        :type node: dict
        :type table_name: str
        :type session_match: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = "/classify-table/" + table_name + \
               "/classify-session/" + session_match
        return ACLKeywords._set_classify_table_properties(node, path)

    @staticmethod
    def get_all_classify_sessions_oper_data(node, table_name):
        """Get operational data about all classify sessions in the classify
        table.

        :param node: Honeycomb node.
        :param table_name: Name of the classify table.
        :type node: dict
        :type table_name: str
        :return: List of classify sessions present in the classify table.
        :rtype: list
        """

        table_data = ACLKeywords.get_classify_table_oper_data(node, table_name)
        try:
            return table_data["classify-table"][0]["classify-session"]
        except (KeyError, TypeError):
            return []

    @staticmethod
    def get_classify_session_oper_data(node, table_name, session_match):
        """Get operational data about the given classify session in the classify
        table.

        :param node: Honeycomb node.
        :param table_name: Name of the classify table.
        :param session_match: Classify session match.
        :type node: dict
        :type table_name: str
        :type session_match: str
        :return: Classify session operational data.
        :rtype: dict
        """

        path = "/classify-table/" + table_name + \
               "/classify-session/" + session_match
        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "oper_classify_table", path)

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get operational information about the "
                "classify tables. Status code: {0}.".format(status_code))
        try:
            return resp["classify-session"][0]
        except (KeyError, TypeError):
            return {}

    @staticmethod
    def create_ietf_classify_chain(node, list_name, layer, data):
        """Create classify chain using the ietf-acl node.

        :param node: Honeycomb node.
        :param list_name: Name for the classify list.
        :param layer: Network layer to classify on.
        :param data: Dictionary of settings to send to Honeycomb.
        :type node: dict
        :type list_name: str
        :type layer: string
        :type data: dict

        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the operation fails.
        """
        if layer.lower() == "l2":
            suffix = "eth"
        elif layer.lower() in ("l3_ip4", "l3_ip6", "l4"):
            raise NotImplementedError
        else:
            raise ValueError("Unexpected value of layer argument {0}."
                             "Valid options are: L2, L3_IP4, L3_IP6, L4."
                             .format(layer))

        path = "/acl/ietf-access-control-list:{0}-acl/{1}".format(
            suffix, list_name)

        status_code, resp = HcUtil.put_honeycomb_data(
            node, "config_ietf_classify_chain", data, path)

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Could not create classify chain."
                "Status code: {0}.".format(status_code))

        return resp

    @staticmethod
    def set_ietf_interface_acl(node, interface, layer, direction, list_name,
                               default_action):
        """Assign an interface to an ietf-acl classify chain.

        :param node: Honeycomb node.
        :param interface: Name of an interface on the node.
        :param layer: Network layer to classify packets on.
        Valid options are: L2, L3, L4. Mixed ACL not supported yet.
        :param direction: Classify incoming or outgiong packets.
        Valid options are: ingress, egress
        :param list_name: Name of an ietf-acl classify chain.
        :param default_action: Default classifier action: permit or deny.
        :type node: dict
        :type interface: str or int
        :type layer: str
        :type direction: str
        :type list_name: str
        :type default_action: str

        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the operation fails.
        """

        interface = Topology.convert_interface_reference(
            node, interface, "name")

        interface = interface.replace("/", "%2F")

        if direction not in ("ingress", "egress"):
            raise ValueError("Unknown traffic direction {0}. "
                             "Valid options are: ingress, egress."
                             .format(direction))

        path = "/interface/{0}/ietf-acl/{1}/access-lists".format(
            interface, direction)

        data = {
                "access-lists": {
                    "acl": [{
                        "type": None,
                        "name": list_name
                    }],
                    "default-action": default_action,
                    "mode": None
                    }
                }

        acl_type = "ietf-access-control-list:{suffix}-acl"

        if layer.lower() == "l2":
            data["access-lists"]["mode"] = "l2"
            data["access-lists"]["acl"][0]["type"] = \
                acl_type.format(suffix="eth")

        elif layer.lower() in ("l3_ip4", "l3_ip6", "L4"):
            raise NotImplementedError
        else:
            raise ValueError("Unknown network layer {0}. "
                             "Valid options are: "
                             "L2, L3_IP4, L3_IP6, L4.".format(layer))

        status_code, resp = HcUtil.put_honeycomb_data(
            node, "config_vpp_interfaces", data, path)

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Could not configure ACL on interface. "
                "Status code: {0}.".format(status_code))

        return resp

    @staticmethod
    def delete_ietf_interface_acls(node, interface):
        """Remove all ietf-acl assignments from an interface.

        :param node: Honeycomb node.
        :param interface: Name of an interface on the node.
        :type node: dict
        :type interface: str or int"""

        interface = Topology.convert_interface_reference(
            node, interface, "name")

        interface = interface.replace("/", "%2F")

        path = "/interface/{0}/ietf-acl/".format(interface)
        status_code, _ = HcUtil.delete_honeycomb_data(
            node, "config_vpp_interfaces", path)

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Could not remove ACL assignment from interface. "
                "Status code: {0}.".format(status_code))

    @staticmethod
    def delete_ietf_classify_chains(node):
        """Remove all classify chains from the ietf-acl node.

        :param node: Honeycomb node.
        :type node: dict
        """

        status_code, _ = HcUtil.delete_honeycomb_data(
            node, "config_ietf_classify_chain")

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Could not remove ietf-acl chain. "
                "Status code: {0}.".format(status_code))
