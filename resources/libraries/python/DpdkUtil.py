# Copyright (c) 2018 Cisco and/or its affiliates.
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

from resources.libraries.python.ssh import SSH, exec_cmd_no_error


class DpdkUtil(object):
    """Utilities for DPDK."""

    @staticmethod
    def get_eal_options(**args):
        """Create EAL parameters string.

        :param args: List of testpmd parameters.
        :type args: dict
        :returns: EAL parameters string.
        :rtype: str
        """
        # Set the hexadecimal bitmask of the cores to run on.
        eal_corelist = '-l {} '.format(args['eal_corelist'])\
            if args.get('eal_corelist', '') else ''
        # Set master core.
        eal_master_core = '--master-lcore 0 '
        # Set the number of memory channels to use.
        eal_mem_channels = '-n {} '.format(args['eal_mem_channels'])\
            if args.get('eal_mem_channels', '') else ''
        # Set the memory to allocate on specific sockets (comma separated).
        eal_socket_mem = '--socket-mem {} '.format(args['eal_socket_mem'])\
            if args.get('eal_socket_mem', '') else ''
        # Load an external driver. Multiple -d options are allowed.
        eal_driver = '-d /usr/lib/librte_pmd_virtio.so '\
            if args.get('eal_driver', True) else ''
        # Run in memory.
        eal_in_memory = '--in-memory '\
            if args.get('eal_in_memory', False) else ''
        eal_options = '-v '\
            + eal_corelist\
            + eal_master_core\
            + eal_mem_channels\
            + eal_socket_mem\
            + eal_driver\
            + eal_in_memory
        return eal_options

    @staticmethod
    def get_pmd_options(**args):
        """Create PMD parameters string.

        :param args: List of testpmd parameters.
        :type args: dict
        :returns: PMD parameters string.
        :rtype: str
        """
        # Set the forwarding mode: io, mac, mac_retry, mac_swap, flowgen,
        # rxonly, txonly, csum, icmpecho, ieee1588
        pmd_fwd_mode = '--forward-mode={} '.format(args['pmd_fwd_mode'])\
            if args.get('pmd_fwd_mode', '') else ''
        # Set the number of packets per burst to N.
        pmd_burst = '--burst=64 '
        # Set the number of descriptors in the TX rings to N.
        pmd_txd = '--txd={} '.format(args.get('pmd_txd', '1024')) \
            if args.get('pmd_txd', '1024') else ''
        # Set the number of descriptors in the RX rings to N.
        pmd_rxd = '--rxd={} '.format(args.get('pmd_rxd', '1024')) \
            if args.get('pmd_rxd', '1024') else ''
        # Set the number of queues in the TX to N.
        pmd_txq = '--txq={} '.format(args.get('pmd_txq', '1')) \
            if args.get('pmd_txq', '1') else ''
        # Set the number of queues in the RX to N.
        pmd_rxq = '--rxq={} '.format(args.get('pmd_rxq', '1')) \
            if args.get('pmd_rxq', '1') else ''
        # Set the hexadecimal bitmask of TX offloads.
        pmd_tx_offloads = '--txqflags=0xf00 '\
            if args.get('pmd_tx_offloads', True) else ''
        # Set the number of mbufs to be allocated in the mbuf pools.
        pmd_total_num_mbufs = '--total-num-mbufs={} '.format(
            args['pmd_num_mbufs']) if args.get('pmd_num_mbufs', '') else ''
        # Set the max packet length.
        pmd_max_pkt_len = "--max-pkt-len={0}".format(args["pmd_max_pkt_len"]) \
            if args.get("pmd_max_pkt_len", "") else ""
        # Disable hardware VLAN.
        pmd_disable_hw_vlan = '--disable-hw-vlan '\
            if args.get('pmd_disable_hw_vlan', True) else ''
        # Set the MAC address XX:XX:XX:XX:XX:XX of the peer port N
        pmd_eth_peer_0 = '--eth-peer={} '.format(args['pmd_eth_peer_0'])\
            if args.get('pmd_eth_peer_0', '') else ''
        pmd_eth_peer_1 = '--eth-peer={} '.format(args['pmd_eth_peer_1'])\
            if args.get('pmd_eth_peer_1', '') else ''
        pmd_options = '-- '\
            + pmd_fwd_mode\
            + pmd_burst\
            + pmd_txd\
            + pmd_rxd\
            + pmd_txq\
            + pmd_rxq\
            + pmd_tx_offloads\
            + pmd_total_num_mbufs\
            + pmd_disable_hw_vlan\
            + pmd_eth_peer_0\
            + pmd_eth_peer_1\
            + pmd_max_pkt_len
        return pmd_options

    @staticmethod
    def get_testpmd_cmdline(**kwargs):
        """Get DPDK testpmd command line arguments.

        :param args: Key-value testpmd parameters.
        :type args: dict
        :returns: Command line string.
        :rtype: str
        """
        eal_options = DpdkUtil.get_eal_options(**kwargs)
        pmd_options = DpdkUtil.get_pmd_options(**kwargs)

        return 'testpmd {0} {1}'.format(eal_options, pmd_options)

    @staticmethod
    def dpdk_testpmd_start(node, **kwargs):
        """Start DPDK testpmd app on VM node.

        :param node: VM Node to start testpmd on.
        :param args: Key-value testpmd parameters.
        :type node: dict
        :type args: dict
        :returns: nothing
        """
        eal_options = DpdkUtil.get_eal_options(**kwargs)
        pmd_options = DpdkUtil.get_pmd_options(**kwargs)

        ssh = SSH()
        ssh.connect(node)
        cmd = "/start-testpmd.sh {0} {1}".format(eal_options, pmd_options)
        exec_cmd_no_error(node, cmd, sudo=True)
        ssh.disconnect(node)

    @staticmethod
    def dpdk_testpmd_stop(node):
        """Stop DPDK testpmd app on node.

        :param node: Node to stop testpmd on.
        :type node: dict
        :returns: nothing
        """
        ssh = SSH()
        ssh.connect(node)
        cmd = "/stop-testpmd.sh"
        exec_cmd_no_error(node, cmd, sudo=True)
        ssh.disconnect(node)
