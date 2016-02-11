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

"""L2 bridge domain utilities Library."""

from robot.api.deco import keyword
from resources.libraries.python.topology import Topology
from resources.libraries.python.VatExecutor import VatExecutor


class L2Util(object):
    """Utilities for l2 bridge domain configuration"""

    def __init__(self):
        pass

    @staticmethod
    @keyword('Setup static L2FIB entry on node "${node}" for MAC "${dst_mac}"'
             ' link "${link}" pair on bd_index "${bd_id}"')
    def static_l2_fib_entry_via_links(node, dst_mac, link, bd_id):
        """ Creates a static fib entry on a vpp node

        :param node: node where we wish to add the static fib entry
        :param dst_mac: destination mac address in the entry
        :param link: link name of the node destination interface
        :param bd_id: l2 bridge domain id
        :type node: dict
        :type dst_mac: str
        :type link: str
        :type bd_id: str
        """
        topology = Topology()
        interface_name = topology.get_interface_by_link_name(node, link)
        sw_if_index = topology.get_interface_sw_index(node, interface_name)
        VatExecutor.cmd_from_template(node, "add_l2_fib_entry.vat",
                                      mac=dst_mac, bd=bd_id,
                                      interface=sw_if_index)

    @staticmethod
    @keyword('Setup l2 bridge domain with id "${bd_id}" flooding "${flood}" '
             'forwarding "${forward}" learning "${learn}" and arp termination '
             '"${arp_term}" on vpp node "${node}"')
    def setup_vpp_l2_bridge_domain(node, bd_id, flood, forward, learn,
                                   arp_term):
        """Create a l2 bridge domain on the chosen vpp node

        Executes "bridge_domain_add_del bd_id {bd_id} flood {flood} uu-flood 1
        forward {forward} learn {learn} arp-term {arp_term}" VAT command on
        the node.
        For the moment acts as a placeholder
        :param node: node where we wish to crate the l2 bridge domain
        :param bd_id: bridge domain id
        :param flood: enable flooding
        :param forward: enable forwarding
        :param learn: enable mac address learning to fib
        :param arp_term: enable arp_termination
        :type node: str
        :type bd_id: str
        :type flood: bool
        :type forward: bool
        :type learn: bool
        :type arp_term:bool
        :return:
        """
        pass

    @keyword('Add interface "${interface}" to l2 bridge domain with index '
             '"${bd_id}" and shg "${shg}" on vpp node "${node}"')
    def add_interface_to_l2_bd(self, node, interface, bd_id, shg):
        """Adds interface to l2 bridge domain.

        Executes the "sw_interface_set_l2_bridge {interface1} bd_id {bd_id}
         shg {shg} enable" VAT command on the given node.
        For the moment acts as a placeholder
        :param node: node where we want to execute the command that does this.
        :param interface:
        :param bd_id:
        :param shg:
        :type node: dict
        :type interface: str
        :type bd_id: str
        :type shg: str
        :return:
        """
        pass

    @staticmethod
    @keyword('Create dict used in bridge domain template file for node '
             '"${node}" with links "${link_names}" and bd_id "${bd_id}"')
    def create_bridge_domain_vat_dict(node, link_names, bd_id):
        """Creates dictionary that can be used in l2 bridge domain template.

        :param node: node data dictionary
        :param link_names: list of names of links the bridge domain should be
        connecting
        :param bd_id: bridge domain index number
        :type node: dict
        :type link_names: list
        :return: dictionary used to generate l2 bridge domain VAT configuration
        from template file
        The resulting dictionary looks like this:
        'interface1': interface name of first interface
        'interface2': interface name of second interface
        'bd_id': bridge domian index
        """
        bd_dict = Topology().get_interfaces_by_link_names(node, link_names)
        bd_dict['bd_id'] = bd_id
        return bd_dict

