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

from copy import deepcopy
from logging import getLogger
from re import fullmatch, sub
import struct
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
    r"(?P<name>\S+)\s+"
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
M_PMB_PL_HEADER = (
    r"\s*Thread\s+power\s+licensing.*"
)
M_PMB_PL_NODE = (
    r"\s*"
    r"(?P<node_name>\S+)\s+"
    r"(?P<lvl0>[\d\.]+)\s+"
    r"(?P<lvl1>[\d\.]+)\s+"
    r"(?P<lvl2>[\d\.]+)\s+"
    r"(?P<throttle>[\d\.]+)"
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
    def __init__(self, program, serializer):
        """
        Initialize Bundle VPP class.

        :param program: VPP instructions.
        :param serializer: Metric serializer.
        :type program: dict
        :type serializer: Serializer
        """
        self.obj = None
        self.code = program[u"code"]
        self.metrics = program[u"metrics"]
        self.cli_command_list = list()
        self.cli_replies_list = list()
        self.serializer = serializer

    def attach(self, duration):
        """
        Attach events to VPP.

        :param duration: Trial duration.
        :type duration: int
        """
        for command in self.code.splitlines():
            self.cli_command_list.append(command.format(duration=duration))

    def detach(self):
        """
        Detach from VPP.
        """
        pass

    def fetch_data(self):
        """
        Fetch data by invoking subprocess calls.
        """
        for command in self.cli_command_list:
            try:
                replies = subprocess.getoutput(command)
            except (AssertionError, AttributeError):
                getLogger("console_stderr").error(
                    f"Failed when executing command: {command}"
                )
                sys.exit(Constants.err_vpp_execute)

            if not isinstance(replies, list):
                replies = [replies]
            for reply in replies:
                self.cli_replies_list.append(reply)
                reply = sub(r"\x1b[^m]*m", u"", reply.reply)
                if reply:
                    getLogger(__name__).info(reply)
                else:
                    getLogger(__name__).info(u"<no reply>")
        self.serializer.create(metrics=self.metrics)

    def process_data(self):
        """
        Post process command reply.
        """
        for command in zip(self.cli_command_list, self.cli_replies_list):
            self_fn = command[0][u"api_args"][u"cmd"].replace(u" ", u"_")
            self_method_list = [meth for meth in dir(self)
                                if callable(getattr(self, meth)) and
                                meth.startswith('__') is False]
            if self_fn not in self_method_list:
                continue
            try:
                self_fn = getattr(self, self_fn)
                self_fn(command[1].reply)
            except AttributeError:
                pass
            except (KeyError, ValueError, TypeError) as exc:
                getLogger("console_stderr").error(
                    f"Failed when processing data. Error message {exc}"
                )
                sys.exit(Constants.err_telemetry_process)

    def show_interface(self, reply):
        """
        Parse the show interface output.

        :param reply: API reply.
        :type reply: str
        """
        for line in reply.splitlines():
            item = dict()
            labels = dict()
            if fullmatch(M_INT_BEGIN, line):
                ifc = fullmatch(M_INT_BEGIN, line).groupdict()
                metric = ifc[u"counter"].replace(" ", "_").replace("-", "_")
                item[u"name"] = metric
                item[u"value"] = ifc[u"count"]
            if fullmatch(M_INT_CONT, line):
                ifc_cnt = fullmatch(M_INT_CONT, line).groupdict()
                metric = ifc_cnt[u"counter"].replace(" ", "_").replace("-", "_")
                item[u"name"] = metric
                item[u"value"] = ifc_cnt[u"count"]
            if fullmatch(M_INT_BEGIN, line) or fullmatch(M_INT_CONT, line):
                labels[u"name"] = ifc[u"name"]
                labels[u"index"] = ifc[u"index"]
                item[u"labels"] = labels
                self.serializer.serialize(
                    metric=metric, labels=labels, item=item
                )

    def show_runtime(self, reply):
        """
        Parse the show runtime output.

        :param reply: API reply.
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
                    item[u"name"] = metric
                    labels[u"name"] = nodes[u"name"]
                    labels[u"state"] = nodes[u"state"]
                    try:
                        labels[u"thread_name"] = thread[u"thread_name"]
                        labels[u"thread_id"] = thread[u"thread_id"]
                        labels[u"thread_lcore"] = thread[u"thread_lcore"]
                    except UnboundLocalError:
                        labels[u"thread_name"] = u"vpp_main"
                        labels[u"thread_id"] = u"0"
                        labels[u"thread_lcore"] = u"0"
                    item[u"labels"] = labels
                    item[u"value"] = nodes[metric]
                    self.serializer.serialize(
                        metric=metric, labels=labels, item=item
                    )

    def show_node_counters_verbose(self, reply):
        """
        Parse the show node conuter output.

        :param reply: API reply.
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
                    item[u"name"] = metric
                    labels[u"name"] = nodes[u"name"]
                    labels[u"reason"] = nodes[u"reason"]
                    labels[u"severity"] = nodes[u"severity"]
                    try:
                        labels[u"thread_name"] = thread[u"thread_name"]
                        labels[u"thread_id"] = thread[u"thread_id"]
                    except UnboundLocalError:
                        labels[u"thread_name"] = u"vpp_main"
                        labels[u"thread_id"] = u"0"
                    item[u"labels"] = labels
                    item[u"value"] = nodes[u"count"]
                    self.serializer.serialize(
                        metric=metric, labels=labels, item=item
                    )

    def show_perfmon_statistics(self, reply):
        """
        Parse the permon output.

        :param reply: API reply.
        :type reply: str
        """
        def perfmon_threads(reply, regex_threads):
            for line in reply.splitlines():
                if fullmatch(regex_threads, line):
                    threads = fullmatch(regex_threads, line).groupdict()
                    for metric in self.serializer.metric_registry:
                        item = dict()
                        labels = dict()
                        item[u"name"] = metric
                        labels[u"name"] = threads[u"thread_name"]
                        labels[u"id"] = threads[u"thread_id"]
                        item[u"labels"] = labels
                        item[u"value"] = threads[metric]
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
                        item[u"name"] = metric
                        labels[u"name"] = node[u"node_name"]
                        labels[u"thread_name"] = thread[u"thread_name"]
                        labels[u"thread_id"] = thread[u"thread_id"]
                        item[u"labels"] = labels
                        item[u"value"] = node[metric]
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
                        item[u"name"] = metric
                        labels[u"name"] = name[u"name"]
                        item[u"labels"] = labels
                        item[u"value"] = name[metric]
                        self.serializer.serialize(
                            metric=metric, labels=labels, item=item
                        )

        reply = sub(r"\x1b[^m]*m", u"", reply)

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
        if fullmatch(M_PMB_PL_HEADER, reply.splitlines()[0]):
            perfmon_nodes(reply, M_PMB_THREAD, M_PMB_PL_NODE)
        if fullmatch(M_PMB_MB_HEADER, reply.splitlines()[0]):
            perfmon_system(reply, M_PMB_MB)

    def show_version(self, reply):
        """
        Parse the version output.

        :param reply: API reply.
        :type reply: str
        """
        for metric in self.serializer.metric_registry:
            version = reply.split()[1]
            item = dict()
            labels = dict()
            item[u"name"] = metric
            labels[u"version"] = version
            item[u"labels"] = labels
            item[u"value"] = {}
            self.serializer.serialize(
                metric=metric, labels=labels, item=item
            )
