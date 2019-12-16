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
| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.HoststackUtil
| Library | resources.libraries.python.NsimUtil
| Variables | resources/libraries/python/Constants.py
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/nsim/nsim.robot
|
| Documentation | L2 keywords to set up VPP to test hoststack.

*** Variables ***
| ${quic_crypto_engine}= | nocrypto
| ${quic_fifo_size}= | 4Mb
| &{vpp_hoststack_attr}=
| ... | rxq=${None}
| ... | phy_cores=${1}
| ... | vpp_api_socket=${SOCKSVR_PATH}
| ... | api_seg_global_size=2G
| ... | api_seg_global_size=2G
| ... | api_seg_api_size=1G
| ... | sess_evt_q_seg_size=4G
| ... | sess_evt_q_length=4000000
| ... | sess_prealloc_sess=4000000
| ... | sess_v4_sess_tbl_buckets=2000000
| ... | sess_v4_sess_tbl_mem=2G
| ... | sess_v4_sess_halfopen_buckets=5000000
| ... | sess_v4_sess_halfopen_mem=3G
| ... | sess_v4_sess_tbl_mem=2G
| ... | sess_lcl_endpt_tbl_buckets=5000000
| ... | sess_lcl_endpt_tbl_mem=3G
| &{vpp_echo_server_attr}=
| ... | role=server
| ... | namespace=default
| ... | vpp_api_socket=${vpp_hoststack_attr.vpp_api_socket}
| ... | json_output=json
| ... | uri_protocol=quic
| ... | uri_ip4_addr=${EMPTY}
| ... | uri_port=1234
| ... | nclients=1
| ... | quic_streams=1
| ... | time=sconnect:lastbyte
| ... | fifo_size=4Mb
| ... | rx_bytes=0
| ... | tx_bytes=0
| ... | rx_results_diff=${False}
| ... | tx_results_diff=${False}
| &{vpp_echo_client_attr}=
| ... | role=client
| ... | namespace=default
| ... | vpp_api_socket=${vpp_hoststack_attr.vpp_api_socket}
| ... | json_output=json
| ... | uri_protocol=quic
| ... | uri_ip4_addr=${EMPTY}
| ... | uri_port=1234
| ... | nclients=1
| ... | quic_streams=1
| ... | time=sconnect:lastbyte
| ... | fifo_size=4Mb
| ... | rx_bytes=0
| ... | tx_bytes=0
| ... | rx_results_diff=${False}
| ... | tx_results_diff=${False}

*** Keywords ***
| Set VPP Echo Server Attributes
| | [Documentation]
| | ... | Set the HostStack external vpp_echo attributes
| | ... | in the vpp_echo_server_attr dictionary.
| |
| | ... | *Arguments:*
| | ... | - ${namespace} - Namespace Type: string
| | ... | - ${nclients} - Number of clients Type: string
| | ... | - ${quic_streams} - Number of quic streams Type: string
| | ... | - ${fifo_size} - Session Fifo Size Type: Integer
| | ... | - ${time} - Timing events (start:end) Type: string
| | ... | - ${rx_bytes} - Number of Bytes to receive Type: string
| | ... | - ${tx_bytes} - Number of Bytes to send Type: string
| | ... | - ${rx_results_diff} - Rx Results are different to pass Type: Boolean
| | ... | - ${tx_results_diff} - Tx Results are different to pass Type: Boolean
| |
| | ... | *Example:*
| |
| | ... | \| Set VPP Echo Server Attributes \| nclients=${nclients} \|
| | ... | \| tx_bytes=${tx_bytes} \|
| |
| | [Arguments]
| | ... | ${namespace}=${vpp_echo_server_attr.namespace}
| | ... | ${nclients}=${vpp_echo_server_attr.nclients}
| | ... | ${quic_streams}=${vpp_echo_server_attr.quic_streams}
| | ... | ${time}=${vpp_echo_server_attr.time}
| | ... | ${fifo_size}=${vpp_echo_server_attr.fifo_size}
| | ... | ${rx_bytes}=${vpp_echo_server_attr.rx_bytes}
| | ... | ${tx_bytes}=${vpp_echo_server_attr.tx_bytes}
| | ... | ${rx_results_diff}=${vpp_echo_server_attr.rx_results_diff}
| | ... | ${tx_results_diff}=${vpp_echo_server_attr.tx_results_diff}
| |
| | Set To Dictionary | ${vpp_echo_server_attr} | namespace | ${namespace}
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

| Set VPP Echo Client Attributes
| | [Documentation]
| | ... | Set the HostStack external vpp_echo attributes
| | ... | in the vpp_echo_client_attr dictionary.
| |
| | ... | *Arguments:*
| | ... | - ${namespace} - Namespace Type: string
| | ... | - ${nclients} - Number of clients Type: string
| | ... | - ${fifo_size} - Session Fifo Size Type: Integer
| | ... | - ${time} - Timing events (start:end) Type: string
| | ... | - ${rx_bytes} - Number of Bytes to receive Type: string
| | ... | - ${tx_bytes} - Number of Bytes to send Type: string
| | ... | - ${rx_results_diff} - Rx Results are different to pass Type: Boolean
| | ... | - ${tx_results_diff} - Tx Results are different to pass Type: Boolean
| |
| | ... | *Example:*
| |
| | ... | \| Set VPP Echo Client Attributes \| nclients=${nclients} \|
| | ... | \| tx_bytes=${tx_bytes} \|
| |
| | [Arguments]
| | ... | ${namespace}=${vpp_echo_client_attr.namespace}
| | ... | ${nclients}=${vpp_echo_client_attr.nclients}
| | ... | ${quic_streams}=${vpp_echo_server_attr.quic_streams}
| | ... | ${time}=${vpp_echo_client_attr.time}
| | ... | ${fifo_size}=${vpp_echo_client_attr.fifo_size}
| | ... | ${rx_bytes}=${vpp_echo_client_attr.rx_bytes}
| | ... | ${tx_bytes}=${vpp_echo_client_attr.tx_bytes}
| | ... | ${rx_results_diff}=${vpp_echo_client_attr.rx_results_diff}
| | ... | ${tx_results_diff}=${vpp_echo_client_attr.tx_results_diff}
| |
| | Set To Dictionary | ${vpp_echo_client_attr} | namespace | ${namespace}
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

| Run hoststack external app on DUT
| | [Documentation]
| | ... | Configure IP address on the port, set it up and start the specified
| | ... | HostStack external app on the specified DUT.
| |
| | ... | *Arguments:*
| | ... | - ${node} - VPP DUT node Type: Node
| | ... | - ${intf} - VPP DUT node interface key Type: string
| | ... | - ${ip4_addr} - VPP DUT node interface ip4 address Type: string
| | ... | - ${ip4_mask} - VPP DUT node interface ip4 network mask Type: string
| | ... | - ${namespace} - Network namespace to run app in Type: string
| | ... | - ${external_app} - Host Stack external external app Type: string
| | ... | - @{app_args} - List of args for the external app
| | ... | Type: List of strings
| |
| | ... | *Example:*
| |
| | ... | \| Run hoststack external app on DUT \| ${dut1} \| ${dut1_if1} \|
| | ... | \| ${dut1_if1_ip4_addr} \| ${dut1_if1_ip4_mask} \| default \|
| | ... | \| vcl_test_client \| @{client_args} \|
| |
| | [Arguments] | ${node} | ${intf} | ${ip4_addr} | ${ip4_mask}
| | | ... | ${namespace} | ${external_app} | @{app_args}
| |
| | Hoststack session enable | ${node}
| | Run Keyword If | ${vpp_nsim_attr.output_feature_enable}
| | ... | Configure VPP NSIM | ${node} | ${vpp_nsim_attr} | ${intf}
| | Set hoststack quic fifo size | ${node} | ${quic_fifo_size}
| | Set hoststack quic crypto engine | ${node} | ${quic_crypto_engine}
| | VPP Get Interface Data | ${node}
| | Set Interface State | ${node} | ${intf} | up
| | VPP Interface Set IP Address | ${node} | ${intf} | ${ip4_addr}
| | ... | ${ip4_mask}
| | Vpp Node Interfaces Ready Wait | ${node}
| | ${hoststack_external_app_pid}= | Start Hoststack External App
| | ... | ${node} | ${namespace} | ${external_app} | @{app_args}
| | Return From Keyword | ${hoststack_external_app_pid}

| Configure VPP hoststack attributes on all DUTs
| | [Documentation]
| | ... | Configure VPP HostStack attributes on all DUTs.
| |
| | Add worker threads to all DUTs
| | ... | ${vpp_hoststack_attr.phy_cores} | ${vpp_hoststack_attr.rxq}
| | Add DPDK PCI devices to all DUTs
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | FOR | ${dut} | IN | @{duts}
| | | Import Library | resources.libraries.python.VppConfigGenerator
| | | ... | WITH NAME | ${dut}
| | | Run keyword | ${dut}.Add socksvr | ${vpp_hoststack_attr.vpp_api_socket}
| | | Run keyword | ${dut}.Add api segment global size
| | | ... | ${vpp_hoststack_attr.api_seg_global_size}
| | | Run keyword | ${dut}.Add api segment api size
| | | ... | ${vpp_hoststack_attr.api_seg_api_size}
| | | Run keyword | ${dut}.Add api segment gid | testuser
| | | Run keyword | ${dut}.Add session event queues memfd segment
| | | Run keyword | ${dut}.Add session event queues segment size
| | | ... | ${vpp_hoststack_attr.sess_evt_q_seg_size}
| | | Run keyword | ${dut}.Add session event queue length
| | | ... | ${vpp_hoststack_attr.sess_evt_q_length}
| | | Run keyword | ${dut}.Add session preallocated sessions
| | | ... | ${vpp_hoststack_attr.sess_prealloc_sess}
| | | Run keyword | ${dut}.Add session v4 session table buckets
| | | ... | ${vpp_hoststack_attr.sess_v4_sess_tbl_buckets}
| | | Run keyword | ${dut}.Add session v4 session table memory
| | | ... | ${vpp_hoststack_attr.sess_v4_sess_tbl_mem}
| | | Run keyword | ${dut}.Add session v4 halfopen table buckets
| | | ... | ${vpp_hoststack_attr.sess_v4_sess_halfopen_buckets}
| | | Run keyword | ${dut}.Add session v4 halfopen table memory
| | | ... | ${vpp_hoststack_attr.sess_v4_sess_halfopen_mem}
| | | Run keyword | ${dut}.Add session local endpoints table buckets
| | | ... | ${vpp_hoststack_attr.sess_lcl_endpt_tbl_buckets}
| | | Run keyword | ${dut}.Add session local endpoints table memory
| | | ... | ${vpp_hoststack_attr.sess_lcl_endpt_tbl_mem}
| | END
| | Apply startup configuration on all VPP DUTs

| Get Test Results From Hoststack VPP Echo Test
| | [Documentation]
| | ... | Configure IP address on the port, set it up and start the specified
| | ... | HostStack external app on the specified DUT.
| |
| | Set To Dictionary | ${vpp_echo_server_attr} | uri_ip4_addr
| | ... | ${dut2_if1_ip4_addr}
| | Set To Dictionary | ${vpp_echo_client_attr} | uri_ip4_addr
| | ... | ${dut2_if1_ip4_addr}
| | Configure VPP Hoststack Attributes on all DUTs
| | ${server_app} | @{server_app_args}=
| | ... | Get VPP Echo Command | ${vpp_echo_server_attr}
| | ${server_pid}= | Run hoststack external app on DUT
| | ... | ${dut2} | ${dut2_if1} | ${dut2_if1_ip4_addr} | ${dut2_if1_ip4_prefix}
| | ... | ${vpp_echo_server_attr.namespace} | ${server_app} | @{server_app_args}
| | ${client_app} | @{client_app_args}=
| | ... | Get VPP Echo Command | ${vpp_echo_client_attr}
| | ${client_pid}= | Run hoststack external app on DUT
| | ... | ${dut1} | ${dut1_if1} | ${dut1_if1_ip4_addr} | ${dut1_if1_ip4_prefix}
| | ... | ${vpp_echo_client_attr.namespace} | ${client_app} | @{client_app_args}
| | When Hoststack External App Finished | ${dut1} | ${client_pid}
| | ${client_no_results} | ${client_output}=
| | ... | Analyze hoststack external app output | ${dut1} | Client
| | ... | ${vpp_nsim_attr} | ${client_app} | ${client_app_args}
| | Then Set test message | ${client_output}
| | And Hoststack External App Finished | ${dut2} | ${server_pid}
| | ${server_no_results} | ${server_output}=
| | ... | Analyze hoststack external app output | ${dut2} | Server
| | ... | ${vpp_nsim_attr} | ${server_app} | ${server_app_args}
| | Set test message | ${server_output} | append=True
| | Run Keyword And Return | No Hoststack External App Results
| | ... | ${server_no_results} | ${client_no_results}
