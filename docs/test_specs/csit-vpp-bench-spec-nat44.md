## Front Matter

Filename: csit-vpp-bench-spec-nat44.md
Author: mkonstan@cisco.com
Date: 23-06-2020

## Overview

This note specifies FD.io CSIT benchmark test plan for VPP NAT44 tests.

### NAT44-EI - Endpoint Independent Mode

- TODO Add NAT44-EI definition.
- TODO Add NAT44-EI IETF reference(s).

### NAT44-ED - Endpoint Dependent Mode

- TODO Add NAT44-ED definition.
- TODO Add NAT44-ED IETF reference(s).

## Followed Specifications

### NAT44 Behaviour

Following IETF documents specify NAT behaviour for the target use case(s):

- [RFC4787] Network Address Translation (NAT) Behavioral Requirements for Unicast UDP.
- [RFC5382] NAT Behavioral Requirements for TCP.
- [RFC5508] NAT Behavioral Requirements for ICMP.
- [RFC7857] Updates to Network Address Translation (NAT) Behavioral Requirements.

The actual NAT use case requirements and VPP support [vpp-nat-wiki], [vpp-nat-src] are to be checklisted against above specs.

#### UDP [rfc4787-req]

- [ ] REQ-1:  A NAT MUST have an "Endpoint-Independent Mapping" behavior.
- [ ] REQ-2:  It is RECOMMENDED that a NAT have an "IP address pooling" behavior of "Paired".  Note that this requirement is not applicable to NATs that do not support IP address pooling.
- [ ] REQ-3:  A NAT MUST NOT have a "Port assignment" behavior of "Port overloading".
- [ ] REQ-4:  It is RECOMMENDED that a NAT have a "Port parity preservation" behavior of "Yes".
- [ ] REQ-5:  A NAT UDP mapping timer MUST NOT expire in less than two minutes, unless REQ-5a applies.
- [ ] REQ-6:  The NAT mapping Refresh Direction MUST have a "NAT Outbound refresh behavior" of "True".
- [ ] REQ-7  A NAT device whose external IP interface can be configured dynamically MUST either (1) Automatically ensure that its internal network uses IP addresses that do not conflict with its external network, or (2) Be able to translate and forward traffic between all internal nodes and all external nodes whose IP addresses numerically conflict with the internal network.
- [ ] REQ-8:  If application transparency is most important, it is RECOMMENDED that a NAT have "Endpoint-Independent Filtering" behavior.  If a more stringent filtering behavior is most important, it is RECOMMENDED that a NAT have "Address-Dependent Filtering" behavior.
- [ ] REQ-9:  A NAT MUST support "Hairpinning".
- [ ] REQ-10:  To eliminate interference with UNSAF NAT traversal mechanisms and allow integrity protection of UDP communications, NAT ALGs for UDP-based protocols SHOULD be turned off.  Future standards track specifications that define an ALG can update this to recommend the ALGs on which they define default.
- [ ] REQ-11:  A NAT MUST have deterministic behavior, i.e., it MUST NOT change the NAT translation (Section 4) or the Filtering (Section 5) Behavior at any point in time, or under any particular conditions.
- [ ] REQ-12:  Receipt of any sort of ICMP message MUST NOT terminate the NAT mapping.
- [ ] REQ-13  If the packet received on an internal IP address has DF=1, the NAT MUST send back an ICMP message "Fragmentation needed and DF set" to the host, as described in [RFC0792].
- [ ] REQ-14:  A NAT MUST support receiving in-order and out-of-order fragments, so it MUST have "Received Fragment Out of Order" behavior.

#### TCP [rfc5382-req]

- [ ] REQ-1:  A NAT MUST have an "Endpoint-Independent Mapping" behavior for TCP.
- [ ] REQ-2:  A NAT MUST support all valid sequences of TCP packets (defined in [RFC0793]) for connections initiated both internally as well as externally when the connection is permitted by the NAT.
- [ ] REQ-3:  If application transparency is most important, it is RECOMMENDED that a NAT have an "Endpoint-Independent Filtering" behavior for TCP.  If a more stringent filtering behavior is most important, it is RECOMMENDED that a NAT have an "Address-Dependent Filtering" behavior.
- [ ] REQ-4:  A NAT MUST NOT respond to an unsolicited inbound SYN packet for at least 6 seconds after the packet is received.  If during this interval the NAT receives and translates an outbound SYN for the connection the NAT MUST silently drop the original unsolicited inbound SYN packet.  Otherwise, the NAT SHOULD send an ICMP Port Unreachable error (Type 3, Code 3) for the original SYN, unless REQ-4a applies.
- [ ] REQ-5:  If a NAT cannot determine whether the endpoints of a TCP connection are active, it MAY abandon the session if it has been idle for some time.  In such cases, the value of the "established connection idle-timeout" MUST NOT be less than 2 hours 4 minutes. The value of the "transitory connection idle-timeout" MUST NOT be less than 4 minutes.
- [ ] REQ-6:  If a NAT includes ALGs that affect TCP, it is RECOMMENDED that all of those ALGs (except for FTP [RFC0959]) be disabled by default.
- [ ] REQ-7:  A NAT MUST NOT have a "Port assignment" behavior of "Port overloading" for TCP.
- [ ] REQ-8:  A NAT MUST support "hairpinning" for TCP.
- [ ] REQ-9:  If a NAT translates TCP, it SHOULD translate ICMP Destination Unreachable (Type 3) messages.
- [ ] REQ-10:  Receipt of any sort of ICMP message MUST NOT terminate the NAT mapping or TCP connection for which the ICMP was generated.

#### ICMP [rfc5508-req]

- [ ] REQ-1: Unless explicitly overridden by local policy, a NAT device MUST permit ICMP Queries and their associated responses, when the Query is initiated from a private host to the external hosts.
- [ ] REQ-2: An ICMP Query session timer MUST NOT expire in less than 60 seconds.
- [ ] REQ-3: When an ICMP Error packet is received, if the ICMP checksum fails to validate, the NAT SHOULD silently drop the ICMP Error packet.  If the ICMP checksum is valid, do the following:
- [ ] REQ-4: If a NAT device receives an ICMP Error packet from an external realm, and the NAT device does not have an active mapping for the embedded payload, the NAT SHOULD silently drop the ICMP Error packet.  If the NAT has active mapping for the embedded payload, then the NAT MUST do the following prior to forwarding the packet, unless explicitly overridden by local policy:
- [ ] REQ-5: If a NAT device receives an ICMP Error packet from the private realm, and the NAT does not have an active mapping for the embedded payload, the NAT SHOULD silently drop the ICMP Error packet.  If the NAT has active mapping for the embedded payload, then the NAT MUST do the following prior to forwarding the packet, unless explicitly overridden by local policy.
- [ ] REQ-6: While processing an ICMP Error packet pertaining to an ICMP Query or Query response message, a NAT device MUST NOT refresh or delete the NAT Session that pertains to the embedded payload within the ICMP Error packet.
- [ ] REQ-7: NAT devices enforcing Basic NAT ([NAT-TRAD]) MUST support the traversal of hairpinned ICMP Query sessions.  All NAT devices (i.e., Basic NAT as well as NAPT devices) MUST support the traversal of hairpinned ICMP Error messages.
- [ ] REQ-8: When a NAT device is unable to establish a NAT Session for a new transport-layer (TCP, UDP, ICMP, etc.) flow due to resource constraints or administrative restrictions, the NAT device SHOULD send an ICMP destination unreachable message, with a code of 13 (Communication administratively prohibited) to the sender, and drop the original packet.
- [ ] REQ-9: A NAT device MAY implement a policy control that prevents ICMP messages being generated toward certain interface(s). Implementation of such a policy control overrides the MUSTs and SHOULDs in REQ-10.
- [ ] REQ-10: Unless overridden by REQ-9's policy, a NAT device needs to support ICMP messages as below, some conforming to Section 4.3 of [RFC1812] and some superseding the requirements of Section 4.3 of [RFC1812]:
- [ ] REQ-11: A NAT MAY drop or appropriately handle Non-QueryError ICMP messages.  The semantics of Non-QueryError ICMP messages is defined in Section 2.

### CGN [rfc6888-req]

What follows is a list of requirements for CGN (Carrier Grade NAT). They are in addition to those found in other documents such as [RFC4787], [RFC5382], and [RFC5508].

- [ ] REQ-1: If a CGN forwards packets containing a given transport protocol, then it MUST fulfill that transport protocol's behavioral requirements.
- [ ] REQ-2: A CGN MUST have a default "IP address pooling" behavior of "Paired" (as defined in Section 4.1 of [RFC4787]). A CGN MAY provide a mechanism for administrators to change this behavior on an application protocol basis.
- [ ] REQ-3: The CGN function SHOULD NOT have any limitations on the size or the contiguity of the external address pool. In particular, the CGN function MUST be configurable with contiguous or non- contiguous external IPv4 address ranges.
- [ ] REQ-4: A CGN MUST support limiting the number of external ports (or, equivalently, "identifiers" for ICMP) that are assigned per subscriber.
- [ ] REQ-5: A CGN SHOULD support limiting the amount of state memory allocated per mapping and per subscriber. This may include limiting the number of sessions, the number of filters, etc., depending on the NAT implementation.
- [ ] REQ-6: It MUST be possible to administratively turn off translation for specific destination addresses and/or ports.
- [ ] REQ-7: It is RECOMMENDED that a CGN use an "endpoint-independent filtering" behavior (as defined in Section 5 of [RFC4787]). If it is known that "Address-Dependent Filtering" does not cause the application-layer protocol to break (how to determine this is out of scope for this document), then it MAY be used instead.
- [ ] REQ-8: Once an external port is deallocated, it SHOULD NOT be reallocated to a new mapping until at least 120 seconds have passed, with the exceptions being: ...
- [ ] REQ-9: A CGN MUST implement a protocol giving subscribers explicit control over NAT mappings. That protocol SHOULD be the Port Control Protocol [RFC6887].
- [ ] REQ-10: CGN implementers SHOULD make their equipment manageable. Standards-based management using standards such as "Definitions of Managed Objects for NAT" [RFC4008] is RECOMMENDED.
- [ ] REQ-11: When a CGN is unable to create a dynamic mapping due to resource constraints or administrative restrictions (i.e., quotas): ...
- [ ] REQ-12: A CGN SHOULD NOT log destination addresses or ports unless required to do so for administrative reasons.
- [ ] REQ-13: A CGN's port allocation scheme SHOULD maximize port utilization.
- [ ] REQ-14: A CGN's port allocation scheme SHOULD minimize log volume.
- [ ] REQ-15: A CGN's port allocation scheme SHOULD make it hard for attackers to guess port numbers.

### NAT44 Benchmarking

IETF [draft-ngfw-perf] specifies industry standard way to benchmark next generation security functions including NAT44 and ngFW. It has been developed by netsecopen.org and IETF BMWG (Benchmarking Working Group).

Following is the list of automated benchmarking tests (based on ) to be developed in CSIT, listed in sequential priority order:

- [ ] TCP/HTTP Connections Per Second
- [ ] Throughput Performance With Traffic Mix
- [ ] Concurrent TCP/HTTP Connection Capacity
- [ ] HTTP Throughput
- [ ] TCP/HTTP Transaction Latency

Secondary set of tests to be developed is related to changed traffic profile with TLS, in case it matters for NAT44 functionality under test.

- [ ] TCP/HTTPS Connections per second
- [ ] HTTPS Throughput
- [ ] Concurrent TCP/HTTPS Connection Capacity
- [ ] HTTPS Transaction Latency

## CSIT VPP NAT44 Benchmarks

### NAT44-EI

#### Prefix Binding Schemes

NAT44-EI prefix bindings should be representative to the target CG-NAT application, where a number of private IPv4 addresses from the range defined by [rfc1918] is mapped to a smaller set of public IPv4 addresses from the public range.

Private address ranges to be used in tests:

- 192.168.0.0     -   192.168.255.255 (192.168/16 prefix)
  - Total of 2^16 (65'536) of usable IPv4 addresses.
  - Used in tests for up to 65'536 inside hosts.
- 172.16.0.0      -   172.31.255.255  (172.16/12 prefix)
  - Total of 2^20 (1'048'576) of usable IPv4 addresses.
  - Used in tests for up to 1'048'576 inside hosts.

Public address ranges to be used in tests should come from the actual Internet ranges as specified in IANA IPv4 Address Space Registry https://www.iana.org/assignments/ipv4-address-space/ipv4-address-space.xhtml.

Examples:

- 68.142.68/24 www.bt.com
- 35.156.134/24 www.bbc.co.uk

Calculating address sharing ratio and ports per inside host given the inside prefix and the outside prefix:

- Inputs
  - in-prefix e.g. length /18, 2^14 = 16'384 addresses
  - out-prefix e.g. length /24 2^8 = 256 addresses
  - usable-port-range = 64'512 ports, 1024-65535 per RFC4787
- Calculated NAT44-EI bindings
  - sharing-ratio = in-prefix / out-prefix = 64
  - ports-per-host = usable-port-range / ratio = 64'512 / 64 = 1008

Calculating the in-prefix given out-prefix, sharing-ratio and ports-per-host:

- Input:
  - out-prefix e.g. length /30, 2^2 = 4 addresses
  - sharing-ratio = 128
- in-prefix
  - out-prefix * ratio = 4 * 128 = 512 addresses, length /23
  - ports-per-host = 64'512 / 128 = 504

Table of sharing ratios and ports per host based on 64'512 (0xFC00) usable public ports:

sharing-ratio | ports-per-host
--------------|---------------
           16 |           4032
           32 |           2016
           64 |           1008
          128 |            504
          256 |            252
          512 |            126
         1024 |             63

#### Host and Session Scale

Host and NAT44-EI session scale to be tested is govern by the following logic:

- Number of hosts H[i] = (H[i-1] x 2^2) with H(0)=1'024, i = 1,2,3, ...
  - H[i] = 1'024, 4'096, 16'384, 65'536, 262'144, 1'048'576, ...
- Number of sessions S[i](ports-per-host) = H[i] * ports-per-host
  - ports-per-host = 63, sharing-ratio = 1024

     i |     hosts |   sessions
    ---|-----------|-----------
     0 |     1'024 |     64'512
     1 |     4'096 |    258'048
     2 |    16'384 |  1'032'192
     3 |    65'536 |  4'128'768
     4 |   262'144 | 16'515'072
     5 | 1'048'576 | 66'060'288

  - ports-per-host = 126, sharing-ratio = 512

     i |     hosts |    sessions
    ---|-----------|------------
     0 |     1'024 |     129'024
     1 |     4'096 |     516'096
     2 |    16'384 |   2'064'384
     3 |    65'536 |   8'257'536
     4 |   262'144 |  33'030'144
     5 | 1'048'576 | 132'120'576

#### VPP Configuration Example

All VPP CLI commands are based on user documentation wiki for NAT-EI (CG-NAT) [vpp-natei-wiki].

Example VPP configuration:

```
nat44 deterministic add in 192.168.16.0/20 out 68.142.68.4/30
nat44 deterministic add in 172.16.20.0/22 out 35.156.134.2/31
```

Resulting NAT44 operational state:

```
vpp# show nat44 deterministic mappings
NAT44 deterministic mappings:
 in 192.168.16.0/20 out 68.142.68.4/30
  outside address sharing ratio: 1024
  number of ports per inside host: 63
  sessions number: 0
 in 172.16.20.0/22 out 35.156.134.2/31
  outside address sharing ratio: 512
  number of ports per inside host: 126
  sessions number: 0
```

#### TRex Traffic Profile Examples

Stream profile-1:

- DUT NAT44-EI settings:
  - ports-per-host = 63, sharing-ratio = 1024
  - 258'048 sessions => 4096 inside hosts, 4 outside addresses
- Two streams sent in directions 0 --> 1 and 1 --> 0 at the same time
- Packet: ETH / IP / UDP
- Direction 0 --> 1:
  - Source IP address range:      192.168.16.0 - 192.168.31.255
  - Destination IP address range: 20.0.0.0 - 20.0.0.255
  - Source UDP port range:        1024 - 1086
  - Destination UDP port range:   1024 - 2048
- Direction 1 --> 0:
  - Source IP address range:      20.0.0.0 - 20.0.0.255
  - Destination IP address range: 68.142.68.4 - 68.142.68.7
  - Source UDP port range:        1024 - 2048
  - Destination UDP port range:   1024 - 65535

Stream profile-2:

- DUT NAT44-EI settings:
  - ports-per-host = 126, sharing-ratio = 512
  - 129'024 sessions => 1024 inside hosts, 2 outside addresses
- Two streams sent in directions 0 --> 1 and 1 --> 0 at the same time.
- Packet: ETH / IP / UDP
- Direction 0 --> 1:
  - Source IP address range:      172.16.20.0 - 172.16.23.255
  - Destination IP address range: 20.1.0.0 - 20.1.0.255
  - Source UDP port range:        1024 - 1149
  - Destination UDP port range:   1024 - 2048
- Direction 1 --> 0:
  - Source IP address range:      20.1.0.0 - 20.1.0.255
  - Destination IP address range: 35.156.134.2 - 35.156.134.3
  - Source UDP port range:        1024 - 2048
  - Destination UDP port range:   1024 - 65535

Stream profile-3:
- DUT NAT44-EI settings:
  - ports-per-host = 63, sharing-ratio = 1024
  - 1'032'192 sessions => 16'384 inside hosts, 16 outside addresses
 - Two streams sent in directions 0 --> 1 and 1 --> 0 at the same time.
 - Packet: ETH / IP / UDP
 - Direction 0 --> 1:
   - Source IP address range:      192.168.0.0 - 192.168.63.255
   - Destination IP address range: 20.0.0.0
   - Source UDP port range:        1024 - 1086
   - Destination UDP port range:   1024
 - Direction 1 --> 0:
   - Source IP address range:      20.0.0.0
   - Destination IP address range: 68.142.68.0 - 68.142.68.15
   - Source UDP port range:        1024
   - Destination UDP port range:   1024 - 65535


#### Initial Implementation

- Number of hosts H[i] = (H[i-1] x 2^2) with H(0)=1'024, i = 1,2,3, ...
  - H[i] = 1'024, 4'096, 16'384, 65'536, 262'144, 1'048'576, ...
- Number of sessions S[i](ports-per-host) = H[i] * ports-per-host
  - ports-per-host = 63, sharing-ratio = 1024

 i |     hosts |   sessions | src a+p inside                    | src a+p  outside                | dst a+p
---|-----------|------------|-----------------------------------|---------------------------------|--------------
 0 |     1'024 |     64'512 | 192.168.(0.0-3.255)     1024-1086 | 68.142.68.0          1024-65535 | 20.0.0.0 1024
 1 |     4'096 |    258'048 | 192.168.(0.0-15.255)    1024-1086 | 68.142.68.(0-3)      1024-65535 | 20.0.0.0 1024
 2 |    16'384 |  1'032'192 | 192.168.(0.0-63.255)    1024-1086 | 68.142.68.(0-15)     1024-65535 | 20.0.0.0 1024
 3 |    65'536 |  4'128'768 | 192.168.(0.0-255.255)   1024-1086 | 68.142.68.(0-63)     1024-65535 | 20.0.0.0 1024
 4 |   262'144 | 16'515'072 | 172.(16.0.0-19.255.255) 1024-1086 | 68.142.68.(0-255)    1024-65535 | 20.0.0.0 1024
 5 | 1'048'576 | 66'060'288 | 172.(16.0.0-31.255.255) 1024-1086 | 68.142.(68.0-71.255) 1024-65535 | 20.0.0.0 1024

#### Test Development TODO

CSIT tests of VPP NAT44-EI (Endpoint Independent mode, a.k.a. Deterministic NAT or Carrier Grade NAT) are using TRex STL APIs (Stateless Python API of TRex profile) [trex-stl] in combination with a flow simulator originally developed by Damjan Marion [flowsim].

Tests are developed following the IETF BMWG specification [draft-ngfw-perf].

Test developed in the following sequential order (status markup: WIP work-in-progress, TBA to-be-analysed):

- [ ] TCP/HTTP Connections Per Second
    - WIP, UDP simple traffic profile.
      - Flowsim equivalent:
        - New flows per second.
        - Skeleton traffic profile: https://github.com/dmarion/vpp-toys/blob/master/trex/stl/flowsim.py#L41
      - CSIT integration of flowsim.py
        - Stream and flow definition logic unchanged, some Python syntax fixes.
        - Integrates through base class from CSIT used today for all TRex traffic profiles.
        - Flowsim profile integration, https://gerrit.fd.io/r/c/csit/+/27339
          - Modifications to CSIT TRex STL profile: https://gerrit.fd.io/r/c/csit/+/27339/1/GPL/tools/trex/trex_stateless_profile.py
          - Flowsim: https://gerrit.fd.io/r/c/csit/+/27339/1/GPL/traffic_profiles/trex/flowsim.py
          - Traffic profile: https://gerrit.fd.io/r/c/csit/+/27339/1/GPL/traffic_profiles/trex/trex-sl-3n-ethip4-flowsim.py
          - TRex STL base class: https://gerrit.fd.io/r/c/csit/+/27339/1/GPL/traffic_profiles/trex/profile_trex_stateless_base_class.py
      - ETA 05-Jun, simple traffic profile, ready to merge.
- [ ] Throughput Performance With Traffic Mix
    - WIP, UDP simple traffic profile
      - Extend the existing NAT44 tests using TRex STL with continuous packet flows, no flowsim
        - 60k sessions (4k sip x 15 sudp) test
          - https://github.com/FDio/csit/blob/master/tests/vpp/perf/ip4/10ge2p1x710-ethip4udp-ip4scale4000-udpsrcscale15-nat44-ndrpdr.robot
            - https://github.com/FDio/csit/blob/master/tests/vpp/perf/ip4/10ge2p1x710-ethip4udp-ip4scale4000-udpsrcscale15-nat44-ndrpdr.robot#L63
            - | ${traffic_profile}= | trex-sl-3n-ethip4udp-4000u15p
            - https://github.com/FDio/csit/blob/master/GPL/traffic_profiles/trex/trex-sl-3n-ethip4udp-4000u15p.py
          - Existing tests to be extended to higher scale for throughput measurements
            - Stepping logic in terms of #sessions
              - Formula: N(i)=[N(i-1) x 2^3) with N(0)=8, i=1,2,3...
              - #sessions tested: 8, 64, 512, 4'096, 32'768, 262'144, 2’097’152, 16’777’216, 134’217’728, ...
      - New flowsim based tests
        - Skeleton traffic profile: https://github.com/dmarion/vpp-toys/blob/master/trex/stl/flowsim.py#L41
        - CSIT integration of flowsim.py
          - See Connections Per Second test description above.
          - Will use different input values to flowsim, exact logic TBA.
      - ETA 05-Jun, simple traffic profile, ready to merge.
    - TBA, UDP custom traffic profile(s)
      - ETA TBC, NetSecOPEN traffic profile per [draft-ngfw-perf].
- [ ] HTTP Throughput
  - WIP, HTTP, simple traffic mix
    - Evaluate if any differences from TCP/UDP traffic profiles.
- [ ] TCP/HTTP Transaction Latency
    - TBA
- [ ] Concurrent TCP/HTTP Connection Capacity
    - TBA

### NAT44-ED

#### Prefix Binding Schemes

NAT44-ED prefix bindings should be representative to the target NAT44-ED application, where a number of private IPv4 addresses from the range defined by [rfc1918] is mapped to a smaller set of public IPv4 addresses from the public range.

Private address ranges to be used in tests:

- 192.168.0.0     -   192.168.255.255 (192.168/16 prefix)
  - Total of 2^16 (65'536) of usable IPv4 addresses.
  - Used in tests for up to 65'536 inside hosts.
- 172.16.0.0      -   172.31.255.255  (172.16/12 prefix)
  - Total of 2^20 (1'048'576) of usable IPv4 addresses.
  - Used in tests for up to 1'048'576 inside hosts.

Public address ranges to be used in tests should come from the actual Internet ranges as specified in IANA IPv4 Address Space Registry https://www.iana.org/assignments/ipv4-address-space/ipv4-address-space.xhtml.

Examples:

- 68.142.68/24 www.bt.com
- 35.156.134/24 www.bbc.co.uk

Calculating address sharing ratio and ports per inside host given the inside prefix and the outside prefix:

- Inputs
  - in-prefix e.g. length /18, 2^14 = 16'384 addresses
  - out-prefix e.g. length /24 2^8 = 256 addresses
  - usable-port-range = 64'512 ports, 1024-65535 per RFC4787
- Calculated NAT44-ED bindings parameters
  - sharing-ratio = in-prefix / out-prefix = 64
  - ports-per-host = usable-port-range / ratio = 64'512 / 64 = 1008

Calculating the in-prefix given out-prefix, sharing-ratio and ports-per-host:

- Input:
  - out-prefix e.g. length /30, 2^2 = 4 addresses
  - sharing-ratio = 128
- in-prefix
  - out-prefix * ratio = 4 * 128 = 512 addresses, length /23
  - ports-per-host = 64'512 / 128 = 504

Table of sharing ratios and ports per host based on 64'512 (0xFC00) usable public ports:

sharing-ratio | ports-per-host
--------------|---------------
           16 |           4032
           32 |           2016
           64 |           1008
          128 |            504
          256 |            252
          512 |            126
         1024 |             63

#### Host and Session Scale

Host and NAT44-EI session scale to be tested is govern by the following logic:

- Number of hosts H[i] = (H[i-1] x 2^2) with H(0)=1'024, i = 1,2,3, ...
  - H[i] = 1'024, 4'096, 16'384, 65'536, 262'144, 1'048'576, ...
- Number of sessions S[i](ports-per-host) = H[i] * ports-per-host
  - ports-per-host = 63, sharing-ratio = 1024

     i |     hosts |   sessions
    ---|-----------|-----------
     0 |     1'024 |     64'512
     1 |     4'096 |    258'048
     2 |    16'384 |  1'032'192
     3 |    65'536 |  4'128'768
     4 |   262'144 | 16'515'072
     5 | 1'048'576 | 66'060'288

  - ports-per-host = 126, sharing-ratio = 512

     i |     hosts |    sessions
    ---|-----------|------------
     0 |     1'024 |     129'024
     1 |     4'096 |     516'096
     2 |    16'384 |   2'064'384
     3 |    65'536 |   8'257'536
     4 |   262'144 |  33'030'144
     5 | 1'048'576 | 132'120'576

#### VPP Configuration

All VPP CLI commands are based on user documentation wiki for NAT-ED [vpp-nated-wiki].

```
set interface nat44 in <intfc> out <intfc>
nat44 add address <ip4-range-start> [- <ip4-range-end>] [tenant-vrf <vrf-id>] [twice-nat] [del]
```

Sample configuration:

```
set interface nat44 in <intfc> out <intfc>
nat44 add address 68.142.68.0 - 68.142.68.15
```

#### TRex Traffic Profile Example

Stream profile

- DUT NAT44-EI settings:
  - ports-per-host = 63, sharing-ratio = 1024
  - 1'032'192 sessions => 16'384 inside hosts, 16 outside addresses
 - Two streams sent in directions 0 --> 1 and 1 --> 0 at the same time.
 - Packet: ETH / IP / UDP
 - Direction 0 --> 1:
   - Source IP address range:      192.168.0.0 - 192.168.63.255
   - Destination IP address range: 20.0.0.0
   - Source UDP port range:        63 randomly generated src ports in range 1024 - 65535
   - Destination UDP port range:   8080
 - Direction 1 --> 0:
   - Source IP address range:      20.0.0.0
   - Destination IP address range: 68.142.68.0 - 68.142.68.15
   - Source UDP port range:        8080
   - Destination UDP port range:   63 dst ports matching the client src ports after NAT in range 1024 - 65535

#### Initial Implementation

- Number of hosts H[i] = (H[i-1] x 2^2) with H(0)=1'024, i = 1,2,3, ...
  - H[i] = 1'024, 4'096, 16'384, 65'536, 262'144, 1'048'576, ...
- Number of sessions S[i](ports-per-host) = H[i] * ports-per-host
  - ports-per-host = 63, sharing-ratio = 1024

     i |     hosts |   sessions | src a+p inside                          | src a+p  outside                | dst a+p
    ---|-----------|------------|-----------------------------------------|---------------------------------|--------------
     0 |     1'024 |     64'512 | 192.168.(0.0-3.255)     rnd(1024-65535) | 68.142.68.0          1024-65535 | 20.0.(0.0-3.255) 8080
     1 |     4'096 |    258'048 | 192.168.(0.0-15.255)    rnd(1024-65535) | 68.142.68.(0-3)      1024-65535 | 20.0.(0.0-15.255) 8080
     2 |    16'384 |  1'032'192 | 192.168.(0.0-63.255)    rnd(1024-65535) | 68.142.68.(0-15)     1024-65535 | 20.0.(0.0-63.255) 8080
     3 |    65'536 |  4'128'768 | 192.168.(0.0-255.255)   rnd(1024-65535) | 68.142.68.(0-63)     1024-65535 | 20.0.(0.0-255.255) 8080
     4 |   262'144 | 16'515'072 | 172.(16.0.0-19.255.255) rnd(1024-65535) | 68.142.68.(0-255)    1024-65535 | 20.(16.0.0-19.255.255) 8080
     5 | 1'048'576 | 66'060'288 | 172.(16.0.0-31.255.255) rnd(1024-65535) | 68.142.(68.0-71.255) 1024-65535 | 20.(16.0.0-31.255.255) 8080

Example of CSIT ASTF traffic profile for i=2:

https://gerrit.fd.io/r/c/csit/+/26898/32/GPL/traffic_profiles/trex/trex-astf-ethip4udp-1024u1p.py#42

```
    self.p1_src_start_ip = u"192.168.0.0"
    self.p1_src_end_ip = u"192.168.63.255"
    self.p1_dst_start_ip = u"20.0.0.0"
    self.p1_dst_end_ip = u"20.0.63.255"

    self.udp_req = u"GET"
    self.udp_res = u"ACK"
```

Test duration set in the test definition:

https://gerrit.fd.io/r/c/csit/+/26898/32/tests/vpp/perf/ip4/2n1l-10ge2p1x710-ethip4udp-ip4scale1024-nat44-ed-ndrpdr.robot#115

It is unclear if TRex executes complete multiplier * (src a+p inside) over 1sec or over duration of the test.
To clarify this with a simple ASTF synthetic flows, two set of tests are proposed:

- set-1, multiplier = number_of_flows = 1'032'192, duration = 1sec, 2sec, 4sec:
  - 1sec, `| | Set Test Variable | \${max_rate} | ${1032192}` => 63 sports/src-ip
  - 2sec, `| | Set Test Variable | \${max_rate} | ${1032192}` => 63 or 126 sports/src-ip
  - 4sec, `| | Set Test Variable | \${max_rate} | ${1032192}` => 63 or 252 sports/src-ip
- set-2, multiplier x duration = number_flows = 1'032'192, duration = 2sec, 4sec:
  - 2sec, `| | Set Test Variable | \${max_rate} | ${516096}` => 32 or 63 sports/src-ip
  - 4sec, `| | Set Test Variable | \${max_rate} | ${258048}` => 16 or 63 sports/src-ip

#### Test Development

CSIT tests of VPP NAT44-ED are using TRex ASTF APIs (Advanced Stateful Python API of TRex profile), [trex-astf].

Tests are developed following the IETF BMWG specification [draft-ngfw-perf].

Test developed in the following sequential order (status markup: WIP work-in-progress, TBA to-be-analysed):

- [ ] TCP/HTTP Connections Per Second
  - WIP, TCP and UDP simple traffic profile
    - T-Rex: Add advanced stateful mode, https://gerrit.fd.io/r/c/csit/+/27168
    - ASTF udp traffic profile: https://gerrit.fd.io/r/c/csit/+/27168/6/GPL/traffic_profiles/trex/trex-astf-ethip4udp-test.py
    - ETA 05-Jun, simple traffic profile, ready to merge.
  - TBA, TCP and UDP custom traffic profile(s)
    - ETA TBC, NetSecOPEN traffic profile per [draft-ngfw-perf].
- [ ] Throughput Performance With Traffic Mix
  - WIP, TCP and UDP, simple traffic mix
    - ASTF interface: https://gerrit.fd.io/r/c/csit/+/27168
    - ASTF traffic profile: https://gerrit.fd.io/r/c/csit/+/27168/6/GPL/traffic_profiles/trex/trex-astf-ethip4udp-test.py
    - ETA 05-Jun, simple traffic profile, ready to merge.
  - TBA, TCP and UDP custom traffic profile(s)
    - ETA TBC, NetSecOPEN traffic profile per [draft-ngfw-perf].
- [ ] HTTP Throughput
  - WIP, HTTP, simple traffic mix
    - Evaluate if any differences from TCP/UDP traffic profiles.
- [ ] TCP/HTTP Transaction Latency
    - TBA
- [ ] Concurrent TCP/HTTP Connection Capacity
    - TBA

## References

- [vpp-nat-wiki] VPP NAT, User documentation, https://wiki.fd.io/view/VPP/NAT
- [vpp-natei-wiki] VPP NAT-EI CG-NAT, User documentation, https://wiki.fd.io/view/VPP/NAT#CGN_-_deterministic_NAT
- [vpp-nated-wiki] VPP NAT-ED, User documentation, https://wiki.fd.io/view/VPP/NAT#CLI
- [vpp-nat-src] VPP NAT plugin source code, https://git.fd.io/vpp/tree/src/plugins/nat
- [rfc4787] Network Address Translation (NAT) Behavioral Requirements for Unicast UDP, https://tools.ietf.org/html/rfc4787
- [rfc4787-req] RFC4787 Requirements, https://tools.ietf.org/html/rfc4787#section-12
- [rfc5382] NAT Behavioral Requirements for TCP, https://tools.ietf.org/html/rfc5382
- [rfc5382-req] RFC5382 Requirements, https://tools.ietf.org/html/rfc5382#section-8
- [rfc5508] NAT Behavioral Requirements for ICMP.- REQ-1 to REQ-11 requirements
- [rfc5508-req] RFC5508 Summary of Requirements, https://tools.ietf.org/html/rfc5508#section-9
- [RFC7857] Updates to Network Address Translation (NAT) Behavioral Requirements, https://tools.ietf.org/html/rfc7857
- [draft-ngfw-perf] Benchmarking Methodology for Network Security Device Performance, https://tools.ietf.org/html/draft-ietf-bmwg-ngfw-performance-03
- [trex-astf] TRex Advanced Stateful Python API, https://trex-tgn.cisco.com/trex/doc/cp_astf_docs/index.html
- [trex-stl] TRex Stateless support, https://trex-tgn.cisco.com/trex/doc/trex_stateless.html
- [flowsim] Simulates UDP flows by creating multiple streams with random dst ports, https://github.com/dmarion/vpp-toys/blob/master/trex/stl/flowsim.py
- [rfc1918] Address Allocation for Private Internets, https://tools.ietf.org/html/rfc1918
