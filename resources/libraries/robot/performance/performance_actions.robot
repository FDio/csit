# Copyright (c) 2024 Cisco and/or its affiliates.
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
| Variables | resources/libraries/python/Constants.py
| Resource | resources/libraries/robot/performance/performance_utils.robot
|
| Documentation
| ... | Performance suite keywords - Actions related to performance tests.

*** Keywords ***
| Additional Statistics Action For bash-perf-stat
| | [Documentation]
| | ... | Additional Statistics Action for bash command "perf stat".
| |
| | Run Keyword If | ${extended_debug}==${True}
| | ... | Perf Stat On All DUTs | ${nodes} | cpu_list=${cpu_alloc_str}

| Additional Statistics Action For trex-runtime
| | [Documentation]
| | ... | Additional Statistics Action for T-Rex telemetry counters with
| | ... | running traffic.
| |
| | ... | See documentation of the called keyword for required test variables.
| |
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${ramp_up_duration} = | Get Ramp Up Duration
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | ${runtime_duration} = | Get Runtime Duration
| | ${runtime_rate} = | Get Runtime Rate
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | Send traffic on tg
| | ... | duration=${-1}
| | ... | rate=${runtime_rate}
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | async_call=${True}
| | ... | ppta=${ppta}
| | ... | use_latency=${use_latency}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | duration_limit=${0.0}
| | ... | ramp_up_duration=${ramp_up_duration}
| | ... | ramp_up_rate=${ramp_up_rate}
| | Sleep | 1s
| | Stop traffic on tg

| Additional Statistics Action For infra-warmup
| | [Documentation]
| | ... | Additional Statistics Action for infra warmup.
| |
| | ... | See documentation of the called keyword for required test variables.
| |
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${ramp_up_duration} = | Get Ramp Up Duration
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | ${runtime_duration} = | Get Runtime Duration
| | ${runtime_rate} = | Get Runtime Rate
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | Send traffic on tg
| | ... | duration=${5}
| | ... | rate=${253}
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | async_call=${False}
| | ... | ppta=${ppta}
| | ... | use_latency=${False}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | duration_limit=${0.0}
| | ... | ramp_up_duration=${ramp_up_duration}
| | ... | ramp_up_rate=${ramp_up_rate}

| Additional Statistics Action For vpp-runtime
| | [Documentation]
| | ... | Additional Statistics Action for clear and show runtime counters with
| | ... | running traffic.
| |
| | ... | See documentation of the called keyword for required test variables.
| |
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${ramp_up_duration} = | Get Ramp Up Duration
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | ${runtime_duration} = | Get Runtime Duration
| | ${runtime_rate} = | Get Runtime Rate
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | ${node_arch} = | Get Node Arch | ${nodes[u'DUT1']}
| | ${profile} = | Set Variable If | "${node_arch}" == "aarch64"
| | ... | vppctl_runtime_arm.yaml | vppctl_runtime.yaml
| | Send traffic on tg
| | ... | duration=${-1}
| | ... | rate=${runtime_rate}
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | async_call=${True}
| | ... | ppta=${ppta}
| | ... | use_latency=${use_latency}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | duration_limit=${0.0}
| | ... | ramp_up_duration=${ramp_up_duration}
| | ... | ramp_up_rate=${ramp_up_rate}
| | Run Telemetry On All DUTs
| | ... | ${nodes} | profile=${profile}
| | ... | rate=${telemetry_rate} | export=${telemetry_export}
| | Stop traffic on tg

| Additional Statistics Action For bpf-runtime
| | [Documentation]
| | ... | Additional Statistics Action for linux bundle counters with
| | ... | running traffic.
| |
| | ... | See documentation of the called keyword for required test variables.
| |
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${ramp_up_duration} = | Get Ramp Up Duration
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | ${runtime_duration} = | Get Runtime Duration
| | ${runtime_rate} = | Get Runtime Rate
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | Send traffic on tg
| | ... | duration=${-1}
| | ... | rate=${runtime_rate}
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | async_call=${True}
| | ... | ppta=${ppta}
| | ... | use_latency=${use_latency}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | duration_limit=${0.0}
| | ... | ramp_up_duration=${ramp_up_duration}
| | ... | ramp_up_rate=${ramp_up_rate}
| | Run Telemetry On All DUTs
| | ... | ${nodes} | profile=bpf_runtime.yaml
| | ... | rate=${telemetry_rate} | export=${False}
| | Stop traffic on tg

| Additional Statistics Action For perf-stat-runtime
| | [Documentation]
| | ... | Additional Statistics Action for linux bundle counters with
| | ... | running traffic.
| |
| | ... | See documentation of the called keyword for required test variables.
| |
| | ${ppta} = | Get Packets Per Transaction Aggregated
| | ${ramp_up_duration} = | Get Ramp Up Duration
| | ${ramp_up_rate} = | Get Ramp Up Rate
| | ${runtime_duration} = | Get Runtime Duration
| | ${runtime_rate} = | Get Runtime Rate
| | ${traffic_directions} = | Get Traffic Directions
| | ${transaction_duration} = | Get Transaction Duration
| | ${transaction_scale} = | Get Transaction Scale
| | ${transaction_type} = | Get Transaction Type
| | ${use_latency} = | Get Use Latency
| | Send traffic on tg
| | ... | duration=${-1}
| | ... | rate=${runtime_rate}
| | ... | frame_size=${frame_size}
| | ... | traffic_profile=${traffic_profile}
| | ... | async_call=${True}
| | ... | ppta=${ppta}
| | ... | use_latency=${use_latency}
| | ... | traffic_directions=${traffic_directions}
| | ... | transaction_duration=${transaction_duration}
| | ... | transaction_scale=${transaction_scale}
| | ... | transaction_type=${transaction_type}
| | ... | duration_limit=${0.0}
| | ... | ramp_up_duration=${ramp_up_duration}
| | ... | ramp_up_rate=${ramp_up_rate}
| | Run Telemetry On All DUTs
| | ... | ${nodes} | profile=perf_stat_runtime.yaml
| | ... | rate=${telemetry_rate} | export=${False}
| | Stop traffic on tg

| Additional Statistics Action For vpp-runtime-iperf3
| | [Documentation]
| | ... | Additional Statistics Action for clear and show runtime counters with
| | ... | iPerf3 running traffic.
| |
| | ... | See documentation of the called keyword for required test variables.
| |
| | ${runtime_duration} = | Get Runtime Duration
| | ${node_arch} = | Get Node Arch | ${nodes['${iperf_server_node}']}
| | ${profile} = | Set Variable If | "${node_arch}" == "aarch64"
| | ... | vppctl_runtime_arm.yaml | vppctl_runtime.yaml
| | ${pids}= | iPerf Client Start Remote Exec
| | | ... | ${nodes['${iperf_client_node}']}
| | | ... | duration=${-1}
| | | ... | rate=${None}
| | | ... | frame_size=${None}
| | | ... | async_call=True
| | | ... | warmup_time=0
| | | ... | traffic_directions=${1}
| | | ... | namespace=${iperf_client_namespace}
| | | ... | udp=${iperf_client_udp}
| | | ... | host=${iperf_server_bind}
| | | ... | bind=${iperf_client_bind}
| | | ... | affinity=${iperf_client_affinity}
| | Run Telemetry On All DUTs
| | ... | ${nodes} | profile=${profile}
| | ... | rate=${telemetry_rate} | export=${telemetry_export}
| | iPerf Client Stop Remote Exec | ${nodes['${iperf_client_node}']} | ${pids}

| Additional Statistics Action For noop
| | [Documentation]
| | ... | Additional Statistics Action for no operation.
| |
| | No operation

| Additional Statistics Action For vpp-clear-stats
| | [Documentation]
| | ... | Additional Statistics Action for clear VPP statistics.
| |
| | Run Telemetry On All DUTs
| | ... | ${nodes} | profile=vppctl_clear_stats.yaml
| | ... | export=${False}

| Additional Statistics Action For vpp-enable-packettrace
| | [Documentation]
| | ... | Additional Statistics Action for enable VPP packet trace.
| |
| | Run Keyword If | ${extended_debug}==${True}
| | ... | VPP Enable Traces On All DUTs | ${nodes} | fail_on_error=${False}

| Additional Statistics Action For vpp-show-packettrace
| | [Documentation]
| | ... | Additional Statistics Action for show VPP packet trace.
| |
| | Run Keyword If | ${extended_debug}==${True}
| | ... | Show Packet Trace On All Duts | ${nodes} | maximum=${100}

| Additional Statistics Action For vpp-show-stats
| | [Documentation]
| | ... | Additional Statistics Action for show VPP statistics.
| |
| | Run Telemetry On All DUTs
| | ... | ${nodes} | profile=vppctl_show_stats.yaml
| | ... | export=${False}
