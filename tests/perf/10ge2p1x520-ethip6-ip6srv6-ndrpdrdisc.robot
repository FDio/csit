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
| Documentation | *High Level Description*
| ...
| ... | *Topology*
| ... | TG-DUT1-DUT2-TG 3-node circular topology with single links between\
| ... | nodes.
| ...
| ... | *Traffic processing*
| ... | Direction 0 --> 1
| ... |  - DUT1 performs SRv6 functions
| ... |  - DUT2 performs plain IPv6 forwarding
| ... | Direction 1 --> 0
| ... |  - DUT1 performs plain IPv6 forwarding
| ... |  - DUT2 performs SRv6 functions
| ...
| ... | *Tests Configurations*
| ... | 1. Transit with encap in SRv6 Policy
| ... | 2. Default endpoint
| ... | 3. Default endpoint + Penultimate Segment Popping
| ... | 4. Endpoint with decap and Xconnect - incoming packet has SRH
| ... | 5. Endpoint with decap and Xconnect - incoming packet has no SRH
| ...
| ... | 1. Transit with encap in SRv6 Policy
| ... | - SRv6: Push outer IP and SR headers associated with the segment
| ... | - IPv6FWD: Forward according to outer header DA
| ... | - Packet sent from TG:
| ... |   - ETH / IPv6 / UDP / Payload
| ... | - Suite name:
| ... |   - 10ge2p1x520-ethip6udp-srv6tenc-ndrpdrdisc
| ...
| ... | 2. Default endpoint
| ... | - SRv6: Decrement Segments Left, update DA
| ... | - IPv6FWD: Forward according to new DA
| ... | - Packet sent from TG:
| ... |   - ETH / IPv6a / SRH / IPv6b / UDP / Payload
| ... | - Suite name:
| ... |   - 10ge2p1x520-ethip6srhip6udp-srv6end-ndrpdrdisc
| ...
| ... | 3. Default endpoint + Penultimate Segment Popping
| ... | - SRv6: Decrement Segments Left, update DA; If Segments Left = 0,\
| ... |   remove SRH
| ... | - IPv6FWD: Forward according to new DA
| ... | - Packet sent from TG:
| ... |   - ETH / IPv6a / SRH / IPv6b / UDP / Payload
| ... | - Suite name:
| ... |   - 10ge2p1x520-ethip6srhip6udp-srv6endpsp-ndrpdrdisc
| ...
| ... | 4. Endpoint with decap and Xconnect - incoming packet has SRH
| ... | - SRv6: Pop the (outer) IPv6 header and its extension headers
| ... | - IPv6FWD: Forward on the interface associated with the Xconnect segment
| ... | - Packet sent from TG:
| ... |   - ETH / IPv6a / SRH / IPv6b / UDP / Payload
| ... | - Suite name:
| ... |   - 10ge2p1x520-ethip6srhip6udp-srv6enddx6srh-ndrpdrdisc
| ...
| ... | 5. Endpoint with decap and Xconnect - incoming packet has no SRH
| ... | - SRv6: Pop the (outer) IPv6 header and its extension headers
| ... | - IPv6FWD: Forward on the interface associated with the Xconnect segment
| ... | - Packet sent from TG:
| ... |   - ETH / IPv6a / IPv6b / UDP / Payload
| ... | - Suite name:
| ... |   - 10ge2p1x520-ethip6ip6udp-srv6enddx6-ndrpdrdisc
| ...
| ... | *Scaling*
| ... | - To be discussed ...
| ...
| ... | *Test suite documentation* - TODO, depending on the particular TS
| ...
| ... | *RFC6830: Packet throughput SRv6 test cases*
| ... | *[Top] Network Topologies:* TG-DUT1-DUT2-TG 3-node circular topology\
| ... | with single links between nodes.
| ... | *[Enc] Packet Encapsulations:*
| ... | *[Cfg] DUT configuration:*
| ... | *[Ver] TG verification:* TG finds and reports throughput NDR (Non Drop\
| ... | Rate) with zero packet loss tolerance or throughput PDR (Partial Drop\
| ... | Rate) with non-zero packet loss tolerance (LT) expressed in percentage\
| ... | of packets transmitted. NDR and PDR are discovered for different\
| ... | Ethernet L2 frame sizes using either binary search or linear search.
| ... | *[Ref] Applicable standard specifications:* RFC6830.
