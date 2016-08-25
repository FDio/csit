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
This module exists to provide the init DPDK.
"""

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants as con
from resources.libraries.python.topology import Topology

class DPDKTools(object): # pylint: disable=too-few-public-methods
    """Test the DPDK l2fwd performance."""

    @staticmethod
    def initialize_dpdk_environment(dut_node, dut_if1, dut_if2):
        """
        Execute the udpfwd on the dut_node.

        :param dut_node: will execute the udpfwd on this node
        :param dut_if: DUT interface name
        :param file_prefix: the test case config file prefix
        :param dest_ip: the UDP packet dest IP
        :param is_ipv4: execute the IPv4 or IPv6 test
        :type dut_node: dict
        :type dut_if: str
        :type file_prefix: str
        :type dest_ip: str
        :type is_ipv4: bool
        :return: none
        """
        pci_address1 = Topology.get_interface_pci_addr(dut_node, dut_if1)
        pci_address2 = Topology.get_interface_pci_addr(dut_node, dut_if2)

        ssh = SSH()
        ssh.connect(dut_node)

        cmd = 'cd {0}/dpdk-tests/dpdk_scripts/ && ./init_dpdk.sh {1} {2}' \
              .format(con.REMOTE_FW_DIR, pci_address1, pci_address2)

        logger.console('Will Execute the cmd: {0}'.format(cmd))

        (ret_code, _, stderr) = ssh.exec_command(cmd, timeout=600)
        if 0 != ret_code:
            logger.error('bind the interface to igb_uio error: {0}'.format(stderr))
            raise Exception('Failed to bind the interfaces to igb_uio at node {0}'
                            .format(dut_node['host']))

    @staticmethod
    def cleanup_dpdk_environment(dut_node, dut_if1, dut_if2):
    
        pci_address1 = Topology.get_interface_pci_addr(dut_node, dut_if1)
        if1_driver = Topology.get_interface_driver(dut_node, dut_if1)
        pci_address2 = Topology.get_interface_pci_addr(dut_node, dut_if2)
        if2_driver = Topology.get_interface_driver(dut_node, dut_if2)

        ssh = SSH()
        ssh.connect(dut_node)
   
        cmd = 'cd {0}/dpdk-tests/dpdk_scripts/ && ./cleanup_dpdk.sh {1} {2} {3} {4}' \
              .format(con.REMOTE_FW_DIR, if1_driver, pci_address1, if2_driver, pci_address2)

        logger.console('Will Execute the cmd: {0}'.format(cmd))

        (ret_code, _, stderr) = ssh.exec_command(cmd, timeout=600)
        if 0 != ret_code:
            logger.error('cleanup the dpdk  error: {0}'.format(stderr))
            raise Exception('Failed to cleanup the dpdk at node {0}'
                            .format(dut_node['host']))
