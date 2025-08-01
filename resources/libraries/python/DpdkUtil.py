# Copyright (c) 2025 Cisco and/or its affiliates.
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

from resources.libraries.python.Constants import Constants
from resources.libraries.python.OptionString import OptionString
from resources.libraries.python.ssh import exec_cmd_no_error


class DpdkUtil:
    """Utilities for DPDK."""

    @staticmethod
    def get_eal_options(**kwargs):
        """Create EAL parameters options (including -v).

        :param kwargs: Dict of testpmd parameters.
        :type kwargs: dict
        :returns: EAL parameters.
        :rtype: OptionString
        """
        options = OptionString(prefix="-")
        options.add("v")
        # Set the hexadecimal bitmask of the cores to run on.
        options.add_with_value_from_dict(
            "-lcores", "eal_coremap", kwargs
        )
        # Add a PCI device in white list.
        options.add_with_value_from_dict(
            "a", "eal_pci_whitelist0", kwargs
        )
        options.add_with_value_from_dict(
            "a", "eal_pci_whitelist1", kwargs
        )
        # Load an external driver. Multiple -d options are allowed.
        options.add_with_value_if_from_dict(
            "d", "/usr/lib/librte_pmd_virtio.so", "eal_driver", kwargs, True
        )
        options.add_if_from_dict(
            "-in-memory", "eal_in_memory", kwargs, False
        )
        return options

    @staticmethod
    def get_testpmd_pmd_options(**kwargs):
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
        options.add_equals(
            "burst", 64
        )
        # Set the number of descriptors in the TX rings to N.
        options.add_equals_from_dict(
            "txd", "pmd_txd", kwargs, 1024
        )
        # Set the number of descriptors in the RX rings to N.
        options.add_equals_from_dict(
            "rxd", "pmd_rxd", kwargs, 1024
        )
        # Set the number of queues in the TX to N.
        options.add_equals_from_dict(
            "txq", "pmd_txq", kwargs, 1
        )
        # Set the number of queues in the RX to N.
        options.add_equals_from_dict(
            "rxq", "pmd_rxq", kwargs, 1
        )
        # Set the hexadecimal bitmask of offloads.
        options.add_equals_from_dict(
            "tx-offloads", "pmd_tx_offloads", kwargs, "0x0"
        )
        # Enables numa aware allocation of mbufs.
        options.add_if_from_dict(
            "numa", "pmd_numa", kwargs, True
        )
        # Run by default.
        options.add_if_from_dict(
            "auto-start", "pmd_auto_start", kwargs, True
        )
        # Set the number of mbufs to be allocated in the mbuf pools.
        options.add_equals_from_dict(
            "total-num-mbufs", "pmd_num_mbufs", kwargs
        )
        # Set the number of forwarding ports.
        options.add_equals_from_dict(
            "nb-ports", "pmd_nb_ports", kwargs
        )
        # Set the hexadecimal bitmask of the ports used by the packet
        # forwarding test.
        options.add_equals_from_dict(
            "portmask", "pmd_portmask", kwargs
        )
        # Disable link status check.
        options.add_if_from_dict(
            "disable-link-check", "pmd_disable_link_check", kwargs, True
        )
        # Set the MAC address XX:XX:XX:XX:XX:XX of the peer port N
        options.add_equals_from_dict(
            "eth-peer", "pmd_eth_peer_0", kwargs
        )
        options.add_equals_from_dict(
            "eth-peer", "pmd_eth_peer_1", kwargs
        )
        # Set the max packet length.
        options.add_equals_from_dict(
            "max-pkt-len", "pmd_max_pkt_len", kwargs
        )
        # Set the mbuf size.
        options.add_equals_from_dict(
            "mbuf-size", "pmd_mbuf_size", kwargs
        )
        # Set the number of forwarding cores based on coremask.
        options.add_equals_from_dict(
            "nb-cores", "pmd_nb_cores", kwargs
        )
        return options

    @staticmethod
    def get_testpmd_args(**kwargs):
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
    def get_testpmd_cmdline(**kwargs):
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
    def dpdk_testpmd_start(node, **kwargs):
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
    def dpdk_testpmd_stop(node):
        """Stop DPDK testpmd app on node.

        :param node: Node to stop testpmd on.
        :type node: dict
        :returns: nothing
        """
        cmd = "/stop-testpmd.sh"  # Completed string, simple one.
        exec_cmd_no_error(node, cmd, sudo=True, disconnect=True)

    @staticmethod
    def get_l3fwd_pmd_options(**kwargs):
        """Create PMD parameters options for l3fwd (without --).

        :param kwargs: List of l3fwd parameters.
        :type kwargs: dict
        :returns: PMD parameters.
        :rtype: OptionString
        """
        options = OptionString(prefix="--")
        # Set to use software to analyze packet type.
        options.add_if_from_dict(
            "parse-ptype", "pmd_parse_ptype", kwargs, True
        )
        # Set the MAC address XX:XX:XX:XX:XX:XX of the peer port N.
        options.add_equals_from_dict(
            "eth-dest", "pmd_eth_dest_0", kwargs
        )
        options.add_equals_from_dict(
            "eth-dest", "pmd_eth_dest_1", kwargs
        )
        # Determines which queues from which ports are mapped to which cores.
        options.add_equals_from_dict(
            "config", "pmd_config", kwargs
        )
        # Set the max packet length.
        options.add_with_value_if_from_dict(
            "max-pkt-len", Constants.MTU_JUMBO, "pmd_max_pkt_len", kwargs, False
        )
        return options

    @staticmethod
    def get_l3fwd_args(**kwargs):
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
