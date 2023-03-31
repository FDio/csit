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
from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd


class DMAUtil:
    """Utilities for DMA's configuration tool accel-config."""

    @staticmethod
    def get_dma_device_info_on_dut(node):
        """Get DMA device information on DUT.

        :param node: Topology node.
        :type node: dict
        :returns: DMA device information on DUT.
        :rtype: dict
        """
        cmd = u"ls /sys/bus/dsa/devices"
        stdout, _ = exec_cmd_no_error(
            node, cmd, sudo=True, message=u"Failed to get DMA device on DUT.",
            retries=3)

        dma_device_info = {}
        for dev_name in stdout.split():
            if u"dsa" in dev_name:
                dma_device_info.setdefault(u"dma_list", [])
                dma_device_info[u"dma_list"].append(dev_name)
            elif u"engine" in dev_name:
                dma_device_info.setdefault(u"engine_list", [])
                dma_device_info[u"engine_list"].append(dev_name)
            elif u"group" in dev_name:
                dma_device_info.setdefault(u"group_list", [])
                dma_device_info[u"group_list"].append(dev_name)
            elif u"wq" in dev_name:
                dma_device_info.setdefault(u"wq_list", [])
                dma_device_info[u"wq_list"].append(dev_name)
        return dma_device_info

    @staticmethod
    def disable_dma_device_on_dut(node, dma_device_name):
        """Disable DMA device on DUT.

        :param node: Topology node.
        :param dma_device_name: Name of DMA device.
        :type node: dict
        :type dma_device_name: str
        :returns: All DMA device information.
        :rtype: dict
        """
        # disable all work queues of DMA device on DUT
        wq_list = []
        dma_device_info = DMAUtil.get_dma_device_info_on_dut(node)
        dma_num = dma_device_name.replace("dsa", "")
        for wq in dma_device_info[u"wq_list"]:
            wq_num = wq.split(".")[0].replace("wq", "")
            if wq_num == dma_num:
                wq_list.append(wq)

        for wq in wq_list:
            cmd = f"cat /sys/bus/dsa/devices/{dma_device_name}/{wq}/state"
            stdout, _ = exec_cmd_no_error(
                node, cmd, sudo=True,
                message=u"Failed to get work queue state.")
            if stdout.strip() == "enabled":
                cmd = f"accel-config disable-wq {dma_device_name}/{wq}"
                exec_cmd_no_error(
                    node, cmd, sudo=True,
                    message=u"Failed to disable work queues of DMA device \
                            on DUT.")

        # disable all DMA device on DUT
        cmd = f"cat /sys/bus/dsa/devices/{dma_device_name}/state"
        stdout, _ = exec_cmd_no_error(
                node, cmd, sudo=True,
                message=u"Failed to get work queue state.")
        if stdout.strip() == "enabled":
            cmd = f"accel-config disable-device {dma_device_name}"
            exec_cmd_no_error(
                node, cmd, sudo=True,
                message=u"Failed to disable DMA device on DUT.")

    @staticmethod
    def enable_dma_device_on_dut(node, dma_device_name, wq_count):
        """Enable DMA device on DUT.

        :param node: Topology node.
        :param dma_device_name: Name of DMA device.
        :param wq_count: The number of work queue required.
        :type node: dict
        :type dma_device_name: str
        :type wq_count: int
        """
        # configure engines of DMA device on DUT
        dma_num = dma_device_name.replace("dsa", "")
        for i in range(wq_count):
            cmd = f"accel-config config-engine " \
                    f"{dma_device_name}/engine{dma_num}.{i} --group-id={i}"
            exec_cmd_no_error(
                node, cmd, sudo=True,
                message=u"Failed to configure engine of DMA device on DUT.")

        # configure work queues of DMA device on DUT
        for i in range(wq_count):
            cmd = f"accel-config config-wq {dma_device_name}/wq{dma_num}.{i} " \
                f" --group-id={i} --type=user --priority=10 --wq-size=32 " \
                f" --max-batch-size=1024 --mode=dedicated -b 1 -a 0 " \
                f" --name=robot_test_dma"

            exec_cmd_no_error(
                node, cmd, sudo=True,
                message=u"Failed to configure work queue of DMA device on DUT.")

        # enable DMA device on DUT
        cmd = f"accel-config enable-device {dma_device_name}"
        exec_cmd_no_error(
            node, cmd, sudo=True,
            message=u"Failed to enable DMA device on DUT.")

        # enable work queues of DMA device on DUT
        enabled_wq_list = list()
        dma_num = dma_device_name.replace("dsa", "")
        for i in range(wq_count):
            enabled_wq_list.append(f"wq{dma_num}.{i}")
            cmd = f"accel-config enable-wq {dma_device_name}/wq{dma_num}.{i}"
            exec_cmd_no_error(
                node, cmd, sudo=True,
                message=u"Failed to enable work queue of DMA device on DUT.")

        return enabled_wq_list
