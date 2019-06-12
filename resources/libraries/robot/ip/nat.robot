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
| Library | resources.libraries.python.NATUtil
| Documentation | Keywords for NAT feature in VPP.

*** Keywords ***
| Configure inside and outside interfaces
| | [Documentation] | Configure inside and outside interfaces for NAT44.
| | ...
| | ... | *Arguments:*
| | ... | - node - DUT node to set NAT44 interfaces on. Type: dictionary
| | ... | - int_in - Inside interface. Type: string
| | ... | - int_out - Outside interface. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure inside and outside interfaces \| ${nodes['DUT1']} \
| | ... | \| FortyGigabitEtherneta/0/0 \| FortyGigabitEtherneta/0/1 \|
| | ...
| | [Arguments] | ${node} | ${int_in} | ${int_out}
| | ...
| | ${int_in_name}= | Set variable | ${node['interfaces']['${int_in}']['name']}
| | ${int_out_name}= | Set variable | ${node['interfaces']['${int_out}']['name']}
| | Set NAT44 Interfaces | ${node} | ${int_in_name} | ${int_out_name}

| Configure deterministic mode for NAT44
| | [Documentation] | Set deterministic behaviour of NAT44.
| | ...
| | ... | *Arguments:*
| | ... | - node - DUT node to set deterministic mode for NAT44 on.
| | ... | Type: dictionary
| | ... | - ip_in - Inside IP. Type: string
| | ... | - subnet_in - Inside IP subnet. Type: string
| | ... | - ip_out - Outside IP. Type: string
| | ... | - subnet_out - Outside IP subnet. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure deterministic mode for NAT44 \| ${nodes['DUT1']} \
| | ... | \| 100.0.0.0 \| 12 \| 12.1.1.0 \| 24 \|
| | ...
| | [Arguments] | ${node} | ${ip_in} | ${subnet_in} | ${ip_out} | ${subnet_out}
| | ...
| | Set NAT44 deterministic | ${node} | ${ip_in} | ${subnet_in} | ${ip_out}
| | ... | ${subnet_out}

| Show NAT verbose
| | [Documentation] | Get the NAT settings on the node.
| | ...
| | ... | *Arguments:*
| | ... | - node - DUT node to show NAT. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Show NAT verbose \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | Show NAT | ${node}
