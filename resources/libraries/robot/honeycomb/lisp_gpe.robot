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
| Library | resources.libraries.python.honeycomb.Lisp.LispGPEKeywords
| Library | resources.libraries.python.LispUtil
| Documentation | Keywords used to test Honeycomb Lisp GPE features.

*** Keywords ***
| Honeycomb enables LISP GPE
| | [Documentation] | Uses Honeycomb API to enable Lisp GPE.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb enables LISP GPE \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | Set LispGPE state | ${node} | ${TRUE}

| Honeycomb disables LISP GPE
| | [Documentation] | Uses Honeycomb API to disable Lisp GPE.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb disables LISP GPE \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | Set LispGPE state | ${node} | ${FALSE}

| Honeycomb adds first Lisp GPE Mapping
| | [Documentation] | Uses Honeycomb API to configure a Lisp mapping. Removes
| | ... | any existing mappings.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - data - Lisp settings to use. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds first Lisp GPE Mapping \| ${nodes['DUT1']} \
| | ... | \| ${data} \|
| | ...
| | [Arguments] | ${node} | ${data}
| | ...
| | Configure LispGPE Mapping | ${node} | ${data}

| Honeycomb adds Lisp GPE Mapping
| | [Documentation] | Uses Honeycomb API to configure a Lisp mapping.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - data - Lisp settings to use. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds Lisp GPE Mapping \| ${nodes['DUT1']} \| ${data} \|
| | ...
| | [Arguments] | ${node} | ${data}
| | ...
| | Add LispGPE Mapping | ${node} | ${data['id']} | ${data}

| Honeycomb removes Lisp GPE mapping
| | [Documentation] | Uses Honeycomb API to remove the specified mapping.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes Lisp GPE mapping \| ${nodes['DUT1']} \| map_name
| | ...
| | [Arguments] | ${node} | ${mapping}
| | ...
| | Delete lispGPE mapping | ${node} | ${mapping}

| LISP GPE should not be configured
| | [Documentation] | Retrieves Lisp GPE configuration from Honeycomb operational\
| | ... | data, and expects an empty dictionary.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| LISP GPE should not be configured \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | ${data}= | Get Lisp GPE operational data | ${node}
| | Should be Equal
| | ... | ${data['gpe-state']['gpe-feature-data']['enable']} | ${FALSE}

| LISP GPE state from Honeycomb should be
| | [Documentation] | Retrieves Lisp GPE state from Honeycomb operational\
| | ... | data, and compares Lisp state with expected value.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - state - Expected Lisp state. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| LISP GPE state from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| enabled \|
| | ...
| | [Arguments] | ${node} | ${state}
| | ${data}= | Get LispGPE operational data | ${node}
| | ...
| | Run keyword if | $state == 'enabled'
| | ... | Should be equal as strings
| | ... | ${data['gpe-state']['gpe-feature-data']['enable']} | ${True}
| | Run keyword if | $state == 'disabled'
| | ... | Should be equal as strings
| | ... | ${data['gpe-state']['gpe-feature-data']['enable']} | ${False}

| LISP GPE state from VAT should be
| | [Documentation] | Retrieves Lisp state from VAT,\
| | ... | and compares Lisp state with expected value.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - state - Expected Lisp state. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| LISP state from VAT should be \| ${nodes['DUT1']} \| enabled \|
| | ...
| | [Arguments] | ${node} | ${state}
| | ...
| | ${status}= | VPP show Lisp State | ${node}
| | Should match | ${status['gpe_status']} | ${state}

| LISP GPE mapping from Honeycomb should be
| | [Documentation] | Retrieves Lisp GPE mapping from Honeycomb operational\
| | ... | data, and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - settings - Expected Lisp mapping data. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| LISP GPE mapping from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| ${settings} \|
| | ...
| | [Arguments] | ${node} | ${settings}
| | ...
| | ${data}= | Get LispGPE mapping | ${node} | ${settings['id']}
| | Compare data structures | ${data} | ${settings}

| LISP GPE mapping from VAT should be
| | [Documentation] | Retrieves Lisp GPE mapping from VAT,\
| | ... | and compares with expected data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - settings - Expected Lisp mapping data. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| LISP GPE mapping from VAT should be \| ${nodes['DUT1']} \
| | ... | \| ${settings} \|
| | ...
| | [Arguments] | ${node} | ${settings}
| | ...
| | ${data}= | VPP show LispGPE eid table | ${node}
| | Compare data structures | ${data[0]} | ${settings}

| LISP GPE mappings from Honeycomb should not exist
| | [Documentation] | Retrieves Lisp GPE mappings from operational\
| | ... | data, and expects to find none.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| LISP GPE mappings from Honeycomb should not exist \
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | ${data}= | Get LispGPE operational data | ${node}
| | Variable Should Not Exist
| | ... | ${data['gpe-state']['gpe-feature-data']['gpe-entry']}

| LISP GPE mappings from VAT should not exist
| | [Documentation] | Retrieves Lisp GPE mappings from VAT,\
| | ... | and expects to receive an empty list.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| LISP GPE mappings from VAT should not exist \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | Log | Not implemented in VPP.
| | Fail

| Honeycomb disables all LISP GPE features
| | [Documentation] | Uses Honeycomb API to remove all Lisp GPE configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb disables all LISP GPE features \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | Disable LispGPE | ${node}

| Send packet and verify LISP GPE encap
| | [Documentation] | Send ICMP packet to DUT out one interface and receive\
| | ... | a LISP-GPE encapsulated packet on the other interface.
| | ...
| | ... | *Arguments:*
| | ...
| | ... | _NOTE:_ Arguments are based on topology:
| | ...             | TG(if1)->(if1)DUT(if2)->TG(if2)
| | ...
| | ... | - tg_node - Node to execute scripts on (TG). Type: dictionary
| | ... | - src_ip - IP of source interface (TG-if1). Type: string
| | ... | - dst_ip - IP of destination interface (TG-if2). Type: string
| | ... | - tx_src_port - Interface of TG-if1. Type: string
| | ... | - tx_src_mac - MAC address of TG-if1. Type: string
| | ... | - tx_dst_mac - MAC address of DUT-if1. Type: string
| | ... | - rx_port - Interface of TG-if1. Type: string
| | ... | - rx_src_mac - MAC address of DUT1-if2. Type: string
| | ... | - rx_dst_mac - MAC address of TG-if2. Type: string
| | ... | - src_rloc - configured RLOC source address. Type: string
| | ... | - dst_rloc - configured RLOC destination address. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Send packet and verify LISP GPE encap \| ${nodes['TG']} \
| | ... | \| 10.0.0.1 \| 32.0.0.1 \|
| | ... | \| eth2 \| 08:00:27:ee:fd:b3 \| 08:00:27:a2:52:5b \
| | ... | \| eth3 \| 08:00:27:4d:ca:7a \| 08:00:27:7d:fd:10 \
| | ... | \| 10.0.1.1 \| 10.0.1.2 \|
| | ...
| | [Arguments] | ${tg_node} | ${src_ip} | ${dst_ip} | ${tx_src_port} |
| | ... | ${tx_src_mac} | ${tx_dst_mac} | ${rx_port} | ${rx_src_mac}
| | ... | ${rx_dst_mac} | ${src_rloc} | ${dst_rloc}
| | ${tx_port_name}= | Get interface name | ${tg_node} | ${tx_src_port}
| | ${rx_port_name}= | Get interface name | ${tg_node} | ${rx_port}
| | ${args}= | Catenate | --tg_src_mac | ${tx_src_mac} | --tg_dst_mac
| | ... | ${rx_dst_mac} | --dut_if1_mac | ${tx_dst_mac} | --dut_if2_mac
| | ... | ${rx_src_mac} | --src_ip | ${src_ip} | --dst_ip | ${dst_ip}
| | ... | --tx_if | ${tx_port_name} | --rx_if | ${rx_port_name}
| | ... | --src_rloc | ${src_rloc} | --dst_rloc | ${dst_rloc}
| | Run Traffic Script On Node | lisp/lispgpe_check.py | ${tg_node}
| | ... | ${args}

| LispGPE Functional Traffic Test Teardown
| | [Documentation] | Teardown for LISP GPE functional traffic test
| | Show Packet Trace on all DUTs | ${nodes}
| | VPP Show LISP EID Table | ${node}
| | Disable LispGPE | ${node}
