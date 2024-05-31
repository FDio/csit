# Copyright (c) 2024 Cisco and/or its affiliates.
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
This module exists to start l3fwd on topology nodes.
"""

from robot.libraries.BuiltIn import BuiltIn
from resources.libraries.python.Constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.DpdkUtil import DpdkUtil
from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd
from resources.libraries.python.topology import NodeType, Topology

NB_PORTS = 2


class L3fwdTest:
    """This class start l3fwd on topology nodes and check if properly started.
    """

    @staticmethod
    def start_l3fwd_on_all_duts(
            nodes, topology_info, phy_cores, rx_queues=None, jumbo=False,
            rxd=None, txd=None):
        """
        Execute the l3fwd on all dut nodes.

        :param nodes: All the nodes info from the topology file.
        :param topology_info: All the info from the topology file.
        :param phy_cores: Number of physical cores to use.
        :param rx_queues: Number of RX queues.
        :param jumbo: Jumbo frames on/off.
        :param rxd: Number of RX descriptors.
        :param txd: Number of TX descriptors.

        :type nodes: dict
        :type topology_info: dict
        :type phy_cores: int
        :type rx_queues: int
        :type jumbo: bool
        :type rxd: int
        :type txd: int
        :raises RuntimeError: If bash return code is not 0.
        """
        cpu_count_int = dp_count_int = int(phy_cores)
        dp_cores = cpu_count_int+1
        tg_flip = topology_info[f"tg_if1_pci"] > topology_info[f"tg_if2_pci"]
        compute_resource_info = CpuUtils.get_affinity_vswitch(
            nodes, phy_cores, rx_queues=rx_queues, rxd=rxd, txd=txd
        )
        for node_name, node in nodes.items():
            if node["type"] == NodeType.DUT:
                if dp_count_int > 1:
                    BuiltIn().set_tags('MTHREAD')
                else:
                    BuiltIn().set_tags('STHREAD')
                BuiltIn().set_tags(
                    f"{dp_count_int}T{cpu_count_int}C"
                )

                cpu_dp = compute_resource_info[f"{node_name}_cpu_dp"]
                rxq_count_int = compute_resource_info["rxq_count_int"]
                if1 = topology_info[f"{node_name}_pf1"][0]
                if2 = topology_info[f"{node_name}_pf2"][0]
                L3fwdTest.start_l3fwd(
                    nodes, node, if1=if1, if2=if2, lcores_list=cpu_dp,
                    nb_cores=dp_count_int, queue_nums=rxq_count_int,
                    jumbo=jumbo, tg_flip=tg_flip
                )
        for node in nodes:
            if u"DUT" in node:
                for i in range(3):
                    try:
                        L3fwdTest.check_l3fwd(nodes[node])
                        break
                    except RuntimeError:
                        L3fwdTest.start_l3fwd(
                            nodes, nodes[node], if1=if1, if2=if2,
                            lcores_list=cpu_dp, nb_cores=dp_count_int,
                            queue_nums=rxq_count_int, jumbo=jumbo,
                            tg_flip=tg_flip
                        )
                else:
                    message = f"Failed to start l3fwd at node {node}"
                    raise RuntimeError(message)

    @staticmethod
    def start_l3fwd(
            nodes, node, if1, if2, lcores_list, nb_cores, queue_nums,
            jumbo, tg_flip):
        """
        Execute the l3fwd on the dut_node.

        L3fwd uses default IP forwarding table, but sorts ports by API address.
        When that does not match the traffic profile (depends on topology),
        the only way to fix is is to latch and recompile l3fwd app.

        :param nodes: All the nodes info in the topology file.
        :param node: DUT node.
        :param if1: The test link interface 1.
        :param if2: The test link interface 2.
        :param lcores_list: The lcore list string for the l3fwd routing
        :param nb_cores: The cores number for the forwarding
        :param queue_nums: The queues number for the NIC
        :param jumbo: Indication if the jumbo frames are used (True) or
                             not (False).
        :param tg_flip: Whether TG ports are reordered.
        :type nodes: dict
        :type node: dict
        :type if1: str
        :type if2: str
        :type lcores_list: str
        :type nb_cores: str
        :type queue_nums: str
        :type jumbo: bool
        :type tg_flip: bool
        """
        if node[u"type"] == NodeType.DUT:
            adj_mac0, adj_mac1, if_pci0, if_pci1 = L3fwdTest.get_adj_mac(
                nodes, node, if1, if2, tg_flip
            )

            lcores = [int(item) for item in lcores_list.split(u",")]

            # prepare the port config param
            nb_cores = int(nb_cores)
            index = 0
            port_config = ''
            for port in range(0, NB_PORTS):
                for queue in range(0, int(queue_nums)):
                    index = 0 if nb_cores == 1 else index
                    port_config += \
                        f"({port}, {queue}, {lcores[index % NB_PORTS]}),"
                    index += 1

            if jumbo:
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
                    pmd_max_pkt_len=jumbo
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
    def check_l3fwd(node):
        """
        Execute the l3fwd check on the DUT node.

        :param node: DUT node.
        :type node: dict
        :raises RuntimeError: If the script "check_l3fwd.sh" fails.
        """
        if node[u"type"] == NodeType.DUT:
            command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"\
                f"/entry/check_l3fwd.sh"
            message = "L3fwd not started properly"
            exec_cmd_no_error(node, command, timeout=1800, message=message)

    @staticmethod
    def get_adj_mac(nodes, node, if1, if2, tg_flip):
        """
        Get adjacency MAC addresses of the DUT node.

        Interfaces are re-ordered according to PCI address,
        but the need to patch and recompile also depends on TG port order.
        "tg_flip" signals whether TG ports are reordered.

        :param nodes: All the nodes info in the topology file.
        :param node: DUT node.
        :param if1: The test link interface 1.
        :param if2: The test link interface 2.
        :param tg_flip: Whether tg ports are reordered.
        :type nodes: dict
        :type node: dict
        :type if1: str
        :type if2: str
        :type tg_flip: bool
        :returns: Returns MAC addresses of adjacency DUT nodes and PCI
            addresses.
        :rtype: str
        """
        if_key0 = if1
        if_key1 = if2
        if_pci0 = Topology.get_interface_pci_addr(node, if_key0)
        if_pci1 = Topology.get_interface_pci_addr(node, if_key1)

        # Flipping routes logic:
        # If TG and DUT ports are reordered -> flip
        # If TG reordered and DUT not reordered -> don't flip
        # If DUT reordered and TG not reordered -> don't flip
        # If DUT and TG not reordered -> flip

        # Detect which is the port 0.
        dut_flip = if_pci0 > if_pci1
        if dut_flip:
            if_key0, if_key1 = if_key1, if_key0
            if tg_flip:
                L3fwdTest.patch_l3fwd(node, u"patch_l3fwd_flip_routes")
        elif not tg_flip:
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
