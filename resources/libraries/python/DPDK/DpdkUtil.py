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

"""Dpdk Utilities Library."""

from typing import Callable, Optional, Tuple, Union

from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.Constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.OptionString import OptionString
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error


class DpdkUtil:
    """Utilities for DPDK."""

    @staticmethod
    def get_eal_options(**kwargs: dict) -> OptionString:
        """Create EAL parameters options (including -v).

        :param kwargs: Dict of testpmd parameters.
        :type kwargs: dict
        :returns: EAL parameters.
        :rtype: OptionString
        """
        options = OptionString(prefix="-")
        options.add("v")
        # Set the hexadecimal bitmask of the cores to run on.
        options.add_with_value_from_dict("l", "eal_corelist", kwargs)
        # Add a PCI device in white list.
        options.add_with_value_from_dict("a", "eal_pci_whitelist0", kwargs)
        options.add_with_value_from_dict("a", "eal_pci_whitelist1", kwargs)
        # Load an external driver. Multiple -d options are allowed.
        options.add_with_value_if_from_dict(
            "d", "/usr/lib/librte_pmd_virtio.so", "eal_driver", kwargs, True
        )
        options.add_if_from_dict("-in-memory", "eal_in_memory", kwargs, False)
        return options

    @staticmethod
    def get_testpmd_pmd_options(**kwargs: dict) -> OptionString:
        """Create PMD parameters options for testpmd (without --).

        :param kwargs: List of testpmd parameters.
        :type kwargs: dict
        :returns: PMD parameters.
        :rtype: OptionString
        """
        options = OptionString(prefix="--")
        # Set the forwarding mode: io, mac, mac_retry, mac_swap, flowgen,
        # rxonly, txonly, csum, icmpecho, ieee1588
        options.add_equals_from_dict(
            "forward-mode", "pmd_fwd_mode", kwargs, "io"
        )
        # Set the number of packets per burst to N.
        options.add_equals("burst", 64)
        # Set the number of descriptors in the TX rings to N.
        options.add_equals_from_dict("txd", "pmd_txd", kwargs, 1024)
        # Set the number of descriptors in the RX rings to N.
        options.add_equals_from_dict("rxd", "pmd_rxd", kwargs, 1024)
        # Set the number of queues in the TX to N.
        options.add_equals_from_dict("txq", "pmd_txq", kwargs, 1)
        # Set the number of queues in the RX to N.
        options.add_equals_from_dict("rxq", "pmd_rxq", kwargs, 1)
        # Set the hexadecimal bitmask of offloads.
        options.add_equals_from_dict(
            "tx-offloads", "pmd_tx_offloads", kwargs, "0x0"
        )
        # Enables numa aware allocation of mbufs.
        options.add_if_from_dict("numa", "pmd_numa", kwargs, True)
        # Run by default.
        options.add_if_from_dict("auto-start", "pmd_auto_start", kwargs, True)
        # Set the number of mbufs to be allocated in the mbuf pools.
        options.add_equals_from_dict("total-num-mbufs", "pmd_num_mbufs", kwargs)
        # Set the number of forwarding ports.
        options.add_equals_from_dict("nb-ports", "pmd_nb_ports", kwargs)
        # Set the hexadecimal bitmask of the ports used by the packet
        # forwarding test.
        options.add_equals_from_dict("portmask", "pmd_portmask", kwargs)
        # Disable link status check.
        options.add_if_from_dict(
            "disable-link-check", "pmd_disable_link_check", kwargs
        )
        # Disable LSC interrupts for all ports.
        # Stops link state even notifications, but (unless disable-link-check)
        # allows full 9s wait period (for links to come up) on startup.
        options.add_if_from_dict(
            "no-lsc-interrupt", "pmd_no_lsc_interrupt", kwargs
        )
        # Set the MAC address XX:XX:XX:XX:XX:XX of the peer port N
        options.add_equals_from_dict("eth-peer", "pmd_eth_peer_0", kwargs)
        options.add_equals_from_dict("eth-peer", "pmd_eth_peer_1", kwargs)
        # Set the max packet length.
        options.add_equals_from_dict("max-pkt-len", "pmd_max_pkt_len", kwargs)
        # Set the mbuf size.
        options.add_equals_from_dict("mbuf-size", "pmd_mbuf_size", kwargs)
        # Set the number of forwarding cores based on coremask.
        options.add_equals_from_dict("nb-cores", "pmd_nb_cores", kwargs)
        return options

    @staticmethod
    def get_testpmd_args(**kwargs: dict) -> OptionString:
        """Get DPDK testpmd command line arguments.

        :param kwargs: Key-value testpmd parameters.
        :type kwargs: dict
        :returns: Command line string.
        :rtype: OptionString
        """
        options = OptionString()
        options.extend(DpdkUtil.get_eal_options(**kwargs))
        options.add("--")
        options.extend(DpdkUtil.get_testpmd_pmd_options(**kwargs))
        return options

    @staticmethod
    def get_testpmd_cmdline(**kwargs: dict) -> OptionString:
        """Get DPDK testpmd command line arguments with testpmd command.

        :param kwargs: Key-value testpmd parameters.
        :type kwargs: dict
        :returns: Command line string.
        :rtype: OptionString
        """
        options = OptionString()
        options.add("dpdk-testpmd")
        options.extend(DpdkUtil.get_eal_options(**kwargs))
        options.add("--")
        options.extend(DpdkUtil.get_testpmd_pmd_options(**kwargs))
        return options

    @staticmethod
    def dpdk_testpmd_start(node: dict, **kwargs: dict) -> None:
        """Start DPDK testpmd app on VM node.

        :param node: VM Node to start testpmd on.
        :param kwargs: Key-value testpmd parameters.
        :type node: dict
        :type kwargs: dict
        """
        cmd_options = OptionString()
        cmd_options.add("/start-testpmd.sh")
        cmd_options.extend(DpdkUtil.get_eal_options(**kwargs))
        cmd_options.add("--")
        cmd_options.extend(DpdkUtil.get_testpmd_pmd_options(**kwargs))
        exec_cmd_no_error(node, cmd_options, sudo=True, disconnect=True)

    @staticmethod
    def dpdk_testpmd_stop(node: dict) -> None:
        """Stop DPDK testpmd app on node.

        :param node: Node to stop testpmd on.
        :type node: dict
        :returns: nothing
        """
        cmd = "/stop-testpmd.sh"  # Completed string, simple one.
        exec_cmd_no_error(node, cmd, sudo=True, disconnect=True)

    @staticmethod
    def get_l3fwd_pmd_options(**kwargs: dict) -> OptionString:
        """Create PMD parameters options for l3fwd (without --).

        :param kwargs: List of l3fwd parameters.
        :type kwargs: dict
        :returns: PMD parameters.
        :rtype: OptionString
        """
        options = OptionString(prefix="--")
        # Set to use software to analyze packet type.
        options.add_if_from_dict("parse-ptype", "pmd_parse_ptype", kwargs, True)
        # Set the MAC address XX:XX:XX:XX:XX:XX of the peer port N.
        options.add_equals_from_dict("eth-dest", "pmd_eth_dest_0", kwargs)
        options.add_equals_from_dict("eth-dest", "pmd_eth_dest_1", kwargs)
        # Determines which queues from which ports are mapped to which cores.
        options.add_equals_from_dict("config", "pmd_config", kwargs)
        # Set the max packet length.
        options.add_with_value_if_from_dict(
            "max-pkt-len", "9200", "pmd_max_pkt_len", kwargs
        )
        return options

    @staticmethod
    def get_l3fwd_args(**kwargs: dict) -> OptionString:
        """Get DPDK l3fwd command line arguments.

        :param kwargs: Key-value l3fwd parameters.
        :type kwargs: dict
        :returns: Command line string.
        :rtype: OptionString
        """
        options = OptionString()
        options.extend(DpdkUtil.get_eal_options(**kwargs))
        options.add("--")
        options.extend(DpdkUtil.get_l3fwd_pmd_options(**kwargs))
        return options

    @staticmethod
    def kill_dpdk(node: dict) -> None:
        """Kill any dpdk app in the node.

        :param node: DUT node.
        :type node: dict
        :raises RuntimeError: If the script "kill_dpdk.sh" fails.
        """
        command = (
            f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}"
            f"/entry/kill_dpdk.sh"
        )
        message = f"Failed to kill dpdk at node {node['host']}"
        exec_cmd_no_error(node, command, message=message)

    @staticmethod
    def get_vals(
        nodes: dict,
        dut_name: str,
        topology_info: dict,
        phy_cores: str,
        rx_queues: Optional[int],
        rxd: Optional[int],
        txd: Optional[int],
    ) -> Tuple[dict, str, str, str, int, int]:
        """FIXME"""
        compute_resource_info = CpuUtils.get_affinity_vswitch(
            nodes=nodes,
            phy_cores=phy_cores,
            rx_queues=rx_queues,
            rxd=rxd,
            txd=txd,
        )
        cpu_dp = compute_resource_info[f"{dut_name}_cpu_dp"]
        rxq_count = compute_resource_info["rxq_count_int"]
        if1 = topology_info[f"{dut_name}_pf1"][0]
        if2 = topology_info[f"{dut_name}_pf2"][0]
        return nodes[dut_name], if1, if2, cpu_dp, int(phy_cores), rxq_count

    @staticmethod
    def start_dpdk_app_on_all_duts(
        start_function: Callable[[str], None],
        check_function: Callable[[dict], None],
        nodes: dict,
        phy_cores: Union[int, str],
    ) -> None:
        """
        Execute a dpdk app on all dut nodes.

        Also set test tags related to threads.
        Keep restarting few times if not all ports are up.

        This function hosts code common for both testpmd and l3fwd.
        The differences are only in arguments start_function and check_function.

        The check_function is simple, it takes node dict as input
        and return bool telling whether the app on the dut is ready.

        The starts (without any unnecessary wait) the app, returs None,
        and accepts the following arguments:
        dict node: The DUT node from nodes.
        str if1: Identifier (topology key) for the first interface to use.
        str if2: Identifier (topology key) for the second interface to use.
        str lcores_list: Comma-separated lcore numbers for app workers.
        int nb_cores: Total number of worker (dataplane) threads.
        str queue_nums: Number of RX (and also TX) queues for app to use.

        Those arguments are the only ones that (in principle can) depend
        of the DUT being processed. It is expected the real app starting
        keywords require more arguments, but those are static (not depending
        on DUT), so the caller should pass a closure that handles such details.

        The logic in this keyword does several tries, where each try:
        kills any running dpdk apps,
        starts new round of apps on all duts at the same time,
        checks if all apps are ready,
        retry if an app is not ready.

        :param start_function: To launch an app on a dut without waiting.
        :param check_function: To check app readiness, can wait if needed.
            Returns True if the app is ready, False otherwse.
        :param nodes: All the nodes info from the topology file.
        :param phy_cores: Number of physical cores to use.
        :type start_function: Callable[[dict, str, str, str, int, str], None]
        :type check_function: Callable[[dict], bool]
        :type nodes: dict
        :type phy_cores: int
        :raises RuntimeError: If bash return code is not 0.
        """
        phy_cores = int(phy_cores)
        if phy_cores > 1:
            BuiltIn().set_tags("MTHREAD")
        else:
            BuiltIn().set_tags("STHREAD")
        BuiltIn().set_tags(f"{phy_cores}T{phy_cores}C")
        dut_names_nodes = [(nam, nodes[nam]) for nam in nodes if "DUT" in nam]
        for _ in range(3):
            for _, dut_node in dut_names_nodes:
                DpdkUtil.kill_dpdk(dut_node)
            for dut_name, _ in dut_names_nodes:
                start_function(dut_name)
            not_ready = []
            for dut_name, dut_node in dut_names_nodes:
                if not check_function(node=dut_node):
                    not_ready.append(dut_name)
                    break
            for _, dut_nodes in dut_names_nodes:
                exec_cmd(dut_nodes, "cat screenlog.0")
            if not not_ready:
                return
            # Even if one app is ready, we need to restart both
            # to confirm link state on both DUTs again.
        raise RuntimeError(f"Dpdk app still not ready on {not_ready[0]}")
