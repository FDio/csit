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

"""Keywords to manipulate interface configuration using Honeycomb REST API.

The keywords make possible to put and get configuration data and to get
operational data.
"""


from resources.libraries.python.HTTPRequest import HTTPCodes
from resources.libraries.python.HoneycombSetup import HoneycombError
from resources.libraries.python.HoneycombUtil import HoneycombUtil as HcUtil
from resources.libraries.python.HoneycombUtil import DataRepresentation


class InterfaceKeywords(object):
    """Keywords for Interface manipulation.

    Implements keywords which get configuration and operational data about
    vpp interfaces and set the interface's parameters using Honeycomb REST API.
    """

    INTF_PARAMS = ("name", "description", "type", "enabled",
                   "link-up-down-trap-enable")
    IPV4_PARAMS = ("enabled", "forwarding", "mtu")
    IPV6_PARAMS = ("enabled", "forwarding", "mtu", "dup-addr-detect-transmits")
    IPV6_AUTOCONF_PARAMS = ("create-global-addresses",
                            "create-temporary-addresses",
                            "temporary-valid-lifetime",
                            "temporary-preferred-lifetime")
    ETH_PARAMS = ("mtu", )
    ROUTING_PARAMS = ("vrf-id", )
    VXLAN_PARAMS = ("src", "dst", "vni", "encap-vrf-id")
    L2_PARAMS = ("bridge-domain", "split-horizon-group",
                 "bridged-virtual-interface")

    def __init__(self):
        pass

    @staticmethod
    def _configure_interface(node, interface, data,
                             data_representation=DataRepresentation.JSON):
        """Send interface configuration data and check the response.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param data: Configuration data to be sent in PUT request.
        :param data_representation: How the data is represented.
        :type node: dict
        :type interface: str
        :type data: dict
        :type data_representation: DataRepresentation
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response on PUT is not
        200 = OK.
        """

        status_code, resp = HcUtil.\
            put_honeycomb_data(node, "config_vpp_interfaces", data,
                               data_representation=data_representation)
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "The configuration of interface '{0}' was not successful. "
                "Status code: {1}.".format(interface, status_code))
        return resp

    @staticmethod
    def get_all_interfaces_cfg_data(node):
        """Get configuration data about all interfaces from Honeycomb.

        :param node: Honeycomb node.
        :type node: dict
        :return: Configuration data about all interfaces from Honeycomb.
        :rtype: list
        :raises HoneycombError: If it is not possible to get configuration data.
        """

        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "config_vpp_interfaces")
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get configuration information about the "
                "interfaces. Status code: {0}.".format(status_code))
        try:
            return resp["interfaces"]["interface"]

        except (KeyError, TypeError):
            return []

    @staticmethod
    def get_interface_cfg_data(node, interface):
        """Get configuration data about the given interface from Honeycomb.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :type node: dict
        :type interface: str
        :return: Configuration data about the given interface from Honeycomb.
        :rtype: dict
        """

        intfs = InterfaceKeywords.get_all_interfaces_cfg_data(node)
        for intf in intfs:
            if intf["name"] == interface:
                return intf
        return {}

    @staticmethod
    def get_all_interfaces_oper_data(node):
        """Get operational data about all interfaces from Honeycomb.

        :param node: Honeycomb node.
        :type node: dict
        :return: Operational data about all interfaces from Honeycomb.
        :rtype: list
        :raises HoneycombError: If it is not possible to get operational data.
        """

        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "oper_vpp_interfaces")
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get operational information about the "
                "interfaces. Status code: {0}.".format(status_code))
        try:
            return resp["interfaces-state"]["interface"]

        except (KeyError, TypeError):
            return []

    @staticmethod
    def get_interface_oper_data(node, interface):
        """Get operational data about the given interface from Honeycomb.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :type node: dict
        :type interface: str
        :return: Operational data about the given interface from Honeycomb.
        :rtype: dict
        """

        intfs = InterfaceKeywords.get_all_interfaces_oper_data(node)
        for intf in intfs:
            if intf["name"] == interface:
                return intf
        return {}

    @staticmethod
    def _set_interface_properties(node, interface, path, new_value=None):
        """Set interface properties.

        This method reads interface configuration data, creates, changes or
        removes the requested data and puts it back to Honeycomb.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param path:  Path to data we want to change / create / remove.
        :param new_value: The new value to be set. If None, the item will be
        removed.
        :type node: dict
        :type interface: str
        :type path: tuple
        :type new_value: str, dict or list
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If it is not possible to get or set the data.
        """

        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "config_vpp_interfaces")
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get configuration information about the "
                "interfaces. Status code: {0}.".format(status_code))

        if new_value:
            new_data = HcUtil.set_item_value(resp, path, new_value)
        else:
            new_data = HcUtil.remove_item(resp, path)
        return InterfaceKeywords._configure_interface(node, interface, new_data)

    @staticmethod
    def set_interface_state(node, interface, state="up"):
        """Set VPP interface state.

        The keyword changes the administration state of interface to up or down
        depending on the parameter "state".

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param state: The requested state, only "up" and "down" are valid
        values.
        :type node: dict
        :type interface: str
        :type state: str
        :return: Content of response.
        :rtype: bytearray
        :raises KeyError: If the argument "state" is nor "up" or "down".
        :raises HoneycombError: If the interface is not present on the node.
        """

        intf_state = {"up": "true",
                      "down": "false"}

        path = ("interfaces", ("interface", "name", str(interface)), "enabled")
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, intf_state[state.lower()])

    @staticmethod
    def set_interface_up(node, interface):
        """Set the administration state of VPP interface to up.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :type node: dict
        :type interface: str
        :return: Content of response
        :rtype: bytearray
        """

        return InterfaceKeywords.set_interface_state(node, interface, "up")

    @staticmethod
    def set_interface_down(node, interface):
        """Set the administration state of VPP interface to down.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :type node: dict
        :type interface: str
        :return: Content of response.
        :rtype: bytearray
        """

        return InterfaceKeywords.set_interface_state(node, interface, "down")

    @staticmethod
    def add_bridge_domain_to_interface(node, interface, bd_name,
                                       split_horizon_group=None, bvi=None):
        """Add a new bridge domain to an interface and set its parameters.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param bd_name: Bridge domain name.
        :param split_horizon_group: Split-horizon group name.
        :param bvi: The bridged virtual interface.
        :type node: dict
        :type interface: str
        :type bd_name: str
        :type split_horizon_group: str
        :type bvi: str
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the interface is not present on the node.
        """

        v3po_l2 = {"bridge-domain": str(bd_name)}
        if split_horizon_group:
            v3po_l2["split-horizon-group"] = str(split_horizon_group)
        if bvi:
            v3po_l2["bridged-virtual-interface"] = str(bvi)

        path = ("interfaces", ("interface", "name", str(interface)), "v3po:l2")

        return InterfaceKeywords._set_interface_properties(
            node, interface, path, v3po_l2)

    @staticmethod
    def configure_interface_base(node, interface, param, value):
        """Configure the base parameters of interface.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param param: Parameter to configure (set, change, remove)
        :param value: The value of parameter. If None, the parameter will be
        removed.
        :type node: dict
        :type interface: str
        :type param: str
        :type value: str
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        if param not in InterfaceKeywords.INTF_PARAMS:
            raise HoneycombError("The parameter {0} is invalid.".format(param))

        path = ("interfaces", ("interface", "name", interface), param)
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, value)

    @staticmethod
    def configure_interface_ipv4(node, interface, param, value):
        """Configure IPv4 parameters of interface

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param param: Parameter to configure (set, change, remove)
        :param value: The value of parameter. If None, the parameter will be
        removed.
        :type node: dict
        :type interface: str
        :type param: str
        :type value: str
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        if param not in InterfaceKeywords.IPV4_PARAMS:
            raise HoneycombError("The parameter {0} is invalid.".format(param))

        path = ("interfaces", ("interface", "name", interface),
                "ietf-ip:ipv4", param)
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, value)

    @staticmethod
    def add_first_ipv4_address(node, interface, ip_addr, netmask):
        """Add the first IPv4 address.

        If there are any other addresses configured, they will be removed.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param ip_addr: IPv4 address to be set.
        :param netmask: Netmask.
        :type node: dict
        :type interface: str
        :type ip_addr: str
        :type netmask: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces", ("interface", "name", interface), "ietf-ip:ipv4")
        address = {"address": [{"ip": ip_addr, "netmask": netmask}, ]}
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, address)

    @staticmethod
    def add_ipv4_address(node, interface, ip_addr, netmask):
        """Add IPv4 address.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param ip_addr: IPv4 address to be set.
        :param netmask: Netmask.
        :type node: dict
        :type interface: str
        :type ip_addr: str
        :type netmask: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces", ("interface", "name", interface), "ietf-ip:ipv4",
                "address")
        address = [{"ip": ip_addr, "prefix-length": netmask}, ]
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, address)

    @staticmethod
    def remove_all_ipv4_addresses(node, interface):
        """Remove all IPv4 addresses from interface.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :type node: dict
        :type interface: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces", ("interface", "name", interface), "ietf-ip:ipv4",
                "address")
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, None)

    @staticmethod
    def add_first_ipv4_neighbor(node, interface, ip_addr, link_layer_address):
        """Add the first IPv4 neighbour.

        If there are any other neighbours configured, they will be removed.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param ip_addr: IPv4 address of neighbour to be set.
        :param link_layer_address: Link layer address.
        :type node: dict
        :type interface: str
        :type ip_addr: str
        :type link_layer_address: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces", ("interface", "name", interface), "ietf-ip:ipv4")
        neighbor = {"neighbor": [{"ip": ip_addr,
                                  "link-layer-address": link_layer_address}, ]}
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, neighbor)

    @staticmethod
    def add_ipv4_neighbor(node, interface, ip_addr, link_layer_address):
        """Add the IPv4 neighbour.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param ip_addr: IPv4 address of neighbour to be set.
        :param link_layer_address: Link layer address.
        :type node: dict
        :type interface: str
        :type ip_addr: str
        :type link_layer_address: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces", ("interface", "name", interface), "ietf-ip:ipv4",
                "neighbor")
        neighbor = [{"ip": ip_addr, "link-layer-address": link_layer_address}, ]
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, neighbor)

    @staticmethod
    def remove_all_ipv4_neighbors(node, interface):
        """Remove all IPv4 neighbours.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :type node: dict
        :type interface: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces", ("interface", "name", interface), "ietf-ip:ipv4",
                "neighbor")
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, None)

    @staticmethod
    def configure_interface_ipv6(node, interface, param, value):
        """Configure IPv6 parameters of interface

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param param: Parameter to configure (set, change, remove)
        :param value: The value of parameter. If None, the parameter will be
        removed.
        :type node: dict
        :type interface: str
        :type param: str
        :type value: str
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        if param in InterfaceKeywords.IPV6_PARAMS:
            path = ("interfaces", ("interface", "name", interface),
                    "ietf-ip:ipv6", param)
        elif param in InterfaceKeywords.IPV6_AUTOCONF_PARAMS:
            path = ("interfaces", ("interface", "name", interface),
                    "ietf-ip:ipv6", "autoconf", param)
        else:
            raise HoneycombError("The parameter {0} is invalid.".format(param))

        return InterfaceKeywords._set_interface_properties(
            node, interface, path, value)

    @staticmethod
    def add_first_ipv6_address(node, interface, ip_addr, prefix_len):
        """Add the first IPv6 address.

        If there are any other addresses configured, they will be removed.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param ip_addr: IPv6 address to be set.
        :param prefix_len: Prefix length.
        :type node: dict
        :type interface: str
        :type ip_addr: str
        :type prefix_len: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces", ("interface", "name", interface), "ietf-ip:ipv6")
        address = {"address": [{"ip": ip_addr, "prefix-length": prefix_len}, ]}
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, address)

    @staticmethod
    def add_ipv6_address(node, interface, ip_addr, prefix_len):
        """Add IPv6 address.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param ip_addr: IPv6 address to be set.
        :param prefix_len: Prefix length.
        :type node: dict
        :type interface: str
        :type ip_addr: str
        :type prefix_len: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces", ("interface", "name", interface), "ietf-ip:ipv6",
                "address")
        address = [{"ip": ip_addr, "prefix-length": prefix_len}, ]
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, address)

    @staticmethod
    def remove_all_ipv6_addresses(node, interface):
        """Remove all IPv6 addresses from interface.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :type node: dict
        :type interface: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces", ("interface", "name", interface), "ietf-ip:ipv6",
                "address")
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, None)

    @staticmethod
    def add_first_ipv6_neighbor(node, interface, ip_addr, link_layer_address):
        """Add the first IPv6 neighbour.

        If there are any other neighbours configured, they will be removed.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param ip_addr: IPv6 address of neighbour to be set.
        :param link_layer_address: Link layer address.
        :type node: dict
        :type interface: str
        :type ip_addr: str
        :type link_layer_address: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces", ("interface", "name", interface), "ietf-ip:ipv6")
        neighbor = {"neighbor": [{"ip": ip_addr,
                                  "link-layer-address": link_layer_address}, ]}
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, neighbor)

    @staticmethod
    def add_ipv6_neighbor(node, interface, ip_addr, link_layer_address):
        """Add the IPv6 neighbour.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param ip_addr: IPv6 address of neighbour to be set.
        :param link_layer_address: Link layer address.
        :type node: dict
        :type interface: str
        :type ip_addr: str
        :type link_layer_address: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces", ("interface", "name", interface), "ietf-ip:ipv6",
                "neighbor")
        neighbor = [{"ip": ip_addr, "link-layer-address": link_layer_address}, ]
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, neighbor)

    @staticmethod
    def remove_all_ipv6_neighbors(node, interface):
        """Remove all IPv6 neighbours.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :type node: dict
        :type interface: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces", ("interface", "name", interface), "ietf-ip:ipv6",
                "neighbor")
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, None)

    @staticmethod
    def configure_interface_ethernet(node, interface, param, value):
        """Configure the ethernet parameters of interface.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param param: Parameter to configure (set, change, remove)
        :param value: The value of parameter. If None, the parameter will be
        removed.
        :type node: dict
        :type interface: str
        :type param: str
        :type value: str
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        if param not in InterfaceKeywords.ETH_PARAMS:
            raise HoneycombError("The parameter {0} is invalid.".format(param))
        path = ("interfaces", ("interface", "name", interface), "v3po:ethernet",
                param)
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, value)

    @staticmethod
    def configure_interface_routing(node, interface, param, value):
        """Configure the routing parameters of interface.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param param: Parameter to configure (set, change, remove)
        :param value: The value of parameter. If None, the parameter will be
        removed.
        :type node: dict
        :type interface: str
        :type param: str
        :type value: str
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        if param not in InterfaceKeywords.ROUTING_PARAMS:
            raise HoneycombError("The parameter {0} is invalid.".format(param))

        path = ("interfaces", ("interface", "name", interface), "v3po:routing",
                param)
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, value)

    @staticmethod
    def configure_interface_vxlan(node, interface, param, value):
        """Configure the VxLAN parameters of interface.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param param: Parameter to configure (set, change, remove)
        :param value: The value of parameter. If None, the parameter will be
        removed.
        :type node: dict
        :type interface: str
        :type param: str
        :type value: str
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        if param not in InterfaceKeywords.VXLAN_PARAMS:
            raise HoneycombError("The parameter {0} is invalid.".format(param))

        path = ("interfaces", ("interface", "name", interface), "v3po:vxlan",
                param)
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, value)

    @staticmethod
    def configure_interface_l2(node, interface, param, value):
        """Configure the L2 parameters of interface.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param param: Parameter to configure (set, change, remove)
        :param value: The value of parameter. If None, the parameter will be
        removed.
        :type node: dict
        :type interface: str
        :type param: str
        :type value: str
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        if param not in InterfaceKeywords.L2_PARAMS:
            raise HoneycombError("The parameter {0} is invalid.".format(param))
        path = ("interfaces", ("interface", "name", interface), "v3po:l2",
                param)
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, value)
