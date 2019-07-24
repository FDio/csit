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
| Library | resources.libraries.python.Classify
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
| | ${policer_index1}= | Policer Set Configuration | ${dut1} | policer1 | ${cir}
| | ... | ${eir} | ${cb} | ${eb} | pps | Closest | 2R3C_RFC_2698 | Transmit
| | ... | Mark_and_Transmit | Transmit | ${t} | exceed_dscp=${dscp}
| | ${table_idx1} | @{rest}= | Vpp Creates Classify Table L3
| | ... | ${dut1} | ip4 | dst | 20.20.20.2
| | Vpp Configures Classify Session L3 | ${dut1} | permit | ${table_idx1} | ip4
| | ... | dst | 20.20.20.2 | hit_next_index=${policer_index1}
| | Policer Classify Set Interface | ${dut1} | ${dut1_if1} | ${table_idx1}
| | ...
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${dut1_if2}
| | ...
| | ${policer_index2}= | Policer Set Configuration | ${dut} | policer2 | ${cir}
| | ... | ${eir} | ${cb} | ${eb} | pps | Closest | 2R3C_RFC_2698 | Transmit
| | ... | Mark_and_Transmit | Transmit | ${t} | exceed_dscp=${dscp}
| | ${table_idx2} | @{rest}= | Vpp Creates Classify Table L3
| | ... | ${dut} | ip4 | dst | 10.10.10.2
| | Vpp Configures Classify Session L3 | ${dut} | permit | ${table_idx2} | ip4
| | ... | dst | 10.10.10.2 | hit_next_index=${policer_index2}
| | Policer Classify Set Interface | ${dut} | ${dut_if2} | ${table_idx2}

| Initialize IPv6 policer 2r3c-${t} in circular topology
| | [Documentation]
| | ... | Setup of 2r3c color-aware or color-blind policer with dst IPv6 match
| | ... | on all DUT nodes in 2-node / 3-node circular topology. Policer is
| | ... | applied on links TG - DUTx.
| | ...
| | ${policer_index1}= | Policer Set Configuration | ${dut1} | policer1 | ${cir}
| | ... | ${eir} | ${cb} | ${eb} | pps | Closest | 2R3C_RFC_2698 | Transmit
| | ... | Mark_and_Transmit | Transmit | ${t} | exceed_dscp=${dscp}
| | ${table_idx1} | @{rest}= | Vpp Creates Classify Table L3
| | ... | ${dut1} | ip4 | dst | 2001:2::2
| | Vpp Configures Classify Session L3 | ${dut1} | permit | ${table_idx1} | ip4
| | ... | dst | 2001:2::2 | hit_next_index=${policer_index1}
| | Policer Classify Set Interface | ${dut1} | ${dut1_if1} | ${table_idx1}
| | ...
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2_if2}
| | ... | ELSE | Set Variable | ${dut1_if2}
| | ...
| | ${policer_index2}= | Policer Set Configuration | ${dut} | policer2 | ${cir}
| | ... | ${eir} | ${cb} | ${eb} | pps | Closest | 2R3C_RFC_2698 | Transmit
| | ... | Mark_and_Transmit | Transmit | ${t} | exceed_dscp=${dscp}
| | ${table_idx2} | @{rest}= | Vpp Creates Classify Table L3
| | ... | ${dut} | ip4 | dst | 2001:2::2
| | Vpp Configures Classify Session L3 | ${dut} | permit | ${table_idx2} | ip4
| | ... | dst | 2001:2::2 | hit_next_index=${policer_index2}
| | Policer Classify Set Interface | ${dut} | ${dut_if2} | ${table_idx2}
