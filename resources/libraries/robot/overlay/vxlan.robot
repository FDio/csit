# Copyright (c) 2019 Cisco and/or its affiliates.
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
| Library  | resources.libraries.python.InterfaceUtil
| ...
| Documentation | VXLAN keywords.

*** Keywords ***
| Get VXLAN dump
| | [Documentation] | Get VXLAN dump.
| | ...
| | ... | *Arguments:*
| | ... | - node - DUT node data. Type: dictionary
| | ... | - interface - Interface on the VPP node (Optional). Type: string
| | ...
| | [Arguments] | ${dut_node} | ${interface}=${None}
| | ...
| | [Return] | ${vxlan_dump}
| | ...
| | ${vxlan_dump}= | VXLAN Dump | ${dut_node} | ${interface}
