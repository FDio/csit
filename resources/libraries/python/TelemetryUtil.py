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

from resources.libraries.python.model.ExportResult import append_telemetry
from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType

__all__ = ["TelemetryUtil"]


class TelemetryUtil:
    """Class contains methods for telemetry utility."""

    @staticmethod
    def run_telemetry(node, profile, hook=None, oload="", export=False):
        """Get telemetry read on node.

        :param node: Node in the topology.
        :param profile: Telemetry configuration profile.
        :param hook: Process IDs or socket paths (optional).
        :param oload: Telemetry offered load, unique within the test (optional).
        :param export: If false, do not attempt JSON export (default false).
        :type node: dict
        :type profile: str
        :type hook: dict
        :type oload: str
        :type export: bool
        """
        config = ""
        config += f"{Constants.REMOTE_FW_DIR}/"
        config += f"{Constants.RESOURCES_TPL_TELEMETRY}/"
        config += f"{profile}"

        cd_cmd = ""
        cd_cmd += f"sh -c \"cd {Constants.REMOTE_FW_DIR}/"
        cd_cmd += f"{Constants.RESOURCES_TOOLS}"

        bin_cmd = f"python3 -m telemetry --config {config} --hook {hook}\""
        hostname = exec_cmd_no_error(node, "hostname")[0].strip()
        hook = list(node["sockets"]["CLI"].keys())[
            list(node["sockets"]["CLI"].values()).index(hook)
        ]

        exec_cmd_no_error(node, f"{cd_cmd} && {bin_cmd}", sudo=True)

        if not export:
            return
        stdout, _ = exec_cmd_no_error(
            node, "cat /tmp/metric.prom", sudo=True, log_stdout_err=False
        )
        prefix = "{"
        prefix += f"hostname=\"{hostname}\","
        prefix += f"hook=\"{hook}\","
        prefix += f"oload=\"{oload}\","
        for line in stdout.splitlines():
            if line and not line.startswith("#"):
                append_telemetry(
                    prefix.join(line.rsplit("{", 1)).replace("\"", "'")
                )

    @staticmethod
    def run_telemetry_on_all_duts(nodes, profile, oload="", export=False):
        """Get telemetry read on all DUTs.

        :param nodes: Nodes in the topology.
        :param profile: Telemetry configuration profile.
        :param oload: Telemetry offered load, unique within the test (optional).
        :param export: If false, do not attempt JSON export (default false).
        :type nodes: dict
        :type profile: str
        :type oload: str
        :type export: bool
        """
        for node in nodes.values():
            if node["type"] == NodeType.DUT:
                try:
                    for hook in node["sockets"]["CLI"].values():
                        TelemetryUtil.run_telemetry(
                            node, profile=profile, hook=hook, oload=oload,
                            export=export
                        )
                except IndexError:
                    pass
