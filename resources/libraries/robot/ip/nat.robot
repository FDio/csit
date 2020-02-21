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
| Library | resources.libraries.python.NATUtil
|
| Documentation | Keywords for NAT feature in VPP.

*** Keywords ***
| Configure inside and outside interfaces
| | [Documentation] | Configure inside and outside interfaces for NAT44.
| |
| | ... | *Arguments:*
| | ... | - node - DUT node to set NAT44 interfaces on. Type: dictionary
| | ... | - int_in - Inside interface. Type: string
| | ... | - int_out - Outside interface. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Configure inside and outside interfaces \| ${nodes['DUT1']} \
| | ... | \| FortyGigabitEtherneta/0/0 \| FortyGigabitEtherneta/0/1 \|
| |
| | [Arguments] | ${node} | ${int_in} | ${int_out}
| |
| | ${int_in_name}= | Set variable | ${node['interfaces']['${int_in}']['name']}
| | ${int_out_name}= | Set variable | ${node['interfaces']['${int_out}']['name']}
| | Set NAT44 Interfaces | ${node} | ${int_in_name} | ${int_out_name}

| Configure deterministic mode for NAT44
| | [Documentation] | Set deterministic behaviour of NAT44.
| |
| | ... | *Arguments:*
| | ... | - node - DUT node to set deterministic mode for NAT44 on.
| | ... | Type: dictionary
| | ... | - ip_in - Inside IP. Type: string
| | ... | - subnet_in - Inside IP subnet. Type: string
| | ... | - ip_out - Outside IP. Type: string
| | ... | - subnet_out - Outside IP subnet. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Configure deterministic mode for NAT44 \| ${nodes['DUT1']} \
| | ... | \| 100.0.0.0 \| 12 \| 12.1.1.0 \| 24 \|
| |
| | [Arguments] | ${node} | ${ip_in} | ${subnet_in} | ${ip_out} | ${subnet_out}
| |
| | Set NAT44 deterministic | ${node} | ${ip_in} | ${subnet_in} | ${ip_out}
| | ... | ${subnet_out}

| Show NAT verbose
| | [Documentation] | Get the NAT settings on the node.
| |
| | ... | *Arguments:*
| | ... | - node - DUT node to show NAT. Type: dictionary
| |
| | ... | *Example:*
| |
| | ... | \| Show NAT verbose \| ${nodes['DUT1']} \|
| |
| | [Arguments] | ${node}
| |
| | Show NAT | ${node}

| Initialize NAT44 in circular topology
| | [Documentation] | Initialization of 2-node / 3-node topology with NAT44
| | ... | between DUTs:
| | ... | - set interfaces up
| | ... | - set IP addresses
| | ... | - set ARP
| | ... | - create routes
| | ... | - set NAT44 - only on DUT1
| |
| | ${dut2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${dut2}
| |
| | Set interfaces in path up
| |
| | VPP Interface Set IP Address | ${dut1} | ${DUT1_${int}1}[0] | 10.0.0.1 | 20
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut1} | ${DUT1_${int}2}[0]
| | ... | 11.0.0.1 | 20
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Interface Set IP Address | ${dut2} | ${DUT2_${int}1}[0]
| | ... | 11.0.0.2 | 20
| | ${dut}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${dut2}
| | ... | ELSE | Set Variable | ${dut1}
| | ${dut_if2}= | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Set Variable | ${DUT2_${int}1}[0]
| | ... | ELSE | Set Variable | ${DUT1_${int}2}[0]
| | VPP Interface Set IP Address | ${dut} | ${dut_if2} | 12.0.0.1 | 20
| |
| | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}1}[0] | 10.0.0.2 | ${TG_pf1_mac}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut1} | ${DUT1_${int}2}[0] | 11.0.0.2 | ${DUT2_${int}1_mac}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | VPP Add IP Neighbor
| | ... | ${dut2} | ${DUT2_${int}1}[0] | 11.0.0.1 | ${DUT1_${int}2_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut} | ${dut_if2} | 12.0.0.2 | ${TG_pf2_mac}[0]
| |
| | Vpp Route Add | ${dut1} | 20.0.0.0 | 18 | gateway=10.0.0.2
| | ... | interface=${DUT1_${int}1}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut1} | 12.0.0.2 | 32 | gateway=11.0.0.2
| | ... | interface=${DUT1_${int}2}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 12.0.0.0 | 24 | gateway=12.0.0.2
| | ... | interface=${DUT2_${int}2}[0]
| | Run Keyword If | '${dut2_status}' == 'PASS'
| | ... | Vpp Route Add | ${dut2} | 200.0.0.0 | 30 | gateway=11.0.0.1
| | ... | interface=${DUT2_${int}1}[0]
| |
| | Configure inside and outside interfaces
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ${DUT1_${int}2}[0]
| | Configure deterministic mode for NAT44
| | ... | ${dut1} | 20.0.0.0 | 18 | 200.0.0.0 | 30
