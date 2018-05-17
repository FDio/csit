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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
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
| | [Documentation] | Setup variables and configure VPP and Honeycomb
| | ... | for performance testing.
| | ...
| | Set Global Variable | ${node}
| | Get CPU Layout from all nodes | ${nodes}
| | ${cores}= | Get Length | ${node['cpuinfo']}
| | Set Global Variable | ${cores}
| | Stop VPP Service on DUT | ${node}
| | Stop Honeycomb service on DUTs | ${node}
| | Generate VPP Startup Configuration for Honeycomb Test on DUT | ${node}
| | Configure Restconf binding address | ${node}
| | Configure Log Level | ${node} | INFO
| | Configure Persistence | ${node} | disable
| | Configure jVPP timeout | ${node} | ${14}
| | Generate Honeycomb startup configuration for performance test
| | ... | ${node} | ${cores}
| | Clear Persisted Honeycomb Configuration | ${node}

| Configure ODL Client for performance tests
| | [Documentation] | Setup ODL client for performance testing.
| | ...
| | ${use_odl_client}= | Get Variable Value | ${HC_ODL}
| | Run Keyword If | '${use_odl_client}' != '${NONE}'
| | ... | Run Keywords
| | ... | Set Global Variable | ${use_odl_client}
| | ... | AND | Copy ODL client | ${node} | ${HC_ODL} | ~ | ${install_dir}
| | ... | AND | Configure ODL Client Service On DUT | ${node} | ${install_dir}
| | ... | ELSE | Log | Variable HC_ODL is not present. Not using ODL.
| | ... | level=INFO
