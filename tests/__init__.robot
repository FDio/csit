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
| ...
| ... | TODO: Find better variable names (both robot and environment).
| Library | OperatingSystem
| Library | String
| Suite Setup | Set Common Variables

*** Keywords ***
| Ensure Global Variable
| | [Documentation] | Give default value (from environment or code) to variable.
| | ...
| | ... | Ideally we would just use Variables table to set global variables.
| | ... | Unfortunately, __init__ files are special (among other things)
| | ... | by the fact that variables set in the table are not available
| | ... | for (sub)directory suites.
| | ... | Therefore we are using BuiltIn.Set_Global_Variable explicitly.
| | ... | While we are running code here, we allow environment variables
| | ... | to override the default values.
| | ... | If environment variable name is not specified (or empty),
| | ... | the upper case of the robot variable name is used.
| | ... | The --variable parameter to pybot takes precedence to environment.
| | ... | TODO: Move this keyword somewhere to resources/libraries/robot/.
| | ...
| | [Arguments] | ${variable_name} | ${default_value} | ${env_var_name}=${EMPTY}
| | ...
| | ${env_var_length} = | Get Length | ${env_var_name}
| | ${default_env_var} = | Convert To Uppercase | ${variable_name}
| | ${env_var} = | Set Variable If | ${env_var_length}
| | ... | ${env_var_name} | ${default_env_var}
| | ${updated_default} = | Get Environment Variable
| | ... | ${env_var} | ${default_value}
| | ${final_value} = | Get Variable Value
| | ... | ${variable_name} | ${updated_default}
| | # For some reason "${variable_name}" does not work in the following line.
| | Set Global Variable | \${${variable_name}} | ${final_value}

| Set Common Variables
| | [Documentation] | Set the following global variables.
| | ... | trial_multiplicity - Number of trial to execute in MRR test.
| | ... | perf_trial_duration - Duration of one trial in MRR test.
| | ...
| | Ensure Global Variable | trial_multiplicity | 1
| | Ensure Global Variable | perf_trial_duration | 10
