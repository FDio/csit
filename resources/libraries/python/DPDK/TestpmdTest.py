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
        nodes, topology_info, phy_cores, rxq, jumbo, rxd=None, txd=None,
    ):
        """Start the testpmd with M worker threads and rxqueues N and jumbo
        support frames on/off on all DUTs.

        :param nodes: All the nodes info from the topology file.
        :param topology_info: Suite variables as computed from path.
        :param phy_cores: Number of physical cores to use.
        :param rxq: Number of RX queues. (Optional, Default: None)
        :param jumbo: Jumbo frames on/off.
        :param rxd: Number of RX descriptors per queue. None means DPDK default.
        :param txd: Number of TX descriptors per queue. None means DPDK default.
        :type nodes: dict
        :type topology_info: dict
        :type phy_cores: int
        :type rxq: Optional[int]
        :type jumbo: bool
        :type rxd: Optional[int]
        :type txd: Optional[int]
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
                    nodes, node, phy_cores, rx_queues=rxq, rxd=rxd, txd=txd,
                )
                if1_pci = topology_info[f"{node.lower()}_if1_pci"]
                if2_pci = topology_info[f"{node.lower()}_if2_pci"]
                TestpmdTest.start_testpmd(
                    node=nodes[node],
                    if1_pci=if1_pci,
                    if2_pci=if2_pci,
                    compute_resource_info=compute_resource_info,
                    jumbo=jumbo,
                )
        for node in nodes:
            if u"DUT" in node:
                for i in range(3):
                    try:
                        TestpmdTest.check_testpmd(nodes[node])
                        break
                    except RuntimeError:
                        compute_resource_info = CpuUtils.get_affinity_vswitch(
                            nodes, node, phy_cores, rx_queues=rxq,
                            rxd=rxd, txd=txd,
                        )
                        if1_pci = topology_info[f"{node.lower()}_if1_pci"]
                        if2_pci = topology_info[f"{node.lower()}_if2_pci"]
                        TestpmdTest.start_testpmd(
                            node=nodes[node],
                            if1_pci=if1_pci,
                            if2_pci=if2_pci,
                            compute_resource_info=compute_resource_info,
                            jumbo=jumbo,
                        )
                else:
                    message = f"Failed to start testpmd at node {node}"
                    raise RuntimeError(message)

    @staticmethod
    def start_testpmd(node, if1_pci, if2_pci, compute_resource_info, jumbo):
        """Launch testpmd on the DUT node. No not check readiness yet.

        :param node: DUT node.
        :param if1_pci: PCI address of the test link interface 1.
        :param if2_pci: PCI address of the test link interface 2.
        :param compute_resource_info: Output of CpuUtils.get_affinity_vswitch.
        :param jumbo: Indication if the jumbo frames are used (True) or
            not (False).
        :type node: dict
        :type if1_pci: str
        :type if2_pci: str
        :type compute_resource_info: dict
        :type jumbo: bool
        :raises RuntimeError: If the script "run_testpmd.sh" fails.
        """
        if node[u"type"] != NodeType.DUT:
            raise RuntimeError(f"Testpmd should start only on DUTs.")

        testpmd_args = DpdkUtil.get_testpmd_args(
            eal_corelist=f"1,{compute_resource_info[u'cpu_dp']}",
            eal_driver=False,
            eal_pci_whitelist0=if1_pci,
            eal_pci_whitelist1=if2_pci,
            eal_in_memory=True,
            pmd_num_mbufs=32768,
            pmd_fwd_mode=u"io",
            pmd_nb_ports=u"2",
            pmd_portmask=u"0x3",
            pmd_max_pkt_len=u"9200" if jumbo else u"1518",
            pmd_mbuf_size=u"16384",
            pmd_rxd=compute_resource_info[u"rxd_count_int"],
            pmd_txd=compute_resource_info[u"txd_count_int"],
            pmd_rxq=compute_resource_info[u"rxq_count_int"],
            pmd_txq=compute_resource_info[u"rxq_count_int"],
            pmd_nb_cores=compute_resource_info[u"dp_count_int"],
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
        command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"\
                  f"/entry/check_testpmd.sh"
        message = "Testpmd not started properly"
        exec_cmd_no_error(node, command, timeout=1800, message=message)
