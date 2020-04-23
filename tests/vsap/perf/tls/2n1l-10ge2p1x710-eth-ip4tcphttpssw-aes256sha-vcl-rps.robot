# Copyright (c) 2020 Intel and/or its affiliates.
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

| Library  | resources.libraries.python.vsap.ab
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/suite_setup.robot
| Resource | resources/libraries/robot/vsap/ab_utils.robot
| Resource | resources/libraries/robot/vsap/vsap_utils.robot
|
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV
| ... | NGINX | TLS | TLS_RPS | AES256-SHA | NIC_Intel-X710 | DRV_VFIO_PCI
| ... | eth-ip4tcphttpssw-aes256sha-vcl
|
| Suite Setup | Setup suite topology interfaces | ab
| Suite Teardown | Tear down suite | ab
| Test Setup | Setup test
| Test Teardown | Tear down test
|
| Test Template | Local Template
|
| Documentation | *TLS requests per seconds.*
|
| ... | *[Top] Network Topologies:* TG-DUT-TG 2-node topology\
| ... | with single link between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4-TLS-HTTPS for TLS
| ... | *[Cfg] DUT configuration:*
| ... | *[Ver] TG verification:*
| ... | *[Ref] Applicable standard specifications:*

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | tlsopenssl_plugin.so
| ${nic_name}= | Intel-X710
| ${crypto_type}= | ${None}
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${0}
| ${ciphers}= | AES256-SHA
| ${rps_cps}= | rps
| ${qat}= | ${0}
| ${mode}= | vcl
| ${rxq_int}= | ${32}

*** Keywords ***
| Local template
| | [Arguments] | ${frame_size} | ${phy_cores} | ${rxq}=${None}
| |
| | Set Test Variable | \${frame_size}
| |
| | Given Set Max Rate And Jumbo
| | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | FOR | ${dut} | IN | @{duts}
| | | Import Library | resources.libraries.python.VppConfigGenerator
| | | ... | WITH NAME | ${dut}
| | | Run keyword | ${dut}.Add DPDK Dev Default RXQ | ${rxq_int}
| | | Run keyword | ${dut}.Add Session Event Queues Memfd Segment
| | | Run keyword | ${dut}.Add tcp congestion control algorithm
| | END
| | And Apply startup configuration on all VPP DUTs
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Set up VCL Nginx or LDP Nginx on DUT node | ${mode}
| | ... | ${rps_cps} | ${phy_cores} | ${qat}
| | And Additional Suite Setup Action For ab
| | Then Measure TLS requests or connections per second
| | ... | ${ciphers} | ${frame_size}

*** Test Cases ***
| tc01-0B-1c-eth-ip4tcphttpssw-aes256sha-vcl-rps
| | [Tags] | 0B | 1C
| | frame_size=${0} | phy_cores=${1}

| tc02-0B-2c-eth-ip4tcphttpssw-aes256sha-vcl-rps
| | [Tags] | 0B | 2C
| | frame_size=${0} | phy_cores=${2}

| tc03-0B-4c-eth-ip4tcphttpssw-aes256sha-vcl-rps
| | [Tags] | 0B | 4C
| | frame_size=${0} | phy_cores=${4}

| tc04-64B-1c-eth-ip4tcphttpssw-aes256sha-vcl-rps
| | [Tags] | 64B | 1C
| | frame_size=${64} | phy_cores=${1}

| tc05-64B-2c-eth-ip4tcphttpssw-aes256sha-vcl-rps
| | [Tags] | 64B | 2C
| | frame_size=${64} | phy_cores=${2}

| tc06-64B-4c-eth-ip4tcphttpssw-aes256sha-vcl-rps
| | [Tags] | 64B | 4C
| | frame_size=${64} | phy_cores=${4}

| tc07-1024B-1c-eth-ip4tcphttpssw-aes256sha-vcl-rps
| | [Tags] | 1024B | 1C
| | frame_size=${1024} | phy_cores=${1}

| tc08-1024B-2c-eth-ip4tcphttpssw-aes256sha-vcl-rps
| | [Tags] | 1024B | 2C
| | frame_size=${1024} | phy_cores=${2}

| tc09-1024B-4c-eth-ip4tcphttpssw-aes256sha-vcl-rps
| | [Tags] | 1024B | 4C
| | frame_size=${1024} | phy_cores=${4}

| tc10-2048B-1c-eth-ip4tcphttpssw-aes256sha-vcl-rps
| | [Tags] | 2048B | 1C
| | frame_size=${2048} | phy_cores=${1}

| tc11-2048B-2c-eth-ip4tcphttpssw-aes256sha-vcl-rps
| | [Tags] | 2048B | 2C
| | frame_size=${2048} | phy_cores=${2}

| tc12-2048B-4c-eth-ip4tcphttpssw-aes256sha-vcl-rps
| | [Tags] | 2048B | 4C
| | frame_size=${2048} | phy_cores=${4}
