# Copyright (c) 2018 Cisco and/or its affiliates.
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
This module is to provide the Load balancer test on topology nodes.
"""

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants
from resources.libraries.python.topology import NodeType, Topology

class LoadBalancerUtil(object):
    """Test the VPP loadbalancer performance."""

    @staticmethod
    def vpp_setup_load_balancer(nodes_info, dut_node, dut_if1, dut_if2, lb_mode):
        """
        Execute the load balancer test on the dut_node.

        :param nodes_info: All the nodes info in the topology file.
        :param dut_node: Will execute the test on this node
        :param dut_if1: The test link interface 1.
        :param dut_if2: The test link interface 2.
        :param lb_mode: load balancer mode (maglev or l3dsr or nat).
        :type nodes_info: dict
        :type dut_node: dict
        :type dut_if1: str
        :type dut_if2: str
        :type lb_mode: str
        """
        if dut_node['type'] == NodeType.DUT:
            adj_mac0, adj_mac1 = LoadBalancerUtil.get_adj_mac_addr( \
                                 nodes_info, dut_node, dut_if1, dut_if2)

            intf0 = Topology.get_interface_name(dut_node, dut_if1)
            intf1 = Topology.get_interface_name(dut_node, dut_if2)

            ssh = SSH()
            ssh.connect(dut_node)

            if lb_mode == "maglev":
                cmd = '{0}/resources/libraries/bash/lb/lb_maglev.sh ' \
                      '{1} {2} {3} {4} '.format(Constants.REMOTE_FW_DIR, \
                       intf0, adj_mac0, intf1, adj_mac1)

            elif lb_mode == "l3dsr":
                cmd = '{0}/resources/libraries/bash/lb/lb_l3dsr.sh ' \
                      '{1} {2} {3} {4} '.format(Constants.REMOTE_FW_DIR, \
                       intf0, adj_mac0, intf1, adj_mac1)

            elif lb_mode == "nat":
                cmd = '{0}/resources/libraries/bash/lb/lb_nat.sh ' \
                  '{1} {2} {3} {4} '.format(Constants.REMOTE_FW_DIR, \
                   intf0, adj_mac0, intf1, adj_mac1)

            else:
                raise Exception('No load balancer mode specified')

            ret_code, _, _ = ssh.exec_command_sudo(cmd, timeout=120)
            if ret_code != 0:
                raise Exception('Failed to execute lb {0} test at node {1}'
                                .format(lb_mode, dut_node['host']))


    @staticmethod
    def get_adj_mac_addr(nodes_info, dut_node, dut_if1, dut_if2):
        """
        Get adjacency MAC addresses of the DUT node.

        :param nodes_info: All the nodes info in the topology file.
        :param dut_node: Will execute the load balancer on this node
        :param dut_if1: The test link interface 1.
        :param dut_if2: The test link interface 2.
        :type nodes_info: dict
        :type dut_node: dict
        :type dut_if1: str
        :type dut_if2: str
        :returns: Returns MAC addresses of adjacency DUT nodes.
        :rtype: str
        """
        if_key0 = dut_if1
        if_key1 = dut_if2
        if_pci0 = Topology.get_interface_pci_addr(dut_node, if_key0)
        if_pci1 = Topology.get_interface_pci_addr(dut_node, if_key1)

        # detect which is the port 0
        if min(if_pci0, if_pci1) != if_pci0:
            if_key0, if_key1 = if_key1, if_key0

        adj_node0, adj_if_key0 = Topology.get_adjacent_node_and_interface( \
                                 nodes_info, dut_node, if_key0)
        adj_node1, adj_if_key1 = Topology.get_adjacent_node_and_interface( \
                                 nodes_info, dut_node, if_key1)

        adj_mac0 = Topology.get_interface_mac(adj_node0, adj_if_key0)
        adj_mac1 = Topology.get_interface_mac(adj_node1, adj_if_key1)

        return adj_mac0, adj_mac1
