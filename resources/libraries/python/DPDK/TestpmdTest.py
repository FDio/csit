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
    This class starts testpmd on topology nodes and checks if ready for traffic.
    """

    @staticmethod
    def start_testpmd_on_all_duts(
        nodes, topology_info, phy_cores, jumbo_frames,
    ):
        """Start the testpmd with M worker threads and rxqueues N and jumbo
        support frames on/off on all DUTs.

        :param nodes: All the nodes info from the topology file.
        :param topology_info: Suite variables as computed from path.
        :param phy_cores: Number of physical cores to use.
        :param jumbo_frames: Jumbo frames on/off.
        :type nodes: dict
        :type topology_info: dict
        :type phy_cores: int
        :type jumbo_frames: bool
        :raises RuntimeError: If still not ready for traffic after the restarts.
        """
        dp_count_int = int(phy_cores)
        if dp_count_int > 1:
            BuiltIn().set_tags('MTHREAD')
        else:
            BuiltIn().set_tags('STHREAD')
        BuiltIn().set_tags(
            f"{dp_count_int}T{dp_count_int}C"
        )
        for node in nodes:
            if u"DUT" in node:
                compute_resource_info = CpuUtils.get_affinity_vswitch(
                    nodes, node, phy_cores,
                )
                cpu_dp = compute_resource_info[u"cpu_dp"]
                rxq_count_int = compute_resource_info[u"rxq_count_int"]
                if1_pci = topology_info[f"{node.lower()}_if1_pci"]
                if2_pci = topology_info[f"{node.lower()}_if2_pci"]
                TestpmdTest.start_testpmd(
                    node=nodes[node],
                    if1_pci=if1_pci,
                    if2_pci=if2_pci,
                    lcores_list=cpu_dp,
                    nb_cores=dp_count_int,
                    queue_nums=rxq_count_int,
                    jumbo_frames=jumbo_frames,
                )
        for node in nodes:
            if u"DUT" in node:
                for i in range(3):
                    try:
                        TestpmdTest.check_testpmd(nodes[node])
                        break
                    except RuntimeError:
                        TestpmdTest.start_testpmd(
                            nodes[node], if1=if1, if2=if2,
                            lcores_list=cpu_dp, nb_cores=dp_count_int,
                            queue_nums=rxq_count_int,
                            jumbo_frames=jumbo_frames,
                        )
                else:
                    message = f"Failed to start testpmd at node {node}"
                    raise RuntimeError(message)

    @staticmethod
    def start_testpmd(
        node, if1_pci, if2_pci, lcores_list, nb_cores, queue_nums, jumbo_frames,
    ):
        """Launch testpmd on the DUT node. No not check readiness yet.

        :param node: DUT node.
        :param if1_pci: PCI address of the test link interface 1.
        :param if2_pci: PCI address of the test link interface 2.
        :param lcores_list: The DPDK run cores.
        :param nb_cores: The cores number for the forwarding.
        :param queue_nums: The queues number for the NIC.
        :param jumbo_frames: Indication if the jumbo frames are used (True) or
            not (False).
        :type node: dict
        :type if1_pci: str
        :type if2_pci: str
        :type lcores_list: str
        :type nb_cores: int
        :type queue_nums: str
        :type jumbo_frames: bool
        :raises RuntimeError: If the script "run_testpmd.sh" fails.
        """
        if node[u"type"] != NodeType.DUT:
            raise RuntimeError(f"Testpmd starts only on DUTs.")

        testpmd_args = DpdkUtil.get_testpmd_args(
            eal_corelist=f"1,{lcores_list}",
            eal_driver=False,
            eal_pci_whitelist0=if1_pci,
            eal_pci_whitelist1=if2_pci,
            eal_in_memory=True,
            pmd_num_mbufs=32768,
            pmd_fwd_mode=u"io",
            pmd_nb_ports=u"2",
            pmd_portmask=u"0x3",
            pmd_max_pkt_len=u"9200" if jumbo_frames else u"1518",
            pmd_mbuf_size=u"16384",
            pmd_rxd=None,
            pmd_txd=None,
            pmd_rxq=queue_nums,
            pmd_txq=queue_nums,
            pmd_nb_cores=nb_cores,
            pmd_disable_link_check=False,
            pmd_auto_start=True,
            pmd_numa=True,
        )

        command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"\
            f"/entry/run_testpmd.sh \"{testpmd_args}\""
        message = f"Failed to launch testpmd at node {node['host']}"
        exec_cmd_no_error(node, command, timeout=1800, message=message)

    @staticmethod
    def check_testpmd(node):
        """Execute the testpmd check on the DUT node.

        :param node: DUT node.
        :type node: dict
        :raises RuntimeError: If the script "check_testpmd.sh" fails.
        """
        if node[u"type"] == NodeType.DUT:
            command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"\
                      f"/entry/check_testpmd.sh"
            message = "Testpmd not started properly"
            exec_cmd_no_error(node, command, timeout=1800, message=message)
