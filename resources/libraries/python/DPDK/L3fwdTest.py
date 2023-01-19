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
            nodes, topology_info, phy_cores, rx_queues=None, jumbo_frames=False,
            rxd=None, txd=None):
        """
        Execute the l3fwd on all dut nodes.

        :param nodes: All the nodes info from the topology file.
        :param topology_info: All the info from the topology file.
        :param phy_cores: Number of physical cores to use.
        :param rx_queues: Number of RX queues.
        :param jumbo_frames: Jumbo frames on/off.
        :param rxd: Number of RX descriptors.
        :param txd: Number of TX descriptors.

        :type nodes: dict
        :type topology_info: dict
        :type phy_cores: int
        :type rx_queues: int
        :type jumbo_frames: bool
        :type rxd: int
        :type txd: int
        :raises RuntimeError: If bash return code is not 0.
        """
        cpu_count_int = dp_count_int = int(phy_cores)
        dp_cores = cpu_count_int+1
        for node in nodes:
            if u"DUT2" in node:
                compute_resource_info = CpuUtils.get_affinity_vswitch(
                    nodes, node, phy_cores, rx_queues=rx_queues,
                    rxd=rxd, txd=txd
                )
                if dp_count_int > 1:
                    BuiltIn().set_tags('MTHREAD')
                else:
                    BuiltIn().set_tags('STHREAD')
                BuiltIn().set_tags(
                    f"{dp_count_int}T{cpu_count_int}C"
                )

                cpu_dp = compute_resource_info[u"cpu_dp"]
                rxq_count_int = compute_resource_info[u"rxq_count_int"]
                if1 = topology_info[f"{node}_pf1"][0]
                if2 = topology_info[f"{node}_pf2"][0]
                L3fwdTest.start_l3fwd(
                    nodes, nodes[node], if1=if1, if2=if2, lcores_list=cpu_dp,
                    nb_cores=dp_count_int, queue_nums=rxq_count_int,
                    jumbo_frames=jumbo_frames
                )
        for node in nodes:
            if u"DUT2" in node:
                for i in range(3):
                    try:
                        L3fwdTest.check_l3fwd(nodes[node])
                        break
                    except RuntimeError:
                        L3fwdTest.start_l3fwd(
                            nodes, nodes[node], if1=if1, if2=if2,
                            lcores_list=cpu_dp, nb_cores=dp_count_int,
                            queue_nums=rxq_count_int, jumbo_frames=jumbo_frames,
                            tg_flip=tg_flip
                        )
                else:
                    message = f"Failed to start l3fwd at node {node}"
                    raise RuntimeError(message)

    @staticmethod
    def start_l3fwd(
            nodes, node, if1, if2, lcores_list, nb_cores, queue_nums,
            jumbo_frames):
        """
        Execute the (perhaps patched) l3fwd on the dut_node.

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
    def get_adj_mac(nodes, node, if1, if2):
        """
        Get MAC addresses adjacent to interfaces (by PCI address) of the DUT.

        Also the mentioned PCI addresses are returned.

        L3fwd uses default IP forwarding table, but sorts ports by PCI address.
        When that does not match the traffic profile (depends on topology),
        the only way to fix is is to patch and recompile l3fwd app.

        This is done here, so that the caller does not need to care
        about port flipping.

        :param nodes: All the nodes info in the topology file.
        :param node: DUT node.
        :param if1: The test link interface 1.
        :param if2: The test link interface 2.
        :type nodes: dict
        :type node: dict
        :type if1: str
        :type if2: str
        :returns: Returns MAC addresses of adjacency DUT/TG nodes
            and PCI addresses (of this DUT node), sorted by PCI address.
        :rtype: str
        """
        if_key0 = if1
        if_key1 = if2
        if_pci0 = Topology.get_interface_pci_addr(node, if_key0)
        if_pci1 = Topology.get_interface_pci_addr(node, if_key1)
        adj_node0, adj_if_key0 = Topology.get_adjacent_node_and_interface(
            nodes, node, if_key0
        )
        adj_node1, adj_if_key1 = Topology.get_adjacent_node_and_interface(
            nodes, node, if_key1
        )
        adj_mac0 = Topology.get_interface_mac(adj_node0, adj_if_key0)
        adj_mac1 = Topology.get_interface_mac(adj_node1, adj_if_key1)

        if if_pci0 < if_pci1:
            # Normal port ordering.
            # But we want 0->1 traffic routed to port 1.
            L3fwdTest.patch_l3fwd(node, u"patch_l3fwd_flip_routes")
            return adj_mac0, adj_mac1, if_pci0, if_pci1
        else:
            # Route table is ok, but caller needs MAC adresses
            # in order given by PCI addresses.
            return adj_mac1, adj_mac0, if_pci1, if_pci0
        # TG flip does not matter as TrafficGenerator reverses flows then,
        # so 0->1 traffic always goes TG->DUT1->DUT2->TG,
        # arriving first at dut1_if1 regardless of PCI addresses.

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
