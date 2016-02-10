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
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/bridge_domain.robot
| Resource | resources/libraries/robot/ipv4.robot
| Library | resources/libraries/python/TrafficGenerator.py
| Library | resources/libraries/python/CrossConnectSetup.py
| Force Tags | topo-3node | PERFTEST
| Test Setup | Setup all DUTs before test
| Suite Setup | Initialize traffic generator | ${nodes['TG']}
| ... | ${nodes['TG']['interfaces']['port3']['pci_address']}
| ... | ${nodes['TG']['interfaces']['port5']['pci_address']}
| Suite Teardown | Teardown traffic generator | ${nodes['TG']}

*** Test Cases ***
| VPP passes 64B frames through L2 cross connect at 30% of linerate in 3-node-topology
| | Given L2 xconnect initialized in a 3-node topology
| | Then Traffic should pass with no loss | 10 | 30 | 64 | 3-node-xconnect

| VPP passes 1518B frames through L2 cross connect at 100% of linerate in 3-node-topology
| | Given L2 xconnect initialized in a 3-node topology
| | Then Traffic should pass with no loss | 10 | 100 | 1518 | 3-node-xconnect

| VPP passes 9000B frames through L2 cross connect at 100% of linerate in 3-node-topology
| | Given L2 xconnect initialized in a 3-node topology
| | Then Traffic should pass with no loss | 10 | 100 | 9000 | 3-node-xconnect

| VPP passes 64B frames through bridge domain at 30% in 3-node topology
| | Given L2 bridge domain initialized in a 3-node topology
| | Then Traffic should pass with no loss | 10 | 30 | 64 | 3-node-bridge

| VPP passes 1518B frames through bridge domain at 100% in 3-node topology
| | Given L2 bridge domain initialized in a 3-node topology
| | Then Traffic should pass with no loss | 10 | 100 | 1518 | 3-node-bridge

| VPP passes 9000B frames through bridge domain at 100% in 3-node topology
| | Given L2 bridge domain initialized in a 3-node topology
| | Then Traffic should pass with no loss | 10 | 100 | 9000 | 3-node-bridge

#| VPP passes 64B frames through IPv4 forwarding at 30% in 3-node topology
#| | Given IPv4 forwarding initialized in a 3-node topology
#| | Then Traffic should pass with no loss | 10 | 30 | 64 | 3-node-IPv4

#| VPP passes 1518B frames through IPv4 forwarding at 100% in 3-node topology
#| | Given IPv4 forwarding initialized in a 3-node topology
#| | Then Traffic should pass with no loss | 10 | 100 | 1518 | 3-node-IPv4

#| VPP passes 9000B frames through IPv4 forwarding at 100% in 3-node topology
#| | Given IPv4 forwarding initialized in a 3-node topology
#| | Then Traffic should pass with no loss | 10 | 100 | 9000 | 3-node-IPv4


*** Keywords ***


| L2 xconnect initialized in a 3-node topology
| | Interfaces on DUT are in "up" state
| | L2 setup xconnect on DUTs

| L2 setup xconnect on DUTs
| | Vpp Setup Bidirectional Cross Connect | ${nodes['DUT1']}
| | ... | ${nodes['DUT1']['interfaces']['port1']['name']}
| | ... | ${nodes['DUT1']['interfaces']['port3']['name']}
| | Vpp Setup Bidirectional Cross Connect | ${nodes['DUT2']}
| | ... | ${nodes['DUT2']['interfaces']['port1']['name']}
| | ... | ${nodes['DUT2']['interfaces']['port3']['name']}

| L2 bridge domain initialized in a 3-node topology
| | ${tg}= | Set Variable | ${nodes['TG']}
| | ${dut1}= | Set Variable | ${nodes['DUT1']}
| | ${dut2}= | Set Variable | ${nodes['DUT2']}
| | ${tg_links}= | bridge_domain.Setup TG "${tg}" DUT1 "${dut1}" And DUT2 "${dut2}" For 3 Node L2 Bridge Domain Test

| IPv4 forwarding initialized in a 3-node topology
| | Setup DUT nodes for IPv4 testing

| Interfaces on DUT are in "${state}" state
| | Node "${nodes['DUT1']}" interface "${nodes['DUT1']['interfaces']['port1']['name']}" is in "${state}" state
| | Node "${nodes['DUT1']}" interface "${nodes['DUT1']['interfaces']['port3']['name']}" is in "${state}" state
| | Node "${nodes['DUT2']}" interface "${nodes['DUT2']['interfaces']['port1']['name']}" is in "${state}" state
| | Node "${nodes['DUT2']}" interface "${nodes['DUT2']['interfaces']['port3']['name']}" is in "${state}" state

| Traffic should pass with no loss
| | [Arguments] | ${duration} | ${rate} | ${framesize} | ${topology_type}
| | Send traffic on | ${nodes} | ${duration}
| | ...             | ${rate} | ${framesize} | ${topology_type}
| | No traffic loss occured
