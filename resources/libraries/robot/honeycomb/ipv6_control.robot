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
| Library | resources.libraries.python.honeycomb.DHCP.DHCPRelayKeywords
| Library | resources.libraries.python.Dhcp.DhcpProxy
| Library | resources.libraries.python.DUTSetup
| Documentation | Keywords used to test Honeycomb DHCP features.

*** Keywords ***
| Convert data-plane interface to control-plane
| | [Documentation] | Unbinds an interface from VPP and binds it to kernel\
| | ... | driver specified in topology.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_name - Name of the interface in topology. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Convert data-plane interface to control-plane \| ${nodes['DUT1']} \
| | ... | \| port3 \|
| | ...
| | [Arguments] | ${node} | ${interface}
| | ${new_driver}= | Get Variable Value
| | ... | ${node['interfaces']['${interface}']['driver']}
| | PCI Driver Unbind | ${node}
| | ... | ${node['interfaces']['${interface}']['pci_address']}
| | Run Keyword If | '${new_driver}' == None
| | ... | PCI Driver Bind | ${node}
| | ... | ${node['interfaces']['${interface}']['pci_address']} | virtio-pci
| | ... | ELSE
| | ... | PCI Driver Bind | ${node}
| | ... | ${node['interfaces']['${interface}']['pci_address']} | ${new_driver}
