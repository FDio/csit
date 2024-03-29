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

"""QAT util library."""

from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.VPPUtil import VPPUtil
from resources.libraries.python.ssh import exec_cmd_no_error


class QATUtil:
    """Contains methods for setting up QATs."""

    @staticmethod
    def crypto_device_verify_on_all_duts(nodes):
        """Verify if Crypto QAT device and its virtual functions are initialized
        on all DUTs.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        VPPUtil.stop_vpp_service_on_all_duts(nodes)

        for node in nodes.values():
            if node["type"] == NodeType.DUT:
                cryptodevs = Topology.get_cryptodev(node)
                if not cryptodevs:
                    return
                for device in cryptodevs.values():
                    QATUtil.crypto_device_init(node, device)

    @staticmethod
    def crypto_device_init(node, device):
        """Init Crypto QAT device virtual functions on DUT.

        :param node: DUT node.
        :device: Crypto device entry from topology file.
        :type node: dict
        :type device: dict
        """
        DUTSetup.verify_kernel_module(node, device["module"], force_load=True)

        current_driver = DUTSetup.get_pci_dev_driver(
            node, device["pci_address"].replace(":", r"\:")
        )
        if current_driver is not None:
            DUTSetup.pci_driver_unbind(node, device["pci_address"])
        # Bind to kernel driver.
        DUTSetup.pci_driver_bind(node, device["pci_address"], device["driver"])

        cmd = f"adf_ctl status | grep {device['pci_address']} | "
        cmd += "awk '{print $1}'"
        stdout, _ = exec_cmd_no_error(
            node, cmd, sudo=True, message="Failed to check crypto device!"
        )
        if stdout.strip():
            qat_dev = stdout.split("_")[-1]
            conf_file = f"/etc/{device['driver']}_{qat_dev.strip()}.conf"
            exec_cmd_no_error(
                node, f"adf_ctl --config {conf_file} {stdout.strip()} restart",
                sudo=True, message="Failed to restart crypto device!"
            )
        else:
            raise ValueError("Crypto device error")

        # Initialize QAT VFs.
        if int(device["numvfs"]) > 0:
            path = f"drivers/{device['driver']}"
            DUTSetup.set_sriov_numvfs(
                node, device["pci_address"], path=path,
                numvfs=device["numvfs"]
            )

        if device["driver"] not in ["c4xxx"]:
            for cvf in range(int(device["numvfs"])):
                DUTSetup.pci_vf_driver_unbind(
                    node, device["pci_address"], cvf
                )
                DUTSetup.pci_vf_driver_bind(
                    node, device["pci_address"], cvf, "vfio-pci"
                )
