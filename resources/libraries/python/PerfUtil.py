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

"""Linux perf utility."""

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd
from resources.libraries.python.topology import NodeType

__all__ = [u"PerfUtil"]


class PerfUtil:
    """Class contains methods for perf utility."""

    @staticmethod
    def perf_stat(node, cpu_list, duration=1):
        """Get perf stat read for duration.

        :param node: Node in the topology.
        :param cpu_list: CPU List.
        :param duration: Measure time in seconds.
        :type node: dict
        :type cpu_list: bool
        :type duration: int
        """
        command = (
            u"perf stat"
            f" --cpu {cpu_list} --no-aggr"
            f" --event '{{{Constants.PERF_STAT_EVENTS}}}'"
            f" -- sleep {int(duration)}"
        )
        exec_cmd(node, command, sudo=True)

    @staticmethod
    def perf_stat_on_all_duts(nodes, cpu_list, duration=1):
        """Get perf stat read for duration on all DUTs.

        :param nodes: Nodes in the topology.
        :param cpu_list: CPU List.
        :param duration: Measure time in seconds.
        :type nodes: dict
        :type cpu_list: bool
        :type duration: int
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                PerfUtil.perf_stat(node, cpu_list, duration=duration)
