# Copyright (c) 2023 Intel and/or its affiliates.
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
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.ssh import exec_cmd_no_error


class DMAUtil:
    """Common DMA utilities"""

    staticmethod
    def get_dma_info(node, dma_device):
        """Get DMA informations from DMA device.

        :param node: Topology node.
        :param dma_device: DMA device.
        :type node: dict
        :type dma_device: str
        :returns: DMA informations.
        :rtype: dict
        """

        cmd = f"ls /sys/bus/pci/devices/{dma_device} | grep dsa"
        stdout, _ = exec_cmd_no_error(
            node, cmd, sudo=True,
            message=u"Failed to get DMA name on DUT.")
        dma_name = stdout.strip()

        cmd = f"cat /sys/bus/pci/devices/{dma_device}/dsa*/max_work_queues_size"
        stdout, _ = exec_cmd_no_error(
            node, cmd, sudo=True,
            message=u"Failed to get DMA name on DUT.")
        max_work_queues_size = stdout.strip()

        cmd = f"ls /sys/bus/pci/devices/{dma_device}/{dma_name}"
        stdout, _ = exec_cmd_no_error(
            node, cmd, sudo=True, message=u"Failed to get DMA info on DUT.")

        dma_info = dict()
        dma_info[u'dma_device'] = dma_device
        dma_info[u'dma_name'] = dma_name
        dma_info[u'max_work_queues_size'] = max_work_queues_size
        dma_info[u'engine'] = list()
        dma_info[u'wq'] = list()
        dma_info[u'group'] = list()

        for dev in stdout.split():
            g = search(r"^(engine|group|wq)\d+\.\d+", dev)
            if g is None:
                continue
            dev_type = g.group(1)
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
                message=u"Failed to get dma state.")
        if stdout.strip() == "disabled":
            return

        cmd = f"accel-config disable-device -f {dma_name}"
        exec_cmd_no_error(
            node, cmd, sudo=True,
            message=u"Failed to disable DMA on DUT.")

    @staticmethod
    def enable_dma_device(node, dma_name, groups, engines, wqs, wq_size):
        """Enable DMA device.

        :param node: Topology node.
        :param dma_name: DMA name.
        :param engines: DMA engines.
        :param wqs: DMA work queues.
        :type node: dict
        :type dma_name: str
        :type engines: list
        :type wqs: list
        """
        # configure DMA group
        for i, group in enumerate(groups):
            cmd = f"accel-config config-group " \
                    f"{dma_name}/{group} --read-buffers-reserved=0"

            exec_cmd_no_error(
                node, cmd, sudo=True,
                message=u"Failed to configure DMA group on DUT.")

        # configure DMA engine
        for i, engine in enumerate(engines):
            cmd = f"accel-config config-engine " \
                    f"{dma_name}/{engine} --group-id={i}"

            exec_cmd_no_error(
                node, cmd, sudo=True,
                message=u"Failed to configure DMA engine on DUT.")

        # configure DMA work queue
        for i, wq in enumerate(wqs):
            cmd = f"sudo -E -S accel-config config-wq {dma_name}/{wq} " \
                f" --group-id={i%len(engines)} --type=user --priority=10 " \
                f" --wq-size={wq_size} --mode=dedicated -b 1 " \
                f" --name=test_dma"

            exec_cmd_no_error(
                node, cmd, sudo=True,
                message=u"Failed to configure DMA work queue on DUT.")

        # enable DMA and work queues
        cmd = f"accel-config enable-device {dma_name}"
        exec_cmd_no_error(
            node, cmd, sudo=True,
            message=u"Failed to enable DMA device on DUT.")

        dma_wqs = [f"{dma_name}/{wq}" for wq in wqs]
        cmd = f"accel-config enable-wq {' '.join(dma_wqs)}"
        exec_cmd_no_error(
            node, cmd, sudo=True,
            message=u"Failed to enable DMA work queue on DUT.")

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
            dev_pci = dev[u"pci_address"]
            dma_info = DMAUtil.get_dma_info(node, dev_pci)

            dma_name = dma_info[u"dma_name"]
            groups = dma_info[u"group"]
            engines = dma_info[u"engine"]
            wqs = dma_info[u"wq"]
            wq_num_per_dma = wq_num//len(dma_devs) if wq_num > 1 else 1
            wq_size = int(dma_info[u"max_work_queues_size"])//wq_num_per_dma

            DMAUtil.disable_dma_device(node, dma_name)
            DMAUtil.enable_dma_device(node,
                    dma_name,
                    groups[:wq_num_per_dma],
                    engines[:wq_num_per_dma],
                    wqs[:wq_num_per_dma],
                    wq_size)
            enabled_wqs += wqs[:wq_num//len(dma_devs)]

        cmd = u"accel-config list"
        exec_cmd_no_error(
            node, cmd, sudo=True, message=u"Failed")

        return enabled_wqs
