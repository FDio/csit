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
| Documentation | VPP counters keywords
| Library | resources.libraries.python.VppCounters

*** Keywords ***
| Clear interface counters on all vpp nodes in topology
| | [Documentation] | Clear interface counters on all VPP nodes in topology
| | [Arguments] | ${nodes}
| | Clear Interface Counters on all DUTs | ${nodes}

| Clear all counters on all DUTs
| | [Documentation] | Clear runtime, interface, hardware and error counters
| | ... | on all DUTs with VPP instance
| | Clear runtime counters on all DUTs | ${nodes}
| | Clear interface counters on all DUTs | ${nodes}
| | Clear hardware counters on all DUTs | ${nodes}
| | Clear error counters on all DUTs | ${nodes}
