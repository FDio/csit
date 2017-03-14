# Copyright (c) 2016 Cisco and/or its affiliates.
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
| Suite Setup | Run Keywords | Setup All DUTs Before Test | AND
| ... | Configure Honeycomb for testing | ${node} | AND
| ... | Set Global Variable | ${node}
| Suite Teardown
| ... | Archive Honeycomb log file | ${node}

*** Keywords ***
| Configure Honeycomb for testing
| | [Arguments] | ${node}
| | Copy Java Libraries | ${node}
| | Configure Restconf binding address | ${node}
| | Enable Module Features | ${node}
| | Configure Log Level | ${node} | TRACE
| | Configure Persistence | ${node} | disable
| | Clear Persisted Honeycomb Configuration | ${node}
| | Setup Honeycomb Service On DUTs | ${node}
| | ${use_odl_client}= | Find ODL client on node | ${node}
| | Set Global Variable | ${use_odl_client}
| | Run Keyword If | ${use_odl_client}
| | ... | Start ODL Client on node | ${node}
