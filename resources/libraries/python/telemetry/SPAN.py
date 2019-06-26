# Copyright (c) 2019 Cisco and/or its affiliates.
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
from resources.libraries.python.PapiExecutor import PapiExecutor


class SPAN(object):
    """Class contains methods for setting up SPAN mirroring on DUTs."""

    def __init__(self):
        """Initializer."""
        pass

    @staticmethod
    def vpp_get_span_configuration(node, is_l2=False):
        """Get full SPAN configuration from VPP node.

        Used by Honeycomb.

        :param node: DUT node.
        :type node: dict

        :returns: Full SPAN configuration as list. One list entry for every
            source/destination interface pair.
        :rtype: list of dict
        """
        args = dict(
            is_l2=1 if is_l2 else 0
        )
        with PapiExecutor(node) as papi_exec:
            dump = papi_exec.add("sw_interface_span_dump", **args). \
                get_dump().reply[0]["api_reply"]

        return dump

    @staticmethod
    def vpp_get_span_configuration_by_interface(node, dst_interface,
                                                ret_format="sw_if_index"):
        """Get a list of all interfaces currently being mirrored
        to the specified interface.

        Used by Honeycomb.

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

        dst_int = Topology.convert_interface_reference(
            node, dst_interface, "sw_if_index")
        src_interfaces = []
        for item in data:
            if item["sw_interface_span_details"]["sw_if_index_to"] == dst_int:
                src_interfaces.append(
                    item["sw_interface_span_details"]["sw_if_index_from"])

        if ret_format != "sw_if_index":
            src_interfaces = [
                Topology.convert_interface_reference(
                    node, interface, ret_format
                ) for interface in src_interfaces]

        return src_interfaces
