# Copyright (c) 2015 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Library | resources/libraries/python/VatExecutor.py
| Library | resources/libraries/python/TrafficGenerator.py
| Force Tags | topo-3node
| Test Setup | Setup all DUTs before test

*** Test Cases ***
| VPP passes traffic through L2 cross connect
| | Given L2 xconnect initialized in topology
| | Then Traffic should pass with no loss | 10 | 10 | 512

*** Keywords ***
| L2 xconnect initialized in topology
| | Setup L2 xconnect | ${nodes['DUT1']} | port1 | port2
| | Setup L2 xconnect | ${nodes['DUT2']} | port1 | port2


| Setup L2 xconnect | [Arguments] | ${node} | ${src_port} | ${dst_port}
| | Execute script | l2xconnect.vat | ${node}
| | Script should have passed


| Traffic should pass with no loss
| | [Arguments] | ${duration} | ${rate} | ${framesize}
| | Send traffic on | ${nodes['TG']} | port1 | port2 | ${duration}
| | ...             | ${rate} | ${framesize}
| | No traffic loss occured
