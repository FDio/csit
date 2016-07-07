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
| Documentation | Lisp static adjacency suite keywords
| Resource | resources/libraries/robot/lisp/lisp_api.robot
| Library  | resources.libraries.python.LispSetup.LispLocatorSet
| Library  | resources.libraries.python.LispSetup.LispLocator
| Library  | resources.libraries.python.LispSetup.LispLocalEid
| Library  | resources.libraries.python.LispSetup.LispAdjacency
| Library  | resources.libraries.python.LispSetup.LispRemoteMapping

*** Keywords ***
| Set up Lisp topology
| | [Documentation] | Set up Lisp static adjacency topology.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_node - DUT1 node. Type: dictionary
| | ... | - dut1_int_name - DUT1 node interface name. Type: string
| | ... | - dut1_int_index - DUT1 node interface index. Type: integer
| | ... | - dut2_node - DUT2 node. Type: dictionary
| | ... | - dut2_int_name - DUT2 node interface name. Type: string
| | ... | - dut2_int_index - DUT2 node interface index. Type: integer
| | ... | - locator_set - Locator set values. Type: dict
| | ... | - dut1_eid - Dut1 node eid address. Type: dict
| | ... | - dut2_eid - Dut2 node eid address. Type: dict
| | ... | - dut1_static_adjacency - Dut1 static adjacency. Type: dict
| | ... | - dut2_static_adjacency - Dut2 static address. Type: dict
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Set up Lisp topology \| ${dut1_node} \| ${interface_name} \
| | ... | \| None \| ${dut2_node} \| ${interface_name} \| None \
| | ... | \| ${locator_set} \| ${dut1_eid} \| ${dut2_eid} \
| | ... | \| ${dut1_static_adjacency} \| ${dut2_static_adjacency} \|
| | ...
| | [Arguments] | ${dut1_node} | ${dut1_int_name} | ${dut1_int_index}
| | ...         | ${dut2_node} | ${dut2_int_name} | ${dut2_int_index}
| | ...         | ${locator_set} | ${dut1_eid} | ${dut2_eid}
| | ...         | ${dut1_static_adjacency} | ${dut2_static_adjacency}
| | ${dut1_int_index}= | Run Keyword If | ${dut1_int_index} is None
| |                    | ... | Get Interface Sw Index | ${dut1_node}
| |                    | ...                          | ${dut1_int_name}
| |                    | ... | ELSE | Set Variable | ${dut1_int_index}
| | ${dut2_int_index}= | Run Keyword If | ${dut2_int_index} is None
| |                    | ... | Get Interface Sw Index | ${dut2_node}
| |                    | ...                          | ${dut2_int_name}
| |                    | ... | ELSE | Set Variable | ${dut2_int_index}
| | Enable Lisp | ${dut1_node}
| | Vpp Add Lisp Locator Set | ${dut1_node} | ${locator_set['locator_name']}
| | Vpp Add Lisp Locator | ${dut1_node} | ${locator_set['locator_name']}
| | ...                  | ${dut1_int_index} | ${locator_set['priority']}
| | ...                  | ${locator_set['weight']}
| | Vpp Add Lisp Local Eid | ${dut1_node} | ${dut1_eid['locator_name']} | ${dut1_eid['eid']}
| | ...                    | ${dut1_eid['prefix']}
| | Vpp Add Lisp Remote Mapping | ${dut1_node} | ${dut1_static_adjacency['vni']}
| | ...                         | ${dut1_static_adjacency['deid']}
| | ...                         | ${dut1_static_adjacency['prefix']}
| | ...                         | ${dut1_static_adjacency['seid']}
| | ...                         | ${dut1_static_adjacency['prefix']}
| | ...                         | ${dut1_static_adjacency['rloc']}
| | Vpp Add Lisp Adjacency | ${dut1_node} | ${dut1_static_adjacency['vni']}
| | ...                    | ${dut1_static_adjacency['deid']}
| | ...                    | ${dut1_static_adjacency['prefix']}
| | ...                    | ${dut1_static_adjacency['seid']}
| | ...                    | ${dut1_static_adjacency['prefix']}
| | Enable Lisp | ${dut2_node}
| | Vpp Add Lisp Locator Set | ${dut2_node} | ${locator_set['locator_name']}
| | Vpp Add Lisp Locator | ${dut2_node} | ${locator_set['locator_name']}
| | ...                  | ${dut2_int_index} | ${locator_set['priority']}
| | ...                  | ${locator_set['weight']}
| | Vpp Add Lisp Local Eid | ${dut2_node} | ${dut2_eid['locator_name']} | ${dut2_eid['eid']}
| | ...                    | ${dut2_eid['prefix']}
| | Vpp Add Lisp Remote Mapping | ${dut2_node} | ${dut2_static_adjacency['vni']}
| | ...                         | ${dut2_static_adjacency['deid']}
| | ...                         | ${dut2_static_adjacency['prefix']}
| | ...                         | ${dut2_static_adjacency['seid']}
| | ...                         | ${dut2_static_adjacency['prefix']}
| | ...                         | ${dut2_static_adjacency['rloc']}
| | Vpp Add Lisp Adjacency | ${dut2_node} | ${dut2_static_adjacency['vni']}
| | ...                    | ${dut2_static_adjacency['deid']}
| | ...                    | ${dut2_static_adjacency['prefix']}
| | ...                    | ${dut2_static_adjacency['seid']}
| | ...                    | ${dut2_static_adjacency['prefix']}