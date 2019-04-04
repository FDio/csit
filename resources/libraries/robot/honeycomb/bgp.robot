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
| Library | resources.libraries.python.honeycomb.BGP.BGPKeywords
| Library | resources.libraries.python.honeycomb.HcAPIKwInterfaces.InterfaceKeywords

*** Keywords ***
| Configure BGP module
| | [Documentation] | Edit Honeycomb's configuration file for the BGP feature.\
| | ... | Honeycomb needs to be restarted for the changes to take effect.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - ip_address - IP address to bind BGP listener to. Type: string
| | ... | - port - Port number to bind BGP listener to. Type: integer
| | ... | - as_number - Autonomous System (AS) ID number. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure BGP module \| ${nodes['DUT1']} \| 192.168.0.1 \| ${179} \
| | ... | \| ${65000} \|
| | ...
| | [Arguments] | ${node} | ${ip_address} | ${port} | ${as_number}
| | Configure BGP base | ${node} | ${ip_address} | ${port} | ${as_number}

| No BGP peers should be configured
| | [Documentation] | Uses Honeycomb API to read BGP configuration and checks
| | ... | if there ary BGP peers conffigured.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| No BGP peers should be configured \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ...
| | ${oper_data}= | Get Full BGP Configuration | ${node}
| | Should be Empty | ${oper_data['bgp-openconfig-extensions:bgp']}

| Honeycomb adds BGP peer
| | [Documentation] | Uses Honeycomb API to add a BGP peer.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - address - IP address of the peer. Type: string
| | ... | - data - Peer configuration data. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds BGP peer \| ${nodes['DUT1']} \| 192.168.0.1 \
| | ... | \| ${data} \|
| | ...
| | [Arguments] | ${node} | ${address} | ${data}
| | ...
| | Add BGP Peer | ${node} | ${address} | ${data}

| BGP Peer From Honeycomb Should be
| | [Documentation] | Uses Honeycomb API to verify BGP peer config data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - address - IP address of the peer. Type: string
| | ... | - data - Peer configuration data. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| BGP Peer From Honeycomb Should be \
| | ... | \| ${nodes['DUT1']} \| 192.168.0.1 \| ${data} \|
| | ...
| | [Arguments] | ${node} | ${address} | ${data}
| | ...
| | ${oper_data}= | Get BGP Peer | ${node} | ${address}
| | Compare Data Structures | ${oper_data} | ${data}

| Peer Operational Data From Honeycomb Should be
| | [Documentation] | Uses Honeycomb API to verify BGP peer operational data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - address - IP address of the peer. Type: string
| | ... | - data - Peer configuration data. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| BGP Peer From Honeycomb Should be \
| | ... | \| ${nodes['DUT1']} \| 192.168.0.1 \| ${data} \|
| | ...
| | [Arguments] | ${node} | ${address}
| | ...
| | ${oper_data}= | Get BGP Peer | ${node} | ${address} | operational
| | Should be Equal | ${oper_data['peer'][0]['peer-id']} | bgp://${address}

| Honeycomb removes BGP peer
| | [Documentation] | Uses Honeycomb API to add a BGP peer.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - address - IP address of the peer. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds BGP peer \| ${nodes['DUT1']} \| 192.168.0.1 \|
| | ...
| | [Arguments] | ${node} | ${address}
| | ...
| | Remove BGP Peer | ${node} | ${address}

| Honeycomb configures BGP route
| | [Documentation] | Uses Honeycomb API to add a BGP route\
| | ... | to the specified peer.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - peer_address - IP address of the peer. Type: string
| | ... | - data - Peer configuration data. Type: dictionary
| | ... | - route_address - IP address of the route. Type: string
| | ... | - route_index - Numeric index of the route under the peer.\
| | ... | Type: integer
| | ... | - ip_version - IP protocol version, ipv4 or ipv6. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb adds BGP peer \| ${nodes['DUT1']} \| 192.168.0.1 \
| | ... | \| ${data} \| 192.168.0.2 \| ${0} \| ipv4 \|
| | ...
| | [Arguments] | ${node} | ${peer_address} | ${data}
| | ... | ${route_address} | ${route_index} | ${ip_version}
| | ...
| | Configure BGP Route | ${node} | ${peer_address} | ${data}
| | ... | ${route_address} | ${route_index} | ${ip_version}

| BGP Route From Honeycomb Should be
| | [Documentation] | Uses Honeycomb API to verify BGP route operational data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - peer_address - IP address of the peer. Type: string
| | ... | - data - Peer configuration data. Type: dictionary
| | ... | - route_address - IP address of the route. Type: string
| | ... | - route_index - Numeric index of the route under the peer.\
| | ... | Type: integer
| | ... | - ip_version - IP protocol version, ipv4 or ipv6. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| BGP Peers From Honeycomb Should Include \
| | ... | \| ${nodes['DUT1']} \| ${data} \|
| | ...
| | [Arguments] | ${node} | ${peer_address} | ${data}
| | ... | ${route_address} | ${route_index} | ${ip_version}
| | ...
| | ${oper_data}= | Get BGP Route | ${node} | ${peer_address}
| | ... | ${route_address} | ${route_index} | ${ip_version}
| | Compare Data Structures | ${oper_data} | ${data}

| Honeycomb removes BGP route
| | [Documentation] | Uses Honeycomb API to remove a BGP route.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - peer_address - IP address of the peer. Type: string
| | ... | - route_address - IP address of the route. Type: string
| | ... | - route_index - Numeric index of the route under the peer.\
| | ... | Type: integer
| | ... | - ip_version - IP protocol version, ipv4 or ipv6. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb removes BGP route \| ${nodes['DUT1']} \| 192.168.0.1 \
| | ... | \| 192.168.0.2 \| ${0} \| ipv4 \|
| | ...
| | [Arguments] | ${node} | ${peer_address} | ${route_address}
| | ... | ${route_index} | ${ip_version}
| | ...
| | Remove BGP Route | ${node} | ${peer_address} | ${route_address}
| | ... | ${route_index} | ${ip_version}

| No BGP routes should be configured
| | [Documentation] | Uses Honeycomb API to verify that no BGP routes\
| | ... | are configured under the specified peer.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - peer_address - IP address of the peer. Type: string
| | ... | - ip_version - IP protocol version, ipv4 or ipv6. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| No BGP routes should be configured \| ${nodes['DUT1']} \
| | ... | \| 192.168.0.1 \| ipv4 \|
| | ...
| | [Arguments] | ${node} | ${peer_address} | ${ip_version}
| | ...
| | ${oper_data}= | Get All Peer Routes
| | ... | ${node} | ${peer_address} | ${ip_version}
| | Should be Empty | ${oper_data['bgp-inet:${ip_version}-routes']}

| No BGP routes should exist
| | [Documentation] | Uses Honeycomb API to verify that no BGP routes\
| | ... | exist under the specified peer.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - peer_address - IP address of the peer. Type: string
| | ... | - ip_version - IP protocol version, ipv4 or ipv6. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| No BGP routes should be configured \| ${nodes['DUT1']} \
| | ... | \| 192.168.0.1 \| ipv4 \|
| | ...
| | [Arguments] | ${node} | ${peer_address} | ${ip_version}
| | ...
| | Run keyword and expect error | *Status code: 404*
| | ... | Get All Peer Routes
| | ... | ${node} | ${peer_address} | ${ip_version}

| BGP Loc-RIB table should include
| | [Documentation] | Uses Honeycomb API to retrieve local BGP RIB table\
| | ... | And verifies that it contains the specified entry.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - data - RIB that should be present in operational data.\
| | ... | Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| BGP Loc-RIB table should include \| ${nodes['DUT1']} \| ${data} \|
| | ...
| | [Arguments] | ${node} | ${data}
| | ...
| | ${oper_data}= | Get BGP Local RIB | ${node}
| | ${oper_data}= | Set Variable | ${oper_data['loc-rib']['tables']}
| | ${data}= | Set Variable | ${data['loc-rib']['tables']}
| | Compare RIB Tables | ${oper_data} | ${data}

| Receive BGP OPEN message
| | [Documentation] | Open a TCP listener on BGP port(179) and listen\
| | ... | for BGP OPEN message. Verify ID and holdtime fields.
| | ...
| | ... | *Arguments:*
| | ... | - tg_node - Information about the TG node. Type: dictionary
| | ... | - rx_ip - IP address to listen on. Type: string
| | ... | - src_ip - IP address of the BGP speaker. Also acts as BGP peer ID.\
| | ... | Type: string
| | ... | - holdtime - Expected value of HOLD_TIME field in received message.\
| | ... | Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Receive BGP OPEN message \| ${node['TG']} \
| | ... | \| 192.168.0.1 \| 192.168.0.2 \| ${0}
| | ...
| | [Arguments] | ${tg_node} | ${rx_ip} | ${src_ip} | ${port} | ${as_number}
| | ... | ${holdtime}
| | ...
| | ${args}= | Catenate | --rx_ip | ${rx_ip}
| | ...                 | --src_ip | ${src_ip}
| | ...                 | --rx_port | ${port}
| | ...                 | --as_number | ${as_number}
| | ...                 | --holdtime | ${holdtime}
| | Run Traffic Script On Node | honeycomb/bgp_open.py
| | ... | ${tg_node} | ${args}
