# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""Keywords used in test teardowns."""

*** Settings ***
| Library | resources.libraries.python.DPDK.DPDKTools
| ...
| Documentation | Test terdown keywords.

*** Keywords ***
| Tear down VPP performance test
| | [Documentation]
| | ... | Common test teardown for performance tests.
| | ...
| | ... | To save space in suites, this keyword does not accept
| | ... | any explicit arguments. Instead, it requires few variables
| | ... | to be defined in at least test scope.
| | ...
| | ... | *Test Variables needed:*
| | ... | - frame_size - L2 Frame Size [B]. Type: integer
| | ... | - traffic_profile - Profile name to run debug trial with. Type: string
| | ... | - nodes - Parsed information object. Type: dict
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set Test Variable \| \${frame_size} \| 64 \|
| | ... | \| Tear down performance test \|
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show PAPI History On All DUTs | ${nodes}
| | Get Core Files on All Nodes | ${nodes}
| | Set Test Variable | ${pkt_trace} | ${True}
| | Run Keyword If Test Failed
| | ... | Traffic should pass with no loss | ${perf_trial_duration} | 10000pps
| | ... | ${frame_size} | ${traffic_profile} | fail_on_loss=${False}

| Tear down VPP device test
| | [Documentation] | Common test teardown for vpp-device tests.
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show PAPI History On All DUTs | ${nodes}
| | Show Packet Trace on All DUTs | ${nodes}
| | Vpp Show Errors On All DUTs | ${nodes}
| | Verify VPP PID in Teardown

| Tear down test with container
| | [Documentation]
| | ... | Common test teardown for tests which uses containers.
| | ...
| | Run Keyword If | "PERFTEST" in @{TEST TAGS} | Tear down VPP performance test
| | Run Keyword If | "DEVICETEST" in @{TEST TAGS} | Tear down VPP device test
| | :FOR | ${container_group} | IN | @{container_groups}
| | | Destroy all '${container_group}' containers

| Tear down test with vhost
| | [Documentation]
| | ... | Common test teardown for tests which use vhost(s) and VM(s).
| | ...
| | Run Keyword If | "PERFTEST" in @{TEST TAGS} | Tear down VPP performance test
| | Run Keyword If | "DEVICETEST" in @{TEST TAGS} | Tear down VPP device test
| | Show VPP vhost on all DUTs | ${nodes}
| | Run Keyword | vnf_manager.Kill All VMs

| Tear down test with NAT
| | [Documentation]
| | ... | Common test teardown for tests with NAT feature used.
| | ...
| | Run Keyword If | "PERFTEST" in @{TEST TAGS} | Tear down VPP performance test
| | Run Keyword If | "DEVICETEST" in @{TEST TAGS} | Tear down VPP device test
| | Show NAT verbose | ${dut1}
| | Show NAT verbose | ${dut2}

| Tear down test with ACL
| | [Documentation]
| | ... | Common test teardown for tests with ACL feature used.
| | ...
| | Run Keyword If | "PERFTEST" in @{TEST TAGS} | Tear down VPP performance test
| | Run Keyword If | "DEVICETEST" in @{TEST TAGS} | Tear down VPP device test
| | Run Keyword If Test Failed | Vpp Log Plugin Acl Settings | ${dut1}
| | Run Keyword If Test Failed | Run Keyword And Ignore Error
| | ... | Vpp Log Plugin Acl Interface Assignment | ${dut1}

| Tear down test with MACIP ACL
| | [Documentation]
| | ... | Common test teardown for tests with MACIP ACL feature used.
| | ...
| | Run Keyword If | "PERFTEST" in @{TEST TAGS} | Tear down VPP performance test
| | Run Keyword If | "DEVICETEST" in @{TEST TAGS} | Tear down VPP device test
| | Run Keyword If Test Failed | Run Keyword And Ignore Error
| | ... | Vpp Log Macip Acl Settings | ${dut1}
| | Run Keyword And Ignore Error
| | ... | Vpp Log Macip Acl Interface Assignment | ${dut1}

| Tear down performance test with SRv6 with encapsulation
| | [Documentation]
| | ... | Common test teardown for tests with SRv6 with encapsulation.
| | ...
| | Run Keyword If | "PERFTEST" in @{TEST TAGS} | Tear down VPP performance test
| | Run Keyword If | "DEVICETEST" in @{TEST TAGS} | Tear down VPP device test
| | Run Keyword If Test Failed | Show SR Policies on all DUTs | ${nodes}
| | Run Keyword If Test Failed
| | ... | Show SR Steering Policies on all DUTs | ${nodes}
| | Run Keyword If Test Failed | Show SR LocalSIDs on all DUTs | ${nodes}

| Tear down test with Ligato Kubernetes
| | [Documentation]
| | ... | Common test teardown for performance tests with Ligato Kubernetes.
| | ...
| | Run Keyword If Test Failed
| | ... | Get Kubernetes logs on all DUTs | ${nodes} | csit
| | Run Keyword If Test Failed
| | ... | Describe Kubernetes resource on all DUTs | ${nodes} | csit
| | Delete Kubernetes resource on all DUTs | ${nodes} | csit
