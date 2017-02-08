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

"""DUT VAT command history setup library."""

from robot.api import logger

from resources.libraries.python.topology import NodeType, DICT__nodes

__all__ = ["DICT__duts_vat_history", "VatHistory"]


def setup_vat_history(nodes):
    duts_vat_history = {}
    for node in nodes.values():
        if node['type'] == NodeType.DUT:
            duts_vat_history[node['host']] = []
    return duts_vat_history

DICT__duts_vat_history = setup_vat_history(DICT__nodes)


class VatHistory(object):
    """Contains methods to set up DUT VAT command history."""

    @staticmethod
    def reset_vat_history(node):
        """Reset VAT command history for DUT node.

        :param node: DUT node to reset VAT command history for.
        :type node: dict
        """
        if node['type'] == NodeType.DUT:
            DICT__duts_vat_history[node['host']] = []

    @staticmethod
    def reset_vat_history_on_all_duts(nodes):
        """Reset VAT command history for all DUT nodes.

        :param nodes: Nodes to reset VAT command history for.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VatHistory.reset_vat_history(node)

    @staticmethod
    def show_vat_history(node):
        """Show VAT command history for DUT node.

        :param node: DUT node to show VAT command history for.
        :type node: dict
        """
        if node['type'] == NodeType.DUT:
            sequence = "\nno VAT command executed"\
                if len(DICT__duts_vat_history[node['host']]) == 0\
                else "".join("\n{}".format(cmd)
                             for cmd in DICT__duts_vat_history[node['host']])
            logger.trace("{0} VAT command history:{1}".
                         format(node['host'], sequence))

    @staticmethod
    def show_vat_history_on_all_duts(nodes):
        """Show VAT command history for all DUT nodes.

        :param nodes: Nodes to show VAT command history for.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VatHistory.show_vat_history(node)

    @staticmethod
    def add_to_vat_history(node, cmd):
        """Add command to VAT command history on DUT node.

        :param node: DUT node to add command to VAT command history for.
        :param cmd: Command to be added to VAT command history.
        :return:
        """
        if node['type'] == NodeType.DUT:
            DICT__duts_vat_history[node['host']].append(cmd)
