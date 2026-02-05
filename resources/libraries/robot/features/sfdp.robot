# Copyright (c) 2026 Cisco and/or its affiliates.
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
| | ${log2} = | Evaluate | int(math.ceil(math.log(${sessions})/math.log(2))) | modules=math
| | # With p63 this will be 98.4% utilization. Too high for bihash.
| | # With two sibling workers, ~75% utilization of per-thread cache
| | # is maybe enough, but this keyword should support also ht_off testbeds.
| | ${log2} = | Evaluate | ${log2} + 1
| | FOR | ${dut} | IN | @{duts}
| | | Import Library | resources.libraries.python.VppConfigGenerator
| | | ... | WITH NAME | ${dut}
| | | Run Keyword | ${dut}.Add Sfdp Log2 Sessions | ${log2}
| | | Run Keyword | ${dut}.Add Sfdp Log2 Sessions Cache Per Thread | ${log2}
| | END

| Initialize SFDP Services
| | [Documentation]
| | ... | FIXME!
| |
| | [Arguments] | ${services} | ${remote_host1_ip}=${NONE} | ${remote_host2_ip}=${NONE}
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
| | Set Sfdp Services | ${dut} | ${services}
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
| |
| | ${resetter} = | Create SFDP Resetter | ${dut}
| | #${ramp_up_rate} = | Get Ramp Up Rate
| | #Return From Keyword If | ${ramp_up_rate}
| | Set Test Variable | \${resetter}
