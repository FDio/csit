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

"""This module implements keywords to manipulate ACL data structures using
Honeycomb REST API."""
from robot.api import logger

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
        :returns: Content of response.
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

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            if data is None and '"error-tag":"data-missing"' in resp:
                logger.debug("data does not exist in path.")
            else:
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
        :returns: Content of response.
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
        :returns: Content of response.
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
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/classify-table/" + table_name
        return ACLKeywords._set_classify_table_properties(node, path)

    @staticmethod
    def get_all_classify_tables_oper_data(node):
        """Get operational data about all classify tables present on the node.

        :param node: Honeycomb node.
        :type node: dict
        :returns: List of classify tables.
        :rtype: list
        """

        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "oper_classify_table")

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get operational information about the "
                "classify tables. Status code: {0}.".format(status_code))

        return resp["vpp-classifier-state"]["classify-table"]

    @staticmethod
    def get_classify_table_oper_data(node, table_name):
        """Get operational data about the given classify table.

        :param node: Honeycomb node.
        :param table_name: Name of the classify table.
        :type node: dict
        :type table_name: str
        :returns: Operational data about the given classify table.
        :rtype: dict
        """

        tables = ACLKeywords.get_all_classify_tables_oper_data(node)
        for table in tables:
            if table["name"] == table_name:
                return table
        raise HoneycombError("Table {0} not found in ACL table list.".format(
            table_name))

    @staticmethod
    def get_all_classify_tables_cfg_data(node):
        """Get configuration data about all classify tables present on the node.

        :param node: Honeycomb node.
        :type node: dict
        :returns: List of classify tables.
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
        :returns: Content of response.
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
        :returns: Content of response.
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
        :returns: List of classify sessions present in the classify table.
        :rtype: list
        """

        table_data = ACLKeywords.get_classify_table_oper_data(node, table_name)

        return table_data["classify-session"]

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
        :returns: Classify session operational data.
        :rtype: dict
        :raises HoneycombError: If no session the specified match Id is found.
        """

        sessions = ACLKeywords.get_all_classify_sessions_oper_data(
            node, table_name)
        for session in sessions:
            if session["match"] == session_match:
                return session
        raise HoneycombError(
            "Session with match value \"{0}\" not found"
            " under ACL table {1}.".format(session_match, table_name))

    @staticmethod
    def create_acl_plugin_classify_chain(node, list_name, data, macip=False):
        """Create classify chain using the ietf-acl node.

        :param node: Honeycomb node.
        :param list_name: Name for the classify list.
        :param data: Dictionary of settings to send to Honeycomb.
        :param macip: Use simple MAC+IP classifier. Optional.
        :type node: dict
        :type list_name: str
        :type data: dict
        :type macip: bool
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the operation fails.
        """

        if macip:
            path = "/acl/vpp-acl:vpp-macip-acl/{0}".format(list_name)
        else:
            path = "/acl/vpp-acl:vpp-acl/{0}".format(list_name)

        status_code, resp = HcUtil.put_honeycomb_data(
            node, "config_plugin_acl", data, path)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "Could not create classify chain."
                "Status code: {0}.".format(status_code))

        return resp

    @staticmethod
    def set_acl_plugin_interface(node, interface, acl_name,
                                 direction, macip=False):
        """Assign an interface to an ietf-acl classify chain.

        :param node: Honeycomb node.
        :param interface: Name of an interface on the node.
        :param acl_name: Name of an ACL chain configured through ACL-plugin.
        :param direction: Classify incoming or outgiong packets.
            Valid options are: ingress, egress
        :param macip: Use simple MAC+IP classifier. Optional.
        :type node: dict
        :type interface: str or int
        :type acl_name: str
        :type direction: str
        :type macip: bool
        :returns: Content of response.
        :rtype: bytearray
        :raises ValueError: If the direction argument is incorrect.
        :raises HoneycombError: If the operation fails.
        """

        interface = Topology.convert_interface_reference(
            node, interface, "name")

        interface = interface.replace("/", "%2F")

        if direction not in ("ingress", "egress"):
            raise ValueError("Unknown traffic direction {0}. "
                             "Valid options are: ingress, egress."
                             .format(direction))

        path = "/interface/{0}/interface-acl:acl/{1}".format(
            interface, direction)

        if macip:
            data = {
                direction: {
                    "vpp-macip-acl": {
                        "type": "vpp-acl:vpp-macip-acl",
                        "name": acl_name
                    }
                }
            }
        else:
            data = {
                direction: {
                    "vpp-acls": [
                        {
                            "type": "vpp-acl:vpp-acl",
                            "name": acl_name
                        }
                    ]
                }
            }

        status_code, resp = HcUtil.put_honeycomb_data(
            node, "config_vpp_interfaces", data, path)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "Could not configure ACL on interface. "
                "Status code: {0}.".format(status_code))

        return resp

    @staticmethod
    def delete_interface_plugin_acls(node, interface):
        """Remove all plugin-acl assignments from an interface.

        :param node: Honeycomb node.
        :param interface: Name of an interface on the node.
        :type node: dict
        :type interface: str or int
        """

        interface = Topology.convert_interface_reference(
            node, interface, "name")

        interface = interface.replace("/", "%2F")

        path = "/interface/{0}/interface-acl:acl/".format(interface)
        status_code, _ = HcUtil.delete_honeycomb_data(
            node, "config_vpp_interfaces", path)

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Could not remove ACL assignment from interface. "
                "Status code: {0}.".format(status_code))

    @staticmethod
    def delete_acl_plugin_classify_chains(node):
        """Remove all plugin-ACL classify chains.

        :param node: Honeycomb node.
        :type node: dict
        """

        status_code, _ = HcUtil.delete_honeycomb_data(
            node, "config_plugin_acl")

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Could not remove plugin-acl chain. "
                "Status code: {0}.".format(status_code))
