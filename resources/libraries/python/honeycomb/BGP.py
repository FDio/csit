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

"""Keywords to manipulate BGP configuration using Honeycomb REST API."""

from resources.libraries.python.constants import Constants as Const
from resources.libraries.python.HTTPRequest import HTTPCodes
from resources.libraries.python.honeycomb.HoneycombSetup import HoneycombError
from resources.libraries.python.honeycomb.HoneycombUtil \
    import HoneycombUtil as HcUtil


class BGPKeywords(object):
    """Keywords to manipulate BGP configuration.

    Implements keywords which read configuration and operational data for
    the BGP feature, and configure BGP parameters using Honeycomb REST API.
    """

    def __init__(self):
        """Initializer."""
        pass

    @staticmethod
    def _configure_bgp_peer(node, path, data=None):
        """Send BGP peer configuration data and check the response.

        :param node: Honeycomb node.
        :param path: Additional path to append to the base BGP config path.
        :param data: Configuration data to be sent in PUT request.
        :type node: dict
        :type path: str
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response to PUT is not
            200 = OK or 201 = ACCEPTED.
        """

        if data is None:
            status_code, resp = HcUtil. \
                delete_honeycomb_data(node, "config_bgp_peer", path)
        else:
            status_code, resp = HcUtil.\
                put_honeycomb_data(node, "config_bgp_peer", data, path)
        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "The configuration of BGP peer was not successful. "
                "Status code: {0}.".format(status_code))
        return resp

    @staticmethod
    def _configure_bgp_route(node, path, data=None):
        """Send BGP route configuration data and check the response.

        :param node: Honeycomb node.
        :param path: Additional path to append to the base BGP config path.
        :param data: Configuration data to be sent in PUT request.
        :type node: dict
        :type path: str
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response to PUT is not
            200 = OK or 201 = ACCEPTED.
        """

        if data is None:
            status_code, resp = HcUtil. \
                delete_honeycomb_data(node, "config_bgp_route", path)
        else:
            status_code, resp = HcUtil. \
                put_honeycomb_data(node, "config_bgp_route", data, path)
        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "The configuration of BGP route was not successful. "
                "Status code: {0}.".format(status_code))
        return resp

    @staticmethod
    def get_full_bgp_configuration(node):
        """Get BGP configuration from the node.

        :param node: Honeycomb node.
        :type node: dict
        :returns: BGP configuration data.
        :rtype: dict
        :raises HoneycombError: If the status code in response is not 200 = OK.
        """

        status_code, resp = HcUtil. \
            get_honeycomb_data(node, "config_bgp_peer")
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get configuration information about BGP."
                " Status code: {0}.".format(status_code))
        return resp

    @staticmethod
    def get_bgp_peer(node, address, datastore='config'):
        """Get BGP configuration of the specified peer from the node.

        :param node: Honeycomb node.
        :param address: IP address of the peer.
        :param datastore: Get data from config or operational datastore.
        :type node: dict
        :type address: str
        :type datastore: str
        :returns: BGP peer configuration data.
        :rtype: dict
        :raises HoneycombError: If the status code in response is not 200 = OK.
        """

        path = "bgp-openconfig-extensions:neighbors/" \
               "neighbor/{0}".format(address)
        if datastore != "operational":
            url = "config_bgp_peer"
        else:
            url = "oper_bgp"
            path = "peer/bgp:%2F%2F{0}".format(address)
        status_code, resp = HcUtil. \
            get_honeycomb_data(node, url, path)
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get configuration information about the BGP"
                " peer. Status code: {0}.".format(status_code))
        return resp

    @staticmethod
    def add_bgp_peer(node, address, data):
        """Configure a BGP peer on the node.

        :param node: Honeycomb node.
        :param address: IP address of the peer.
        :param data: Peer configuration data.
        :type node: dict
        :type address: str
        :type data: dict
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "bgp-openconfig-extensions:neighbors/neighbor/{address}".format(
            address=address)
        return BGPKeywords._configure_bgp_peer(node, path, data)

    @staticmethod
    def remove_bgp_peer(node, address):
        """Remove a BGP peer from the configuration.

        :param node: Honeycomb node.
        :param address: IP address of the peer.
        :type node: dict
        :type address: str
        :returns: Content of response.
        :rtype: bytearray
        """

        path = "bgp-openconfig-extensions:neighbors/neighbor/{address}".format(
            address=address)
        return BGPKeywords._configure_bgp_peer(node, path)

    @staticmethod
    def configure_bgp_route(node, peer_address, data, route_address,
                            index, ip_version):
        """Configure a route for the BGP peer specified by peer IP address.

        :param node: Honeycomb node.
        :param peer_address: IP address of the BGP peer.
        :param data: Route configuration data.
        :param route_address: IP address of the route.
        :param index: Index number of the route within specified peer.
        :param ip_version: IP protocol version. ipv4 or ipv6
        :type node: dict
        :type peer_address: str
        :type data: dict
        :type route_address: str
        :type index: int
        :type ip_version: str
        :returns: Content of response.
        :rtype: bytearray
        """

        route_address = route_address.replace("/", "%2F")

        if ip_version.lower() == "ipv4":
            path = "{0}/tables/bgp-types:ipv4-address-family/" \
                   "bgp-types:unicast-subsequent-address-family/" \
                   "bgp-inet:ipv4-routes/ipv4-route/{1}/{2}" \
                .format(peer_address, route_address, index)
        else:
            path = "{0}/tables/bgp-types:ipv6-address-family/" \
                   "bgp-types:unicast-subsequent-address-family/" \
                   "bgp-inet:ipv6-routes/ipv6-route/{1}/{2}" \
                .format(peer_address, route_address, index)

        return BGPKeywords._configure_bgp_route(node, path, data)

    @staticmethod
    def get_bgp_route(node, peer_address, route_address, index, ip_version):
        """Get all BGP peers from operational data.

        :param node: Honeycomb node.
        :param peer_address: IP address of the BGP peer.
        :param route_address: IP address of the route.
        :param index: Index number of the route within specified peer.
        :param ip_version: IP protocol version. ipv4 or ipv6
        :type node: dict
        :type peer_address: str
        :type route_address: str
        :type index: int
        :type ip_version: str
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response is not 200 = OK.
        """

        route_address = route_address.replace("/", "%2F")

        if ip_version.lower() == "ipv4":
            path = "{0}/tables/bgp-types:ipv4-address-family/" \
                   "bgp-types:unicast-subsequent-address-family/" \
                   "bgp-inet:ipv4-routes/ipv4-route/{1}/{2}" \
                .format(peer_address, route_address, index)
        else:
            path = "{0}/tables/bgp-types:ipv6-address-family/" \
                   "bgp-types:unicast-subsequent-address-family/" \
                   "bgp-inet:ipv6-routes/ipv6-route/{1}/{2}" \
                .format(peer_address, route_address, index)
        status_code, resp = HcUtil. \
            get_honeycomb_data(node, "config_bgp_route", path)
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get configuration information about the BGP"
                " route. Status code: {0}.".format(status_code))

        return resp

    @staticmethod
    def get_all_peer_routes(node, peer_address, ip_version):
        """Get all configured routes for the given BGP peer.

        :param node: Honeycomb node.
        :param peer_address: IP address of the peer.
        :param ip_version: IP protocol version. ipv4 or ipv6
        :type node: dict
        :type peer_address: str
        :type ip_version: str
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response is not 200 = OK.
        """

        if ip_version.lower() == "ipv4":
            path = "{0}/tables/bgp-types:ipv4-address-family/" \
                   "bgp-types:unicast-subsequent-address-family/" \
                   "bgp-inet:ipv4-routes".format(peer_address)
        else:
            path = "{0}/tables/bgp-types:ipv6-address-family/" \
                   "bgp-types:unicast-subsequent-address-family/" \
                   "bgp-inet:ipv6-routes".format(peer_address)
        status_code, resp = HcUtil. \
            get_honeycomb_data(node, "config_bgp_route", path)
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get configuration information about BGP"
                " routes. Status code: {0}.".format(status_code))

        return resp

    @staticmethod
    def remove_bgp_route(node, peer_address, route_address, index, ip_version):
        """Remove the specified BGP route from configuration.

        :param node: Honeycomb node.
        :param peer_address: IP address of the BGP peer.
        :param route_address: IP address of the route.
        :param index: Index number of the route within specified peer.
        :param ip_version: IP protocol version. ipv4 or ipv6
        :type node: dict
        :type peer_address: str
        :type route_address: str
        :type index: int
        :type ip_version: str
        :returns: Content of response.
        :rtype: bytearray
        """

        route_address = route_address.replace("/", "%2F")

        if ip_version.lower() == "ipv4":
            path = "{0}/tables/bgp-types:ipv4-address-family/" \
                   "bgp-types:unicast-subsequent-address-family/" \
                   "bgp-inet:ipv4-routes/ipv4-route/{1}/{2}" \
                .format(peer_address, route_address, index)
        else:
            path = "{0}/tables/bgp-types:ipv6-address-family/" \
                   "bgp-types:unicast-subsequent-address-family/" \
                   "bgp-inet:ipv6-routes/ipv6-route/{1}/{2}" \
                .format(peer_address, route_address, index)

        return BGPKeywords._configure_bgp_route(node, path)

    @staticmethod
    def get_bgp_local_rib(node):
        """Get local RIB table from the Honeycomb node.

        :param node: Honeycomb node.
        :type node: dict
        :returns: RIB operational data.
        :rtype: dict
        :raises HoneycombError: If the status code in response is not 200 = OK.
        """

        path = "loc-rib"

        status_code, resp = HcUtil. \
            get_honeycomb_data(node, "oper_bgp", path)

        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get operational data from BGP local RIB."
                " Status code: {0}.".format(status_code))

        return resp

    @staticmethod
    def configure_bgp_base(node, ip_address, port, as_number):
        """Modify BGP config file. Requires a restart of Honeycomb to take
        effect.

        :param node: Honeycomb node.
        :param ip_address: BGP peer identifier/binding address.
        :param port: BGP binding port.
        :param as_number: Autonomous System ID number.
        :type node: dict
        :type ip_address: str
        :type port: int
        :type as_number: int
        :raises HoneycombError: If modifying the configuration fails.
        """

        from resources.libraries.python.ssh import SSH

        config = {
            '\\"bgp-binding-address\\"': '\\"{0}\\"'.format(ip_address),
            '\\"bgp-port\\"': port,
            '\\"bgp-as-number\\"': as_number}

        path = "{0}/config/bgp.json".format(Const.REMOTE_HC_DIR)

        for key, value in config.items():
            find = key
            replace = '"{0}": "{1}",'.format(key, value)

            argument = '"/{0}/c\\ {1}"'.format(find, replace)
            command = "sed -i {0} {1}".format(argument, path)

            ssh = SSH()
            ssh.connect(node)
            (ret_code, _, stderr) = ssh.exec_command_sudo(command)
            if ret_code != 0:
                raise HoneycombError("Failed to modify configuration on "
                                     "node {0}, {1}".format(node, stderr))

    @staticmethod
    def compare_rib_tables(data, ref):
        """Compare provided RIB table with reference. All reference entries must
        be present in data. Data entries not present in reference are ignored.

        :param data: Data from Honeycomb node.
        :param ref: Reference data to compare against.
        :type data: dict
        :type ref: dict
        :raises HoneycombError: If the tables do not match.
        """

        # Remove runtime attributes from data
        for item in data:
            item.pop("attributes", "")

        for item in ref:
            if item not in data:
                raise HoneycombError(
                    "RIB entry {0} not found in operational data.")
