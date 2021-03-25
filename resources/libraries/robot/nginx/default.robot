# Copyright (c) 2021 Intel and/or its affiliates.
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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.NginxUtil
| Library | Collections

*** Keywords ***
| Apply startup configuration on all NGINX DUT
| | [Documentation]
| | ... | Setup for suites which uses VCL or LDP Nginx on DUT.
| |
| | ... | *Arguments:*
| | ... | - mode - VCL Nginx or LDP Nginx.
| | ... | Type: string
| | ... | - rps_cps - Test request or connect.
| | ... | Type: string
| | ... | - phy_cores - Nginx work processes number.
| | ... | Type: string
| | ... | - tls_tcp - TLS or TCP.
| | ... | Type: string
| | ... | - cpu_idle_str - cpu idle str
| |
| | ... | *Example:*
| |
| | ... | \| startup configuration on all NGINX DUT \| ${mode}\
| | ... | \| ${rps_cps} \| ${phy_cores} \| ${tls_tcp} \| ${cpu_idle_str} \|
| |
| | [Arguments] | ${mode} | ${rps_cps} | ${phy_cores} | ${tls_tcp}
| | ... | ${cpu_idle_str}
| |
| | Set Nginx Worker Processes | ${dut1} | ${phy_cores} |
| | Set Nginx Keepalive Timeout | ${dut1} | ${rps_cps} |
| | Set Nginx listen Port | ${dut1} | ${tls_tcp} |
| | Nginx Start | ${dut1} | ${mode} |
| | Taskset Idle Cores To Nginx Pid | ${dut1} | ${cpu_idle_str} |


