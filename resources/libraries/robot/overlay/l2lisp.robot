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
| Documentation | LISP-gpe encapsulation suite keywords
| Library | resources.libraries.python.topology.Topology
| Resource | resources/libraries/robot/overlay/lisp_api.robot
| Library  | resources.libraries.python.LispSetup.LispLocatorSet
| Library  | resources.libraries.python.LispSetup.LispLocator
| Library  | resources.libraries.python.LispSetup.LispLocalEid
| Library  | resources.libraries.python.LispSetup.LispAdjacency
| Library  | resources.libraries.python.LispSetup.LispRemoteMapping
| Library  | resources.libraries.python.LispSetup.LispMapResolver
| Library  | resources.libraries.python.LispSetup.LispEidTableMap

*** Keywords ***
| Configure L2 LISP on DUT
| | [Documentation] | Set up LISP L2 topology.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - DUT node. Type: dictionary
| | ... | - adjacency - DUT static adjacency settings. Type: dict
| | ... | - settings - DUT other LISP related settings. Type: dict
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Configure LISP GPE topology in 3-node circular topology \| ${dut_node} \| ${adjacency} \
| | ... | \| ${settings} \|
| | ...
| | [Arguments]
| | ... | ${dut_node} | ${adjacency} | ${settings}
| | ...
| | ${int_idx}= | Get Interface Sw Index | ${dut_node} | ${${adjacency['int']}}
| | Enable Lisp | ${dut_node}
| | Vpp Add Lisp Locator Set | ${dut_node}
| | ... | ${settings['locator_name']}
| | Vpp Add Lisp Locator | ${dut_node}
| | ... | ${settings['locator_name']}
| | ... | ${int_idx}
| | ... | ${settings['priority']}
| | ... | ${settings['weight']}
| | Vpp Lisp Eid Table Mapping | ${dut_node}
| | ... | ${settings['vni']}
| | ... | bd_id=${settings['bd']}
| | Vpp Add Lisp Local Eid | ${dut_node}
| | ... | ${settings['locator_name']}
| | ... | ${settings['vni']}
| | ... | ${adjacency['seid']}
| | Vpp Add Map Resolver | ${dut_node}
| | ... | ${adjacency['map_res']}
| | Vpp Add Lisp Remote Mapping | ${dut_node}
| | ... | ${settings['vni']}
| | ... | ${adjacency['eid']}
| | ... | 0
| | ... | ${adjacency['seid']}
| | ... | 0
| | ... | ${adjacency['rloc']}
| | ... | is_mac=${TRUE}
| | Vpp Add Lisp Adjacency | ${dut_node}
| | ... | ${settings['vni']}
| | ... | ${adjacency['eid']}
| | ... | 0
| | ... | ${adjacency['seid']}
| | ... | 0
| | ... | is_mac=${TRUE}
