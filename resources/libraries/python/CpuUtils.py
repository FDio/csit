# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""CPU utilities library."""

from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import Topology

__all__ = ["CpuUtils"]


class CpuUtils(object):
    """CPU utilities"""

    # Number of threads per core.
    NR_OF_THREADS = 2

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
    def is_smt_enabled(cpu_info):
        """Uses CPU mapping to find out if SMT is enabled or not. If SMT is
        enabled, the L1d,L1i,L2,L3 setting is the same for two processors. These
        two processors are two threads of one core.

        :param cpu_info: CPU info, the output of "lscpu -p".
        :type cpu_info: list
        :returns: True if SMT is enabled, False if SMT is disabled.
        :rtype: bool
        """
        cpu_mems = [item[-4:] for item in cpu_info]
        cpu_mems_len = len(cpu_mems) / CpuUtils.NR_OF_THREADS
        count = 0
        for cpu_mem in cpu_mems[:cpu_mems_len]:
            if cpu_mem in cpu_mems[cpu_mems_len:]:
                count += 1
        return bool(count == cpu_mems_len)

    @staticmethod
    def get_cpu_layout_from_all_nodes(nodes):
        """Retrieve cpu layout from all nodes, assuming all nodes
           are Linux nodes.

        :param nodes: DICT__nodes from Topology.DICT__nodes.
        :type nodes: dict
        :raises RuntimeError: If the ssh command "lscpu -p" fails.
        """
        for node in nodes.values():
            stdout, _ = exec_cmd_no_error(node, 'lscpu -p')
            node['cpuinfo'] = list()
            for line in stdout.split("\n"):
                if line and line[0] != "#":
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
        cpu_info = node.get("cpuinfo")
        if cpu_info is not None:
            return node["cpuinfo"][-1][3] + 1
        else:
            raise RuntimeError("Node cpuinfo not available.")

    @staticmethod
    def cpu_list_per_node(node, cpu_node, smt_used=False):
        """Return node related list of CPU numbers.

        :param node: Node dictionary with cpuinfo.
        :param cpu_node: Numa node number.
        :param smt_used: True - we want to use SMT, otherwise false.
        :type node: dict
        :type cpu_node: int
        :type smt_used: bool
        :returns: List of cpu numbers related to numa from argument.
        :rtype: list of int
        :raises RuntimeError: If node cpuinfo is not available
            or if SMT is not enabled.
        """
        cpu_node = int(cpu_node)
        cpu_info = node.get("cpuinfo")
        if cpu_info is None:
            raise RuntimeError("Node cpuinfo not available.")

        smt_enabled = CpuUtils.is_smt_enabled(cpu_info)
        if not smt_enabled and smt_used:
            raise RuntimeError("SMT is not enabled.")

        cpu_list = []
        for cpu in cpu_info:
            if cpu[3] == cpu_node:
                cpu_list.append(cpu[0])

        if not smt_enabled or smt_enabled and smt_used:
            pass

        if smt_enabled and not smt_used:
            cpu_list_len = len(cpu_list)
            cpu_list = cpu_list[:cpu_list_len / CpuUtils.NR_OF_THREADS]

        return cpu_list

    @staticmethod
    def cpu_slice_of_list_per_node(node, cpu_node, skip_cnt=0, cpu_cnt=0,
                                   smt_used=False):
        """Return string of node related list of CPU numbers.

        :param node: Node dictionary with cpuinfo.
        :param cpu_node: Numa node number.
        :param skip_cnt: Skip first "skip_cnt" CPUs.
        :param cpu_cnt: Count of cpus to return, if 0 then return all.
        :param smt_used: True - we want to use SMT, otherwise false.
        :type node: dict
        :type cpu_node: int
        :type skip_cnt: int
        :type cpu_cnt: int
        :type smt_used: bool
        :returns: Cpu numbers related to numa from argument.
        :rtype: list
        :raises RuntimeError: If we require more cpus than available.
        """
        cpu_list = CpuUtils.cpu_list_per_node(node, cpu_node, smt_used)

        cpu_list_len = len(cpu_list)
        if cpu_cnt + skip_cnt > cpu_list_len:
            raise RuntimeError("cpu_cnt + skip_cnt > length(cpu list).")

        if cpu_cnt == 0:
            cpu_cnt = cpu_list_len - skip_cnt

        if smt_used:
            cpu_list_0 = cpu_list[:cpu_list_len / CpuUtils.NR_OF_THREADS]
            cpu_list_1 = cpu_list[cpu_list_len / CpuUtils.NR_OF_THREADS:]
            cpu_list = [cpu for cpu in cpu_list_0[skip_cnt:skip_cnt + cpu_cnt]]
            cpu_list_ex = [cpu for cpu in
                           cpu_list_1[skip_cnt:skip_cnt + cpu_cnt]]
            cpu_list.extend(cpu_list_ex)
        else:
            cpu_list = [cpu for cpu in cpu_list[skip_cnt:skip_cnt + cpu_cnt]]

        return cpu_list

    @staticmethod
    def cpu_list_per_node_str(node, cpu_node, skip_cnt=0, cpu_cnt=0, sep=",",
                              smt_used=False):
        """Return string of node related list of CPU numbers.

        :param node: Node dictionary with cpuinfo.
        :param cpu_node: Numa node number.
        :param skip_cnt: Skip first "skip_cnt" CPUs.
        :param cpu_cnt: Count of cpus to return, if 0 then return all.
        :param sep: Separator, default: 1,2,3,4,....
        :param smt_used: True - we want to use SMT, otherwise false.
        :type node: dict
        :type cpu_node: int
        :type skip_cnt: int
        :type cpu_cnt: int
        :type sep: str
        :type smt_used: bool
        :returns: Cpu numbers related to numa from argument.
        :rtype: str
        """
        cpu_list = CpuUtils.cpu_slice_of_list_per_node(node, cpu_node,
                                                       skip_cnt=skip_cnt,
                                                       cpu_cnt=cpu_cnt,
                                                       smt_used=smt_used)
        return sep.join(str(cpu) for cpu in cpu_list)

    @staticmethod
    def cpu_range_per_node_str(node, cpu_node, skip_cnt=0, cpu_cnt=0, sep="-",
                               smt_used=False):
        """Return string of node related range of CPU numbers, e.g. 0-4.

        :param node: Node dictionary with cpuinfo.
        :param cpu_node: Numa node number.
        :param skip_cnt: Skip first "skip_cnt" CPUs.
        :param cpu_cnt: Count of cpus to return, if 0 then return all.
        :param sep: Separator, default: "-".
        :param smt_used: True - we want to use SMT, otherwise false.
        :type node: dict
        :type cpu_node: int
        :type skip_cnt: int
        :type cpu_cnt: int
        :type sep: str
        :type smt_used: bool
        :returns: String of node related range of CPU numbers.
        :rtype: str
        """
        cpu_list = CpuUtils.cpu_slice_of_list_per_node(node, cpu_node,
                                                       skip_cnt=skip_cnt,
                                                       cpu_cnt=cpu_cnt,
                                                       smt_used=smt_used)
        if smt_used:
            cpu_list_len = len(cpu_list)
            cpu_list_0 = cpu_list[:cpu_list_len / CpuUtils.NR_OF_THREADS]
            cpu_list_1 = cpu_list[cpu_list_len / CpuUtils.NR_OF_THREADS:]
            cpu_range = "{}{}{},{}{}{}".format(cpu_list_0[0], sep,
                                               cpu_list_0[-1],
                                               cpu_list_1[0], sep,
                                               cpu_list_1[-1])
        else:
            cpu_range = "{}{}{}".format(cpu_list[0], sep, cpu_list[-1])

        return cpu_range

    @staticmethod
    def cpu_slice_of_list_for_nf(node, cpu_node, nf_chains=1, nf_nodes=1,
                                 nf_chain=1, nf_node=1, nf_dtc=1, nf_mtcr=2,
                                 nf_dtcr=1, skip_cnt=0):
        """Return list of DUT node related list of CPU numbers. The main
        computing unit is physical core count.

        :param node: DUT node.
        :param cpu_node: Numa node number.
        :param nf_chains: Number of NF chains.
        :param nf_nodes: Number of NF nodes in chain.
        :param nf_chain: Chain number indexed from 1.
        :param nf_node: Node number indexed from 1.
        :param vs_dtc: Amount of physical cores for vswitch dataplane.
        :param nf_dtc: Amount of physical cores for NF dataplane.
        :param nf_mtcr: NF main thread per core ratio.
        :param nf_dtcr: NF dataplane thread per core ratio.
        :param skip_cnt: Skip first "skip_cnt" CPUs.
        :type node: dict
        :param cpu_node: int.
        :type nf_chains: int
        :type nf_nodes: int
        :type nf_chain: int
        :type nf_node: int
        :type vs_dtc: int
        :type nf_dtc: int or float
        :type nf_mtcr: int
        :type nf_dtcr: int
        :type skip_cnt: int
        :returns: List of CPUs allocated to NF.
        :rtype: list
        :raises RuntimeError: If we require more cpus than available or if
        placement is not possible due to wrong parameters.
        """
        if nf_chain - 1 >= nf_chains:
            raise RuntimeError("ChainID is higher than total number of chains!")
        if nf_node - 1 >= nf_nodes:
            raise RuntimeError("NodeID is higher than chain nodes!")

        smt_used = CpuUtils.is_smt_enabled(node['cpuinfo'])
        cpu_list = CpuUtils.cpu_list_per_node(node, cpu_node, smt_used)
        # CPU thread sibling offset.
        sib = len(cpu_list) / CpuUtils.NR_OF_THREADS

        if not smt_used and not isinstance(nf_dtc, int):
            raise RuntimeError("Cannot allocate if SMT is not enabled!")
        # TODO: Workaround as we are using physical core as main unit, we must
        # adjust number of physical dataplane cores in case of float for further
        # array referencing. As rounding method in Py2.7 and Py3.x differs, we
        # are using static mapping. This can be rewritten using flat arrays and
        # different logic (from Physical core unit to Logical core unit).
        dtc = 1 if not isinstance(nf_dtc, int) else nf_dtc

        mt_req = ((nf_chains * nf_nodes) + nf_mtcr - 1) / nf_mtcr
        dt_req = ((nf_chains * nf_nodes) + nf_dtcr - 1) / nf_dtcr
        cpu_req = skip_cnt + mt_req + dt_req

        if smt_used and cpu_req > len(cpu_list) / CpuUtils.NR_OF_THREADS:
            raise RuntimeError("Not enough CPU cores available for placement!")
        elif not smt_used and cpu_req > len(cpu_list):
            raise RuntimeError("Not enough CPU cores available for placement!")

        offset = (nf_node - 1) + (nf_chain - 1) * nf_nodes
        try:
            mt_odd = (offset / mt_req) & 1
            mt_skip = skip_cnt + (offset % mt_req)
            dt_odd = (offset / dt_req) & 1
            dt_skip = skip_cnt + mt_req + (offset % dt_req) * dtc
        except ZeroDivisionError:
            raise RuntimeError("Invalid placement combination!")
        if smt_used:
            mt_list = [cpu for cpu in cpu_list[mt_skip+sib:mt_skip+sib + 1]] \
                if mt_odd else [cpu for cpu in cpu_list[mt_skip:mt_skip + 1]]
            dt_list = [cpu for cpu in cpu_list[dt_skip+sib:dt_skip+sib + dtc]] \
                if dt_odd else [cpu for cpu in cpu_list[dt_skip:dt_skip + dtc]]
            if isinstance(nf_dtc, int):
                dt_list = \
                    [cpu for cpu in cpu_list[dt_skip:dt_skip + dtc]]
                dt_list += \
                    [cpu for cpu in cpu_list[dt_skip+sib:dt_skip+sib + dtc]]
        else:
            mt_list = [cpu for cpu in cpu_list[mt_skip:mt_skip + 1]]
            dt_list = [cpu for cpu in cpu_list[dt_skip:dt_skip + dtc]]

        return mt_list + dt_list

    @staticmethod
    def get_affinity_nf(nodes, node, nf_chains=1, nf_nodes=1, nf_chain=1,
                        nf_node=1, vs_dtc=1, nf_dtc=1, nf_mtcr=2, nf_dtcr=1):

        """Get affinity of NF (network function). Result will be used to compute
        the amount of CPUs and also affinity.

        :param nodes: Physical topology nodes.
        :param node: SUT node.
        :param nf_chains: Number of NF chains.
        :param nf_nodes: Number of NF nodes in chain.
        :param nf_chain: Chain number indexed from 1.
        :param nf_node: Node number indexed from 1.
        :param vs_dtc: Amount of physical cores for vswitch dataplane.
        :param nf_dtc: Amount of physical cores for NF dataplane.
        :param nf_mtcr: NF main thread per core ratio.
        :param nf_dtcr: NF dataplane thread per core ratio.
        :type nodes: dict
        :type node: dict
        :type nf_chains: int
        :type nf_nodes: int
        :type nf_chain: int
        :type nf_node: int
        :type vs_dtc: int
        :type nf_dtc: int or float
        :type nf_mtcr: int
        :type nf_dtcr: int
        :returns: List of CPUs allocated to NF.
        :rtype: list
        """
        skip_cnt = Constants.CPU_CNT_SYSTEM + Constants.CPU_CNT_MAIN + vs_dtc

        interface_list = []
        interface_list.append(
            BuiltIn().get_variable_value('${{{node}_if1}}'.format(node=node)))
        interface_list.append(
            BuiltIn().get_variable_value('${{{node}_if2}}'.format(node=node)))

        cpu_node = Topology.get_interfaces_numa_node(
            nodes[node], *interface_list)

        return CpuUtils.cpu_slice_of_list_for_nf(
            node=nodes[node], cpu_node=cpu_node, nf_chains=nf_chains,
            nf_nodes=nf_nodes, nf_chain=nf_chain, nf_node=nf_node,
            nf_mtcr=nf_mtcr, nf_dtcr=nf_dtcr, nf_dtc=nf_dtc, skip_cnt=skip_cnt)

