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
| Resource | resources/libraries/robot/honeycomb.robot
| Suite Setup | Setup Honeycomb service
| Suite Teardown | Stop Honeycomb service

*** Test Cases ***
| Honeycomb reports running configuration
| | [Documentation] | *Check the contents of honeycomb configuration*
| | ...
| | ... | _Test steps:_
| | ... | - 1. Send HTTP GET request to obtain configured topology from all honeycomb nodes
| | ... | - 2. Retrieve configuration as JSON object
| | ... | - 3. Parse JSON for VPP instance ID string
| | ... | - 4. regex match ID string against expected pattern (vpp1, vpp2, vpp3,...)
| | ...
| | ... | _Pass criteria:_
| | ... | The test passes if the ID strings of VPP instances on each honeycomb node match the expected pattern
| | ...
| | ... | _Used global constants and variables:_
| | ... | - RESOURCES_TPL_HC - path to honeycomb templates directory
| | ... | - nodes - dictionary of all nodes in topology.YAML file
| | ...
| | [Tags] | honeycomb_sanity
| | Honeycomb checks VPP node configuration