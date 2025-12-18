# Copyright (c) 2025 Cisco and/or its affiliates.
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

| Documentation | SFDP keywords

*** Keywords ***
| Set SFDP Capacity For Sessions
| | [Documentation]
| | ... | FIXME!
| |
| | [Arguments] | ${sessions}
| |
| | ${log2} = | Evaluate | int(math.ceil(math.log(${sessions}))) | modules=math
| | FOR | ${dut} | IN | @{duts}
| | | Import Library | resources.libraries.python.VppConfigGenerator
| | | ... | WITH NAME | ${dut}
| | | ${dut}.Add Sfdp Log2 Sessions | ${log2}
| | | ${dut}.Add Sfdp Log2 Sessions Cache Per Thread | ${log2}
| | END

| Initialize IPv4 forwarding for SFDP
| | [Documentation]
| | ... | FIXME!
| |
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links. In case of 3-node topology setup IPv4 adresses with /30 prefix
| | ... | on DUT1-DUT2 link and set routing on both DUT nodes with prefix /24
| | ... | and next hop of neighbour DUT interface IPv4 address.
| |
| | ... | *Arguments:*
| | ... | - remote_host1_ip - IP address of remote host1 (Optional).
| | ... | Type: string
| | ... | - remote_host2_ip - IP address of remote host2 (Optional).
| | ... | Type: string
| | ... | - remote_host_mask - Mask of remote host IP addresses (Optional).
| | ... | Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Initialize IPv4 forwarding in circular topology \
| | ... | \| 192.168.0.1 \| 192.168.0.2 \| 24 \|
| |
| | [Arguments] | ${remote_host1_ip}=${NONE} | ${remote_host2_ip}=${NONE}
| | ... | ${remote_host_mask}=22
| |
| | Set interfaces in path up
| |
| | ${dut}= | Set Variable | ${dut1}
| | ${in1}= | Set Variable | ${DUT1_${int}1}[0]
| | ${in2}= | Set Variable | ${DUT1_${int}2}[0]
| | ${ix1}= | Get Interface Index | ${dut} | ${in1}
| | ${ix2}= | Get Interface Index | ${dut} | ${in2}
| |
| | VPP Add IP Neighbor
| | ... | ${dut} | ${in1} | 10.10.10.2 | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut} | ${in2} | 20.20.20.2 | ${TG_pf2_mac}[0]
| | VPP Interface Set IP Address | ${dut} | ${in1}
| | ... | 10.10.10.1 | 24
| | VPP Interface Set IP Address | ${dut} | ${in2}
| | ... | 20.20.20.1 | 24
| |
| | Add Sfdp Tenant | ${dut} | ${1}
| |
| | Set Sfdp Services Ip4 | ${dut}
| |
| | Enable Sfdp Interface Input | ${dut} | ${ix1}
| | Enable Sfdp Interface Input | ${dut} | ${ix2}
| |
| | Run Keyword If | '${remote_host1_ip}' != '${NONE}'
| | ... | Vpp Route Add | ${dut} | ${remote_host1_ip} | ${remote_host_mask}
| | ... | gateway=10.10.10.2 | interface=${in1}
| | Run Keyword If | '${remote_host2_ip}' != '${NONE}'
| | ... | Vpp Route Add | ${dut} | ${remote_host2_ip} | ${remote_host_mask}
| | ... | gateway=20.20.20.2 | interface=${in2}

| Initialize IPv4 forwarding and TCP tracking for SFDP
| | [Documentation]
| | ... | FIXME!
| |
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node / 3-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links. In case of 3-node topology setup IPv4 adresses with /30 prefix
| | ... | on DUT1-DUT2 link and set routing on both DUT nodes with prefix /24
| | ... | and next hop of neighbour DUT interface IPv4 address.
| |
| | ... | *Arguments:*
| | ... | - remote_host1_ip - IP address of remote host1 (Optional).
| | ... | Type: string
| | ... | - remote_host2_ip - IP address of remote host2 (Optional).
| | ... | Type: string
| | ... | - remote_host_mask - Mask of remote host IP addresses (Optional).
| | ... | Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Initialize IPv4 forwarding in circular topology \
| | ... | \| 192.168.0.1 \| 192.168.0.2 \| 24 \|
| |
| | [Arguments] | ${remote_host1_ip}=${NONE} | ${remote_host2_ip}=${NONE}
| | ... | ${remote_host_mask}=22
| |
| | Set interfaces in path up
| |
| | ${dut}= | Set Variable | ${dut1}
| | ${in1}= | Set Variable | ${DUT1_${int}1}[0]
| | ${in2}= | Set Variable | ${DUT1_${int}2}[0]
| | ${ix1}= | Get Interface Index | ${dut} | ${in1}
| | ${ix2}= | Get Interface Index | ${dut} | ${in2}
| |
| | VPP Add IP Neighbor
| | ... | ${dut} | ${in1} | 10.10.10.2 | ${TG_pf1_mac}[0]
| | VPP Add IP Neighbor
| | ... | ${dut} | ${in2} | 20.20.20.2 | ${TG_pf2_mac}[0]
| | VPP Interface Set IP Address | ${dut} | ${in1}
| | ... | 10.10.10.1 | 24
| | VPP Interface Set IP Address | ${dut} | ${in2}
| | ... | 20.20.20.1 | 24
| |
| | Add Sfdp Tenant | ${dut} | ${1}
| |
| | Set Sfdp Services Ip4 Tcp | ${dut}
| |
| | Enable Sfdp Interface Input | ${dut} | ${ix1}
| | Enable Sfdp Interface Input | ${dut} | ${ix2}
| |
| | Run Keyword If | '${remote_host1_ip}' != '${NONE}'
| | ... | Vpp Route Add | ${dut} | ${remote_host1_ip} | ${remote_host_mask}
| | ... | gateway=10.10.10.2 | interface=${in1}
| | Run Keyword If | '${remote_host2_ip}' != '${NONE}'
| | ... | Vpp Route Add | ${dut} | ${remote_host2_ip} | ${remote_host_mask}
| | ... | gateway=20.20.20.2 | interface=${in2}

