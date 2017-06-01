# Copyright (c) 2017 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.honeycomb.ProxyARP.ProxyARPKeywords
| Library | resources.libraries.python.honeycomb.ProxyARP.IPv6NDProxyKeywords
| Documentation | Keywords used to test Honeycomb ARP proxy and IPv6ND proxy.

*** Keywords ***
| Honeycomb configures proxyARP
| | [Documentation] | Uses Honeycomb API to configure proxyARP for a specific\
| | ... | destination IP range.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - data - Configuration to use. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb configures proxyARP \| ${nodes['DUT1']} \| ${data} \|
| | [Arguments] | ${node} | ${data}
| | Configure proxyARP | ${node} | ${data}

| Honeycomb removes proxyARP configuration
| | [Documentation] | Uses Honeycomb API to remove existing proxyARP\
| | ... | IP range configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes proxyARP configuration \| ${nodes['DUT1']} \|
| | [Arguments] | ${node}
| | Remove proxyARP configuration | ${node}

| Honeycomb enables proxyARP on interface
| | [Documentation] | Uses Honeycomb API to enable the proxyARP\
| | ... | feature on an interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb enables proxyARP on interface \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | Set proxyARP interface config | ${node} | ${interface} | enable

| Honeycomb disables proxyARP on interface
| | [Documentation] | Uses Honeycomb API to disable the proxyARP\
| | ... | feature on an interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb disables proxyARP on interface \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | Set proxyARP interface config | ${node} | ${interface} | disable

| Honeycomb configures IPv6 ND proxy on interface
| | [Documentation] | Uses Honeycomb API to enable the IPv6 ND proxy\
| | ... | feature on an interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ... | - addresses - one or more addresses to configure ND proxy with.\
| | ... | Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb configures IPv6 ND proxy on interface \
| | ... | \| ${nodes['DUT1']} \| GigabitEthernet0/8/0 \| 10::10 \| 10::11 \|
| | ...
| | [Arguments] | ${node} | ${interface} | @{addresses}
| | Configure IPv6ND | ${node} | ${interface} | ${addresses}

| Honeycomb disables IPv6 ND proxy on interface
| | [Documentation] | Uses Honeycomb API to disable the IPv6 ND proxy\
| | ... | feature on an interface.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb disables IPv6 ND proxy on interface \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | [Arguments] | ${node} | ${interface}
| | Configure IPv6ND | ${node} | ${interface}

| IPv6 ND proxy from Honeycomb should be
| | [Documentation] | Retrieves IPv6 ND proxy operational data and compares\
| | ... | with expected values.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ... | - addresses - one or more addresses to expect. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| IPv6 ND proxy from Honeycomb should be \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \| 10::10 \| 10::11 \|
| | ...
| | [Arguments] | ${node} | ${interface} | @{addresses}
| | ${oper_data}= | Get interface oper data | ${node} | ${interface}
| | ${oper_data}= | Set Variable
| | ... | ${oper_data['ietf-ip:ipv6']['nd-proxy:nd-proxies']['nd-proxy']}
| | ${data}= | Evaluate | [{"address":x} for x in $addresses]
| | Sort List | ${oper_data}
| | Sort List | ${data}
| | Should be equal | ${oper_data} | ${data}

| IPv6 ND proxy from Honeycomb should be empty
| | [Documentation] | Retrieves IPv6 ND proxy operational data and expects\
| | ... | to fail due to no data present.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - interface - name of an interface on the node. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \|IPv6 ND proxy from Honeycomb should be empty \| ${nodes['DUT1']} \
| | ... | \| GigabitEthernet0/8/0 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | ${oper_data}= | Get interface oper data | ${node} | ${interface}
| | Variable Should Not Exist
| | ... | ${oper_data['ietf-ip:ipv6']['nd-proxy:nd-proxies']['nd-proxy']}

| Verify IPv6ND proxy
| | [Documentation] | Send and receive ICMPv6 messages between TG interfaces
| | ... | through Neighbor Discovery proxy.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - TG node. Type: dictionary
| | ... | - tg_interface1 - TG interface. Type: string
| | ... | - tg_interface2 - TG interface. Type: string
| | ... | - src_ip - Source IPv6 address to use. Type: string
| | ... | - dst_ip - Destination IPv6 address to use. Type: string
| | ... | - src_mac - MAC address of source interface. Type: string
| | ... | - dst_mac - MAC address of destination interface. Type: string
| | ... | - proxy_to_src_mac - MAC address of DUT interface on link to source\
| | ... | TG interface. Type: string
| | ... | - proxy_to_dst_mac - MAC address of DUT interface on link to dest\
| | ... | TG interface. Type: string
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Verify IPv6ND proxy \| ${nodes['TG']} \
| | ... | \| eth3 \| eth4 \| 3ffe:62::1 \| 3ffe:63::2 \
| | ... | \| 08:00:27:cc:4f:54 \| 08:00:27:64:18:d2 \
| | ... | \| 08:00:27:c9:6a:d5 \| 08:00:27:c4:75:3a \|
| | ...
| | [Arguments] | ${tg_node} | ${tg_interface1} | ${tg_interface2}
| | ... | ${src_ip} | ${dst_ip} | ${src_mac} | ${dst_mac}
| | ... | ${proxy_to_src_mac} | ${proxy_to_dst_mac}
| | ${tg_interface_name1}= | Get interface name | ${tg_node} | ${tg_interface1}
| | ${tg_interface_name2}= | Get interface name | ${tg_node} | ${tg_interface2}
| | ${args}= | Catenate | --tx_if | ${tg_interface_name1}
| | ...                 | --rx_if | ${tg_interface_name2}
| | ...                 | --src_ip | ${src_ip}
| | ...                 | --dst_ip | ${dst_ip}
| | ...                 | --src_mac | ${src_mac}
| | ...                 | --dst_mac | ${dst_mac}
| | ...                 | --proxy_to_src_mac | ${proxy_to_src_mac}
| | ...                 | --proxy_to_dst_mac | ${proxy_to_dst_mac}
| | Run Traffic Script On Node | ipv6_nd_proxy_check.py
| | ... | ${tg_node} | ${args}
