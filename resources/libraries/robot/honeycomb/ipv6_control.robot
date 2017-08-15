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
| Documentation | Keywords used to test Honeycomb DHCP features.

*** Keywords ***
| Convert data-plane interface to control-plane
| | [Arguments] | ${node} | ${interface}
| | Bind Interface Driver | ${node}
| | ... | ${node['interfaces']['${interface}']['pci_address']}
| | ... | uio_pci_generic | ${node['interfaces']['${interface}']['driver']}

| Convert control-plane interface to data-plane
| | [Arguments] | ${node} | ${interface}
| | Bind Interface Driver | ${node}
| | ... | ${node['interfaces']['${interface}']['pci_address']}
| | ... | ${node['interfaces']['${interface}']['driver']} | uio_pci_generic
