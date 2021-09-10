# Copyright (c) 2021 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.model.export_json
|
| Suite Setup | Global Suite Setup
| Suite Teardown | Global Suite Teardown

*** Keywords ***
| Global Suite Setup
| | [Documentation]
| | ... | Perform initializations needed for any subsequent suite.
| | ... | Currently only a minimal JSON export initialization.
| |
| | Start Suite Setup Export
| | # Nothing explicit here, implicitly a place to find global start timestamp.
| | Finalize Suite Setup Export

| Global Suite Teardown
| | [Documentation]
| | ... | Perform cleanup needed after any preceding suite.
| | ... | Currently only a minimal JSON export and required flush.
| |
| | Start Suite Teardown Export
| | # Nothing explicit here, implicitly a place to find global end timestamp.
| | Finalize Suite Teardown Export
| | Export Pending Data
