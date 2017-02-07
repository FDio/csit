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

"""CPU utilities library"""

from resources.libraries.python.ssh import SSH

__all__ = ["CpuUtils"]

class CpuUtils(object):
    """CPU utilities"""

    @staticmethod
    def __str2int(string):
        """Conversion from string to integer, 0 in case of empty string.

        :param string: Input string.
        :type string: str
        :returns: Integer converted from string, 0 in case of ValueError.
        :rtype: int
        """
        try:
            return int(string)
        except ValueError:
            return 0

    @staticmethod
    def get_cpu_layout_from_all_nodes(nodes):
        """Retrieve cpu layout from all nodes, assuming all nodes
           are Linux nodes.

        :param nodes: DICT__nodes from Topology.DICT__nodes.
        :type nodes: dict
        :raises RuntimeError: If the ssh command "lscpu -p" fails.
        """
        ssh = SSH()
        for node in nodes.values():
            ssh.connect(node)
            cmd = "lscpu -p"
            ret, stdout, stderr = ssh.exec_command(cmd)
#           parsing of "lscpu -p" output:
#           # CPU,Core,Socket,Node,,L1d,L1i,L2,L3
#           0,0,0,0,,0,0,0,0
#           1,1,0,0,,1,1,1,0
            if ret != 0:
                raise RuntimeError(
                    "Failed to execute ssh command, ret: {} err: {}".format(
                        ret, stderr))
            node['cpuinfo'] = list()
            for line in stdout.split("\n"):
                if len(line) > 0 and line[0] != "#":
                    node['cpuinfo'].append([CpuUtils.__str2int(x) for x in
                                            line.split(",")])

    @staticmethod
    def cpu_node_count(node):
        """Return count of numa nodes.

        :param node: Targeted node.
        :type node: dict
        :returns: Count of numa nodes.
        :rtype: int
        :raises RuntimeError: If node cpuinfo is not available.
        """
        cpuinfo = node.get("cpuinfo")
        if cpuinfo is not None:
            return node["cpuinfo"][-1][3] + 1
        else:
            raise RuntimeError("Node cpuinfo not available.")

    @staticmethod
    def cpu_list_per_node(node, cpu_node):
        """Return node related list of CPU numbers.

        :param node: Node dictionary with cpuinfo.
        :param cpu_node: Numa node number.
        :type node: dict
        :type cpu_node: int
        :returns: List of cpu numbers related to numa from argument.
        :rtype: list of int
        :raises RuntimeError: If node cpuinfo is not available.
        """
        cpu_node = int(cpu_node)
        cpuinfo = node.get("cpuinfo")
        cpulist = []
        if cpuinfo is not None:
            for cpu in cpuinfo:
                if cpu[3] == cpu_node:
                    cpulist.append(cpu[0])
        else:
            raise RuntimeError("Node cpuinfo not available.")

        return cpulist

    @staticmethod
    def cpu_list_per_node_str(node, cpu_node, skip_cnt=0,
                              cpu_cnt=0, sep=","):
        """Return string of node related list of CPU numbers.

        :param node: Node dictionary with cpuinfo.
        :param cpu_node: Numa node number.
        :param skip_cnt: Skip first "skip_cnt" CPUs.
        :param cpu_cnt: Count of cpus to return, if 0 then return all.
        :param sep: Separator, default: 1,2,3,4,....
        :type node: dict
        :type cpu_node: int
        :type skip_cnt: int
        :type cpu_cnt: int
        :type sep: str
        :returns: Cpu numbers related to numa from argument.
        :rtype: str
        :raises RuntimeError: If we require more cpus than available.
        """

        cpu_list = CpuUtils.cpu_list_per_node(node, cpu_node)
        cpu_list_len = len(cpu_list)
        if cpu_cnt == 0:
            cpu_cnt = cpu_list_len - skip_cnt

        if cpu_cnt + skip_cnt > cpu_list_len:
            raise RuntimeError("cpu_cnt + skip_cnt > length(cpu list).")

        cpu_flist = sep.join(str(a) for a in
                             cpu_list[skip_cnt:skip_cnt+cpu_cnt])

        return cpu_flist

    @staticmethod
    def cpu_range_per_node_str(node, cpu_node, skip_cnt=0, cpu_cnt=0, sep="-"):
        """Return string of node related range of CPU numbers, e.g. 0-4.

        :param node: Node dictionary with cpuinfo.
        :param cpu_node: Numa node number.
        :param skip_cnt: Skip first "skip_cnt" CPUs.
        :param cpu_cnt: Count of cpus to return, if 0 then return all.
        :param sep: Separator, default: 0-4.
        :type node: dict
        :type cpu_node: int
        :type skip_cnt: int
        :type cpu_cnt: int
        :type sep: str
        :returns: String of node related range of CPU numbers.
        :rtype: str
        :raises RuntimeError: If we require more cpus than available.
        """

        cpu_list = CpuUtils.cpu_list_per_node(node, cpu_node)
        cpu_list_len = len(cpu_list)
        if cpu_cnt == 0:
            cpu_cnt = cpu_list_len - skip_cnt

        if cpu_cnt + skip_cnt > cpu_list_len:
            raise RuntimeError("cpu_cnt + skip_cnt > length(cpu list).")

        first = cpu_list[skip_cnt]
        last = cpu_list[skip_cnt + cpu_cnt - 1]
        return "{}{}{}".format(first, sep, last)
