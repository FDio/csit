# Copyright (c) 2024 Intel and/or its affiliates.
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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/hoststack/hoststack.robot
|
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV
| ... | HOSTSTACK | LDP_NGINX | TCP | NIC_Intel-X710 | DRV_VFIO_PCI
| ... | TCP_RPS | DMA
| ... | eth-ip4tcphttp-dma-ldpreload-nginx-1_21_5
|
| Suite Setup | Setup suite topology interfaces | ab | nginx
| Suite Teardown | Tear down suite | ab
| Test Setup | Setup test
| Test Teardown | Tear down test | nginx
|
| Test Template | Local Template
|
| Documentation | **TCP requests per seconds.**
| ... |
| ... | - **[Top] Network Topologies:** TG-DUT-TG 2-node topology \
| ... | with single link between nodes.
| ... |
| ... | - **[Enc] Packet Encapsulations:** Eth-IPv4-TCP-HTTP for TCP
| ... |
| ... | - **[Cfg] DUT configuration:**
| ... |
| ... | - **[Ver] TG verification:**
| ... |
| ... | - **[Ref] Applicable standard specifications:**

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | perfmon_plugin.so
| ... | dma_intel_plugin.so | ping_plugin.so
| ${nic_name}= | Intel-X710
| ${crypto_type}= | ${None}
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${0}
| ${dpdk_enable_tcp_udp_checksum}= | ${True}
| ${dpdk_no_tx_checksum_offload}= | ${False}
#| ${page_size}= | 1G
| ${ciphers}= | 0
| ${rps_cps}= | rps
| ${qat}= | ${0}
| ${r_total}= | ${1000000}
| ${c_total}= | ${2000}
| ${listen_port}= | ${80}
| ${mode}= | ldp
| ${tls_tcp}= | tcp
| ${keep_time}= | 300
| ${ab_ip_prefix}= | 24
| @{ab_ip_addrs}= | 192.168.10.2
| ${dut_ip_prefix}= | 24
| @{dut_ip_addrs}= | 192.168.10.1
| ${nginx_version}= | 1.21.5
| ${use_dma}= | ${True}

*** Keywords ***
| Local template
| | [Arguments] | ${frame_size} | ${phy_cores} | ${rxq}=${None}
| |
| | Set Test Variable | \${frame_size}
| | Given Set Max Rate And Jumbo
| | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | And Add Additional Startup Configuration For DMA On All DUTs
| | And Apply startup configuration on all VPP DUTs
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Set up LDP or VCL Nginx on DUT1 node | ${mode}
| | ... | ${rps_cps} | ${phy_cores} | ${qat} | ${tls_tcp}
| | ... | ${True}
| | And Additional Suite Setup Action For ab
| | Then Measure TLS requests or connections per second
| | ... | ${ciphers} | ${frame_size} | ${tls_tcp} | ${rps_cps}

*** Test Cases ***
| 0B-1c-eth-ip4tcphttp-dma-ldpreload-nginx-1_21_5-rps
| | [Tags] | 0B | 1C
| | frame_size=${0} | phy_cores=${1}

| 0B-2c-eth-ip4tcphttp-dma-ldpreload-nginx-1_21_5-rps
| | [Tags] | 0B | 2C
| | frame_size=${0} | phy_cores=${2}

| 64B-1c-eth-ip4tcphttp-dma-ldpreload-nginx-1_21_5-rps
| | [Tags] | 64B | 1C
| | frame_size=${64} | phy_cores=${1}

| 64B-2c-eth-ip4tcphttp-dma-ldpreload-nginx-1_21_5-rps
| | [Tags] | 64B | 2C
| | frame_size=${64} | phy_cores=${2}

| 1024B-1c-eth-ip4tcphttp-dma-ldpreload-nginx-1_21_5-rps
| | [Tags] | 1024B | 1C
| | frame_size=${1024} | phy_cores=${1}

| 1024B-2c-eth-ip4tcphttp-dma-ldpreload-nginx-1_21_5-rps
| | [Tags] | 1024B | 2C
| | frame_size=${1024} | phy_cores=${2}

| 2048B-1c-eth-ip4tcphttp-dma-ldpreload-nginx-1_21_5-rps
| | [Tags] | 2048B | 1C
| | frame_size=${2048} | phy_cores=${1}

| 2048B-2c-eth-ip4tcphttp-dma-ldpreload-nginx-1_21_5-rps
| | [Tags] | 2048B | 2C
| | frame_size=${2048} | phy_cores=${2}
