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
from resources.libraries.python.topology import Topology
from resources.libraries.python.VPPUtil import VPPUtil


class QATUtil:
    """Contains methods for setting up QATs."""

    @staticmethod
    def crypto_device_verify(node, crypto_type, numvfs, force_init=False):
        """Verify if Crypto QAT device virtual functions are initialized on all
        DUTs. If parameter force initialization is set to True, then try to
        initialize or remove VFs on QAT.

        :param node: DUT node.
        :crypto_type: Crypto device type - HW_DH895xcc, HW_C3xxx, HW_C4xxx
                      or HW_4xxx.
        :param numvfs: Number of VFs to initialize, 0 - disable the VFs.
        :param force_init: If True then try to initialize to specific value.
        :type node: dict
        :type crypto_type: string
        :type numvfs: int
        :type force_init: bool
        :returns: nothing
        :raises RuntimeError: If QAT VFs are not created and force init is set
                              to False.
        """
        pci_addr = Topology.get_cryptodev(node)
        sriov_numvfs = DUTSetup.get_sriov_numvfs(node, pci_addr)

        if sriov_numvfs != numvfs:
            if force_init:
                # QAT is not initialized and we want to initialize with numvfs
                QATUtil.crypto_device_init(node, crypto_type, numvfs)
            else:
                raise RuntimeError(
                    f"QAT device failed to create VFs on {node[u'host']}"
                )

    @staticmethod
    def crypto_device_init(node, crypto_type, numvfs):
        """Init Crypto QAT device virtual functions on DUT.

        :param node: DUT node.
        :crypto_type: Crypto device type - HW_DH895xcc, HW_C3xxx, HW_C4xxx
                      or HW_4xxx.
        :param numvfs: Number of VFs to initialize, 0 - disable the VFs.
        :type node: dict
        :type crypto_type: string
        :type numvfs: int
        :returns: nothing
        :raises RuntimeError: If failed to stop VPP or QAT failed to initialize.
        """
        if crypto_type == u"HW_DH895xcc":
            kernel_mod = u"qat_dh895xcc"
            kernel_drv = u"dh895xcc"
        elif crypto_type == u"HW_C3xxx":
            kernel_mod = u"qat_c3xxx"
            kernel_drv = u"c3xxx"
        elif crypto_type == u"HW_C4xxx":
            kernel_mod = u"qat_c4xxx"
            kernel_drv = u"c4xxx"
        elif crypto_type == u"HW_4xxx":
            kernel_mod = u"qat_4xxx"
            kernel_drv = u"4xxx"
        else:
            raise RuntimeError(
                f"Unsupported crypto device type on {node[u'host']}"
            )

        pci_addr = Topology.get_cryptodev(node)

        # QAT device must be re-bound to kernel driver before initialization.
        DUTSetup.verify_kernel_module(node, kernel_mod, force_load=True)

        # Stop VPP to prevent deadlock.
        VPPUtil.stop_vpp_service(node)

        current_driver = DUTSetup.get_pci_dev_driver(
            node, pci_addr.replace(u":", r"\:")
        )
        if current_driver is not None:
            DUTSetup.pci_driver_unbind(node, pci_addr)

        # Bind to kernel driver.
        DUTSetup.pci_driver_bind(node, pci_addr, kernel_drv)

        # Initialize QAT VFs.
        if numvfs > 0:
            DUTSetup.set_sriov_numvfs(node, pci_addr, numvfs)