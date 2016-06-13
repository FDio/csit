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
| Resource | resources/libraries/robot/double_qemu_setup.robot
| Resource | resources/libraries/robot/qemu.robot
| Library  | resources.libraries.python.Trace
| Library  | resources.libraries.python.Docker.SetupDocker
| Library  | resources.libraries.python.Tap
| Library  | resources.libraries.python.Namespaces
| Force Tags | HW_ENV | VM_ENV
| Test Setup | Run Keywords | Setup all DUTs before test
| ...        | AND          | Setup all TGs before traffic script
#| Test Teardown | Run Keywords | Show Packet Trace on All DUTs | ${nodes}
| Documentation | *Provider network FDS related.*
| ...
| ... | Test suite uses 3-node topology TG - DUT1 - DUT2 - TG
| ... | with one link between nodes. Test packets are sent in both directions
| ... | between namespaces in DUT1 and DUT2 with both positive and negative
| ... | scenarios tested.
*** Variables ***
| ${tap1_ip}= | 16.0.10.0
| ${tap2_ip}= | 16.0.10.1
| ${tap3_ip}= | 16.0.10.2
| ${tap3_ip_HOST}= | 16.0.10.3

| ${prefix}= | 16
*** Test Cases ***
| Tap interface ping
| | Given Path for 2-node testing is set | ${nodes['TG']} | ${nodes['DUT2']} | ${nodes['TG']}
| | Clean Up | ${dut_node}
| | Remove and clean all dockers | ${dut_node}
| | Setup Tap On Node | ${dut_node}
| | Setup Docker On Dut | ${dut_node}
| | Setup Traffic | ${dut_node}
#| | Sleep | 10
#| | Remove and clean all dockers | ${dut_node}
#| | Clean Up | ${dut_node}
*** Keywords ***
| Setup Docker On Dut
| | [Arguments] | ${node}
| | Install docker on dut | ${dut_node}
| | Pull Docker Os | ${dut_node}
| | Create Docker Container On Dut | ${dut_node} | container1
| | Create Docker Container On Dut | ${dut_node} | container2
| | Connect Docker With Namespace | ${dut_node} | container1
| | Connect Docker With Namespace | ${dut_node} | container2
| | Set Namespace Link | ${node} | tap_int1 | container1
| | Set Namespace Link | ${node} | tap_int2 | container2

| Setup Tap On Node
| | [Arguments] | ${node}
| | ${int1}= | Add Tap Interface | ${node} | tap_int1
| | ${int2}= | Add Tap Interface | ${node} | tap_int2
| | ${int3}= | Add Tap Interface | ${node} | tap_int3
| | Set Interface Address
| | ... | ${node} | ${int1} | ${tap1_ip} | ${prefix}
| | Set Interface Address
| | ... | ${node} | ${int2} | ${tap2_ip} | ${prefix}
| | Set Interface Address
| | ... | ${node} | ${int3} | ${tap3_ip} | ${prefix}
| | Set Interface State | ${node} | ${int1} | up
| | Set Interface State | ${node} | ${int2} | up
| | Set Interface State | ${node} | ${int3} | up

| Setup Traffic
| | [Arguments] | ${node}
| | Set Dev Interface Ip | ${node} | tap_int3 | ${tap3_ip_HOST} | ${prefix}
