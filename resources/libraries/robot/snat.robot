# Copyright (c) 2017 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.SNATUtil
| Library | resources.libraries.python.NAT.NATUtil
| Documentation | Keywords for SNAT feature in VPP.

*** Keywords ***
| Set inside and outside interfaces
| | [Documentation] | Set inside and outside interfaces for SNAT.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - int_in - Inside interface. Type: string
| | ... | - int_out - Outside interface. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set inside and outside interfaces \| ${nodes['DUT1']} \
| | ... | \| FortyGigabitEtherneta/0/0 \| FortyGigabitEtherneta/0/1 \|
| | ...
| | [Arguments] | ${node} | ${int_in} | ${int_out}
| | ...
| | Set SNAT Interfaces | ${node} | ${int_in} | ${int_out}

| Set deterministic mode for SNAT
| | [Documentation] | Set deterministic behaviour of SNAT.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - ip_in - Inside IP. Type: string
| | ... | - range_in - Inside IP range. Type: string
| | ... | - ip_out - Outside IP. Type: string
| | ... | - range_out - Outside IP range. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set deterministic mode for SNAT \| ${nodes['DUT1']} \
| | ... | \| 100.0.0.0 \| 12 \| 12.1.1.0 \| 24 \|
| | ...
| | [Arguments] | ${node} | ${ip_in} | ${range_in} | ${ip_out} | ${range_out}
| | ...
| | Set SNAT deterministic | ${node} | ${ip_in} | ${range_in} | ${ip_out}
| | ... | ${range_out}

| Set workers for SNAT
| | [Documentation] | Set workers for SNAT.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - lcores - list of cores, format: range e.g. 1-5 or list of ranges \
| | ... | e.g.: 1-5,18-22. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set workers for SNAT \| ${nodes['DUT1']} \| 12-23,36-47 \|
| | ...
| | [Arguments] | ${node} | ${lcores}
| | ...
| | Set SNAT workers | ${node} | ${lcores}

| Get NAT interfaces
| | [Documentation] | Get list of interfaces configured with NAT from VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Get NAT interfaces \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | VPP get NAT interfaces | ${node}

| Get NAT static mappings
| | [Documentation] | Get NAT static mappings from VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Get NAT static mappings \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | VPP get NAT static mappings] | ${node}

| SNAT is initialized in a 3-node circular topology for performance test
| | [Documentation] | Initialization of 3-node topology with SNAT between DUTs:
| | ... | - set interfaces up
| | ... | - set IP addresses
| | ... | - set ARP
| | ... | - create routes
| | ... | - set SNAT
| | ... | - write the debug info to log - NAT interfaces and NAT static \
| | ... | mappings for both DUTs.
| | ...
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | Set Interface State | ${dut1} | ${dut1_if2} | up
| | Set Interface State | ${dut2} | ${dut2_if1} | up
| | Set Interface State | ${dut2} | ${dut2_if2} | up
| | All Vpp Interfaces Ready Wait | ${nodes}
| | ...
| | IP addresses are set on interfaces | ${dut1} | ${dut1_if1} | 10.0.0.1 | 20
| | IP addresses are set on interfaces | ${dut1} | ${dut1_if2} | 10.0.0.2 | 20
| | IP addresses are set on interfaces | ${dut2} | ${dut2_if1} | 12.1.1.1 | 32
| | IP addresses are set on interfaces | ${dut2} | ${dut2_if2} | 40.1.1.2 | 32
| | ...
| | ${tg_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ${dut2_if1_mac}= | Get Interface MAC | ${dut2} | ${dut2_if1}
| | Add arp on dut | ${dut1} | ${dut1_if1} | 10.0.0.3 | ${tg_if1_mac}
| | Add arp on dut | ${dut1} | ${dut1_if2} | 12.1.1.1 | ${dut2_if1_mac}
| | Add arp on dut | ${dut2} | ${dut2_if1} | 10.0.0.2 | ${dut1_if2_mac}
| | Add arp on dut | ${dut2} | ${dut2_if2} | 40.1.1.2 | ${tg_if2_mac}
| | ...
| | Vpp Route Add | ${dut1} | 40.1.1.0 | 24 | 12.1.1.1 | ${dut1_if2}
| | Vpp Route Add | ${dut1} | 10.0.0.0 | 20 | 10.0.0.3 | ${dut1_if1}
| | Vpp Route Add | ${dut2} | 40.1.1.0 | 24 | 40.1.1.2 | ${dut2_if2}
| | Vpp Route Add | ${dut2} | 12.1.1.1 | 32 | 10.0.0.2 | ${dut2_if1}
| | ...
| | Set inside and outside interfaces | ${dut1} | ${dut1_if2} | ${dut2_if1}
| | Set deterministic mode for SNAT | ${dut1} | 10.0.0.3 | 20 | 12.1.1.0 | 24
| | ...
| | Set inside and outside interfaces | ${dut2} | ${dut1_if2} | ${dut2_if1}
| | Set deterministic mode for SNAT | ${dut2} | 10.0.0.3 | 20 | 12.1.1.0 | 24
| | ...
| | Comment | Debug info:
| | Get NAT interfaces | ${dut1}
| | Get NAT interfaces | ${dut2}
| | Get NAT static mappings | ${dut1}
| | Get NAT static mappings | ${dut2}
