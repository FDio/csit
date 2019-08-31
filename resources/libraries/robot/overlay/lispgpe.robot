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
| Library  | resources.libraries.python.LispSetup.LispEidTableMap

*** Keywords ***
| Configure LISP GPE topology in 3-node circular topology
| | [Documentation] | Configure LISP GPE topology in 3-node circular topology.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_node - DUT1 node. Type: dictionary
| | ... | - dut1_if - DUT1 node interface. Type: string
| | ... | - dut1_int_index - DUT1 node interface index. Type: integer
| | ... | - dut2_node - DUT2 node. Type: dictionary
| | ... | - dut2_if - DUT2 node interface. Type: string
| | ... | - dut2_int_index - DUT2 node interface index. Type: integer
| | ... | - locator_set - Locator set values. Type: dictionary
| | ... | - dut1_eid - DUT1 node eid address. Type: dictionary
| | ... | - dut2_eid - DUT2 node eid address. Type: dictionary
| | ... | - dut1_static_adjacency - DUT1 static adjacency. Type: dictionary
| | ... | - dut2_static_adjacency - DUT2 static adjacency. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Configure LISP GPE topology in 3-node circular topology \| ${dut1_node} \| ${interface_name} \
| | ... | \| None \| ${dut2_node} \| ${interface_name} \| None \
| | ... | \| ${locator_set} \| ${dut1_eid} \| ${dut2_eid} \
| | ... | \| ${dut1_static_adjacency} \| ${dut2_static_adjacency} \|
| | ...
| | [Arguments]
| | ... | ${dut1_node} | ${dut1_if} | ${dut1_int_index}
| | ... | ${dut2_node} | ${dut2_if} | ${dut2_int_index}
| | ... | ${locator_set} | ${dut1_eid} | ${dut2_eid}
| | ... | ${dut1_static_adjacency} | ${dut2_static_adjacency}
| | ... | ${vni_table}=0 | ${vrf_table}=0
| | ...
# DUT1 settings:
| | ${dut1_int_index}= | Run Keyword If | ${dut1_int_index} is None
| | | ... | Get Interface Sw Index | ${dut1_node} | ${dut1_if}
| | | ... | ELSE | Set Variable | ${dut1_int_index}
| | Enable Lisp | ${dut1_node}
| | Enable Lisp GPE | ${dut1_node}
| | Vpp Add Lisp Locator Set | ${dut1_node}
| | ... | ${locator_set['locator_name']}
| | Vpp Add Lisp Locator | ${dut1_node}
| | ... | ${locator_set['locator_name']}
| | ... | ${dut1_int_index}
| | ... | ${locator_set['priority']}
| | ... | ${locator_set['weight']}
| | Vpp Lisp Eid Table Mapping | ${dut1_node}
| | ... | ${vni_table}
| | ... | vrf=${vrf_table}
| | Vpp Add Lisp Local Eid | ${dut1_node}
| | ... | ${dut1_eid['locator_name']}
| | ... | ${vni_table}
| | ... | ${dut1_eid['eid']}
| | ... | ${dut1_eid['prefix']}
| | Vpp Add Lisp Remote Mapping | ${dut1_node}
| | ... | ${vni_table}
| | ... | ${dut1_static_adjacency['deid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['seid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['rloc']}
| | Vpp Add Lisp Adjacency | ${dut1_node}
| | ... | ${vni_table}
| | ... | ${dut1_static_adjacency['deid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['seid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ...
# DUT2 settings:
| | ${dut2_int_index}= | Run Keyword If | ${dut2_int_index} is None
| | | ... | Get Interface Sw Index | ${dut2_node} | ${dut2_if}
| | | ... | ELSE | Set Variable | ${dut2_int_index}
| | Enable Lisp | ${dut2_node}
| | Enable Lisp GPE | ${dut2_node}
| | Vpp Add Lisp Locator Set | ${dut2_node}
| | ... | ${locator_set['locator_name']}
| | Vpp Add Lisp Locator | ${dut2_node}
| | ... | ${locator_set['locator_name']}
| | ... | ${dut2_int_index}
| | ... | ${locator_set['priority']}
| | ... | ${locator_set['weight']}
| | Vpp Lisp Eid Table Mapping | ${dut2_node}
| | ... | ${vni_table}
| | ... | vrf=${vrf_table}
| | Vpp Add Lisp Local Eid | ${dut2_node}
| | ... | ${dut2_eid['locator_name']}
| | ... | ${vni_table}
| | ... | ${dut2_eid['eid']}
| | ... | ${dut2_eid['prefix']}
| | Vpp Add Lisp Remote Mapping | ${dut2_node}
| | ... | ${vni_table}
| | ... | ${dut2_static_adjacency['deid']}
| | ... | ${dut2_static_adjacency['prefix']}
| | ... | ${dut2_static_adjacency['seid']}
| | ... | ${dut2_static_adjacency['prefix']}
| | ... | ${dut2_static_adjacency['rloc']}
| | Vpp Add Lisp Adjacency | ${dut2_node}
| | ... | ${vni_table}
| | ... | ${dut2_static_adjacency['deid']}
| | ... | ${dut2_static_adjacency['prefix']}
| | ... | ${dut2_static_adjacency['seid']}
| | ... | ${dut2_static_adjacency['prefix']

| Configure LISP GPE topology in 2-node circular topology
| | [Documentation] | Configure LISP GPE topology in 2-node circular topology.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_node - DUT1 node. Type: dictionary
| | ... | - dut1_if - DUT1 node interface. Type: string
| | ... | - dut1_int_index - DUT1 node interface index. Type: integer
| | ... | - locator_set - Locator set values. Type: dictionary
| | ... | - dut1_eid - DUT1 node eid address. Type: dictionary
| | ... | - dut1_static_adjacency - DUT1 static adjacency. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Configure LISP GPE topology in 2-node circular topology \| ${dut1_node} \| ${interface_name} \
| | ... | \| None \
| | ... | \| ${locator_set} \| ${dut1_eid} \
| | ... | \| ${dut1_static_adjacency} \|
| | ...
| | [Arguments]
| | ... | ${dut1_node} | ${dut1_if} | ${dut1_int_index}
| | ... | ${locator_set} | ${dut1_eid}
| | ... | ${dut1_static_adjacency}
| | ... | ${vni_table}=0 | ${vrf_table}=0
| | ...
# DUT1 settings:
| | ${dut1_int_index}= | Run Keyword If | ${dut1_int_index} is None
| | | ... | Get Interface Sw Index | ${dut1_node} | ${dut1_if}
| | | ... | ELSE | Set Variable | ${dut1_int_index}
| | Enable Lisp | ${dut1_node}
| | Enable Lisp GPE | ${dut1_node}
| | Vpp Add Lisp Locator Set | ${dut1_node}
| | ... | ${locator_set['locator_name']}
| | Vpp Add Lisp Locator | ${dut1_node}
| | ... | ${locator_set['locator_name']}
| | ... | ${dut1_int_index}
| | ... | ${locator_set['priority']}
| | ... | ${locator_set['weight']}
| | Vpp Lisp Eid Table Mapping | ${dut1_node}
| | ... | ${vni_table}
| | ... | vrf=${vrf_table}
| | Vpp Add Lisp Local Eid | ${dut1_node}
| | ... | ${dut1_eid['locator_name']}
| | ... | ${vni_table}
| | ... | ${dut1_eid['eid']}
| | ... | ${dut1_eid['prefix']}
| | Vpp Add Lisp Remote Mapping | ${dut1_node}
| | ... | ${vni_table}
| | ... | ${dut1_static_adjacency['deid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['seid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['rloc']}
| | Vpp Add Lisp Adjacency | ${dut1_node}
| | ... | ${vni_table}
| | ... | ${dut1_static_adjacency['deid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['seid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ...

| Configure IPV6 LISPoIPV4  topology in 2-node circular topology
| | [Documentation] | Configure LISPoIPV4 GPE topology in 2-node circular topology.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_node - DUT1 node. Type: dictionary
| | ... | - dut1_if - DUT1 node interface. Type: string
| | ... | - dut1_int_index - DUT1 node interface index. Type: integer
| | ... | - locator_set - Locator set values. Type: dictionary
| | ... | - dut1_eid - DUT1 node eid address. Type: dictionary
| | ... | - dut1_static_adjacency - DUT1 static adjacency. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ... | \| Configure LISP GPE topology in 2-node circular topology \| ${dut1_node} \| ${interface_name} \
| | ... | \| None \
| | ... | \| ${locator_set} \| ${dut1_eid} \
| | ... | \| ${dut1_static_adjacency} \|
| | ...
| | [Arguments]
| | ... | ${dut1_node} | ${dut1_if} | ${dut1_int_index}
| | ... | ${locator_set} | ${dut1_eid}
| | ... | ${dut1_static_adjacency}
| | ... | ${vni_table}=0 | ${vrf_table}=0
| | ...
# DUT1 settings:
| | ${dut1_int_index}= | Run Keyword If | ${dut1_int_index} is None
| | | ... | Get Interface Sw Index | ${dut1_node} | ${dut1_if}
| | | ... | ELSE | Set Variable | ${dut1_int_index}
| | Enable Lisp | ${dut1_node}
| | Enable Lisp GPE | ${dut1_node}
| | Vpp Add Lisp Locator Set | ${dut1_node}
| | ... | ${locator_set['locator_name']}
| | Vpp Add Lisp Locator | ${dut1_node}
| | ... | ${locator_set['locator_name']}
| | ... | ${dut1_int_index}
| | ... | ${locator_set['priority']}
| | ... | ${locator_set['weight']}
| | Vpp Lisp Eid Table Mapping | ${dut1_node}
| | ... | ${vni_table}
| | ... | vrf=${vrf_table}
| | Vpp Add Lisp Local Eid | ${dut1_node}
| | ... | ${dut1_eid['locator_name']}
| | ... | ${vni_table}
| | ... | ${dut1_eid['eid']}
| | ... | ${dut1_eid['prefix']}
| | Vpp Add Lisp Remote Mapping | ${dut1_node}
| | ... | ${vni_table}
| | ... | ${dut1_static_adjacency['deid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['seid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['rloc']}
| | Vpp Add Lisp Adjacency | ${dut1_node}
| | ... | ${vni_table}
| | ... | ${dut1_static_adjacency['deid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ... | ${dut1_static_adjacency['seid']}
| | ... | ${dut1_static_adjacency['prefix']}
| | ...
