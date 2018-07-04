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
| Documentation
| ... | Set global variables common to all tests.
| ...
| ... | Ideally we would use Variables table to set global variables.
| ... | Unfortunately, __init__ files are special (among other things)
| ... | by the fact that variables set in the table are not available
| ... | for (sub)directory suites.
| ... | Therefore we are using BuiltIn.Set_Global_Variable explicitly,
| ... | and OperatingSystem.Get_Environment_Variable for user overrides
| ... | (instead of --variable parameter to pybot).
| ...
| ... | TODO: Find better variable names (both robot and environment).
| Library | OpratingSystem
| Suite Setup | Set Common Variables

*** Keywords ***
| Set Common Variables
| | Documentation | Set the following global variables.
| | ... | trial_multiplicity - Number of trial to execute in MRR test.
| | ... | perf_trial_duration - Duration of one trial in MRR test.
| | ...
| | ${trial_multiplicity} = | Get Environment Variable
| | ... | TRIAL_MULTIPLICITY | 1
| | Set Global Variable | \${trial_multiplicity}
| | ${perf_trial_duration} = | Get Environment Variable
| | ... | PERF_TRIAL_DURATION | 10
| | Set Global Variable | \${perf_trial_duration}
