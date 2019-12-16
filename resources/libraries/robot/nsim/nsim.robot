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
| Library | resources.libraries.python.NsimUtil
|
| Documentation | L2 keywords to set up VPP Network Simulator to test hoststack.

*** Variables ***
| &{vpp_nsim_attr}=
| ... | delay_in_usec=${1}
| ... | average_packet_size=${1500}
| ... | bandwidth_in_bits_per_second=${40000000000}
| ... | packets_per_drop=${0}
| ... | output_feature_enable=${False}
| ... | cross_connect_feature_enable=${False}

*** Keywords ***
| Set VPP NSIM Attributes
| | [Documentation]
| | ... | Set the VPP NSIM attributes in the
| | ... | vpp_nsim_attr dictionary.
| |
| | ... | *Arguments:*
| | ... | - ${delay_in_usec} - Delay in Microseconds Type: Int
| | ... | - ${average_packet_size} - Average packet size Type: Int
| | ... | - ${bandwidth_in_bits_per_second} - Bandwidth of output interface Type: Int
| | ... | - ${pkts_per_drop} - Number of packets to drop Type: Int
| | ... | - ${output_feature_enable} - Enable/Disable NSIM Output Feature Type: Int
| | ... | - ${cross_connect_feature_enable} - Enable/Disable NSIM Cross Connect
| | ... |                                     Feature Type: Int
| |
| | ... | *Example:*
| |
| | ... | \| Set VPP NSIM Attributes \| output_feature_enable=${True} \|
| | ... | \| packets_per_drop=${pkts_per_drop} \|
| |
| | [Arguments]
| | ... | ${delay_in_usec}=${vpp_nsim_attr.delay_in_usec}
| | ... | ${average_packet_size}=${vpp_nsim_attr.average_packet_size}
| | ... | ${bandwidth_in_bits_per_second}=${vpp_nsim_attr.bandwidth_in_bits_per_second}
| | ... | ${packets_per_drop}=${vpp_nsim_attr.packets_per_drop}
| | ... | ${output_feature_enable}=${vpp_nsim_attr.output_feature_enable}
| | ... | ${cross_connect_feature_enable}=${vpp_nsim_attr.cross_connect_feature_enable}
| |
| | Set To Dictionary | ${vpp_nsim_attr} | delay_in_usec | ${delay_in_usec}
| | Set To Dictionary | ${vpp_nsim_attr} | average_packet_size | ${average_packet_size}
| | Set To Dictionary | ${vpp_nsim_attr} | bandwidth_in_bits_per_second | ${bandwidth_in_bits_per_second}
| | Set To Dictionary | ${vpp_nsim_attr} | packets_per_drop | ${packets_per_drop}
| | Set To Dictionary | ${vpp_nsim_attr} | output_feature_enable | ${output_feature_enable}
| | Set To Dictionary | ${vpp_nsim_attr} | cross_connect_feature_enable | ${cross_connect_feature_enable}

