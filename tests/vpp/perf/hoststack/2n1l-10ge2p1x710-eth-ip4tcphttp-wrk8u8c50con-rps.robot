# Copyright (c) 2020 Cisco and/or its affiliates.
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

| Library  | resources.tools.wrk.wrk
| Resource | resources/libraries/robot/wrk/wrk_utils.robot
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/hoststack/tcp_setup.robot
|
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV
| ... | HTTP | TCP | TCP_RPS | NIC_Intel-X710 | DRV_VFIO_PCI
|
| Suite Setup | Setup suite single link | wrk
| Suite Teardown | Tear down suite | wrk
| Test Setup | Setup test
| Test Teardown | Tear down test
|
| Test Template | Local template
|
| Documentation | *HTTP requests per seconds.*
|
| ... | *[Top] Network Topologies:* TG-DUT-TG 2-node topology
| ... | with single link between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-TCP-HTTP for TCP Host Stack
| ... | *[Cfg] DUT configuration:*
| ... | *[Ver] TG verification:*
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | http_static_plugin.so
| ... | hs_apps_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | Intel-X710
| ${nic_driver}= | vfio-pci
| ${overhead}= | ${0}
| ${frame_size}= | IMIX_v4_1
| ${traffic_profile}= | wrk-sf-2n-ethip4tcphttp-8u8c50con-rps
| ${http_static_plugin}= | ${true}

*** Keywords ***
| Local template
| | [Arguments] | ${phy_cores} | ${rxq}=${None}
| |
| | Given Set Max Rate And Jumbo
| | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | FOR | ${dut} | IN | @{duts}
| | | Import Library | resources.libraries.python.VppConfigGenerator
| | | ... | WITH NAME | ${dut}
| | | Run keyword | ${dut}.Add api segment global size | 2G
| | | Run keyword | ${dut}.Add api segment api size | 1G
| | | Run keyword | ${dut}.Add TCP preallocated connections | 1000000
| | | Run keyword | ${dut}.Add TCP preallocated half open connections | 1000000
| | | Run keyword | ${dut}.Add session event queue length | 1000000
| | | Run keyword | ${dut}.Add session preallocated sessions | 1000000
| | | Run keyword | ${dut}.Add session v4 session table buckets | 500000
| | | Run keyword | ${dut}.Add session v4 session table memory | 1g
| | | Run keyword | ${dut}.Add session v4 halfopen table buckets | 2500000
| | | Run keyword | ${dut}.Add session v4 halfopen table memory | 3g
| | | Run keyword | ${dut}.Add session local endpoints table buckets | 2500000
| | | Run keyword | ${dut}.Add session local endpoints table memory | 3g
| | END
| | And Apply startup configuration on all VPP DUTs
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Set up HTTP server with parameters on the VPP node
| | ... | ${http_static_plugin} | 500000 | 4 | 4000m
| | Then Measure requests per second | ${traffic_profile}

*** Test Cases ***
| tc01-IMIX-1c-eth-ip4tcphttp-wrk8u8c50con-rps
| | [Tags] | 1C
| | phy_cores=${1}

| tc02-IMIX-2c-eth-ip4tcphttp-wrk8u8c50con-rps
| | [Tags] | 2C
| | phy_cores=${2}

| tc03-IMIX-4c-eth-ip4tcphttp-wrk8u8c50con-rps
| | [Tags] | 4C
| | phy_cores=${4}
