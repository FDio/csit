# Copyright (c) 2020 Cisco and/or its affiliates.
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
|
| Documentation | Policer keywords

*** Keywords ***
| Initialize IPv4 policer 2r3c-${t} in circular topology
| | [Documentation]
| | ... | Setup of 2r3c color-aware or color-blind policer with dst IPv4 match
| | ... | on all DUT nodes in 2-node / 3-node circular topology. Policer is
| | ... | applied on links TG - DUTx.
| |
| | ${policer_index}= | Policer Set Configuration | ${dut1} | policer1 | ${cir}
| | ... | ${eir} | ${cb} | ${eb} | pps | Closest | 2R3C_RFC_2698 | Transmit
| | ... | Mark_and_Transmit | Transmit | ${t} | exceed_dscp=${dscp}
| | ${table_idx} | ${skip_n} | ${match_n}= | Vpp Creates Classify Table L3
| | ... | ${dut1} | ip4 | dst | 255.255.255.255
| | ${pre_color}= | Policer Classify Get Precolor | exceed_color
| | Vpp Configures Classify Session L3 | ${dut1} | permit | ${table_idx}
| | ... | ${skip_n} | ${match_n} | ip4 | dst | 20.20.20.2
| | ... | hit_next_index=${policer_index} | opaque_index=${pre_color}
| | Policer Classify Set Interface
| | ... | ${dut1} | ${DUT1_${int}1}[0]
| | ... | ip4_table_index=${table_idx}
| |
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${DUT2_${int}2}[0]
| | ... | ELSE | Set Variable | ${DUT1_${int}2}[0]
| |
| | ${policer_index}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Policer Set Configuration | ${dut} | policer2 | ${cir}
| | ... | ${eir} | ${cb} | ${eb} | pps | Closest | 2R3C_RFC_2698 | Transmit
| | ... | Mark_and_Transmit | Transmit | ${t} | exceed_dscp=${dscp}
| | ... | ELSE | Set Variable | ${policer_index}
| | ${table_idx} | ${skip_n} | ${match_n}=
| | ... | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Creates Classify Table L3 | ${dut} | ip4 | dst | 255.255.255.255
| | ... | ELSE | Set Variable | ${table_idx} | ${skip_n} | ${match_n}
| | Vpp Configures Classify Session L3 | ${dut} | permit | ${table_idx}
| | ... | ${skip_n} | ${match_n} | ip4 | dst | 10.10.10.2
| | ... | hit_next_index=${policer_index} | opaque_index=${pre_color}
| | Policer Classify Set Interface | ${dut} | ${dut_if2}
| | ... | ip4_table_index=${table_idx}

| Initialize IPv6 policer 2r3c-${t} in circular topology
| | [Documentation]
| | ... | Setup of 2r3c color-aware or color-blind policer with dst IPv6 match
| | ... | on all DUT nodes in 2-node / 3-node circular topology. Policer is
| | ... | applied on links TG - DUTx.
| |
| | ${policer_index}= | Policer Set Configuration | ${dut1} | policer1 | ${cir}
| | ... | ${eir} | ${cb} | ${eb} | pps | Closest | 2R3C_RFC_2698 | Transmit
| | ... | Mark_and_Transmit | Transmit | ${t} | exceed_dscp=${dscp}
| | ${table_idx} | ${skip_n} | ${match_n}= | Vpp Creates Classify Table L3
| | ... | ${dut1} | ip6 | dst | ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
| | ${pre_color}= | Policer Classify Get Precolor | exceed_color
| | Vpp Configures Classify Session L3 | ${dut1} | permit | ${table_idx}
| | ... | ${skip_n} | ${match_n} | ip6 | dst | 2001:2::2
| | ... | hit_next_index=${policer_index} | opaque_index=${pre_color}
| | Policer Classify Set Interface | ${dut1} | ${DUT1_${int}1}[0]
| | ... | ip6_table_index=${table_idx}
| |
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${DUT2_${int}2}[0]
| | ... | ELSE | Set Variable | ${DUT1_${int}2}[0]
| |
| | ${policer_index}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Policer Set Configuration | ${dut} | policer2 | ${cir}
| | ... | ${eir} | ${cb} | ${eb} | pps | Closest | 2R3C_RFC_2698 | Transmit
| | ... | Mark_and_Transmit | Transmit | ${t} | exceed_dscp=${dscp}
| | ... | ELSE | Set Variable | ${policer_index}
| | ${table_idx} | ${skip_n} | ${match_n}=
| | ... | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Creates Classify Table L3
| | ... | ${dut} | ip6 | dst | ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
| | ... | ELSE | Set Variable | ${table_idx} | ${skip_n} | ${match_n}
| | Vpp Configures Classify Session L3 | ${dut} | permit | ${table_idx}
| | ... | ${skip_n} | ${match_n} | ip6 | dst | 2001:1::2
| | ... | hit_next_index=${policer_index} | opaque_index=${pre_color}
| | Policer Classify Set Interface | ${dut} | ${dut_if2}
| | ... | ip6_table_index=${table_idx}

| Show Classify Tables Verbose on all DUTs
| | [Documentation] | Show classify tables verbose on all DUT nodes in topology.
| |
| | ... | *Arguments:*
| | ... | - nodes - Topology. Type: dictionary
| |
| | ... | *Example:*
| |
| | ... | \| Show Classify Tables Verbose on all DUTs \| ${nodes} \|
| |
| | [Arguments] | ${nodes}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Show Classify Tables Verbose | ${nodes['${dut}']}
| | END
