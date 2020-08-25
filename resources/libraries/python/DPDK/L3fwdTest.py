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

"""
This module exists to provide the l3fwd test for DPDK on topology nodes.
"""

from resources.libraries.python.Constants import Constants
from resources.libraries.python.DpdkUtil import DpdkUtil
from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd
from resources.libraries.python.topology import NodeType, Topology


class L3fwdTest:
    """Test the DPDK l3fwd performance."""

    @staticmethod
    def start_l3fwd(
            nodes, node, if1, if2, lcores_list, nb_cores, queue_nums,
            jumbo_frames):
        """
        Execute the l3fwd on the dut_node.

        :param nodes: All the nodes info in the topology file.
        :param node: DUT node.
        :param if1: The test link interface 1.
        :param if2: The test link interface 2.
        :param lcores_list: The lcore list string for the l3fwd routing
        :param nb_cores: The cores number for the forwarding
        :param queue_nums: The queues number for the NIC
        :param jumbo_frames: Indication if the jumbo frames are used (True) or
                             not (False).
        :type nodes: dict
        :type node: dict
        :type if1: str
        :type if2: str
        :type lcores_list: str
        :type nb_cores: str
        :type queue_nums: str
        :type jumbo_frames: bool
        """
        if node[u"type"] == NodeType.DUT:
            adj_mac0, adj_mac1, if_pci0, if_pci1 = L3fwdTest.get_adj_mac(
                nodes, node, if1, if2
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

            if jumbo_frames:
                l3fwd_args = DpdkUtil.get_l3fwd_args(
                    eal_corelist=f"1,{lcores_list}",
                    eal_driver=False,
                    eal_pci_whitelist0=if_pci0,
                    eal_pci_whitelist1=if_pci1,
                    eal_in_memory=True,
                    pmd_config=f"\\\"{port_config.rstrip(u',')}\\\"",
                    pmd_eth_dest_0=f"\\\"0,{adj_mac0}\\\"",
                    pmd_eth_dest_1=f"\\\"1,{adj_mac1}\\\"",
                    pmd_parse_ptype=True,
                    pmd_enable_jumbo=jumbo_frames,
                    pmd_max_pkt_len=jumbo_frames
                )
            else:
                l3fwd_args = DpdkUtil.get_l3fwd_args(
                    eal_corelist=f"1,{lcores_list}",
                    eal_driver=False,
                    eal_pci_whitelist0=if_pci0,
                    eal_pci_whitelist1=if_pci1,
                    eal_in_memory=True,
                    pmd_config=f"\\\"{port_config.rstrip(u',')}\\\"",
                    pmd_eth_dest_0=f"\\\"0,{adj_mac0}\\\"",
                    pmd_eth_dest_1=f"\\\"1,{adj_mac1}\\\"",
                    pmd_parse_ptype=True
                )

            command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"\
                f"/entry/run_l3fwd.sh \"{l3fwd_args} -P -L -p 0x3\""
            message = f"Failed to execute l3fwd test at node {node['host']}"
            exec_cmd_no_error(node, command, timeout=1800, message=message)


    @staticmethod
    def get_adj_mac(nodes, node, if1, if2):
        """
        Get adjacency MAC addresses of the DUT node.

        :param nodes: All the nodes info in the topology file.
        :param node: DUT node.
        :param if1: The test link interface 1.
        :param if2: The test link interface 2.
        :type nodes: dict
        :type node: dict
        :type if1: str
        :type if2: str
        :returns: Returns MAC addresses of adjacency DUT nodes and PCI
            addresses.
        :rtype: str
        """
        if_key0 = if1
        if_key1 = if2
        if_pci0 = Topology.get_interface_pci_addr(node, if_key0)
        if_pci1 = Topology.get_interface_pci_addr(node, if_key1)

        # Detect which is the port 0.
        if min(if_pci0, if_pci1) != if_pci0:
            if_key0, if_key1 = if_key1, if_key0
            L3fwdTest.patch_l3fwd(node, u"patch_l3fwd_flip_routes")

        adj_node0, adj_if_key0 = Topology.get_adjacent_node_and_interface(
            nodes, node, if_key0
        )
        adj_node1, adj_if_key1 = Topology.get_adjacent_node_and_interface(
            nodes, node, if_key1
        )
        if_pci0 = Topology.get_interface_pci_addr(node, if_key0)
        if_pci1 = Topology.get_interface_pci_addr(node, if_key1)
        adj_mac0 = Topology.get_interface_mac(adj_node0, adj_if_key0)
        adj_mac1 = Topology.get_interface_mac(adj_node1, adj_if_key1)

        return adj_mac0, adj_mac1, if_pci0, if_pci1

    @staticmethod
    def patch_l3fwd(node, patch):
        """
        Patch l3fwd application and recompile.

        :param node: DUT node.
        :param patch: Patch to apply.
        :type node: dict
        :type patch: str
        :raises RuntimeError: Patching of l3fwd failed.
        """
        command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"\
            f"/entry/patch_l3fwd.sh " \
            f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"\
            f"/entry/{patch}"
        message = f"Failed to patch l3fwd at node {node['host']}"
        ret_code, stdout, _ = exec_cmd(node, command, timeout=1800)
        if ret_code != 0 and u"Skipping patch." not in stdout:
            raise RuntimeError(message)
