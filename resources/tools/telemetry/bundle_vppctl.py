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

"""VPP execution bundle."""

from logging import getLogger
from re import fullmatch, sub
import subprocess
import sys

from .constants import Constants

M_RUN_THREAD = (
    r"Thread\s"
    r"(?P<thread_id>\d+)\s"
    r"(?P<thread_name>\S+)\s.*"
    r"(?P<thread_lcore>\d+).*"
)
M_RUN_SEPARATOR = (
    r"(-)+"
)
M_RUN_NODES = (
    r"(?P<node_name>\S+)\s+"
    r"(?P<state>\S+\s\S+|\S+)\s+"
    r"(?P<calls>\d+)\s+"
    r"(?P<vectors>\d+)\s+"
    r"(?P<suspends>\d+)\s+"
    r"(?P<clocks>\S+)\s+"
    r"(?P<vectors_calls>\S+)"
)
M_RUN_TIME = (
    r"Time\s\S+,\s\d+\ssec\sinternal\snode\svector\srate\s"
    r"(?P<rate>\S+)\sloops/sec\s"
    r"(?P<loops>\S+)"
)
M_INT_BEGIN = (
    r"(?P<name>\S+)\s+"
    r"(?P<index>\S+)\s+"
    r"(?P<state>\S+)\s+"
    r"(?P<mtu>\S+)\s+"
    r"(?P<counter>\S+\s\S+|\S+)\s+"
    r"(?P<count>\d+)"
)
M_INT_CONT = (
    r"\s+"
    r"(?P<counter>\S+\s\S+|\S+)\s+"
    r"(?P<count>\d+)"
)
M_NODE_COUNTERS_THREAD = (
    r"Thread\s"
    r"(?P<thread_id>\d+)\s\("
    r"(?P<thread_name>\S+)\):\s*"
)
M_NODE_COUNTERS = (
    r"\s*"
    r"(?P<count>\d+)\s+"
    r"(?P<name>\S+)\s+"
    r"(?P<reason>(\S+\s)+)\s+"
    r"(?P<severity>\S+)\s+"
    r"(?P<index>\d+)\s*"
)
M_PMB_CS_HEADER = (
    r"\s*per-thread\s+context\s+switches.*"
)
M_PMB_CS = (
    r"(?P<thread_name>\S+)\s+\("
    r"(?P<thread_id>\S+)\)\s+\S+\s+"
    r"(?P<context_switches>[\d\.]+)"
)
M_PMB_PF_HEADER = (
    r"\s*per-thread\s+page\s+faults.*"
)
M_PMB_PF = (
    r"(?P<thread_name>\S+)\s+\("
    r"(?P<thread_id>\S+)\)\s+\S+\s+"
    r"(?P<minor_page_faults>[\d\.]+)\s+"
    r"(?P<major_page_faults>[\d\.]+)"
)
M_PMB_THREAD = (
    r"\s*"
    r"(?P<thread_name>\S+)\s+\("
    r"(?P<thread_id>\d+)\)\s*"
)
M_PMB_IC_HEADER = (
    r"\s*instructions/packet,\s+cycles/packet\s+and\s+IPC.*"
)
M_PMB_IC_NODE = (
    r"\s*"
    r"(?P<node_name>\S+)\s+"
    r"(?P<calls>[\d\.]+)\s+"
    r"(?P<packets>[\d\.]+)\s+"
    r"(?P<packets_per_call>[\d\.]+)\s+"
    r"(?P<clocks_per_packets>[\d\.]+)\s+"
    r"(?P<instructions_per_packets>[\d\.]+)\s+"
    r"(?P<ipc>[\d\.]+)"
)
M_PMB_CM_HEADER = (
    r"\s*cache\s+hits\s+and\s+misses.*"
)
M_PMB_CM_NODE = (
    r"\s*"
    r"(?P<node_name>\S+)\s+"
    r"(?P<l1_hit>[\d\.]+)\s+"
    r"(?P<l1_miss>[\d\.]+)\s+"
    r"(?P<l2_hit>[\d\.]+)\s+"
    r"(?P<l2_miss>[\d\.]+)\s+"
    r"(?P<l3_hit>[\d\.]+)\s+"
    r"(?P<l3_miss>[\d\.]+)"
)
M_PMB_LO_HEADER = (
    r"\s*load\s+operations.*"
)
M_PMB_LO_NODE = (
    r"\s*"
    r"(?P<node_name>\S+)\s+"
    r"(?P<calls>[\d\.]+)\s+"
    r"(?P<packets>[\d\.]+)\s+"
    r"(?P<one>[\d\.]+)\s+"
    r"(?P<two>[\d\.]+)\s+"
    r"(?P<three>[\d\.]+)"
)
M_PMB_BM_HEADER = (
    r"\s*Branches,\s+branches\s+taken\s+and\s+mis-predictions.*"
)
M_PMB_BM_NODE = (
    r"\s*"
    r"(?P<node_name>\S+)\s+"
    r"(?P<branches_per_call>[\d\.]+)\s+"
    r"(?P<branches_per_packet>[\d\.]+)\s+"
    r"(?P<taken_per_call>[\d\.]+)\s+"
    r"(?P<taken_per_packet>[\d\.]+)\s+"
    r"(?P<mis_predictions>[\d\.]+)"
)
M_PMB_MB_HEADER = (
    r"\s*memory\s+reads\s+and\s+writes\s+per\s+memory\s+controller.*"
)
M_PMB_MB = (
    r"\s*"
    r"(?P<name>\S+)\s+"
    r"(?P<runtime>[\d\.]+)\s+"
    r"(?P<reads_mbs>[\d\.]+)\s+"
    r"(?P<writes_mbs>[\d\.]+)\s+"
    r"(?P<total_mbs>[\d\.]+)"
)


class BundleVppctl:
    """
    Creates a VPP object. This is the main object for defining a VPP program,
    and interacting with its output.
    """
    def __init__(self, program, serializer, hook):
        """
        Initialize Bundle VPP class.

        :param program: VPP instructions.
        :param serializer: Metric serializer.
        :param hook: VPP CLI socket.
        :type program: dict
        :type serializer: Serializer
        :type hook: int
        """
        self.obj = None
        self.code = program["code"]
        self.metrics = program["metrics"]
        self.cli_command_list = list()
        self.cli_replies_list = list()
        self.serializer = serializer
        self.hook = hook

    def attach(self, duration):
        """
        Attach events to VPP.

        :param duration: Trial duration.
        :type duration: int
        """
        for command in self.code.splitlines():
            self.cli_command_list.append(
                command.format(duration=duration, socket=self.hook)
            )

    def detach(self):
        """
        Detach from VPP.
        """

    def fetch_data(self):
        """
        Fetch data by invoking subprocess calls.
        """
        for command in self.cli_command_list:
            try:
                getLogger(__name__).info(command)
                replies = subprocess.getoutput(command)
            except (AssertionError, AttributeError):
                getLogger("console_stderr").error(
                    f"Failed when executing command: {command}"
                )
                sys.exit(Constants.err_vpp_execute)

            self.cli_replies_list.append(replies)
            replies = sub(r"\x1b[^m]*m", "", replies)
            if replies:
                getLogger(__name__).info(replies)
            else:
                getLogger(__name__).info("<no reply>")
        self.serializer.create(metrics=self.metrics)

    def process_data(self):
        """
        Post process command reply.
        """
        for command in zip(self.cli_command_list, self.cli_replies_list):
            self_fn = command[0].replace(
                f"-s {self.hook} ", "").replace(" ", "_")
            self_method_list = [meth for meth in dir(self)
                                if callable(getattr(self, meth)) and
                                meth.startswith('__') is False]
            if self_fn not in self_method_list:
                continue
            try:
                self_fn = getattr(self, self_fn)
                self_fn(command[1])
            except AttributeError:
                pass
            except (KeyError, ValueError, TypeError) as exc:
                getLogger("console_stderr").error(
                    f"Failed when processing data. Error message {exc}"
                )
                sys.exit(Constants.err_telemetry_process)

    def vppctl_show_interface(self, reply):
        """
        Parse the show interface output.

        :param reply: VPP reply.
        :type reply: str
        """
        for line in reply.splitlines():
            item = dict()
            labels = dict()
            if fullmatch(M_INT_BEGIN, line):
                ifc = fullmatch(M_INT_BEGIN, line).groupdict()
                metric = ifc["counter"].replace(" ", "_").replace("-", "_")
                item["name"] = metric
                item["value"] = ifc["count"]
            if fullmatch(M_INT_CONT, line):
                ifc_cnt = fullmatch(M_INT_CONT, line).groupdict()
                metric = ifc_cnt["counter"].replace(" ", "_").replace("-", "_")
                item["name"] = metric
                item["value"] = ifc_cnt["count"]
            if fullmatch(M_INT_BEGIN, line) or fullmatch(M_INT_CONT, line):
                labels["name"] = ifc["name"]
                labels["index"] = ifc["index"]
                item["labels"] = labels
                self.serializer.serialize(
                    metric=metric, labels=labels, item=item
                )

    def vppctl_show_runtime(self, reply):
        """
        Parse the show runtime output.

        :param reply: VPP reply.
        :type reply: str
        """
        for line in reply.splitlines():
            if fullmatch(M_RUN_THREAD, line):
                thread = fullmatch(M_RUN_THREAD, line).groupdict()
            if fullmatch(M_RUN_NODES, line):
                nodes = fullmatch(M_RUN_NODES, line).groupdict()
                for metric in self.serializer.metric_registry:
                    item = dict()
                    labels = dict()
                    item["name"] = metric
                    labels["node_name"] = nodes["node_name"]
                    labels["state"] = nodes["state"]
                    try:
                        labels["thread_name"] = thread["thread_name"]
                        labels["thread_id"] = thread["thread_id"]
                        labels["thread_lcore"] = thread["thread_lcore"]
                    except UnboundLocalError:
                        labels["thread_name"] = "vpp_main"
                        labels["thread_id"] = "0"
                        labels["thread_lcore"] = "0"
                    item["labels"] = labels
                    item["value"] = nodes[metric]
                    self.serializer.serialize(
                        metric=metric, labels=labels, item=item
                    )

    def vppctl_show_node_counters_verbose(self, reply):
        """
        Parse the show node conuter output.

        :param reply: VPP reply.
        :type reply: str
        """
        for line in reply.splitlines():
            if fullmatch(M_NODE_COUNTERS_THREAD, line):
                thread = fullmatch(M_NODE_COUNTERS_THREAD, line).groupdict()
            if fullmatch(M_NODE_COUNTERS, line):
                nodes = fullmatch(M_NODE_COUNTERS, line).groupdict()
                for metric in self.serializer.metric_registry_registry:
                    item = dict()
                    labels = dict()
                    item["name"] = metric
                    labels["name"] = nodes["name"]
                    labels["reason"] = nodes["reason"]
                    labels["severity"] = nodes["severity"]
                    try:
                        labels["thread_name"] = thread["thread_name"]
                        labels["thread_id"] = thread["thread_id"]
                    except UnboundLocalError:
                        labels["thread_name"] = "vpp_main"
                        labels["thread_id"] = "0"
                    item["labels"] = labels
                    item["value"] = nodes["count"]
                    self.serializer.serialize(
                        metric=metric, labels=labels, item=item
                    )

    def vppctl_show_perfmon_statistics(self, reply):
        """
        Parse the perfmon output.

        :param reply: VPP reply.
        :type reply: str
        """
        def perfmon_threads(reply, regex_threads):
            for line in reply.splitlines():
                if fullmatch(regex_threads, line):
                    threads = fullmatch(regex_threads, line).groupdict()
                    for metric in self.serializer.metric_registry:
                        item = dict()
                        labels = dict()
                        item["name"] = metric
                        labels["name"] = threads["thread_name"]
                        labels["id"] = threads["thread_id"]
                        item["labels"] = labels
                        item["value"] = threads[metric]
                        self.serializer.serialize(
                            metric=metric, labels=labels, item=item
                        )

        def perfmon_nodes(reply, regex_threads, regex_nodes):
            for line in reply.splitlines():
                if fullmatch(regex_threads, line):
                    thread = fullmatch(regex_threads, line).groupdict()
                if fullmatch(regex_nodes, line):
                    node = fullmatch(regex_nodes, line).groupdict()
                    for metric in self.serializer.metric_registry:
                        item = dict()
                        labels = dict()
                        item["name"] = metric
                        labels["node_name"] = node["node_name"]
                        labels["thread_name"] = thread["thread_name"]
                        labels["thread_id"] = thread["thread_id"]
                        item["labels"] = labels
                        item["value"] = node[metric]
                        self.serializer.serialize(
                            metric=metric, labels=labels, item=item
                        )

        def perfmon_system(reply, regex_line):
            for line in reply.splitlines():
                if fullmatch(regex_line, line):
                    name = fullmatch(regex_line, line).groupdict()
                    for metric in self.serializer.metric_registry:
                        item = dict()
                        labels = dict()
                        item["name"] = metric
                        labels["name"] = name["name"]
                        item["labels"] = labels
                        item["value"] = name[metric]
                        self.serializer.serialize(
                            metric=metric, labels=labels, item=item
                        )

        reply = sub(r"\x1b[^m]*m", "", reply)

        if fullmatch(M_PMB_CS_HEADER, reply.splitlines()[0]):
            perfmon_threads(reply, M_PMB_CS)
        if fullmatch(M_PMB_PF_HEADER, reply.splitlines()[0]):
            perfmon_threads(reply, M_PMB_PF)
        if fullmatch(M_PMB_IC_HEADER, reply.splitlines()[0]):
            perfmon_nodes(reply, M_PMB_THREAD, M_PMB_IC_NODE)
        if fullmatch(M_PMB_CM_HEADER, reply.splitlines()[0]):
            perfmon_nodes(reply, M_PMB_THREAD, M_PMB_CM_NODE)
        if fullmatch(M_PMB_LO_HEADER, reply.splitlines()[0]):
            perfmon_nodes(reply, M_PMB_THREAD, M_PMB_LO_NODE)
        if fullmatch(M_PMB_BM_HEADER, reply.splitlines()[0]):
            perfmon_nodes(reply, M_PMB_THREAD, M_PMB_BM_NODE)
        if fullmatch(M_PMB_MB_HEADER, reply.splitlines()[0]):
            perfmon_system(reply, M_PMB_MB)

    def vppctl_show_version(self, reply):
        """
        Parse the version output.

        :param reply: VPP reply.
        :type reply: str
        """
        for metric in self.serializer.metric_registry:
            version = reply.split()[1]
            item = dict()
            labels = dict()
            item["name"] = metric
            labels["version"] = version
            item["labels"] = labels
            item["value"] = {}
            self.serializer.serialize(
                metric=metric, labels=labels, item=item
            )
