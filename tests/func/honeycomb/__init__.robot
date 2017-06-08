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
| Library | resources/libraries/python/honeycomb/HcPersistence.py
| Resource | resources/libraries/robot/default.robot
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| ...
| Suite Setup | Run Keywords | Configure all DUTs before test | AND
| ... | Configure Honeycomb for testing | ${node} | AND
| ... | Configure ODL Client for testing | ${node} | AND
| ... | Set Global Variable | ${node}
| ...
| Suite Teardown | Archive Honeycomb log file | ${node}

*** Keywords ***
| Configure Honeycomb for testing
| | [Arguments] | ${node}
| | Configure Restconf binding address | ${node}
| | Enable Module Features | ${node}
| | Configure Log Level | ${node} | TRACE
| | Configure Persistence | ${node} | disable
| | Configure jVPP timeout | ${node} | ${14}
| | Clear Persisted Honeycomb Configuration | ${node}
| | Setup Honeycomb Service On DUTs | ${node}

| Configure ODL Client for testing
| | [Arguments] | ${node}
| | ${use_odl_client}= | Get Variable Value | ${HC_ODL}
| | Run Keyword If | '${use_odl_client}' != '${NONE}'
| | ... | Run Keywords
| | ... | Set Global Variable | ${use_odl_client} | AND
| | ... | Configure ODL Client Service On DUT | ${node} | ${use_odl_client}
| | ... | ELSE | Log | Variable HC_ODL is not present. Not using ODL.
| | ... | level=INFO
