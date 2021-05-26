# Copyright (c) 2021 Cisco and/or its affiliates.
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

"""IRQ handling library."""

from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.InterfaceUtil import InterfaceUtil


class IrqUtil:
    """Contains methods for managing IRQs."""

    @staticmethod
    def get_pci_interface_irqs(node, pci_addr):
        """Get IRQs for interface in linux specified by PCI address.

        :param node: Topology node.
        :param pci_addr: Linux interface PCI address.
        :type node: dict
        :type pci_addr: str
        :returns: List of IRQs attached to specified interface.
        :rtype: list
        """
        interface = InterfaceUtil.pci_to_eth(node, pci_addr)
        return IrqUtil.get_interface_irqs(node, interface)

    @staticmethod
    def get_interface_irqs(node, interface):
        """Get IRQs for interface in linux.

        :param node: Topology node.
        :param interface: Linux interface name.
        :type node: dict
        :type interface: str
        :returns: List of IRQs attached to specified interface.
        :rtype: list
        """
        irqs = []
        command = u"grep '{interface}-.*TxRx' /proc/interrupts | cut -f1 -d:"
        message = f"Failed to get IRQs for {interface} on {node[u'host']}!"

        stdout, _ = exec_cmd_no_error(
            node, command, timeout=30, sudo=True, message=message
        )

        for line in stdout.splitlines():
            irqs.append(line.strip())

        return irqs

    @staticmethod
    def set_pci_interface_irqs_affinity(node, pci_addr):
        """Set IRQs for interface in linux specified by PCI address.

        :param node: Topology node.
        :param pci_addr: Linux interface PCI address.
        :type node: dict
        :type pci_addr: str
        :returns: List of IRQs attached to specified interface.
        :rtype: list
        """
        interface = InterfaceUtil.pci_to_eth(node, pci_addr)
        IrqUtil.set_interface_irqs(node, interface)

    @staticmethod
    def set_interface_irqs_affinity(node, interface):
        """Set IRQs for interface in linux.

        :param node: Topology node.
        :param interface: Linux interface name.
        :type node: dict
        :type interface: str
        :returns: List of IRQs attached to specified interface.
        :rtype: list
        """
        irqs = []
        command = u"grep '{interface}-.*TxRx' /proc/interrupts | cut -f1 -d:"
        message = f"Failed to get IRQs for {interface} on {node[u'host']}!"

        stdout, _ = exec_cmd_no_error(
            node, command, timeout=30, sudo=True, message=message
        )

        for line in stdout.splitlines():
            irqs.append(line.strip())

        return irqs
