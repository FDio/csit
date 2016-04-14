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

"""Keywords used with Honeycomb.

There are implemented keywords which work with:
- Honeycomb operations
- VPP Interfaces
- Bridge domains

The keywords make possible to put and get configuration data and to get
operational data.
"""

from json import dumps

from robot.api import logger

from resources.libraries.python.HTTPRequest import HTTPCodes
from resources.libraries.python.HoneycombSetup import HoneycombError
from resources.libraries.python.HoneycombUtil import HoneycombUtil as HcUtil
from resources.libraries.python.HoneycombUtil import DataRepresentation


class OperationsKeywords(object):
    """Keywords which perform "operations" in Honeycomb.

    The keywords in this class are not a part of a specific area in Honeycomb,
    e.g.: interfaces or bridge domains, but they perform "operations" in any
    area of Honeycomb.
    """

    def __init__(self):
        pass

    @staticmethod
    def poll_oper_data(node):
        """Poll operational data.

        You can use this keyword when you configure something in Honeycomb and
        you want configuration data to make effect immediately, e.g.:

        | | Create Bridge Domain | ....
        | | Add Bridge Domain To Interface | ....
        | | Poll Oper Data | ....
        | | ${br}= | Get Oper Info About Bridge Domain | ....

        ..note:: This is not very reliable way how to poll operational data.
        This keyword is only temporary workaround and will be removed when this
        problem is solved in Honeycomb.
        :param node: Honeycomb node.
        :type: dict
        :raises HoneycombError: If it is not possible to poll operational data.
        """

        status_code, _ = HcUtil.\
            post_honeycomb_data(node, "poll_oper_data", data='',
                                data_representation=DataRepresentation.NO_DATA,
                                timeout=30)
        if status_code != HTTPCodes.OK:
            raise HoneycombError("It was not possible to poll operational data "
                                 "on node {0}.".format(node['host']))


class InterfaceKeywords(object):
    """Keywords for Interface manipulation.

    Implements keywords which get configuration and operational data about
    vpp interfaces and set the interface's parameters using Honeycomb REST API.
    """

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
        :type data: str
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

        status_code, resp = HcUtil.get_honeycomb_data(node,
                                                      "config_vpp_interfaces")
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get configuration information about the "
                "interfaces. Status code: {0}.".format(status_code))
        try:
            intf = HcUtil.parse_json_response(resp, ("interfaces", "interface"))
            return intf
        except KeyError:
            return []

    @staticmethod
    def get_interface_cfg_info(node, interface):
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
    def get_all_interfaces_oper_info(node):
        """Get operational data about all interfaces from Honeycomb.

        :param node: Honeycomb node.
        :type node: dict
        :return: Operational data about all interfaces from Honeycomb.
        :rtype: list
        :raises HoneycombError: If it is not possible to get operational data.
        """

        status_code, resp = HcUtil.get_honeycomb_data(node,
                                                      "oper_vpp_interfaces")
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get operational information about the "
                "interfaces. Status code: {0}.".format(status_code))
        try:
            intf = HcUtil.parse_json_response(resp, ("interfaces-state",
                                                     "interface"))
            return intf
        except KeyError:
            return []

    @staticmethod
    def get_interface_oper_info(node, interface):
        """Get operational data about the given interface from Honeycomb.

        :param node: Honeycomb node.
        :param interface: The name of interface.
        :type node: dict
        :type interface: str
        :return: Operational data about the given interface from Honeycomb.
        :rtype: dict
        """

        intfs = InterfaceKeywords.get_all_interfaces_oper_info(node)
        for intf in intfs:
            if intf["name"] == interface:
                return intf
        return {}

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
        intfs = InterfaceKeywords.get_all_interfaces_cfg_data(node)
        for intf in intfs:
            if intf["name"] == interface:
                intf["enabled"] = intf_state[state.lower()]
                new_intf = {"interfaces": {"interface": intfs}}
                return InterfaceKeywords._configure_interface(node, interface,
                                                              dumps(new_intf))
        raise HoneycombError("The interface '{0}' is not present on node "
                             "'{1}'.".format(interface, node['host']))

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

        intfs = InterfaceKeywords.get_all_interfaces_cfg_data(node)
        v3po_l2 = {"bridge-domain": str(bd_name)}
        if split_horizon_group:
            v3po_l2["split-horizon-group"] = str(split_horizon_group)
        if bvi:
            v3po_l2["bridged-virtual-interface"] = str(bvi)
        for intf in intfs:
            if intf["name"] == interface:
                intf["v3po:l2"] = v3po_l2
                new_intf = {"interfaces": {"interface": intfs}}
                return InterfaceKeywords._configure_interface(node, interface,
                                                              dumps(new_intf))
        raise HoneycombError("The interface '{0}' is not present on node "
                             "'{1}'.".format(interface, node['host']))


class BridgeDomainKeywords(object):
    """Keywords for Bridge domain manipulation.

    Implements keywords which get configuration and operational data about
    bridge domains and put the bridge domains' parameters using Honeycomb REST
    API.
    """

    def __init__(self):
        pass

    @staticmethod
    def _create_json_bridge_domain_info(name, **kwargs):
        """Generate bridge domain information in the structure as it is expected
        by Honeycomb.

        The generated data structure is as follows:
        {
            "bridge-domains": {
                "bridge-domain": [
                    {
                        "name": "bd_name",
                        "flood": "false",
                        "forward": "false",
                        "learn": "false",
                        "unknown-unicast-flood": "false",
                        "arp-termination": "false"
                    }
                ]
            }
        }

        :param name: The name of new bridge-domain.
        :param kwargs: named arguments:
            flood (bool): If True, flooding is enabled.
            forward (bool): If True, packet forwarding is enabled.
            learn (bool): If True, learning is enabled.
            uu_flood (bool): If True, unknown unicast flooding is enabled.
            arp_termination (bool): If True, ARP termination is enabled.
        :type name: str
        :type kwargs: dict
        :return: Bridge domain information in format suitable for Honeycomb.
        :rtype: dict
        :raises KeyError: If at least one of kwargs items is missing.
        """

        brd_info = {
            "bridge-domains": {
                "bridge-domain": [
                    {"name": name,
                     "flood": str(kwargs["flood"]).lower(),
                     "forward": str(kwargs["forward"]).lower(),
                     "learn": str(kwargs["learn"]).lower(),
                     "unknown-unicast-flood": str(kwargs["uu_flood"]).lower(),
                     "arp-termination": str(kwargs["arp_termination"]).lower()},
                ]
            }
        }

        return brd_info

    @staticmethod
    def create_bridge_domain(node, name, flood=True, forward=True, learn=True,
                             uu_flood=True, arp_termination=False):
        """Create a bridge domain using Honeycomb.

        This keyword adds a new bridge domain to the list of bridge domains and
        sets its parameters. The existing bridge domains are untouched.
        :param node: Node with Honeycomb where the bridge domain should be
        created.
        :param name: The name of new bridge-domain.
        :param flood: If True, flooding is enabled.
        :param forward: If True, packet forwarding is enabled.
        :param learn: If True, learning is enabled.
        :param uu_flood: If True, unknown unicast flooding is enabled.
        :param arp_termination: If True, ARP termination is enabled.
        :type node: dict
        :type name: str
        :type flood: bool
        :type forward: bool
        :type learn: bool
        :type uu_flood: bool
        :type arp_termination: bool
        :raises HoneycombError: If the bridge domain already exists or it has
        not been created.
        """

        existing_brds = BridgeDomainKeywords.get_all_bds_cfg_data(node, True)

        for brd in existing_brds:
            if brd["name"] == name:
                raise HoneycombError("Bridge domain {0} already exists.".
                                     format(name))

        brd_info = BridgeDomainKeywords._create_json_bridge_domain_info(
            name, flood=flood, forward=forward, learn=learn, uu_flood=uu_flood,
            arp_termination=arp_termination)
        for brd in existing_brds:
            brd_info["bridge-domains"]["bridge-domain"].append(brd)

        status_code, _ = HcUtil.put_honeycomb_data(node, "config_bridge_domain",
                                                   dumps(brd_info))
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Bridge domain {0} was not created. "
                "Status code: {01}.".format(name, status_code))

    @staticmethod
    def get_all_bds_oper_data(node):
        """Get operational data about all bridge domains from Honeycomb.

        :param node: Honeycomb node.
        :type node: dict
        :return: Operational data about all bridge domains from Honeycomb.
        :rtype: list
        :raises HoneycombError: If it is not possible to get information about
        the bridge domains.
        """

        status_code, resp = HcUtil.get_honeycomb_data(node,
                                                      "oper_bridge_domains")
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get information about the bridge domains. "
                "Status code: {0}.".format(status_code))
        try:
            br_domains = HcUtil.parse_json_response(resp, ("bridge-domains",
                                                           "bridge-domain"))
        except KeyError:
            return []
        return br_domains

    @staticmethod
    def get_bd_oper_data(node, name):
        """Get operational data about the given bridge domain from Honeycomb.

        :param node: Honeycomb node.
        :param name: The name of bridge domain.
        :type node: dict
        :type name: str
        :return: Operational data about the given bridge domain from Honeycomb.
        :rtype: dict
        """

        br_domains = BridgeDomainKeywords.get_all_bds_oper_data(node)
        for br_domain in br_domains:
            if br_domain["name"] == name:
                br_domain["name"] = br_domain["name"]
                return br_domain
        return {}

    @staticmethod
    def get_all_bds_cfg_data(node, ignore_404=False):
        """Get configuration data about all bridge domains from Honeycomb.

        :param node: Honeycomb node.
        :param ignore_404: If True, the error 404 is ignored.
        :type node: dict
        :type ignore_404: bool
        :return: Configuration data about all bridge domains from Honeycomb.
        :rtype: list
        :raises HoneycombError: If it is not possible to get information about
        the bridge domains.
        """

        status_code, resp = HcUtil.get_honeycomb_data(node,
                                                      "config_bridge_domain")
        if status_code != HTTPCodes.OK:
            if ignore_404 and status_code == HTTPCodes.NOT_FOUND:
                br_domains = list()
                logger.debug("Error 404 ignored")
            else:
                raise HoneycombError(
                    "Not possible to get information about the bridge domains. "
                    "Status code: {0}.".format(status_code))
        else:
            try:
                br_domains = HcUtil.parse_json_response(resp, ("bridge-domains",
                                                               "bridge-domain"))
            except KeyError:
                return []
        return br_domains

    @staticmethod
    def get_bd_cfg_data(node, name):
        """Get configuration data about the given bridge domain from Honeycomb.

        :param node: Honeycomb node.
        :param name: The name of bridge domain.
        :type node: dict
        :type name: str
        :return: Configuration data about the given bridge domain from
        Honeycomb.
        :rtype: dict
        """

        br_domains = BridgeDomainKeywords.get_all_bds_cfg_data(node)
        for br_domain in br_domains:
            if br_domain["name"] == name:
                return br_domain
        return {}

    @staticmethod
    def delete_all_bridge_domains(node):
        """Delete all bridge domains on Honeycomb node.

        :param node: Honeycomb node.
        :type node: dict
        :return: Response from DELETE request.
        :rtype: str
        :raises HoneycombError: If it is not possible to delete all bridge
        domains.
        """

        status_code, resp = HcUtil.delete_honeycomb_data(node,
                                                         "config_bridge_domain")
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to delete all bridge domains. "
                "Status code: {0}.".format(status_code))
        return resp

    @staticmethod
    def remove_bridge_domain(node, name):
        """Remove one bridge domain from Honeycomb.

        :param node: Honeycomb node.
        :param name: Name of the bridge domain to be removed.
        :type node: dict
        :type name: str
        :return: True if the bridge domain was removed.
        :rtype: bool
        :raises HoneycombError: If it is not possible to remove the bridge
        domain.
        """

        br_domains = BridgeDomainKeywords.get_all_bds_cfg_data(node)
        for br_domain in br_domains:
            if br_domain["name"] == name:
                br_domains.remove(br_domain)
                brd_info = {"bridge-domains": {"bridge-domain": br_domains}}
                status_code, _ = HcUtil.put_honeycomb_data(
                    node, "config_bridge_domain", dumps(brd_info))
                if status_code != HTTPCodes.OK:
                    raise HoneycombError(
                        "Bridge domain '{0}' was not deleted. "
                        "Status code: {1}.".format(name, status_code))
                return True

        raise HoneycombError("Not possible to delete bridge domain '{0}'. The "
                             "bridge domain was not found".format(name))
