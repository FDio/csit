# Copyright (c) 2017 Cisco and/or its affiliates.
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


"""
This module exists to provide the UDP test for TLDK on topology nodes.
"""

from scapy.utils import rdpcap
from scapy.layers.inet import IP
from scapy.layers.inet6 import IPv6

from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.ssh import SSH
from resources.libraries.python.TLDK.TLDKConstants import TLDKConstants as con
from resources.libraries.python.topology import Topology

class UdpTest(object):
    """Test the TLDK UDP function."""

    @staticmethod
    def get_pcap_info(file_prefix):
        """Get the Dest IP from the RX pcap file

        :param file_prefix: the test case pcap file prefix
        :type file_prefix: str
        :returns: packet counts, dest ip, is or not ipv4
        :rtype: tuple(int, str, bool).
        """
        exec_dir = BuiltIn().get_variable_value("${EXECDIR}")

        rx_pcapfile = '{0}/{1}/{2}_rx.pcap' \
            .format(exec_dir, con.TLDK_TESTCONFIG, file_prefix)
        packets = rdpcap(rx_pcapfile)
        count = len(packets)

        ### the first packet
        pkt = packets[0]
        if pkt.type == 0x0800:
            ### this is a IPv4 packet
            dest_ip = pkt[IP].dst
            is_ipv4 = True
        elif pkt.type == 0x86dd:
            ### this is a IPv6 packet
            dest_ip = pkt[IPv6].dst
            is_ipv4 = False

        return count, dest_ip, is_ipv4

    @staticmethod
    def exec_the_udpfwd_test(dut_node, dut_if, file_prefix, \
            dest_ip, is_ipv4=True):
        """Execute the udpfwd on the dut_node.

        :param dut_node: Will execute the udpfwd on this node.
        :param dut_if: DUT interface name.
        :param file_prefix: The test case config file prefix.
        :param dest_ip: The UDP packet dest IP.
        :param is_ipv4: Execute the IPv4 or IPv6 test.
        :type dut_node: dict
        :type dut_if: str
        :type file_prefix: str
        :type dest_ip: str
        :type is_ipv4: bool
        :raises RuntimeError: If failed to execute udpfwd test on the dut node.
        """
        pci_address = Topology.get_interface_pci_addr(dut_node, dut_if)
        ssh = SSH()
        ssh.connect(dut_node)
        if is_ipv4:
            cmd = 'cd {0}/{4} && ./run_tldk.sh {0}/{5}/{2}_rx.pcap ' \
                '{0}/{5}/{2}_tx.pcap {1} {0}/{5}/{2}_fe.cfg ' \
                '{0}/{5}/{2}_be.cfg {3} NONE' \
                .format(con.REMOTE_FW_DIR, pci_address, file_prefix, \
                dest_ip, con.TLDK_SCRIPTS, con.TLDK_TESTCONFIG)
        else:
            cmd = 'cd {0}/{4} && ./run_tldk.sh {0}/{5}/{2}_rx.pcap ' \
                '{0}/{5}/{2}_tx.pcap {1} {0}/{5}/{2}_fe.cfg ' \
                '{0}/{5}/{2}_be.cfg NONE {3}' \
                .format(con.REMOTE_FW_DIR, pci_address, file_prefix, \
                dest_ip, con.TLDK_SCRIPTS, con.TLDK_TESTCONFIG)

        (ret_code, _, _) = ssh.exec_command(cmd, timeout=600)
        if ret_code != 0:
            raise RuntimeError('Failed to execute udpfwd test at node {0}'
                               .format(dut_node['host']))

    @staticmethod
    def get_the_test_result(dut_node, file_prefix):
        """
        After execute the udpfwd cmd, use this to get the test result.

        :param dut_node: will get the test result in this dut node
        :param dut_if: the dut interface name
        :param file_prefix: the test case output file prefix
        :type dut_node: dice
        :type dut_if: str
        :type file_prefix: str
        :returns: str.
        :rtype: str
        :raises RuntimeError: If failed to get the test result.
        """
        ssh = SSH()
        ssh.connect(dut_node)
        cmd = 'cd {0}; sudo /usr/sbin/tcpdump -nnnn -vvv -r ./{2}/{1}_tx.pcap' \
              ' | grep \'udp sum ok\' | wc -l' \
            .format(con.REMOTE_FW_DIR, file_prefix, con.TLDK_TESTCONFIG)

        (ret_code, stdout, _) = ssh.exec_command(cmd, timeout=100)
        if ret_code != 0:
            raise RuntimeError('Failed to get test result at node {0}'
                               .format(dut_node['host']))

        return stdout
