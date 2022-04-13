# Copyright (c) 2022 Cisco and/or its affiliates.
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

"""Telemetry utility."""

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.OptionString import OptionString
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
from resources.libraries.python.topology import NodeType

__all__ = [u"TelemetryUtil"]


class TelemetryUtil:
    """Class contains methods for telemetry utility."""

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
                TelemetryUtil.perf_stat(
                    node, cpu_list=cpu_list, duration=duration
                )

    @staticmethod
    def run_telemetry(node, profile, hook=None):
        """Get telemetry stat read for duration.

        :param node: Node in the topology.
        :param profile: Telemetry configuration profile.
        :param hook: Process ID or socket path (optional).
        :type node: dict
        :type profile: str
        :type hook: str
        """
        config = u""
        config += f"{Constants.REMOTE_FW_DIR}/"
        config += f"{Constants.RESOURCES_TPL_TELEMETRY}/"
        config += f"{profile}"

        cd_cmd = u""
        cd_cmd += f"sh -c \"cd {Constants.REMOTE_FW_DIR}/"
        cd_cmd += f"{Constants.RESOURCES_TOOLS}"

        if hook is None:
            bin_cmd = f"python3 -m telemetry --config {config}\""
        else:
            bin_cmd = f"python3 -m telemetry --config {config} --hook {hook}\""

        hostname = node[u"host"]

        exec_cmd_no_error(node, f"{cd_cmd} && {bin_cmd}", sudo=True)
        stdout, _ = exec_cmd_no_error(
            node, u"cat /tmp/metric.prom", sudo=True, log_stdout_err=False
        )
        logger.info(
            u"# TYPE target info\n"
            u"# HELP target Target metadata\n"
            f"target_info{{hostname=\"{hostname}\",hook=\"{hook}\"}} 1\n"
            f"{stdout}"
        )

    @staticmethod
    def run_telemetry_on_all_duts(nodes, profile):
        """Get telemetry stat read on all DUTs.

        :param nodes: Nodes in the topology.
        :param profile: Telemetry configuration profile.
        :param hooks: Dict of Process IDs or socket paths (optional).
        :type nodes: dict
        :type profile: str
        :type hooks: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                try:
                    if u"bpf" in profile:
                        TelemetryUtil.run_telemetry(node, profile=profile)
                        continue

                    for socket in node[u"sockets"][u"PAPI"].values():
                        TelemetryUtil.run_telemetry(
                            node, profile=profile, hook=socket
                        )
                except IndexError:
                    pass
