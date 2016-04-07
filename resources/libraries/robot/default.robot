# Copyright (c) 2016 Cisco and/or its affiliates.
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
| Variables | resources/libraries/python/topology.py
| Library | resources/libraries/python/DUTSetup.py
| Library | resources/libraries/python/TGSetup.py
| Library | resources/libraries/python/VppConfigGenerator.py
| Library | Collections

*** Keywords ***
| Setup all DUTs before test
| | [Documentation] | Setup all DUTs in topology before test execution
| | Setup All DUTs | ${nodes}

| Setup all TGs before traffic script
| | [Documentation] | Prepare all TGs before traffic scripts execution
| | All TGs Set Interface Default Driver | ${nodes}

| Show statistics on all DUTs
| | [Documentation] | Show VPP statistics on all DUTs after the test failed
| | Sleep | 10 | Waiting for statistics to be collected
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Vpp show stats | ${nodes['${dut}']}

| Setup '${wt}' worker threads and rss '${rss}' without HTT on all DUTs
| | [Documentation] |  Setup N worker threads and rss M in startup
| | ...             |  configuration of VPP on all DUTs
| | ${cpu}= | Run Keyword If | '${wt}' == '1' | Catenate | main-core | 0 |
| |                                           | ...      | corelist-workers | 1
| | ...     | ELSE IF        | '${wt}' == '2' | Catenate | main-core | 0 |
| |                                           | ...      | corelist-workers | 1-2
| | ...     | ELSE IF        | '${wt}' == '4' | Catenate | main-core | 0 |
| |                                           | ...      | corelist-workers | 1-4
| | ...     | ELSE           | Catenate | main-core | 1
| | ${rss=} | Run Keyword If | '${rss}' == '1' | Catenate | rss | 1
| | ...     | ELSE IF        | '${rss}' == '2' | Catenate | rss | 2
| | ...     | ELSE IF        | '${rss}' == '3' | Catenate | rss | 3
| | ...     | ELSE IF        | '${rss}' == '4' | Catenate | rss | 4
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Add CPU configuration into startup configuration on DUT | ${nodes['${dut}']}
| | | ...                                                     | ${cpu}
| | | Add PCI configuration into startup configuration on DUT | ${nodes['${dut}']}
#| | |  Apply startup configuration on DUT | ${nodes['${dut}']}

| Add CPU configuration into startup configuration on DUT
| | [Arguments] | ${node} | ${cpu}
| | Add cpu config | ${node} | ${cpu}

| Add PCI configuration into startup configuration on DUT
| | [Arguments] | ${node}
| | Add pci device | ${node}

| Apply startup configuration on DUT
| | [Arguments] | ${node}
| | Add pci device | ${node}
