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
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.InterfaceUtil

*** Keywords ***
| L2 setup xconnect on DUT
| | [Documentation] | Setup Bidirectional Cross Connect on DUTs
| | [Arguments] | ${node} | ${if1} | ${if2} |
| | ${if1_name}= | Get interface name | ${node} | ${if1}
| | Set Interface State | ${node} | ${if1_name} | up
| | ${if2_name}= | Get interface name | ${node} | ${if2}
| | Set Interface State | ${node} | ${if2_name} | up
| | Vpp Setup Bidirectional Cross Connect | ${node} | ${if1_name} | ${if2_name}
