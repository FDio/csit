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

from resources.libraries.python.topology import Topology
from resources.libraries.python.HTTPRequest import HTTPCodes
from resources.libraries.python.honeycomb.HoneycombSetup import HoneycombError
from resources.libraries.python.honeycomb.HoneycombUtil \
    import DataRepresentation
from resources.libraries.python.honeycomb.HoneycombUtil \
    import HoneycombUtil as HcUtil


class NATKeywords(object):
    """Keywords for NAT configuration."""

    def __init__(self):
        pass

    @staticmethod
    def _set_nat_properties(node, path, data=None):
        """Set NAT properties and check the return code.

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
                put_honeycomb_data(node, "config_nat", data, path,
                                   data_representation=DataRepresentation.JSON)
        else:
            status_code, resp = HcUtil. \
                delete_honeycomb_data(node, "config_nat", path)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "The configuration of NAT was not successful. "
                "Status code: {0}.".format(status_code))
        return resp

    @staticmethod
    def get_nat_oper_data(node):
        """Read NAT operational data.

        :param node: Honeycomb node.
        :type node: dict
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the operation fails or the response
            is not as expected.
        """

        status_code, resp = HcUtil.get_honeycomb_data(node, "oper_nat")

        if status_code != HTTPCodes.OK:
            raise HoneycombError("Could not retrieve NAT operational data.")

        if "nat-state" not in resp.keys():
            raise HoneycombError(
                "Unexpected format, response does not contain nat-state.")
        return resp['nat-state']

    @staticmethod
    def configure_nat_entries(node, data, instance=0, entry=1):
        """Configure NAT entries on node.

        :param node: Honeycomb node.
        :param data: Data to be configured on node.
        :param instance: NAT instance ID.
        :param entry: NAT entry index.
        :type node: dict
        :type data: dict
        :type instance: int
        :type entry: int
        :returns: Content of response.
        :rtype: bytearray
        """

        return NATKeywords._set_nat_properties(
            node,
            '/nat-instances/nat-instance/{0}/'
            'mapping-table/mapping-entry/{1}/'.format(instance, entry),
            data)

    @staticmethod
    def configure_nat_on_interface(node, interface, direction, delete=False):
        """Configure NAT on the specified interface.

        :param node: Honeycomb node.
        :param interface: Name of an interface on the node.
        :param direction: NAT direction, outbound or inbound.
        :param delete: Delete an existing interface NAT configuration.
        :type node: dict
        :type interface: str
        :type direction: str
        :type delete: bool
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the operation fails.
        """

        interface = Topology.convert_interface_reference(
            node, interface, "name")

        interface = interface.replace("/", "%2F")
        path = "/interface/{0}/interface-nat:nat/{1}".format(
            interface, direction)

        data = {direction: {}}

        if delete:
            status_code, resp = HcUtil.delete_honeycomb_data(
                node, "config_vpp_interfaces", path)
        else:
            status_code, resp = HcUtil.put_honeycomb_data(
                node, "config_vpp_interfaces", data, path)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "Could not configure NAT on interface. "
                "Status code: {0}.".format(status_code))

        return resp
