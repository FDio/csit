# Copyright (c) 2023 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/shared/default.robot
| Library | resources.libraries.python.PapiHistory
| Library | resources.libraries.python.topology.Topology
| Variables | resources/libraries/python/Constants.py
|
| Documentation | Test teardown keywords.

*** Keywords ***
| Tear down test
| | [Documentation]
| | ... | Common test teardown for VPP tests.
| |
| | ... | *Arguments:*
| | ... | - ${actions} - Additional teardown action. Type: list
| |
| | [Arguments] | @{actions}
| |
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show PAPI History On All DUTs | ${nodes}
| | Show Log On All DUTs | ${nodes}
| | Run Keyword If Test Failed
| | ... | Get Core Files on All Nodes | ${nodes}
| | Run Keyword If Test Failed
| | ... | Verify VPP PID in Teardown
| | Run Keyword If Test Failed
| | ... | VPP Show Memory On All DUTs | ${nodes}
| | FOR | ${action} | IN | @{actions}
| | | Run Keyword | Additional Test Tear Down Action For ${action}
| | END
| | Clean Sockets On All Nodes | ${nodes}
| | Finalize Test Export

| Tear down test raw
| | [Documentation]
| | ... | Common test teardown for raw tests.
| |
| | ... | *Arguments:*
| | ... | - ${actions} - Additional teardown action. Type: list
| |
| | [Arguments] | @{actions}
| |
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | FOR | ${action} | IN | @{actions}
| | | Run Keyword | Additional Test Tear Down Action For ${action}
| | END
| | Clean Sockets On All Nodes | ${nodes}
| | Finalize Test Export

# Additional Test Tear Down Actions in alphabetical order
| Additional Test Tear Down Action For acl
| | [Documentation]
| | ... | Additional teardown for tests which uses ACL feature.
| |
| | Run Keyword If Test Failed
| | ... | Vpp Log Plugin Acl Settings | ${dut1}
| | Run Keyword If Test Failed
| | ... | Vpp Log Plugin Acl Interface Assignment | ${dut1}

| Additional Test Tear Down Action For classify
| | [Documentation]
| | ... | Additional teardown for tests which uses classify tables.
| |
| | Run Keyword If Test Failed
| | ... | Show Classify Tables Verbose on all DUTs | ${nodes}

| Additional Test Tear Down Action For container
| | [Documentation]
| | ... | Additional teardown for tests which uses containers.
| |
| | FOR | ${container_group} | IN | @{container_groups}
| | | Destroy all '${container_group}' containers
| | END

| Additional Test Tear Down Action For nginx
| | [Documentation]
| | ... | Additional teardown for tests which uses nginx.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Kill Program | ${nodes['${dut}']} | nginx
| | END

| Additional Test Tear Down Action For det44
| | [Documentation]
| | ... | Additional teardown for tests which uses DET44 feature.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword If Test Failed
| | | ... | Show DET44 verbose | ${nodes['${dut}']}
| | END

| Additional Test Tear Down Action For geneve4
| | [Documentation]
| | ... | Additional teardown for tests which uses GENEVE IPv4 tunnel.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword If Test Failed
| | | ... | Show Geneve Tunnel Data | ${nodes['${dut}']}
| | END

| Additional Test Tear Down Action For iPerf3
| | [Documentation]
| | ... | Additional teardown for test which uses iPerf3 server.
| |
| | Run Keyword And Ignore Error
| | ... | Teardown iPerf | ${nodes['${iperf_server_node}']}

| Additional Test Tear Down Action For ipsec_sa
| | [Documentation]
| | ... | Additional teardown for tests which uses IPSec security association.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword If Test Failed
| | | ... | Show Ipsec Security Association | ${nodes['${dut}']}
| | END

| Additional Test Tear Down Action For ipsec_all
| | [Documentation]
| | ... | Additional teardown for tests which use varied IPSec configuration.
| | ... | Databases.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword If Test Failed
| | | ... | Vpp Ipsec Show All | ${nodes['${dut}']}
| | END

| Additional Test Tear Down Action For linux_bridge
| | [Documentation]
| | ... | Additional teardown for tests which uses linux_bridge.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Linux Del Bridge | ${nodes['${dut}']} | ${bid_TAP}
| | END

| Additional Test Tear Down Action For macipacl
| | [Documentation]
| | ... | Additional teardown for tests which uses MACIP ACL feature.
| |
| | Run Keyword If Test Failed
| | ... | Vpp Log Macip Acl Settings | ${dut1}
| | Run Keyword If Test Failed
| | ... | Vpp Log Macip Acl Interface Assignment | ${dut1}

| Additional Test Tear Down Action For namespace
| | [Documentation]
| | ... | Additional teardown for tests which uses namespace.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Clean Up Namespaces | ${nodes['${dut}']}
| | END

| Additional Test Tear Down Action For nat-ed
| | [Documentation]
| | ... | Additional teardown for tests which uses NAT feature.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Show NAT44 Config | ${nodes['${dut}']}
| | | Show NAT44 Summary | ${nodes['${dut}']}
| | | Show NAT Base Data | ${nodes['${dut}']}
| | | Vpp Get Ip Table Summary | ${nodes['${dut}']}
| | END

| Additional Test Tear Down Action For packet_trace
| | [Documentation]
| | ... | Additional teardown for tests which uses packet trace.
| |
| | Show Packet Trace on All DUTs | ${nodes}

| Additional Test Tear Down Action For telemetry
| | [Documentation]
| | ... | Additional teardown for tests which uses telemetry reads.
| |
| | Run Telemetry On All DUTs
| | ... | ${nodes} | profile=${telemetry_profile}.yaml

| Additional Test Tear Down Action For performance
| | [Documentation]
| | ... | Additional teardown for tests which uses performance measurement.
| | ... | Optionally, call \${resetter} (if defined) to reset DUT state.
| |
| | Run Keyword If Test Passed | Return From Keyword
| | ${use_latency} = | Get Use Latency
| | ${rate_for_teardown} = | Get Rate For Teardown
| | Call Resetter
| | Set Test Variable | \${extended_debug} | ${True}
| | Set Test Variable | ${telemetry_rate} | ${EMPTY}
| | Set Test Variable | ${telemetry_export} | ${False}
| | Send traffic at specified rate
| | ... | trial_duration=${1.0}
| | ... | rate=${rate_for_teardown}
| | ... | trial_multiplicity=${1}
| | ... | use_latency=${use_latency}
| | ... | duration_limit=${1.0}

| Additional Test Tear Down Action For srv6
| | [Documentation]
| | ... | Additional teardown for tests which uses SRv6.
| |
| | Run Keyword If Test Failed
| | ... | Show SR Policies on all DUTs | ${nodes}
| | Run Keyword If Test Failed
| | ... | Show SR Steering Policies on all DUTs | ${nodes}
| | Run Keyword If Test Failed
| | ... | Show SR LocalSIDs on all DUTs | ${nodes}

| Additional Test Tear Down Action For vhost
| | [Documentation]
| | ... | Additional teardown for tests which uses vhost(s) and VM(s).
| |
| | Show VPP vhost on all DUTs | ${nodes}
| | ${vnf_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Keyword Should Exist | vnf_manager.Kill All VMs
| | Run Keyword If | '${vnf_status}' == 'PASS' | vnf_manager.Kill All VMs

| Additional Test Tear Down Action For vhost-pt
| | [Documentation]
| | ... | Additional teardown for tests which uses pci-passtrough and VM(s).
| |
| | ${vnf_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Keyword Should Exist | vnf_manager.Kill All VMs
| | Run Keyword If | '${vnf_status}' == 'PASS' | vnf_manager.Kill All VMs
