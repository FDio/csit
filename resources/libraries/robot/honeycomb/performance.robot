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
| Library | resources.libraries.python.honeycomb.Performance
| Library | resources.libraries.python.InterfaceUtil
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Documentation | Keywords used in Honeycomb performance testing.

*** Keywords ***
| Configure Honeycomb Netconf threads
| | [Documentation] | Modify thread configuration of Honeycomb's Netconf server,
| | ... | then restart Honeycomb to apply new configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - Node to change configuration on. Type: dictionary
| | ... | - threads - Number of threads to configure. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure Honeycomb Netconf Threads \| ${nodes[DUT1]} \| ${2} \|
| | ...
| | [Arguments] | ${node} | ${threads}
| | Configure Netconf Threads | ${node} | ${threads}
| | Restart Honeycomb and VPP | ${node}

| Run base operational read performance trial
| | [Documentation] | Send Netconf requests over plain TCP to obtain VPP version
| | ... | from Honeycomb operational data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Node to run test on. Type: dictionary
| | ... | - cycles - Number of test cycles to run. Final results will\
| | ... | be averaged across all runs. Type: integer
| | ... | - threads - Number of threads to use for generating traffic.\
| | ... | Type: integer
| | ... | - requests - Number of requests to send in each thread and cycle.\
| | ... | Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Run base operational read performance trial \| ${nodes[DUT1]} \
| | ... | \| ${3} \| ${4} \| ${10000} \|
| | ...
| | [Arguments] | ${node} | ${cores} | ${cycles} | ${threads} | ${requests}
| | Run traffic script on DUT | ${node} | read_vpp_version.py | ${cores}
| | ... | cycles=${cycles} | threads=${threads} | requests=${requests}
