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

"""CSR counters library."""

from resources.libraries.python.ssh import exec_cmd
from resources.libraries.python.topology import Topology, SocketType, NodeType


class CsrCounters:
    """CSR counters class."""

    def __init__(self):
        pass

    @staticmethod
    def show_csr_interfaces(node):
        """Show CSR interfaces on single VM.

        :param node: Topology node [NodeType.VM].
        :type node: dict
        """
        cmd = "show interfaces"
        exec_cmd(node, cmd, disconnect=True)

    @staticmethod
    def show_csr_cpu_alloc(node):
        """Show CSR CPU allocation on single VM.

        :param node: Topology node [NodeType.VM].
        :type node: dict
        """
        cmd = "show platform software cpu alloc"
        exec_cmd(node, cmd, disconnect=True)

    @staticmethod
    def show_csr_utilization_summary(node):
        """Show CSR utilization summary on single VM.

        :param node: Topology node [NodeType.VM].
        :type node: dict
        """
        cmd = "show platform hardware qfp active datapath utilization summary"
        exec_cmd(node, cmd, disconnect=True)

    @staticmethod
    def show_csr_infrastructure_sw_cio(node):
        """Show CSR infrastructure sw-cio on single VM.

        :param node: Topology node [NodeType.VM].
        :type node: dict
        """
        cmd = "show platform hardware qfp active datapath infrastructure sw-cio"
        exec_cmd(node, cmd, disconnect=True)

    @staticmethod
    def show_csr_drop(node):
        """Show CSR runtime on single VM.

        :param node: Topology node [NodeType.VM].
        :type node: dict
        """
        cmd = "show platform hardware qfp active statistics drop clear"
        exec_cmd(node, cmd, disconnect=True)

    @staticmethod
    def show_csr_runtime_on_all_duts(nodes):
        """Show CSR runtime on all DUTs.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.VM:
                CsrCounters.show_csr_infrastructure_sw_cio(node)

    @staticmethod
    def clear_csr_runtime_on_all_duts(nodes):
        """Clear CSR runtime on all DUTs.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        CsrCounters.show_csr_runtime_on_all_duts(nodes)

    @staticmethod
    def show_csr_statistics(node):
        """Show CSR statistics on single VM.

        :param node: Topology node [NodeType.VM].
        :type node: dict
        """
        CsrCounters.show_csr_interfaces(node)
        CsrCounters.show_csr_cpu_alloc(node)
        CsrCounters.show_csr_drop(node)
        CsrCounters.show_csr_utilization_summary(node)
        CsrCounters.show_csr_infrastructure_sw_cio(node)

    @staticmethod
    def show_csr_statistics_on_all_duts(nodes):
        """Show CSR statistics on all VMs.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.VM:
                CsrCounters.show_csr_statistics(node)

    @staticmethod
    def clear_csr_statistics_on_all_duts(nodes):
        """Clear CSR statistics on all VMs.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        CsrCounters.show_csr_statistics_on_all_duts(nodes)
