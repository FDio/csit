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
| Library | resources.libraries.python.L2Util

*** Keywords ***
| Get L2 FIB entry PAPI
| | [Documentation] | Retrieve the operational data about the specified L2 \
| | ... | FIB entry using Python API.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_index - Index of the bridge domain. Type: integer
| | ... | - mac - MAC address. Type: string
| | ...
| | ... | *Example:*
| | ... | \| Get L2 FIB entry PAPI \
| | ... | \| ${nodes['DUT1']} \| test_bd \| 00:fe:c8:e5:46:d1 \|
| | ...
| | [Arguments] | ${node} | ${bd_index} | ${mac}
| | ...
| | [Return] | ${l2_fib_data}
| | ...
| | ${l2_fib_data}= | Get L2 FIB entry by MAC | ${node} | ${bd_index}
| | ... | ${mac}

| Get L2 FIB table PAPI
| | [Documentation] | Retrieve L2 FIB table data of the specified bridge \
| | ... | domain using Python API.
| | ...
| | ... | *Arguments:*
| | ... | - node - Information about a DUT node. Type: dictionary
| | ... | - bd_index - Index of the bridge domain. Type: integer
| | ...
| | ... | *Example:*
| | ... | \| Get L2 FIB table PAPI \| ${nodes['DUT1']} \| test_bd \|
| | ...
| | [Arguments] | ${node} | ${bd_index}
| | ...
| | [Return] | ${l2_fib_data}
| | ...
| | ${l2_fib_data}= | Get L2 FIB table | ${node} | ${bd_index}
