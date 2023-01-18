# Copyright (c) 2023 Intel and/or its affiliates.
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
| ... | eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5
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
| ... | dma_intel_plugin.so
| ${nic_name}= | Intel-X710
| ${crypto_type}= | ${None}
| ${nic_driver}= | vfio-pci
| ${nic_rxq_size}= | 0
| ${nic_txq_size}= | 0
| ${nic_pfs}= | 2
| ${nic_vfs}= | 0
| ${overhead}= | ${0}
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
| @{ab_ip_addrs}= | 192.168.10.2 | 192.168.11.2
| ${dut_ip_prefix}= | 24
| @{dut_ip_addrs}= | 192.168.10.1 | 192.168.11.1
| ${nginx_version}= | 1.21.5

*** Keywords ***
| Local template
| | [Arguments] | ${frame_size} | ${vpp_cores} | ${rxq}=${None}
| | ... | ${nginx_cores}=${None}
| |
| | ${frame_size}= | Run Keyword If | 'KB' in '${frame_size}'
| | ... | Evaluate | int('${frame_size}'.replace('KB', ''))*1024
| | ... | ELSE | Set Variable | ${frame_size}
| | Set Test Variable | \${frame_size}
| | Set Test Variable | ${dpdk_no_tx_checksum_offload} | ${False}
| | Set Test Variable | ${nginx_cores}
| | Given Set Max Rate And Jumbo
| | And Add worker threads to all DUTs | ${vpp_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | And Add additional startup configuration for DMA on all DUTs | ${False}
| | Apply startup configuration on all VPP DUTs
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Set up LDP or VCL Nginx on DUT node | ${dut1} | ${mode}
| | ... | ${rps_cps} | ${nginx_cores} | ${qat} | ${tls_tcp}
| | ... | enable_hugepage=${True} | ratio=${1}
| | ${phy_cores} | Evaluate | int(${vpp_cores}+${nginx_cores})
| | Regenerate tag with Nginx cores | ${phy_cores}
| | And Additional Suite Setup Action For ab
| | Then Measure TLS requests or connections per second
| | ... | ${ciphers} | ${frame_size} | ${tls_tcp} | ${rps_cps}

*** Test Cases ***
| 0B-2c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 0B | 2C
| | frame_size=${0} | vpp_cores=${1} | nginx_cores=${1}

| 0B-3c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 0B | 3C
| | frame_size=${0} | vpp_cores=${1} | nginx_cores=${2}

| 0B-4c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 0B | 4C
| | frame_size=${0} | vpp_cores=${1} | nginx_cores=${3}

| 64B-2c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 64B | 2C
| | frame_size=${64} | vpp_cores=${1} | nginx_cores=${1}

| 64B-3c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 64B | 3C
| | frame_size=${64} | vpp_cores=${1} | nginx_cores=${2}

| 64B-4c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 64B | 4C
| | frame_size=${64} | vpp_cores=${1} | nginx_cores=${3}

| 1KB-2c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 1KB | 2C
| | frame_size=1KB | vpp_cores=${1} | nginx_cores=${1}

| 1KB-3c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 1KB | 3C
| | frame_size=1KB | vpp_cores=${1} | nginx_cores=${2}

| 1KB-4c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 1KB | 4C
| | frame_size=1KB | vpp_cores=${1} | nginx_cores=${3}

| 2KB-2c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 2KB | 2C
| | frame_size=2KB | vpp_cores=${1} | nginx_cores=${1}

| 2KB-3c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 2KB | 3C
| | frame_size=2KB | vpp_cores=${1} | nginx_cores=${2}

| 2KB-4c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 2KB | 4C
| | frame_size=2KB | vpp_cores=${1} | nginx_cores=${3}

| 4KB-2c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 4KB | 2C
| | frame_size=4KB | vpp_cores=${1} | nginx_cores=${1}

| 4KB-3c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 4KB | 3C
| | frame_size=4KB | vpp_cores=${1} | nginx_cores=${2}

| 4KB-4c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 4KB | 4C
| | frame_size=4KB | vpp_cores=${1} | nginx_cores=${3}

| 8KB-2c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 8KB | 2C
| | frame_size=8KB | vpp_cores=${1} | nginx_cores=${1}

| 8KB-3c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 8KB | 3C
| | frame_size=8KB | vpp_cores=${1} | nginx_cores=${2}

| 8KB-4c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 8KB | 4C
| | frame_size=8KB | vpp_cores=${1} | nginx_cores=${3}

| 16KB-2c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 16KB | 2C
| | frame_size=16KB | vpp_cores=${1} | nginx_cores=${1}

| 16KB-3c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 16KB | 3C
| | frame_size=16KB | vpp_cores=${1} | nginx_cores=${2}

| 16KB-4c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 16KB | 4C
| | frame_size=16KB | vpp_cores=${1} | nginx_cores=${3}

| 32KB-2c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 32KB | 2C
| | frame_size=32KB | vpp_cores=${1} | nginx_cores=${1}

| 32KB-3c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 32KB | 3C
| | frame_size=32KB | vpp_cores=${1} | nginx_cores=${2}

| 32KB-4c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 32KB | 4C
| | frame_size=32KB | vpp_cores=${1} | nginx_cores=${3}

| 64KB-2c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 64KB | 2C
| | frame_size=64KB | vpp_cores=${1} | nginx_cores=${1}

| 64KB-3c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 64KB | 3C
| | frame_size=64KB | vpp_cores=${1} | nginx_cores=${2}

| 64KB-4c-eth-ip4tcphttp2cl-hugepage-ldpreload-nginx-1_21_5-rps
| | [Tags] | 64KB | 4C
| | frame_size=64KB | vpp_cores=${1} | nginx_cores=${3}
