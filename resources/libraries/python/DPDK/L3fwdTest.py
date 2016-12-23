# Copyright (c) 2016 Cisco and/or its affiliates.
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

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants as con
from resources.libraries.python.topology import Topology

class L3fwdTest(object):
    """Test the DPDK l3fwd performance."""

    @staticmethod
    def start_the_l3fwd_test(nodes_info, dut_node, cpu_coremask, nb_cores, lcores_list, queue_nums,
                            jumbo_frames):
        """
        Execute the l3fwd on the dut_node.

        :param nodes_info: all the nodes info in the topology file.
        :param dut_node: will execute the l2fwd on this node
        :param cpu_coremask: the DPDK run core mask
        :param nb_cores: the cores number for the forwarding
        :param lcores_list: the lcore list for the l3fwd routing
        :param queue_nums: the queues number for the NIC
        :param jumbo_frames: is jumbo frames or not
        :type nodes_info: dict
        :type dut_node: dict
        :type cpu_coremask: str
        :type nb_cores: str
        :type lcores_list: list
        :type queue_nums: str
        :type jumbo_frames: str
        :return: none
        """
        #in here, we just get all the DUT node if, maybe get the used_if for better.
        if_keys = Topology.get_node_interfaces(dut_node)

        if_key0 = if_keys[0]
        if_key1 = if_keys[1]
        if_pci0 = Topology.get_interface_pci_addr(dut_node, if_key0)
        if_pci1 = Topology.get_interface_pci_addr(dut_node, if_key1)

        #detect which is the port 0
        if min(if_pci0, if_pci1) != if_pci0:
            if_key0, if_key1 = if_key1, if_key0
            if_pci0, if_pci1 = if_pci1, if_pci0

        adj_node0, adj_if_key0 = Topology.get_adjacent_node_and_interface(nodes_info, dut_node, if_key0)
        adj_node1, adj_if_key1 = Topology.get_adjacent_node_and_interface(nodes_info, dut_node, if_key1)

        adj_mac0 = Topology.get_interface_mac(adj_node0, adj_if_key0)
        adj_mac1 = Topology.get_interface_mac(adj_node1, adj_if_key1)

        #prepare the port config param
        index = 0
        port_config = ''
        for port in range(0,2):
            for queue in range(0, int(queue_nums)):
                if int(nb_cores) == 1:
                    index = 0
                    temp_str = '({0}, {1}, {2}),'.format(port, queue, lcores_list[index])
                else:
                    temp_str = '({0}, {1}, {2}),'.format(port, queue, lcores_list[index])

                port_config += temp_str
                index = index + 1

        port_config_param = port_config.rstrip(',')

        ssh = SSH()
        ssh.connect(dut_node)

        cmd = 'cd {0}/dpdk-tests/dpdk_scripts/ && ./run_l3fwd.sh {1} {2} {3} {4} {5}' \
              .format(con.REMOTE_FW_DIR, cpu_coremask,
              port_config_param, adj_mac0, adj_mac1, jumbo_frames)

        logger.console('Will Execute the cmd: {0}'.format(cmd))

        (ret_code, _, stderr) = ssh.exec_command(cmd, timeout=600)
        if 0 != ret_code:
            logger.error('Execute the l3fwd error: {0}'.format(stderr))
            raise Exception('Failed to execute l3fwd test at node {0}'
                            .format(dut_node['host']))

