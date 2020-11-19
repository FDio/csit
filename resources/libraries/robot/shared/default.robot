# Copyright (c) 2021 Cisco and/or its affiliates.
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
|
| Library | Collections
| Library | OperatingSystem
| Library | String
|
| Library | resources.libraries.python.Adl
| Library | resources.libraries.python.Classify
| Library | resources.libraries.python.CpuUtils
| Library | resources.libraries.python.CoreDumpUtil
| Library | resources.libraries.python.DUTSetup
| Library | resources.libraries.python.L2Util
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.IPv6Util
| Library | resources.libraries.python.NodePath
| Library | resources.libraries.python.Namespaces
| Library | resources.libraries.python.PapiHistory
| Library | resources.libraries.python.SchedUtils
| Library | resources.libraries.python.Tap
| Library | resources.libraries.python.Tap.TapFeatureMask
| Library | resources.libraries.python.TestConfig
| Library | resources.libraries.python.TGSetup
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.VhostUser.VirtioFeatureMask
| Library | resources.libraries.python.VppCounters
| Library | resources.libraries.python.VPPUtil
|
| Resource | resources/libraries/robot/lb/load_balancer.robot
| Resource | resources/libraries/robot/crypto/ipsec.robot
| Resource | resources/libraries/robot/features/acl.robot
| Resource | resources/libraries/robot/features/policer.robot
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/ip/ip6.robot
| Resource | resources/libraries/robot/ip/nat.robot
| Resource | resources/libraries/robot/l2/l2_bridge_domain.robot
| Resource | resources/libraries/robot/l2/l2_patch.robot
| Resource | resources/libraries/robot/l2/l2_traffic.robot
| Resource | resources/libraries/robot/l2/l2_xconnect.robot
| Resource | resources/libraries/robot/l2/tagging.robot
| Resource | resources/libraries/robot/overlay/srv6.robot
| Resource | resources/libraries/robot/overlay/lisp.robot
| Resource | resources/libraries/robot/overlay/lispgpe.robot
| Resource | resources/libraries/robot/overlay/lisp_api.robot
| Resource | resources/libraries/robot/performance/performance_utils.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/container.robot
| Resource | resources/libraries/robot/shared/memif.robot
| Resource | resources/libraries/robot/shared/suite_teardown.robot
| Resource | resources/libraries/robot/shared/suite_setup.robot
| Resource | resources/libraries/robot/shared/test_teardown.robot
| Resource | resources/libraries/robot/shared/test_setup.robot
| Resource | resources/libraries/robot/shared/traffic.robot
| Resource | resources/libraries/robot/shared/vm.robot

*** Variables ***
| ${cpu_alloc_str}= | ${0}

*** Keywords ***
# TODO: Sort keywords alphabetically.

| Call Resetter
| | [Documentation]
| | ... | Check for a presence of test variable \${resetter}.
| | ... | If it exists (and not None), call the resetter (as a Python callable).
| | ... | This is usually used to reset any state on DUT before next trial.
| |
| | ... | TODO: Move to a more specific library if needed.
| |
| | ... | *Example:*
| |
| | ... | \| Call Resetter \|
| |
| | ${resetter} = | Get Resetter
| | # See http://robotframework.org/robotframework/3.1.2/libraries/BuiltIn.html
| | # #Evaluating%20expressions for $variable (without braces) syntax.
| | # Parens are there to perform the call.
| | Run Keyword If | $resetter | Evaluate | $resetter()

| Workers From Physical Cores
| | [Documentation]
| | ... | Convert from core count to worker count.
| |
| | ... | This just calls CpuUtils.worker_count_from_cores_and_smt keyword
| | ... | with the global \${smt_used} value.
| | ... | See documentation there.
| |
| | ... | *Arguments:*
| | ... | - phy_cores - Number of physical cores to convert from. Type: integer.
| |
| | ... | *Return value:*
| | ... | - Number of workers active on the given number of cores.
| |
| | ... | *Example:*
| |
| | ... | \| \${dp_workers} = \| Workers from Physical Cores \| \${1} \|
| |
| | [Arguments] | ${phy_cores}
| |
| | Run Keyword And Return | Worker Count From Cores And Smt
| | ... | phy_cores=${phy_cores} | smt_used=${smt_used}

| Configure crypto device on all DUTs
| | [Documentation] | Verify if Crypto QAT device virtual functions are
| | ... | initialized on all DUTs. If parameter force_init is set to True, then
| | ... | try to initialize/disable.
| |
| | ... | *Arguments:*
| | ... | - crypto_type - Crypto device type - HW_DH895xcc or HW_C3xxx; default
| | ... | value: HW_DH895xcc. Type: string
| | ... | - numvfs - Number of VFs to initialize, 0 - disable the VFs; default
| | ... | value: ${32} Type: integer
| | ... | - force_init - Force to initialize. Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Configure crypto device on all DUTs \| HW_DH895xcc \| ${32} \|
| |
| | [Arguments] | ${crypto_type} | ${numvfs} | ${force_init}=${False}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Crypto Device Verify | ${nodes['${dut}']} | ${crypto_type}
| | | ... | ${numvfs} | force_init=${force_init}
| | END

| Configure kernel module on all DUTs
| | [Documentation] | Verify if specific kernel module is loaded on all DUTs.
| | ... | If parameter force_load is set to True, then try to load.
| |
| | ... | *Arguments:*
| | ... | - module - Module to verify. Type: string
| | ... | - force_load - Try to load module. Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Configure kernel module on all DUTs \| ${True} \|
| |
| | [Arguments] | ${module} | ${force_load}=${False}
| |
| | Verify Kernel Module on All DUTs | ${nodes} | ${module}
| | ... | force_load=${force_load}

| Get Keyname for DUT
| | [Documentation]
| | ... | Get the Keyname for the DUT in the keyname list.
| | ... | Returns lowercase keyname value.
| |
| | ... | *Arguments:*
| | ... | - dutx - DUT to find keyname. Type: dict
| | ... | - dut_keys - DUT Keynames to search. Type: list
| |
| | ... | *Example:*
| |
| | ... | \| Get Keyname for DUT \| ${dutx} \| ${duts} \|
| |
| | [Arguments] | ${dutx} | ${dut_keys}
| |
| | FOR | ${key} | IN | @{dut_keys}
| | | ${found_key} | ${value}= | Run Keyword And Ignore Error
| | | ... | Dictionaries Should Be Equal | ${nodes['${key}']} | ${dutx}
| | | Run Keyword If | '${found_key}' == 'PASS' | EXIT FOR LOOP
| | END
| | Run Keyword If | '${found_key}' != 'PASS'
| | ... | Fail | Keyname for ${dutx} not found
| | ${keyname}= | Convert To Lowercase | ${key}
| | Return From Keyword | ${keyname}

| Create base startup configuration of VPP on all DUTs
| | [Documentation] | Create base startup configuration of VPP to all DUTs.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Import Library | resources.libraries.python.VppConfigGenerator
| | | ... | WITH NAME | ${dut}
| | | Run Keyword | ${dut}.Set Node | ${nodes['${dut}']} | node_key=${dut}
| | | Run Keyword | ${dut}.Add Unix Log
| | | Run Keyword | ${dut}.Add Unix CLI Listen
| | | Run Keyword | ${dut}.Add Unix Nodaemon
| | | Run Keyword | ${dut}.Add Unix Coredump
| | | Run Keyword | ${dut}.Add Socksvr | ${SOCKSVR_PATH}
| | | Run Keyword | ${dut}.Add Main Heap Size | ${${heap_size_mult}*${2}}G
| | | Run Keyword | ${dut}.Add Main Heap Page Size | 2M
| | | Run Keyword | ${dut}.Add Statseg Size | 2G
| | | Run Keyword | ${dut}.Add Statseg Page Size | 2M
| | | Run Keyword | ${dut}.Add Statseg Per Node Counters | on
| | | Run Keyword | ${dut}.Add Plugin | disable | default
| | | Run Keyword | ${dut}.Add Plugin | enable | @{plugins_to_enable}
| | | Run Keyword | ${dut}.Add IP6 Hash Buckets | 2000000
| | | Run Keyword | ${dut}.Add IP6 Heap Size | 4G
| | | Run Keyword | ${dut}.Add Graph Node Variant | ${GRAPH_NODE_VARIANT}
| | END

| Add worker threads to all DUTs
| | [Documentation] | Setup worker threads in vpp startup configuration on all
| | ... | DUTs. Based on the SMT configuration of DUT if enabled keyword will
| | ... | automatically map also the sibling logical cores.
| | ... | Keyword will automatically set the appropriate test TAGs in format
| | ... | mTnC, where m=logical_core_count and n=physical_core_count.
| | ... | RXQ are computed automatically by dividing thread count with number 2
| | ... | (TODO: Add division by actual number of interfaces). User can manually
| | ... | override RX, RXD, TXD parameters if needed.
| |
| | ... | *Arguments:*
| | ... | - phy_cores - Number of physical cores to use. Type: integer
| | ... | - rx_queues - Number of RX queues. Type: integer
| | ... | - rxd - Number of RX descriptors. Type: integer
| | ... | - txd - Number of TX descriptors. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Add worker threads to all DUTs \| ${1} \| ${1} \|
| |
| | [Arguments] | ${phy_cores} | ${rx_queues}=${None} | ${rxd}=${None}
| | ... | ${txd}=${None}
| |
| | ${cpu_count_int} | Convert to Integer | ${phy_cores}
| | ${thr_count_int} | Convert to Integer | ${phy_cores}
| | ${rxd_count_int}= | Set variable | ${rxd}
| | ${txd_count_int}= | Set variable | ${txd}
| | FOR | ${dut} | IN | @{duts}
| | | ${numa}= | Get interfaces numa node
| | | ... | ${nodes['${dut}']} | @{${dut}_pf_keys}
| | | ${smt_used}= | Is SMT enabled | ${nodes['${dut}']['cpuinfo']}
| | | ${skip_cnt}= | Set variable | ${CPU_CNT_SYSTEM}
| | | ${cpu_main}= | Cpu list per node str | ${nodes['${dut}']} | ${numa}
| | | ... | skip_cnt=${skip_cnt} | cpu_cnt=${CPU_CNT_MAIN}
| | | ${skip_cnt}= | Evaluate | ${CPU_CNT_SYSTEM} + ${CPU_CNT_MAIN}
| | | ${cpu_wt}= | Run Keyword If | ${cpu_count_int} > 0 |
| | | ... | Cpu list per node str | ${nodes['${dut}']} | ${numa}
| | | ... | skip_cnt=${skip_cnt} | cpu_cnt=${cpu_count_int}
| | | ... | smt_used=${smt_used}
| | | ${thr_count_int}= | Run Keyword If | ${smt_used}
| | | ... | Evaluate | int(${cpu_count_int}*2)
| | | ... | ELSE | Set variable | ${thr_count_int}
| | | ${rxq_ratio} = | Get Variable Value | \${rxq_ratio} | ${2}
| | | ${rxq_count_int}= | Run Keyword If | ${rx_queues}
| | | ... | Set variable | ${rx_queues}
| | | ... | ELSE | Evaluate | int(${thr_count_int}/${rxq_ratio})
| | | ${rxq_count_int}= | Run Keyword If | ${rxq_count_int} == 0
| | | ... | Set variable | ${1}
| | | ... | ELSE | Set variable | ${rxq_count_int}
| | | Run Keyword | ${dut}.Add CPU Main Core | ${cpu_main}
| | | Run Keyword If | ${cpu_count_int} > 0
| | | ... | ${dut}.Add CPU Corelist Workers | ${cpu_wt}
| | | Run Keyword If | ${smt_used}
| | | ... | Run Keyword | ${dut}.Add Buffers Per Numa | ${215040} | ELSE
| | | ... | Run Keyword | ${dut}.Add Buffers Per Numa | ${107520}
| | | Run Keyword If | ${thr_count_int} > 1
| | | ... | Set Tags | MTHREAD | ELSE | Set Tags | STHREAD
| | | Set Tags | ${thr_count_int}T${cpu_count_int}C
| | END
| | ${cpu_alloc_str}= | Catenate | SEPARATOR=, | ${cpu_alloc_str} | ${cpu_main}
| | ${cpu_alloc_str}= | Catenate | SEPARATOR=, | ${cpu_alloc_str} | ${cpu_wt}
| | Set Test Variable | ${smt_used}
| | Set Test Variable | ${cpu_alloc_str}
| | Set Test Variable | ${cpu_count_int}
| | Set Test Variable | ${thr_count_int}
| | Set Test Variable | ${rxd_count_int}
| | Set Test Variable | ${txd_count_int}
| | Set Test Variable | ${rxq_count_int}

| Add worker threads for GSO tests to all DUTs
| | [Documentation] | Setup worker threads in vpp startup configuration on all
| | ... | DUTs. Based on the SMT configuration of DUT if enabled keyword will
| | ... | automatically map also the sibling logical cores.
| | ... | Keyword will automatically set the appropriate test TAGs in format
| | ... | mTnC, where m=logical_core_count and n=physical_core_count.
| | ... | RXQ are computed automatically by dividing thread count with number 2
| | ... | (TODO: Add division by actual number of interfaces). User can manually
| | ... | override RX, RXD, TXD parameters if needed.
| |
| | ... | *Arguments:*
| | ... | - phy_cores - Number of physical cores to use. Type: integer
| | ... | - rx_queues - Number of RX queues. Type: integer
| | ... | - rxd - Number of RX descriptors. Type: integer
| | ... | - txd - Number of TX descriptors. Type: integer
| |
| | ... | *Example:*
| |
| | ... | \| Add worker threads for GSO tests to all DUTs \| ${1} \| ${1} \|
| |
| | [Arguments] | ${phy_cores} | ${rx_queues}=${None} | ${rxd}=${None}
| | ... | ${txd}=${None}
| |
| | ${cpu_count_int} | Convert to Integer | ${phy_cores}
| | ${thr_count_int} | Convert to Integer | ${phy_cores}
| | ${rxd_count_int}= | Set variable | ${rxd}
| | ${txd_count_int}= | Set variable | ${txd}
| | FOR | ${dut} | IN | @{duts}
| | | ${numa}= | Get interfaces numa node
| | | ... | ${nodes['${dut}']} | @{${dut}_pf_keys}
| | | ${smt_used}= | Set variable | ${False}
| | | ${skip_cnt}= | Set variable | ${CPU_CNT_SYSTEM}
| | | ${cpu_main}= | Cpu list per node str | ${nodes['${dut}']} | ${numa}
| | | ... | skip_cnt=${skip_cnt} | cpu_cnt=${CPU_CNT_MAIN}
| | | ${skip_cnt}= | Evaluate | ${CPU_CNT_SYSTEM} + ${CPU_CNT_MAIN}
| | | ${cpu_wt}= | Run Keyword If | ${cpu_count_int} > 0 |
| | | ... | Cpu list per node str | ${nodes['${dut}']} | ${numa}
| | | ... | skip_cnt=${skip_cnt} | cpu_cnt=${cpu_count_int}
| | | ... | smt_used=${smt_used}
| | | ${thr_count_int}= | Run Keyword If | ${smt_used}
| | | ... | Evaluate | int(${cpu_count_int}*2)
| | | ... | ELSE | Set variable | ${thr_count_int}
| | | ${rxq_ratio} = | Get Variable Value | \${rxq_ratio} | ${2}
| | | ${rxq_count_int}= | Run Keyword If | ${rx_queues}
| | | ... | Set variable | ${rx_queues}
| | | ... | ELSE | Evaluate | int(${thr_count_int}/${rxq_ratio})
| | | ${rxq_count_int}= | Run Keyword If | ${rxq_count_int} == 0
| | | ... | Set variable | ${1}
| | | ... | ELSE | Set variable | ${rxq_count_int}
| | | Run Keyword | ${dut}.Add CPU Main Core | ${cpu_main}
| | | Run Keyword If | ${cpu_count_int} > 0
| | | ... | ${dut}.Add CPU Corelist Workers | ${cpu_wt}
| | | Run Keyword If | ${smt_used}
| | | ... | Run Keyword | ${dut}.Add Buffers Per Numa | ${215040} | ELSE
| | | ... | Run Keyword | ${dut}.Add Buffers Per Numa | ${107520}
| | | Run Keyword If | ${thr_count_int} > 1
| | | ... | Set Tags | MTHREAD | ELSE | Set Tags | STHREAD
| | | Set Tags | ${thr_count_int}T${cpu_count_int}C
| | END
| | ${cpu_alloc_str}= | Catenate | SEPARATOR=, | ${cpu_alloc_str} | ${cpu_main}
| | ${cpu_alloc_str}= | Catenate | SEPARATOR=, | ${cpu_alloc_str} | ${cpu_wt}
| | Set Test Variable | ${smt_used}
| | Set Test Variable | ${cpu_alloc_str}
| | Set Test Variable | ${cpu_count_int}
| | Set Test Variable | ${thr_count_int}
| | Set Test Variable | ${rxd_count_int}
| | Set Test Variable | ${txd_count_int}
| | Set Test Variable | ${rxq_count_int}

| Add DPDK VLAN strip offload switch off between DUTs
| | [Documentation]
| | ... | Add VLAN Strip Offload switch off on PCI devices between DUTs to VPP
| | ... | configuration file.
| |
| | FOR | ${pf} | IN RANGE | 1 | ${nic_pfs} + 1
| | | ${_even}= | Evaluate | ${pf} % 2
| | | Run Keyword Unless | ${even}
| | | ... | DUT1.Add DPDK Dev Parameter | ${DUT1_${int}${pf}_pci}[0]
| | | ... | vlan-strip-offload | off
| | END
| | FOR | ${pf} | IN RANGE | 1 | ${nic_pfs} + 1
| | | ${_even}= | Evaluate | ${pf} % 2
| | | Run Keyword If | ${even}
| | | ... | DUT2.Add DPDK Dev Parameter | ${DUT2_${int}${pf}_pci}[0]
| | | ... | vlan-strip-offload | off
| | END

| Add NAT to all DUTs
| | [Documentation] | Add NAT configuration to all DUTs.
| |
| | ... | *Arguments:*
| | ... | - nat_mode - NAT mode; default value: deterministic. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Add NAT to all DUTs \| nat_mode=endpoint-dependent \|
| |
| | [Arguments] | ${nat_mode}=deterministic
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword | ${dut}.Add NAT | value=${nat_mode}
| | END

| Add NAT max translations per thread to all DUTs
| | [Documentation] | Add NAT maximum number of translations per thread
| | ... | configuration.
| |
| | ... | *Arguments:*
| | ... | - max_translations_per_thread - NAT maximum number of translations per
| | ... | thread. Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Add NAT translation memory to all DUTs \
| | ... | \| max_translations_per_thread=2048 \|
| |
| | [Arguments] | ${max_translations_per_thread}=1024
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword | ${dut}.Add NAT max translations per thread
| | | ... | value=${max_translations_per_thread}
| | END

| Write startup configuration on all VPP DUTs
| | [Documentation] | Write VPP startup configuration without restarting VPP.
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword | ${dut}.Write Config
| | END

| Apply startup configuration on all VPP DUTs
| | [Documentation] | Write VPP startup configuration and restart VPP on all
| | ... | DUTs.
| |
| | ... | *Arguments:*
| | ... | - with_trace - Enable packet trace after VPP restart Type: boolean
| |
| | ... | *Example:*
| |
| | ... | \| Apply startup configuration on all VPP DUTs \| False \|
| |
| | [Arguments] | ${with_trace}=${False}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Run Keyword | ${dut}.Apply Config
| | END
| | Save VPP PIDs
| | Enable Coredump Limit VPP on All DUTs | ${nodes}
| | Update All Interface Data On All Nodes | ${nodes} | skip_tg=${True}
| | Run Keyword If | ${with_trace} | VPP Enable Traces On All Duts | ${nodes}

| Apply startup configuration on VPP DUT
| | [Documentation] | Write VPP startup configuration and restart VPP DUT.
| |
| | ... | *Arguments:*
| | ... | - dut - DUT on which to apply the configuration. Type: string
| | ... | - with_trace - Enable packet trace after VPP restart Type: boolean
| |
| | [Arguments] | ${dut} | ${with_trace}=${False}
| |
| | Run Keyword | ${dut}.Apply Config
| | Save VPP PIDs on DUT | ${dut}
| | Enable Coredump Limit VPP on DUT | ${nodes['${dut}']}
| | ${dutnode}= | Copy Dictionary | ${nodes}
| | Keep In Dictionary | ${dutnode} | ${dut}
| | Update All Interface Data On All Nodes | ${dutnode} | skip_tg=${True}
| | Run Keyword If | ${with_trace} | VPP Enable Traces On Dut
| | ... | ${nodes['${dut}']}

| Save VPP PIDs
| | [Documentation] | Get PIDs of VPP processes from all DUTs in topology and\
| | ... | set it as a test variable. The PIDs are stored as dictionary items\
| | ... | where the key is the host and the value is the PID.
| |
| | ${setup_vpp_pids}= | Get VPP PIDs | ${nodes}
| | ${keys}= | Get Dictionary Keys | ${setup_vpp_pids}
| | FOR | ${key} | IN | @{keys}
| | | ${pid}= | Get From Dictionary | ${setup_vpp_pids} | ${key}
| | | Run Keyword If | $pid is None | FAIL | No VPP PID found on node ${key}
| | END
| | Set Test Variable | ${setup_vpp_pids}

| Save VPP PIDs on DUT
| | [Documentation] | Get PID of VPP processes from DUT and\
| | ... | set it as a test variable. The PID is stored as dictionary item\
| | ... | where the key is the host and the value is the PID.
| |
| | [Arguments] | ${dut}
| |
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
| |
| | ${teardown_vpp_pids}= | Get VPP PIDs | ${nodes}
| | ${err_msg}= | Catenate | ${SUITE NAME} - ${TEST NAME}
| | ... | \nThe VPP PIDs are not equal!\nTest Setup VPP PIDs:
| | ... | ${setup_vpp_pids}\nTest Teardown VPP PIDs: ${teardown_vpp_pids}
| | ${rc} | ${msg}= | Run Keyword And Ignore Error
| | ... | Dictionaries Should Be Equal
| | ... | ${setup_vpp_pids} | ${teardown_vpp_pids}
| | Run Keyword And Return If | '${rc}'=='FAIL' | Log | ${err_msg}
| | ... | console=yes | level=WARN
