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


"""This module exists to provide the UDP test for TLDK on topology
nodes. 
"""
import sys
from scapy.all import *

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.ssh import SSH
from resources.libraries.python.TLDK.constants import Constants as con
from resources.libraries.python.topology import NodeType
from resources.libraries.python.topology import Topology

class UdpTest(object): # pylint: disable=too-few-public-methods
    """Test the TLDK UDP function.
    """

    @staticmethod
    def get_pcap_info(file_prefix):
        """ Get the Dest IP from the RX pcap file """
        exec_dir = BuiltIn().get_variable_value("${EXECDIR}")

        rx_pcapfile = '{0}/tldk_testconfig/{1}_rx.pcap'.format(exec_dir, file_prefix)
        packets = rdpcap(rx_pcapfile)
        count = len(packets)

        """ the first packet """
        pkt = packets[0]
        if pkt.type == 0x0800:
            """ this is a IPv4 packet """
            dest_ip = pkt[IP].dst
            is_ipv4 = True
        elif pkt.type == 0x86dd:
            """ this is a IPv6 packet """
            dest_ip = pkt[IPv6].dst
            is_ipv4 = False

        return count, dest_ip, is_ipv4

    @staticmethod
    def exec_the_udpfwd_test(dut_node, dut_if, file_prefix, dest_ip, is_ipv4=True):
        """Execute the udpfwd on the dut_node."""
		
        pci_address = Topology.get_interface_pci_addr(dut_node, dut_if)
        ssh = SSH()
        ssh.connect(dut_node)
        if is_ipv4:
            cmd = 'cd {0} && ./run_tldk.sh {0}/tldk_testconfig/{2}_rx.pcap {0}/tldk_testconfig/{2}_tx.pcap ' \
                '{1} {0}/tldk_testconfig/{2}_fe.cfg {0}/tldk_testconfig/{2}_be.cfg {3} NONE'.format(con.REMOTE_FW_DIR, pci_address, file_prefix, dest_ip)
        else:
            cmd = 'cd {0} && ./run_tldk.sh {0}/tldk_testconfig/{2}_rx.pcap {0}/tldk_testconfig/{2}_tx.pcap ' \
                '{1} {0}/tldk_testconfig/{2}_fe.cfg {0}/tldk_testconfig/{2}_be.cfg NONE {3}'.format(con.REMOTE_FW_DIR, pci_address, file_prefix, dest_ip)

        logger.console('Will Execute the cmd: {0}'.format(cmd))
        
        (ret_code, _, stderr) = ssh.exec_command(cmd, timeout=600)
        if 0 != ret_code:
		    logger.error('Execute the udpfwd error: {0}'.format(stderr))
		    raise Exception('Failed to execute udpfwd test at node {0}'.format(dut_node['host']))
	
    @staticmethod
    def get_the_test_result(dut_node, dut_if, file_prefix):
        """After execute the udpfwd cmd, use this to get the test result."""
		
        ssh = SSH()
        ssh.connect(dut_node)
		
        cmd = 'cd {0}; tcpdump -nnnn -vvv -r ./tldk_testconfig/{1}_tx.pcap | ' \
		    'grep \'udp sum ok\' | wc -l'.format(con.REMOTE_FW_DIR, file_prefix)
		
        logger.console('Will Execute the cmd: {0}'.format(cmd))
        
        (ret_code, stdout, stderr) = ssh.exec_command(cmd, timeout=100)
        if 0 != ret_code:
		    logger.error('Execute the udpfwd error: {0}'.format(stdout + stderr))
		    raise Exception('Failed to execute udpfwd test at node {0}'.format(dut_node['host']))
        else:
            logger.console('Get the test result: {0}'.format(stdout))

        return stdout
