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
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/port_mirroring.robot
| Resource | resources/libraries/robot/honeycomb/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
# Test suite out of date since https://gerrit.fd.io/r/4272
# | Force Tags | honeycomb_sanity
| Suite Setup | Add Interface local0 To Topology | ${node}
| Suite Teardown | Run Keyword If Any Tests Failed
| | ... | Restart Honeycomb and VPP | ${node}
| Documentation | *Honeycomb port mirroring test suite.*

*** Variables ***
| ${interface1}= | ${node['interfaces']['port1']['name']}
| ${interface2}= | ${node['interfaces']['port3']['name']}
| ${interface3}= | local0

*** Test Cases ***
# TODO: Add verification once operational data is available (HONEYCOMB-306)
| TC01: Honeycomb can configure SPAN on an interface
| | [Documentation] | Honeycomb configures SPAN on interface and verifies/
| | ... | against VPP SPAN dump.
| | Given SPAN configuration from VAT should not exist
| | ... | ${node}
| | When Honeycomb Configures SPAN on interface
| | ... | ${node} | ${interface1} | ${interface2}
| | Then Interface SPAN configuration from VAT should be
| | ... | ${node} | ${interface1} | ${interface2}

| TC02: Honeycomb can disable SPAN on interface
| | [Documentation] | Honeycomb removes existing SPAN configuration\
| | ... | on interface and verifies against VPP SPAN dump.
| | Given Interface SPAN configuration from VAT should be
| | ... | ${node} | ${interface1} | ${interface2}
| | When Honeycomb removes interface SPAN configuration
| | ... | ${node} | ${interface1}
| | Then SPAN configuration from VAT should not exist
| | ... | ${node}

| TC03: Honeycomb can configure SPAN on one interface to mirror two interfaces
| | [Documentation] | Honeycomb configures SPAN on interface, mirroring\
| | ... | two interfaces at the same time. Then verifies against VPP SPAN dump.
| | [Teardown] | Honeycomb removes interface SPAN configuration
| | ... | ${node} | ${interface1}
| | Given SPAN configuration from VAT should not exist
| | ... | ${node}
| | When Honeycomb Configures SPAN on interface
| | ... | ${node} | ${interface1} | ${interface2} | ${interface3}
| | Then Interface SPAN configuration from VAT should be
| | ... | ${node} | ${interface1} | ${interface2} | ${interface3}
