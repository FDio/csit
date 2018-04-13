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

"""SPAN setup library"""

from resources.libraries.python.topology import Topology
from resources.libraries.python.VatExecutor import VatTerminal


class SPAN(object):
    """Class contains methods for setting up SPAN mirroring on DUTs."""

    def __init__(self):
        """Initializer."""
        pass

    @staticmethod
    def set_span_mirroring(node, src_if, dst_if):
        """Set Span mirroring on the specified node.

        :param node: DUT node.
        :param src_if: Interface to mirror traffic from.
        :param dst_if: Interface to mirror traffic to.
        :type node: dict
        :type src_if: str
        :type dst_if: str
        """

        src_if = Topology.get_interface_sw_index(node, src_if)
        dst_if = Topology.get_interface_sw_index(node, dst_if)

        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template('span_create.vat',
                                                    src_sw_if_index=src_if,
                                                    dst_sw_if_index=dst_if)

    @staticmethod
    def vpp_get_span_configuration(node):
        """Get full SPAN configuration from VPP node.

        :param node: DUT node.
        :type node: dict
        :returns: Full SPAN configuration as list. One list entry for every
            source/destination interface pair.
        :rtype: list of dict
        """

        with VatTerminal(node, json_param=True) as vat:
            data = vat.vat_terminal_exec_cmd_from_template('span_dump.vat')
            return data[0]

    @staticmethod
    def vpp_get_span_configuration_by_interface(node, dst_interface,
                                                ret_format="sw_if_index"):
        """Get a list of all interfaces currently being mirrored
        to the specified interface.

        :param node: DUT node.
        :param dst_interface: Name, sw_if_index or key of interface.
        :param ret_format: Optional. Desired format of returned interfaces.
        :type node: dict
        :type dst_interface: str or int
        :type ret_format: string
        :returns: List of SPAN source interfaces for the provided destination
            interface.
        :rtype: list
        """

        data = SPAN.vpp_get_span_configuration(node)

        dst_interface = Topology.convert_interface_reference(
            node, dst_interface, "sw_if_index")
        src_interfaces = []
        for item in data:
            if item["dst-if-index"] == dst_interface:
                src_interfaces.append(item["src-if-index"])

        if ret_format != "sw_if_index":
            src_interfaces = [
                Topology.convert_interface_reference(
                    node, interface, ret_format
                ) for interface in src_interfaces]

        return src_interfaces
