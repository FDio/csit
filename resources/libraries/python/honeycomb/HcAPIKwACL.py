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

from resources.libraries.python.HTTPRequest import HTTPCodes
from resources.libraries.python.honeycomb.HoneycombSetup import HoneycombError
from resources.libraries.python.honeycomb.HoneycombUtil \
    import HoneycombUtil as HcUtil
from resources.libraries.python.honeycomb.HoneycombUtil \
    import DataRepresentation


class ACLKeywords(object):
    """Implementation of keywords which make possible to:
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
        :raises HoneycombError: If the status code in response on PUT is not
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
    def remove_all_classify_sessions(node, table_name):
        """Remove all classify sessions from the classify table.

        :param node: Honeycomb node.
        :param table_name: Name of the classify table.
        :type node: dict
        :type table_name: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = "/classify-table/" + table_name + "/classify-session/"
        return ACLKeywords._set_classify_table_properties(node, path)

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
