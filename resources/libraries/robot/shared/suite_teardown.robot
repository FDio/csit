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

"""Keywords used in suite teardowns."""

*** Settings ***
| Library | resources.libraries.python.DPDK.DPDKTools
| ...
| Documentation | Suite terdown keywords.

*** Keywords ***
| Tear down suite
| | [Documentation]
| | ... | Common suite teardown for tests with no additional post processing.
| | ...
| | Run Keyword If | "PERFTEST" in @{TEST TAGS}
| | ... | Teardown traffic generator | ${tg}

| Tear down suite with dpdk
| | [Documentation]
| | ... | Common suite teardown for tests with dpdk.
| | ...
| | Tear down suite
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Cleanup DPDK Environment
| | | ... | ${nodes['${dut}']} | ${${dut}_if1} | ${${dut}_if2}
