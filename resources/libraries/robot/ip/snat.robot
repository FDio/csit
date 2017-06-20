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
| Configure inside and outside interfaces
| | [Documentation] | Configure inside and outside interfaces for SNAT.
| | ...
| | ... | *Arguments:*
| | ... | - node - DUT node to set SNAT interfaces on. Type: dictionary
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
| | Set SNAT Interfaces | ${node} | ${int_in_name} | ${int_out_name}

| Configure deterministic mode for SNAT
| | [Documentation] | Set deterministic behaviour of SNAT.
| | ...
| | ... | *Arguments:*
| | ... | - node - DUT node to set deterministic mode for SNAT on.
| | ... | Type: dictionary
| | ... | - ip_in - Inside IP. Type: string
| | ... | - subnet_in - Inside IP subnet. Type: string
| | ... | - ip_out - Outside IP. Type: string
| | ... | - subnet_out - Outside IP subnet. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure deterministic mode for SNAT \| ${nodes['DUT1']} \
| | ... | \| 100.0.0.0 \| 12 \| 12.1.1.0 \| 24 \|
| | ...
| | [Arguments] | ${node} | ${ip_in} | ${subnet_in} | ${ip_out} | ${subnet_out}
| | ...
| | Set SNAT deterministic | ${node} | ${ip_in} | ${subnet_in} | ${ip_out}
| | ... | ${subnet_out}

| Configure workers for SNAT
| | [Documentation] | Configure workers for SNAT.
| | ...
| | ... | *Arguments:*
| | ... | - node - DUT node to set SNAT workers on. Type: dictionary
| | ... | - lcores - list of cores, format: range e.g. 1-5 or list of ranges \
| | ... | e.g.: 1-5,18-22. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure workers for SNAT \| ${nodes['DUT1']} \| 12-23,36-47 \|
| | ...
| | [Arguments] | ${node} | ${lcores}
| | ...
| | Set SNAT workers | ${node} | ${lcores}

| Show SNAT verbose
| | [Documentation] | Get the SNAT settings on the node.
| | ...
| | ... | *Arguments:*
| | ... | - node - DUT node to show SNAT. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Show SNAT verbose \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | Show SNAT | ${node}

| Get SNAT deterministic forward
| | [Documentation] | Show forward IP address and port(s).
| | ...
| | ... | *Arguments:*
| | ... | - node - DUT node to get SNAT deterministic forward on.
| | ... | Type: dictionary
| | ... | - ip - IP address. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Get SNAT deterministic forward \| ${nodes['DUT1']} \| 10.0.0.2 \|
| | ...
| | [Arguments] | ${node} | ${ip}
| | ...
| | Show SNAT deterministic forward | ${node} | ${ip}

| Get SNAT deterministic reverse
| | [Documentation] | Show reverse IP address.
| | ...
| | ... | *Arguments:*
| | ... | - node - DUT node to get SNAT deterministic reverse on.
| | ... | Type: dictionary
| | ... | - ip - IP address. Type: string
| | ... | - port - Port. Type: string or integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Get SNAT deterministic reverse \| ${nodes['DUT1']} \| 10.0.0.2 \
| | ... | \| 1025 \|
| | ...
| | [Arguments] | ${node} | ${ip} | ${port}
| | ...
| | Show SNAT deterministic reverse | ${node} | ${ip} | ${port}

| Get NAT interfaces
| | [Documentation] | Get list of interfaces configured with NAT from VPP node.
| | ...
| | ... | *Arguments:*
| | ... | - node - DUT node to get SNAT interfaces on. Type: dictionary
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
| | ... | - node - DUT node to get SNAT static mappings on. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Get NAT static mappings \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | VPP get NAT static mappings | ${node}
