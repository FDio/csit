# Copyright (c) 2024 Intel and/or its affiliates.
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

"""DMA util library."""

from re import search

from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology


class DMAUtil:
    """Common DMA utilities"""

    @staticmethod
    def get_dma_resource(node, dma_device):
        """Get DMA resource from DMA device.

        :param node: Topology node.
        :param dma_device: DMA device.
        :type node: dict
        :type dma_device: str
        :returns: DMA resource.
        :rtype: dict
        """

        cmd = f"grep -H . /sys/bus/pci/devices/{dma_device}/dsa*/*"
        _, stdout, stderr = exec_cmd(node, cmd, sudo=True)

        dma_info = dict()
        dma_info["dma_device"] = dma_device
        dma_info["engine"] = list()
        dma_info["wq"] = list()
        dma_info["group"] = list()

        for line in stdout.split():
            g1 = search(r"/(dsa\d+)/(.+):(.+)", line)
            if g1 is not None:
                dma_info["dma_name"] = g1.group(1)
                dma_info[f"{g1.group(2)}"] = g1.group(3)

        for line in stderr.split():
            g2 = search(r"/(dsa\d+)/((engine|group|wq)\d+\.\d+)", line)
            if g2 is not None:
                dev_type = g2.group(3)
                dev = g2.group(2)
                dma_info[dev_type].append(dev)

        return dma_info

    @staticmethod
    def disable_dma_device(node, dma_name):
        """Disable DMA device.

        :param node: Topology node.
        :param dma_name: DMA name.
        :type node: dict
        :type dma_name: str
        """
        cmd = f"cat /sys/bus/dsa/devices/{dma_name}/state"
        stdout, _ = exec_cmd_no_error(
                node, cmd, sudo=True,
                message="Failed to get dma state.")
        if stdout.strip() == "disabled":
            return

        cmd = f"accel-config disable-device -f {dma_name}"
        exec_cmd_no_error(
            node, cmd, sudo=True,
            message="Failed to disable DMA on DUT.")

    @staticmethod
    def enable_dma_device(node, dma_name, groups, engines, wqs, wq_size,
            max_batch_size, max_transfer_size):
        """Enable DMA device.

        :param node: Topology node.
        :param dma_name: DMA name.
        :param groups: DMA groups.
        :param engines: DMA engines.
        :param wqs: DMA work queues.
        :param wq_size: DMA work queue size.
        :param max_batch_size: Wq max batch size.
        :param max_transfer_size: Wq max transfer size.
        :type node: dict
        :type dma_name: str
        :type groups: list
        :type engines: list
        :type wqs: list
        :type wq_size: int
        :type max_batch_size: int
        :type max_transfer_size: int
        """

        # Configure Device
        cmd = f"accel-config config-device {dma_name}"

        exec_cmd_no_error(
            node, cmd, sudo=True,
            message="Failed to configure DMA device on DUT.")

        # Configure DMA group
        for i, group in enumerate(groups):
            cmd = f"accel-config config-group " \
                    f"{dma_name}/{group} --read-buffers-reserved=0"

            exec_cmd_no_error(
                node, cmd, sudo=True,
                message="Failed to configure DMA group on DUT.")

        # Configure DMA engine
        for i, engine in enumerate(engines):
            cmd = f"accel-config config-engine " \
                    f"{dma_name}/{engine} --group-id={i}"

            exec_cmd_no_error(
                node, cmd, sudo=True,
                message="Failed to configure DMA engine on DUT.")

        # Configure DMA work queue
        for i, wq in enumerate(wqs):
            cmd = f"accel-config config-wq {dma_name}/{wq} " \
                f" --group-id={i%len(engines)} --type=user " \
                f" --priority=10 --block-on-fault=1 " \
                f" --wq-size={wq_size} --mode=dedicated " \
                f" --name={dma_name}_{i} " \
                f" --max-batch-size={max_batch_size} " \
                f" --max-transfer-size={max_transfer_size} "

            exec_cmd_no_error(
                node, cmd, sudo=True,
                message="Failed to configure DMA work queue on DUT.")

        # Enable DMA and work queues
        cmd = f"accel-config enable-device {dma_name}"
        exec_cmd_no_error(
            node, cmd, sudo=True,
            message="Failed to enable DMA device on DUT.")

        dma_wqs = [f"{dma_name}/{wq}" for wq in wqs]
        cmd = f"accel-config enable-wq {' '.join(dma_wqs)}"
        exec_cmd_no_error(
            node, cmd, sudo=True,
            message="Failed to enable DMA work queue on DUT.")

    @staticmethod
    def enable_dmas_and_wqs_on_dut(node, wq_num):
        """Enable DMAs and work queues on DUT.

        :param node: Topology node.
        :param wq_num: Number of work queues.
        :type node: dict
        :type wq_num: int
        :returns: DMA work queues enabled.
        :rtype: list
        """
        if node["type"] == NodeType.DUT:
            dma_devs = Topology.get_bus(node)

        enabled_wqs = list()

        for dev in dma_devs.values():
            if "Intel-DSA" not in dev["model"]:
                continue

            dev_pci = dev["pci_address"]
            dma_info = DMAUtil.get_dma_resource(node, dev_pci)

            dma_name = dma_info["dma_name"]
            groups = dma_info["group"]
            engines = dma_info["engine"]
            wqs = dma_info["wq"]
            wq_num_per_dma = wq_num//len(dma_devs) if wq_num > 1 else 1
            max_transfer_size = \
                    int(dma_info["max_transfer_size"])//wq_num_per_dma
            wq_size = int(dma_info["max_work_queues_size"])//wq_num_per_dma
            max_batch_size = int(dma_info["max_batch_size"])

            DMAUtil.disable_dma_device(node, dma_name)

            DMAUtil.enable_dma_device(node,
                    dma_name,
                    groups[:wq_num_per_dma],
                    engines[:wq_num_per_dma],
                    wqs[:wq_num_per_dma],
                    wq_size,
                    max_batch_size,
                    max_transfer_size
                    )
            enabled_wqs += wqs[:wq_num_per_dma]

            cmd = f"lspci -vvv -s {dev_pci}"
            exec_cmd_no_error(
                node, cmd, sudo=True, message="Failed")

        cmd = "accel-config list"
        exec_cmd_no_error(
            node, cmd, sudo=True, message="Failed")

        cmd = "cat /proc/cmdline"
        exec_cmd_no_error(
            node, cmd, sudo=True, message="Failed")

        return enabled_wqs

    @staticmethod
    def vpp_show_dma(node):
        """Call show dma CLI command on all sockets.

        :param node: Topology node.
        :type node: dict
        """
        PapiSocketExecutor.run_cli_cmd_on_all_sockets(node, u"show dma")
