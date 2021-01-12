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
| Documentation | IACL keywords.


*** Keywords ***

#code for Ip4
| Configure IPv4 IACLs
| | ${table_idx} | ${skip_n} | ${match_n}= | And Vpp Creates Classify Table L3
| | ... | ${dut1} | ip4 | dst | 255.255.255.255
| | And Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip4 | dst
| | ... | 20.20.20.2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ip4 | ${table_idx}
| | Then Send packet and verify headers
| | ... | ${tg} | 10.10.10.2 | 20.20.20.2
| | ... | ${TG_pf1}[0] | ${TG_pf1_mac}[0] | ${DUT1_vf1_mac}[0]
| | ... | ${TG_pf2}[0] | ${DUT1_vf2_mac}[0] | ${TG_pf2_mac}[0]

#performance test ip4 iacl

| Configure IPv4 IACLs
| | ${table_idx} | ${skip_n} | ${match_n}= | And Vpp Creates Classify Table L3
| | ... | ${dut1} | ip4 | dst | 255.255.255.0
| | And Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip4 | dst
| | ... | 20.20.20.0
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ip4 | ${table_idx}
| | And Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip4 | dst
| | ... | 10.10.10.0
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ip4 | ${table_idx}

#performance test ip4 10ge2p1x710
| Configure IPv4 IACLs
| | ${table_idx} | ${skip_n} | ${match_n}= | And Vpp Creates Classify Table L3
| | ... | ${dut1} | ip4 | dst | 255.255.255.0
| | And Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip4 | dst
| | ... | 20.20.20.0
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ip4 | ${table_idx}
| | ${table_idx} | ${skip_n} | ${match_n}= | And Vpp Creates Classify Table L3
| | ... | ${dut2} | ip4 | dst | 255.255.255.0
| | And Vpp Configures Classify Session L3
| | ... | ${dut2} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip4 | dst
| | ... | 10.10.10.0
| | And Vpp Enable Input Acl Interface
| | ... | ${dut2} | ${DUT2_${int}2}[0] | ip4 | ${table_idx}


#IP6


#performance test IP6
| Configure IPv6 IACLs
| | ${table_idx} | ${skip_n} | ${match_n}= | And Vpp Creates Classify Table L3
| | ... | ${dut1} | ip6 | dst | ffff:ffff:ffff:ffff:ffff:ffff:ffff:0
| | And Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip6 | dst
| | ... | 2001:2::0
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ip6 | ${table_idx}
| | And Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip6 | dst
| | ... | 2001:1::0
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${DUT1_${int}2}[0] | ip6 | ${table_idx}

#code for IP6
| Configure IPv6 IACLs
| | ${table_idx} | ${skip_n} | ${match_n}= | And Vpp Creates Classify Table L3
| | ... | ${dut1} | ip6 | dst | ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
| | And Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip6 | dst
| | ... | 2001:2::2
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ip6 | ${table_idx}
| | Then Send packet and verify headers
| | ... | ${tg} | 2001:1::2 | 2001:2::2
| | ... | ${TG_pf1}[0] | ${TG_pf1_mac}[0] | ${DUT1_vf1_mac}[0]
| | ... | ${TG_pf2}[0] | ${DUT1_vf2_mac}[0] | ${TG_pf2_mac}[0]

#performance test ip6 10ge2p1x710
| Configure IPv6 IACLs
| | ${table_idx} | ${skip_n} | ${match_n}= | And Vpp Creates Classify Table L3
| | ... | ${dut1} | ip6 | dst | ffff:ffff:ffff:ffff:ffff:ffff:ffff:0
| | And Vpp Configures Classify Session L3
| | ... | ${dut1} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip6 | dst
| | ... | 2001:2::0
| | And Vpp Enable Input Acl Interface
| | ... | ${dut1} | ${DUT1_${int}1}[0] | ip6 | ${table_idx}
| | ${table_idx} | ${skip_n} | ${match_n}= | And Vpp Creates Classify Table L3
| | ... | ${dut2} | ip6 | dst | ffff:ffff:ffff:ffff:ffff:ffff:ffff:0
| | And Vpp Configures Classify Session L3
| | ... | ${dut2} | permit | ${table_idx} | ${skip_n} | ${match_n} | ip6 | dst
| | ... | 2001:1::0
| | And Vpp Enable Input Acl Interface
| | ... | ${dut2} | ${DUT2_${int}2}[0] | ip6 | ${table_idx}