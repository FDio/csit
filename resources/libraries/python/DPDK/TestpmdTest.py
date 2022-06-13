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

"""This module implements functionality which sets L2 forwarding for DPDK on
DUT nodes.
"""

from resources.libraries.python.Constants import Constants
from resources.libraries.python.DpdkUtil import DpdkUtil
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology


class TestpmdTest:
    """Setup the DPDK for testpmd performance test."""

    @staticmethod
    def start_testpmd(
            node, if1, if2, lcores_list, nb_cores, queue_nums,
            jumbo_frames, rxq_size=1024, txq_size=1024):
        """
        Execute the testpmd on the DUT node.

        :param node: DUT node.
        :param if1: The test link interface 1.
        :param if2: The test link interface 2.
        :param lcores_list: The DPDK run cores.
        :param nb_cores: The cores number for the forwarding.
        :param queue_nums: The queues number for the NIC.
        :param jumbo_frames: Indication if the jumbo frames are used (True) or
            not (False).
        :param rxq_size: RXQ size. Default=1024.
        :param txq_size: TXQ size. Default=1024.
        :type node: dict
        :type if1: str
        :type if2: str
        :type lcores_list: str
        :type nb_cores: str
        :type queue_nums: str
        :type jumbo_frames: bool
        :type rxq_size: int
        :type txq_size: int
        :raises RuntimeError: If the script "run_testpmd.sh" fails.
        """
        if node[u"type"] == NodeType.DUT:
            if_pci0 = Topology.get_interface_pci_addr(node, if1)
            if_pci1 = Topology.get_interface_pci_addr(node, if2)

            pmd_max_pkt_len = u"9200" if jumbo_frames else u"1518"
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
