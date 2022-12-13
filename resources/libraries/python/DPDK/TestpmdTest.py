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

import time

from robot.libraries.BuiltIn import BuiltIn
from resources.libraries.python.Constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.DpdkUtil import DpdkUtil
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology


class TestpmdTest:
    """
    This class starts testpmd on topology nodes and checks if ready for traffic.
    """

    @staticmethod
    def start_testpmd_on_all_duts(nodes, topology_info, phy_cores, jumbo):
        """Start the testpmd, make sure it is ready for traffic.

        Also set test tags.

        Just launching testpmd does not ensure it is also ready for traffic,
        see bash function dpdk_testpmd_check for symptoms and workarounds.

        On this level, it suffices to say repeated testpmd restarts do help,
        and check_testpmd is called to detect whether testpmd is ready.

        Testpmd is restarted on both DUTs even if only one of the was not ready,
        to reduce the possibility of any other future error
        (the current DPDK version is not affected by such partial restart).

        Regardless of whether all duts are ready for traffic,
        screenlog is dumped so we can monitor future CSIT-1848 behavior.

        :param nodes: All the nodes info from the topology file.
        :param topology_info: Suite variables as computed from path.
        :param phy_cores: Number of physical cores to use.
        :param jumbo: Jumbo frames on/off.
        :type nodes: dict
        :type topology_info: dict
        :type phy_cores: int
        :type jumbo: bool
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
        duts = [node for node in nodes if u"DUT" in node]
        for dut in duts:
            for restart in range(10):
                TestpmdTest.kill_dpdk(nodes[dut])
                TestpmdTest.start_testpmd(
                    nodes=nodes,
                    dut=dut,
                    topology_info=topology_info,
                    nb_cores=dp_count_int,
                    jumbo=jumbo,
                )
                if TestpmdTest.is_testpmd_ready(nodes[dut]):
                    exec_cmd(nodes[dut], u"cat screenlog.0")
                    break
            else:
                exec_cmd(nodes[dut], u"cat screenlog.0")
                raise RuntimeError(f"Testpmd on {dut} not started properly.")


    @staticmethod
    def start_testpmd(nodes, dut, topology_info, nb_cores, jumbo):
        """Launch testpmd on the DUT node. No not check readiness yet.

        Any previous testpmd instance is assumed to be killed already.

        :param nodes: All the nodes info from the topology file.
        :param node: Name of the intended DUT node.
        :param topology_info: Suite variables as computed from path.
        :param nb_cores: The cores number for the forwarding.
        :param jumbo: Indication if the jumbo frames are used (True) or
            not (False).
        :type nodes: dict
        :type node: str
        :type topology_info: dict
        :type nb_cores: int
        :type jumbo: bool
        :raises RuntimeError: If the script "run_testpmd.sh" fails.
        """
        node = nodes[dut]
        if node[u"type"] != NodeType.DUT:
            raise RuntimeError(f"Testpmd starts only on DUTs, not {dut}")

        compute_info = CpuUtils.get_affinity_vswitch(
            nodes, dut, nb_cores,
        )
        testpmd_args = DpdkUtil.get_testpmd_args(
            eal_corelist=f"1,{compute_info[u'cpu_dp']}",
            eal_driver=False,
            eal_pci_whitelist0=topology_info[f"{dut.lower()}_if1_pci"],
            eal_pci_whitelist1=topology_info[f"{dut.lower()}_if2_pci"],
            eal_in_memory=True,
            pmd_num_mbufs=32768,
            pmd_fwd_mode=u"io",
            pmd_nb_ports=u"2",
            pmd_portmask=u"0x3",
            pmd_max_pkt_len=u"9200" if jumbo else u"1518",
            pmd_mbuf_size=u"16384",
            pmd_rxd=None,
            pmd_txd=None,
            pmd_rxq=compute_info[u"rxq_count_int"],
            pmd_txq=compute_info[u"rxq_count_int"],
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
    def kill_dpdk(node):
        """Kill any dpdk app in the node.

        :param node: DUT node.
        :type node: dict
        :raises RuntimeError: If the script "kill_dpdk.sh" fails.
        """
        command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"\
            f"/entry/kill_dpdk.sh"
        message = f"Failed to kill dpdk at node {node['host']}"
        exec_cmd_no_error(node, command, message=message)

    @staticmethod
    def is_testpmd_ready(node):
        """Execute the testpmd check on the DUT node.

        See description in dpdk_testpmd_check bach function for more details.

        :param node: DUT node.
        :type node: dict
        :returns: False if testpmd is not ready for traffic yet.
        :rtype: bool
        """
        if node[u"type"] != NodeType.DUT:
            return True
        command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"\
                  f"/entry/check_testpmd.sh"
        rc, _, _ = exec_cmd(node, command)
        return rc == 0
