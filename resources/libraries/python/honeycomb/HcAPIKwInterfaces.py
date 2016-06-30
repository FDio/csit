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
                   "link-up-down-trap-enable", "v3po:l2", "v3po:vxlan-gpe",
                   "vpp-vlan:sub-interfaces")
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
    TAP_PARAMS = ("tap-name", "mac", "device-instance")
    VHOST_USER_PARAMS = ("socket", "role")
    SUB_IF_PARAMS = ("identifier",
                     "vlan-type",
                     "enabled")
    SUB_IF_MATCH = ("default",
                    "untagged",
                    "vlan-tagged",
                    "vlan-tagged-exact-match")
    BD_PARAMS = ("bridge-domain",
                 "split-horizon-group",
                 "bridged-virtual-interface")
    VXLAN_GPE_PARAMS = ("local",
                        "remote",
                        "vni",
                        "next-protocol",
                        "encap-vrf-id",
                        "decap-vrf-id")

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
    def get_bd_oper_data_from_interface(node, interface):
        """Returns operational data about bridge domain settings in the
        interface.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :type interface: str
        :type node: str
        :return: Operational data about bridge domain settings in the
        interface.
        :rtype: dict
        """

        if_data = InterfaceKeywords.get_interface_oper_data(node, interface)

        if if_data:
            try:
                return if_data["v3po:l2"]
            except KeyError:
                return {}
        return {}

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
        :raises HoneycombError: If the provided netmask or prefix is not valid.
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
        :raises HoneycombError: If the provided netmask or prefix is not valid.
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
    def create_sub_interface(node, super_interface, match, tags=None, **kwargs):
        """Create a new sub-interface.

        :param node: Honeycomb node.
        :param super_interface: Super interface.
        :param match: Match type. The valid values are defined in
        InterfaceKeywords.SUB_IF_MATCH.
        :param tags: List of tags.
        :param kwargs: Parameters and their values. The accepted parameters are
        defined in InterfaceKeywords.SUB_IF_PARAMS.
        :type node: dict
        :type super_interface: str
        :type match: str
        :type tags: list
        :type kwargs: dict
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the parameter is not valid.
        :raises KeyError: If the parameter 'match' is invalid.
        """

        match_type = {
            "default":
                {"default": {}},
            "untagged":
                {"untagged": {}},
            "vlan-tagged":
                {"vlan-tagged": {"match-exact-tags": "false"}},
            "vlan-tagged-exact-match":
                {"vlan-tagged": {"match-exact-tags": "true"}}
        }

        new_sub_interface = {
            "tags": {
                "tag": []
            },
        }

        for param, value in kwargs.items():
            if param in InterfaceKeywords.SUB_IF_PARAMS:
                new_sub_interface[param] = value
            else:
                raise HoneycombError("The parameter {0} is invalid.".
                                     format(param))
        try:
            new_sub_interface["match"] = match_type[match]
        except KeyError:
            raise HoneycombError("The value '{0}' of parameter 'match' is "
                                 "invalid.".format(match))

        if tags:
            new_sub_interface["tags"]["tag"].extend(tags)

        path = ("interfaces",
                ("interface", "name", super_interface),
                "vpp-vlan:sub-interfaces",
                "sub-interface")
        new_sub_interface_structure = [new_sub_interface, ]
        return InterfaceKeywords._set_interface_properties(
            node, super_interface, path, new_sub_interface_structure)

    @staticmethod
    def get_sub_interface_oper_data(node, super_interface, identifier):
        """Retrieves sub-interface operational data using Honeycomb API.

        :param node: Honeycomb node.
        :param super_interface: Super interface.
        :param identifier: The ID of sub-interface.
        :type node: dict
        :type super_interface: str
        :type identifier: int
        :return: Sub-interface operational data.
        :rtype: dict
        :raises HoneycombError: If there is no sub-interface with the given ID.
        """

        if_data = InterfaceKeywords.get_interface_oper_data(node,
                                                            super_interface)
        for sub_if in if_data["vpp-vlan:sub-interfaces"]["sub-interface"]:
            if str(sub_if["identifier"]) == str(identifier):
                return sub_if

        raise HoneycombError("The interface {0} does not have sub-interface "
                             "with ID {1}".format(super_interface, identifier))

    @staticmethod
    def remove_all_sub_interfaces(node, super_interface):
        """Remove all sub-interfaces from the given interface.

        :param node: Honeycomb node.
        :param super_interface: Super interface.
        :type node: dict
        :type super_interface: str
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces",
                ("interface", "name", super_interface),
                "vpp-vlan:sub-interfaces")

        return InterfaceKeywords._set_interface_properties(
            node, super_interface, path, {})

    @staticmethod
    def set_sub_interface_state(node, super_interface, identifier, state):
        """Set the administrative state of sub-interface.

        :param node: Honeycomb node.
        :param super_interface: Super interface.
        :param identifier: The ID of sub-interface.
        :param state: Required sub-interface state - up or down.
        :type node: dict
        :type super_interface: str
        :type identifier: int
        :type state: str
        :return: Content of response.
        :rtype: bytearray
        """

        intf_state = {"up": "true",
                      "down": "false"}

        path = ("interfaces",
                ("interface", "name", super_interface),
                "vpp-vlan:sub-interfaces",
                ("sub-interface", "identifier", identifier),
                "enabled")

        return InterfaceKeywords._set_interface_properties(
            node, super_interface, path, intf_state[state])

    @staticmethod
    def add_bridge_domain_to_sub_interface(node, super_interface, identifier,
                                           config):
        """Add a sub-interface to a bridge domain and set its parameters.

        :param node: Honeycomb node.
        :param super_interface: Super interface.
        :param identifier: The ID of sub-interface.
        :param config: Bridge domain configuration.
        :type node: dict
        :type super_interface: str
        :type identifier: int
        :type config: dict
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces",
                ("interface", "name", super_interface),
                "vpp-vlan:sub-interfaces",
                ("sub-interface", "identifier", int(identifier)),
                "l2")

        return InterfaceKeywords._set_interface_properties(
            node, super_interface, path, config)

    @staticmethod
    def get_bd_data_from_sub_interface(node, super_interface, identifier):
        """Get the operational data about the bridge domain from sub-interface.

        :param node: Honeycomb node.
        :param super_interface: Super interface.
        :param identifier: The ID of sub-interface.
        :type node: dict
        :type super_interface: str
        :type identifier: int
        :return: Operational data about the bridge domain.
        :rtype: dict
        :raises HoneycombError: If there is no sub-interface with the given ID.
        """

        try:
            bd_data = InterfaceKeywords.get_sub_interface_oper_data(
                node, super_interface, identifier)["l2"]
            return bd_data
        except KeyError:
            raise HoneycombError("The operational data does not contain "
                                 "information about a bridge domain.")

    @staticmethod
    def configure_tag_rewrite(node, super_interface, identifier, config):
        """Add / change / disable vlan tag rewrite on a sub-interface.

        :param node: Honeycomb node.
        :param super_interface: Super interface.
        :param identifier: The ID of sub-interface.
        :param config: Rewrite tag configuration.
        :type node: dict
        :type super_interface: str
        :type identifier: int
        :type config: dict
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces",
                ("interface", "name", super_interface),
                "vpp-vlan:sub-interfaces",
                ("sub-interface", "identifier", int(identifier)),
                "l2",
                "rewrite")

        return InterfaceKeywords._set_interface_properties(
            node, super_interface, path, config)

    @staticmethod
    def get_tag_rewrite_oper_data(node, super_interface, identifier):
        """Get the operational data about tag rewrite.

        :param node: Honeycomb node.
        :param super_interface: Super interface.
        :param identifier: The ID of sub-interface.
        :type node: dict
        :type super_interface: str
        :type identifier: int
        :return: Operational data about tag rewrite.
        :rtype: dict
        :raises HoneycombError: If there is no sub-interface with the given ID.
        """

        try:
            tag_rewrite = InterfaceKeywords.get_sub_interface_oper_data(
                node, super_interface, identifier)["l2"]["rewrite"]
            return tag_rewrite
        except KeyError:
            raise HoneycombError("The operational data does not contain "
                                 "information about the tag-rewrite.")

    @staticmethod
    def add_ipv4_address_to_sub_interface(node, super_interface, identifier,
                                          ip_addr, network):
        """Add an ipv4 address to the specified sub-interface, with the provided
        netmask or network prefix length. Any existing ipv4 addresses on the
        sub-interface will be replaced.

        :param node: Honeycomb node.
        :param super_interface: Super interface.
        :param identifier: The ID of sub-interface.
        :param ip_addr: IPv4 address to be set.
        :param network: Network mask or network prefix length.
        :type node: dict
        :type super_interface: str
        :type identifier: int
        :type ip_addr: str
        :type network: str or int
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the provided netmask or prefix is not valid.
        """

        path = ("interfaces",
                ("interface", "name", super_interface),
                "vpp-vlan:sub-interfaces",
                ("sub-interface", "identifier", int(identifier)),
                "ipv4")

        if isinstance(network, basestring):
            address = {"address": [{"ip": ip_addr, "netmask": network}, ]}

        elif isinstance(network, int) and 0 < network < 33:
            address = {"address": [{"ip": ip_addr, "prefix-length": network}, ]}

        else:
            raise HoneycombError("{0} is not a valid netmask or prefix length."
                                 .format(network))

        return InterfaceKeywords._set_interface_properties(
            node, super_interface, path, address)

    @staticmethod
    def remove_all_ipv4_addresses_from_sub_interface(node, super_interface,
                                                     identifier):
        """Remove all ipv4 addresses from the specified sub-interface.

        :param node: Honeycomb node.
        :param super_interface: Super interface.
        :param identifier: The ID of sub-interface.
        :type node: dict
        :type super_interface: str
        :type identifier: int
        :return: Content of response.
        :rtype: bytearray
        """

        path = ("interfaces",
                ("interface", "name", super_interface),
                "vpp-vlan:sub-interfaces",
                ("sub-interface", "identifier", int(identifier)),
                "ipv4", "address")

        return InterfaceKeywords._set_interface_properties(
            node, super_interface, path, None)

    @staticmethod
    def compare_data_structures(data, ref):
        """Checks if data obtained from UUT is as expected.

        :param data: Data to be checked.
        :param ref: Referential data used for comparison.
        :type data: dict
        :type ref: dict
        :raises HoneycombError: If a parameter from referential data is not
        present in operational data or if it has different value.
        """

        for key, item in ref.items():
            try:
                if data[key] != item:
                    raise HoneycombError("The value of parameter '{0}' is "
                                         "incorrect. It should be "
                                         "'{1}' but it is '{2}'".
                                         format(key, item, data[key]))
            except KeyError:
                raise HoneycombError("The parameter '{0}' is not present in "
                                     "operational data".format(key))

    @staticmethod
    def compare_interface_lists(list1, list2):
        """Compare provided lists of interfaces by name.

        :param list1: List of interfaces.
        :param list2: List of interfaces.
        :type list1: list
        :type list2: list
        :raises HoneycombError: If an interface exists in only one of the lists.
        """

        ignore = ["vx_tunnel0", "vxlan_gpe_tunnel0"]
        # these have no equivalent in config data and no effect on VPP

        names1 = [x['name'] for x in list1]
        names2 = [x['name'] for x in list2]

        for name in names1:
            if name not in names2 and name not in ignore:
                raise HoneycombError("Interface {0} not present in list {1}"
                                     .format(name, list2))
        for name in names2:
            if name not in names1 and name not in ignore:
                raise HoneycombError("Interface {0} not present in list {1}"
                                     .format(name, list1))

    @staticmethod
    def create_vxlan_gpe_interface(node, interface, **kwargs):
        """Create a new VxLAN GPE interface.

        :param node: Honeycomb node.
        :param interface: The name of interface to be created.
        :param kwargs: Parameters and their values. The accepted parameters are
        defined in InterfaceKeywords.VXLAN_GPE_PARAMS.
        :type node: dict
        :type interface: str
        :type kwargs: dict
        :return: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If a parameter in kwargs is not valid.
        """

        new_vxlan_gpe = {
            "name": interface,
            "type": "v3po:vxlan-gpe-tunnel",
            "v3po:vxlan-gpe": {}
        }
        for param, value in kwargs.items():
            if param in InterfaceKeywords.INTF_PARAMS:
                new_vxlan_gpe[param] = value
            elif param in InterfaceKeywords.VXLAN_GPE_PARAMS:
                new_vxlan_gpe["v3po:vxlan-gpe"][param] = value
            else:
                raise HoneycombError("The parameter {0} is invalid.".
                                     format(param))
        path = ("interfaces", "interface")
        vxlan_gpe_structure = [new_vxlan_gpe, ]
        return InterfaceKeywords._set_interface_properties(
            node, interface, path, vxlan_gpe_structure)
