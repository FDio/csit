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

"""CPU utilities library."""

from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import Topology

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
    def worker_count_from_cores_and_smt(phy_cores, smt_used):
        """Simple conversion utility, needs smt from caller.

        The implementation assumes we pack 1 or 2 workers per core,
        depending on hyperthreading.

        Some keywords use None to indicate no core/worker limit,
        so this converts None to None.

        :param phy_cores: How many physical cores to use for workers.
        :param smt_used: Whether symmetric multithreading is used.
        :type phy_cores: Optional[int]
        :type smt_used: bool
        :returns: How many VPP workers fit into the given number of cores.
        :rtype: Optional[int]
        """
        if phy_cores is None:
            return None
        workers_per_core = CpuUtils.NR_OF_THREADS if smt_used else 1
        workers = phy_cores * workers_per_core
        return workers

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
            node, if1_pci, if2_pci, tg_mtc=1, tg_dtc=1, tg_ltc=1):
        """Get affinity for T-Rex. Result will be used to pin T-Rex threads.

        :param node: TG node.
        :param if1_pci: TG first interface.
        :param if2_pci: TG second interface.
        :param tg_mtc: TG main thread count.
        :param tg_dtc: TG dataplane thread count.
        :param tg_ltc: TG latency thread count.
        :type node: dict
        :type if1_pci: str
        :type if2_pci: str
        :type tg_mtc: int
        :type tg_dtc: int
        :type tg_ltc: int
        :returns: List of CPUs allocated to T-Rex including numa node.
        :rtype: int, int, int, list
        """
        interface_list = [if1_pci, if2_pci]
        cpu_node = Topology.get_interfaces_numa_node(node, *interface_list)

        master_thread_id = CpuUtils.cpu_slice_of_list_per_node(
            node, cpu_node, skip_cnt=0, cpu_cnt=tg_mtc,
            smt_used=False)

        threads = CpuUtils.cpu_slice_of_list_per_node(
            node, cpu_node, skip_cnt=tg_mtc, cpu_cnt=tg_dtc,
            smt_used=False)

        latency_thread_id = CpuUtils.cpu_slice_of_list_per_node(
            node, cpu_node, skip_cnt=tg_mtc + tg_dtc, cpu_cnt=tg_ltc,
            smt_used=False)

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
