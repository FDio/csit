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

*** Keywords ***
| VPP 4 Vhosts are created
| | [Documentation] | Create four Vhost-User interfaces on defined VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - node - DUT node. Type: dictionary
| | ... | - sock1 - Socket path for first Vhost-User interface. Type: string
| | ... | - sock2 - Socket path for second Vhost-User interface. Type: string
| | ... | - sock3 - Socket path for third Vhost-User interface. Type: string
| | ... | - sock4 - Socket path for forth Vhost-User interface. Type: string
| | ...
| | ... | _NOTE:_ This KW sets following test case variable:
| | ... | - ${vhost_if1} - First Vhost-User interface.
| | ... | - ${vhost_if2} - Second Vhost-User interface.
| | ... | - ${vhost_if3} - Third Vhost-User interface.
| | ... | - ${vhost_if4} - Forth Vhost-User interface.
| | ...
| | ... | *Example:*
| | ... | \| VPP 4 Vhosts are created \| ${nodes['DUT1']} \
| | ... | \| /tmp/sock1 \| /tmp/sock2 \| /tmp/sock3 \| /tmp/sock4 \|
| | ...
| | [Arguments] | ${node} | ${sock1} | ${sock2} | ${sock3} | ${sock4}
| | ${vhost_if1}= | Vpp Create Vhost User Interface | ${node} | ${sock1}
| | ${vhost_if2}= | Vpp Create Vhost User Interface | ${node} | ${sock2}
| | ${vhost_if3}= | Vpp Create Vhost User Interface | ${node} | ${sock3}
| | ${vhost_if4}= | Vpp Create Vhost User Interface | ${node} | ${sock4}
| | Set Test Variable | ${vhost_if1}
| | Set Test Variable | ${vhost_if2}
| | Set Test Variable | ${vhost_if3}
| | Set Test Variable | ${vhost_if4}

| Setup QEMU Vhost and Run
| | [Documentation] | Setup Qemu vhosts and namespaces.
| | ...
| | ... | *Arguments:*
| | ... | - sock1 - Socket path for first Vhost-User interface. Type: string
| | ... | - sock2 - Socket path for second Vhost-User interface. Type: string
| | ... | - sock3 - Socket path for third Vhost-User interface. Type: string
| | ... | - sock4 - Socket path for forth Vhost-User interface. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Setup QEMU Vhost \| /tmp/sock1 \| /tmp/sock2 \
| | ... | \| /tmp/sock3 \| /tmp/sock4 \|
| | ...
| | [Arguments] | ${node} | ${sock1} | ${sock2} | ${sock3} | ${sock4} | ${ip1} | ${ip2}
| | ... | ${ip3} | ${ip4} | ${prefix_length} | ${qemu_name} | ${mac_ID}
| | Import Library | resources.libraries.python.QemuUtils \
| | ... | WITH NAME | ${qemu_name}
| | ${qemu_add_vhost}= | Replace Variables | ${qemu_name}.Qemu Add Vhost User If
| | ${qemu_set_node}= | Replace Variables | ${qemu_name}.Qemu Set Node
| | ${qemu_start}= | Replace Variables | ${qemu_name}.Qemu Start
| | Run keyword | ${qemu_add_vhost} | ${sock1} | mac=52:54:00:00:${mac_ID}:01
| | Run keyword | ${qemu_add_vhost} | ${sock2} | mac=52:54:00:00:${mac_ID}:02
| | Run keyword | ${qemu_add_vhost} | ${sock3} | mac=52:54:00:00:${mac_ID}:03
| | Run keyword | ${qemu_add_vhost} | ${sock4} | mac=52:54:00:00:${mac_ID}:04
| | Run keyword | ${qemu_set_node} | ${node}
| | ${vm}= | Run keyword | ${qemu_start}
| | ${vhost1}= | Get Vhost User If Name By Sock | ${vm} | ${sock1}
| | ${vhost2}= | Get Vhost User If Name By Sock | ${vm} | ${sock2}
| | ${vhost3}= | Get Vhost User If Name By Sock | ${vm} | ${sock3}
| | ${vhost4}= | Get Vhost User If Name By Sock | ${vm} | ${sock4}
| | Set Interface State | ${vm} | ${vhost1} | up
| | Set Interface State | ${vm} | ${vhost2} | up
| | Set Interface State | ${vm} | ${vhost3} | up
| | Set Interface State | ${vm} | ${vhost4} | up
| | Setup Network Namespace
| | ... | ${vm} | nmspace1 | ${vhost1} | ${ip1} | ${prefix_length}
| | Setup Network Namespace
| | ... | ${vm} | nmspace2 | ${vhost2} | ${ip2} | ${prefix_length}
| | Setup Network Namespace
| | ... | ${vm} | nmspace3 | ${vhost3} | ${ip3} | ${prefix_length}
| | Setup Network Namespace
| | ... | ${vm} | nmspace4 | ${vhost4} | ${ip4} | ${prefix_length}
| | Set Test Variable | ${${qemu_name}} | ${vm}

| Setup Vxlan and BD on Dut
| | [Arguments] | ${dut} | ${src_ip} | ${dst_ip}
| | Bridge domain on DUT node is created | ${dut} | ${bid_b} | learn=${TRUE}
| | Bridge domain on DUT node is created | ${dut} | ${bid_r} | learn=${TRUE}
| | ${vxlan1_if} | Create VXLAN interface     | ${dut} | ${vni_blue}
| |                 | ...  | ${src_ip} | ${dst_ip}
| | ${vxlan2_if} | Create VXLAN interface     | ${dut} | ${vni_red}
| |                 | ...  | ${src_ip} | ${dst_ip}
| | Interface is added to bridge domain | ${dut} | ${vxlan1_if} | ${bid_b} | 0
| | Interface is added to bridge domain | ${dut} | ${vhost_if1} | ${bid_b} | 0
| | Interface is added to bridge domain | ${dut} | ${vhost_if2} | ${bid_b} | 0
| | Interface is added to bridge domain | ${dut} | ${vxlan2_if} | ${bid_r} | 0
| | Interface is added to bridge domain | ${dut} | ${vhost_if3} | ${bid_r} | 0
| | Interface is added to bridge domain | ${dut} | ${vhost_if4} | ${bid_r} | 0

| Setup Vlan and BD on Dut
| | [Arguments] | ${dut} | ${src_ip} | ${dst_ip} | ${interface}
| | Bridge domain on DUT node is created | ${dut} | ${bid_b} | learn=${TRUE}
| | Bridge domain on DUT node is created | ${dut} | ${bid_r} | learn=${TRUE}
| | ${vlan1_name} | ${vlan1_index}= | Create Vlan Subinterface
| | ... | ${dut} | ${interface} | ${vlan_blue}
| | ${vlan2_name} | ${vlan2_index}= | Create Vlan Subinterface
| | ... | ${dut} | ${interface} | ${vlan_red}
| | L2 Tag Rewrite | ${dut} | ${vhost_if1} | push-1 | ${vlan_blue}
| | L2 Tag Rewrite | ${dut} | ${vhost_if2} | push-1 | ${vlan_blue}
| | L2 Tag Rewrite | ${dut} | ${vhost_if3} | push-1 | ${vlan_red}
| | L2 Tag Rewrite | ${dut} | ${vhost_if4} | push-1 | ${vlan_red}
| | Interface is added to bridge domain | ${dut} | ${vlan1_index} | ${bid_b} | 0
| | Interface is added to bridge domain | ${dut} | ${vhost_if1} | ${bid_b} | 0
| | Interface is added to bridge domain | ${dut} | ${vhost_if2} | ${bid_b} | 0
| | Interface is added to bridge domain | ${dut} | ${vlan2_index} | ${bid_r} | 0
| | Interface is added to bridge domain | ${dut} | ${vhost_if3} | ${bid_r} | 0
| | Interface is added to bridge domain | ${dut} | ${vhost_if4} | ${bid_r} | 0

| Qemu Teardown
| | [Documentation] | Stop QEMU, clear used sockets and close SSH connection
| | ...             | running on ${dut}, ${vm} is VM node info dictionary
| | ...             | returned by qemu_start or None.
| | [Arguments] | ${dut} | ${vm} | ${qemu_name}
| | ${set_node}= | Replace Variables | ${qemu_name}.Qemu Set Node
| | ${sys_status}= | Replace Variables | ${qemu_name}.Qemu System Status
| | ${kill}= | Replace Variables | ${qemu_name}.Qemu Kill
| | ${sys_pd}= | Replace Variables | ${qemu_name}.Qemu System Powerdown
| | ${quit}= | Replace Variables | ${qemu_name}.Qemu Quit
| | ${clear_socks}= | Replace Variables | ${qemu_name}.Qemu Clear Socks
| | run keyword | ${set_node} | ${dut}
| | ${status} | ${value}= | Run Keyword And Ignore Error | ${sys_status}
| | Run Keyword If | "${status}" == "FAIL" | ${kill}
| | ... | ELSE IF | "${value}" == "running" | ${sys_pd}
| | ... | ELSE | ${quit}
| | run keyword | ${clear_socks}
| | Run Keyword If | ${vm} is not None | Disconnect | ${vm}