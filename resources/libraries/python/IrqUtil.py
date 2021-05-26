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

from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import Topology


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

        command = f"grep '{interface}-.*TxRx' /proc/interrupts | cut -f1 -d:"
        message = f"Failed to get IRQs for {interface} on {node['host']}!"
        stdout, _ = exec_cmd_no_error(
            node, command, timeout=30, sudo=True, message=message
        )

        for line in stdout.splitlines():
            irqs.append(int(line.strip()))

        return irqs

    @staticmethod
    def set_interface_irqs_affinity(node, interface, cpu_skip_cnt=0, cpu_cnt=1):
        """Set IRQs affinity for interface in linux.

        :param node: Topology node.
        :param interface: Topology interface.
        :param cpu_skip_cnt: Amount of CPU cores to skip.
        :param cpu_cnt: CPU threads count. (Optional, Default: 0)
        :param cpu_list: List of CPUs. (Optional, Default: 1)
        :type node: dict
        :type interface: str
        :type cpu_skip_cnt: int
        :type cpu_cnt: int
        """
        cpu_list = CpuUtils.get_affinity_af_xdp(
            node, interface, cpu_skip_cnt=cpu_skip_cnt, cpu_cnt=cpu_cnt
        )
        interface = Topology.get_interface_name(node, interface)
        irq_list = IrqUtil.get_interface_irqs(node, interface)

        for irq, cpu in zip(irq_list, cpu_list):
            if cpu < 32:
                mask = 1 << cpu
                mask = f"{mask:x}"
            else:
                groups = int(cpu/32)
                mask_fill = u""
                for _ in range(groups):
                    mask_fill = f"{mask_fill},00000000"
                mask = 1 << (cpu - (32 * groups))
                mask = f"{mask:x}{mask_fill}"

            command = f"sh -c 'echo {mask} > /proc/irq/{irq}/smp_affinity'"
            message = f"Failed to set IRQ affinity for {irq} on {node['host']}!"
            exec_cmd_no_error(
                node, command, timeout=30, sudo=True, message=message
            )
