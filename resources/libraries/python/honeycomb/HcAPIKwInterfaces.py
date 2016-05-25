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
from resources.libraries.python.honeycomb.HoneycombSetup import HoneycombError
from resources.libraries.python.honeycomb.HoneycombUtil \
    import DataRepresentation
from resources.libraries.python.honeycomb.HoneycombUtil \
    import HoneycombUtil as HcUtil


# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines
class InterfaceKeywords(object):
    """Keywords for Interface manipulation.

    Implements keywords which get configuration and operational data about
    vpp interfaces and set the interface's parameters using Honeycomb REST API.
    """

    INTF_PARAMS = ("name", "description", "type", "enabled",
                   "link-up-down-trap-enable", "v3po:l2")
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
    L2_REWRITE_TAG_PARAMS = ("rewrite-operation",
                             "first-pushed",
                             "tag1",
                             "tag2")
    TAP_PARAMS = ("tap-name", "mac", "device-instance")
    VHOST_USER_PARAMS = ("socket", "role")
    SUB_INTF_PARAMS = ("super-interface",
                       "identifier",
                       "vlan-type",
                       "number-of-tags",
                       "outer-id",
                       "inner-id",
                       "match-any-outer-id",
                       "match-any-inner-id",
                       "exact-match",
                       "default-subif")

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
    def add_first_ipv4_address(node, interface, ip_addr, network):
        """Add the first IPv4 address.

        If there are any other addresses configured, they will be removed.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param ip_addr: IPv4 address to be set.
        :param network: Netmask or length of network prefix.
        :type node: dict
        :type interface: str
        :type ip_addr: str
        :type network: str or int
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces", ("interface", "name", interface), "ietf-ip:ipv4")
        if isinstance(network, basestring):
            address = {"address": [{"ip": ip_addr, "netmask": network}, ]}
        elif isinstance(network, int) and (0 < network < 33):
            address = {"address": [{"ip": ip_addr, "prefix-length": network}, ]}
        else:
            raise HoneycombError("Value {0} is not a valid netmask or network "
                                 "prefix length.".format(network))
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, address)

    @staticmethod
    def add_ipv4_address(node, interface, ip_addr, network):
        """Add IPv4 address.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param ip_addr: IPv4 address to be set.
        :param network: Netmask or length of network prefix.
        :type node: dict
        :type interface: str
        :type ip_addr: str
        :type network: str or int
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces", ("interface", "name", interface), "ietf-ip:ipv4",
                "address")
        if isinstance(network, basestring):
            address = {"address": [{"ip": ip_addr, "netmask": network}, ]}
        elif isinstance(network, int) and (0 < network < 33):
            address = {"address": [{"ip": ip_addr, "prefix-length": network}, ]}
        else:
            raise HoneycombError("Value {0} is not a valid netmask or network "
                                 "prefix length.".format(network))
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
    def create_vxlan_interface(node, interface, **kwargs):
        """Create a new VxLAN interface.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param kwargs: Parameters and their values. The accepted parameters are
        defined in InterfaceKeywords.VXLAN_PARAMS.
        :type node: dict
        :type interface: str
        :type kwargs: dict
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        new_vx_lan = {
            "name": interface,
            "type": "v3po:vxlan-tunnel",
            "v3po:vxlan": {}
        }
        for param, value in kwargs.items():
            if param not in InterfaceKeywords.VXLAN_PARAMS:
                raise HoneycombError("The parameter {0} is invalid.".
                                     format(param))
            new_vx_lan["v3po:vxlan"][param] = value

        path = ("interfaces", "interface")
        vx_lan_structure = [new_vx_lan, ]
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, vx_lan_structure)

    @staticmethod
    def delete_interface(node, interface):
        """Delete an interface.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :type node: dict
        :type interface: str
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If it is not possible to get information about
        interfaces or it is not possible to delete the interface.
        """

        path = ("interfaces", ("interface", "name", interface))

        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "config_vpp_interfaces")
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get configuration information about the "
                "interfaces. Status code: {0}.".format(status_code))

        new_data = HcUtil.remove_item(resp, path)
        status_code, resp = HcUtil.\
            put_honeycomb_data(node, "config_vpp_interfaces", new_data)
        if status_code != HTTPCodes.OK:
            raise HoneycombError("Not possible to remove interface {0}. "
                                 "Status code: {1}.".
                                 format(interface, status_code))
        return resp

    @staticmethod
    def configure_interface_vxlan(node, interface, **kwargs):
        """Configure VxLAN on the interface.

        The keyword configures VxLAN parameters on the given interface. The type
        of interface must be set to "v3po:vxlan-tunnel".
        The new VxLAN parameters overwrite the current configuration. If a
        parameter in new configuration is missing, it is removed from VxLAN
        configuration.
        If the dictionary kwargs is empty, VxLAN configuration is removed.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param kwargs: Parameters and their values. The accepted parameters are
        defined in InterfaceKeywords.VXLAN_PARAMS.
        :type node: dict
        :type interface: str
        :type kwargs: dict
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        vx_lan_structure = dict()
        for param, value in kwargs.items():
            if param not in InterfaceKeywords.VXLAN_PARAMS:
                raise HoneycombError("The parameter {0} is invalid.".
                                     format(param))
            vx_lan_structure[param] = value

        path = ("interfaces", ("interface", "name", interface), "v3po:vxlan")
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, vx_lan_structure)

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

    @staticmethod
    def create_tap_interface(node, interface, **kwargs):
        """Create a new TAP interface.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param kwargs: Parameters and their values. The accepted parameters are
        defined in InterfaceKeywords.TAP_PARAMS.
        :type node: dict
        :type interface: str
        :type kwargs: dict
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        new_tap = {
            "name": interface,
            "type": "v3po:tap",
            "v3po:tap": {}
        }
        for param, value in kwargs.items():
            if param not in InterfaceKeywords.TAP_PARAMS:
                raise HoneycombError("The parameter {0} is invalid.".
                                     format(param))
            new_tap["v3po:tap"][param] = value

        path = ("interfaces", "interface")
        new_tap_structure = [new_tap, ]
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, new_tap_structure)

    @staticmethod
    def configure_interface_tap(node, interface, **kwargs):
        """Configure TAP on the interface.

        The keyword configures TAP parameters on the given interface. The type
        of interface must be set to "v3po:tap".
        The new TAP parameters overwrite the current configuration. If a
        parameter in new configuration is missing, it is removed from TAP
        configuration.
        If the dictionary kwargs is empty, TAP configuration is removed.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param kwargs: Parameters and their values. The accepted parameters are
        defined in InterfaceKeywords.TAP_PARAMS.
        :type node: dict
        :type interface: str
        :type kwargs: dict
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        tap_structure = dict()
        for param, value in kwargs.items():
            if param not in InterfaceKeywords.TAP_PARAMS:
                raise HoneycombError("The parameter {0} is invalid.".
                                     format(param))
            tap_structure[param] = value

        path = ("interfaces", ("interface", "name", interface), "v3po:tap")
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, tap_structure)

    @staticmethod
    def configure_interface_vhost_user(node, interface, **kwargs):
        """Configure vhost-user on the interface.

        The keyword configures vhost-user parameters on the given interface.
        The type of interface must be set to "v3po:vhost-user".
        The new vhost-user parameters overwrite the current configuration. If a
        parameter in new configuration is missing, it is removed from vhost-user
        configuration.
        If the dictionary kwargs is empty, vhost-user configuration is removed.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param kwargs: Parameters and their values. The accepted parameters are
        defined in InterfaceKeywords.VHOST_USER_PARAMS.
        :type node: dict
        :type interface: str
        :type kwargs: dict
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        vhost_structure = dict()
        for param, value in kwargs.items():
            if param not in InterfaceKeywords.VHOST_USER_PARAMS:
                raise HoneycombError("The parameter {0} is invalid.".
                                     format(param))
            vhost_structure[param] = value

        path = ("interfaces", ("interface", "name", interface),
                "v3po:vhost-user")
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, vhost_structure)

    @staticmethod
    def create_vhost_user_interface(node, interface, **kwargs):
        """Create a new vhost-user interface.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :param kwargs: Parameters and their values. The accepted parameters are
        defined in InterfaceKeywords.VHOST_USER_PARAMS.
        :type node: dict
        :type interface: str
        :type kwargs: dict
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        new_vhost = {
            "name": interface,
            "type": "v3po:vhost-user",
            "v3po:vhost-user": {}
        }
        for param, value in kwargs.items():
            if param not in InterfaceKeywords.VHOST_USER_PARAMS:
                raise HoneycombError("The parameter {0} is invalid.".
                                     format(param))
            new_vhost["v3po:vhost-user"][param] = value

        path = ("interfaces", "interface")
        new_vhost_structure = [new_vhost, ]
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, new_vhost_structure)

    @staticmethod
    def create_sub_interface(node, super_interface, identifier, **kwargs):
        """Create a new sub-interface.

        :param node: Honeycomb node.
        :param super_interface: The name of super interface.
        :param identifier: sub-interface identifier.
        :param kwargs: Parameters and their values. The accepted parameters are
        defined in InterfaceKeywords.SUB_INTF_PARAMS.
        :type node: dict
        :type super_interface: str
        :type identifier: int
        :type kwargs: dict
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        # These parameters are empty types (in JSON represented as empty
        # dictionary) but ODL internally represents them as Booleans. If the
        # value is an empty dictionary, it is True, if the parameter is
        # missing, it is False.
        empty_types = ("match-any-outer-id",
                       "match-any-inner-id",
                       "exact-match",
                       "default-subif")

        sub_interface_name = "{0}.{1}".format(super_interface, str(identifier))
        new_sub_interface = {
            "name": sub_interface_name,
            "type": "v3po:sub-interface",
            "enabled": "false",
            "sub-interface": {
                "super-interface": super_interface,
                "identifier": identifier
            }
        }
        for param, value in kwargs.items():
            if param in InterfaceKeywords.INTF_PARAMS:
                new_sub_interface[param] = value
            elif param in InterfaceKeywords.SUB_INTF_PARAMS:
                if param in empty_types:
                    if value:
                        new_sub_interface["sub-interface"][param] = dict()
                else:
                    new_sub_interface["sub-interface"][param] = value
            else:
                raise HoneycombError("The parameter {0} is invalid.".
                                     format(param))

        path = ("interfaces", "interface")
        new_sub_interface_structure = [new_sub_interface, ]
        return InterfaceKeywords._set_interface_properties(
            node, sub_interface_name, path, new_sub_interface_structure)

    @staticmethod
    def add_vlan_tag_rewrite_to_sub_interface(node, sub_interface, **kwargs):
        """Add vlan tag rewrite to a sub-interface.

        :param node: Honeycomb node.
        :param sub_interface: The name of sub-interface.
        :param kwargs: Parameters and their values. The accepted parameters are
        defined in InterfaceKeywords.L2_REWRITE_TAG_PARAMS.
        :type node: dict
        :type sub_interface: str
        :type kwargs: dict
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        new_rewrite = dict()
        for param, value in kwargs.items():
            if param in InterfaceKeywords.L2_REWRITE_TAG_PARAMS:
                new_rewrite[param] = value
            else:
                raise HoneycombError("The parameter {0} is invalid.".
                                     format(param))

        path = ("interfaces", ("interface", "name", sub_interface), "v3po:l2",
                "vlan-tag-rewrite")
        return InterfaceKeywords._set_interface_properties(
            node, sub_interface, path, new_rewrite)

    @staticmethod
    def remove_vlan_tag_rewrite_from_sub_interface(node, sub_interface):
        """Remove vlan tag rewrite from a sub-interface.

        :param node: Honeycomb node.
        :param sub_interface: The name of sub-interface.
        :type node: dict
        :type sub_interface: str
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        """

        path = ("interfaces", ("interface", "name", sub_interface), "v3po:l2",
                "vlan-tag-rewrite")
        return InterfaceKeywords._set_interface_properties(
            node, sub_interface, path, None)

    @staticmethod
    def compare_interface_lists(list1, list2):
        """Compare provided lists of interfaces by name.

        :param list1: list of interfaces
        :param list2: list of interfaces
        :type list1: list
        :type list2: list
        :raises HoneycombError: If an interface exists in only one of the lists.
        """

        ignore = ["vx_tunnel0"]
        # vx_tunnel0 has no equivalent in config data and no effect on VPP

        names1 = [x['name'] for x in list1]
        names2 = [x['name'] for x in list2]

        for name in names1:
            if name in names2 or name in ignore:
                pass
            else:
                raise HoneycombError("Interface {0} not present in list {1}"
                                     .format(name, list2))
        for name in names2:
            if name in names1 or name in ignore:
                pass
            else:
                raise HoneycombError("Interface {0} not present in list {1}"
                                     .format(name, list1))
