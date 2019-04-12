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

"""Dpdk Utilities Library."""

from resources.libraries.python.OptionString import OptionString
from resources.libraries.python.ssh import SSH, exec_cmd_no_error


class DpdkUtil(object):
    """Utilities for DPDK."""

    @staticmethod
    def get_eal_options(**kwargs):
        """Create EAL parameters options (including -v).

        :param kwargs: Dict of testpmd parameters.
        :type kwargs: dict
        :returns: EAL parameters.
        :rtype: OptionString
        """
        options = OptionString()
        option.add_one('-v')
        # Set the hexadecimal bitmask of the cores to run on.
        options.add_two_or_zero_from_dict('-l', 'eal_corelist', kwargs)
        # Set master core.
        options.add_two_or_zero('--master-lcore', '0')
        # Load an external driver. Multiple -d options are allowed.
        options.add_two_or_zero_if_from_dict(
            '-d', '/usr/lib/librte_pmd_virtio.so', 'eal_driver', kwargs, True)
        options.add_one_if_from_dict(
            '--in-memory', 'eal_in_memory', kwargs, False)
        return options

    @staticmethod
    def get_pmd_options(**kwargs):
        """Create PMD parameters options (without --).

        :param kwargs: List of testpmd parameters.
        :type kwargs: dict
        :returns: PMD parameters.
        :rtype: OptionString
        """
        options = OptionString()
        # Set the forwarding mode: io, mac, mac_retry, mac_swap, flowgen,
        # rxonly, txonly, csum, icmpecho, ieee1588
        options.add_equals_from_dict(
            '--forward-mode', 'pmd_fwd_mode', kwargs, 'io')
        # Set the number of packets per burst to N.
        options.add_equals('--burst', 64)
        # Set the number of descriptors in the TX rings to N.
        options.add_equals_from_dict('--txd', 'pmd_txd', kwargs, 1024)
        # Set the number of descriptors in the RX rings to N.
        options.add_equals_from_dict('--rxd', 'pmd_rxd', kwargs, 1024)
        # Set the number of queues in the TX to N.
        options.add_equals_from_dict('--txq', 'pmd_txq', kwargs, 1)
        # Set the number of queues in the RX to N.
        options.add_equals_from_dict('--rxq', 'pmd_rxq', kwargs, 1)
        # Set the hexadecimal bitmask of TX queue flags.
        options.add_equals_if(
            '--txqflags', '0xf00', kwargs.get('pmd_tx_offloads', True))
        # Set the number of mbufs to be allocated in the mbuf pools.
        options.add_equals_from_dict(
            '--total-num-mbufs', 'pmd_num_mbufs', kwargs)
        # Disable hardware VLAN.
        options.add_one_if(
            '--disable-hw-vlan', kwargs.get('pmd_disable_hw_vlan', True))
        # Set the MAC address XX:XX:XX:XX:XX:XX of the peer port N
        options.add_equals_from_dict(
            '--eth-peer', 'pmd_eth-peer_0', kwargs)
        options.add_equals_from_dict(
            '--eth-peer', 'pmd_eth-peer_1', kwargs)
        # Set the max packet length.
        options.add_equals_from_dict(
            '--max-pkt-len', 'pmd_max_pkt_len', kwargs)
        # Set the number of forwarding cores based on coremask.
        options.add_equals_from_dict(
            '--nb-cores', 'pmd_nb_cores', kwargs)
        return options

    @staticmethod
    def get_testpmd_cmdline(**kwargs):
        """Get DPDK testpmd command line arguments.

        :param args: Key-value testpmd parameters.
        :type args: dict
        :returns: Command line string.
        :rtype: OptionString
        """
        options = OptionString()
        options.add_one('testpmd')
        options.extend(DpdkUtil.get_eal_options(**kwargs))
        options.add_one('--')
        options.extend(DpdkUtil.get_pmd_options(**kwargs))
        return options

    @staticmethod
    def dpdk_testpmd_start(node, **kwargs):
        """Start DPDK testpmd app on VM node.

        :param node: VM Node to start testpmd on.
        :param args: Key-value testpmd parameters.
        :type node: dict
        :type kwargs: dict
        """
        cmd_options = OptionString()
        cmd_options.add_one("/start-testpmd.sh")
        cmd_options.extend(DpdkUtil.get_eal_options(**kwargs))
        cmd_options.add_one('--')
        cmd_options.extend(DpdkUtil.get_pmd_options(**kwargs))
        exec_cmd_no_error(node, cmd_options, sudo=True, disconnect=True)

    @staticmethod
    def dpdk_testpmd_stop(node):
        """Stop DPDK testpmd app on node.

        :param node: Node to stop testpmd on.
        :type node: dict
        :returns: nothing
        """
        cmd = "/stop-testpmd.sh"
        exec_cmd_no_error(node, cmd, sudo=True, disconnect=True)
