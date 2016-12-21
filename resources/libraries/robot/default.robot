# Copyright (c) 2016 Cisco and/or its affiliates.
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
| Variables | resources/libraries/python/VatHistory.py
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.VatHistory
| Library | resources.libraries.python.CpuUtils
| Library | resources.libraries.python.DUTSetup
| Library | resources.libraries.python.SchedUtils
| Library | resources.libraries.python.TGSetup
| Library | resources/libraries/python/VppConfigGenerator.py
| Library | resources/libraries/python/VppCounters.py
| Library | Collections

*** Keywords ***
| Setup all DUTs before test
| | [Documentation] | Setup all DUTs in topology before test execution.
| | ...
| | Setup All DUTs | ${nodes}

| Setup all TGs before traffic script
| | [Documentation] | Prepare all TGs before traffic scripts execution.
| | ...
| | All TGs Set Interface Default Driver | ${nodes}

| Show Vpp Version On All DUTs
| | [Documentation] | Show VPP version verbose on all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Vpp show version verbose | ${nodes['${dut}']}

| Show Vpp Errors On All DUTs
| | [Documentation] | Show VPP errors verbose on all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Vpp Show Errors | ${nodes['${dut}']}

| Show Vpp Trace Dump On All DUTs
| | [Documentation] | Save API trace and dump output on all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Vpp api trace save | ${nodes['${dut}']}
| | | Vpp api trace dump | ${nodes['${dut}']}

| Show Vpp Vhost On All DUTs
| | [Documentation] | Show Vhost User on all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Vpp Show Vhost | ${nodes['${dut}']}

| Setup Scheduler Policy for Vpp On All DUTs
| | [Documentation] | Set realtime scheduling policy (SCHED_RR) with priority 1
| | ... | on all VPP worker threads on all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Set VPP Scheduling rr | ${nodes['${dut}']}

| Verify Crypto Device On All DUTs
| | [Documentation] | Verify if Crypto QAT device virtual functions are
| | ... | initialized on all DUTs. If parameter force_init is set to True, then
| | ... | try to initialize.
| | ...
| | ... | *Arguments:*
| | ... | - ${force_init} - Try to initialize. Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Verify Crypto Device On All DUTs \| True \|
| | ...
| | [Arguments] | ${force_init}=${False}
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Crypto Device Verify | ${nodes['${dut}']} | force_init=${force_init}

| Add '${m}' worker threads and rxqueues '${n}' in 3-node single-link topo
| | [Documentation] | Setup M worker threads and N rxqueues in vpp startup\
| | ... | configuration on all DUTs in 3-node single-link topology.
| | ...
| | ${m_int}= | Convert To Integer | ${m}
| | ${dut1_numa}= | Get interfaces numa node | ${dut1}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${dut2_numa}= | Get interfaces numa node | ${dut2}
| | ... | ${dut2_if1} | ${dut2_if2}
| | ${dut1_cpu_main}= | Cpu list per node str | ${dut1} | ${dut1_numa}
| | ... | skip_cnt=${1} | cpu_cnt=${1}
| | ${dut1_cpu_w}= | Cpu list per node str | ${dut1} | ${dut1_numa}
| | ... | skip_cnt=${2} | cpu_cnt=${m_int}
| | ${dut2_cpu_main}= | Cpu list per node str | ${dut2} | ${dut2_numa}
| | ... | skip_cnt=${1} | cpu_cnt=${1}
| | ${dut2_cpu_w}= | Cpu list per node str | ${dut2} | ${dut2_numa}
| | ... | skip_cnt=${2} | cpu_cnt=${m_int}
| | ${dut1_cpu}= | Catenate | main-core | ${dut1_cpu_main}
| | ... | corelist-workers | ${dut1_cpu_w}
| | ${dut2_cpu}= | Catenate | main-core | ${dut2_cpu_main}
| | ... | corelist-workers | ${dut2_cpu_w}
| | ${rxqueues}= | Catenate | num-rx-queues | ${n}
| | Add CPU config | ${dut1} | ${dut1_cpu}
| | Add CPU config | ${dut2} | ${dut2_cpu}
| | Add rxqueues config | ${dut1} | ${rxqueues}
| | Add rxqueues config | ${dut2} | ${rxqueues}

| Add '${m}' worker threads and rxqueues '${n}' in 2-node single-link topo
| | [Documentation] | Setup M worker threads and N rxqueues in vpp startup\
| | ... | configuration on all DUTs in 2-node single-link topology.
| | ...
| | ${m_int}= | Convert To Integer | ${m}
| | ${dut1_numa}= | Get interfaces numa node | ${dut1}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${dut1_cpu_main}= | Cpu list per node str | ${dut1} | ${dut1_numa}
| | ... | skip_cnt=${1} | cpu_cnt=${1}
| | ${dut1_cpu_w}= | Cpu list per node str | ${dut1} | ${dut1_numa}
| | ... | skip_cnt=${2} | cpu_cnt=${m_int}
| | ${dut1_cpu}= | Catenate | main-core | ${dut1_cpu_main}
| | ... | corelist-workers | ${dut1_cpu_w}
| | ${rxqueues}= | Catenate | num-rx-queues | ${n}
| | Add CPU config | ${dut1} | ${dut1_cpu}
| | Add rxqueues config | ${dut1} | ${rxqueues}

| Add '${m}' worker threads using SMT and rxqueues '${n}' in 3-node single-link topo
| | [Documentation] | Setup M worker threads using SMT and N rxqueues in vpp\
| | ... | startup configuration on all DUTs in 3-node single-link topology.
| | ...
| | ${m_int}= | Convert To Integer | ${m}
| | ${dut1_numa}= | Get interfaces numa node | ${dut1}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${dut2_numa}= | Get interfaces numa node | ${dut2}
| | ... | ${dut2_if1} | ${dut2_if2}
| | ${dut1_cpu_main}= | Cpu list per node str | ${dut1} | ${dut1_numa}
| | ... | skip_cnt=${1} | cpu_cnt=${1} | smt_used=${True}
| | ${dut1_cpu_w}= | Cpu list per node str | ${dut1} | ${dut1_numa}
| | ... | skip_cnt=${2} | cpu_cnt=${m_int} | smt_used=${True}
| | ${dut2_cpu_main}= | Cpu list per node str | ${dut2} | ${dut2_numa}
| | ... | skip_cnt=${1} | cpu_cnt=${1} | smt_used=${True}
| | ${dut2_cpu_w}= | Cpu list per node str | ${dut2} | ${dut2_numa}
| | ... | skip_cnt=${2} | cpu_cnt=${m_int} | smt_used=${True}
| | ${dut1_cpu}= | Catenate | main-core | ${dut1_cpu_main}
| | ... | corelist-workers | ${dut1_cpu_w}
| | ${dut2_cpu}= | Catenate | main-core | ${dut2_cpu_main}
| | ... | corelist-workers | ${dut2_cpu_w}
| | ${rxqueues}= | Catenate | num-rx-queues | ${n}
| | Add CPU config | ${dut1} | ${dut1_cpu}
| | Add CPU config | ${dut2} | ${dut2_cpu}
| | Add rxqueues config | ${dut1} | ${rxqueues}
| | Add rxqueues config | ${dut2} | ${rxqueues}

| Add '${m}' worker threads using SMT and rxqueues '${n}' in 2-node single-link topo
| | [Documentation] | Setup M worker threads and N rxqueues in vpp startup\
| | ... | configuration on all DUTs in 2-node single-link topology.
| | ...
| | ${m_int}= | Convert To Integer | ${m}
| | ${dut1_numa}= | Get interfaces numa node | ${dut1}
| | ... | ${dut1_if1} | ${dut1_if2}
| | ${dut1_cpu_main}= | Cpu list per node str | ${dut1} | ${dut1_numa}
| | ... | skip_cnt=${1} | cpu_cnt=${1} | smt_used=${True}
| | ${dut1_cpu_w}= | Cpu list per node str | ${dut1} | ${dut1_numa}
| | ... | skip_cnt=${2} | cpu_cnt=${m_int} | smt_used=${True}
| | ${dut1_cpu}= | Catenate | main-core | ${dut1_cpu_main}
| | ... | corelist-workers | ${dut1_cpu_w}
| | ${rxqueues}= | Catenate | num-rx-queues | ${n}
| | Add CPU config | ${dut1} | ${dut1_cpu}
| | Add rxqueues config | ${dut1} | ${rxqueues}

| Add worker threads and rxqueues to all DUTs
| | [Documentation] | Setup worker threads and rxqueues in VPP startup\
| | ... | configuration to all DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - ${cpu} - CPU configuration. Type: string
| | ... | - ${rxqueues} - rxqueues configuration. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Add worker threads and rxqueues to all DUTs \| main-core 0 \
| | ... | \| rxqueues 2 \|
| | ...
| | [Arguments] | ${cpu} | ${rxqueues}
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Add CPU config | ${nodes['${dut}']} | ${cpu}
| | | Add rxqueues config | ${nodes['${dut}']} | ${rxqueues}

| Add all PCI devices to all DUTs
| | [Documentation] | Add all available PCI devices from topology file to VPP\
| | ... | startup configuration to all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Add PCI all devices | ${nodes['${dut}']}

| Add PCI device to DUT
| | [Documentation] | Add PCI device to VPP startup configuration
| | ... | to DUT specified as argument.
| | ...
| | ... | *Arguments:*
| | ... | - ${node} - DUT node. Type: dictionary
| | ... | - ${pci_address} - PCI address. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Add PCI device to DUT \| ${nodes['DUT1']} \| 0000:00:00.0 \|
| | ...
| | [Arguments] | ${node} | ${pci_address}
| | ...
| | Add PCI device | ${node} | ${pci_address}

| Add Heapsize Config to all DUTs
| | [Documentation] | Add Add Heapsize Config to VPP startup configuration\
| | ... | to all DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - ${heapsize} - Heapsize string (5G, 200M, ...)
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Add Heapsize Config to all DUTs \| 200M \|
| | ...
| | [Arguments] | ${heapsize}
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Add Heapsize Config | ${nodes['${dut}']} | ${heapsize}

| Add No Multi Seg to all DUTs
| | [Documentation] | Add No Multi Seg to VPP startup configuration to all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Add No Multi Seg Config | ${nodes['${dut}']}

| Add Enable Vhost User to all DUTs
| | [Documentation] | Add Enable Vhost User to VPP startup configuration to all\
| | ... | DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Add Enable Vhost User Config | ${nodes['${dut}']}

| Add Cryptodev to all DUTs
| | [Documentation] | AddCryptodev to VPP startup configuration to all
| | ...             | DUTs
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Add Cryptodev Config | ${nodes['${dut}']}

| Remove startup configuration of VPP from all DUTs
| | [Documentation] | Remove VPP startup configuration from all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Remove All PCI Devices | ${nodes['${dut}']}
| | | Remove All CPU Config | ${nodes['${dut}']}
| | | Remove Socketmem Config | ${nodes['${dut}']}
| | | Remove Cryptodev Config | ${nodes['${dut}']}
| | | Remove Heapsize Config | ${nodes['${dut}']}
| | | Remove Rxqueues Config | ${nodes['${dut}']}
| | | Remove No Multi Seg Config | ${nodes['${dut}']}
| | | Remove Enable Vhost User Config | ${nodes['${dut}']}

| Setup default startup configuration of VPP on all DUTs
| | [Documentation] | Setup default startup configuration of VPP to all DUTs.
| | ...
| | Remove startup configuration of VPP from all DUTs
| | Add '1' worker threads and rxqueues '1' in 3-node single-link topo
| | Add all PCI devices to all DUTs
| | Apply startup configuration on all VPP DUTs

| Setup 2-node startup configuration of VPP on all DUTs
| | [Documentation] | Setup default startup configuration of VPP to all DUTs.
| | ...
| | Remove startup configuration of VPP from all DUTs
| | Add '1' worker threads and rxqueues '1' in 2-node single-link topo
| | Add all PCI devices to all DUTs
| | Apply startup configuration on all VPP DUTs

| Apply startup configuration on all VPP DUTs
| | [Documentation] | Apply startup configuration of VPP and restart VPP on all\
| | ... | DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Apply Config | ${nodes['${dut}']}
| | Update All Interface Data On All Nodes | ${nodes} | skip_tg=${TRUE}

| Save VPP PIDs
| | [Documentation] | Get PIDs of VPP processes from all DUTs in topology and\
| | ... | set it as a test variable. The PIDs are stored as dictionary items\
| | ... | where the key is the host and the value is the PID.
| | ...
| | ${setup_vpp_pids}= | Get VPP PIDs | ${nodes}
| | Set Test Variable | ${setup_vpp_pids}

| Check VPP PID in Teardown
| | [Documentation] | Check if the VPP PIDs on all DUTs are the same at the end\
| | ... | of test as they were at the begining. If they are not, only a message\
| | ... | is printed on console and to log. The test will not fail.
| | ...
| | ${teardown_vpp_pids}= | Get VPP PIDs | ${nodes}
| | ${err_msg}= | Catenate | \nThe VPP PIDs are not equal!\nTest Setup VPP PIDs:
| | ... | ${setup_vpp_pids}\nTest Teardown VPP PIDs: ${teardown_vpp_pids}
| | ${rc} | ${msg}= | Run keyword and ignore error
| | ... | Dictionaries Should Be Equal
| | ... | ${setup_vpp_pids} | ${teardown_vpp_pids}
| | Run Keyword And Return If | '${rc}'=='FAIL' | Log | ${err_msg}
| | ... | console=yes | level=WARN

| Func Test Setup
| | [Documentation] | Common test setup for functional tests.
| | ...
| | Setup all DUTs before test
| | Save VPP PIDs
| | Setup all TGs before traffic script
| | Update All Interface Data On All Nodes | ${nodes}
| | Reset VAT History On All DUTs | ${nodes}

| Func Test Teardown
| | [Documentation] | Common test teardown for functional tests.
| | ...
| | Show Packet Trace on All DUTs | ${nodes}
| | Show VAT History On All DUTs | ${nodes}
| | Vpp Show Errors On All DUTs | ${nodes}
| | Check VPP PID in Teardown
