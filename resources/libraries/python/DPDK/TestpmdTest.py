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
This module exists to start testpmd on topology nodes.
"""

from robot.libraries.BuiltIn import BuiltIn
from resources.libraries.python.Constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.DpdkUtil import DpdkUtil
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology


class TestpmdTest:
    """
    This class start testpmd on topology nodes and check if properly started.
    """

    @staticmethod
    def start_testpmd_on_all_duts(
            nodes, topology_info, phy_cores, rx_queues=None, jumbo=False,
            rxd=None, txd=None, nic_rxq_size=None, nic_txq_size=None):
        """
        Start the testpmd with M worker threads and rxqueues N and jumbo
        support frames on/off on all DUTs.

        :param nodes: All the nodes info from the topology file.
        :param topology_info: All the info from the topology file.
        :param phy_cores: Number of physical cores to use.
        :param rx_queues: Number of RX queues.
        :param jumbo: Jumbo frames on/off.
        :param rxd: Number of RX descriptors.
        :param txd: Number of TX descriptors.
        :param nic_rxq_size: RX queue size.
        :param nic_txq_size: TX queue size.

        :type nodes: dict
        :type topology_info: dict
        :type phy_cores: int
        :type rx_queues: int
        :type jumbo: bool
        :type rxd: int
        :type txd: int
        :type nic_rxq_size: int
        :type nic_txq_size: int
        :raises RuntimeError: If bash return code is not 0.
        """

        cpu_count_int = dp_count_int = int(phy_cores)
        dp_cores = cpu_count_int+1
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
                TestpmdTest.start_testpmd(
                    node, if1=if1, if2=if2, lcores_list=cpu_dp,
                    nb_cores=dp_count_int, queue_nums=rxq_count_int,
                    jumbo=jumbo, rxq_size=nic_rxq_size,
                    txq_size=nic_txq_size
                )
        for node in nodes:
            if u"DUT" in node:
                for i in range(3):
                    try:
                        nic_model = nodes[node]["interfaces"][if1]["model"]
                        if "Mellanox-CX7VEAT" in nic_model:
                            break
                        if "Mellanox-CX6DX" in nic_model:
                            break
                        TestpmdTest.check_testpmd(nodes[node])
                        break
                    except RuntimeError:
                        TestpmdTest.start_testpmd(
                            nodes[node], if1=if1, if2=if2,
                            lcores_list=cpu_dp, nb_cores=dp_count_int,
                            queue_nums=rxq_count_int,
                            jumbo=jumbo,
                            rxq_size=nic_rxq_size, txq_size=nic_txq_size
                        )
                else:
                    message = f"Failed to start testpmd at node {node}"
                    raise RuntimeError(message)

    @staticmethod
    def start_testpmd(
            node, if1, if2, lcores_list, nb_cores, queue_nums,
            jumbo, rxq_size=1024, txq_size=1024):
        """
        Execute the testpmd on the DUT node.

        :param node: DUT node.
        :param if1: The test link interface 1.
        :param if2: The test link interface 2.
        :param lcores_list: The DPDK run cores.
        :param nb_cores: The cores number for the forwarding.
        :param queue_nums: The queues number for the NIC.
        :param jumbo: Indication if the jumbo frames are used (True) or
            not (False).
        :param rxq_size: RXQ size. Default=1024.
        :param txq_size: TXQ size. Default=1024.
        :type node: dict
        :type if1: str
        :type if2: str
        :type lcores_list: str
        :type nb_cores: int
        :type queue_nums: str
        :type jumbo: bool
        :type rxq_size: int
        :type txq_size: int
        :raises RuntimeError: If the script "run_testpmd.sh" fails.
        """
        if node[u"type"] == NodeType.DUT:
            if_pci0 = Topology.get_interface_pci_addr(node, if1)
            if_pci1 = Topology.get_interface_pci_addr(node, if2)

            pmd_max_pkt_len = u"9200" if jumbo else u"1518"
            testpmd_args = DpdkUtil.get_testpmd_args(
                eal_corelist=f"1,{lcores_list}",
                eal_driver=False,
                eal_pci_whitelist0=if_pci0,
                eal_pci_whitelist1=if_pci1,
                eal_in_memory=True,
                pmd_num_mbufs=32768,
                pmd_fwd_mode=u"io",
                pmd_nb_ports=u"2",
                pmd_portmask=u"0x3",
                pmd_max_pkt_len=pmd_max_pkt_len,
                pmd_mbuf_size=u"16384",
                pmd_rxd=rxq_size,
                pmd_txd=txq_size,
                pmd_rxq=queue_nums,
                pmd_txq=queue_nums,
                pmd_nb_cores=nb_cores,
                pmd_disable_link_check=False,
                pmd_auto_start=True,
                pmd_numa=True
            )

            command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"\
                f"/entry/run_testpmd.sh \"{testpmd_args}\""
            message = f"Failed to execute testpmd at node {node['host']}"
            exec_cmd_no_error(node, command, timeout=1800, message=message)

    @staticmethod
    def check_testpmd(node):
        """
        Execute the testpmd check on the DUT node.

        :param node: DUT node.
        :type node: dict
        :raises RuntimeError: If the script "check_testpmd.sh" fails.
        """
        if node[u"type"] == NodeType.DUT:
            command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"\
                      f"/entry/check_testpmd.sh"
            message = "Testpmd not started properly"
            exec_cmd_no_error(node, command, timeout=1800, message=message)
