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
| Documentation | Test teardown keywords.

*** Keywords ***
| Tear down test
| | [Documentation]
| | ... | Common test teardown for tests with no additional post processing.
| | ...
| | [Arguments] | @{actions}
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show PAPI History On All DUTs | ${nodes}
| | Get Core Files on All Nodes | ${nodes}
| | Verify VPP PID in Teardown
| | :FOR | ${action} | IN | @{actions}
| | | Run Keyword | Tear down test with ${action}

| Tear down test with performance
| | [Documentation]
| | ... | Additional teardown for tests which uses containers.
| | ...
| | Set Test Variable | ${pkt_trace} | ${True}
| | Run Keyword If Test Failed
| | ... | Traffic should pass with no loss | ${perf_trial_duration} | 10000pps
| | ... | ${frame_size} | ${traffic_profile} | fail_on_loss=${False}

| Tear down test with packet_trace
| | [Documentation]
| | ... | Additional teardown for tests which shows packet trace.
| | ...
| | Show Packet Trace on All DUTs | ${nodes}

| Tear down test with container
| | [Documentation]
| | ... | Additional teardown for tests which uses containers.
| | ...
| | :FOR | ${container_group} | IN | @{container_groups}
| | | Destroy all '${container_group}' containers

| Tear down test with vhost
| | [Documentation]
| | ... | Additional teardown for tests which use vhost(s) and VM(s).
| | ...
| | Show VPP vhost on all DUTs | ${nodes}
| | Run Keyword If | "PERFTEST" in @{TEST TAGS} | vnf_manager.Kill All VMs
| | Run Keyword If | "DEVICETEST" in @{TEST TAGS} | vm_node.Qemu Kill

| Tear down test with nat
| | [Documentation]
| | ... | Additional teardown for tests with NAT feature used.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Show NAT verbose | ${nodes['${dut}']}

| Tear down test with namespace
| | [Documentation]
| | ... | Additional teardown for tests with namespace used.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Clean Up Namespaces | ${nodes['${dut}']}

| Tear down test with linux_bridge
| | [Documentation]
| | ... | Additional teardown for tests with linux_bridge used.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Linux Del Bridge | ${nodes['${dut}']} | ${bid_TAP}

| Tear down test with acl
| | [Documentation]
| | ... | Additional teardown for tests with ACL feature used.
| | ...
| | Run Keyword If Test Failed | Vpp Log Plugin Acl Settings | ${dut1}
| | Run Keyword If Test Failed | Run Keyword And Ignore Error
| | ... | Vpp Log Plugin Acl Interface Assignment | ${dut1}

| Tear down test with macipacl
| | [Documentation]
| | ... | Additional teardown for tests with MACIP ACL feature used.
| | ...
| | Run Keyword If Test Failed | Run Keyword And Ignore Error
| | ... | Vpp Log Macip Acl Settings | ${dut1}
| | Run Keyword And Ignore Error
| | ... | Vpp Log Macip Acl Interface Assignment | ${dut1}

| Tear down test with srv6
| | [Documentation]
| | ... | Additional teardown for tests with SRv6.
| | ...
| | Run Keyword If Test Failed | Show SR Policies on all DUTs | ${nodes}
| | Run Keyword If Test Failed
| | ... | Show SR Steering Policies on all DUTs | ${nodes}
| | Run Keyword If Test Failed | Show SR LocalSIDs on all DUTs | ${nodes}

| Tear down test with ligato
| | [Documentation]
| | ... | Additional teardown for performance tests with Ligato.
| | ...
| | Run Keyword If Test Failed
| | ... | Get Kubernetes logs on all DUTs | ${nodes} | csit
| | Run Keyword If Test Failed
| | ... | Describe Kubernetes resource on all DUTs | ${nodes} | csit
| | Delete Kubernetes resource on all DUTs | ${nodes} | csit
