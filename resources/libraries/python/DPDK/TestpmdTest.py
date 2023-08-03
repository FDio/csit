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

"""This module exists to start testpmd on topology nodes."""

from typing import Optional

from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.Constants import Constants
from resources.libraries.python.DPDK.DpdkUtil import DpdkUtil
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology


class TestpmdTest:
    """
    This class starts testpmd on topology nodes and checks if ready for traffic.
    """

    @staticmethod
    def start_testpmd_on_all_duts(
        nodes: dict,
        topology_info: dict,
        phy_cores: int,
        rx_queues: Optional[int] = None,
        jumbo_frames: bool = False,
        rxd: Optional[int] = None,
        txd: Optional[int] = None,
        nic_rxq_size: Optional[int] = None,
        nic_txq_size: Optional[int] = None,
    ) -> None:
        """Start the testpmd app, make sure it is ready for traffic.

        Also set test tags related to threads.
        Keep restarting a few times if not all ports are up.

        :param nodes: All the nodes info from the topology file.
        :param topology_info: All the info from the topology file.
        :param phy_cores: Number of physical cores to use.
        :param rx_queues: Number of RX queues.
        :param jumbo_frames: Jumbo frames on/off.
        :param rxd: Number of RX descriptors.
        :param txd: Number of TX descriptors.
        :param nic_rxq_size: RX queue size.
        :param nic_txq_size: TX queue size.
        :type nodes: dict
        :type topology_info: dict
        :type phy_cores: int
        :type rx_queues: int
        :type jumbo_frames: bool
        :type rxd: int
        :type txd: int
        :type nic_rxq_size: int
        :type nic_txq_size: int
        :raises RuntimeError: If still not ready for traffic after the restarts.
        """

        def start_function(dut_name: str) -> None:
            """Call start_testpmd with added static arguments.

            FIXME: params, types.
            """
            dut_node, if1, if2, cpu_dp, dp_count, rxq_count = DpdkUtil.get_vals(
                nodes=nodes,
                dut_name=dut_name,
                topology_info=topology_info,
                phy_cores=phy_cores,
                rx_queues=rx_queues,
                rxd=rxd,
                txd=txd,
            )
            TestpmdTest.start_testpmd(
                node=dut_node,
                if1=if1,
                if2=if2,
                lcores_list=cpu_dp,
                nb_cores=dp_count,
                queue_nums=rxq_count,
                jumbo_frames=jumbo_frames,
                rxq_size=nic_rxq_size,
                txq_size=nic_txq_size,
            )

        DpdkUtil.start_dpdk_app_on_all_duts(
            start_function=start_function,
            check_function=TestpmdTest.is_testpmd_ready,
            nodes=nodes,
            phy_cores=phy_cores,
        )

    @staticmethod
    def start_testpmd(
        node: dict,
        if1: str,
        if2: str,
        lcores_list: str,
        nb_cores: int,
        queue_nums: str,
        jumbo_frames: bool,
        rxq_size: int = 1024,
        txq_size: int = 1024,
    ) -> None:
        """Launch testpmd on the DUT node. Do not check readiness yet.

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
        :type nb_cores: int
        :type queue_nums: str
        :type jumbo_frames: bool
        :type rxq_size: int
        :type txq_size: int
        :raises RuntimeError: If the script "run_testpmd.sh" fails.
        """
        if node["type"] == NodeType.DUT:
            if_pci0 = Topology.get_interface_pci_addr(node, if1)
            if_pci1 = Topology.get_interface_pci_addr(node, if2)
            pmd_max_pkt_len = "9200" if jumbo_frames else "1518"
            testpmd_args = DpdkUtil.get_testpmd_args(
                eal_corelist=f"1,{lcores_list}",
                eal_driver=False,
                eal_pci_whitelist0=if_pci0,
                eal_pci_whitelist1=if_pci1,
                eal_in_memory=True,
                pmd_num_mbufs=32768,
                pmd_fwd_mode="io",
                pmd_nb_ports="2",
                pmd_portmask="0x3",
                pmd_max_pkt_len=pmd_max_pkt_len,
                pmd_mbuf_size="16384",
                pmd_rxd=rxq_size,
                pmd_txd=txq_size,
                pmd_rxq=queue_nums,
                pmd_txq=queue_nums,
                pmd_nb_cores=nb_cores,
                pmd_auto_start=True,
                pmd_numa=True,
                # The following pair of options makes testpmd act like l3fwd,
                # simplifying readiness check logic.
                pmd_disable_link_check=False,  # For reporting link as up.
                pmd_no_lsc_interrupt=True,  # For not Done when link is down.
            )
            command = (
                f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"
                f'/entry/run_testpmd.sh "{testpmd_args}"'
            )
            message = f"Failed to execute testpmd at node {node['host']}"
            exec_cmd_no_error(node, command, timeout=5, message=message)

    @staticmethod
    def is_testpmd_ready(node: dict) -> bool:
        """Execute the testpmd check on the DUT node.

        See description in dpdk_testpmd_check bash function for more details.

        :param node: DUT node.
        :type node: dict
        :returns: False if testpmd is not ready for traffic yet.
        :rtype: bool
        """
        command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"
        command += "/entry/check_testpmd.sh"
        return_code, _, _ = exec_cmd(node, command)
        return return_code == 0
