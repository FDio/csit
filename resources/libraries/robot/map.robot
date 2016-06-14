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
| Library | resources.libraries.python.Map
| Documentation | TBD

*** Keywords ***
| Send IPv4 and check headers for lightweight 4over6
| | [Documentation]
| | ... | LW4o6  \
| | ... | TBD.
| | ...
| | [Arguments]
| | ... | ${tg_node}
| | ... | ${tx_if}
| | ... | ${rx_if}
| | ... | ${tx_dst_mac}
| | ... | ${tx_dst_ipv4}
| | ... | ${tx_src_ipv4}
| | ... | ${tx_dst_udp_port}
| | ... | ${rx_dst_mac}
| | ... | ${rx_src_mac}
| | ... | ${dst_ipv6}
| | ... | ${src_ipv6}
| | ...
| | ${args}= | Catenate
| | ... | --tx_if | ${tx_if}
| | ... | --rx_if | ${rx_if}
| | ... | --tx_dst_mac | ${tx_dst_mac}
| | ... | --tx_src_ipv4 | ${tx_src_ipv4}
| | ... | --tx_dst_ipv4 | ${tx_dst_ipv4}
| | ... | --tx_dst_udp_port | ${tx_dst_udp_port}
| | ... | --rx_dst_mac | ${rx_dst_mac}
| | ... | --rx_src_mac | ${rx_src_mac}
| | ... | --src_ipv6 | ${src_ipv6}
| | ... | --dst_ipv6 | ${dst_ipv6}
| | ...
| | Run Traffic Script On Node
| | ... | send_ipv4_check_lw_4o6.py | ${tg_node} | ${args}

