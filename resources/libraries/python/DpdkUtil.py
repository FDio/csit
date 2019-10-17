# Copyright (c) 2020 Cisco and/or its affiliates.
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
from resources.libraries.python.ssh import exec_cmd_no_error, disconnect_node


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
        options = OptionString(prefix=u"-")
        options.add(u"v")
        # Set the hexadecimal bitmask of the cores to run on.
        options.add_with_value_from_dict(u"l", u"eal_corelist", kwargs)
        # Set master core.
        options.add_with_value(u"-master-lcore", u"0")
        # Load an external driver. Multiple -d options are allowed.
        options.add_with_value_if_from_dict(
            u"d", u"/usr/lib/librte_pmd_virtio.so", u"eal_driver", kwargs, True
        )
        options.add_if_from_dict(
            u"-in-memory", u"eal_in_memory", kwargs, False
        )
        return options

    @staticmethod
    def get_pmd_options(**kwargs):
        """Create PMD parameters options (without --).

        :param kwargs: List of testpmd parameters.
        :type kwargs: dict
        :returns: PMD parameters.
        :rtype: OptionString
        """
        options = OptionString(prefix=u"--")
        # Set the forwarding mode: io, mac, mac_retry, mac_swap, flowgen,
        # rxonly, txonly, csum, icmpecho, ieee1588
        options.add_equals_from_dict(
            u"forward-mode", u"pmd_fwd_mode", kwargs, u"io"
        )
        # Set the number of packets per burst to N.
        options.add_equals(u"burst", 64)
        # Set the number of descriptors in the TX rings to N.
        options.add_equals_from_dict(u"txd", u"pmd_txd", kwargs, 1024)
        # Set the number of descriptors in the RX rings to N.
        options.add_equals_from_dict(u"rxd", u"pmd_rxd", kwargs, 1024)
        # Set the number of queues in the TX to N.
        options.add_equals_from_dict(u"txq", u"pmd_txq", kwargs, 1)
        # Set the number of queues in the RX to N.
        options.add_equals_from_dict(u"rxq", u"pmd_rxq", kwargs, 1)
        # Set the hexadecimal bitmask of offloads.
        options.add_equals_from_dict(u"tx-offloads", u"pmd_tx_offloads", kwargs)
        # Set the number of mbufs to be allocated in the mbuf pools.
        options.add_equals_from_dict(
            u"total-num-mbufs", u"pmd_num_mbufs", kwargs
        )
        # Disable hardware VLAN.
        options.add_if_from_dict(
            u"disable-hw-vlan", u"pmd_disable_hw_vlan", kwargs, True
        )
        # Set the MAC address XX:XX:XX:XX:XX:XX of the peer port N
        options.add_equals_from_dict(u"eth-peer", u"pmd_eth_peer_0", kwargs)
        options.add_equals_from_dict(u"eth-peer", u"pmd_eth_peer_1", kwargs)
        # Set the max packet length.
        options.add_equals_from_dict(u"max-pkt-len", u"pmd_max_pkt_len", kwargs)
        # Set the number of forwarding cores based on coremask.
        options.add_equals_from_dict(u"nb-cores", u"pmd_nb_cores", kwargs)
        return options

    @staticmethod
    def get_testpmd_cmdline(**kwargs):
        """Get DPDK testpmd command line arguments.

        :param kwargs: Key-value testpmd parameters.
        :type kwargs: dict
        :returns: Command line string.
        :rtype: OptionString
        """
        options = OptionString()
        options.add(u"testpmd")
        options.extend(DpdkUtil.get_eal_options(**kwargs))
        options.add(u"--")
        options.extend(DpdkUtil.get_pmd_options(**kwargs))
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
        cmd_options.add(u"/start-testpmd.sh")
        cmd_options.extend(DpdkUtil.get_eal_options(**kwargs))
        cmd_options.add(u"--")
        cmd_options.extend(DpdkUtil.get_pmd_options(**kwargs))
        exec_cmd_no_error(node, cmd_options, sudo=True)
        disconnect_node(node)

    @staticmethod
    def dpdk_testpmd_stop(node):
        """Stop DPDK testpmd app on node.

        :param node: Node to stop testpmd on.
        :type node: dict
        :returns: nothing
        """
        cmd = u"/stop-testpmd.sh"
        exec_cmd_no_error(node, cmd, sudo=True)
        disconnect_node(node)
