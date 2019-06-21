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

*** Settings ***
| Resource | resources/libraries/robot/performance/performance_setup.robot
| ...
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | PERFTEST | HW_ENV | NDRPDR
| ... | NIC_Intel-X710 | ETH | L2BDMACLRN | L2BDBASE | SCALE | MEMIF
| ... | K8S | 1VSWITCH | 2VNF | VPP_AGENT | SFC_CONTROLLER | CHAIN
| ...
| Suite Setup | Set up 3-node performance topology with DUT's NIC model
| ... | L2 | ${nic_name}
| Suite Teardown | Tear down suite | performance
| ...
| Test Setup | Set up performance test with Ligato Kubernetes
| Test Teardown | Tear down test | ligato
| ...
| Test Template | Local Template
| ...
| Documentation | *RFC2544: Pkt throughput L2BD test cases*
| ...
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:* Eth-IPv4 for L2 bridge domain.
| ... | *[Cfg] DUT configuration:* DUT1 and DUT2 are configured with two L2
| ... | bridge domains and MAC learning enabled. DUT1 and DUT2 tested with
| ... | ${nic_name}.\
| ... | VNF Containers are connected to VSWITCH container via Memif interface.
| ... | All containers are running same VPP version. Containers are deployed
| ... | with Kubernetes. Configuration is applied by vnf-agent.
| ... | *[Ver] TG verification:* TG finds and reports throughput NDR (Non Drop\
| ... | Rate) with zero packet loss tolerance and throughput PDR (Partial Drop\
| ... | Rate) with non-zero packet loss tolerance (LT) expressed in percentage\
| ... | of packets transmitted. NDR and PDR are discovered for different\
| ... | Ethernet L2 frame sizes using MLRsearch library.\
| ... | TG traffic profile contains two L3 flow-groups
| ... | (flow-group per direction, 254 flows per flow-group) with all packets
| ... | containing Ethernet header, IPv4 header with IP protocol=61 and static
| ... | payload. MAC addresses are matching MAC addresses of the TG node
| ... | interfaces.
| ... | *[Ref] Applicable standard specifications:* RFC2544.

*** Variables ***
| ${nic_name}= | Intel-X710
| ${overhead}= | ${0}
# SFC profile
| ${sfc_profile}= | configmaps/eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain
# Traffic profile:
| ${traffic_profile}= | trex-sl-3n-ethip4-ip4src254
# CPU settings
| ${system_cpus}= | ${1}
| ${vswitch_cpus}= | ${5}
| ${vnf_cpus}= | ${2}

*** Keywords ***
| Local Template
| | [Documentation]
| | ... | [Cfg] DUT runs Container orchestrated config.
| | ... | [Ver] Measure NDR and PDR values using MLRsearch algorithm.\
| | ...
| | ... | *Arguments:*
| | ... | - frame_size - Framesize in Bytes in integer or string (IMIX_v4_1).
| | ... | Type: integer, string
| | ... | - phy_cores - Number of physical cores. Type: integer
| | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
| | ...
| | [Arguments] | ${frame_size} | ${phy_cores} | ${rxq}=${None}
| | ...
| | Set Test Variable | \${frame_size}
| | ...
| | Set Max Rate And Jumbo
| | ${dut1_if1_name}= | Get interface name | ${dut1} | ${dut1_if1}
| | ${dut1_if2_name}= | Get interface name | ${dut1} | ${dut1_if2}
| | ${dut2_if1_name}= | Get interface name | ${dut2} | ${dut2_if1}
| | ${dut2_if2_name}= | Get interface name | ${dut2} | ${dut2_if2}
| | ${tg_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | Create Kubernetes VSWITCH startup config on all DUTs
| | ... | ${phy_cores} | ${rxq} | ${jumbo}
| | Create Kubernetes VNF'1' startup config on all DUTs
| | Create Kubernetes VNF'2' startup config on all DUTs
| | Create Kubernetes CM from file on all DUTs | ${nodes} | csit
| | ... | name=vswitch-vpp-cfg | vpp.conf=/tmp/vswitch.conf
| | Create Kubernetes CM from file on all DUTs | ${nodes} | csit
| | ... | name=vnf1-vpp-cfg | vpp.conf=/tmp/vnf1.conf
| | Create Kubernetes CM from file on all DUTs | ${nodes} | csit
| | ... | name=vnf2-vpp-cfg | vpp.conf=/tmp/vnf2.conf
| | Apply Kubernetes resource on node | ${dut1}
| | ... | pods/contiv-vnf.yaml | $$VNF$$=vnf1
| | Apply Kubernetes resource on node | ${dut2}
| | ... | pods/contiv-vnf.yaml | $$VNF$$=vnf1
| | Apply Kubernetes resource on node | ${dut1}
| | ... | pods/contiv-vnf.yaml | $$VNF$$=vnf2
| | Apply Kubernetes resource on node | ${dut2}
| | ... | pods/contiv-vnf.yaml | $$VNF$$=vnf2
| | Apply Kubernetes resource on node | ${dut1}
| | ... | ${sfc_profile}.yaml | $$TEST_NAME$$=${TEST NAME}
| | ... | $$VSWITCH_IF1$$=${dut1_if1_name}
| | ... | $$VSWITCH_IF2$$=${dut1_if2_name}
| | Apply Kubernetes resource on node | ${dut2}
| | ... | ${sfc_profile}.yaml | $$TEST_NAME$$=${TEST NAME}
| | ... | $$VSWITCH_IF1$$=${dut2_if1_name}
| | ... | $$VSWITCH_IF2$$=${dut2_if2_name}
| | Wait for Kubernetes PODs on all DUTs | ${nodes} | csit
| | Set Kubernetes PODs affinity on all DUTs | ${nodes}
| | Find NDR and PDR intervals using optimized search

*** Test Cases ***
| tc01-64B-1c-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s-ndrpdr
| | [Tags] | 64B | 1C
| | frame_size=${64} | phy_cores=${1}

| tc02-64B-2c-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s-ndrpdr
| | [Tags] | 64B | 2C
| | frame_size=${64} | phy_cores=${2}

| tc03-64B-4c-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s-ndrpdr
| | [Tags] | 64B | 4C
| | frame_size=${64} | phy_cores=${4}

| tc04-1518B-1c-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s-ndrpdr
| | [Tags] | 1518B | 1C
| | frame_size=${1518} | phy_cores=${1}

| tc05-1518B-2c-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s-ndrpdr
| | [Tags] | 1518B | 2C
| | frame_size=${1518} | phy_cores=${2}

| tc06-1518B-4c-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s-ndrpdr
| | [Tags] | 1518B | 4C
| | frame_size=${1518} | phy_cores=${4}

| tc07-9000B-1c-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s-ndrpdr
| | [Tags] | 9000B | 1C
| | frame_size=${9000} | phy_cores=${1}

| tc08-9000B-2c-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s-ndrpdr
| | [Tags] | 9000B | 2C
| | frame_size=${9000} | phy_cores=${2}

| tc09-9000B-4c-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s-ndrpdr
| | [Tags] | 9000B | 4C
| | frame_size=${9000} | phy_cores=${4}

| tc10-IMIX-1c-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s-ndrpdr
| | [Tags] | IMIX | 1C
| | frame_size=IMIX_v4_1 | phy_cores=${1}

| tc11-IMIX-2c-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s-ndrpdr
| | [Tags] | IMIX | 2C
| | frame_size=IMIX_v4_1 | phy_cores=${2}

| tc12-IMIX-4c-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s-ndrpdr
| | [Tags] | IMIX | 4C
| | frame_size=IMIX_v4_1 | phy_cores=${4}
