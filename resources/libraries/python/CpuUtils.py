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

"""CPU utilities library."""

from random import choice

from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import Topology, NodeType

__all__ = [u"CpuUtils"]


class CpuUtils:
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
        cpu_mems_len = len(cpu_mems) // CpuUtils.NR_OF_THREADS
        count = 0
        for cpu_mem in cpu_mems[:cpu_mems_len]:
            if cpu_mem in cpu_mems[cpu_mems_len:]:
                count += 1
        return bool(count == cpu_mems_len)

    @staticmethod
    def get_cpu_info_from_all_nodes(nodes):
        """Assuming all nodes are Linux nodes, retrieve the following
           cpu information from all nodes:
               - cpu architecture
               - cpu layout

        :param nodes: DICT__nodes from Topology.DICT__nodes.
        :type nodes: dict
        :raises RuntimeError: If an ssh command retrieving cpu information
            fails.
        """
        for node in nodes.values():
            stdout, _ = exec_cmd_no_error(node, u"uname -m")
            node[u"arch"] = stdout.strip()
            stdout, _ = exec_cmd_no_error(node, u"lscpu -p")
            node[u"cpuinfo"] = list()
            for line in stdout.split(u"\n"):
                if line and line[0] != u"#":
                    node[u"cpuinfo"].append(
                        [CpuUtils.__str2int(x) for x in line.split(u",")]
                    )

    @staticmethod
    def cpu_node_count(node):
        """Return count of numa nodes.

        :param node: Targeted node.
        :type node: dict
        :returns: Count of numa nodes.
        :rtype: int
        :raises RuntimeError: If node cpuinfo is not available.
        """
        cpu_info = node.get(u"cpuinfo")
        if cpu_info is not None:
            return node[u"cpuinfo"][-1][3] + 1

        raise RuntimeError(u"Node cpuinfo not available.")

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
        cpu_info = node.get(u"cpuinfo")
        if cpu_info is None:
            raise RuntimeError(u"Node cpuinfo not available.")

        smt_enabled = CpuUtils.is_smt_enabled(cpu_info)
        if not smt_enabled and smt_used:
            raise RuntimeError(u"SMT is not enabled.")

        cpu_list = []
        for cpu in cpu_info:
            if cpu[3] == cpu_node:
                cpu_list.append(cpu[0])

        if not smt_enabled or smt_enabled and smt_used:
            pass

        if smt_enabled and not smt_used:
            cpu_list_len = len(cpu_list)
            cpu_list = cpu_list[:cpu_list_len // CpuUtils.NR_OF_THREADS]

        return cpu_list

    @staticmethod
    def cpu_slice_of_list_per_node(
            node, cpu_node, skip_cnt=0, cpu_cnt=0, smt_used=False):
        """Return node related subset of list of CPU numbers.

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
            raise RuntimeError(u"cpu_cnt + skip_cnt > length(cpu list).")

        if cpu_cnt == 0:
            cpu_cnt = cpu_list_len - skip_cnt

        if smt_used:
            cpu_list_0 = cpu_list[:cpu_list_len // CpuUtils.NR_OF_THREADS]
            cpu_list_1 = cpu_list[cpu_list_len // CpuUtils.NR_OF_THREADS:]
            cpu_list = cpu_list_0[skip_cnt:skip_cnt + cpu_cnt]
            cpu_list_ex = cpu_list_1[skip_cnt:skip_cnt + cpu_cnt]
            cpu_list.extend(cpu_list_ex)
        else:
            cpu_list = cpu_list[skip_cnt:skip_cnt + cpu_cnt]

        return cpu_list

    @staticmethod
    def cpu_list_per_node_str(
            node, cpu_node, skip_cnt=0, cpu_cnt=0, sep=u",", smt_used=False):
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
        cpu_list = CpuUtils.cpu_slice_of_list_per_node(
            node, cpu_node, skip_cnt=skip_cnt, cpu_cnt=cpu_cnt,
            smt_used=smt_used
        )
        return sep.join(str(cpu) for cpu in cpu_list)

    @staticmethod
    def cpu_range_per_node_str(
            node, cpu_node, skip_cnt=0, cpu_cnt=0, sep=u"-", smt_used=False):
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
        cpu_list = CpuUtils.cpu_slice_of_list_per_node(
            node, cpu_node, skip_cnt=skip_cnt, cpu_cnt=cpu_cnt,
            smt_used=smt_used
        )
        if smt_used:
            cpu_list_len = len(cpu_list)
            cpu_list_0 = cpu_list[:cpu_list_len // CpuUtils.NR_OF_THREADS]
            cpu_list_1 = cpu_list[cpu_list_len // CpuUtils.NR_OF_THREADS:]
            cpu_range = f"{cpu_list_0[0]}{sep}{cpu_list_0[-1]}," \
                        f"{cpu_list_1[0]}{sep}{cpu_list_1[-1]}"
        else:
            cpu_range = f"{cpu_list[0]}{sep}{cpu_list[-1]}"

        return cpu_range

    @staticmethod
    def cpu_slice_of_list_for_nf(
            node, cpu_node, nf_chains=1, nf_nodes=1, nf_chain=1, nf_node=1,
            nf_dtc=1, nf_mtcr=2, nf_dtcr=1, skip_cnt=0):
        """Return list of DUT node related list of CPU numbers. The main
        computing unit is physical core count.

        :param node: DUT node.
        :param cpu_node: Numa node number.
        :param nf_chains: Number of NF chains.
        :param nf_nodes: Number of NF nodes in chain.
        :param nf_chain: Chain number indexed from 1.
        :param nf_node: Node number indexed from 1.
        :param nf_dtc: Amount of physical cores for NF data plane.
        :param nf_mtcr: NF main thread per core ratio.
        :param nf_dtcr: NF data plane thread per core ratio.
        :param skip_cnt: Skip first "skip_cnt" CPUs.
        :type node: dict
        :param cpu_node: int.
        :type nf_chains: int
        :type nf_nodes: int
        :type nf_chain: int
        :type nf_node: int
        :type nf_dtc: int or float
        :type nf_mtcr: int
        :type nf_dtcr: int
        :type skip_cnt: int
        :returns: List of CPUs allocated to NF.
        :rtype: list
        :raises RuntimeError: If we require more cpus than available or if
            placement is not possible due to wrong parameters.
        """
        if not 1 <= nf_chain <= nf_chains:
            raise RuntimeError(u"ChainID is out of range!")
        if not 1 <= nf_node <= nf_nodes:
            raise RuntimeError(u"NodeID is out of range!")

        smt_used = CpuUtils.is_smt_enabled(node[u"cpuinfo"])
        cpu_list = CpuUtils.cpu_list_per_node(node, cpu_node, smt_used)
        # CPU thread sibling offset.
        sib = len(cpu_list) // CpuUtils.NR_OF_THREADS

        dtc_is_integer = isinstance(nf_dtc, int)
        if not smt_used and not dtc_is_integer:
            raise RuntimeError(u"Cannot allocate if SMT is not enabled!")
        if not dtc_is_integer:
            nf_dtc = 1

        mt_req = ((nf_chains * nf_nodes) + nf_mtcr - 1) // nf_mtcr
        dt_req = ((nf_chains * nf_nodes) + nf_dtcr - 1) // nf_dtcr

        if (skip_cnt + mt_req + dt_req) > (sib if smt_used else len(cpu_list)):
            raise RuntimeError(u"Not enough CPU cores available for placement!")

        offset = (nf_node - 1) + (nf_chain - 1) * nf_nodes
        mt_skip = skip_cnt + (offset % mt_req)
        dt_skip = skip_cnt + mt_req + (offset % dt_req) * nf_dtc

        result = cpu_list[dt_skip:dt_skip + nf_dtc]
        if smt_used:
            if (offset // mt_req) & 1:  # check oddness
                mt_skip += sib

            dt_skip += sib
            if dtc_is_integer:
                result.extend(cpu_list[dt_skip:dt_skip + nf_dtc])
            elif (offset // dt_req) & 1:  # check oddness
                result = cpu_list[dt_skip:dt_skip + nf_dtc]

        result[0:0] = cpu_list[mt_skip:mt_skip + 1]
        return result

    @staticmethod
    def get_affinity_af_xdp(
            node, pf_key, cpu_skip_cnt=0, cpu_cnt=1):
        """Get affinity for AF_XDP interface. Result will be used to pin IRQs.

        :param node: Topology node.
        :param pf_key: Topology interface.
        :param cpu_skip_cnt: Amount of CPU cores to skip.
        :param cpu_cnt: CPU threads count.
        :type node: dict
        :type pf_key: str
        :type cpu_skip_cnt: int
        :type cpu_cnt: int
        :returns: List of CPUs allocated to AF_XDP interface.
        :rtype: list
        """
        if pf_key:
            cpu_node = Topology.get_interface_numa_node(node, pf_key)
        else:
            cpu_node = 0

        smt_used = CpuUtils.is_smt_enabled(node[u"cpuinfo"])
        if smt_used:
            cpu_cnt = cpu_cnt // CpuUtils.NR_OF_THREADS

        return CpuUtils.cpu_slice_of_list_per_node(
            node, cpu_node, skip_cnt=cpu_skip_cnt, cpu_cnt=cpu_cnt,
            smt_used=smt_used
        )

    @staticmethod
    def get_affinity_nf(
            nodes, node, nf_chains=1, nf_nodes=1, nf_chain=1, nf_node=1,
            vs_dtc=1, nf_dtc=1, nf_mtcr=2, nf_dtcr=1):

        """Get affinity of NF (network function). Result will be used to compute
        the amount of CPUs and also affinity.

        :param nodes: Physical topology nodes.
        :param node: SUT node.
        :param nf_chains: Number of NF chains.
        :param nf_nodes: Number of NF nodes in chain.
        :param nf_chain: Chain number indexed from 1.
        :param nf_node: Node number indexed from 1.
        :param vs_dtc: Amount of physical cores for vswitch data plane.
        :param nf_dtc: Amount of physical cores for NF data plane.
        :param nf_mtcr: NF main thread per core ratio.
        :param nf_dtcr: NF data plane thread per core ratio.
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

        interface_list = list()
        interface_list.append(BuiltIn().get_variable_value(f"${{{node}_if1}}"))
        interface_list.append(BuiltIn().get_variable_value(f"${{{node}_if2}}"))

        cpu_node = Topology.get_interfaces_numa_node(
            nodes[node], *interface_list)

        return CpuUtils.cpu_slice_of_list_for_nf(
            node=nodes[node], cpu_node=cpu_node, nf_chains=nf_chains,
            nf_nodes=nf_nodes, nf_chain=nf_chain, nf_node=nf_node,
            nf_mtcr=nf_mtcr, nf_dtcr=nf_dtcr, nf_dtc=nf_dtc, skip_cnt=skip_cnt
        )

    @staticmethod
    def get_affinity_trex(
            node, if_key, tg_mtc=1, tg_dtc=1, tg_ltc=1, tg_dtc_offset=0):
        """Get affinity for T-Rex. Result will be used to pin T-Rex threads.

        :param node: TG node.
        :param if_key: TG first interface.
        :param tg_mtc: TG main thread count.
        :param tg_dtc: TG dataplane thread count.
        :param tg_ltc: TG latency thread count.
        :param tg_dtc_offset: TG dataplane thread offset.
        :type node: dict
        :type if_key: str
        :type tg_mtc: int
        :type tg_dtc: int
        :type tg_ltc: int
        :type tg_dtc_offset: int
        :returns: List of CPUs allocated to T-Rex including numa node.
        :rtype: int, int, int, list
        """
        interface_list = [if_key]
        cpu_node = Topology.get_interfaces_numa_node(node, *interface_list)

        master_thread_id = CpuUtils.cpu_slice_of_list_per_node(
            node, cpu_node, skip_cnt=0, cpu_cnt=tg_mtc,
            smt_used=False)

        threads = CpuUtils.cpu_slice_of_list_per_node(
            node, cpu_node, skip_cnt=tg_mtc + tg_ltc + tg_dtc_offset,
            cpu_cnt=tg_dtc, smt_used=False)

        latency_thread_id = CpuUtils.cpu_slice_of_list_per_node(
            node, cpu_node, skip_cnt=tg_mtc, cpu_cnt=tg_ltc, smt_used=False)

        return master_thread_id[0], latency_thread_id[0], cpu_node, threads

    @staticmethod
    def get_affinity_iperf(
            node, pf_key, cpu_skip_cnt=0, cpu_cnt=1):
        """Get affinity for iPerf3. Result will be used to pin iPerf3 threads.

        :param node: Topology node.
        :param pf_key: Topology interface.
        :param cpu_skip_cnt: Amount of CPU cores to skip.
        :param cpu_cnt: CPU threads count.
        :type node: dict
        :type pf_key: str
        :type cpu_skip_cnt: int
        :type cpu_cnt: int
        :returns: List of CPUs allocated to iPerf3.
        :rtype: str
        """
        if pf_key:
            cpu_node = Topology.get_interface_numa_node(node, pf_key)
        else:
            cpu_node = 0

        return CpuUtils.cpu_range_per_node_str(
            node, cpu_node, skip_cnt=cpu_skip_cnt, cpu_cnt=cpu_cnt,
            smt_used=False)

    @staticmethod
    def get_affinity_vhost(
            node, pf_key, skip_cnt=0, cpu_cnt=1):
        """Get affinity for vhost. Result will be used to pin vhost threads.

        :param node: Topology node.
        :param pf_key: Topology interface.
        :param skip_cnt: Amount of CPU cores to skip.
        :param cpu_cnt: CPU threads count.
        :type node: dict
        :type pf_key: str
        :type skip_cnt: int
        :type cpu_cnt: int
        :returns: List of CPUs allocated to vhost process.
        :rtype: str
        """
        if pf_key:
            cpu_node = Topology.get_interface_numa_node(node, pf_key)
        else:
            cpu_node = 0

        smt_used = CpuUtils.is_smt_enabled(node[u"cpuinfo"])
        if smt_used:
            cpu_cnt = cpu_cnt // CpuUtils.NR_OF_THREADS

        return CpuUtils.cpu_slice_of_list_per_node(
            node, cpu_node=cpu_node, skip_cnt=skip_cnt, cpu_cnt=cpu_cnt,
            smt_used=False)

    @staticmethod
    def get_cpu_idle_list(node, cpu_node, smt_used, cpu_alloc_str, sep=u","):
        """Get idle CPU List.

        :param node: Node dictionary with cpuinfo.
        :param cpu_node: Numa node number.
        :param smt_used: True - we want to use SMT, otherwise false.
        :param cpu_alloc_str: vpp used cores.
        :param sep: Separator, default: ",".
        :type node: dict
        :type cpu_node: int
        :type smt_used: bool
        :type cpu_alloc_str: str
        :type smt_used: bool
        :type sep: str
        :rtype: list
        """
        cpu_list = CpuUtils.cpu_list_per_node(node, cpu_node, smt_used)
        cpu_idle_list = [i for i in cpu_list
                         if str(i) not in cpu_alloc_str.split(sep)]
        return cpu_idle_list

    @staticmethod
    def get_affinity_vswitch(
            nodes, phy_cores, rx_queues=None, rxd=None, txd=None):
        """Get affinity for vswitch on all DUTs.

        :param nodes: Topology nodes.
        :param phy_cores: Number of physical cores to allocate.
        :param rx_queues: Number of RX queues. (Optional, Default: None)
        :param rxd: Number of RX descriptors. (Optional, Default: None)
        :param txd: Number of TX descriptors. (Optional, Default: None)
        :type nodes: dict
        :type phy_cores: int
        :type rx_queues: int
        :type rxd: int
        :type txd: int
        :returns: Compute resource information dictionary.
        :rtype: dict
        """
        compute_resource_info = dict()
        for node_name, node in nodes.items():
            if node["type"] != NodeType.DUT:
                continue
            # Number of Data Plane physical cores.
            dp_cores_count = BuiltIn().get_variable_value(
                "${dp_cores_count}", phy_cores
            )
            # Number of Feature Plane physical cores.
            fp_cores_count = BuiltIn().get_variable_value(
                "${fp_cores_count}", phy_cores - dp_cores_count
            )
            # Ratio between RX queues and data plane threads.
            rxq_ratio = BuiltIn().get_variable_value(
                "${rxq_ratio}", 1
            )

            dut_pf_keys = BuiltIn().get_variable_value(
                f"${{{node_name}_pf_keys}}"
            )
            # SMT override in case of non standard test cases.
            smt_used = BuiltIn().get_variable_value(
                "${smt_used}", CpuUtils.is_smt_enabled(node["cpuinfo"])
            )

            cpu_node = Topology.get_interfaces_numa_node(node, *dut_pf_keys)
            skip_cnt = Constants.CPU_CNT_SYSTEM
            cpu_main = CpuUtils.cpu_list_per_node_str(
                node, cpu_node,
                skip_cnt=skip_cnt,
                cpu_cnt=Constants.CPU_CNT_MAIN if phy_cores else 0,
                smt_used=False
            )
            cpu_main = cpu_main if phy_cores else choice(cpu_main.split(","))
            skip_cnt += Constants.CPU_CNT_MAIN
            cpu_dp = CpuUtils.cpu_list_per_node_str(
                node, cpu_node,
                skip_cnt=skip_cnt,
                cpu_cnt=int(dp_cores_count),
                smt_used=smt_used
            ) if int(dp_cores_count) else ""
            skip_cnt = skip_cnt + int(dp_cores_count)
            cpu_fp = CpuUtils.cpu_list_per_node_str(
                node, cpu_node,
                skip_cnt=skip_cnt,
                cpu_cnt=int(fp_cores_count),
                smt_used=smt_used
            ) if int(fp_cores_count) else ""

            fp_count_int = \
                int(fp_cores_count) * CpuUtils.NR_OF_THREADS if smt_used \
                else int(fp_cores_count)
            dp_count_int = \
                int(dp_cores_count) * CpuUtils.NR_OF_THREADS if smt_used \
                else int(dp_cores_count)

            rxq_count_int = \
                int(rx_queues) if rx_queues \
                else int(dp_count_int/rxq_ratio)
            rxq_count_int = 1 if not rxq_count_int else rxq_count_int

            compute_resource_info["buffers_numa"] = \
                215040 if smt_used else 107520
            compute_resource_info["smt_used"] = smt_used
            compute_resource_info[f"{node_name}_cpu_main"] = cpu_main
            compute_resource_info[f"{node_name}_cpu_dp"] = cpu_dp
            compute_resource_info[f"{node_name}_cpu_fp"] = cpu_fp
            compute_resource_info[f"{node_name}_cpu_wt"] = \
                ",".join(filter(None, [cpu_dp, cpu_fp]))
            compute_resource_info[f"{node_name}_cpu_alloc_str"] = \
                ",".join(filter(None, [cpu_main, cpu_dp, cpu_fp]))
            compute_resource_info["cpu_count_int"] = \
                int(dp_cores_count) + int(fp_cores_count)
            compute_resource_info["rxd_count_int"] = rxd
            compute_resource_info["txd_count_int"] = txd
            compute_resource_info["rxq_count_int"] = rxq_count_int
            compute_resource_info["fp_count_int"] = fp_count_int
            compute_resource_info["dp_count_int"] = dp_count_int

        return compute_resource_info
