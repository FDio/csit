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

*** Settings ***
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Trace
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/vrf.robot
| Resource | resources/libraries/robot/qemu.robot
| Force Tags | VM_ENV | HW_ENV | 3_NODE_DOUBLE_LINK_TOPO
| Test Teardown | Run Keywords
| ... | Show Packet Trace on All DUTs | ${nodes} | AND
| ... | Show vpp trace dump on all DUTs | AND
| ... | Show Vpp Settings | ${nodes['DUT1']} | AND
| ... | Show Vpp Settings | ${nodes['DUT2']} | AND
| ... | Stop and Clear QEMU | ${dut1_node} | ${vm_node} | AND
| ... | Check VPP PID in Teardown

#| Suite Setup | Run Keywords
#| ... | Setup all DUTs before test | AND
#| ... | Setup all TGs before traffic script | AND
#| ... | Update All Interface Data On All Nodes | ${nodes} | AND
#| ... | Setup DUT nodes for IPv4 testing
#| Test Setup | Run Keywords | Save VPP PIDs | AND
#| ... | Clear interface counters on all vpp nodes in topology | ${nodes}
#| Test Teardown | Run Keywords
#| ... | Show packet trace on all DUTs | ${nodes} | AND
#| ... | Show vpp trace dump on all DUTs | AND
#| ... | Check VPP PID in Teardown
#| Documentation | *IPv4 routing test cases*
#| ...
#| ... | RFC791 IPv4, RFC826 ARP, RFC792 ICMPv4. Encapsulations: Eth-IPv4-ICMPv4
#| ... | on links TG-DUT1, TG-DUT2, DUT1-DUT2. IPv4 routing tests use circular
#| ... | 3-node topology TG - DUT1 - DUT2 - TG with one link between the nodes.
#| ... | DUT1 and DUT2 are configured with IPv4 routing and static routes. Test
#| ... | ICMPv4 Echo Request packets are sent in both directions by TG on links
#| ... | to DUT1 and DUT2 and received on TG links on the other side of circular
#| ... | topology. On receive TG verifies packets IPv4 src-addr, dst-addr and MAC
#| ... | addresses.

*** Variables ***
| ${net1_ip1}= | 10.0.1.1
| ${net1_ip2}= | 10.0.1.2
| ${net2_ip1}= | 10.0.2.1
| ${net2_ip2}= | 10.0.2.2
| ${net3_ip1}= | 10.0.3.1
| ${net3_ip2}= | 10.0.3.2
| ${prefix_length}= | 24
| ${fib_table_2}= | 20
#| ${neighbor_1_ip}= | 192.168.2.10
#| ${neighbor_1_mac}= | 02:00:00:00:00:02
#| ${neighbor_2_ip}= | 192.168.2.20
#| ${neighbor_2_mac}= | 02:00:00:00:00:03
#

*** Test Cases ***
| TC01: IPv4 forward via vhost to another VRF
| | [Tags] | tmp
| | [Documentation]
| | ... | TBD
| |
| | Given Path for 2-node testing is set
| | ... | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | And Interfaces in 2-node path are UP

| | ${vhost1}= | And Vpp Create Vhost User Interface | ${dut_node} | ${sock1}
| | ${vhost2}= | And Vpp Create Vhost User Interface | ${dut_node} | ${sock2}
| | And Set Interface State | ${dut1_node} | ${vhost1} | up
| | And Set Interface State | ${dut1_node} | ${vhost2} | up

| | Assign Interface To Fib Table | ${dut_node}
| | ... | ${vhost2} | ${fib_table}
| | And Assign Interface To Fib Table | ${dut_node}
| | ... | ${dut_to_tg_if2} | ${fib_table_2}

| | And Set Interface Address | ${dut_node}
| | ... | ${dut_to_tg_if1} | ${net1_ip1} | ${prefix_length}
| | ... | ${vhost1} | ${net2_ip1} | ${prefix_length}
| | ... | ${vhost2} | ${net2_ip2} | ${prefix_length}
| | ... | ${dut_to_tg_if2} | ${net3_ip1} | ${prefix_length}




#| | ${vhost_mac}= | Get Vhost User Mac By SW Index | ${dut1_node} | ${vhost2}
#| | Set test variable | ${dst_vhost_mac} | ${vhost_mac}
#| | VM for Vhost L2BD forwarding is setup | ${dut1_node} | ${sock1} | ${sock2}
#
#| | Set Interface Address | ${dut1_node} | ${vhost2} | ${vhost_ip} | ${prefix4}
#| | And Set Interface Address | ${dut_node}
#| | ... | ${dut_to_tg_if1} | ${net1_ip1} | ${prefix_length}
#| | And Set Interface Address | ${dut_node}
#| | ... | ${dut_to_tg_if2} | ${net3_ip1} | ${prefix_length}
#
#| | And Add Arp On Dut
#| | ... | ${dut_node} | ${dut_to_tg_if1} | ${neighbor_1_ip} | ${neighbor_1_mac}


# create vm
# set bd on vm
# create vrf
# interface set vrf, ip, neighbour,
# set routes to vrf
# send ip traffic

*** Keywords ***
| Setup Qemu DUT1
| | [Documentation] | Setup Vhosts on DUT1 and setup IP on one of them. Setup\
| | ... | Qemu and bridge the vhosts. Optionally, you can set fib table ID\
| | ... | where the vhost2 interface should be assigned to.
| | ...
| | [Arguments] | ${fib_table}=0
| | ...
| | ${vhost1}= | Vpp Create Vhost User Interface | ${dut1_node} | ${sock1}
| | ${vhost2}= | Vpp Create Vhost User Interface | ${dut1_node} | ${sock2}
| | Set Interface Address | ${dut1_node} | ${vhost2} | ${vhost_ip} | ${prefix4}
| | Assign Interface To Fib Table | ${dut1_node}
| | ... | ${vhost2} | ${fib_table}
| | Set Interface State | ${dut1_node} | ${vhost1} | up
| | Set Interface State | ${dut1_node} | ${vhost2} | up
| | Bridge domain on DUT node is created | ${dut1_node} | ${bid} | learn=${TRUE}
| | Interface is added to bridge domain | ${dut1_node}
| | ... | ${dut1_to_tg} | ${bid} | 0
| | Interface is added to bridge domain | ${dut1_node}
| | ... | ${vhost1} | ${bid} | 0
| | ${vhost_mac}= | Get Vhost User Mac By SW Index | ${dut1_node} | ${vhost2}
| | Set test variable | ${dst_vhost_mac} | ${vhost_mac}
| | VM for Vhost L2BD forwarding is setup | ${dut1_node} | ${sock1} | ${sock2}
