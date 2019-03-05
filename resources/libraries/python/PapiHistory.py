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

"""DUT PAPI command history setup library."""

from robot.api import logger

from resources.libraries.python.topology import NodeType, DICT__nodes

__all__ = ["DICT__DUTS_PAPI_HISTORY", "PapiHistory"]


DICT__DUTS_PAPI_HISTORY = dict()


class PapiHistory(object):
    """Contains methods to set up DUT PAPI command history.
    """

    @staticmethod
    def reset_papi_history(node):
        """Reset PAPI command history for DUT node.

        :param node: DUT node to reset PAPI command history for.
        :type node: dict
        """
        if node['type'] == NodeType.DUT:
            DICT__DUTS_PAPI_HISTORY[node['host']] = list()

    @staticmethod
    def reset_papi_history_on_all_duts(nodes):
        """Reset PAPI command history for all DUT nodes.

        :param nodes: Nodes to reset PAPI command history for.
        :type nodes: dict
        """
        for node in nodes.values():
            PapiHistory.reset_papi_history(node)

    @staticmethod
    def add_to_papi_history(node, cmd, **kwargs):
        """Add command to PAPI command history on DUT node.

        :param node: DUT node to add command to PAPI command history for.
        :param cmd: Command to be added to PAPI command history.
        :param kwargs: Optional key-value arguments.
        :type node: dict
        :type cmd: str
        :type kwargs: dict
        """
        args = list()
        for key, val in kwargs.iteritems():
            args.append("{key}={val}".format(key=key, val=val))
        item = "{cmd}({args})".format(cmd=cmd, args=",".join(args))
        DICT__DUTS_PAPI_HISTORY[node['host']].append(item)

    @staticmethod
    def show_papi_history(node):
        """Show PAPI command history for DUT node.

        :param node: DUT node to show PAPI command history for.
        :type node: dict
        """
        if node['type'] == NodeType.DUT:
            history = "\nNo PAPI command executed"
            if DICT__DUTS_PAPI_HISTORY[node['host']]:
                history = "".join(["\n{}".format(
                    cmd) for cmd in DICT__DUTS_PAPI_HISTORY[node['host']]])
            logger.trace(
                "{0} PAPI command history:{1}\n".format(node['host'], history))

    @staticmethod
    def show_papi_history_on_all_duts(nodes):
        """Show PAPI command history for all DUT nodes.

        :param nodes: Nodes to show PAPI command history for.
        :type nodes: dict
        """
        for node in nodes.values():
            PapiHistory.show_papi_history(node)


PapiHistory.reset_papi_history_on_all_duts(DICT__nodes)
