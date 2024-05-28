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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.HoststackUtil
| Library | resources.libraries.python.NginxUtil
| Library | resources.libraries.python.NsimUtil
| Library | resources.libraries.python.DMAUtil
| Library | resources.tools.ab.ABTools
| Variables | resources/libraries/python/Constants.py
| Resource | resources/libraries/robot/features/dma.robot
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/nsim/nsim.robot
| Resource | resources/libraries/robot/nginx/default.robot
|
| Documentation | *L2 keywords to set up VPP to test hoststack.*

*** Variables ***
| ${quic_crypto_engine}= | nocrypto
| ${quic_fifo_size}= | 4M
| &{vpp_hoststack_attr}=
| ... | rxd=${256}
| ... | txd=${256}
| ... | phy_cores=${1}
| ... | app_api_socket=/run/vpp/app_ns_sockets/default
| ... | tcp_cc_algo=cubic
| ... | sess_evt_q_length=16384
| ... | sess_prealloc_sess=1024
| ... | sess_v4_tbl_buckets=20000
| ... | sess_v4_tbl_mem=64M
| ... | sess_v4_hopen_buckets=20000
| ... | sess_v4_hopen_mem=64M
| ... | sess_lendpt_buckets=250000
| ... | sess_lendpt_mem=512M
| &{vpp_echo_server_attr}=
| ... | role=server
| ... | cpu_cnt=${1}
| ... | cfg_vpp_feature=${None}
| ... | namespace=default
| ... | app_api_socket=${vpp_hoststack_attr}[app_api_socket]
| ... | json_output=json
| ... | uri_protocol=quic
| ... | uri_ip4_addr=${EMPTY}
| ... | uri_port=1234
| ... | nthreads=1
| ... | mq_size=${vpp_hoststack_attr}[sess_evt_q_length]
| ... | nclients=1
| ... | quic_streams=1
| ... | time=sconnect:lastbyte
| ... | fifo_size=4M
| ... | rx_bytes=0
| ... | tx_bytes=0
| ... | rx_results_diff=${False}
| ... | tx_results_diff=${False}
| ... | use_app_socket_api=${True}
| &{vpp_echo_client_attr}=
| ... | role=client
| ... | cpu_cnt=${1}
| ... | cfg_vpp_feature=${None}
| ... | namespace=default
| ... | app_api_socket=${vpp_hoststack_attr}[app_api_socket]
| ... | json_output=json
| ... | uri_protocol=quic
| ... | uri_ip4_addr=${EMPTY}
| ... | uri_port=1234
| ... | nthreads=1
| ... | mq_size=${vpp_hoststack_attr}[sess_evt_q_length]
| ... | nclients=1
| ... | quic_streams=1
| ... | time=sconnect:lastbyte
| ... | fifo_size=4M
| ... | rx_bytes=0
| ... | tx_bytes=0
| ... | rx_results_diff=${False}
| ... | tx_results_diff=${False}
| ... | use_app_socket_api=${True}
| &{iperf3_server_attr}=
| ... | role=server
| ... | cpu_cnt=${1}
| ... | cfg_vpp_feature=${Empty}
| ... | namespace=default
| ... | vcl_config=vcl_iperf3.conf
| ... | ld_preload=${True}
| ... | transparent_tls=${False}
| ... | json=${True}
| ... | ip_version=${4}
| &{iperf3_client_attr}=
| ... | role=client
| ... | cpu_cnt=${1}
| ... | cfg_vpp_feature=${Empty}
| ... | namespace=default
| ... | vcl_config=vcl_iperf3.conf
| ... | ld_preload=${True}
| ... | transparent_tls=${False}
| ... | json=${True}
| ... | ip_version=${4}
| ... | ip_address=${EMPTY}
| ... | parallel=${1}
| ... | time=${20}
| ... | udp=${False}
| ... | bandwidth=10000000
| ... | length=${0}
| &{nginx_server_attr}=
| ... | role=server
| ... | cpu_cnt=${1}
| ... | cfg_vpp_feature=${Empty}
| ... | namespace=default
| ... | vcl_config=vcl_nginx.conf
| ... | ld_preload=${True}
| ... | transparent_tls=${False}
| ... | json=${True}
| ... | ip_version=${4}
| &{nginx_server_with_dma_attr}=
| ... | role=server
| ... | cpu_cnt=${1}
| ... | cfg_vpp_feature=${Empty}
| ... | namespace=default
| ... | vcl_config=vcl_dma.conf
| ... | ld_preload=${True}
| ... | transparent_tls=${False}
| ... | json=${True}
| ... | ip_version=${4}

*** Keywords ***
| Set VPP Hoststack Attributes
| | [Documentation]
| | ... | Set the VPP HostStack attributes in the vpp_hoststack_attr dictionary.
| |
| | ... | *Arguments:*
| | ... | - ${rxd} - Number of Rx Descriptors Type: int
| | ... | - ${txd} - Number of Tx Descriptors Type: int
| | ... | - ${phy_cores} - Number of cores for workers Type: int
| | ... | - ${app_api_socket} - Path to application api socket file Type: string
| | ... | - ${tcp_cc_algo} - TCP congestion control algorithm Type: string
| | ... | Type: string
| | ... | - ${sess_evt_q_length} - Session event queue length Type: string
| | ... | - ${sess_prealloc_sess} - Number of sessions to preallocate
| | ... | Type: string
| | ... | - ${sess_v4_tbl_buckets} - Number of IPv4 session table buckets
| | ... | Type: string
| | ... | - ${sess_v4_tbl_mem} - IPv4 session table memory size
| | ... | Type: string
| | ... | - ${sess_v4_hopen_buckets} - Number of IPv4 session
| | ... | half open table buckets Type: string
| | ... | - ${sess_v4_hopen_mem} - IPv4 session half open
| | ... | table memory size Type: string
| | ... | - ${sess_lendpt_buckets} - Number of session local endpoint
| | ... | table buckets Type: string
| | ... | - ${sess_lendpt_mem} - Session local endpoint
| | ... | table memory size Type: string
| |
| | ... | *Example:*
| |
| | ... | \| Set VPP Hoststack Attributes \| phy_cores=${phy_cores} \|
| |
| | [Arguments]
| | ... | ${rxd}=${vpp_hoststack_attr}[rxd]
| | ... | ${txd}=${vpp_hoststack_attr}[txd]
| | ... | ${phy_cores}=${vpp_hoststack_attr}[phy_cores]
| | ... | ${app_api_socket}=${vpp_hoststack_attr}[app_api_socket]
| | ... | ${tcp_cc_algo}=${vpp_hoststack_attr}[tcp_cc_algo]
| | ... | ${sess_evt_q_length}=${vpp_hoststack_attr}[sess_evt_q_length]
| | ... | ${sess_prealloc_sess}=${vpp_hoststack_attr}[sess_prealloc_sess]
| | ... | ${sess_v4_tbl_buckets}=${vpp_hoststack_attr}[sess_v4_tbl_buckets]
| | ... | ${sess_v4_tbl_mem}=${vpp_hoststack_attr}[sess_v4_tbl_mem]
| | ... | ${sess_v4_hopen_buckets}=${vpp_hoststack_attr}[sess_v4_hopen_buckets]
| | ... | ${sess_v4_hopen_mem}=${vpp_hoststack_attr}[sess_v4_hopen_mem]
| | ... | ${sess_lendpt_buckets}=${vpp_hoststack_attr}[sess_lendpt_buckets]
| | ... | ${sess_lendpt_mem}=${vpp_hoststack_attr}[sess_lendpt_mem]
| |
| | Set To Dictionary | ${vpp_hoststack_attr} | rxd | ${rxd}
| | Set To Dictionary | ${vpp_hoststack_attr} | txd | ${txd}
| | Set To Dictionary | ${vpp_hoststack_attr} | phy_cores | ${phy_cores}
| | Set To Dictionary | ${vpp_hoststack_attr}
| | ... | app_api_socket | ${app_api_socket}
| | Set To Dictionary | ${vpp_hoststack_attr}
| | ... | tcp_cc_algo | ${tcp_cc_algo}
| | Set To Dictionary | ${vpp_hoststack_attr}
| | ... | sess_evt_q_length | ${sess_evt_q_length}
| | Set To Dictionary | ${vpp_hoststack_attr}
| | ... | sess_prealloc_sess | ${sess_prealloc_sess}
| | Set To Dictionary | ${vpp_hoststack_attr}
| | ... | sess_v4_tbl_buckets | ${sess_v4_tbl_buckets}
| | Set To Dictionary | ${vpp_hoststack_attr}
| | ... | sess_v4_tbl_mem | ${sess_v4_tbl_mem}
| | Set To Dictionary | ${vpp_hoststack_attr}
| | ... | sess_v4_hopen_buckets | ${sess_v4_hopen_buckets}
| | Set To Dictionary | ${vpp_hoststack_attr}
| | ... | sess_v4_hopen_mem | ${sess_v4_hopen_mem}
| | Set To Dictionary | ${vpp_hoststack_attr}
| | ... | sess_lendpt_buckets | ${sess_lendpt_buckets}
| | Set To Dictionary | ${vpp_hoststack_attr}
| | ... | sess_lendpt_mem | ${sess_lendpt_mem}

| Set VPP Echo Server Attributes
| | [Documentation]
| | ... | Set the HostStack vpp_echo test program attributes
| | ... | in the vpp_echo_server_attr dictionary.
| |
| | ... | *Arguments:*
| | ... | - ${cfg_vpp_feature} - VPP Feature requiring config Type: string
| | ... | - ${namespace} - Namespace Type: string
| | ... | - ${nthreads} - Number of threads Type: string
| | ... | - ${mq_size} - Number of threads Type: string
| | ... | - ${nclients} - Number of clients Type: string
| | ... | - ${quic_streams} - Number of quic streams Type: string
| | ... | - ${fifo_size} - Session Fifo Size Type: integer
| | ... | - ${time} - Timing events (start:end) Type: string
| | ... | - ${rx_bytes} - Number of Bytes to receive Type: string
| | ... | - ${tx_bytes} - Number of Bytes to send Type: string
| | ... | - ${rx_results_diff} - Rx Results are different to pass Type: boolean
| | ... | - ${tx_results_diff} - Tx Results are different to pass Type: boolean
| | ... | - ${use_app_socket_api} - Use app socket API instead of VPP API
| |
| | ... | *Example:*
| |
| | ... | \| Set VPP Echo Server Attributes \| nclients=${nclients} \|
| | ... | \| tx_bytes=${tx_bytes} \|
| |
| | [Arguments]
| | ... | ${cfg_vpp_feature}=${vpp_echo_server_attr}[cfg_vpp_feature]
| | ... | ${namespace}=${vpp_echo_server_attr}[namespace]
| | ... | ${nthreads}=${vpp_echo_server_attr}[nthreads]
| | ... | ${mq_size}=${vpp_echo_server_attr}[mq_size]
| | ... | ${nclients}=${vpp_echo_server_attr}[nclients]
| | ... | ${quic_streams}=${vpp_echo_server_attr}[quic_streams]
| | ... | ${time}=${vpp_echo_server_attr}[time]
| | ... | ${fifo_size}=${vpp_echo_server_attr}[fifo_size]
| | ... | ${rx_bytes}=${vpp_echo_server_attr}[rx_bytes]
| | ... | ${tx_bytes}=${vpp_echo_server_attr}[tx_bytes]
| | ... | ${rx_results_diff}=${vpp_echo_server_attr}[rx_results_diff]
| | ... | ${tx_results_diff}=${vpp_echo_server_attr}[tx_results_diff]
| | ... | ${use_app_socket_api}=${vpp_echo_server_attr}[use_app_socket_api]
| |
| | Set To Dictionary | ${vpp_echo_server_attr} | cfg_vpp_feature
| | ... | ${cfg_vpp_feature}
| | Set To Dictionary | ${vpp_echo_server_attr} | namespace | ${namespace}
| | Set To Dictionary | ${vpp_echo_server_attr} | nthreads | ${nthreads}
| | Set To Dictionary | ${vpp_echo_server_attr} | mq_size | ${mq_size}
| | Set To Dictionary | ${vpp_echo_server_attr} | nclients | ${nclients}
| | Set To Dictionary | ${vpp_echo_server_attr} | quic_streams | ${quic_streams}
| | Set To Dictionary | ${vpp_echo_server_attr} | time | ${time}
| | Set To Dictionary | ${vpp_echo_server_attr} | fifo_size | ${fifo_size}
| | Set To Dictionary | ${vpp_echo_server_attr} | rx_bytes | ${rx_bytes}
| | Set To Dictionary | ${vpp_echo_server_attr} | tx_bytes | ${tx_bytes}
| | Set To Dictionary
| | ... | ${vpp_echo_server_attr} | rx_results_diff | ${rx_results_diff}
| | Set To Dictionary
| | ... | ${vpp_echo_server_attr} | tx_results_diff | ${tx_results_diff}
| | Set To Dictionary
| | ... | ${vpp_echo_server_attr} | use_app_socket_api | ${use_app_socket_api}

| Set VPP Echo Client Attributes
| | [Documentation]
| | ... | Set the HostStack vpp_echo test program attributes
| | ... | in the vpp_echo_client_attr dictionary.
| |
| | ... | *Arguments:*
| | ... | - ${cfg_vpp_feature} - VPP Feature requiring config Type: string
| | ... | - ${namespace} - Namespace Type: string
| | ... | - ${nthreads} - Number of threads Type: string
| | ... | - ${mq_size} - Number of threads Type: string
| | ... | - ${nclients} - Number of clients Type: string
| | ... | - ${quic_streams} - Number of quic streams Type: string
| | ... | - ${fifo_size} - Session Fifo Size Type: integer
| | ... | - ${time} - Timing events (start:end) Type: string
| | ... | - ${rx_bytes} - Number of Bytes to receive Type: string
| | ... | - ${tx_bytes} - Number of Bytes to send Type: string
| | ... | - ${rx_results_diff} - Rx Results are different to pass Type: boolean
| | ... | - ${tx_results_diff} - Tx Results are different to pass Type: boolean
| | ... | - ${use_app_socket_api} - Use app socket API instead of VPP API
| |
| | ... | *Example:*
| |
| | ... | \| Set VPP Echo Client Attributes \| nclients=${nclients} \|
| | ... | \| tx_bytes=${tx_bytes} \|
| |
| | [Arguments]
| | ... | ${cfg_vpp_feature}=${vpp_echo_client_attr}[cfg_vpp_feature]
| | ... | ${namespace}=${vpp_echo_client_attr}[namespace]
| | ... | ${nthreads}=${vpp_echo_client_attr}[nthreads]
| | ... | ${mq_size}=${vpp_echo_client_attr}[mq_size]
| | ... | ${nclients}=${vpp_echo_client_attr}[nclients]
| | ... | ${quic_streams}=${vpp_echo_client_attr}[quic_streams]
| | ... | ${time}=${vpp_echo_client_attr}[time]
| | ... | ${fifo_size}=${vpp_echo_client_attr}[fifo_size]
| | ... | ${rx_bytes}=${vpp_echo_client_attr}[rx_bytes]
| | ... | ${tx_bytes}=${vpp_echo_client_attr}[tx_bytes]
| | ... | ${rx_results_diff}=${vpp_echo_client_attr}[rx_results_diff]
| | ... | ${tx_results_diff}=${vpp_echo_client_attr}[tx_results_diff]
| | ... | ${use_app_socket_api}=${vpp_echo_client_attr}[use_app_socket_api]
| |
| | Set To Dictionary | ${vpp_echo_client_attr} | cfg_vpp_feature
| | ... | ${cfg_vpp_feature}
| | Set To Dictionary | ${vpp_echo_client_attr} | namespace | ${namespace}
| | Set To Dictionary | ${vpp_echo_client_attr} | nthreads | ${nthreads}
| | Set To Dictionary | ${vpp_echo_client_attr} | mq_size | ${mq_size}
| | Set To Dictionary | ${vpp_echo_client_attr} | nclients | ${nclients}
| | Set To Dictionary | ${vpp_echo_client_attr} | quic_streams | ${quic_streams}
| | Set To Dictionary | ${vpp_echo_client_attr} | time | ${time}
| | Set To Dictionary | ${vpp_echo_client_attr} | fifo_size | ${fifo_size}
| | Set To Dictionary | ${vpp_echo_client_attr} | rx_bytes | ${rx_bytes}
| | Set To Dictionary | ${vpp_echo_client_attr} | tx_bytes | ${tx_bytes}
| | Set To Dictionary
| | ... | ${vpp_echo_client_attr} | rx_results_diff | ${rx_results_diff}
| | Set To Dictionary
| | ... | ${vpp_echo_client_attr} | tx_results_diff | ${tx_results_diff}
| | Set To Dictionary
| | ... | ${vpp_echo_client_attr} | use_app_socket_api | ${use_app_socket_api}

| Set Iperf3 Server Attributes
| | [Documentation]
| | ... | Set the HostStack iperf3 test program attributes
| | ... | in the iperf3_server_attr dictionary.
| |
| | ... | *Arguments:*
| | ... | - ${vcl_config} - VCL configuration file name Type: string
| | ... | - ${ld_preload} - Use the VCL LD_PRELOAD library Type: boolean
| | ... | - ${transparent_tls} - Use VCL Transparent-TLS mode Type: boolean
| | ... | - ${ip_version} - IP version (4 or 6) Type: int
| |
| | ... | *Example:*
| |
| | ... | \| Set Iperf3 Server Attributes \| vcl_config=${vcl_config} \|
| | ... | \| ip_version=${ip_version} \|
| |
| | [Arguments]
| | ... | ${vcl_config}=${iperf3_server_attr}[vcl_config]
| | ... | ${ld_preload}=${iperf3_server_attr}[ld_preload]
| | ... | ${transparent_tls}=${iperf3_server_attr}[transparent_tls]
| | ... | ${ip_version}=${iperf3_server_attr}[ip_version]
| |
| | Set To Dictionary | ${iperf3_server_attr} | vcl_config | ${vcl_config}
| | Set To Dictionary | ${iperf3_server_attr} | ld_preload | ${ld_preload}
| | Set To Dictionary | ${iperf3_server_attr} | transparent_tls
| | ... | ${transparent_tls}
| | Set To Dictionary | ${iperf3_server_attr} | ip_version | ${ip_version}

| Set Iperf3 Client Attributes
| | [Documentation]
| | ... | Set the HostStack iperf3 test program attributes
| | ... | in the iperf3_client_attr dictionary.
| |
| | ... | *Arguments:*
| | ... | - ${vcl_config} - VCL configuration file name Type: string
| | ... | - ${ld_preload} - Use the VCL LD_PRELOAD library Type: boolean
| | ... | - ${transparent_tls} - Use VCL Transparent-TLS mode Type: boolean
| | ... | - ${ip_version} - IP version (4 or 6) Type: int
| | ... | - ${parallel} - Number of parallel streams Type: int
| | ... | - ${bandwidth} - Target bandwidth in bits/sec Type: int
| | ... | - ${udp} - UDP or TCP protocol Type: boolean
| | ... | - ${length} - Packet Length Type: int
| |
| | ... | *Example:*
| |
| | ... | \| Set Iperf3 Client Attributes \| vcl_config=${vcl_config} \|
| | ... | \| ip_version=${ip_version} \| parallel=${streams} \|
| | ... | \| bandwidth=${bandwidth} | udp=${True} \|
| |
| | [Arguments]
| | ... | ${vcl_config}=${iperf3_client_attr}[vcl_config]
| | ... | ${ld_preload}=${iperf3_client_attr}[ld_preload]
| | ... | ${transparent_tls}=${iperf3_client_attr}[transparent_tls]
| | ... | ${ip_version}=${iperf3_client_attr}[ip_version]
| | ... | ${parallel}=${iperf3_client_attr}[parallel]
| | ... | ${bandwidth}=${iperf3_client_attr}[bandwidth]
| | ... | ${udp}=${iperf3_client_attr}[udp]
| | ... | ${length}=${iperf3_client_attr}[length]
| |
| | Set To Dictionary | ${iperf3_client_attr} | vcl_config | ${vcl_config}
| | Set To Dictionary | ${iperf3_client_attr} | ld_preload | ${ld_preload}
| | Set To Dictionary | ${iperf3_client_attr} | transparent_tls
| | ... | ${transparent_tls}
| | Set To Dictionary | ${iperf3_client_attr} | ip_version | ${ip_version}
| | Set To Dictionary | ${iperf3_client_attr} | parallel | ${parallel}
| | Set To Dictionary | ${iperf3_client_attr} | bandwidth | ${bandwidth}
| | Set To Dictionary | ${iperf3_client_attr} | udp | ${udp}
| | Set To Dictionary | ${iperf3_client_attr} | length | ${length}

| Run hoststack test program on DUT
| | [Documentation]
| | ... | Configure IP address on the port, set it up and start the specified
| | ... | HostStack test program on the specified DUT.
| |
| | ... | *Arguments:*
| | ... | - ${node} - VPP DUT node Type: Node
| | ... | - ${intf} - VPP DUT node interface key Type: string
| | ... | - ${ip4_addr} - VPP DUT node interface ip4 address Type: string
| | ... | - ${ip4_mask} - VPP DUT node interface ip4 network mask Type: string
| | ... | - ${namespace} - Network namespace to run test program in Type: string
| | ... | - ${cfg_vpp_feature} - VPP hoststack feature requiring
| | ... | additional VPP configuration Type: string
| | ... | - ${core_list} - Cpu core affinity list Type: string
| | ... | - ${test_program} - Host Stack test program Type: dict
| |
| | ... | *Example:*
| |
| | ... | \| Run hoststack test program on DUT \| ${dut1} \| ${dut1_if1} \|
| | ... | \| ${dut1_if1_ip4_addr} \| ${dut1_if1_ip4_mask} \| default \|
| | ... | \| quic \| ${vpp_echo_server} \|
| |
| | [Arguments] | ${node} | ${intf} | ${ip4_addr} | ${ip4_mask}
| | | ... | ${namespace} | ${core_list} | ${cfg_vpp_feature}
| | | ... | ${test_program}
| |
| | ${is_dut1}= | Run Keyword And Return Status
| | ... | Dictionaries should be equal | ${node} | ${dut1}
| | Run Keyword If
| | ... | ${is_dut1} and ${vpp_nsim_attr}[output_nsim_enable]
| | ... | Configure VPP NSIM | ${node} | ${vpp_nsim_attr} | ${intf}
| | Run Keyword If | '${cfg_vpp_feature}' != ''
| | ... | Additional VPP Config for Feature ${cfg_vpp_feature} | ${node}
| | VPP Get Interface Data | ${node}
| | Set Interface State | ${node} | ${intf} | up
| | VPP Interface Set IP Address | ${node} | ${intf} | ${ip4_addr}
| | ... | ${ip4_mask}
| | Vpp Node Interfaces Ready Wait | ${node}
| | ${hoststack_test_program_pid}= | Start Hoststack Test Program
| | ... | ${node} | ${namespace} | ${core_list} | ${test_program}
| | Return From Keyword | ${hoststack_test_program_pid}

| Additional VPP Config For Feature quic
| | [Documentation]
| | ... | Configure VPP quic attributes on the specified DUT.
| |
| | ... | *Arguments:*
| | ... | - ${node} - VPP DUT node Type: Node
| |
| | [Arguments] | ${node}
| |
| | Set hoststack quic fifo size | ${node} | ${quic_fifo_size}
| | Set hoststack quic crypto engine | ${node} | ${quic_crypto_engine}

| Configure VPP Hoststack Attributes on all DUTs
| | [Documentation]
| | ... | Configure VPP HostStack attributes on all DUTs.
| |
| | Set Max Rate And Jumbo
| | Add worker threads to all DUTs
| | ... | ${vpp_hoststack_attr}[phy_cores]
| | ... | rxd=${vpp_hoststack_attr}[rxd] | txd=${vpp_hoststack_attr}[txd]
| | Pre-initialize layer driver | ${nic_driver}
| | FOR | ${dut} | IN | @{duts}
| | | Import Library | resources.libraries.python.VppConfigGenerator
| | | ... | WITH NAME | ${dut}
| | | Run Keyword If
| | | ... | '${dut}' == 'DUT1' and ${vpp_nsim_attr}[output_nsim_enable]
| | | ... | ${dut}.Add Nsim poll main thread
| | | Run keyword | ${dut}.Add api segment gid | testuser
| | | Run keyword | ${dut}.Add tcp congestion control algorithm
| | | ... | ${vpp_hoststack_attr}[tcp_cc_algo]
| | | Run keyword | ${dut}.Add session enable
| | | Run keyword | ${dut}.Add session app socket api
| | | Run keyword | ${dut}.Add session event queue length
| | | ... | ${vpp_hoststack_attr}[sess_evt_q_length]
| | | Run keyword | ${dut}.Add session preallocated sessions
| | | ... | ${vpp_hoststack_attr}[sess_prealloc_sess]
| | | Run keyword | ${dut}.Add session v4 session table buckets
| | | ... | ${vpp_hoststack_attr}[sess_v4_tbl_buckets]
| | | Run keyword | ${dut}.Add session v4 session table memory
| | | ... | ${vpp_hoststack_attr}[sess_v4_tbl_mem]
| | | Run keyword | ${dut}.Add session v4 halfopen table buckets
| | | ... | ${vpp_hoststack_attr}[sess_v4_hopen_buckets]
| | | Run keyword | ${dut}.Add session v4 halfopen table memory
| | | ... | ${vpp_hoststack_attr}[sess_v4_hopen_mem]
| | | Run keyword | ${dut}.Add session local endpoints table buckets
| | | ... | ${vpp_hoststack_attr}[sess_lendpt_buckets]
| | | Run keyword | ${dut}.Add session local endpoints table memory
| | | ... | ${vpp_hoststack_attr}[sess_lendpt_mem]
| | END
| | Apply startup configuration on all VPP DUTs

| Get Test Results From Hoststack VPP Echo Test
| | [Documentation]
| | ... | Configure IP address on the port, set it up and start the specified
| | ... | HostStack test programs on the DUTs. Gather test program
| | ... | output and append JSON formatted test data in message.
| | ... | Return boolean indicating there was a defered failure of either the
| | ... | server and/or client test programs.
| |
| | Set To Dictionary | ${vpp_echo_server_attr} | uri_ip4_addr
| | ... | ${dut2_if1_ip4_addr}
| | Set To Dictionary | ${vpp_echo_client_attr} | uri_ip4_addr
| | ... | ${dut2_if1_ip4_addr}
| | Configure VPP Hoststack Attributes on all DUTs
| | ${vpp_echo_server}= | Get VPP Echo Command | ${vpp_echo_server_attr}
| | ${skip_cnt}= | Evaluate
| | ... | ${CPU_CNT_SYSTEM} + ${CPU_CNT_MAIN} + ${vpp_hoststack_attr}[phy_cores]
| | ${numa}= | Get interfaces numa node | ${dut2} | ${dut2_if1}
| | ${core_list}= | Cpu list per node str | ${dut2} | ${numa}
| | ... | skip_cnt=${skip_cnt} | cpu_cnt=${vpp_echo_server_attr}[cpu_cnt]
| | FOR | ${action} | IN | @{stat_pre_trial}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | ${server_pid}= | Run hoststack test program on DUT
| | ... | ${dut2} | ${dut2_if1} | ${dut2_if1_ip4_addr} | ${dut2_if1_ip4_prefix}
| | ... | ${vpp_echo_server_attr}[namespace] | ${core_list}
| | ... | ${vpp_echo_server_attr}[cfg_vpp_feature] | ${vpp_echo_server}
| | ${vpp_echo_client}= | Get VPP Echo Command | ${vpp_echo_client_attr}
| | ${numa}= | Get interfaces numa node | ${dut1} | ${dut1_if1}
| | ${core_list}= | Cpu list per node str | ${dut1} | ${numa}
| | ... | skip_cnt=${skip_cnt} | cpu_cnt=${vpp_echo_client_attr}[cpu_cnt]
| | ${client_pid}= | Run hoststack test program on DUT
| | ... | ${dut1} | ${dut1_if1} | ${dut1_if1_ip4_addr} | ${dut1_if1_ip4_prefix}
| | ... | ${vpp_echo_client_attr}[namespace] | ${core_list}
| | ... | ${vpp_echo_client_attr}[cfg_vpp_feature] | ${vpp_echo_client}
| | When Hoststack Test Program Finished | ${dut1} | ${client_pid}
| | ... | ${vpp_echo_client} | ${dut2} | ${vpp_echo_server}
| | ${client_defer_fail} | ${client_output}=
| | ... | Analyze hoststack test program output | ${dut1} | Client
| | ... | ${vpp_nsim_attr} | ${vpp_echo_client}
| | Then Set test message | ${client_output}
| | And Hoststack Test Program Finished | ${dut2} | ${server_pid}
| | ... | ${vpp_echo_server} | ${dut1} | ${vpp_echo_client}
| | ${server_defer_fail} | ${server_output}=
| | ... | Analyze hoststack test program output | ${dut2} | Server
| | ... | ${vpp_nsim_attr} | ${vpp_echo_server}
| | FOR | ${action} | IN | @{stat_post_trial}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | Set test message | ${server_output} | append=True
| | Run Keyword And Return | Hoststack Test Program Defer Fail
| | ... | ${server_defer_fail} | ${client_defer_fail}

| Get Test Results From Hoststack Iperf3 Test
| | [Documentation]
| | ... | Configure IP address on the port, set it up and start the specified
| | ... | HostStack test programs on the DUTs. Gather test program
| | ... | output and append JSON formatted test data in message.
| | ... | Return boolean indicating there was a defered failure of either the
| | ... | server and/or client test programs.
| |
| | Set To Dictionary | ${iperf3_client_attr} | ip_address
| | ... | ${dut2_if1_ip4_addr}
| | Configure VPP Hoststack Attributes on all DUTs
| | ${iperf3_server}= | Get Iperf3 Command | ${iperf3_server_attr}
| | ${skip_cnt}= | Evaluate
| | ... | ${CPU_CNT_SYSTEM} + ${CPU_CNT_MAIN} + ${vpp_hoststack_attr}[phy_cores]
| | ${numa}= | Get interfaces numa node | ${dut2} | ${dut2_if1}
| | ${core_list}= | Cpu list per node str | ${dut2} | ${numa}
| | ... | skip_cnt=${skip_cnt} | cpu_cnt=${iperf3_server_attr}[cpu_cnt]
| | FOR | ${action} | IN | @{stat_pre_trial}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | ${server_pid}= | Run hoststack test program on DUT
| | ... | ${dut2} | ${dut2_if1} | ${dut2_if1_ip4_addr} | ${dut2_if1_ip4_prefix}
| | ... | ${iperf3_server_attr}[namespace] | ${core_list}
| | ... | ${iperf3_server_attr}[cfg_vpp_feature] | ${iperf3_server}
| | ${iperf3_client}= | Get Iperf3 Command | ${iperf3_client_attr}
| | ${numa}= | Get interfaces numa node | ${dut1} | ${dut1_if1}
| | ${core_list}= | Cpu list per node str | ${dut1} | ${numa}
| | ... | skip_cnt=${skip_cnt} | cpu_cnt=${iperf3_client_attr}[cpu_cnt]
| | ${client_pid}= | Run hoststack test program on DUT
| | ... | ${dut1} | ${dut1_if1} | ${dut1_if1_ip4_addr} | ${dut1_if1_ip4_prefix}
| | ... | ${iperf3_client_attr}[namespace] | ${core_list}
| | ... | ${iperf3_client_attr}[cfg_vpp_feature] | ${iperf3_client}
| | When Hoststack Test Program Finished | ${dut1} | ${client_pid}
| | ... | ${iperf3_client} | ${dut2} | ${iperf3_server}
| | FOR | ${action} | IN | @{stat_post_trial}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | ${client_defer_fail} | ${client_output}=
| | ... | Analyze hoststack test program output | ${dut1} | Client
| | ... | ${vpp_nsim_attr} | ${iperf3_client}
| | Then Set test message | ${client_output}
| | Return From Keyword | ${client_defer_fail}

| Set up LDP or VCL Nginx on DUT1 node
| | [Documentation]
| | ... | Setup for suites which uses VCL or LDP Nginx on DUT1.
| |
| | ... | Currently hardcoded to work on DUT1, assuming its node dict
| | ... | and similar values like \${DUT1_cpu_alloc_str} are already defined.
| |
| | ... | *Arguments:*
| | ... | - mode - VCL Nginx or LDP Nginx. Type: string
| | ... | - rps_cps - Test rps or cps. Type: string
| | ... | - core_num - Nginx work processes number. Type: int
| | ... | - qat - Whether to use the qat engine. Type: string
| | ... | - tls_tcp - TLS or TCP. Type: string
| | ... | - use_dma - Whether to use DMA, Default: False. Type: bool
| |
| | ... | *Example:*
| |
| | ... | \| Set up LDP or VCL NGINX on DUT1 node \| ${mode}\
| | ... | \| ${rps_cps} \| ${phy_cores} \| ${qat} \| ${tls_tcp} \|
| |
| | [Arguments] | ${mode} | ${rps_cps} | ${phy_cores} | ${qat} | ${tls_tcp}
| | | ... | ${use_dma}=${False}
| |
| | Set Interface State | ${DUT1} | ${DUT1_${int}1}[0] | up
| | VPP Interface Set IP Address | ${DUT1} | ${DUT1_${int}1}[0]
| | ... | ${dut_ip_addrs}[0] | ${dut_ip_prefix}
| | Vpp Node Interfaces Ready Wait | ${DUT1}
| | ${skip_cnt}= | Evaluate
| | ... | ${CPU_CNT_SYSTEM} + ${CPU_CNT_MAIN} + ${vpp_hoststack_attr}[phy_cores]
| | ${numa}= | Get interfaces numa node | ${DUT1} | ${DUT1_${int}1}[0]
| | Apply Nginx configuration on DUT | ${DUT1} | ${phy_cores}
| | ${attr}= | Run Keyword If | ${use_dma} == ${True}
| | ... | Set Variable | ${nginx_server_with_dma_attr}
| | ... | ELSE | Set Variable | ${nginx_server_attr}
| | Set To Dictionary | ${attr} | ip_address
| | ... | ${dut_ip_addrs}[0]
| | ${core_list}= | Cpu list per node str | ${DUT1} | ${numa}
| | ... | skip_cnt=${skip_cnt} | cpu_cnt=${attr}[cpu_cnt]
| | ... | smt_used=${smt_used}
| | ${cpu_idle}= | Cpu List per node | ${DUT1} | ${numa}
| | ${cpu_idle_list}= | Get Slice From List | ${cpu_idle}
| | ... | ${${skip_cnt} + ${attr}[cpu_cnt]}
| | ${nginx_server}= | Get Nginx Command | ${attr}
| | ... | ${nginx_version} | ${packages_dir}
| | Start Hoststack Test Program
| | ... | ${DUT1} | ${attr}[namespace] | ${core_list}
| | ... | ${nginx_server}
| | Get Hoststack Test Program Logs | ${DUT1} | ${nginx_server}
| | Taskset Nginx PID to idle cores | ${DUT1} | ${cpu_idle_list}

| Measure TLS requests or connections per second
| | [Documentation]
| | ... | Measure number of requests or connections per second using ab.
| |
| | ... | *Arguments:*
| | ... | - ${ciphers} - Specify SSL/TLS cipher suite
| | ... | - ${files} - Filename to be requested from the servers
| | ... | - ${tls_tcp} - Test TLS or TCP.
| | ... | - ${mode} - VCL Nginx or LDP Nginx.
| |
| | ... | *Example:*
| |
| | ... | \| Measure TLS requests or connections per second
| | ... | \| AES128-SHA \| 64 \| tls \| rps \|
| |
| | [Arguments] | ${ciphers} | ${files} | ${tls_tcp} | ${mode}
| |
| | ${dut_ip_addrs_str} | Evaluate | ','.join(${dut_ip_addrs})
| | ${ad_ip_addrs_str} | Evaluate | ','.join(${ab_ip_addrs})
| | FOR | ${action} | IN | @{stat_pre_trial}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | ${output}= | Run ab | ${tg} | ${dut_ip_addrs_str} | ${ad_ip_addrs_str}
| | ... | ${tls_tcp} | ${ciphers} | ${files} | ${mode} | ${r_total} | ${c_total}
| | ... | ${listen_port}
| | FOR | ${action} | IN | @{stat_post_trial}
| | | Run Keyword | Additional Statistics Action For ${action}
| | END
| | Set test message | ${output}

| Configure VPP startup configuration for NGINX
| | [Documentation]
| | ... | COnfigure VPP startup configuration for NGINX related tests
| |
| | [Arguments] | ${sess_prealloc_sess} | ${sess_evt_q_length}
| | ... | ${v4_sess_tbl_buckets} | ${v4_sess_tbl_mem} | ${local_endpts_tbl_buckets}
| | ... | ${local_endpts_tbl_mem} | ${tcp_prealloc_conns} | ${tcp_prealloc_ho_conns}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Import Library | resources.libraries.python.VppConfigGenerator
| | | ... | WITH NAME | ${dut}
| | | Run keyword | ${dut}.Add session enable
| | | Run keyword | ${dut}.Add session app socket api
| | | Run keyword | ${dut}.Add session preallocated sessions
| | | ... | ${sess_prealloc_sess}
| | | Run keyword | ${dut}.Add session event queue length
| | | ... | ${sess_evt_q_length}
| | | Run keyword | ${dut}.Add session v4 session table buckets
| | | ... | ${v4_sess_tbl_buckets}
| | | Run keyword | ${dut}.Add session v4 session table memory
| | | ... | ${v4_sess_tbl_mem}
| | | Run keyword | ${dut}.Add session local endpoints table buckets
| | | ... | ${local_endpts_tbl_buckets}
| | | Run keyword | ${dut}.Add session local endpoints table memory
| | | ... | ${local_endpts_tbl_mem}
| | | Run keyword | ${dut}.Add tcp preallocated connections
| | | ... | ${tcp_prealloc_conns}
| | | Run keyword | ${dut}.Add tcp preallocated half open connections
| | | ... | ${tcp_prealloc_ho_conns}
| | END

| Add Additional Startup Configuration For DMA On All DUTs
| | [Documentation]
| | ... | Add additional startup configuration for DMA on all DUTs
| |
| | [Arguments] | ${use_dma}=${True}
| |
| | FOR | ${dut} | IN | @{duts}
| | | Import Library | resources.libraries.python.VppConfigGenerator
| | | ... | WITH NAME | ${dut}
| | | Run keyword | ${dut}.Add Session Event Queues Memfd Segment
| | | Run keyword | ${dut}.Add TCP Congestion Control Algorithm
| | | Run keyword | ${dut}.Add TCP Tso
| | | Run keyword | ${dut}.Add Session Enable
| | | Run keyword If | ${use_dma} == ${True}
| | | ... | ${dut}.Add Session Use Dma
| | | Run keyword If | ${use_dma} == ${True}
| | | ... | Enable DMA WQs on all DUTs
| | | Run keyword If | ${use_dma} == ${True}
| | | ... | ${dut}.Add DMA Dev | ${${dut}_dma_wqs}
| | | Run keyword If | '${nic_driver}' == 'vfio-pci'
| | | ... | ${dut}.Add DPDK Dev Default Tso
| | | Run keyword If | '${nic_driver}' == 'vfio-pci'
| | | ... | ${dut}.Add DPDK Enable Tcp Udp Checksum
| | END
