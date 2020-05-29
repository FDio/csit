## Front Matter

  Filename: csit-vpp-bench-spec-nat44.md
  Author: mkonstan@cisco.com
  Date: 29-05-2020

## Overview

  This note specifies FD.io CSIT test plan for VPP NAT44 tests.

## Reference Specifications

### Behavioral for NAT

  Following IETF documents specify NAT behaviour for the use case(s) targetted by Umbrella CDFW VPP:

  - [RFC4787] Network Address Translation (NAT) Behavioral Requirements for Unicast UDP.
  - [RFC5382] NAT Behavioral Requirements for TCP.
  - [RFC5508] NAT Behavioral Requirements for ICMP.
  - [RFC7857] Updates to Network Address Translation (NAT) Behavioral Requirements.

  The actual CDFW NAT requirements [cdfw-nat-req] and VPP support [vpp-nat-wiki], [vpp-nat-src] are to be checklisted against above specs.

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

### Benchmarking for NAT44

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

## CSIT VPP NAT44 Tests

### NAT44 Endpoint Dependent Mode

  CSIT tests of VPP NAT44-ED (Endpoint Dependent mode) are using TRex ASTF APIs (Advanced Stateful Python API of TRex profile), [trex-astf].

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

### NAT44 Endpoint Dependent Mode

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

## VPP NAT44 Configurations

  All VPP NAT44 configurations are based on user documentation [vpp-nat-wiki].

### NAT44 Endpoint Dependent Mode

#### Configuration

  All VPP CLI commands are based on user documentation wiki for NAT-ED [vpp-nated-wiki].

#### Matching Traffic Profile

### NAT44 Endpoint Independent Mode

#### Configuration

  All VPP CLI commands are based on user documentation wiki for NAT-EI (CG-NAT) [vpp-natei-wiki].

  TODO Edit all of the below content to align with the actual tests. Insert variables as used by test.

  ```
  To enable NAT feature (local network interface GigabitEthernet0/8/0 and external network interface GigabitEthernet0/a/0) use:

  vpp# set int nat44 in GigabitEthernet0/8/0 out GigabitEthernet0/a/0
  To create deterministic mapping between inside network 10.0.0.0/18 and outside address range 1.1.1.0/30 use:

  vpp# nat44 deterministic add in 10.0.0.0/18 out 1.1.1.1/30
  To show deterministic mapping information use:

  vpp# show nat44 deterministic mappings
  NAT44 deterministic mappings:
   in 10.0.0.0/24 out 1.1.1.1/32
    outside address sharing ratio: 256
    number of ports per inside host: 252
    sessions number: 0
  To obtain outside address and port range of the inside host 10.0.0.2 use:

  vpp# nat44 deterministic forward 10.0.0.2
  1.1.1.0:<1054-1068>
  To obtain inside host address from outside address 1.1.1.1 and port 1276 use:

  vpp# nat44 deterministic reverse 1.1.1.1:1276
  10.0.16.16
  ```

#### Matching Traffic Profile

  TODO Edit all of the below content to align with the actual tests. Insert variables as used by test.

  CSIT test: https://github.com/FDio/csit/blob/master/GPL/traffic_profiles/trex/trex-sl-3n-ethip4udp-4000u15p.py

  """Stream profile for T-rex traffic generator.
  Stream profile:
   - Two streams sent in directions 0 --> 1 and 1 --> 0 at the same time.
   - Packet: ETH / IP / UDP
   - Direction 0 --> 1:
     - Source IP address range:      20.0.0.0 - 20.0.15.159
     - Destination IP address range: 12.0.0.2
     - Source UDP port range:        1024 - 1038
     - Destination UDP port range:   1024
   - Direction 1 --> 0:
     - Source IP address range:      12.0.0.2
     - Destination IP address range: 200.0.0.0
     - Source UDP port range:        1024
     - Destination UDP port range:   1024 - 61022
  """

## References

  [cdfw-nat-req] NAT Requirements for CDP, https://docs.google.com/document/d/1seeY4Vy7HmpZoAznNhdZJFykPwSt7IOHszyKub3aTjA/edit
  [vpp-nat-wiki] VPP NAT, User documentation, https://wiki.fd.io/view/VPP/NAT
  [vpp-natei-wiki] VPP NAT-EI CG-NAT, User documentation, https://wiki.fd.io/view/VPP/NAT#CGN_-_deterministic_NAT
  [vpp-nated-wiki] VPP NAT-ED, User documentation, https://wiki.fd.io/view/VPP/NAT#CLI
  [vpp-nat-src] VPP NAT plugin source code, https://git.fd.io/vpp/tree/src/plugins/nat
  [rfc4787] Network Address Translation (NAT) Behavioral Requirements for Unicast UDP, https://tools.ietf.org/html/rfc4787
  [rfc4787-req] RFC4787 Requirements, https://tools.ietf.org/html/rfc4787#section-12
  [rfc5382] NAT Behavioral Requirements for TCP, https://tools.ietf.org/html/rfc5382
  [rfc5382-req] RFC5382 Requirements, https://tools.ietf.org/html/rfc5382#section-8
  [rfc5508] NAT Behavioral Requirements for ICMP.- REQ-1 to REQ-11 requirements
  [rfc5508-req] RFC5508 Summary of Requirements, https://tools.ietf.org/html/rfc5508#section-9
  [RFC7857] Updates to Network Address Translation (NAT) Behavioral Requirements, https://tools.ietf.org/html/rfc7857
  [draft-ngfw-perf] Benchmarking Methodology for Network Security Device Performance, https://tools.ietf.org/html/draft-ietf-bmwg-ngfw-performance-03
  [trex-astf] TRex Advanced Stateful Python API, https://trex-tgn.cisco.com/trex/doc/cp_astf_docs/index.html
  [trex-stl] TRex Stateless support, https://trex-tgn.cisco.com/trex/doc/trex_stateless.html
  [flowsim] Simulates UDP flows by creating multiple streams with random dst ports, https://github.com/dmarion/vpp-toys/blob/master/trex/stl/flowsim.py
