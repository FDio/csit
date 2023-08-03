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


"""This module implements initialization and cleanup of DPDK framework."""

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology


class DPDKTools:
    """This class implements:
    - Initialization of DPDK environment,
    - Cleanup of DPDK environment.
    """

    @staticmethod
    def initialize_dpdk_framework(
        node: dict, if1: str, if2: str, nic_driver: str
    ) -> None:
        """
        Initialize the DPDK framework on the DUT node. Bind interfaces to
        driver.

        :param node: DUT node.
        :param if1: DUT first interface name.
        :param if2: DUT second interface name.
        :param nic_driver: Interface driver.
        :type node: dict
        :type if1: str
        :type if2: str
        :type nic_driver: str
        :raises RuntimeError: If it fails to bind the interfaces to driver.
        """
        if node["type"] == NodeType.DUT:
            pci_address1 = Topology.get_interface_pci_addr(node, if1)
            pci_address2 = Topology.get_interface_pci_addr(node, if2)

            command = (
                f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"
                f"/entry/init_dpdk.sh "
                f"{nic_driver} {pci_address1} {pci_address2}"
            )
            message = "Initialize the DPDK failed!"
            exec_cmd_no_error(node, command, timeout=600, message=message)

    @staticmethod
    def cleanup_dpdk_framework(node: dict, if1: str, if2: str) -> None:
        """
        Cleanup the DPDK framework on the DUT node. Bind interfaces to
        default driver specified in topology.

        :param node: Will cleanup the DPDK on this node.
        :param if1: DUT first interface name.
        :param if2: DUT second interface name.
        :type node: dict
        :type if1: str
        :type if2: str
        :raises RuntimeError: If it fails to cleanup the dpdk.
        """
        if node["type"] == NodeType.DUT:
            pci_address1 = Topology.get_interface_pci_addr(node, if1)
            pci_address2 = Topology.get_interface_pci_addr(node, if2)
            # We are not supporting more than one driver yet.
            nic_driver = Topology.get_interface_driver(node, if1)

            command = (
                f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"
                f"/entry/cleanup_dpdk.sh "
                f"{nic_driver} {pci_address1} {pci_address2}"
            )
            message = "Cleanup the DPDK failed!"
            exec_cmd_no_error(node, command, timeout=1200, message=message)

    @staticmethod
    def get_dpdk_version(node: dict) -> str:
        """Log and return the installed DPDK version.

        The logged string ends with newline, the returned one is stripped.

        :param node: Node from topology file.
        :type node: dict
        :returns: Stripped DPDK version string.
        :rtype: str
        :raises RuntimeError: If command returns nonzero return code.
        """
        command = f"cat {Constants.REMOTE_FW_DIR}/dpdk*/VERSION"
        message = "Get DPDK version failed!"
        stdout, _ = exec_cmd_no_error(node, command, message=message)
        # TODO: PAL should already tolerate stripped value in the log.
        logger.info(f"DPDK Version: {stdout}")
        return stdout.strip()

    @staticmethod
    def install_dpdk_framework(node: dict) -> None:
        """
        Prepare the DPDK framework on the DUT node.

        :param node: Node from topology file.
        :type node: dict
        :raises RuntimeError: If command returns nonzero return code.
        """
        command = (
            f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"
            f"/entry/install_dpdk.sh"
        )
        message = "Install the DPDK failed!"
        exec_cmd_no_error(node, command, timeout=3600, message=message)
        DPDKTools.get_dpdk_version(node)

    @staticmethod
    def install_dpdk_framework_on_all_duts(nodes: dict) -> None:
        """
        Prepare the DPDK framework on all DUTs.

        :param nodes: Nodes from topology file.
        :type nodes: dict
        """
        for node in list(nodes.values()):
            if node["type"] == NodeType.DUT:
                DPDKTools.install_dpdk_framework(node)
