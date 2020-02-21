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
| Library | resources.tools.wrk.wrk
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.DUTSetup
| Library | resources.libraries.python.TrafficGenerator
| Library | resources.libraries.python.topology.Topology
|
| Documentation | L2 keywords to set up wrk and to measure performance
| ... | parameters using wrk.

*** Variables ***
| ${wrk_ip_prefix}= | 24
| @{wrk_ip_addrs}= | 192.168.10.1 | 192.168.20.1 | 192.168.30.1
| ... | 192.168.40.1 | 192.168.50.1 | 192.168.60.1 | 192.168.70.1
| ... | 192.168.80.1

*** Keywords ***
| Measure throughput
| | [Documentation]
| | ... | Measure throughput using wrk.
| |
| | ... | *Arguments:*
| | ... | - ${profile} - The name of the wrk traffic profile defining the
| | ... | traffic. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Measure throughput \| wrk-bw-1url-1core-50con \|
| |
| | [Arguments] | ${profile}
| |
| | ${tg_numa}= | Get interfaces numa node | ${tg} | ${TG_pf1}[0] | ${TG_pf2}[0]
| | ${output}= | Run wrk | ${tg} | ${profile} | ${tg_numa} | bw
| | Set test message | ${output}

| Measure requests per second
| | [Documentation]
| | ... | Measure number of requests per second using wrk.
| |
| | ... | *Arguments:*
| | ... | - ${profile} - The name of the wrk traffic profile defining the
| | ... | traffic. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Measure requests per second \| wrk-bw-1url-1core-50con \|
| |
| | [Arguments] | ${profile}
| |
| | ${tg_numa}= | Get interfaces numa node | ${tg} | ${TG_pf1}[0] | ${TG_pf2}[0]
| | ${output}= | Run wrk | ${tg} | ${profile} | ${tg_numa} | rps
| | Set test message | ${output}

| Measure connections per second
| | [Documentation]
| | ... | Measure number of connections per second using wrk.
| |
| | ... | *Arguments:*
| | ... | - ${profile} - The name of the wrk traffic profile defining the
| | ... | traffic. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Measure connections per second \| wrk-bw-1url-1core-50con \|
| |
| | [Arguments] | ${profile}
| |
| | ${tg_numa}= | Get interfaces numa node | ${tg} | ${TG_pf1}[0] | ${TG_pf2}[0]
| | ${output}= | Run wrk | ${tg} | ${profile} | ${tg_numa} | cps
| | Set test message | ${output}
