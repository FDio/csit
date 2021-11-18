# Copyright (c) 2021 Cisco and/or its affiliates.
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

from resources.libraries.python.topology import (
    DICT__nodes, NodeType, SocketType, Topology
)

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
        DICT__DUTS_PAPI_HISTORY[node[u"host"]] = dict()

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
    def add_to_papi_history(node, sock, csit_papi_command, papi=True, **kwargs):
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

        VAT:
            sw_interface_set_flags sw_if_index 3 admin-up link-up

        :param node: DUT node to add command to PAPI command history for.
        :param sock: Filesystem path to remote Unix Domain Socket.
        :param csit_papi_command: Command to be added to PAPI command history.
        :param papi: Says if the command to store is PAPi or VAT. Remove when
            VAT executor is completely removed.
        :param kwargs: Optional key-value arguments.
        :type node: dict
        :type sock: str
        :type csit_papi_command: str
        :type papi: bool
        :type kwargs: dict
        """
        if papi:
            args = list()
            for key, val in kwargs.items():
                args.append(f"{key}={val!r}")
            item = f"{csit_papi_command}({u','.join(args)})"
        else:
            # This else part is here to store VAT commands.
            # VAT history is not used.
            # TODO: Remove when VatExecutor is completely removed.
            item = f"{csit_papi_command}"
        dict_of_socks = DICT__DUTS_PAPI_HISTORY[node[u"host"]]
        list_for_sock = dict_of_socks.get(sock, list())
        list_for_sock.append(item)
        DICT__DUTS_PAPI_HISTORY[node[u"host"]][sock] = list_for_sock

    @staticmethod
    def show_papi_history(node, socket):
        """Show PAPI command history for DUT node.

        :param node: DUT node to show PAPI command history for.
        :param socket: Remote Unix Domain Socket path the PAPI used.
        :type node: dict
        :type socket: str
        """
        history_list = DICT__DUTS_PAPI_HISTORY[node[u"host"]].get(socket)
        if not history_list:
            history_list = (u"No PAPI command executed", )
        history = u'\n'.join(history_list)
        logger.info(f"{node[u'host']} {socket} PAPI history:\n{history}\n")

    @staticmethod
    def show_papi_history_on_all_duts(nodes):
        """Show PAPI command history for all DUT nodes.

        This also iterates over all sockets used on the DUT node.

        :param nodes: Nodes to show PAPI command history for.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                sockets = Topology.get_node_sockets(
                    node, socket_type=SocketType.PAPI
                )
                if sockets:
                    for socket in sockets.values():
                        PapiHistory.show_papi_history(node, socket)

# This module can be imported outside usual Robot test context,
# e.g. in pylint or by tools generating docs from docstrings.
# For the tools to work, we need to avoid processing
# when DICT__nodes value is not usable.
if DICT__nodes:
    PapiHistory.reset_papi_history_on_all_duts(DICT__nodes)
