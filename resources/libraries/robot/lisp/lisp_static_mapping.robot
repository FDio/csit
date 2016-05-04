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
| Resource | resources/libraries/robot/interfaces.robot
| Library  | resources.libraries.python.NodePath
| Library  | resources.libraries.python.LispSetup.LispLocatorSet
| Library  | resources.libraries.python.LispSetup.LispLocator
| Library  | resources.libraries.python.LispSetup.LispLocalEid
| Library  | resources.libraries.python.LispSetup.LispRemoteMapping
| Library  | resources.libraries.python.LispSetup.LispSetup
| Library  | resources.libraries.python.LispUtil

*** Keywords ***
| Set up Lisp topology
| | [Documentation] | Set up Lisp static remote mapping topology.
| | ...
| | ... | *Arguments:*
| | ... | - ${dut1_node} - DUT1 node. Type: dictionary
| | ... | - ${dut1_int_name} - DUT1 node interface name. Type: string
| | ... | - ${dut1_int_index} - DUT1 node interface index. Type: integer
| | ... | - ${dut2_node} - DUT2 node. Type: dictionary
| | ... | - ${dut2_int_name} - DUT2 node interface name. Type: string
| | ... | - ${dut2_int_index} - DUT2 node interface index. Type: integer
| | ... | - ${duts_locator_name} - Lisp locator_set name. Type: string
| | ... | - ${duts_priority} - Lisp locator_set locator priority. Type: integer
| | ... | - ${duts_weight} - Lisp locator_set locator weight. Type: integer
| | ... | - ${duts_prefix} - IP prefix, for all address in Lisp. Type: integer
| | ... | - ${dut1_vni} - DUT1 node Lisp vni. Type: integer
| | ... | - ${dut1_eid} - DUT1 node eid address. Type: string
| | ... | - ${dut1_deid} - DUT1 node destination eid address. Type: string
| | ... | - ${dut1_seid} - DUT1 node source eid address. Type: string
| | ... | - ${dut1_rloc} - DUT1 node receiver locator address. Type: string
| | ... | - ${dut2_vni} - DUT2 node Lisp vni. Type: integer
| | ... | - ${dut2_eid} - DUT2 node eid address. Type: string
| | ... | - ${dut2_deid} - DUT2 node destination eid address. Type: string
| | ... | - ${dut2_seid} - DUT2 node source eid address. Type: string
| | ... | - ${dut2_rloc} - DUT2 node receiver locator address. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Set up Lisp topology \| ${dut1_node} \| ${interface_name} \
| | ... | \| None \| ${dut2_node} \| ${interface_name} \| None \
| | ... | \| ${locator_name} \| ${locator_priority} \| ${locator_weight} \
| | ... | \| ${ip_prefix} \| ${lisp_vni1} \| ${lisp_eid1} \| ${deid1} \
| | ... | \| ${seid1} \| ${rloc1} \| ${lisp_vni2} \| ${lisp_eid2} \
| | ... | \| ${deid2} \| ${seid2} \| ${rloc2} \|
| | ...
| | [Arguments] | ${dut1_node} | ${dut1_int_name} | ${dut1_int_index}
| | ...         | ${dut2_node} | ${dut2_int_name} | ${dut2_int_index}
| | ...         | ${duts_locator_name} | ${duts_priority} | ${duts_weight}
| | ...         | ${duts_prefix}
| | ...         | ${dut1_vni} | ${dut1_eid} | ${dut1_deid} | ${dut1_seid}
| | ...         | ${dut1_rloc}
| | ...         | ${dut2_vni} | ${dut2_eid} | ${dut2_deid} | ${dut2_seid}
| | ...         | ${dut2_rloc}
| | ${dut1_int_index}= | Run Keyword If | ${dut1_int_index} is None
| |                    | ... | Get Interface Sw Index | ${dut1_node}
| |                    | ...                          | ${dut1_int_name}
| |                    | ... | ELSE | Set Variable | ${dut1_int_index}
| | ${dut2_int_index}= | Run Keyword If | ${dut2_int_index} is None
| |                    | ... | Get Interface Sw Index | ${dut2_node}
| |                    | ...                          | ${dut2_int_name}
| |                    | ... | ELSE | Set Variable | ${dut2_int_index}
| | Vpp lisp state | ${dut1_node} | enable
| | Vpp Add Lisp Locator Set | ${dut1_node} | ${duts_locator_name}
| | Vpp Add Lisp Locator | ${dut1_node} | ${duts_locator_name}
| | ...                  | ${dut1_int_index} | ${duts_priority} | ${duts_weight}
| | Vpp Add Lisp Local Eid | ${dut1_node} | ${duts_locator_name} | ${dut1_eid}
| | ...                    | ${duts_prefix}
| | Vpp Add Lisp Remote Mapping | ${dut1_node} | ${dut1_vni} | ${dut1_deid}
| |                             | ... | ${duts_prefix} | ${dut1_seid}
| |                             | ... | ${duts_prefix} | ${dut1_rloc}
| | Vpp Lisp State | ${dut2_node} | enable
| | Vpp Add Lisp Locator Set | ${dut2_node} | ${duts_locator_name}
| | Vpp Add Lisp Locator | ${dut2_node} | ${duts_locator_name}
| | ...                  | ${dut2_int_index} | ${duts_priority} | ${duts_weight}
| | Vpp Add Lisp Local Eid | ${dut2_node} | ${duts_locator_name} | ${dut2_eid}
| | ...                    | ${duts_prefix}
| | Vpp Add Lisp Remote Mapping | ${dut2_node} | ${dut2_vni} | ${dut2_deid}
| | ...                         | ${duts_prefix} | ${dut2_seid}
| | ...                         | ${duts_prefix} | ${dut2_rloc}
