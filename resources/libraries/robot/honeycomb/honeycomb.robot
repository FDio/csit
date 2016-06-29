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

*** Settings ***
| Library | resources/libraries/python/honeycomb/HoneycombSetup.py
| Library | resources/libraries/python/honeycomb/HoneycombUtil.py

*** Keywords ***
| Setup Honeycomb service on DUTs
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
| | Wait until keyword succeeds | 10min | 20sec
| | ... | Check honeycomb startup state | @{duts}

| Stop honeycomb service on DUTs
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
| | Wait until keyword succeeds | 2m | 10s
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
| | [Arguments] | @{duts}
| | Clear persisted Honeycomb config | @{duts}