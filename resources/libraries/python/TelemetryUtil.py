# Copyright (c) 2023 Cisco and/or its affiliates.
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
    def _run_telemetry(
            node, profile, sid=None, spath=None, rate="", export=False):
        """Get telemetry read on node.

        The special rate value "teardown" means the test failed
        and there is additional trial at some small load.
        In that case, we want to run the telemetry without export,
        regardless of export argument value.

        :param node: Node in the topology.
        :param profile: Telemetry configuration profile.
        :param sid: Socket ID used to describe recipient side of socket.
        :param spath: Socket path.
        :param rate: Telemetry load, unique within the test (optional).
        :param export: If false, do not attempt JSON export (default false).
        :type node: dict
        :type profile: str
        :type sid: str
        :type spath: str
        :type rate: str
        :type export: bool
        """
        config = ""
        config += f"{Constants.REMOTE_FW_DIR}/"
        config += f"{Constants.RESOURCES_TPL_TELEMETRY}/"
        config += f"{profile}"

        cd_cmd = ""
        cd_cmd += f"sh -c \"cd {Constants.REMOTE_FW_DIR}/"
        cd_cmd += f"{Constants.RESOURCES_TOOLS}"

        if spath:
            bin_cmd = f"python3 -m telemetry --config {config} --hook {spath}\""
        else:
            bin_cmd = f"python3 -m telemetry --config {config}\""
        exec_cmd_no_error(node, f"{cd_cmd} && {bin_cmd}", sudo=True)

        if not export or rate == "teardown":
            return

        hostname = exec_cmd_no_error(node, "hostname")[0].strip()
        stdout, _ = exec_cmd_no_error(
            node, "cat /tmp/metric.prom", sudo=True, log_stdout_err=False
        )
        prefix = "{"
        prefix += f"hostname=\"{hostname}\","
        if sid:
            prefix += f"hook=\"{sid}\","
        prefix += f"rate=\"{rate}\","
        for line in stdout.splitlines():
            if line and not line.startswith("#"):
                append_telemetry(
                    prefix.join(line.rsplit("{", 1)).replace("\"", "'")
                )

    def run_telemetry_on_all_duts(self, nodes, profile, rate="", export=False):
        """Get telemetry read on all DUTs.

        :param nodes: Nodes in the topology.
        :param profile: Telemetry configuration profile.
        :param rate: Telemetry load, unique within the test (optional).
        :param export: If false, do not attempt JSON export (default false).
        :type nodes: dict
        :type profile: str
        :type rate: str
        :type export: bool
        """
        for node in nodes.values():
            if node["type"] == NodeType.DUT:
                try:
                    for sid, spath in node["sockets"]["CLI"].items():
                        self._run_telemetry(
                            node, profile=profile, sid=sid, spath=spath,
                            rate=rate, export=export
                        )
                except IndexError:
                    pass
