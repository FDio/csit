# Copyright (c) 2017 Cisco and/or its affiliates.
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

*** Variables***
# Honeycomb node to run tests on.
| ${node}= | ${nodes['DUT1']}

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/interfaces.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Resource | resources/libraries/robot/honeycomb/performance.robot
| Library | resources.libraries.python.SetupFramework
| Library | resources.libraries.python.CpuUtils
| Library | resources.libraries.python.honeycomb.Performance
| Suite Setup | Setup suite for Honeycomb performance tests
| Suite Teardown | Run Keywords
| ... | Stop VPP Service on DUT | ${node}
| ... | AND | Archive Honeycomb Log File | ${node} | perf=${True}
| ... | AND | Stop honeycomb service on DUTs | ${node}

*** Keywords ***
| Setup suite for Honeycomb performance tests
| | Set Global Variable | ${node}
| | ${cores}= | Get Length | ${node['cpuinfo']}
| | Set Global Variable | ${cores}
| | Create Honeycomb base startup configuration of VPP on DUT | DUT1
| | Apply startup configuration on VPP DUT | DUT1
| | Configure Honeycomb for performance tests | ${node}

| Configure Honeycomb for performance tests
| | [Arguments] | ${node}
| | Configure Restconf binding address | ${node}
| | Configure Log Level | ${node} | DEBUG
| | Configure Persistence | ${node} | disable
| | Configure jVPP timeout | ${node} | ${14}
| | Generate Honeycomb startup configuration for performance test
| | ... | ${node} | ${cores}
| | Clear Persisted Honeycomb Configuration | ${node}

| Configure ODL Client for performance tests
| | [Arguments] | ${node}
| | ${use_odl_client}= | Get Variable Value | ${HC_ODL}
| | Run Keyword If | '${use_odl_client}' != '${NONE}'
| | ... | Run Keywords
| | ... | Set Global Variable | ${use_odl_client}
| | ... | AND | Copy ODL client | ${node} | ${HC_ODL} | ~ | ${install_dir}
| | ... | AND | Configure ODL Client Service On DUT | ${node} | ${install_dir}
| | ... | ELSE | Log | Variable HC_ODL is not present. Not using ODL.
| | ... | level=INFO
