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
from resources.libraries.python.OptionString import OptionString
from resources.libraries.python.ssh import exec_cmd
from resources.libraries.python.topology import NodeType

__all__ = [u"PerfUtil"]


class PerfUtil:
    """Class contains methods for perf utility."""

    @staticmethod
    def perf_stat(node, cpu_list=None, duration=1):
        """Get perf stat read for duration.

        :param node: Node in the topology.
        :param cpu_list: CPU List as a string separated by comma.
        :param duration: Measure time in seconds.
        :type node: dict
        :type cpu_list: str
        :type duration: int
        """
        if cpu_list:
            cpu_list = list(dict.fromkeys(cpu_list.split(u",")))
            cpu_list = ",".join(str(cpu) for cpu in cpu_list)

        cmd_opts = OptionString(prefix=u"--")
        cmd_opts.add(u"no-aggr")
        cmd_opts.add_with_value_if(
            u"cpu", cpu_list, cpu_list
        )
        cmd_opts.add_if(
            u"all-cpus", not(cpu_list)
        )
        cmd_opts.add_with_value_if(
            u"event", f"'{{{Constants.PERF_STAT_EVENTS}}}'",
            Constants.PERF_STAT_EVENTS
        )
        cmd_opts.add_with_value(
            u"interval-print", 1000
        )
        cmd_opts.add_with_value(
            u"field-separator", u"';'"
        )

        cmd_base = OptionString()
        cmd_base.add(f"perf stat")
        cmd_base.extend(cmd_opts)
        cmd_base.add(u"--")
        cmd_base.add_with_value(u"sleep", int(duration))

        exec_cmd(node, cmd_base, sudo=True)

    @staticmethod
    def perf_stat_on_all_duts(nodes, cpu_list=None, duration=1):
        """Get perf stat read for duration on all DUTs.

        :param nodes: Nodes in the topology.
        :param cpu_list: CPU List.
        :param duration: Measure time in seconds.
        :type nodes: dict
        :type cpu_list: str
        :type duration: int
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                PerfUtil.perf_stat(node, cpu_list=cpu_list, duration=duration)
