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

from robot.api import logger
from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error
from re import search

class DMAUtil:
    """Utilities for DMA's configuration tool accel-config."""

    @staticmethod
    def get_dma_device_info_on_dut(node, numa_node=None):
        """Get DMA device information on DUT.

        :param node: Topology node.
        :param numa_node: The interface numa_node ID
        :type node: dict
        :type numa_node: int
        :returns: DMA device information on DUT.
        :rtype: dict
        """
        cmd = u"grep -H . /sys/bus/dsa/devices/dsa*/numa_node"
        stdout, _ = exec_cmd_no_error(
            node, cmd, sudo=True,
            message=u"Failed to get DMA device numa_node information on DUT.",
            retries=3)

        numa_node_info = dict()
        for i in stdout.split():
            g = search(r"/(dsa\d+)/numa_node:(\d+)", i)
            if g:
                dma = g.group(1)
                dma_numa_node = int(g.group(2))
                numa_node_info[dma] = dma_numa_node

        cmd = u"ls /sys/bus/dsa/devices"
        stdout, _ = exec_cmd_no_error(
            node, cmd, sudo=True, message=u"Failed to get DMA device on DUT.",
            retries=3)

        dma_device_info = dict()
        for dev in stdout.split():
            g = search(r"^(engine|group|wq)(\d+)\.\d+", dev)
            if g is None:
                continue

            dev_type = g.group(1)
            dev_num = g.group(2)
            dma_device_name = f"dsa{dev_num}"
            if dma_device_name not in numa_node_info.keys():
                continue

            if (numa_node is not None and
                numa_node_info[dma_device_name] == numa_node) or \
                numa_node is None:
                dma_device_info.setdefault(dma_device_name, dict())
                dma_device_info[dma_device_name].setdefault(dev_type,
                    list())
                dma_device_info[dma_device_name][dev_type].append(dev)
                dma_device_info[dma_device_name]["numa_node"] = \
                    numa_node_info[dma_device_name]

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
        # disable work queues of DMA device on DUT
        cmd = f"grep -H . /sys/bus/dsa/devices/{dma_device_name}/wq*/state"
        stdout, _ = exec_cmd_no_error(
            node, cmd, sudo=True,
            message=u"Failed to get DMA device wq state information on DUT.",
            retries=3)

        enabled_list = list()
        for i in stdout.split():
            g = search(r"/(wq.*)/state:(.*)", i)
            if g:
                wq = g.group(1)
                wq_state = g.group(2)
                if wq_state == "enabled":
                    enabled_list.append(f"{dma_device_name}/{wq}")

        if enabled_list:
            cmd = f"accel-config disable-wq {' '.join(enabled_list)}"
            exec_cmd_no_error(
                node, cmd, sudo=True,
                message=u"Failed to disable work queues of DMA device \
                    on DUT.")

        # disable DMA device on DUT
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
        dma_device_info = DMAUtil.get_dma_device_info_on_dut(node)
        wq_list = list()

        # configure engine of DMA device on DUT
        cmd_list = list()
        for i in range(wq_count):
            engine_index = i % len(dma_device_info[dma_device_name]["engine"])
            engine_name = \
                dma_device_info[dma_device_name]["engine"][engine_index]
            cmd = f"accel-config config-engine " \
                    f"{dma_device_name}/{engine_name} --group-id={i}"
            cmd_list.append(cmd)
        exec_cmd_no_error(
            node, ";".join(cmd_list), sudo=True,
            message=u"Failed to configure engine of DMA device on DUT.")

        # configure work queue of DMA device on DUT
        cmd_list = list()
        for i in range(wq_count):
            wq_index = i % len(dma_device_info[dma_device_name]["wq"])
            wq_name = dma_device_info[dma_device_name]["wq"][wq_index]
            wq_list.append(wq_name)
            cmd = f"accel-config config-wq {dma_device_name}/{wq_name} " \
                f" --group-id={i} --type=user --priority=10 --wq-size=32 " \
                f" --max-batch-size=1024 --mode=dedicated -b 1 " \
                f" --name=robot_test_dma"
            cmd_list.append(cmd)
        exec_cmd_no_error(
            node, ";".join(cmd_list), sudo=True,
            message=u"Failed to configure work queue of DMA device on DUT.")

        # enable DMA device on DUT
        cmd = f"accel-config enable-device {dma_device_name}"
        exec_cmd_no_error(
            node, cmd, sudo=True,
            message=u"Failed to enable DMA device on DUT.")

        wq_list = sorted(list(set(wq_list)))
        # enable work queues of DMA device on DUT
        enable_wq_list = list()
        for wq in wq_list:
            enable_wq_list.append(f"{dma_device_name}/{wq}")
        cmd = f"accel-config enable-wq {' '.join(enable_wq_list)}"
        exec_cmd_no_error(
            node, cmd, sudo=True,
            message=u"Failed to enable work queue of DMA device on DUT.")

        return wq_list

    @staticmethod
    def show_lspci(node):
        cmd = u"ls -lh /sys/bus/dsa/devices/dsa*"
        stdout, _ = exec_cmd_no_error(
            node, cmd, sudo=True, message=u"Failed to get DMA device on DUT.",
            retries=3)

        pci_info = dict()
        for dev in stdout.split("\n"):
            g = search(r"/devices/(dsa\d+).*pci.*?/(.*)/dsa", dev)
            if g is None:
                continue
            pci_info[g.group(1)] = g.group(2)

        for k, v in pci_info.items():
            cmd = f"lspci -vvv -s {v}"
            stdout, _ = exec_cmd_no_error(
                node, cmd, sudo=True,
                message=u"Failed to get lspci on DUT.",
                retries=3)
            logger.debug(stdout)

        # file_name = f"intel_dsa_sample.c"
        cmd = f"cd {Constants.REMOTE_FW_DIR}; \
            make intel_dsa_sample LDLIBS=-laccel-config; \
            sudo ./intel_dsa_sample; echo over"
        stdout, _ = exec_cmd_no_error(
                node, cmd, sudo=True,
                message=u"Failed to run intel_dsa_sample on DUT.",
                retries=3)
        logger.debug(stdout)
