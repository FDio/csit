# Copyright (c) 2018 Cisco and/or its affiliates.
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
| Resource | resources/libraries/robot/performance/performance_setup.robot
| Resource | resources/libraries/robot/crypto/ipsec.robot
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | NDRPDR
| ... | IP4FWD | IPSEC | IPSECHW | IPSECTUN | NIC_Intel-XL710 | BASE
| ...
| Suite Setup | Set up IPSec performance test suite | L3 | Intel-XL710
| ... | HW_cryptodev
| ...
| Suite Teardown | Tear down 3-node performance topology
| ...
| Test Setup | Set up performance test
| ...
| Test Teardown | Tear down performance discovery test | ${min_rate}pps
| ... | ${framesize} | ${traffic_profile}
| ...
| Test Template | Local Template
| ...
| Documentation | *IPv4 IPsec tunnel mode performance test suite.*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4 on TG-DUTn,
| ... | Eth-IPv4-IPSec on DUT1-DUT2
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with multiple
| ... | IPsec tunnels between them. DUTs get IPv4 traffic from TG, encrypt it
| ... | and send to another DUT, where packets are decrypted and sent back to TG
| ... | *[Ver] TG verification:* TG finds and reports throughput NDR (Non Drop
| ... | Rate) with zero packet loss tolerance or throughput PDR (Partial Drop
| ... | Rate) with non-zero packet loss tolerance (LT) expressed in number
| ... | of packets transmitted. NDR is discovered for different
| ... | number of IPsec tunnels using MLRsearch library.
| ... | TG traffic profile contains two L3 flow-groups
| ... | (flow-group per direction, number of flows per flow-group equals to
| ... | number of IPSec tunnels) with all packets
| ... | containing Ethernet header, IPv4 header with IP protocol=61 and
| ... | static payload. MAC addresses are matching MAC addresses of the TG
| ... | node interfaces. Incrementing of IP.dst (IPv4 destination address) field
| ... | is applied to both streams.
| ... | *[Ref] Applicable standard specifications:* RFC4303 and RFC2544.

*** Variables ***
# XL710-DA2 bandwidth limit ~49Gbps/2=24.5Gbps
| ${s_24.5G}= | ${24500000000}
# XL710-DA2 Mpps limit 37.5Mpps/2=18.75Mpps
| ${s_18.75Mpps}= | ${18750000}
| ${tg_if1_ip4}= | 192.168.10.2
| ${dut1_if1_ip4}= | 192.168.10.1
| ${dut1_if2_ip4}= | 172.168.1.1
| ${dut2_if1_ip4}= | 172.168.1.2
| ${dut2_if2_ip4}= | 192.168.20.1
| ${tg_if2_ip4}= | 192.168.20.2
| ${raddr_ip4}= | 20.0.0.0
| ${laddr_ip4}= | 10.0.0.0
| ${addr_range}= | ${32}
| ${overhead}= | ${58}
| ${n_tunnels}= | ${1}
# Traffic profile:
| ${traffic_profile}= | trex-sl-3n-ethip4-ip4dst${n_tunnels}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] DUTs run 1 IPsec tunnel CBC-SHA1 in each direction.
| | ... | Each DUT uses ${phy_cores} physical core(s) for worker threads.
| | ... | [Ver] Measure NDR and PDR values using MLRsearch algorithm.\
| | ...
| | ... | *Arguments:*
| | ... | - framesize - Framesize in Bytes in integer or string (IMIX_v4_1).
| | ... | Type: integer, string
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
| | ...
| | [Arguments] | ${framesize} | ${phy_cores} | ${rxq}=${None}
| | ...
| | Set Test Variable | ${framesize}
| | Set Test Variable | ${min_rate} | ${10000}
| | ${encr_alg} = | Crypto Alg AES CBC 128
| | ${auth_alg} = | Integ Alg SHA1 96
| | ...
| | Given Add worker threads and rxqueues to all DUTs | ${phy_cores} | ${rxq}
| | And Add PCI devices to all DUTs
| | ${max_rate} | ${jumbo} = | Get Max Rate And Jumbo And Handle Multi Seg
| | ... | ${s_24.5G} | ${framesize} | overhead=${overhead}
| | ... | pps_limit=${s_18.75Mpps}
| | And Add cryptodev to all DUTs | ${phy_cores}
| | And Add DPDK dev default RXD to all DUTs | 2048
| | And Add DPDK dev default TXD to all DUTs | 2048
| | And Apply startup configuration on all VPP DUTs
| | When Generate keys for IPSec | ${encr_alg} | ${auth_alg}
| | And Initialize IPSec in 3-node circular topology
| | And Vpp Route Add | ${dut1} | ${raddr_ip4} | 8 | ${dut2_if1_ip4}
| | ... | ${dut1_if2}
| | And Vpp Route Add | ${dut2} | ${laddr_ip4} | 8 | ${dut1_if2_ip4}
| | ... | ${dut2_if1}
| | And VPP IPsec Add Multiple Tunnels
| | ... | ${dut1} | ${dut2} | ${dut1_if2} | ${dut2_if1} | ${n_tunnels}
| | ... | ${encr_alg} | ${encr_key} | ${auth_alg} | ${auth_key}
| | ... | ${dut1_if2_ip4} | ${dut2_if1_ip4} | ${laddr_ip4} | ${raddr_ip4}
| | ... | ${addr_range}
| | Then Find NDR and PDR intervals using optimized search
| | ... | ${framesize} | ${traffic_profile} | ${min_rate} | ${max_rate}

*** Test Cases ***
| tc01-64B-1c-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdr
| | [Tags] | 64B | 1C
| | framesize=${64} | phy_cores=${1}

| tc02-64B-2c-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdr
| | [Tags] | 64B | 2C
| | framesize=${64} | phy_cores=${2}

| tc03-64B-4c-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdr
| | [Tags] | 64B | 4C
| | framesize=${64} | phy_cores=${4}

| tc04-1518B-1c-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdr
| | [Tags] | 1518B | 1C
| | framesize=${1518} | phy_cores=${1}

| tc05-1518B-2c-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdr
| | [Tags] | 1518B | 2C
| | framesize=${1518} | phy_cores=${2}

| tc06-1518B-4c-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdr
| | [Tags] | 1518B | 4C
| | framesize=${1518} | phy_cores=${4}

| tc07-9000B-1c-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdr
| | [Tags] | 9000B | 1C
| | framesize=${9000} | phy_cores=${1}

| tc08-9000B-2c-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdr
| | [Tags] | 9000B | 2C
| | framesize=${9000} | phy_cores=${2}

| tc09-9000B-4c-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdr
| | [Tags] | 9000B | 4C
| | framesize=${9000} | phy_cores=${4}

| tc10-IMIX-1c-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdr
| | [Tags] | IMIX | 1C
| | framesize=IMIX_v4_1 | phy_cores=${1}

| tc11-IMIX-2c-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdr
| | [Tags] | IMIX | 2C
| | framesize=IMIX_v4_1 | phy_cores=${2}

| tc12-IMIX-4c-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdr
| | [Tags] | IMIX | 4C
| | framesize=IMIX_v4_1 | phy_cores=${4}
