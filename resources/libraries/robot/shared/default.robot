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
| ...
| Library | Collections
| Library | OperatingSystem
| Library | String
| ...
| Library | resources.libraries.python.CoreDumpUtil
| Library | resources.libraries.python.CpuUtils
| Library | resources.libraries.python.DUTSetup
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.SchedUtils
| Library | resources.libraries.python.Tap
| Library | resources.libraries.python.TGSetup
| Library | resources.libraries.python.PapiHistory
| Library | resources.libraries.python.VppCounters
| Library | resources.libraries.python.VPPUtil
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.topology.Topology
| ...
| Resource | resources/libraries/robot/shared/container.robot
| Resource | resources/libraries/robot/vm/qemu.robot

*** Keywords ***
| Configure all DUTs before test
| | [Documentation] | Setup all DUTs in topology before test execution.
| | ...
| | Setup All DUTs | ${nodes}

| Configure all TGs for traffic script
| | [Documentation] | Prepare all TGs before traffic scripts execution.
| | ...
| | All TGs Set Interface Default Driver | ${nodes}

| Show Vpp Errors On All DUTs
| | [Documentation] | Show VPP errors verbose on all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Vpp Show Errors | ${nodes['${dut}']}

| Show VPP trace dump on all DUTs
| | [Documentation] | Save API trace and dump output on all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Vpp api trace save | ${nodes['${dut}']}
| | | Vpp api trace dump | ${nodes['${dut}']}

| Show Bridge Domain Data On All DUTs
| | [Documentation] | Show Bridge Domain data on all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Vpp Get Bridge Domain Data | ${nodes['${dut}']}

| Setup Scheduler Policy for Vpp On All DUTs
| | [Documentation] | Set realtime scheduling policy (SCHED_RR) with priority 1
| | ... | on all VPP worker threads on all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Set VPP Scheduling rr | ${nodes['${dut}']}

| Configure crypto device on all DUTs
| | [Documentation] | Verify if Crypto QAT device virtual functions are
| | ... | initialized on all DUTs. If parameter force_init is set to True, then
| | ... | try to initialize/disable.
| | ...
| | ... | *Arguments:*
| | ... | - force_init - Force to initialize. Type: boolean
| | ... | - numvfs - Number of VFs to initialize, 0 - disable the VFs
| | ... | (Optional). Type: integer, default value: ${32}
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure crypto device on all DUTs \| ${True} \|
| | ...
| | [Arguments] | ${force_init}=${False} | ${numvfs}=${32}
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Crypto Device Verify | ${nodes['${dut}']} | force_init=${force_init}
| | | ... | numvfs=${numvfs}

| Configure AVF interfaces on all DUTs
| | [Documentation] | Configure virtual functions for AVF interfaces on PCI
| | ... | interface on all DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - numvfs - Number of VFs to initialize, 0 - disable the VFs
| | ... | (Optional). Type: integer, default value: ${1}
| | ... | - topology_type - Topology type.
| | ... | (Optional). Type: string, default value: L2
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure AVF device on all DUTs \| ${1} \| L2 \|
| | ...
| | [Arguments] | ${numvfs}=${1} | ${topology_type}=L2
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | ${if1_avf_arr}= | Init AVF interface | ${nodes['${dut}']} | ${${dut}_if1}
| | | ... | numvfs=${numvfs} | topology_type=${topology_type}
| | | ${if2_avf_arr}= | Init AVF interface | ${nodes['${dut}']} | ${${dut}_if2}
| | | ... | numvfs=${numvfs} | topology_type=${topology_type}
# Currently only one AVF is supported.
| | | Set Suite Variable | ${${dut}_if1_vf0} | ${if1_avf_arr[0]}
| | | Set Suite Variable | ${${dut}_if2_vf0} | ${if2_avf_arr[0]}

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
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Import Library | resources.libraries.python.VppConfigGenerator
| | | ... | WITH NAME | ${dut}
| | | Run keyword | ${dut}.Set Node |  ${nodes['${dut}']}
| | | Run keyword | ${dut}.Add Unix Log
| | | Run keyword | ${dut}.Add Unix CLI Listen
| | | Run keyword | ${dut}.Add Unix Nodaemon
| | | Run keyword | ${dut}.Add Unix Coredump
| | | Run keyword | ${dut}.Add DPDK No Tx Checksum Offload
| | | Run keyword | ${dut}.Add DPDK Log Level | debug
| | | Run keyword | ${dut}.Add DPDK Uio Driver
| | | Run keyword | ${dut}.Add Heapsize | 4G
| | | Run keyword | ${dut}.Add Statseg size | 4G
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
| | ${num_mbufs_int} | Convert to Integer | 16384
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | ${if1_status} | ${value}= | Run Keyword And Ignore Error
| | | ... | Variable Should Exist | ${${dut}_if1}
| | | @{if_list}= | Run Keyword If | '${if1_status}' == 'PASS'
| | | ... | Create List | ${${dut}_if1}
| | | ... | ELSE | Create List | ${${dut}_if1_1} | ${${dut}_if1_2}
| | | ${if2_status} | ${value}= | Run Keyword And Ignore Error
| | | ... | Variable Should Exist | ${${dut}_if2}
| | | Run Keyword If | '${if2_status}' == 'PASS'
| | | ... | Append To List | ${if_list} | ${${dut}_if2}
| | | ... | ELSE
| | | ... | Append To List | ${if_list} | ${${dut}_if2_1} | ${${dut}_if2_2}
| | | ${numa}= | Get interfaces numa node | ${nodes['${dut}']} | @{if_list}
| | | ${smt_used}= | Is SMT enabled | ${nodes['${dut}']['cpuinfo']}
| | | ${cpu_main}= | Cpu list per node str | ${nodes['${dut}']} | ${numa}
| | | ... | skip_cnt=${1} | cpu_cnt=${1}
| | | ${cpu_wt}= | Cpu list per node str | ${nodes['${dut}']} | ${numa}
| | | ... | skip_cnt=${2} | cpu_cnt=${cpu_count_int} | smt_used=${smt_used}
| | | ${thr_count_int}= | Run keyword if | ${smt_used}
| | | ... | Evaluate | int(${cpu_count_int}*2)
| | | ... | ELSE | Set variable | ${thr_count_int}
| | | ${rxq_count_int}= | Run keyword if | ${rx_queues}
| | | ... | Set variable | ${rx_queues}
| | | ... | ELSE | Evaluate | int(${thr_count_int}/2)
| | | ${rxq_count_int}= | Run keyword if | ${rxq_count_int} == 0
| | | ... | Set variable | ${1}
| | | ... | ELSE | Set variable | ${rxq_count_int}
| | | ${num_mbufs_int}= | Evaluate | int(${num_mbufs_int}*${rxq_count_int})
| | | Run keyword | ${dut}.Add CPU Main Core | ${cpu_main}
| | | Run keyword | ${dut}.Add CPU Corelist Workers | ${cpu_wt}
| | | Run keyword | ${dut}.Add DPDK Dev Default RXQ | ${rxq_count_int}
# Temporarily desabling due to API changes:
# https://gerrit.fd.io/r/#/c/16638/
#| | | Run keyword | ${dut}.Add DPDK Num Mbufs | ${num_mbufs_int}
| | | Run keyword if | ${thr_count_int} > 1
| | | ... | Set Tags | MTHREAD | ELSE | Set Tags | STHREAD
| | | Set Tags | ${thr_count_int}T${cpu_count_int}C
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
| | ${num_mbufs_int} | Convert to Integer | 16384
| | ${duts}= | Get Matches | ${nodes} | DUT*
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
| | | ${num_mbufs_int}= | Evaluate | int(${num_mbufs_int}*${rxq_count_int})
| | | ${config}= | Run keyword | Create Kubernetes VSWITCH startup config
| | | ... | node=${nodes['${dut}']} | phy_cores=${phy_cores}
| | | ... | cpu_node=${numa} | jumbo=${jumbo} | rxq_count_int=${rxq_count_int}
| | | ... | num_mbufs_int=${num_mbufs_int}
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

| Add no multi seg to all DUTs
| | [Documentation] | Add No Multi Seg to VPP startup configuration to all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Add DPDK No Multi Seg

| Add DPDK no PCI to all DUTs
| | [Documentation] | Add DPDK no-pci to VPP startup configuration to all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
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
| | ${duts}= | Get Matches | ${nodes} | DUT*
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
| | ${duts}= | Get Matches | ${nodes} | DUT*
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
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Add DPDK Uio Driver | ${uio_driver}

| Add NAT to all DUTs
| | [Documentation] | Add NAT configuration to all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
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
| | ${duts}= | Get Matches | ${nodes} | DUT*
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

| Apply startup configuration on all VPP DUTs
| | [Documentation] | Write startup configuration and restart VPP on all DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - restart_vpp - Whether to restart VPP (Optional). Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Apply startup configuration on all VPP DUTs \| ${False} \|
| | ...
| | [Arguments] | ${restart_vpp}=${True}
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Apply Config | restart_vpp=${restart_vpp}
| | Enable Coredump Limit VPP on All DUTs | ${nodes}
| | Update All Interface Data On All Nodes | ${nodes} | skip_tg=${True}

| Save VPP PIDs
| | [Documentation] | Get PIDs of VPP processes from all DUTs in topology and\
| | ... | set it as a test variable. The PIDs are stored as dictionary items\
| | ... | where the key is the host and the value is the PID.
| | ...
| | ${setup_vpp_pids}= | Get VPP PIDs | ${nodes}
| | ${keys}= | Get Dictionary Keys | ${setup_vpp_pids}
| | :FOR | ${key} | IN | @{keys}
| | | ${pid}= | Get From Dictionary | ${setup_vpp_pids} | ${key}
| | | Run Keyword If | $pid is None | FAIL | No VPP PID found on node ${key}
| | | Run Keyword If | ',' in '${pid}'
| | | ... | FAIL | More then one VPP PID found on node ${key}: ${pid}
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
| | Configure all DUTs before test
| | Save VPP PIDs
| | Configure all TGs for traffic script
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

| Set up VPP device test
# TODO: Generalize this KW if it will not diverge from Functional derivate too
# much
| | [Documentation] | Common test setup for vpp-device tests.
| | ...
| | Configure all DUTs before test
| | Save VPP PIDs
| | Configure all TGs for traffic script
| | Update All Interface Data On All Nodes | ${nodes} | skip_tg_udev=${True}
| | Reset PAPI History On All DUTs | ${nodes}

| Tear down VPP device test
# TODO: Generalize this KW if it will not diverge from Functional derivate too
# much
| | [Documentation] | Common test teardown for vpp-device tests.
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

| Tear down LISP functional test with QEMU
| | [Documentation] | Common test teardown for functional tests with LISP and\
| | ... | QEMU.
| | ...
| | Remove All Added Ports On All DUTs From Topology | ${nodes}
| | Show Packet Trace on All DUTs | ${nodes}
| | Show PAPI History On All DUTs | ${nodes}
| | Show Vpp Settings | ${nodes['DUT1']}
| | Show Vpp Settings | ${nodes['DUT2']}
| | Vpp Show Errors On All DUTs | ${nodes}
| | Tear down QEMU
| | Verify VPP PID in Teardown

| Set up TAP functional test
| | [Documentation] | Common test setup for functional tests with TAP.
| | ...
| | Set up functional test
| | Clean Up Namespaces | ${nodes['DUT1']}

| Set up functional test with containers
| | [Documentation]
| | ... | Common test setup for functional tests with containers.
| | ...
| | ... | *Arguments:*
| | ... | - chains: Total number of chains (Optional). Type: integer, default
| | ... | value: ${1}
| | ... | - nodeness: Total number of nodes per chain (Optional). Type: integer,
| | ... | default value: ${1}
| | ...
| | ... | _NOTE:_ This KW sets following test case variables:
| | ... | - dcr_uuid - Parent container UUID.
| | ... | - dcr_root - Parent container overlay.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Set up functional test with containers \| 1 \| 1 \|
| | ...
| | [Arguments] | ${chains}=${1} | ${nodeness}=${1}
| | ...
| | Set Test Variable | @{container_groups} | @{EMPTY}
| | Set Test Variable | ${container_group} | CNF
| | Import Library | resources.libraries.python.ContainerUtils.ContainerManager
| | ... | engine=${container_engine} | WITH NAME | ${container_group}
| | ...
| | ${dcr_uuid}= | Get Environment Variable | CSIT_DUT1_UUID
| | ${dcr_root}= | Run Keyword | Get Docker Mergeddir | ${nodes['DUT1']}
| | ... | ${dcr_uuid}
| | Set Test Variable | ${dcr_uuid}
| | Set Test Variable | ${dcr_root}
| | ...
| | Construct chains of containers on all DUTs | ${chains} | ${nodeness}
| | ... | nested=${True}
| | Acquire all '${container_group}' containers
| | Create all '${container_group}' containers
| | Configure VPP in all '${container_group}' containers
| | Start VPP in all '${container_group}' containers
| | Append To List | ${container_groups} | ${container_group}

| Tear down TAP functional test
| | [Documentation] | Common test teardown for functional tests with TAP.
| | ...
| | Tear down functional test
| | Clean Up Namespaces | ${nodes['DUT1']}

| Tear down TAP functional test with Linux bridge
| | [Documentation] | Common test teardown for functional tests with TAP and
| | ... | a Linux bridge.
| | ...
| | ... | *Arguments:*
| | ... | - bid_TAP - Bridge name. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down TAP functional test with Linux bridge \| ${bid_TAP} \|
| | ...
| | [Arguments] | ${bid_TAP}
| | ...
| | Tear down functional test
| | Linux Del Bridge | ${nodes['DUT1']} | ${bid_TAP}
| | Clean Up Namespaces | ${nodes['DUT1']}

| Tear down FDS functional test
| | [Documentation] | Common test teardown for FDS functional tests.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_node - Node Nr.1 where to clean qemu. Type: dictionary
| | ... | - dut2_node - Node Nr.2 where to clean qemu. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down FDS functional test \| ${dut1_node} \| ${dut2_node} \|
| | ...
| | [Arguments] | ${dut1_node} | ${dut2_node}
| | ...
| | Tear down functional test
| | Tear down QEMU | qemu_node1
| | Tear down QEMU | qemu_node2

| Tear down functional test with container
| | [Documentation]
| | ... | Common test teardown for functional tests which uses containers.
| | ...
| | :FOR | ${container_group} | IN | @{container_groups}
| | | Destroy all '${container_group}' containers

| Stop VPP Service on DUT
| | [Documentation] | Stop the VPP service on the specified node.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Stop VPP Service on DUT \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Stop VPP Service | ${node}

| Start VPP Service on DUT
| | [Documentation] | Start the VPP service on the specified node.
| | ...
| | ... | *Arguments:*
| | ... | - node - information about a DUT node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Start VPP Service on DUT \| ${nodes['DUT1']} \|
| | ...
| | [Arguments] | ${node}
| | Start VPP Service | ${node}
