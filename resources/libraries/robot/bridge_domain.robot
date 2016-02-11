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
| Library | resources.libraries.python.VatConfigGenerator
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.L2Util
| Variables | resources/libraries/python/constants.py

*** Variables ***
| ${VAT_BD_TEMPLATE} | ${Constants.RESOURCES_TPL_VAT}/l2_bridge_domain.vat
| ${VAT_BD_STATIC_TPL} | ${Constants.RESOURCES_TPL_VAT}/l2_bridge_domain_static.vat
| ${VAT_BD_GEN_FILE} | ${Constants.RESOURCES_TPL_VAT}/l2_bridge_domain_gen.vat
| ${VAT_BD_REMOTE_PATH} | ${Constants.REMOTE_FW_DIR}/${Constants.RESOURCES_TPL_VAT}/l2_bridge_domain_gen.vat

*** Keywords ***
| Setup l2 bridge on node "${node}" via links "${link_names}"
| | ${interface_config}= | Get Interfaces By Link Names | ${node} | ${link_names}
| | ${commands}= | Generate Vat Config File | ${VAT_BD_TEMPLATE} | ${interface_config} | ${VAT_BD_GEN_FILE}
| | Copy Config To Remote | ${node} | ${VAT_BD_GEN_FILE} | ${VAT_BD_REMOTE_PATH}
# TODO: will be removed once v4 is merged to master.
| | Execute Script | l2_bridge_domain_gen.vat | ${node} | json_out=False
| | Script Should Have Passed

| Setup l2 bridge with static fib on node "${node}" via links "${link_names}" on bd with index "${bd_id}"
| | ${vat_template_dict}= | Create dict used in bridge domain template file for node "${node}" with links "${link_names}" and bd_id "${bd_id}"
| | ${commands}= | Generate Vat Config File | ${VAT_BD_STATIC_TPL} | ${vat_template_dict} | ${VAT_BD_GEN_FILE}
| | Copy Config To Remote | ${node} | ${VAT_BD_GEN_FILE} | ${VAT_BD_REMOTE_PATH}
# TODO: will be removed once v4 is merged to master.
| | Execute Script | l2_bridge_domain_gen.vat | ${node} | json_out=False
| | Script Should Have Passed

| Send traffic on node "${node}" from link "${link1}" to link "${link2}"
| | ${src_port}= | Get Interface By Link Name | ${node} | ${link1}
| | ${dst_port}= | Get Interface By Link Name | ${node} | ${link2}
| | ${src_ip}= | Set Variable | 192.168.100.1
| | ${dst_ip}= | Set Variable | 192.168.100.2
| | ${src_mac}= | Get Node Link Mac | ${node} | ${link1}
| | ${dst_mac}= | Get Node Link Mac | ${node} | ${link2}
| | ${args}= | Traffic Script Gen Arg | ${dst_port} | ${src_port} | ${src_mac} | ${dst_mac} | ${src_ip} | ${dst_ip}
| | Run Traffic Script On Node | send_ip_icmp.py | ${node} | ${args}

| Setup TG "${tg}" DUT1 "${dut1}" and DUT2 "${dut2}" for 3 node l2 bridge domain test
| | ${topology_links}= | Get link data useful in circular topology test from tg "${tg}" dut1 "${dut1}" dut2 "${dut2}"
| | Setup l2 bridge on node "${dut1}" via links "${topology_links['DUT1_BD_LINKS']}"
| | Setup l2 bridge on node "${dut2}" via links "${topology_links['DUT2_BD_LINKS']}"
| | [Return] | ${topology_links['TG_TRAFFIC_LINKS']}

| Setup TG "${tg}" DUT1 "${dut1}" and DUT2 "${dut2}" for 3 node static l2fib test
| | ${topology_links}= | Get link data useful in circular topology test from tg "${tg}" dut1 "${dut1}" dut2 "${dut2}"
| | ${dst_mac}= | Get Node Link Mac | ${tg} | ${topology_links["DUT2_TG_LINK"]}
| | ${bd_index}= | Set Variable | 1
| | Setup l2 bridge with static fib on node "${dut1}" via links "${topology_links['DUT1_BD_LINKS']}" on bd with index "${bd_index}"
| | Setup static L2FIB entry on node "${dut1}" for MAC "${dst_mac}" link "${topology_links['DUT1_DUT2_LINK']}" pair on bd_index "${bd_index}"
| | Setup l2 bridge with static fib on node "${dut2}" via links "${topology_links['DUT2_BD_LINKS']}" on bd with index "${bd_index}"
| | Setup static L2FIB entry on node "${dut2}" for MAC "${dst_mac}" link "${topology_links['DUT2_TG_LINK']}" pair on bd_index "${bd_index}"
| | [Return] | ${topology_links["TG_TRAFFIC_LINKS"]}
