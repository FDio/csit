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

| Library | resources.libraries.python.VatExecutor
| Library | resources.libraries.python.CrossConnectSetup
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.IPv4Util
| Variables | resources/libraries/python/constants.py

*** Keywords ***

| L2 setup xconnect on DUTs
| | [Documentation] | Setup Bidirectional Cross Connect on DUTs
# TODO: rewrite with dynamic path selection
| | Vpp Setup Bidirectional Cross Connect | ${nodes['DUT1']}
| | ... | ${nodes['DUT1']['interfaces']['port1']['name']}
| | ... | ${nodes['DUT1']['interfaces']['port3']['name']}
| | Vpp Setup Bidirectional Cross Connect | ${nodes['DUT2']}
| | ... | ${nodes['DUT2']['interfaces']['port1']['name']}
| | ... | ${nodes['DUT2']['interfaces']['port3']['name']}


| Get traffic links between TG "${tg}" and DUT1 "${dut1}" and DUT2 "${dut2}"
| | ${DUT1_TG_link}= | Get first active connecting link between node "${dut1}" and "${tg}"
| | ${DUT2_TG_link}= | Get first active connecting link between node "${dut2}" and "${tg}"
| | ${tg_traffic_links}= | Create List | ${DUT1_TG_link} | ${DUT2_TG_link}
| | [Return] | ${tg_traffic_links}


| Send traffic on node "${node}" from link "${link1}" to link "${link2}"
| | ${src_port}= | Get Interface By Link Name | ${node} | ${link1}
| | ${dst_port}= | Get Interface By Link Name | ${node} | ${link2}
| | ${src_ip}= | Set Variable | 192.168.100.1
| | ${dst_ip}= | Set Variable | 192.168.100.2
| | ${src_mac}= | Get Node Link Mac | ${node} | ${link1}
| | ${dst_mac}= | Get Node Link Mac | ${node} | ${link2}
| | ${args}= | Traffic Script Gen Arg | ${dst_port} | ${src_port} | ${src_mac} | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | send_ip_icmp.py | ${node} | ${args}


| Interfaces on all DUTs are in "${state}" state
| | Node "${nodes['DUT1']}" interface "${nodes['DUT1']['interfaces']['port1']['name']}" is in "${state}" state
| | Node "${nodes['DUT1']}" interface "${nodes['DUT1']['interfaces']['port3']['name']}" is in "${state}" state
| | Node "${nodes['DUT2']}" interface "${nodes['DUT2']['interfaces']['port1']['name']}" is in "${state}" state
| | Node "${nodes['DUT2']}" interface "${nodes['DUT2']['interfaces']['port3']['name']}" is in "${state}" state

