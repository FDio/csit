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
| Documentation | Keyword library for exporting results and other output.
|
| ... | Currently it contains only the flush keyword,
| ... | data adding is to be done by Python keywords in other libraries.
|
| Library | resources.libraries.python.model.export_json

*** Keywords ***
| Flush Test Json
| | [Documentation] | Write to file the JSON output for the test case.
| |
| | resources.libraries.python.model.export_json.flush_test
