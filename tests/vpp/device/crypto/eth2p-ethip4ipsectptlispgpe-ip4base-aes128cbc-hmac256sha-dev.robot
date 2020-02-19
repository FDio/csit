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
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/crypto/ipsec.robot
|
| Variables | resources/test_data/lisp/performance/lisp_static_adjacency.py
| Variables | resources/test_data/lisp/lisp.py
| Force Tags | 2_NODE_SINGLE_LINK_TOPO | DEVICETEST | HW_ENV | DCR_ENV | SCAPY
| ... | IP4FWD | LISPGPE | IPSEC | IPSECHW | IPSECTRAN | ENCAP | IP4UNRLAY
| ... | IP4OVRLAY | NIC_Virtual | AES_128_CBC | HMAC_SHA_256 | HMAC | AES
| ... | DRV_VFIO_PCI
| ... | ethip4ipsectptlispgpe-ip4base-aes128cbc-hmac256sha
|
| Suite Setup | Setup suite single link | scapy
| Test Setup | Setup test
| Test Teardown | Tear down test | packet_trace
|
| Test Template | Local Template
|
| Documentation | *IPv4 IPsec transport mode test suite.*
|
| ... | *[Top] Network Topologies:* TG-DUT1-TG 2-node circular topology\
| ... | with single links between nodes.
| ... | *[Cfg] DUT configuration:* DUT1 is configured with LISP and IPsec\
| ... | in each direction. IPsec is in transport mode. DUTs get IPv4 traffic\
| ... | from TG, encrypt it and send to TG.
| ... | *[Ver] TG verification:ESP packet is sent from TG to DUT1. ESP packet
| ... | is received on TG from DUT1.
| ... | *[Ref] Applicable standard specifications:* RFC6830, RFC4303 and\
| ... | RFC2544.

*** Variables ***
| @{plugins_to_enable}= | dpdk_plugin.so | crypto_native_plugin.so
| ... | crypto_ipsecmb_plugin.so | crypto_openssl_plugin.so
| ${crypto_type}= | ${None}
| ${nic_name}= | virtual
| ${nic_driver}= | vfio-pci
| ${osi_layer}= | L3
| ${overhead}= | ${58}
| ${tg_spi}= | ${1000}
| ${dut_spi}= | ${1001}
| ${ESP_PROTO}= | ${50}
| ${tg_if1_ip4}= | 6.0.0.2
| ${dut_if1_ip4}= | 6.0.0.1
| ${tg_if2_ip4}= | 6.0.1.2
| ${dut_if2_ip4}= | 6.0.1.1
| ${tg_lo_ip4}= | 6.0.0.2
| ${dut_lo_ip4}= | 6.0.2.2
| ${tg_host_ip4}= | 6.0.0.2
| ${ip4_plen}= | ${24}
| ${is_gpe}= | ${1}
| ${vni_table}= | ${1}
| ${vrf_table}= | ${1}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] DUT is configured with LISP and IPsec in each direction.\
| | ... | IPsec is in transport mode.
| | ... | DUT uses ${phy_cores} physical core(s) for worker threads.
| |
| | ... | *Arguments:*
| | ... | - frame_size - Framesize in Bytes in integer or string (IMIX_v4_1).
| | ... | Type: integer, string
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
| |
| | [Arguments] | ${frame_size} | ${phy_cores} | ${rxq}=${None}
| |
| | Set Test Variable | \${frame_size}
| |
| | # These are enums (not strings) so they cannot be in Variables table.
| | ${encr_alg}= | Crypto Alg AES CBC 128
| | ${auth_alg}= | Integ Alg SHA 256 128
| |
| | Given Set Max Rate And Jumbo
| | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
| | And Pre-initialize layer driver | ${nic_driver}
| | And Apply startup configuration on all VPP DUTs
| | When Initialize layer driver | ${nic_driver}
| | And Initialize layer interface
| | And Configure topology for IPv4 IPsec testing
| | And Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | And Configure LISP in 2-node circular topology
| | ... | ${dut1} | ${dut1_if2} | ${NONE}
| | ... | ${duts_locator_set} | ${dut1_ip4_eid}
| | ... | ${dut1_ip4_static_adjacency} | ${is_gpe} | ${vni_table} | ${vrf_table}
| | And Configure manual keyed connection for IPSec
| | ... | ${dut1} | ${dut1_if1} | ${encr_alg} | ${encr_key} | ${auth_alg}
| | ... | ${auth_key} | ${dut_spi} | ${tg_spi} | ${tg_if2_ip4} | ${tg_if1_ip4}
| | Then Send IPsec Packet and verify ESP encapsulation in received packet
| | ... | ${tg} | ${tg_if1} | ${tg_if2} | ${dut1_if1_mac} | ${dut1_if2_mac}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key} | ${tg_spi}
| | ... | ${dut_spi} | ${tg_if1_ip4} | ${tg_if2_ip4}

*** Test Cases ***
| tc01-64B-1c-ethip4ipsectptlispgpe-ip4base-aes128cbc-hmac256sha-dev
| | [Tags] | 64B | 1C
| | frame_size=${64} | phy_cores=${1}
