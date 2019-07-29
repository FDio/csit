# Copyright (c) 2019 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.GBP
| ...
| Documentation | GBP keywords

*** Keywords ***
| Initialize GBP routing domains on node
| | [Documentation]
| | ... | Initialize GBP routing domains on node.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT node. Type: string
| | ... | - count - Number of baseline interface variables. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize GBP routing domains on node \| DUT1 \| 1 \|
| | ...
| | [Arguments] | ${dut} | ${count}=${1}
| | ...
| | ${dut_str}= | Convert To Lowercase | ${dut}
| | :FOR | ${id} | IN RANGE | 1 | ${count} + 1
| | | ${dut_lo}= | VPP Create Loopback | ${nodes['${dut}']}
| | | ... | mac=ba:dc:00:ff:ee:01
| | | Set Interface State
| | | ... | ${nodes['${dut}']} | ${dut_lo} | up
| | | Add Fib Table
| | | ... | ${nodes['${dut}']} | ${id}
| | | GBP Route Domain Add
| | | ... | ${nodes['${dut}']} | rd_id=${id}
| | | Assign Interface To Fib Table
| | | ... | ${nodes['${dut}']} | ${dut_lo} | ${id}
| | | Create L2 BD
| | | ... | ${nodes['${dut}']} | ${id} | arp_term=${1}
| | | GBP Bridge Domain Add
| | | ... | ${nodes['${dut}']} | ${dut_lo} | bd_id=${id}
| | | GBP Endpoint Group Add
| | | ... | ${nodes['${dut}']} | bd_id=${id} | rd_id=${id}
| | | Configure IP addresses on interfaces
| | | ... | ${nodes['${dut}']} | ${dut_lo} | 10.10.10.1 | 24
| | | GBP Subnet Add Del
| | | ... | ${nodes['${dut}']} | 10.10.10.0 | 24 | bd_id=${id} | sclass=${100}
| | | GBP Ext Itf Add Del
| | | ... | ${nodes['${dut}']} | ${dut_lo} | bd_id=${id} | rd_id=${id}
| | | GBP Endpoint Add
| | | ... | ${nodes['${dut}']} | ${${dut_str}_dot1q_${id}_1} | 10.10.10.2
| | | ... | ${${dut_str}_if1_mac} | sclass=${100}
| | | GBP Endpoint Add
| | | ... | ${nodes['${dut}']} | ${${dut_str}_dot1q_${id}_1} | 10.10.10.3
| | | ... | ${${dut_str}_if2_mac} | sclass=${100}
| | | VPP Route Add
| | | ... | ${nodes['${dut}']} | 20.20.20.0 | 24 | gateway=10.10.10.2
| | | ... | interface=${dut_lo}
| | | VPP Route Add
| | | ... | ${nodes['${dut}']} | 30.30.30.0 | 24 | gateway=10.10.10.3
| | | ... | interface=${dut_lo}
| | | GBP Subnet Add Del
| | | ... | ${nodes['${dut}']} | 20.20.20.0 | 24 | bd_id=${id} | sclass=${200}
| | | GBP Subnet Add Del
| | | ... | ${nodes['${dut}']} | 30.30.30.0 | 24 | bd_id=${id} | sclass=${300}
| | | Add Replace Acl Multi Entries
| | | ... | ${nodes['${dut}']}
| | | ... | rules="ipv4 permit src 0.0.0.0/0 dst 0.0.0.0/0 proto 61"
| | | ... | tag="gbp-permit-200-300"
| | | GBP Contract Add Del
| | | ... | ${nodes['${dut}']} | ${0} | ${200} | ${300}

| Initialize GBP routing domains
| | [Documentation]
| | ... | Initialize GBP routing domains on all DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - count - Number of GBP routing domains. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Initialize GBP routing domains \| 1 \|
| | ...
| | [Arguments] | ${count}=${1}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Initialize GBP routing domains on node | ${dut} | count=${count}
| | Set interfaces in path up
