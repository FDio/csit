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
This module exists to provide the l3fwd test for DPDK on topology nodes.
"""

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants
from resources.libraries.python.topology import NodeType, Topology

class L3fwdTest(object):
    """Test the DPDK l3fwd performance."""

    @staticmethod
    def start_the_l3fwd_test(nodes_info, dut_node, dut_if1, dut_if2,
                             nb_cores, lcores_list, queue_nums, jumbo_frames):
        """
        Execute the l3fwd on the dut_node.

        :param nodes_info: All the nodes info in the topology file.
        :param dut_node: Will execute the l3fwd on this node
        :param dut_if1: The test link interface 1.
        :param dut_if2: The test link interface 2.
        :param nb_cores: The cores number for the forwarding
        :param lcores_list: The lcore list string for the l3fwd routing
        :param queue_nums: The queues number for the NIC
        :param jumbo_frames: Indication if the jumbo frames are used (True) or
                             not (False).
        :type nodes_info: dict
        :type dut_node: dict
        :type dut_if1: str
        :type dut_if2: str
        :type nb_cores: str
        :type lcores_list: str
        :type queue_nums: str
        :type jumbo_frames: bool
        """
        if dut_node['type'] == NodeType.DUT:
            adj_mac0, adj_mac1 = L3fwdTest.get_adj_mac(nodes_info, dut_node,
                                                       dut_if1, dut_if2)

            list_cores = lcores_list.split(',')

            # prepare the port config param
            index = 0
            port_config = ''
            for port in range(0, 2):
                for queue in range(0, int(queue_nums)):
                    if int(nb_cores) == 1:
                        index = 0
                        temp_str = '({port}, {queue}, {core}),'.\
                        format(port=port, queue=queue,
                               core=int(list_cores[index]))
                    else:
                        temp_str = '({port}, {queue}, {core}),'.\
                        format(port=port, queue=queue,
                               core=int(list_cores[index]))

                    port_config += temp_str
                    index = index + 1

            ssh = SSH()
            ssh.connect(dut_node)

            jumbo = 'yes' if jumbo_frames else 'no'
            cmd = '{fwdir}/tests/dpdk/dpdk_scripts/run_l3fwd.sh ' \
                  '"{lcores}" "{ports}" {mac1} {mac2} {jumbo}'.\
                  format(fwdir=Constants.REMOTE_FW_DIR, lcores=lcores_list,
                         ports=port_config.rstrip(','), mac1=adj_mac0,
                         mac2=adj_mac1, jumbo=jumbo)

            ret_code, _, _ = ssh.exec_command_sudo(cmd, timeout=600)
            if ret_code != 0:
                raise Exception('Failed to execute l3fwd test at node {name}'
                                .format(name=dut_node['host']))

    @staticmethod
    def get_adj_mac(nodes_info, dut_node, dut_if1, dut_if2):
        """
        Get adjacency MAC addresses of the DUT node.

        :param nodes_info: All the nodes info in the topology file.
        :param dut_node: Will execute the l3fwd on this node
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
            L3fwdTest.patch_l3fwd(dut_node, 'patch_l3fwd_flip_routes')

        adj_node0, adj_if_key0 = Topology.get_adjacent_node_and_interface( \
                                 nodes_info, dut_node, if_key0)
        adj_node1, adj_if_key1 = Topology.get_adjacent_node_and_interface( \
                                 nodes_info, dut_node, if_key1)

        adj_mac0 = Topology.get_interface_mac(adj_node0, adj_if_key0)
        adj_mac1 = Topology.get_interface_mac(adj_node1, adj_if_key1)

        return adj_mac0, adj_mac1

    @staticmethod
    def patch_l3fwd(node, patch):
        """
        Patch l3fwd application and recompile.

        :param node: Dictionary created from topology.
        :param patch: Patch to apply.
        :type node: dict
        :type patch: str
        :raises RuntimeError: Patching of l3fwd failed.
        """
        arch = Topology.get_node_arch(node)

        ssh = SSH()
        ssh.connect(node)

        ret_code, _, _ = ssh.exec_command(
            '{fwdir}/tests/dpdk/dpdk_scripts/patch_l3fwd.sh {arch} '
            '{fwdir}/tests/dpdk/dpdk_scripts/{patch}'.
            format(fwdir=Constants.REMOTE_FW_DIR, arch=arch, patch=patch),
                   timeout=600)

        if ret_code != 0:
            raise RuntimeError('Patch of l3fwd failed.')