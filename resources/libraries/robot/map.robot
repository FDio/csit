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
| Variables | resources/libraries/python/topology.py
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.DUTSetup
| Library | resources.libraries.python.TGSetup
| Library | resources.libraries.python.Map
| Documentation | TBD

*** Keywords ***
| Lightweight 4over6 is set
| | [Documentation] | TBD
| | ${domain_index}=
| | ... | Map Add Domain | 20.0.0.0/32 | ::/0 | 2001:10::1 | 0 | 6 | 6
| | Map Add Rule | ${domain_index} | 0 | 2001:10::1
