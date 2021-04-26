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
| Library | resources.libraries.python.NginxConfigGenerator
| Library | Collections

*** Keywords ***
| Apply startup configuration on all NGINX DUT
| | [Documentation]
| | ... | Setup for suites which uses VCL or LDP Nginx on DUT.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT node.
| | ... | Type: string
| | ... | - phy_cores - vpp used phy cores number.
| |
| | ... | *Example:*
| |
| | ... | \| startup configuration on all NGINX DUT \| ${dut} | ${phy_cores}
| |
| | [Arguments] | ${dut} | ${phy_cores}
| |
| | Import Library | resources.libraries.python.NginxConfigGenerator
| | ... | WITH NAME | nc_Manager
| | Run Keyword | nc_Manager.Set Node | ${dut}
| | Run Keyword | nc_Manager.Set Nginx Path | ${packages_dir}
| | ... | ${nginx_version}
| | Run Keyword | nc_Manager.Add Worker Processes | ${phy_cores} | ${smt_used}
| | Run Keyword | nc_Manager.Add Master Process
| | Run Keyword | nc_Manager.Add Daemon
| | Run Keyword | nc_Manager.Add Worker Rlimit Nofile
| | Run Keyword | nc_Manager.Add Events Use
| | Run Keyword | nc_Manager.Add Events Worker Connections
| | Run Keyword | nc_Manager.Add Events Accept Mutex
| | Run Keyword | nc_Manager.Add Events Multi Accept
| | Run Keyword | nc_Manager.Add Http Access Log
| | Run Keyword | nc_Manager.Add Http Include
| | Run Keyword | nc_Manager.Add Http Default Type
| | Run Keyword | nc_Manager.Add Http Sendfile
| | Run Keyword | nc_Manager.Add Http Keepalive Timeout | ${keep_time}
| | Run Keyword If | ${keep_time} > 0
| | ... | nc_Manager.Add Http Keepalive Requests | ${r_total}
| | Run Keyword | nc_Manager.Add Http Server Listen | ${listen_port}
| | Run Keyword | nc_Manager.Add Http Server Root
| | Run Keyword | nc_Manager.Add Http Server Index
| | Run Keyword | nc_Manager.Add Http Server Location | ${0}
| | Run Keyword | nc_Manager.Add Http Server Location | ${64}
| | Run Keyword | nc_Manager.Add Http Server Location | ${1024}
| | Run Keyword | nc_Manager.Add Http Server Location | ${2048}
| | Run Keyword | nc_Manager.Apply Config

