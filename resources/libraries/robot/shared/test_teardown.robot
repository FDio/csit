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
| Resource | resources/libraries/robot/shared/container.robot
| Library | resources.libraries.python.PapiHistory
| Library | resources.libraries.python.topology.Topology
| ...
| Documentation | Test teardown keywords.

*** Keywords ***
| Tear down test
| | [Documentation]
| | ... | Common test teardown for tests.
| | ...
| | ... | *Arguments:*
| | ... | - ${actions} - Additional teardown action. Type: list
| | ...
| | [Arguments] | @{actions}
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show PAPI History On All DUTs | ${nodes}
| | Run Keyword If Test Failed
| | ... | Get Core Files on All Nodes | ${nodes}
| | Run Keyword If Test Failed
| | ... | Verify VPP PID in Teardown
| | :FOR | ${action} | IN | @{actions}
| | | Run Keyword | Additional Test Tear Down Action For ${action}
| | Clean Sockets On All Nodes | ${nodes}

| Additional Test Tear Down Action For performance
| | [Documentation]
| | ... | Additional teardown for tests which uses performance measurement.
| | ...
| | Run Keyword If Test Failed
| | ... | Send traffic at specified rate | ${perf_trial_duration} | 10000pps
| | ... | ${frame_size} | ${traffic_profile} | pkt_trace=${True}

| Additional Test Tear Down Action For packet_trace
| | [Documentation]
| | ... | Additional teardown for tests which uses packet trace.
| | ...
| | Show Packet Trace on All DUTs | ${nodes}

| Additional Test Tear Down Action For container
| | [Documentation]
| | ... | Additional teardown for tests which uses containers.
| | ...
| | :FOR | ${container_group} | IN | @{container_groups}
| | | Destroy all '${container_group}' containers

| Additional Test Tear Down Action For vhost
| | [Documentation]
| | ... | Additional teardown for tests which uses vhost(s) and VM(s).
| | ...
| | Show VPP vhost on all DUTs | ${nodes}
| | ${vnf_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Keyword Should Exist | vnf_manager.Kill All VMs
| | Run Keyword If | '${vnf_status}' == 'PASS' | vnf_manager.Kill All VMs

| Additional Test Tear Down Action For nat
| | [Documentation]
| | ... | Additional teardown for tests which uses NAT feature.
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Run Keyword If Test Failed
| | | ... | Show NAT verbose | ${nodes['${dut}']}

| Additional Test Tear Down Action For namespace
| | [Documentation]
| | ... | Additional teardown for tests which uses namespace.
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Clean Up Namespaces | ${nodes['${dut}']}

| Additional Test Tear Down Action For linux_bridge
| | [Documentation]
| | ... | Additional teardown for tests which uses linux_bridge.
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Linux Del Bridge | ${nodes['${dut}']} | ${bid_TAP}

| Additional Test Tear Down Action For acl
| | [Documentation]
| | ... | Additional teardown for tests which uses ACL feature.
| | ...
| | Run Keyword If Test Failed
| | ... | Vpp Log Plugin Acl Settings | ${dut1}
| | Run Keyword If Test Failed
| | ... | Vpp Log Plugin Acl Interface Assignment | ${dut1}

| Additional Test Tear Down Action For macipacl
| | [Documentation]
| | ... | Additional teardown for tests which uses MACIP ACL feature.
| | ...
| | Run Keyword If Test Failed
| | ... | Vpp Log Macip Acl Settings | ${dut1}
| | Run Keyword If Test Failed
| | ... | Vpp Log Macip Acl Interface Assignment | ${dut1}

| Additional Test Tear Down Action For srv6
| | [Documentation]
| | ... | Additional teardown for tests which uses SRv6.
| | ...
| | Run Keyword If Test Failed
| | ... | Show SR Policies on all DUTs | ${nodes}
| | Run Keyword If Test Failed
| | ... | Show SR Steering Policies on all DUTs | ${nodes}
| | Run Keyword If Test Failed
| | ... | Show SR LocalSIDs on all DUTs | ${nodes}

| Additional Test Tear Down Action For ligato
| | [Documentation]
| | ... | Additional teardown for performance tests with Ligato.
| | ...
| | Run Keyword If Test Failed
| | ... | Get Kubernetes logs on all DUTs | ${nodes} | csit
| | Run Keyword If Test Failed
| | ... | Describe Kubernetes resource on all DUTs | ${nodes} | csit
| | Delete Kubernetes resource on all DUTs | ${nodes} | csit
