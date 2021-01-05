# Copyright (c) 2020 Intel and/or its affiliates.
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
| Library | resources.libraries.python.vsap.VSAPUtil
| Library | resources.libraries.python.vsap.NginxUtil
|
| Documentation | L2 keywords to set up VPP to test tls.

*** Variables ***
| ${dut1_ip_prefix}= | 24
| @{dut1_ip_addrs}= | 192.168.10.1

*** Keywords ***
| Set up VCL Nginx or LDP Nginx on DUT node
| | [Documentation]
| | ... | Setup for suites which uses CVL or LDP Nginx on DUT.
| |
| | ... | *Arguments:*
| | ... | - mode - VCL Nginx or LDP Nginx.
| | ... | Type: string
| | ... | - rps_cps - Test request or connect.
| | ... | Type: string
| | ... | - core_num - Nginx work processes number.
| | ... | Type: int
| | ... | - qat - Whether to use the qat engine.
| | ... | Type: string
| | ... | - tls_tcp - TLS or TCP.
| |
| | ... | *Example:*
| |
| | ... | \| Set up VCL Nginx or LDP NGINX on DUT node \| ${mode}\
| | ... | \| ${rps_cps} \| ${phy_cores} \| ${qat} \| ${tls_tcp} \|
| |
| | [Arguments] | ${mode} | ${rps_cps} | ${core_num} | ${qat} | ${tls_tcp}
| |
| | Run Keyword If | '${tls_tcp}' == 'tls'
| | ... | Stop Qat Service | ${dut1} | ${qat}
| | ... | Install Openssl3 On Duts | ${dut1} | ${packages_dir}
| | Set Interface State | ${dut1} | ${dut1_if1} | up
| | VPP Interface Set IP Address | ${dut1} | ${dut1_if1} | 192.168.10.1 | 24
| | Vpp Node Interfaces Ready Wait | ${dut1}
| | Run Keyword If | '${tls_tcp}' == 'tls'
| | ... | Restart Qat Service | ${dut1} | ${qat}
| | Run Keyword If | '${tls_tcp}' == 'tls'
| | ... | VPP TLS Openssl Set Engine | ${dut1} | ${qat}
| | Run Nginx | ${dut1} | ${mode} | ${rps_cps} | ${core_num} | ${tls_tcp}
