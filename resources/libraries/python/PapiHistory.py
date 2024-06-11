# Copyright (c) 2024 Cisco and/or its affiliates.
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

"""DUT PAPI command history setup library."""

from robot.api import logger

from resources.libraries.python.topology import NodeType, DICT__nodes

__all__ = [u"DICT__DUTS_PAPI_HISTORY", u"PapiHistory"]


DICT__DUTS_PAPI_HISTORY = dict()


class PapiHistory:
    """Contains methods to set up DUT PAPI command history.
    """

    @staticmethod
    def reset_papi_history(node):
        """Reset PAPI command history for DUT node.

        :param node: DUT node to reset PAPI command history for.
        :type node: dict
        """
        DICT__DUTS_PAPI_HISTORY[node[u"host"]] = list()

    @staticmethod
    def reset_papi_history_on_all_duts(nodes):
        """Reset PAPI command history for all DUT nodes.

        :param nodes: Nodes to reset PAPI command history for.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                PapiHistory.reset_papi_history(node)

    @staticmethod
    def add_to_papi_history(node, csit_papi_command, **kwargs):
        """Add command to PAPI command history on DUT node.

        Repr strings are used for argument values.

        The argument name 'csit_papi_command' must be unique enough as it cannot
        be repeated in kwargs.

        Examples of PAPI history items:

        Request without parameters:
            show_threads()

        Request with parameters:
            ipsec_select_backend(index=1,protocol=1)

        Dump:
            sw_interface_rx_placement_dump(sw_if_index=4)

        VPP Stats:
            vpp-stats(path=['^/if', '/err/ip4-input', '/sys/node/ip4-input'])

        :param node: DUT node to add command to PAPI command history for.
        :param csit_papi_command: Command to be added to PAPI command history.
        :param kwargs: Optional key-value arguments.
        :type node: dict
        :type csit_papi_command: str
        :type kwargs: dict
        """
        args = list()
        for key, val in kwargs.items():
            args.append(f"{key}={val!r}")
        item = f"{csit_papi_command}({u','.join(args)})"
        DICT__DUTS_PAPI_HISTORY[node[u"host"]].append(item)

    @staticmethod
    def show_papi_history(node):
        """Show PAPI command history for DUT node.

        :param node: DUT node to show PAPI command history for.
        :type node: dict
        """
        history_list = DICT__DUTS_PAPI_HISTORY[node[u"host"]]
        if not history_list:
            history_list = (u"No PAPI command executed", )
        history = u'\n'.join(history_list)
        logger.info(f"{node[u'host']} PAPI command history:\n{history}\n")


# This module can be imported outside usual Robot test context,
# e.g. in pylint or by tools generating docs from docstrings.
# For the tools to work, we need to avoid processing
# when DICT__nodes value is not usable.
if DICT__nodes:
    PapiHistory.reset_papi_history_on_all_duts(DICT__nodes)
