# Copyright (c) 2017 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.honeycomb.Performance
| Library | resources.libraries.python.InterfaceUtil
| Resource | resources/libraries/robot/honeycomb/honeycomb.robot
| Documentation | Keywords used in Honeycomb performance testing.

*** Keywords ***
| Configure Honeycomb Netconf threads
| | [Documentation] | Modify thread configuration of Honeycomb's Netconf server,
| | ... | Requires a restart of Honeycomb to take effect.
| | ...
| | ... | *Arguments:*
| | ... | - node - Node to change configuration on. Type: dictionary
| | ... | - threads - Number of threads to configure. Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Configure Honeycomb Netconf Threads \| ${nodes[DUT1]} \| ${2} \|
| | ...
| | [Arguments] | ${node} | ${threads}
| | Configure Netconf Threads | ${node} | ${threads}

| Run base operational read performance trial
| | [Documentation] | Send Netconf requests over plain TCP to obtain VPP version
| | ... | from Honeycomb operational data.
| | ...
| | ... | *Arguments:*
| | ... | - node - Node to run test on. Type: dictionary
| | ... | - cycles - Number of test cycles to run. Final results will\
| | ... | be averaged across all runs. Type: integer
| | ... | - threads - Number of threads to use for generating traffic.\
| | ... | Type: integer
| | ... | - requests - Number of requests to send in each thread and cycle.\
| | ... | Type: integer
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Run base operational read performance trial \| ${nodes[DUT1]} \
| | ... | \| ${3} \| ${4} \| ${10000} \|
| | ...
| | [Arguments] | ${node} | ${cores} | ${cycles} | ${threads} | ${requests}
| | ${result}= | Run traffic script on DUT | ${node} | read_vpp_version.py
| | ... | ${cores} | cycles=${cycles} | threads=${threads}
| | ... | requests=${requests}
| | Set Test Message | ${result}

| Generate VPP Startup Configuration for Honeycomb Test on DUT
| | [Arguments] | ${node}
| | [Documentation] | Create VPP base startup configuration on DUT, then restart
| | ... | VPP to apply the configuration.
| | ...
| | ... | *Arguments:*
| | ... | - node - VPP node to configure. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Generate VPP Startup Configuration for Honeycomb Test on DUT \
| | ... | \| ${nodes[DUT1]} \| ${3} \| ${4} \| ${10000} \|
| | ...
| | Import Library | resources.libraries.python.VppConfigGenerator
| | ... | WITH NAME | VPP_config
| | Run keyword | VPP_config.Set Node | ${node}
| | Run keyword | VPP_config.Add Unix Log
| | Run keyword | VPP_config.Add Unix CLI Listen
| | Run keyword | VPP_config.Add Unix Nodaemon
| | Run keyword | VPP_config.Add DPDK Socketmem | "1024,1024"
| | Run keyword | VPP_config.Add Heapsize | "3G"
| | Run keyword | VPP_config.Add IP6 Hash Buckets | "2000000"
| | Run keyword | VPP_config.Add IP6 Heap Size | "3G"
#| | Run keyword | VPP_config.Add CPU Main Core | ${1}
#| | Run keyword | VPP_config.Add CPU Corelist Workers | ${2}
#| | Run keyword | VPP_config.Add DPDK Dev Default RXQ | ${1}
| | Apply startup configuration on VPP DUT | VPP_config

| Log Honeycomb and VPP process distribution on cores
| | [Documentation] | Log the distribution of VPP and Honeycomb child processes
| | ... | over the CPU cores.
| | ...
| | ... | *Arguments:*
| | ... | - node - Honeycomb node. Type: dictionary
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Log Honeycomb and VPP process distribution on cores \
| | ... | \| ${nodes[DUT1]} \|
| | ...
| | [Arguments] | ${node}
| | Log Core Schedule | ${node} | vpp
| | Log Core Schedule | ${node} | java

| Generate Honeycomb startup configuration for performance test
| | [Arguments] | ${node} | ${cores}
| | Import Library | resources.libraries.python.honeycomb.HoneycombSetup.HoneycombStartupConfig
| | ... | WITH NAME | HC_config
| | Run Keyword | HC_config.Set CPU Scheduler | FIFO
| | Run Keyword | HC_config.Set CPU Core Affinity | ${2} | ${cores}
| | Run Keyword | HC_config.Set JIT Compiler Mode | server
| | Run Keyword | HC_config.Set Memory Size | ${512} | ${2048}
| | Run Keyword | HC_config.Set Metaspace Size | ${128} | ${512}
| | Run Keyword | HC_config.Set NUMA Optimization
| | Run Keyword | HC_config.generate config | ${node}
| | Run Keyword | HC_config.deploy config | ${node}
