# Copyright (c) 2020 Cisco and/or its affiliates.
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

"""Packet trace library."""

from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.topology import NodeType, Topology


class Trace:
    """This class provides methods to manipulate the VPP packet trace."""

    @staticmethod
    def show_packet_trace_on_all_duts(nodes, maximum=None):
        """Show VPP packet trace.

        :param nodes: Nodes from which the packet trace will be displayed.
        :param maximum: Maximum number of packet traces to be displayed.
        :type nodes: dict
        :type maximum: int
        """
        max_opt = f"" if maximum is None else f" max {maximum}"
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                PapiSocketExecutor.run_cli_cmd_on_all_sockets(
                    node, f"show trace{max_opt}")

    @staticmethod
    def clear_packet_trace_on_all_duts(nodes):
        """Clear VPP packet trace.

        :param nodes: Nodes where the packet trace will be cleared.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                PapiSocketExecutor.run_cli_cmd_on_all_sockets(
                    node, u"clear trace")

    @staticmethod
    def pcap_trace_on(node, pkt_filter, pkt_limit, interface, file):
        """Start packet capturing by VPP.

        :param node: Node where to start packet capturing.
        :param pkt_filter: Packet filter (can be a combination of values):
            - rx => capture received packets,
            - tx => capture transmitted packets,
            - drop => capture dropped packets.
        :param pkt_limit: Depth of local buffer. Once given number of packets
        have been received, buffer is flushed to a file. Once another given
        number of packets have been received, buffer is flushed to file,
        overwriting previous write.
        :param interface: Interface key of interface where to capture packets.
        :param file: Name of the output file. The file will be placed in /tmp
        directory.
        :type node: dict
        :type pkt_filter: str
        :type pkt_limit: int
        :type interface: str
        :type file: str
        """
        ifc_name = Topology.get_interface_name(node, interface)
        PapiSocketExecutor.run_cli_cmd_on_all_sockets(
            node,
            f"pcap trace {pkt_filter} max {pkt_limit} intfc {ifc_name} "
            f"file {file}"
        )

    @staticmethod
    def pcap_trace_off(node):
        """Stop packet capturing by VPP.

        :param node: Node where to stop packet capturing.
        :type node: dict
        """
        PapiSocketExecutor.run_cli_cmd_on_all_sockets(
            node, f"pcap trace off"
        )
