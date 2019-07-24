# Copyright (c) 2019 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.Policer
| ...
| Documentation | Policer keywords

*** Keywords ***
| Initialize IPv4 policer 2r3c-${t} in circular topology
| | [Documentation]
| | ... | Setup of 2r3c color-aware or color-blind policer with dst IPv4 match
| | ... | on all DUT nodes in 2-node / 3-node circular topology. Policer is
| | ... | applied on links TG - DUTx.
| | ...
| | Policer Classify Set Match IP | 20.20.20.2 | ${False}
| | Policer Set Configuration | ${dut1} | ${dut1_if1} | policer1
| | ... | ${cir} | ${eir} | ${cb} | ${eb}
| | ... | pps | Closest | 2R3C 2698 | Transmit
| | ... | Mark and Transmit | Transmit | True
| | ... | 10 | l3 ip4 src | exceed_dscp=AF22
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${dut1_if2}
| | Run Keyword Unless | '${dut2_status}' == 'PASS'
| | ... | Policer Set Name | policer2
| | Policer Set Node | ${dut}
| | Policer Classify Set Interface | ${dut_if2}
| | Policer Classify Set Match IP | 10.10.10.2 | ${False}
| | Policer Set Configuration | ${dut1} | policer2 | ${cir} 
| | ... | ${eir} | ${cb} | ${eb}
| | ... | pps | Closest | 2R3C 2698 | Transmit
| | ... | Mark and Transmit | Transmit | True | exceed_dscp=AF22

| Initialize IPv6 policer 2r3c-${t} in circular topology
| | [Documentation]
| | ... | Setup of 2r3c color-aware or color-blind policer with dst IPv6 match
| | ... | on all DUT nodes in 2-node / 3-node circular topology. Policer is
| | ... | applied on links TG - DUTx.
| | ...
| | ${dscp}= | DSCP AF22
| | Policer Set Name | policer1
| | Policer Set CIR | ${cir}
| | Policer Set EIR | ${eir}
| | Policer Set CB | ${cb}
| | Policer Set EB | ${eb}
| | Policer Set Rate Type pps
| | Policer Set Round Type Closest
| | Policer Set Type 2R3C 2698
| | Policer Set Conform Action Transmit
| | Policer Set Exceed Action Mark and Transmit | ${dscp}
| | Policer Set Violate Action Transmit
| | Policer Enable Color Aware
| | Run Keyword If | ${t} == 'ca' | Policer Enable Color Aware
| | Policer Classify Set Precolor Exceed
| | Policer Set Node | ${dut1}
| | Policer Classify Set Interface | ${dut1_if1}
| | Policer Classify Set Match IP | 2001:2::2 | ${False}
| | Policer Set Configuration
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${dut1_if2}
| | Run Keyword Unless | '${dut2_status}' == 'PASS'
| | ... | Policer Set Name | policer2
| | Policer Set Node | ${dut}
| | Policer Classify Set Interface | ${dut_if2}
| | Policer Classify Set Match IP | 2001:1::2 | ${False}
| | Policer Set Configuration
