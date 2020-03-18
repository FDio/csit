# Copyright (c) 2020 Cisco and/or its affiliates.
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
| Variables | ${CURDIR}/../resources/libraries/python/Constants.py
| Suite Setup | Fail If Fake

*** Keywords ***
| Fail If Fake
| | [Documentation]
| | ... | Check whether this run is fake, fail if yes.
| |
| | ... | Fake runs do not perform any testbed reservation,
| | ... | so it is important to fail before any testbed access is attempted
| | ... | by the tests.
| | ... | Constants.py determines fake runs from environment variables.
| |
| | Run Keyword If | ${RUN_IS_FAKE} | Fail | Failing the fake run.
