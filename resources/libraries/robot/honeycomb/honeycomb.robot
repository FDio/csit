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

*** Settings ***
| Library | resources.libraries.python.honeycomb.HoneycombSetup
| Library | resources.libraries.python.honeycomb.HoneycombUtil
| Library | resources.libraries.python.honeycomb.HcPersistence
| Library | resources.libraries.python.DUTSetup
| Library | resources.libraries.python.InterfaceUtil

*** Keywords ***
| Configure Honeycomb service on DUTs
| | [Documentation] | *Setup environment for honeycomb testing.*
| | ...
| | ... | _Setup steps:_
| | ... | - 1. Login to each honeycomb node using ssh
| | ... | - 2. Startup honeycomb service
| | ... | - 3. Monitor service startup using HTTP GET request loop
| | ... | Expected sequence of HTTP replies:
| | ... | connection refused -> 404 -> 401 -> 503 or 500 -> 200 (pass)
| | ... | - 4. Configure honeycomb nodes using HTTP PUT request
| | ...
| | ... | _Arguments:_
| | ... | - duts - list of nodes to setup Honeycomb on
| | ...
| | ... | _Used global constants and variables:_
| | ... | - RESOURCES_TPL_HC - path to honeycomb templates directory
| | ... | - HTTPCodes - HTTP protocol status codes
| | ...
| | [Arguments] | @{duts}
| | Start honeycomb on DUTs | @{duts}
| | Wait until keyword succeeds | 6min | 16sec
| | ... | Check honeycomb startup state | @{duts}
| | Sleep | 5s | Make sure all modules are loaded and ready.

| Stop Honeycomb service on DUTs
| | [Documentation] | *Cleanup environment after honeycomb testing.*
| | ...
| | ... | _Teardown steps:_
| | ... | - 1. Login to each honeycomb node using ssh
| | ... | - 2. Stop honeycomb service
| | ... | - 3. Monitor service shutdown using HTTP GET request loop
| | ... | Expected sequence of HTTP replies:
| | ... | 200 -> 404 -> connection refused (pass)
| | ...
| | ... | _Arguments:_
| | ... | - duts - list of nodes to stop Honeycomb on
| | ...
| | ... | _Used global constants and variables:_
| | ... | - RESOURCES_TPL_HC - path to honeycomb templates directory
| | ... | - HTTPCodes - HTTP protocol status codes
| | ...
| | [Arguments] | @{duts}
| | Stop honeycomb on DUTs | @{duts}
| | Wait until keyword succeeds | 60sec | 16sec
| | ... | Check honeycomb shutdown state | @{duts}

| Clear persisted Honeycomb configuration
| | [Documentation] | *Delete saved configuration.*
| | ...
| | ... | *Arguments:*
| | ... | - duts - one or more nodes to clear persistence on. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Clear persisted Honeycomb configuration \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | @{duts}
| | Clear persisted Honeycomb config | @{duts}

| Restart Honeycomb and VPP and clear persisted configuration
| | [Documentation] | Restarts Honeycomb and VPP with default configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Restart Honeycomb and VPP and clear persisted configuration \
| | ... | \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Stop Honeycomb service on DUTs | ${node}
| | Clear persisted Honeycomb configuration | ${node}
| | Setup DUT | ${node}
| | Sleep | 10s | Wait 10sec so VPP is up for sure.
| | Configure Honeycomb service on DUTs | ${node}

| Restart Honeycomb and VPP
| | [Documentation] | Stops the Honeycomb service and verifies it is stopped.
| | ... | Then restarts VPP, starts Honeycomb again and verifies it is running.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Restart Honeycomb and VPP \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Stop Honeycomb service on DUTs | ${node}
| | Setup DUT | ${node}
| | Sleep | 10s | Wait 10sec so VPP is up for sure.
| | Configure Honeycomb service on DUTs | ${node}

| Restart Honeycomb and VPP in performance test
| | [Documentation] | Stops Honeycomb and VPP and verifies HC is stopped.
| | ... | Then restarts VPP, starts Honeycomb again and verifies it is running.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Restart Honeycomb and VPP \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Stop Honeycomb service on DUTs | ${node}
| | Stop VPP service on DUT | ${node}
| | Setup DUT | ${node}
| | Sleep | 10s | Wait 10sec so VPP is up for sure.
| | Configure Honeycomb service on DUTs | ${node}
| | Wait until keyword succeeds | 2min | 16sec
| | ... | Check honeycomb startup state | ${node}

| Archive Honeycomb log file
| | [Documentation] | Copy honeycomb.log file from Honeycomb node\
| | ... | to test executor.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - perf - Running on performance testbed? Yes/no Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Archive Honeycomb log file \| ${nudes['DUT1']} \|
| | ...
| | [Arguments] | ${node} | ${perf}=${False}
| | Archive Honeycomb log | ${node} | ${perf}

| Configure ODL Client Service On DUT
| | [Documentation] | Configure and start ODL client, then repeatedly check if
| | ... | it is running.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ... | - odl_name - Name of ODL client version. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure ODL Client Service on DUT \| ${nodes['DUT1']} \
| | ... | \| carbon-SR1 \|
| | ...
| | [Arguments] | ${node} | ${odl_name}
| | Copy ODL Client | ${node} | ${odl_name} | /mnt/common | /tmp
| | Setup ODL Client | ${node} | /tmp
| | Wait until keyword succeeds | 3min | 30sec
| | ... | Install ODL Features | ${node} | /tmp
| | Wait until keyword succeeds | 4min | 16sec
| | ... | Mount Honeycomb on ODL | ${node}
| | Wait until keyword succeeds | 3min | 16sec
| | ... | Check ODL startup state | ${node}
| | Wait until keyword succeeds | 2min | 16sec
| | ... | Check honeycomb startup state | ${node}

| Configure Honeycomb for functional testing
| | [Documentation] | Configure Honeycomb with parameters for functional
| | ... | testing, then start Honeycomb and repeatedly check startup status.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure Honeycomb for functional testing \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Configure Restconf binding address | ${node}
| | Configure Log Level | ${node} | TRACE
| | Configure Persistence | ${node} | disable
| | Configure jVPP timeout | ${node} | ${14}
| | Clear Persisted Honeycomb Configuration | ${node}
| | Configure Honeycomb service on DUTs | ${node}

| Configure ODL Client for functional testing
| | [Documentation] | Read external variable HC_ODL. Depending on its
| | ... | value either: do nothing, or setup ODL client for testing and
| | ... | create a global variable that modifies Restconf requests to use ODL.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure ODL Client for functional testing \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ${use_odl_client}= | Get Variable Value | ${HC_ODL}
| | Run Keyword If | '${use_odl_client}' != '${NONE}'
| | ... | Run Keywords
| | ... | Set Global Variable | ${use_odl_client} | AND
| | ... | Configure ODL Client Service On DUT | ${node} | ${use_odl_client}
| | ... | ELSE | Log | Variable HC_ODL is not present. Not using ODL.
| | ... | level=INFO

| Set Up Honeycomb Functional Test Suite
| | [Documentation] | Generic test suite setup for Honeycomb functional tests.
| | ... | Restarts VPP, then enables Honeycomb and optionally ODL, based
| | ... | on external variable.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set Up Honeycomb Functional Test Suite \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Setup DUT | ${node}
| | Configure all TGs for traffic script
| | Configure Honeycomb for functional testing | ${node}
| | Configure ODL Client for functional testing | ${node}

| Tear Down Honeycomb Functional Test Suite
| | [Documentation] | Generic test suite teardown for Honeycomb functional
| | ... | tests. Stops ODL client (if used), then stops Honeycomb and verifies
| | ... | that they are both stopped.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear Down Honeycomb Functional Test Suite \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | ${use_odl_client}= | Get Variable Value | ${HC_ODL}
| | Run Keyword If | '${use_odl_client}' != '${NONE}'
| | ... | Run Keywords
| | ... | Stop ODL Client | ${node} | /tmp | AND
| | ... | Wait until keyword succeeds | 2min | 15sec
| | ... | Check ODL shutdown state | ${node} | AND
| | ... | Set Global Variable | ${use_odl_client} | ${NONE}
| | Stop Honeycomb service on DUTs | ${node}
| | Stop VPP Service on DUT | ${node}

| Enable Honeycomb Feature
| | [Documentation] | Enable the specified feature in Honeycomb configuration.
| | ... | Requires a restart of Honeycomb to take effect.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Enable Honeycomb Feature \| ${nodes['DUT1']} \| NSH \|
| | ...
| | [arguments] | ${node} | ${feature}
| | Manage Honeycomb Features | ${node} | ${feature}

| Disable Honeycomb Feature
| | [Documentation] | Disable the specified feature in Honeycomb configuration.
| | ... | Requires a restart of Honeycomb to take effect.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Disable Honeycomb Feature \| ${nodes['DUT1']} \| NSH \|
| | ...
| | [arguments] | ${node} | ${feature}
| | Manage Honeycomb Features | ${node} | ${feature} | disable=${True}

| Stop VPP Service on DUT
| | [Documentation] | Stop the VPP service on the specified node.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Stop VPP Service on DUT \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Stop VPP Service | ${node}

| Honeycomb Performance Suite Setup Generic
| | [Documentation] | Generic test suite setup for Honeycomb performance tests.
| | ... | Performs multiple attempts to start Honeycomb+VPP stack.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb Performance Suite Setup Generic \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Wait until keyword succeeds | 8min | 2min
| | ... | Restart Honeycomb and VPP in Performance test | ${node}

| Honeycomb Performance Suite Teardown Generic
| | [Documentation] | Generic test suite teardown for Honeycomb performance
| | ... | tests. Logs CPU usage before stopping Honeycomb.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Honeycomb Performance Suite Teardown Generic \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Log Honeycomb and VPP process distribution on cores | ${node}
| | Stop Honeycomb service on DUTs | ${node}
| | Stop VPP Service on DUT | ${node}
