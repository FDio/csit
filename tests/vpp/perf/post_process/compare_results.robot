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
| Resource |
| ...
| Force Tags |
| ...
| Suite Setup |
| ...
| Suite Teardown |
| ...
| Test Setup |
| ...
| Test Teardown |
| ...
| Documentation
| ...
| ... | High Level Design
| ...
| ... | The purpose of this test is to compare the last run of the specified job
| ... | e.g. performance daily trending to the reference run and report changes
| ... | (improvements and degradations) in the results of performance tests.
| ...
| ... | The job which is running this test passes if there is an improvement
| ... | or no change in the results of performance tests, it fails if there is a
| ... | degradation in the results of performance tests.
| ...
| ... | Pass / Fail criteria:
| ...
| ... | 1. number of failed performance tests in the tested run
| ... | 2. relative change of results, either ???
| ... |    a. all tests as one group, or
| ... |    b. tests in separate groups (e.g. current feature suites)
| ...
| ... | The test passes if:
| ... | - the number of failed tests compared to reference run is lower than ???
| ... | - the relative change of performace results is higher than ???

*** Keywords ***


*** Test Cases ***


