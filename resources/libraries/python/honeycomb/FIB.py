# Copyright (c) 2018 Bell Canada, Pantheon Technologies and/or its affiliates.
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

"""This module implements keywords to manipulate FIB tables using
Honeycomb REST API."""

from robot.api import logger

from resources.libraries.python.HTTPRequest import HTTPCodes
from resources.libraries.python.honeycomb.HoneycombSetup import HoneycombError
from resources.libraries.python.honeycomb.HoneycombUtil \
    import DataRepresentation
from resources.libraries.python.honeycomb.HoneycombUtil \
    import HoneycombUtil as HcUtil


class FibKeywords(object):
    """Implementation of keywords which make it possible to:
    - add/remove FIB tables,
    - add/remove FIB table entries
    - get operational data about FIB tables,
    """

    def __init__(self):
        pass

    @staticmethod
    def _set_fib_table_properties(node, path, data=None):
        """Set FIB table properties and check the return code.

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
            status_code, resp = HcUtil. \
                put_honeycomb_data(node, "config_fib_table", data, path,
                                   data_representation=DataRepresentation.JSON)
        else:
            status_code, resp = HcUtil. \
                delete_honeycomb_data(node, "config_fib_table", path)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            if data is None and '"error-tag":"data-missing"' in resp:
                logger.debug("data does not exist in path.")
            else:
                raise HoneycombError(
                    "The configuration of FIB table was not successful. "
                    "Status code: {0}.".format(status_code))
        return resp

    @staticmethod
    def configure_fib_table(node, ip_version, vrf=1):
        """Configure a FIB table according to the data provided.

        :param node: Honeycomb node.
        :param ip_version: IP protocol version, ipv4 or ipv6.
        :param vrf: vrf-id to attach configuration to.
        :type node: dict
        :type ip_version: str
        :type vrf: int
        :returns: Content of response.
        :rtype: bytearray
        """
        full_data = {
            "vpp-fib-table-management:table": [
                {
                    "table-id": vrf,
                    "address-family": "vpp-fib-table-management:{0}"
                                      .format(ip_version),
                    "name": "{0}-VRF:{1}".format(ip_version, vrf)
                }
            ]
        }
        path = "/table/{0}/vpp-fib-table-management:{1}".format(vrf, ip_version)
        return FibKeywords._set_fib_table_properties(node, path, full_data)

    @staticmethod
    def delete_fib_table(node, ip_version, vrf=1):
        """Delete the specified FIB table from configuration data.

        :param node: Honeycomb node.
        :param ip_version: IP protocol version, ipv4 or ipv6.
        :param vrf: vrf-id to attach configuration to.
        :type node: dict
        :type ip_version: str
        :type vrf: int
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "/table/{0}/vpp-fib-table-management:{1}".format(vrf, ip_version)
        return FibKeywords._set_fib_table_properties(node, path)

    @staticmethod
    def get_fib_table_oper(node, ip_version, vrf=1):
        """Retrieve operational data about the specified FIB table.

        :param node: Honeycomb node.
        :param ip_version: IP protocol version, ipv4 or ipv6.
        :param vrf: vrf-id to attach configuration to.
        :type node: dict
        :type ip_version: str
        :type vrf: int
        :returns: FIB table operational data.
        :rtype: list
        :raises HoneycombError: If the operation fails.
        """

        path = "/table/{0}/vpp-fib-table-management:{1}".format(vrf, ip_version)
        status_code, resp = HcUtil. \
            get_honeycomb_data(node, "oper_fib_table", path)

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get operational information about the "
                "FIB tables. Status code: {0}.".format(status_code))

        data = resp['vpp-fib-table-management:table'][0]

        return data
