# Copyright (c) 2021 PANTHEON.tech and/or its affiliates.
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
| Documentation | IACL keywords.


*** Keywords ***
| Initialize IPv4 iACL in circular topology
| | ${table_idx} | ${skip_n} | ${match_n}= | Vpp Creates Classify Table L3
| | ... | ${dut1} | ip4 | dst | ${mask}
| | Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip4 | dst
| | ... | 20.20.20.0
| | Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ip4 | ${table_idx}
| | Run Keyword If | ${duts_count} == 1
| | ... | Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip4 | dst
| | ... | 10.10.10.0
| | ... | ELSE | ${duts_count} == 2
| | ... | ${table_idx} | ${skip_n} | ${match_n}= | Vpp Creates Classify Table L3
| | ... | ${dut2} | ip6 | dst | ${mask}
| | ... | Vpp Configures Classify Session L3 |
| | ... | ${dut2} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip4 | dst
| | ... | 10.10.10.0
| | Run Keyword If | ${duts_count} == 1
| | ... | Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ip4 | ${table_idx}
| | ... | ELSE | ${duts_count} == 2
| | ... | Vpp Enable Input Acl Interface |
| | ... | ${dut2} | ${DUT2_${int}2}[0] | ip4 | ${table_idx}

#IP6

| Initialize IPv6 iACL in circular topology
| | ${table_idx} | ${skip_n} | ${match_n}= | Vpp Creates Classify Table L3
| | ... | ${dut1} | ip6 | dst | ${mask}
| | Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip6 | dst
| | ... | 2001:2::0
| | Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ip6 | ${table_idx}
| | Run Keyword If | ${duts_count} == 1
| | ... | Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip6 | dst
| | ... | 2001:1::0
| | ... | ELSE | ${duts_count} == 2
| | ... | ${table_idx} | ${skip_n} | ${match_n}= | Vpp Creates Classify Table L3
| | ... | ${dut2} | ip6 | dst | ${mask}
| | ... | Vpp Configures Classify Session L3
| | ... | ${dut2} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip6 | dst
| | ... | 2001:1::0
| | Run Keyword If | ${duts_count} == 1
| | ... | Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ip6 | ${table_idx}
| | ... | ELSE | ${duts_count} == 2
| | ... | ${dut2} | ip6 | dst | ${mask}
| | ... | Vpp Enable Input Acl Interface
| | ... | ${dut2} | ${DUT2_${int}2}[0] | ip6 | ${table_idx}


