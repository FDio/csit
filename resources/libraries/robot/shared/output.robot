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
| Library | resources.libraries.python.StateDatabase
| ... | suite_name=${SUITE_NAME} | log_dir=${OUTPUT_DIR}

*** Keywords ***
| Save Output
| | [Documentation] | Save string under key in this test's subdatabase.
| |
| | ... | *Arguments:* FIXME.
| | ... | *Example:* FIXME.
| |
| | [Arguments] | ${key} | ${value}
| |
| | resources.libraries.python.StateDatabase.Database Update
| | ... | test_name=${TEST_NAME} | key=${key} | value=${value}

| | Flush Test
| | [Documentation] | Write to file (and forget) the state related to a test case.
| |
| | ... | *Arguments:* FIXME.
| | ... | *Example:* FIXME.
| |
| | resources.libraries.python.StateDatabase.Database Flush Test
| | ... | test_name=${TEST_NAME}
