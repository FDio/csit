# Copyright (c) 2018 Cisco and/or its affiliates.
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
# TODO: Extract other common lines from child inits.
| Suite Setup | Run Keywords | Setup common performance global Variables

*** Keywords ***
| Setup common performance global Variables
| | [Documentation]
| | ... | Setup suite Variables. Variables are used across performance testing.
| | ...
| | ... | _NOTE:_ This KW sets following suite variables:
| | ... | - i_x520_da2_uni_max - Maximal unidirectional transmit rate for 520 [bps]
| | ... | - i_x520_da2_bi_max - Maximal bidirectional transmit rate for 520 [bps]
| | ...
| | Set Global Variable | ${i_x520_da2_uni_max} | ${10000000000}
| | Set Global Variable | ${i_x520_da2_bi_max} | ${20000000000}
