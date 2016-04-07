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
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.DUTSetup
| Library | resources.libraries.python.TGSetup
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

| Setup '${m}' worker threads and rss '${n}' without HTT on all DUTs
| | [Documentation] |  Setup M worker threads without HTT and rss N in startup
| | ...             |  configuration of VPP on all DUTs
| | ${cpu}= | Catenate | main-core | 0 | corelist-workers
| | ${cpu}= | Run Keyword If | '${m}' == '1' | Catenate | ${cpu} | 1
| | ...     | ELSE IF        | '${m}' == '2' | Catenate | ${cpu} | 1-2
| | ...     | ELSE IF        | '${m}' == '4' | Catenate | ${cpu} | 1-4
| | ...     | ELSE IF        | '${m}' == '6' | Catenate | ${cpu} | 1-6
| | ...     | ELSE           | Fail | Not supported combination
| | ${rss}= | Catenate | rss | ${n}
| | Setup worker threads and rss on all DUTs | ${cpu} | ${rss}

| Setup '${m}' worker threads and rss '${n}' with HTT on all DUTs
| | [Documentation] |  Setup M worker threads with HTT and rss N in startup
| | ...             |  configuration of VPP on all DUTs
| | ${cpu}= | Catenate | main-core | 0 | corelist-workers
| | ${cpu}= | Run Keyword If | '${m}' == '2' | Catenate | ${cpu} | 1,10
| | ...     | ELSE IF        | '${m}' == '4' | Catenate | ${cpu} | 1-2,10-11
| | ...     | ELSE IF        | '${m}' == '6' | Catenate | ${cpu} | 1-3,10-12
| | ...     | ELSE IF        | '${m}' == '8' | Catenate | ${cpu} | 1-4,10-13
| | ...     | ELSE           | Fail | Not supported combination
| | ${rss}= | Catenate | rss | ${n}
| | Setup worker threads and rss on all DUTs | ${cpu} | ${rss}

| Setup worker threads and rss on all DUTs
| | [Documentation] |  Setup worker threads and rss in startup configuration of
| | ...             |  VPP on all DUTs
| | [Arguments] | ${cpu} | ${rss}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Add CPU config | ${nodes['${dut}']}
| | | ...            | ${cpu}
| | | Add PCI device | ${nodes['${dut}']}
| | | Add RSS config | ${nodes['${dut}']}
| | | ...            | ${rss}
| | | Apply config | ${nodes['${dut}']}

| Reset startup configuration of VPP on all DUTs
| | [Documentation] | Reset startup configuration of VPP on all DUTs
| | ${cpu}= | Catenate | main-core | 1
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Remove All PCI Devices | ${nodes['${dut}']}
| | | Remove All CPU Config | ${nodes['${dut}']}
| | | Remove Socketmem Config | ${nodes['${dut}']}
| | | Remove Heapsize Config | ${nodes['${dut}']}
| | | Remove RSS Config | ${nodes['${dut}']}
| | | Add CPU Config | ${nodes['${dut}']}
| | | ...            | ${cpu}
| | | Add PCI Device | ${nodes['${dut}']}
| | | Apply Config | ${nodes['${dut}']}

