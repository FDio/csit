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

"""Packet trace library."""

from robot.api import logger

from resources.libraries.python.PapiExecutor import PapiExecutor
from resources.libraries.python.topology import NodeType

# TODO: Remove
from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal



class Trace(object):
    """This class provides methods to manipulate the VPP packet trace."""

    @staticmethod
    def show_packet_trace_on_all_duts(nodes, maximum=None):
        """Show VPP packet trace.

        :param nodes: Nodes from which the packet trace will be displayed.
        :param maximum: Maximum number of packet traces to be displayed.
        :type nodes: dict
        :type maximum: int
        """
        maximum = "max {count}".format(count=maximum) if maximum is not None\
            else ""

        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                PapiExecutor.run_cli_cmd(node, cmd="show trace {max}".
                                         format(max=maximum))

                args = dict(path='^/')
                with PapiExecutor(node) as papi_exec:
                    stats = papi_exec.add("vpp-stats", **args).get_stats()[0]
                logger.info(stats)

                # TODO: Remove
                with VatTerminal(node, json_param=False) as vat:
                    vat.vat_terminal_exec_cmd_from_template(
                        'show_trace.vat', maximum=maximum)

    @staticmethod
    def clear_packet_trace_on_all_duts(nodes):
        """Clear VPP packet trace.

        :param nodes: Nodes where the packet trace will be cleared.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                PapiExecutor.run_cli_cmd(node, cmd="clear trace")

                # TODO: Remove
                vat = VatExecutor()
                vat.execute_script("clear_trace.vat", node, json_out=False)
