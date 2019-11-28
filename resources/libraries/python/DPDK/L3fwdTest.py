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

"""
This module exists to provide the l3fwd test for DPDK on topology nodes.
"""

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import NodeType, Topology


class L3fwdTest:
    """Test the DPDK l3fwd performance."""

    @staticmethod
    def start_the_l3fwd_test(
            nodes_info, dut_node, dut_if1, dut_if2, nb_cores, lcores_list,
            queue_nums, jumbo_frames):
        """
        Execute the l3fwd on the dut_node.

        :param nodes_info: All the nodes info in the topology file.
        :param dut_node: Will execute the l3fwd on this node
        :param dut_if1: The test link interface 1.
        :param dut_if2: The test link interface 2.
        :param nb_cores: The cores number for the forwarding
        :param lcores_list: The lcore list string for the l3fwd routing
        :param queue_nums: The queues number for the NIC
        :param jumbo_frames: Indication if the jumbo frames are used (True) or
                             not (False).
        :type nodes_info: dict
        :type dut_node: dict
        :type dut_if1: str
        :type dut_if2: str
        :type nb_cores: str
        :type lcores_list: str
        :type queue_nums: str
        :type jumbo_frames: bool
        """
        if dut_node[u"type"] == NodeType.DUT:
            adj_mac0, adj_mac1 = L3fwdTest.get_adj_mac(
                nodes_info, dut_node, dut_if1, dut_if2
            )

            list_cores = [int(item) for item in lcores_list.split(u",")]

            # prepare the port config param
            nb_cores = int(nb_cores)
            index = 0
            port_config = ''
            for port in range(0, 2):
                for queue in range(0, int(queue_nums)):
                    index = 0 if nb_cores == 1 else index
                    port_config += f"({port}, {queue}, {list_cores[index]}),"
                    index += 1

            ssh = SSH()
            ssh.connect(dut_node)

            cmd = f"{Constants.REMOTE_FW_DIR}/tests/dpdk/dpdk_scripts" \
                f"/run_l3fwd.sh \"{lcores_list}\" " \
                f"\"{port_config.rstrip(u',')}\" " \
                f"{adj_mac0} {adj_mac1} {u'yes' if jumbo_frames else u'no'}"

            ret_code, _, _ = ssh.exec_command_sudo(cmd, timeout=600)
            if ret_code != 0:
                raise Exception(
                    f"Failed to execute l3fwd test at node {dut_node[u'host']}"
                )

    @staticmethod
    def get_adj_mac(nodes_info, dut_node, dut_if1, dut_if2):
        """
        Get adjacency MAC addresses of the DUT node.

        :param nodes_info: All the nodes info in the topology file.
        :param dut_node: Will execute the l3fwd on this node
        :param dut_if1: The test link interface 1.
        :param dut_if2: The test link interface 2.
        :type nodes_info: dict
        :type dut_node: dict
        :type dut_if1: str
        :type dut_if2: str
        :returns: Returns MAC addresses of adjacency DUT nodes.
        :rtype: str
        """
        if_key0 = dut_if1
        if_key1 = dut_if2
        if_pci0 = Topology.get_interface_pci_addr(dut_node, if_key0)
        if_pci1 = Topology.get_interface_pci_addr(dut_node, if_key1)

        # detect which is the port 0
        if min(if_pci0, if_pci1) != if_pci0:
            if_key0, if_key1 = if_key1, if_key0
            L3fwdTest.patch_l3fwd(dut_node, u"patch_l3fwd_flip_routes")

        adj_node0, adj_if_key0 = Topology.get_adjacent_node_and_interface(
            nodes_info, dut_node, if_key0
        )
        adj_node1, adj_if_key1 = Topology.get_adjacent_node_and_interface(
            nodes_info, dut_node, if_key1
        )

        adj_mac0 = Topology.get_interface_mac(adj_node0, adj_if_key0)
        adj_mac1 = Topology.get_interface_mac(adj_node1, adj_if_key1)

        return adj_mac0, adj_mac1

    @staticmethod
    def patch_l3fwd(node, patch):
        """
        Patch l3fwd application and recompile.

        :param node: Dictionary created from topology.
        :param patch: Patch to apply.
        :type node: dict
        :type patch: str
        :raises RuntimeError: Patching of l3fwd failed.
        """
        arch = Topology.get_node_arch(node)

        ssh = SSH()
        ssh.connect(node)

        ret_code, _, _ = ssh.exec_command(
            f"{Constants.REMOTE_FW_DIR}/tests/dpdk/dpdk_scripts/patch_l3fwd.sh "
            f"{arch} {Constants.REMOTE_FW_DIR}/tests/dpdk/dpdk_scripts/{patch}",
            timeout=600
        )

        if ret_code != 0:
            raise RuntimeError(u"Patch of l3fwd failed.")
