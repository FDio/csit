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
| Resource | resources/libraries/robot/vm/qemu.robot
| Variables | resources/libraries/python/topology.py
| Variables | resources/libraries/python/VatHistory.py
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.VatHistory
| Library | resources.libraries.python.CpuUtils
| Library | resources.libraries.python.DUTSetup
| Library | resources.libraries.python.SchedUtils
| Library | resources.libraries.python.TGSetup
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.Tap
| Library | resources/libraries/python/VppConfigGenerator.py
| Library | resources/libraries/python/VppCounters.py
| Library | Collections

*** Keywords ***
| Configure all DUTs before test
| | [Documentation] | Setup all DUTs in topology before test execution.
| | ...
| | Setup All DUTs | ${nodes}

| Configure all TGs for traffic script
| | [Documentation] | Prepare all TGs before traffic scripts execution.
| | ...
| | All TGs Set Interface Default Driver | ${nodes}

| Show VPP version on all DUTs
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

| Show VPP trace dump on all DUTs
| | [Documentation] | Save API trace and dump output on all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Vpp api trace save | ${nodes['${dut}']}
| | | Vpp api trace dump | ${nodes['${dut}']}

| Show VPP vhost on all DUTs
| | [Documentation] | Show Vhost User on all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Vpp Show Vhost | ${nodes['${dut}']}

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
| | ... | try to initialize.
| | ...
| | ... | *Arguments:*
| | ... | - ${force_init} - Try to initialize. Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure crypto device on all DUTs \| ${True} \|
| | ...
| | [Arguments] | ${force_init}=${False}
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Crypto Device Verify | ${nodes['${dut}']} | force_init=${force_init}

| Configure kernel module on all DUTs
| | [Documentation] | Verify if specific kernel module is loaded on all DUTs.
| | ... | If parameter force_load is set to True, then try to initialize.
| | ...
| | ... | *Arguments:*
| | ... | - ${module} - Module to verify. Type: string
| | ... | - ${force_load} - Try to load module. Type: boolean
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure kernel module on all DUTs \| ${True} \|
| | ...
| | [Arguments] | ${module} | ${force_load}=${False}
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Kernel Module Verify | ${nodes['${dut}']} | ${module}
| | | ... | force_load=${force_load}

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
| | | Run keyword | ${dut}.Add DPDK Socketmem | "1024,1024"
| | | Run keyword | ${dut}.Add Heapsize | "3G"
| | | Run keyword | ${dut}.Add IP6 Hash Buckets | "2000000"
| | | Run keyword | ${dut}.Add IP6 Heap Size | "3G"

| Add '${m}' worker threads and '${n}' rxqueues in 3-node single-link circular topology
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
| | Run keyword | DUT1.Add CPU Main Core | ${dut1_cpu_main}
| | Run keyword | DUT2.Add CPU Main Core | ${dut2_cpu_main}
| | Run keyword | DUT1.Add CPU Corelist Workers | ${dut1_cpu_w}
| | Run keyword | DUT2.Add CPU Corelist Workers | ${dut2_cpu_w}
| | Run keyword | DUT1.Add DPDK Dev Default RXQ | ${n}
| | Run keyword | DUT2.Add DPDK Dev Default RXQ | ${n}

| Add '${m}' worker threads and '${n}' rxqueues in 2-node single-link circular topology
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
| | Run keyword | DUT1.Add CPU Main Core | ${dut1_cpu_main}
| | Run keyword | DUT1.Add CPU Corelist Workers | ${dut1_cpu_w}
| | Run keyword | DUT1.Add DPDK Dev Default RXQ | ${n}

| Add '${m}' worker threads using SMT and '${n}' rxqueues in 3-node single-link circular topology
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
| | Run keyword | DUT1.Add CPU Main Core | ${dut1_cpu_main}
| | Run keyword | DUT2.Add CPU Main Core | ${dut2_cpu_main}
| | Run keyword | DUT1.Add CPU Corelist Workers | ${dut1_cpu_w}
| | Run keyword | DUT2.Add CPU Corelist Workers | ${dut2_cpu_w}
| | Run keyword | DUT1.Add DPDK Dev Default RXQ | ${n}
| | Run keyword | DUT2.Add DPDK Dev Default RXQ | ${n}

| Add '${m}' worker threads using SMT and '${n}' rxqueues in 2-node single-link circular topology
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
| | Run keyword | DUT1.Add CPU Main Core | ${dut1_cpu_main}
| | Run keyword | DUT1.Add CPU Corelist Workers | ${dut1_cpu_w}
| | Run keyword | DUT1.Add DPDK Dev Default RXQ | ${n}

| Add no multi seg to all DUTs
| | [Documentation] | Add No Multi Seg to VPP startup configuration to all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Add DPDK No Multi Seg

| Add SNAT to all DUTs
| | [Documentation] | Add SNAT configuration to all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Add SNAT

| Add cryptodev to all DUTs
| | [Documentation] | Add Cryptodev to VPP startup configuration to all DUTs.
| | ...
| | ... | *Arguments:*
| | ... | - ${count} - Number of QAT devices. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Add cryptodev to all DUTs \| ${4} \|
| | ...
| | [Arguments] | ${count}
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Add DPDK Cryptodev | ${count}

| Apply startup configuration on all VPP DUTs
| | [Documentation] | Write startup configuration and restart VPP on all DUTs.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Run keyword | ${dut}.Apply Config
| | Update All Interface Data On All Nodes | ${nodes} | skip_tg=${TRUE}

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
| | Reset VAT History On All DUTs | ${nodes}

| Tear down functional test
| | [Documentation] | Common test teardown for functional tests.
| | ...
| | Show Packet Trace on All DUTs | ${nodes}
| | Show VAT History On All DUTs | ${nodes}
| | Vpp Show Errors On All DUTs | ${nodes}
| | Verify VPP PID in Teardown

| Tear down LISP functional test
| | [Documentation] | Common test teardown for functional tests with LISP.
| | ...
| | Show Packet Trace on All DUTs | ${nodes}
| | Show VAT History On All DUTs | ${nodes}
| | Show Vpp Settings | ${nodes['DUT1']}
| | Show Vpp Settings | ${nodes['DUT2']}
| | Vpp Show Errors On All DUTs | ${nodes}
| | Verify VPP PID in Teardown

| Tear down LISP functional test with QEMU
| | [Documentation] | Common test teardown for functional tests with LISP and\
| | ... | QEMU.
| | ...
| | ... | *Arguments:*
| | ... | - vm_node - VM to stop. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down LISP functional test with QEMU \| ${vm_node} \|
| | ...
| | [Arguments] | ${vm_node}
| | ...
| | Show Packet Trace on All DUTs | ${nodes}
| | Show VAT History On All DUTs | ${nodes}
| | Show Vpp Settings | ${nodes['DUT1']}
| | Show Vpp Settings | ${nodes['DUT2']}
| | Vpp Show Errors On All DUTs | ${nodes}
| | Stop and clear QEMU | ${nodes['DUT1']} | ${vm_node}
| | Verify VPP PID in Teardown

| Set up TAP functional test
| | [Documentation] | Common test setup for functional tests with TAP.
| | ...
| | Set up functional test
| | Clean Up Namespaces | ${nodes['DUT1']}

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
