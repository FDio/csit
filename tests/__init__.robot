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
| Documentation | Set global variables common to all tests.
| Resource | resources/libraries/robot/robot_enhancements.robot
| Suite Setup | Set Common Variables

*** Keywords ***
| Set Common Variables
| | [Documentation] | Set the following global variables.
| | ...
| | ... | While currently only MRR tests are using the values,
| | ... | any new test might decide to use them,
| | ... | so variable names are generic for "perf" scope.
| | ...
| | ... | perf_trial_multiplicity - Number of trials to execute in MRR test.
| | ... | perf_trial_duration - Duration of one trial in MRR test.
| | ...
| | Ensure Global Variable | perf_trial_multiplicity | 1
| | Ensure Global Variable | perf_trial_duration | 100
