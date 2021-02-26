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
| Documentation | Keyword library for gathering results and other output.
|
| Library | resources.libraries.python.StateDatabase | import.${SUITE NAME}.${TEST NAME}


*** Keywords ***
| Save Output
| | [Documentation] | Save string under key in this test's subdatabase.
| |
| | ... | *Arguments:* FIXME.
| | ... | *Example:* FIXME.
| |
| | [Arguments] | ${sub_key} | ${value}
| |
| | ${super_key} = | Set Variable | save.${SUITE NAME}.${TEST NAME}.key.${sub_key}
| | StateDatabase.update | key=${super_key} | value=${value}

| Dump Json
| | [Documentation] | Return JSON-encoded global database
| |
| | ... | *Arguments:* FIXME.
| | ... | *Example:* FIXME.
| |
| | Run Keyword And Return | StateDatabase.dump | filename=json.log
