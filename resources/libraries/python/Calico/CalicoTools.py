# Copyright (c) 2026  Cisco and/or its affiliates.
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
This module deploys Calico framework on node.
"""

from robot.libraries.BuiltIn import BuiltIn
from resources.libraries.python.Constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology


class CalicoTools:
    """Calico utilities."""

    @staticmethod
    def deploy_calico_vpp_on_all_duts(
            nodes, topology_info, phy_cores, rx_queues=None, jumbo=False,
            rxd=None, txd=None):
        """
        Deploy calico on all DUT nodes.

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
        compute_resource_info = CpuUtils.get_affinity_vswitch(
            nodes, phy_cores, rx_queues=rx_queues, rxd=rxd, txd=txd
        )
        for node_name, node in nodes.items():
            if node["type"] == NodeType.DUT:
                if dp_count_int > 1:
                    BuiltIn().set_tags("MTHREAD")
                else:
                    BuiltIn().set_tags("STHREAD")
                BuiltIn().set_tags(
                    f"{dp_count_int}T{cpu_count_int}C"
                )

                cpu_dp = compute_resource_info[f"{node_name}_cpu_dp"]
                cpu_dp = [f"{i+1}@{x}" for i,x in enumerate(cpu_dp.split(","))]
                cpu_dp = ",".join(cpu_dp)
                rxq_count_int = compute_resource_info["rxq_count_int"]

                command = (
                    f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"
                    f"/entry/run_testpmd.sh \"{testpmd_args}\""
                )
                message = f"Failed to execute testpmd at node {node['host']}"
                exec_cmd_no_error(node, command, timeout=1800, message=message)