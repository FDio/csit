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
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/ipv4.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/double_qemu_setup.robot
| Resource | resources/libraries/robot/qemu.robot
| Library  | resources.libraries.python.Trace
| Force Tags | HW_ENV | VM_ENV | SKIP_PATCH
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...           | AND          | Show vpp trace dump on all DUTs
| ...           | AND          | Qemu Teardown | ${dut1_node} | ${qemu_node1}
| ...                          | qemu_node1
| ...           | AND          | Qemu Teardown | ${dut2_node} | ${qemu_node2}
| ...                          | qemu_node2
| Documentation | *Provider network FDS related.*
| ...
| ... | Test suite uses 3-node topology TG - DUT1 - DUT2 - TG
| ... | with one link between nodes. Test packets are sent in both directions
| ... | between namespaces in DUT1 and DUT2 with both positive and negative
| ... | scenarios tested.

*** Variables ***
| ${bd_id1}= | 1
| ${bd_id2}= | 2
| ${shg1}= | 3
| ${shg2}= | 4
| ${sock1}= | /tmp/sock1
| ${sock2}= | /tmp/sock2
| ${sock3}= | /tmp/sock3
| ${sock4}= | /tmp/sock4

| ${bid_b}= | 23
| ${bid_r}= | 24

| ${vlan_red}= | 50
| ${vlan_blue}= | 60

| ${dut1_if_ip}= | 16.0.0.1
| ${dut2_if_ip}= | 16.0.0.2

| ${dut1_blue1}= | 16.0.10.1
| ${dut1_blue2}= | 16.0.10.2
| ${dut1_red1}= | 16.0.10.3
| ${dut1_red2}= | 16.0.10.4

| ${dut2_blue1}= | 16.0.20.1
| ${dut2_blue2}= | 16.0.20.2
| ${dut2_red1}= | 16.0.20.3
| ${dut2_red2}= | 16.0.20.4

| ${namespace1}= | nmspace1
| ${namespace2}= | nmspace2
| ${namespace3}= | nmspace3
| ${namespace4}= | nmspace4

| ${prefix_length}= | 16

*** Test Cases ***
| Provider network test cases with provider physical networks (VLAN)
| | [Documentation] | Ping among all ports inside the same network should pass.
| | ...             | a) test l2 connectivity inside every network
| | ...             | b) test l2 connectivity between networks
| | [Tags] | 3_NODE_DOUBLE_LINK_TOPO | VPP_VM_ENV
| | Given Path for 3-node testing is set | ${nodes['TG']} | ${nodes['DUT1']}
| | ... | ${nodes['DUT2']} | ${nodes['TG']}
| | And Set Interface Address | ${dut1_node} | ${dut1_to_dut2} | ${dut1_if_ip}
| | ... | ${prefix_length}
| | And Set Interface Address | ${dut2_node} | ${dut2_to_dut1} | ${dut2_if_ip}
| | ... | ${prefix_length}
| | And Set Interface State | ${dut1_node} | ${dut1_to_dut2} | up
| | And Set Interface State | ${dut2_node} | ${dut2_to_dut1} | up
| | ${vhost_if1_DUT1}= | And Vpp Create Vhost User Interface
| | ... | ${dut1_node} | ${sock1}
| | ${vhost_if2_DUT1}= | And Vpp Create Vhost User Interface
| | ... | ${dut1_node} | ${sock2}
| | ${vhost_if3_DUT1}= | And Vpp Create Vhost User Interface
| | ... | ${dut1_node} | ${sock3}
| | ${vhost_if4_DUT1}= | And Vpp Create Vhost User Interface
| | ... | ${dut1_node} | ${sock4}
| | ${dut1_vhosts}= | And Create List | ${vhost_if1_DUT1} | ${vhost_if2_DUT1}
| | ... | ${vhost_if3_DUT1} | ${vhost_if4_DUT1}
| | ${vhost_if1_DUT2}= | And Vpp Create Vhost User Interface
| | ... | ${dut2_node} | ${sock1}
| | ${vhost_if2_DUT2}= | And Vpp Create Vhost User Interface
| | ... | ${dut2_node} | ${sock2}
| | ${vhost_if3_DUT2}= | And Vpp Create Vhost User Interface
| | ... | ${dut2_node} | ${sock3}
| | ${vhost_if4_DUT2}= | And Vpp Create Vhost User Interface
| | ... | ${dut2_node} | ${sock4}
| | ${dut2_vhosts}= | And Create List | ${vhost_if1_DUT2} | ${vhost_if2_DUT2}
| | ... | ${vhost_if3_DUT2} | ${vhost_if4_DUT2}
| | When Setup QEMU Vhost and Run | ${dut1_node}
| | ...                   | ${sock1}
| | ...                   | ${sock2}
| | ...                   | ${sock3}
| | ...                   | ${sock4}
| | ...                   | ${dut1_blue1}
| | ...                   | ${dut1_blue2}
| | ...                   | ${dut1_red1}
| | ...                   | ${dut1_red2}
| | ...                   | ${prefix_length}
| | ...                   | qemu_node1
| | ...                   | 04
| | And Setup QEMU Vhost and Run | ${dut2_node}
| | ...                   | ${sock1}
| | ...                   | ${sock2}
| | ...                   | ${sock3}
| | ...                   | ${sock4}
| | ...                   | ${dut2_blue1}
| | ...                   | ${dut2_blue2}
| | ...                   | ${dut2_red1}
| | ...                   | ${dut2_red2}
| | ...                   | ${prefix_length}
| | ...                   | qemu_node2
| | ...                   | 06
| | And Setup VLAN and BD on Dut | ${dut1_node} | ${dut1_to_dut2}
| | ... | @{dut1_vhosts}
| | And Setup VLAN and BD on Dut | ${dut2_node} | ${dut2_to_dut1}
| | ... | @{dut2_vhosts}
| | Then Positive Scenario Ping From DUT1 - Intra network
| | And Positive Scenario Ping From DUT1 - Inter network
| | And Positive Scenario Ping From DUT2 - Intra network
| | And Positive Scenario Ping From DUT2 - Inter network
| | And Negative Scenario Ping From DUT1 - Intra network
| | And Negative Scenario Ping From DUT1 - Inter network
| | And Negative Scenario Ping From DUT2 - Intra network
| | And Negative Scenario Ping From DUT2 - Inter network

*** Keywords ***
| Setup VLAN and BD on Dut
| | [Documentation] | Setup VLAN and bridge domain on specific DUT and
| | ...             | subsequently interconnect them properly. Also set VLAN tag
| | ...             | rewrite on vhosts.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - Node where to setup VLAN and BD. Type: dict
| | ... | - interface - Interface where to create VLAN sub-interface.
| | ... |               Type: string
| | ... | - vhosts - List containing vhost interfaces.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Setup VLAN and BD on Dut \| ${dut_node} \| GigabitEthernet0/6/0 \
| | ... | \| @{vhosts} \|
| | ...
| | [Arguments] | ${dut_node} | ${interface} | @{vhosts}
| | Bridge domain on DUT node is created | ${dut_node} | ${bid_b} | learn=${TRUE}
| | Bridge domain on DUT node is created | ${dut_node} | ${bid_r} | learn=${TRUE}
| | ${interface_name}= | Get interface name | ${dut_node} | ${interface}
| | ${vlan1_name} | ${vlan1_index}= | Create Vlan Subinterface
| | ... | ${dut_node} | ${interface_name} | ${vlan_blue}
| | ${vlan2_name} | ${vlan2_index}= | Create Vlan Subinterface
| | ... | ${dut_node} | ${interface_name} | ${vlan_red}
| | L2 Tag Rewrite | ${dut_node} | @{vhosts}[0] | push-1 | ${vlan_blue}
| | L2 Tag Rewrite | ${dut_node} | @{vhosts}[1] | push-1 | ${vlan_blue}
| | L2 Tag Rewrite | ${dut_node} | @{vhosts}[2] | push-1 | ${vlan_red}
| | L2 Tag Rewrite | ${dut_node} | @{vhosts}[3] | push-1 | ${vlan_red}
| | Interface is added to bridge domain | ${dut_node}
| | ... | ${vlan1_index} | ${bid_b} | 0
| | Interface is added to bridge domain | ${dut_node}
| | ... | @{vhosts}[0] | ${bid_b} | 0
| | Interface is added to bridge domain | ${dut_node}
| | ... | @{vhosts}[1] | ${bid_b} | 0
| | Interface is added to bridge domain | ${dut_node}
| | ... | ${vlan2_index} | ${bid_r} | 0
| | Interface is added to bridge domain | ${dut_node}
| | ... | @{vhosts}[2] | ${bid_r} | 0
| | Interface is added to bridge domain | ${dut_node}
| | ... | @{vhosts}[3] | ${bid_r} | 0

| Positive Scenario Ping From DUT1 - Intra network
| | [Documentation] | Send ping packets from specified namespaces to other in
| | ...             | order to test connectivity.
| | Send Ping From Node To Dst | ${qemu_node1} | ${dut1_blue2} | ${namespace1}
| | Send Ping From Node To Dst | ${qemu_node1} | ${dut1_blue1} | ${namespace2}
| | Send Ping From Node To Dst | ${qemu_node1} | ${dut1_red2} | ${namespace3}
| | Send Ping From Node To Dst | ${qemu_node1} | ${dut1_red1} | ${namespace4}

| Positive Scenario Ping From DUT1 - Inter network
| | [Documentation] | Send ping packets from specified namespaces to other in
| | ...             | order to test connectivity.
| | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_blue1} | ${namespace1}
| | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_blue2} | ${namespace1}
| | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_blue1} | ${namespace2}
| | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_blue2} | ${namespace2}
| | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_red1} | ${namespace3}
| | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_red2} | ${namespace3}
| | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_red1} | ${namespace4}
| | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_red2} | ${namespace4}

| Positive Scenario Ping From DUT2 - Intra network
| | [Documentation] | Send ping packets from specified namespaces to other in
| | ...             | order to test connectivity.
| | Send Ping From Node To Dst | ${qemu_node2} | ${dut2_blue2} | ${namespace1}
| | Send Ping From Node To Dst | ${qemu_node2} | ${dut2_blue1} | ${namespace2}
| | Send Ping From Node To Dst | ${qemu_node2} | ${dut2_red2} | ${namespace3}
| | Send Ping From Node To Dst | ${qemu_node2} | ${dut2_red1} | ${namespace4}

| Positive Scenario Ping From DUT2 - Inter network
| | [Documentation] | Send ping packets from specified namespaces to other in
| | ...             | order to test connectivity.
| | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_blue1} | ${namespace1}
| | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_blue2} | ${namespace1}
| | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_blue1} | ${namespace2}
| | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_blue2} | ${namespace2}
| | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_red1} | ${namespace3}
| | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_red2} | ${namespace3}
| | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_red1} | ${namespace4}
| | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_red2} | ${namespace4}

| Negative Scenario Ping From DUT1 - Intra network
| | [Documentation] | Send ping packets from specified namespaces to other in
| | ...             | order to test unreachability of namespaces.
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut1_red1}
| | ... | ${namespace1}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut1_red2}
| | ... | ${namespace1}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut1_red1}
| | ... | ${namespace2}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut1_red2}
| | ... | ${namespace2}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut1_blue1}
| | ... | ${namespace3}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut1_blue2}
| | ... | ${namespace3}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut1_blue1}
| | ... | ${namespace4}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut1_blue2}
| | ... | ${namespace4}


| Negative Scenario Ping From DUT1 - Inter network
| | [Documentation] | Send ping packets from specified namespaces to other in
| | ...             | order to test unreachability of namespaces.
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_red1}
| | ... | ${namespace1}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_red2}
| | ... | ${namespace1}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_red1}
| | ... | ${namespace2}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_red2}
| | ... | ${namespace2}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_blue1}
| | ... | ${namespace3}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_blue2}
| | ... | ${namespace3}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_blue1}
| | ... | ${namespace4}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node1} | ${dut2_blue2}
| | ... | ${namespace4}

| Negative Scenario Ping From DUT2 - Intra network
| | [Documentation] | Send ping packets from specified namespaces to other in
| | ...             | order to test unreachability of namespaces.
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut2_red1}
| | ... | ${namespace1}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut2_red2}
| | ... | ${namespace1}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut2_red1}
| | ... | ${namespace2}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut2_red2}
| | ... | ${namespace2}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut2_blue1}
| | ... | ${namespace3}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut2_blue2}
| | ... | ${namespace3}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut2_blue1}
| | ... | ${namespace4}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut2_blue2}
| | ... | ${namespace4}


| Negative Scenario Ping From DUT2 - Inter network
| | [Documentation] | Send ping packets from specified namespaces to other in
| | ...             | order to test unreachability of namespaces.
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_red1}
| | ... | ${namespace1}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_red2}
| | ... | ${namespace1}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_red1}
| | ... | ${namespace2}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_red2}
| | ... | ${namespace2}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_blue1}
| | ... | ${namespace3}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_blue2}
| | ... | ${namespace3}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_blue1}
| | ... | ${namespace4}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node2} | ${dut1_blue2}
| | ... | ${namespace4}
