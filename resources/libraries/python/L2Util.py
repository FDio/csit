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

"""L2 Setup Library."""

from robot.api.deco import keyword
from resources.libraries.python.topology import Topology
from resources.libraries.python.VatExecutor import VatExecutor


class L2Util(object):
    """Utilities for l2 configuration"""

    @staticmethod
    def vpp_add_l2fib_entry(node, mac, interface, bd_id):
        """ Creates a static L2FIB entry on a vpp node.

        :param node: Node to add L2FIB entry on.
        :param mac: Destination mac address.
        :param interface: Interface name.
        :param bd_id: Bridge domain id.
        :type node: dict
        :type mac: str
        :type interface: str
        :type bd_id: int
        """
        sw_if_index = Topology.get_interface_sw_index(node, interface)
        VatExecutor.cmd_from_template(node, "add_l2_fib_entry.vat",
                                      mac=mac, bd=bd_id,
                                      interface=sw_if_index)

    @staticmethod
    @keyword('Setup l2 bridge domain with id "${bd_id}" flooding "${flood}" '
             'forwarding "${forward}" learning "${learn}" and arp termination '
             '"${arp_term}" on vpp node "${node}"')
    def setup_vpp_l2_bridge_domain(bd_id, flood, forward, learn,
                                   arp_term, node):
        """Create a l2 bridge domain on the chosen vpp node

        Executes "bridge_domain_add_del bd_id {bd_id} flood {flood} uu-flood 1
        forward {forward} learn {learn} arp-term {arp_term}" VAT command on
        the node.

        :param node: node where we wish to crate the l2 bridge domain
        :param bd_id: bridge domain index number
        :param flood: enable flooding
        :param forward: enable forwarding
        :param learn: enable mac address learning to fib
        :param arp_term: enable arp_termination
        :type node: dict
        :type bd_id: int
        :type flood: bool
        :type forward: bool
        :type learn: bool
        :type arp_term:bool
        :return:
        """
        VatExecutor.cmd_from_template(node, "l2_bd_create.vat",
                                      bd_id=bd_id, flood=flood,
                                      forward=forward, learn=learn,
                                      arp_term=arp_term)

    @staticmethod
    @keyword('Add interface "${interface}" to l2 bridge domain with index '
             '"${bd_id}" and shg "${shg}" on vpp node "${node}"')
    def add_interface_to_l2_bd(interface, bd_id, shg, node):
        """Adds interface to l2 bridge domain.

        Gets SW IF ID and adds it to the bridge domain.

        :param node: node where we want to execute the command that does this
        :param interface: interface name
        :param bd_id: bridge domain index number to add Interface name to
        :param shg: split horizon group
        :type node: dict
        :type interface: str
        :type bd_id: int
        :type shg: int
        :return:
        """
        topology = Topology()
        sw_if_index = topology.get_interface_sw_index(node, interface)
        L2Util.add_sw_if_index_to_l2_bd(sw_if_index, bd_id, shg, node)

    @staticmethod
    @keyword('Add sw interface index "${sw_if_index}" to l2 bridge domain with'
             ' index "${bd_id}" and shg "${shg}" on vpp node "${node}"')
    def add_sw_if_index_to_l2_bd(sw_if_index, bd_id, shg, node):
        """Adds interface with sw_if_index to l2 bridge domain.

        Executes the "sw_interface_set_l2_bridge sw_if_index {sw_if_index}
         bd_id {bd_id} shg {shg} enable" VAT command on the given node.

        :param sw_if_index: interface index
        :param bd_id: bridge domain index number to add SW IF ID to
        :param shg: split horizon group
        :param node: node where we want to execute the command that does this
        :type sw_if_index: int
        :type bd_id: int
        :type shg: int
        :type node: dict
        :return:
        """
        VatExecutor.cmd_from_template(node, "l2_bd_add_sw_if_index.vat",
                                      bd_id=bd_id, sw_if_index=sw_if_index,
                                      shg=shg)

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
        'bd_id': bridge domain index
        """
        bd_dict = Topology().get_interfaces_by_link_names(node, link_names)
        bd_dict['bd_id'] = bd_id
        return bd_dict

    @staticmethod
    def vpp_add_l2_bridge_domain(node, bd_id, port_1, port_2, learn=True):
        """Add L2 bridge domain with 2 interfaces to the VPP node.

        :param node: Node to add L2BD on.
        :param bd_id: Bridge domain ID.
        :param port_1: First interface name added to L2BD.
        :param port_2: Second interface name addded to L2BD.
        :param learn: Enable/disable MAC learn.
        :type node: dict
        :type bd_id: int
        :type interface1: str
        :type interface2: str
        :type learn: bool
        """
        sw_if_index1 = Topology.get_interface_sw_index(node, port_1)
        sw_if_index2 = Topology.get_interface_sw_index(node, port_2)
        VatExecutor.cmd_from_template(node,
                                      'l2_bridge_domain.vat',
                                      sw_if_id1=sw_if_index1,
                                      sw_if_id2=sw_if_index2,
                                      bd_id=bd_id,
                                      learn=int(learn))
