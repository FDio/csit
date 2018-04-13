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

"""This module implements keywords to manipulate NSH-SFC data structures using
Honeycomb REST API."""

from resources.libraries.python.HTTPRequest import HTTPCodes
from resources.libraries.python.honeycomb.HoneycombSetup import HoneycombError
from resources.libraries.python.honeycomb.HoneycombUtil \
    import HoneycombUtil as HcUtil
from resources.libraries.python.honeycomb.HoneycombUtil \
    import DataRepresentation


class NSHKeywords(object):
    """Implementation of keywords which make it possible to:
    - add and remove NSH entries,
    - get operational data about NSH entries,
    - add and remove NSH maps,
    - get operational data about NSH maps.
    """

    def __init__(self):
        pass

    @staticmethod
    def _set_nsh_properties(node, path, data=None):
        """Set NSH properties and check the return code.

        :param node: Honeycomb node.
        :param path: Path which is added to the base path to identify the data.
        :param data: The new data to be set. If None, the item will be removed.
        :type node: dict
        :type path: str
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response to PUT is not
            OK or ACCEPTED.
        """

        if data:
            status_code, resp = HcUtil. \
                put_honeycomb_data(node, "config_nsh", data, path,
                                   data_representation=DataRepresentation.JSON)
        else:
            status_code, resp = HcUtil. \
                delete_honeycomb_data(node, "config_nsh", path)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "The configuration of NSH-SFC was not successful. "
                "Status code: {0}.".format(status_code))
        return resp

    @staticmethod
    def add_nsh_entry(node, name, data):
        """Add an NSH entry to the list of entries. The keyword does
        not validate given data.

        :param node: Honeycomb node.
        :param name: Name for the NSH entry.
        :param data: Settings for the new entry.
        :type node: dict
        :type name: str
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/nsh-entries/nsh-entry/{0}".format(name)

        return NSHKeywords._set_nsh_properties(node, path, data)

    @staticmethod
    def add_nsh_map(node, name, data):
        """Add an NSH map to the list of maps. The keyword does
        not validate given data.

        :param node: Honeycomb node.
        :param name: Name for the NSH map.
        :param data: Settings for the new map.
        :type node: dict
        :type name: str
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        """
        path = "/nsh-maps/nsh-map/{0}".format(name)

        return NSHKeywords._set_nsh_properties(node, path, data)

    @staticmethod
    def remove_nsh_entry(node, name):
        """Remove an NSH entry from the list of entries.
        :param node: Honeycomb node.
        :param name: Name of the NSH entry.
        :type node: dict
        :type name: str
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/nsh-entries/nsh-entry/{0}".format(name)
        return NSHKeywords._set_nsh_properties(node, path)

    @staticmethod
    def remove_nsh_map(node, name):
        """Remove an NSH map from the list of maps.
        :param node: Honeycomb node.
        :param name: Name of the NSH map.
        :type node: dict
        :type name: str
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/nsh-maps/nsh-map/{0}".format(name)
        return NSHKeywords._set_nsh_properties(node, path)

    @staticmethod
    def get_nsh_oper_data(node, entry_name=None, map_name=None):
        """Get all NSH operational data present on the node. Optionally
        filter out data for a specific entry or map.

        :param node: Honeycomb node.
        :param entry_name: Name of a specific NSH entry. Optional.
        :param map_name: Name of a specific NSH map. Optional. Do not use
            together with entry_name.
        :type node: dict
        :type entry_name: str
        :type map_name: str
        :returns: List of classify tables.
        :rtype: list
        """
        if entry_name:
            path = "/nsh-entries/nsh-entry/{0}".format(entry_name)
        elif map_name:
            path = "/nsh-maps/nsh-map/{0}".format(map_name)
        else:
            path = ''

        status_code, resp = HcUtil. \
            get_honeycomb_data(node, "oper_nsh", path)

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get operational information about the "
                "classify tables. Status code: {0}.".format(status_code))

        return resp

    @staticmethod
    def clear_nsh_settings(node):
        """Remove the entire NSH container with all of its entries and maps.

        :param node: Honeycomb node.
        :type node: dict
        :returns: Content of response.
        :rtype: bytearray
        """

        return NSHKeywords._set_nsh_properties(node, '')
