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
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/testing_path.robot
| Resource | resources/libraries/robot/traffic.robot
| Library  | resources.libraries.python.Trace
| Library  | resources.libraries.python.Docker.SetupDocker
| Library  | resources.libraries.python.Tap
| Library  | resources.libraries.python.Namespaces
| Library  | resources.libraries.python.IPUtil
| Force Tags | HW_ENV | VM_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
| ...        | AND          | Clean Up | ${nodes['DUT1']}
| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| ...            | AND | Log | ...
| ...           | AND          | Remove and clean all dockers | ${nodes['DUT1']}
| ...           | AND          | Clean Up | ${nodes['DUT1']}
| Documentation | *Provider network FDS related.*
| ...
| ... | Test suite uses 3-node topology TG - DUT1 - DUT2 - TG
| ... | with one link between nodes. Test packets are sent in both directions
| ... | between namespaces in DUT1 and DUT2 with both positive and negative
| ... | scenarios tested.
*** Variables ***
| ${tap1_ip}= | 16.0.10.1
| ${tap2_ip}= | 16.0.20.1

| ${tap1_NM}= | 16.0.10.2
| ${tap2_NM}= | 16.0.20.2

| ${bid_from_TG}= | 19
| ${bid_to_TG}= | 20
| ${bid_NM}= | container1_br

| ${tap_mac}= | 02:00:00:00:00:02
| ${tap_NM_mac}= | 02:00:00:00:00:04

| ${prefix}= | 24
*** Test Cases ***
| Tap Interface With BD Send Packet
| | Given Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Interfaces in 2-node path are up
| | Setup Tap On Node | ${dut_node}
| | Setup Docker On Dut | ${dut_node}
| | Setup Namespaces | ${dut_node}
| | Setup Bridge Domain | ${dut_node}
| | Send and receive ICMP Packet | ${tg_node} | ${tg_to_dut_if1} | ${tg_to_dut_if2}

| Tap Interface Send Ping
| | Given Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['TG']}
| | Interfaces in 2-node path are up
| | Set Interface Address | ${dut_node} | ${dut_to_tg_if1} | 192.168.0.1 | ${prefix}

| | ${int1}= | Add Tap Interface | ${dut_node} | tap_int1 | ${tap_mac}
| | Set Interface Address
| | ... | ${dut_node} | ${int1} | ${tap1_ip} | ${prefix}
| | Set Interface State | ${dut_node} | ${int1} | up

| | Setup Docker On Dut | ${dut_node}
| | Attach Interface To Namespace | ${dut_node} | container1 | tap_int1
| | Set Int State In Namespace | ${dut_node} | container1 | tap_int1 | up
| | Set Int IP In Namespace | ${dut_node} | container1 | tap_int1 | ${tap1_NM} | ${prefix}

#| | And Add Arp On Dut
#| | ... | ${dut_node} | ${dut_to_tg_if1} | ${tap1_ip} | ${tap_mac}
| | Set Int Mac In Namespace | ${dut_node} | container1 | tap_int1 | ${tap_NM_mac}
| | VPP IP Probe | ${dut_node} | tap-0 | ${tap1_NM}
| | And Add Arp On Dut
| | ... | ${dut_node} | ${int1} | ${tap1_NM} | ${tap_NM_mac}
| | Int Add Route In Namespace | ${dut_node} | container1 | 192.168.0.0 | ${prefix} | ${tap1_ip}
#| | Vpp Route Add | ${dut_node} | 192.168.0.2 | ${prefix} | ${tap1_ip} | ${dut_to_tg_if1}
| | Node replies to ICMP echo request | ${tg_node} | ${tg_to_dut_if1} | ${dut_to_tg_if1_mac} | ${tg_to_dut_if1_mac} | ${tap1_NM} | 192.168.0.2


*** Keywords ***
| Setup Docker On Dut
| | [Arguments] | ${node}
| | Install docker on dut | ${node}
| | Pull Docker Os | ${node}
| | Create Docker Container On Dut | ${node} | container1
| | Connect Docker With Namespace | ${node} | container1


| Setup Tap On Node
| | [Arguments] | ${node}
| | ${int1}= | Add Tap Interface | ${node} | tap_int1
| | ${int2}= | Add Tap Interface | ${node} | tap_int2
| | Set Interface State | ${node} | ${int1} | up
| | Set Interface State | ${node} | ${int2} | up
| | Set Test Variable | ${tap1_int} | ${int1}
| | Set Test Variable | ${tap2_int} | ${int2}

| Setup Namespaces
| | [Arguments] | ${node}
| | Attach Interface To Namespace | ${node} | container1 | tap_int1
| | Attach Interface To Namespace | ${node} | container1 | tap_int2
| | Set Int State In Namespace | ${node} | container1 | tap_int1 | up
| | Set Int State In Namespace | ${node} | container1 | tap_int2 | up

| Setup Bridge Domain
| | [Arguments] | ${node}
| | Bridge domain on DUT node is created | ${node} | ${bid_to_TG} | learn=${TRUE}
| | Bridge domain on DUT node is created | ${node} | ${bid_from_TG} | learn=${TRUE}
| | Create Bridge For Int In Namespace | ${node} | container1 | ${bid_NM} | tap_int1 | tap_int2

| | Interface is added to bridge domain | ${node} | ${tap1_int} | ${bid_to_TG} | 0
| | Interface is added to bridge domain | ${node} | ${dut_to_tg_if1} | ${bid_to_TG} | 0
| | Interface is added to bridge domain | ${node} | ${tap2_int} | ${bid_from_TG} | 0
| | Interface is added to bridge domain | ${node} | ${dut_to_tg_if2} | ${bid_from_TG} | 0

