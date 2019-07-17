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
| Variables | resources/libraries/python/topology.py
| Variables | resources/libraries/python/PapiHistory.py
| Variables | resources/libraries/python/Constants.py
| ...
| Library | Collections
| Library | OperatingSystem
| Library | String
| ...
| Library | resources.libraries.python.Classify.Classify
| Library | resources.libraries.python.CpuUtils
| Library | resources.libraries.python.CoreDumpUtil
| Library | resources.libraries.python.Cop
| Library | resources.libraries.python.DUTSetup
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.Namespaces
| Library | resources.libraries.python.PapiHistory
| Library | resources.libraries.python.SchedUtils
| Library | resources.libraries.python.Tap
| Library | resources.libraries.python.TestConfig
| Library | resources.libraries.python.TGSetup
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.VppCounters
| Library | resources.libraries.python.VPPUtil
| ...
| Resource | resources/libraries/robot/crypto/ipsec.robot
| Resource | resources/libraries/robot/features/acl.robot
| Resource | resources/libraries/robot/features/gbp.robot
| Resource | resources/libraries/robot/features/policer.robot
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/ip/ip6.robot
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
| Resource | resources/libraries/robot/l2/l2_patch.robot
| Resource | resources/libraries/robot/l2/l2_traffic.robot
| Resource | resources/libraries/robot/l2/l2_xconnect.robot
| Resource | resources/libraries/robot/l2/tagging.robot
| Resource | resources/libraries/robot/overlay/srv6.robot
| Resource | resources/libraries/robot/performance/performance_configuration.robot
| Resource | resources/libraries/robot/performance/performance_limits.robot
| Resource | resources/libraries/robot/performance/performance_utils.robot
| Resource | resources/libraries/robot/shared/counters.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/container.robot
| Resource | resources/libraries/robot/shared/memif.robot
| Resource | resources/libraries/robot/shared/suite_teardown.robot
| Resource | resources/libraries/robot/shared/suite_setup.robot
| Resource | resources/libraries/robot/shared/test_teardown.robot
| Resource | resources/libraries/robot/shared/test_setup.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| Resource | resources/libraries/robot/shared/vm.robot

*** Keywords ***
| Configure crypto device on all DUTs
| | [Documentation] | Verify if Crypto QAT device virtual functions are
| | ... | initialized on all DUTs. If parameter force_init is set to True, then
| | ... | try to initialize/disable.
| | ...
| | ... | *Arguments:*
| | ... | - crypto_type - Crypto device type - HW_DH895xcc or HW_C3xxx.
| | ... | Type: string, default value: HW_DH895xcc
| | ... | - numvfs - Number of VFs to initialize, 0 - disable the VFs
| | ... | Type: integer, default value: ${32}
| | ... | - force_init - Force to initialize. Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure crypto device on all DUTs \| HW_DH895xcc \| ${32} \|
| | ...
| | [Arguments] | ${crypto_type} | ${numvfs} | ${force_init}=${False}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Crypto Device Verify | ${nodes['${dut}']} | ${crypto_type}
| | | ... | ${numvfs} | force_init=${force_init}

| Configure kernel module on all DUTs
| | [Documentation] | Verify if specific kernel module is loaded on all DUTs.
| | ... | If parameter force_load is set to True, then try to load.
| | ...
| | ... | *Arguments:*
| | ... | - module - Module to verify. Type: string
| | ... | - force_load - Try to load module. Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure kernel module on all DUTs \| ${True} \|
| | ...
| | [Arguments] | ${module} | ${force_load}=${False}
| | ...
| | Verify Kernel Module on All DUTs | ${nodes} | ${module}
| | ... | force_load=${force_load}

| Create base startup configuration of VPP on all DUTs
| | [Documentation] | Create base startup configuration of VPP to all DUTs.
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Import Library | resources.libraries.python.VppConfigGenerator
| | | ... | WITH NAME | ${dut}
| | | Run keyword | ${dut}.Set Node |  ${nodes['${dut}']}
| | | Run keyword | ${dut}.Add Unix Log
| | | Run keyword | ${dut}.Add Unix CLI Listen
| | | Run keyword | ${dut}.Add Unix Nodaemon
| | | Run keyword | ${dut}.Add Unix Coredump
| | | Run keyword | ${dut}.Add Socksvr
| | | Run keyword | ${dut}.Add DPDK No Tx Checksum Offload
| | | Run keyword | ${dut}.Add DPDK Log Level | debug
| | | Run keyword | ${dut}.Add DPDK Uio Driver
| | | Run keyword | ${dut}.Add Heapsize | 4G
| | | Run keyword | ${dut}.Add Statseg size | 4G
| | | Run keyword | ${dut}.Add Statseg Per Node Counters | on
| | | Run keyword | ${dut}.Add Plugin | disable | default
| | | Run keyword | ${dut}.Add Plugin | enable | @{plugins_to_enable}
| | | Run keyword | ${dut}.Add IP6 Hash Buckets | 2000000
| | | Run keyword | ${dut}.Add IP6 Heap Size | 4G
| | | Run keyword | ${dut}.Add IP Heap Size | 4G

| Add worker threads and rxqueues to all DUTs
| | [Documentation] | Setup worker threads and rxqueues in vpp startup
| | ... | configuration on all DUTs. Based on the SMT configuration of DUT if
| | ... | enabled keyword will automatically map also the sibling logical cores.
| | ... | Keyword will automatically set the appropriate test TAGs in format
| | ... | mTnC, where m=logical_core_count and n=physical_core_count.
| | ...
| | ... | *Arguments:*
| | ... | - phy_cores - Number of physical cores to use. Type: integer
| | ... | - rx_queues - Number of RX queues. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Add worker threads and rxqueues to all DUTs \| ${1} \| ${1} \|
| | ...
| | [Arguments] | ${phy_cores} | ${rx_queues}=${None}
| | ...
| | ${cpu_count_int} | Convert to Integer | ${phy_cores}
| | ${thr_count_int} | Convert to Integer | ${phy_cores}
| | :FOR | ${dut} | IN | @{duts}
| | | Add worker threads and rxqueues to DUT | ${dut} | ${phy_cores} |
| | | ... | ${None}

| Add worker threads and rxqueues to DUT
| | [Documentation] | Setup worker threads and rxqueues in vpp startup
| | ... | configuration on DUT. Based on the SMT configuration of DUT if
| | ... | enabled keyword will automatically map also the sibling logical cores.
| | ... | Keyword will automatically set the appropriate test TAGs in format
| | ... | mTnC, where m=logical_core_count and n=physical_core_count.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT on which to set the worker threads and rxqueues
| | ... | - phy_cores - Number of physical cores to use. Type: integer
| | ... | - rx_queues - Number of RX queues. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Add worker threads and rxqueues to DUT \| DUT1
| | ... | \| ${1} \| ${1} \|
| | ...
| | [Arguments] | ${dut} | ${phy_cores} | ${rx_queues}=${None}
| | ...
| | ${cpu_count_int} | Convert to Integer | ${phy_cores}
| | ${thr_count_int} | Convert to Integer | ${phy_cores}
| | ${if1_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${${dut}_if1}
| | @{if_list}= | Run Keyword If | '${if1_status}' == 'PASS'
| | ... | Create List | ${${dut}_if1}
| | ... | ELSE | Create List | ${${dut}_if1_1} | ${${dut}_if1_2}
| | ${if2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${${dut}_if2}
| | Run Keyword If | '${if2_status}' == 'PASS'
| | ... | Append To List | ${if_list} | ${${dut}_if2}
| | ... | ELSE
| | ... | Append To List | ${if_list} | ${${dut}_if2_1} | ${${dut}_if2_2}
| | ${numa}= | Get interfaces numa node | ${nodes['${dut}']} | @{if_list}
| | ${smt_used}= | Is SMT enabled | ${nodes['${dut}']['cpuinfo']}
| | ${skip_cnt}= | Set variable | ${CPU_CNT_SYSTEM}
| | ${cpu_main}= | Cpu list per node str | ${nodes['${dut}']} | ${numa}
| | ... | skip_cnt=${skip_cnt} | cpu_cnt=${CPU_CNT_MAIN}
| | ${skip_cnt}= | Evaluate | ${CPU_CNT_SYSTEM} + ${CPU_CNT_MAIN}
| | ${cpu_wt}= | Run keyword if | ${cpu_count_int} > 0 |
| | ... | Cpu list per node str | ${nodes['${dut}']} | ${numa}
| | ... | skip_cnt=${skip_cnt} | cpu_cnt=${cpu_count_int}
| | ... | smt_used=${smt_used}
| | ${thr_count_int}= | Run keyword if | ${smt_used}
| | ... | Evaluate | int(${cpu_count_int}*2)
| | ... | ELSE | Set variable | ${thr_count_int}
| | ${rxq_count_int}= | Run keyword if | ${rx_queues}
| | ... | Set variable | ${rx_queues}
| | ... | ELSE | Evaluate | int(${thr_count_int}/2)
| | ${rxq_count_int}= | Run keyword if | ${rxq_count_int} == 0
| | ... | Set variable | ${1}
| | ... | ELSE | Set variable | ${rxq_count_int}
| | Run keyword if | ${cpu_count_int} > 0
| | ... | ${dut}.Add CPU Main Core | ${cpu_main}
| | Run keyword if | ${cpu_count_int} > 0
| | ... | ${dut}.Add CPU Corelist Workers | ${cpu_wt}
| | Run keyword
| | ... | ${dut}.Add DPDK Dev Default RXQ | ${rxq_count_int}
# For now there is no way to easily predict the number of buffers. Statically
# doing maximum amount of buffers allowed by DPDK.
| | Run keyword if | ${smt_used}
| | ... | Run keyword | ${dut}.Add Buffers Per Numa | ${215040} | ELSE
| | ... | Run keyword | ${dut}.Add Buffers Per Numa | ${107520}
| | Run keyword if | ${thr_count_int} > 1
| | ... | Set Tags | MTHREAD | ELSE | Set Tags | STHREAD
| | Set Tags | ${thr_count_int}T${cpu_count_int}C
| | Set Test Variable | ${smt_used}
| | Set Test Variable | ${thr_count_int}
| | Set Test Variable | ${cpu_count_int}
| | Set Test Variable | ${rxq_count_int}

| Create Kubernetes VSWITCH startup config on all DUTs
| | [Documentation] | Create base startup configuration of VSWITCH in Kubernetes
| | ... | deploy to all DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - ${jumbo} - Jumbo packet. Type: boolean
| | ... | - ${phy_cores} - Physical cores. Type: integer
| | ... | - ${rxq} - RX queues. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Create Kubernetes VSWITCH startup config on all DUTs \| ${True} \
| | ... | \| ${1} \| ${1}
| | ...
| | [Arguments] | ${phy_cores} | ${rx_queues}=${None} | ${jumbo}=${False}
| | ...
| | ${cpu_count_int} | Convert to Integer | ${phy_cores}
| | ${thr_count_int} | Convert to Integer | ${phy_cores}
| | :FOR | ${dut} | IN | @{duts}
| | | ${numa}= | Get interfaces numa node | ${nodes['${dut}']}
| | | ... | ${${dut}_if1} | ${${dut}_if2}
| | | ${smt_used}= | Is SMT enabled | ${nodes['${dut}']['cpuinfo']}
| | | ${if1_pci}= | Get Interface PCI Addr | ${nodes['${dut}']} | ${${dut}_if1}
| | | ${if2_pci}= | Get Interface PCI Addr | ${nodes['${dut}']} | ${${dut}_if2}
| | | ${thr_count_int}= | Run keyword if | ${smt_used}
| | | ... | Evaluate | int(${cpu_count_int}*2)
| | | ... | ELSE | Set variable | ${thr_count_int}
| | | ${rxq_count_int}= | Run keyword if | ${rx_queues}
| | | ... | Set variable | ${rx_queues}
| | | ... | ELSE | Evaluate | int(${thr_count_int}/2)
| | | ${rxq_count_int}= | Run keyword if | ${rxq_count_int} == 0
| | | ... | Set variable | ${1}
| | | ... | ELSE | Set variable | ${rxq_count_int}
| | | ${config}= | Run keyword | Create Kubernetes VSWITCH startup config
| | | ... | node=${nodes['${dut}']} | phy_cores=${phy_cores}
| | | ... | cpu_node=${numa} | jumbo=${jumbo} | rxq_count_int=${rxq_count_int}
| | | ... | buffers_per_numa=${215040}
| | | ... | filename=/tmp/vswitch.conf | if1=${if1_pci} | if2=${if2_pci}
| | | Run keyword if | ${thr_count_int} > 1
| | | ... | Set Tags | MTHREAD | ELSE | Set Tags | STHREAD
| | | Set Tags | ${thr_count_int}T${cpu_count_int}C
| | Set Test Variable | ${smt_used}
| | Set Test Variable | ${thr_count_int}
| | Set Test Variable | ${cpu_count_int}
| | Set Test Variable | ${rxq_count_int}

| Create Kubernetes VNF'${i}' startup config on all DUTs
| | [Documentation] | Create base startup configuration of VNF in Kubernetes
| | ... | deploy to all DUTs.
| | ...
| | ${i_int}= | Convert To Integer | ${i}
| | ${cpu_skip}= | Evaluate | ${vswitch_cpus}+${system_cpus}
| | ${dut1_numa}= | Get interfaces numa node | ${dut1}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${dut2_numa}= | Get interfaces numa node | ${dut2}
| | ... | ${dut2_if1} | ${dut2_if2}
| | ${config}= | Run keyword | Create Kubernetes VNF startup config
| | ... | node=${dut1} | phy_cores=${vnf_cpus} | cpu_node=${dut1_numa}
| | ... | cpu_skip=${cpu_skip} | filename=/tmp/vnf${i}.conf
| | ... | i=${i_int}
| | ${config}= | Run keyword | Create Kubernetes VNF startup config
| | ... | node=${dut2} | phy_cores=${vnf_cpus} | cpu_node=${dut2_numa}
| | ... | cpu_skip=${cpu_skip} | filename=/tmp/vnf${i}.conf
| | ... | i=${i_int}

| Add PCI devices to all DUTs
| | [Documentation]
| | ... | Add PCI devices to VPP configuration file.
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Add PCI devices to DUT | ${dut}

| Add PCI devices to DUT
| | [Documentation]
| | ... | Add PCI devices to VPP configuration file.
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT on which to set the PCI devices. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | Add PCI devices to DUT \| DUT1
| | ...
| | [Arguments] | ${dut}
| | ...
| | ${if1_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${${dut}_if1}
| | ${if1_pci}= | Run Keyword If | '${if1_status}' == 'PASS'
| | ... | Get Interface PCI Addr | ${nodes['${dut}']} | ${${dut}_if1}
| | ${if1_1_pci}= | Run Keyword Unless | '${if1_status}' == 'PASS'
| | ... | Get Interface PCI Addr | ${nodes['${dut}']} | ${${dut}_if1_1}
| | ${if1_2_pci}= | Run Keyword Unless | '${if1_status}' == 'PASS'
| | ... | Get Interface PCI Addr | ${nodes['${dut}']} | ${${dut}_if1_2}
| | ${if2_status} | ${value}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${${dut}_if2}
| | ${if2_pci}= | Run Keyword If | '${if2_status}' == 'PASS'
| | ... | Get Interface PCI Addr | ${nodes['${dut}']} | ${${dut}_if2}
| | ${if2_1_pci}= | Run Keyword Unless | '${if2_status}' == 'PASS'
| | ... | Get Interface PCI Addr | ${nodes['${dut}']} | ${${dut}_if2_1}
| | ${if2_2_pci}= | Run Keyword Unless | '${if2_status}' == 'PASS'
| | ... | Get Interface PCI Addr | ${nodes['${dut}']} | ${${dut}_if2_2}
| | @{pci_devs}= | Run Keyword If | '${if1_status}' == 'PASS'
| | ... | Create List | ${if1_pci}
| | ... | ELSE
| | ... | Create List | ${if1_1_pci} | ${if1_2_pci}
| | Run Keyword If | '${if2_status}' == 'PASS'
| | ... | Append To List | ${pci_devs} | ${if2_pci}
| | ... | ELSE
| | ... | Append To List | ${pci_devs} | ${if2_1_pci} | ${if2_2_pci}
| | Run keyword | ${dut}.Add DPDK Dev | @{pci_devs}
| | Run Keyword If | '${if1_status}' == 'PASS'
| | ... | Set Test Variable | ${${dut}_if1_pci} | ${if1_pci}
| | Run Keyword Unless | '${if1_status}' == 'PASS'
| | ... | Set Test Variable | ${${dut}_if1_1_pci} | ${if1_1_pci}
| | Run Keyword Unless | '${if1_status}' == 'PASS'
| | ... | Set Test Variable | ${${dut}_if1_2_pci} | ${if1_2_pci}
| | Run Keyword If | '${if2_status}' == 'PASS'
| | ... | Set Test Variable | ${${dut}_if2_pci} | ${if2_pci}
| | Run Keyword Unless | '${if2_status}' == 'PASS'
| | ... | Set Test Variable | ${${dut}_if2_1_pci} | ${if2_1_pci}
| | Run Keyword Unless | '${if2_status}' == 'PASS'
| | ... | Set Test Variable | ${${dut}_if2_2_pci} | ${if2_2_pci}

| Add single PCI device to all DUTs
| | [Documentation]
| | ... | Add single (first) PCI device on DUT1 and single (last) PCI device on
| | ... | DUT2 to VPP configuration file.
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | ${if1_pci}= | Get Interface PCI Addr | ${nodes['${dut}']} | ${${dut}_if1}
| | | Run keyword | ${dut}.Add DPDK Dev | ${if1_pci}
| | | Set Test Variable | ${${dut}_if1_pci} | ${if1_pci}

| Add no multi seg to all DUTs
| | [Documentation] | Add No Multi Seg to VPP startup configuration to all DUTs.
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Add DPDK No Multi Seg

| Add DPDK no PCI to all DUTs
| | [Documentation] | Add DPDK no-pci to VPP startup configuration to all DUTs.
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Add DPDK no PCI

| Add DPDK dev default RXD to all DUTs
| | [Documentation] | Add DPDK num-rx-desc to VPP startup configuration to all
| | ... | DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - rxd - Number of RX descriptors. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Add DPDK dev default RXD to all DUTs \| ${rxd} \|
| | ...
| | [Arguments] | ${rxd}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Add DPDK Dev Default RXD | ${rxd}

| Add DPDK dev default TXD to all DUTs
| | [Documentation] | Add DPDK num-tx-desc to VPP startup configuration to all
| | ... | DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - txd - Number of TX descriptors. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Add DPDK dev default TXD to all DUTs \| ${txd} \|
| | ...
| | [Arguments] | ${txd}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Add DPDK Dev Default TXD | ${txd}

| Add DPDK Uio Driver on all DUTs
| | [Documentation] | Add DPDK uio driver to VPP startup configuration on all
| | ... | DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - uio_driver - Required uio driver. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Add DPDK Uio Driver on all DUTs \| igb_uio \|
| | ...
| | [Arguments] | ${uio_driver}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Add DPDK Uio Driver | ${uio_driver}

| Add VLAN strip offload switch off
| | [Documentation]
| | ... | Add VLAN Strip Offload switch off on all PCI devices.
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | ${dut_str}= | Convert To Lowercase | ${dut}
| | | ${if1_pci}= | Get Interface PCI Addr | ${nodes['${dut}']}
| | | ... | ${${dut_str}_if1}
| | | ${if2_pci}= | Get Interface PCI Addr | ${nodes['${dut}']}
| | | ... | ${${dut_str}_if2}
| | | Run keyword | ${dut}.Add DPDK Dev Parameter | ${if1_pci}
| | | ... | vlan-strip-offload | off
| | | Run keyword | ${dut}.Add DPDK Dev Parameter | ${if2_pci}
| | | ... | vlan-strip-offload | off

| Add VLAN strip offload switch off between DUTs in 3-node single link topology
| | [Documentation]
| | ... | Add VLAN Strip Offload switch off on PCI devices between DUTs to VPP
| | ... | configuration file.
| | ...
| | Run keyword | DUT1.Add DPDK Dev Parameter | ${dut1_if2_pci}
| | ... | vlan-strip-offload | off
| | Run keyword | DUT2.Add DPDK Dev Parameter | ${dut2_if1_pci}
| | ... | vlan-strip-offload | off

| Add VLAN strip offload switch off between DUTs in 3-node double link topology
| | [Documentation]
| | ... | Add VLAN Strip Offload switch off on PCI devices between DUTs to VPP
| | ... | configuration file
| | ...
| | Run keyword | DUT1.Add DPDK Dev Parameter | ${dut1_if2_1_pci}
| | ... | vlan-strip-offload | off
| | Run keyword | DUT1.Add DPDK Dev Parameter | ${dut1_if2_2_pci}
| | ... | vlan-strip-offload | off
| | Run keyword | DUT2.Add DPDK Dev Parameter | ${dut2_if1_1_pci}
| | ... | vlan-strip-offload | off
| | Run keyword | DUT2.Add DPDK Dev Parameter | ${dut2_if1_2_pci}
| | ... | vlan-strip-offload | off

| Add NAT to all DUTs
| | [Documentation] | Add NAT configuration to all DUTs.
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Add NAT

| Add cryptodev to all DUTs
| | [Documentation] | Add Cryptodev to VPP startup configuration to all DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - count - Number of QAT devices. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Add cryptodev to all DUTs \| ${4} \|
| | ...
| | [Arguments] | ${count}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | ${smt_used}= | Is SMT enabled | ${nodes['${dut}']['cpuinfo']}
| | | ${thr_count_int}= | Run keyword if | ${smt_used}
| | | ... | Evaluate | int(${count}*2)
| | | ... | ELSE | Set variable | ${count}
| | | Run keyword | ${dut}.Add DPDK Cryptodev | ${thr_count_int}

| Add DPDK SW cryptodev on DUTs in 3-node single-link circular topology
| | [Documentation] | Add required number of SW crypto devices of given type
| | ... | to VPP startup configuration on all DUTs in 3-node single-link
| | ... | circular topology.
| | ...
| | ... | *Arguments:*
| | ... | - sw_pmd_type - PMD type of SW crypto device. Type: string
| | ... | - count - Number of SW crypto devices. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Add DPDK SW cryptodev on DUTs in 3-node single-link circular\
| | ... | topology \| aesni-mb \| ${2} \|
| | ...
| | [Arguments] | ${sw_pmd_type} | ${count}
| | ${smt_used}= | Is SMT enabled | ${nodes['DUT1']['cpuinfo']}
| | ${thr_count_int}= | Run keyword if | ${smt_used}
| | ... | Evaluate | int(${count}*2)
| | ... | ELSE | Set variable | ${count}
| | ${socket_id}= | Get Interface Numa Node | ${nodes['DUT1']} | ${dut1_if2}
| | Run keyword | DUT1.Add DPDK SW Cryptodev | ${sw_pmd_type} | ${socket_id}
| | ... | ${thr_count_int}
| | ${smt_used}= | Is SMT enabled | ${nodes['DUT2']['cpuinfo']}
| | ${thr_count_int}= | Run keyword if | ${smt_used}
| | ... | Evaluate | int(${count}*2)
| | ... | ELSE | Set variable | ${count}
| | ${socket_id}= | Get Interface Numa Node | ${nodes['DUT2']} | ${dut2_if1}
| | Run keyword | DUT2.Add DPDK SW Cryptodev | ${sw_pmd_type} | ${socket_id}
| | ... | ${thr_count_int}

| Write startup configuration on all VPP DUTs
| | [Documentation] | Write VPP startup configuration without restarting VPP.
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Write Config

| Apply startup configuration on all VPP DUTs
| | [Documentation] | Write VPP startup configuration and restart VPP on all
| | ... | DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - with_trace - Enable packet trace after VPP restart Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Apply startup configuration on all VPP DUTs \| False \|
| | ...
| | [Arguments] | ${with_trace}=${False}
| | ...
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Apply Config
| | Save VPP PIDs
| | Enable Coredump Limit VPP on All DUTs | ${nodes}
| | Update All Interface Data On All Nodes | ${nodes} | skip_tg=${True}
| | Run keyword If | ${with_trace} | VPP Enable Traces On All Duts | ${nodes}

| Apply startup configuration on VPP DUT
| | [Documentation] | Write VPP startup configuration and restart VPP DUT
| | ...
| | ... | *Arguments:*
| | ... | - dut - DUT on which to apply the configuration. Type: string
| | ... | - with_trace - Enable packet trace after VPP restart Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Apply startup configuration on VPP DUT \| DUT1 \| False \|
| | ...
| | [Arguments] | ${dut} | ${with_trace}=${False}
| | ...
| | Run keyword | ${dut}.Apply Config
| | Save VPP PIDs on DUT | ${dut}
| | Enable Coredump Limit VPP on DUT | ${nodes['${dut}']}
| | ${dutnode}= | Copy Dictionary | ${nodes}
| | Keep In Dictionary | ${dutnode} | ${dut}
| | Update All Interface Data On All Nodes | ${dutnode} | skip_tg=${True}
| | Run keyword If | ${with_trace} | VPP Enable Traces On Dut
| | ... | ${nodes['${dut}']}

| Save VPP PIDs
| | [Documentation] | Get PIDs of VPP processes from all DUTs in topology and\
| | ... | set it as a test variable. The PIDs are stored as dictionary items\
| | ... | where the key is the host and the value is the PID.
| | ...
| | ${setup_vpp_pids}= | Get VPP PIDs | ${nodes}
| | ${keys}= | Get Dictionary Keys | ${setup_vpp_pids}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${key} | IN | @{keys}
| | | ${pid}= | Get From Dictionary | ${setup_vpp_pids} | ${key}
| | | Run Keyword If | $pid is None | FAIL | No VPP PID found on node ${key}
| | Set Test Variable | ${setup_vpp_pids}

| Save VPP PIDs on DUT
| | [Documentation] | Get PID of VPP processes from DUT and\
| | ... | set it as a test variable. The PID is stored as dictionary item\
| | ... | where the key is the host and the value is the PID.
| | ...
| | [Arguments] | ${dut}
| | ...
| | ${vpp_pids}= | Get VPP PID | ${nodes['${dut}']}
| | Run Keyword If | ${vpp_pids} is None | FAIL
| | ... | No VPP PID found on node ${nodes['${dut}']['host']
| | ${status} | ${message}= | Run Keyword And Ignore Error
| | ... | Variable Should Exist | ${setup_vpp_pids}
| | ${setup_vpp_pids}= | Run Keyword If | '${status}' == 'FAIL'
| | ... | Create Dictionary | ${nodes['${dut}']['host']}=${vpp_pids}
| | ... | ELSE | Set To Dictionary | ${setup_vpp_pids}
| | ... | ${nodes['${dut}']['host']}=${vpp_pids}
| | Set Test Variable | ${setup_vpp_pids}

| Verify VPP PID in Teardown
| | [Documentation] | Check if the VPP PIDs on all DUTs are the same at the end\
| | ... | of test as they were at the begining. If they are not, only a message\
| | ... | is printed on console and to log. The test will not fail.
| | ...
| | ${teardown_vpp_pids}= | Get VPP PIDs | ${nodes}
| | ${err_msg}= | Catenate | ${SUITE NAME} - ${TEST NAME}
| | ... | \nThe VPP PIDs are not equal!\nTest Setup VPP PIDs:
| | ... | ${setup_vpp_pids}\nTest Teardown VPP PIDs: ${teardown_vpp_pids}
| | ${rc} | ${msg}= | Run keyword and ignore error
| | ... | Dictionaries Should Be Equal
| | ... | ${setup_vpp_pids} | ${teardown_vpp_pids}
| | Run Keyword And Return If | '${rc}'=='FAIL' | Log | ${err_msg}
| | ... | console=yes | level=WARN

| Set up functional test
| | [Documentation] | Common test setup for functional tests.
| | ...
| | Restart Vpp Service On All Duts | ${nodes}
| | Verify Vpp On All Duts | ${nodes}
| | VPP Enable Traces On All Duts | ${nodes}
| | Save VPP PIDs
| | All TGs Set Interface Default Driver | ${nodes}
| | Update All Interface Data On All Nodes | ${nodes}
| | Reset PAPI History On All DUTs | ${nodes}

| Tear down functional test
| | [Documentation] | Common test teardown for functional tests.
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show Packet Trace on All DUTs | ${nodes}
| | Show PAPI History On All DUTs | ${nodes}
| | Vpp Show Errors On All DUTs | ${nodes}
| | Verify VPP PID in Teardown

| Tear down LISP functional test
| | [Documentation] | Common test teardown for functional tests with LISP.
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show Packet Trace on All DUTs | ${nodes}
| | Show PAPI History On All DUTs | ${nodes}
| | Show Vpp Settings | ${nodes['DUT1']}
| | Show Vpp Settings | ${nodes['DUT2']}
| | Vpp Show Errors On All DUTs | ${nodes}
| | Verify VPP PID in Teardown
