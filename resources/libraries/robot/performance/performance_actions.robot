# Copyright (c) 2021 Cisco and/or its affiliates.
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
| Variables | resources/libraries/python/Constants.py
| Resource | resources/libraries/robot/performance/performance_utils.robot
|
| Documentation
| ... | Performance suite keywords - Actions related to performance tests.

*** Keywords ***
| Additional Statistics Action For bash-perf-stat
| | [Documentation]
| | ... | Additional Statistics Action for bash command "perf stat".
| |
| | Run Keyword If | ${extended_debug}==${True}
| | ... | Perf Stat On All DUTs | ${nodes} | cpu_list=${cpu_alloc_str}

| Additional Statistics Action For clear-show-runtime-with-traffic
| | [Documentation]
| | ... | Additional Statistics Action for clear and show runtime counters with
| | ... | running traffic.
| |
| | ... | See documentation of the called keyword for required test variables.
| |
| | Clear and show runtime counters with running traffic

| Additional Statistics Action For clear-show-runtime-with-iperf3
| | [Documentation]
| | ... | Additional Statistics Action for clear and show runtime counters with
| | ... | iPerf3 running traffic.
| |
| | ... | See documentation of the called keyword for required test variables.
| |
| | Clear and show runtime counters with running iperf3

| Additional Statistics Action For noop
| | [Documentation]
| | ... | Additional Statistics Action for no operation.
| |
| | No operation

| Additional Statistics Action For vpp-clear-runtime
| | [Documentation]
| | ... | Additional Statistics Action for clear VPP runtime.
| |
| | VPP Clear Runtime On All DUTs | ${nodes}

| Additional Statistics Action For vpp-clear-stats
| | [Documentation]
| | ... | Additional Statistics Action for clear VPP statistics.
| |
| | Clear Statistics On All DUTs | ${nodes}

| Additional Statistics Action For vpp-enable-elog
| | [Documentation]
| | ... | Additional Statistics Action for enable VPP elog trace.
| |
| | VPP Enable Elog Traces On All DUTs | ${nodes}

| Additional Statistics Action For vpp-enable-packettrace
| | [Documentation]
| | ... | Additional Statistics Action for enable VPP packet trace.
| |
| | Run Keyword If | ${extended_debug}==${True}
| | ... | VPP Enable Traces On All DUTs | ${nodes} | fail_on_error=${False}

| Additional Statistics Action For vpp-show-elog
| | [Documentation]
| | ... | Additional Statistics Action for show VPP elog trace.
| |
| | Show Event Logger On All DUTs | ${nodes}

| Additional Statistics Action For vpp-show-packettrace
| | [Documentation]
| | ... | Additional Statistics Action for show VPP packet trace.
| |
| | Run Keyword If | ${extended_debug}==${True}
| | ... | Show Packet Trace On All Duts | ${nodes} | maximum=${100000}

| Additional Statistics Action For vpp-show-runtime
| | [Documentation]
| | ... | Additional Statistics Action for show VPP runtime.
| |
| | VPP Show Runtime On All DUTs | ${nodes}

| Additional Statistics Action For vpp-show-stats
| | [Documentation]
| | ... | Additional Statistics Action for show VPP statistics.
| |
| | Show Statistics On All DUTs | ${nodes}
