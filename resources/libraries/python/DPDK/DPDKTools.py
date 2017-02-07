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


"""This module implements initialization and cleanup of DPDK environment."""

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants as con
from resources.libraries.python.topology import Topology


class DPDKTools(object):
    """This class implements:
    - Initialization of DPDK environment,
    - Cleanup of DPDK environment.
    """

    @staticmethod
    def initialize_dpdk_environment(dut_node, dut_if1, dut_if2):
        """
        Initialize the DPDK test environment on the dut_node.
        Load the module uio and igb_uio, then bind the test NIC to the igb_uio.

        :param dut_node: Will init the DPDK on this node.
        :param dut_if1: DUT interface name.
        :param dut_if2: DUT interface name.
        :type dut_node: dict
        :type dut_if1: str
        :type dut_if2: str
        :returns: none
        :raises RuntimeError: If it fails to bind the interfaces to igb_uio.
        """
        pci_address1 = Topology.get_interface_pci_addr(dut_node, dut_if1)
        pci_address2 = Topology.get_interface_pci_addr(dut_node, dut_if2)

        ssh = SSH()
        ssh.connect(dut_node)

        cmd = 'cd {0}/dpdk-tests/dpdk_scripts/ && sudo ./init_dpdk.sh {1} {2}' \
              .format(con.REMOTE_FW_DIR, pci_address1, pci_address2)

        (ret_code, _, _) = ssh.exec_command(cmd, timeout=600)
        if ret_code != 0:
            raise RuntimeError('Failed to bind the interfaces to igb_uio at '
                               'node {0}'.format(dut_node['host']))

    @staticmethod
    def cleanup_dpdk_environment(dut_node, dut_if1, dut_if2):
        """
        Cleanup the DPDK test environment on the DUT node.
        Unbind the NIC from the igb_uio and bind them to the kernel driver.

        :param dut_node: Will cleanup the DPDK on this node.
        :param dut_if1: DUT interface name.
        :param dut_if2: DUT interface name.
        :type dut_node: dict
        :type dut_if1: str
        :type dut_if2: str
        :returns: none
        :raises RuntimeError: If it fails to cleanup the dpdk.
        """
        pci_address1 = Topology.get_interface_pci_addr(dut_node, dut_if1)
        if1_driver = 'igb_uio'
        pci_address2 = Topology.get_interface_pci_addr(dut_node, dut_if2)
        if2_driver = 'igb_uio'

        ssh = SSH()
        ssh.connect(dut_node)

        cmd = 'cd {0}/dpdk-tests/dpdk_scripts/ && sudo ./cleanup_dpdk.sh ' \
              '{1} {2} {3} {4}'.format(con.REMOTE_FW_DIR, if1_driver,
                                       pci_address1, if2_driver, pci_address2)

        (ret_code, _, _) = ssh.exec_command(cmd, timeout=600)
        if ret_code != 0:
            raise RuntimeError('Failed to cleanup the dpdk at node {0}'
                               .format(dut_node['host']))
