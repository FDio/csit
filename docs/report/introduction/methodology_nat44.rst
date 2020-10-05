Network Address Translation IPv4 to IPv4
----------------------------------------

NAT44 Prefix Bindings
^^^^^^^^^^^^^^^^^^^^^

NAT44det prefix bindings should be representative to the target CG-NAT
(Carrier Grade NAT) applications, where a number of private IPv4
addresses from the range defined by :rfc:`1918` is mapped to a smaller set
of public IPv4 addresses from the public range.

Private address ranges to be used in tests:

- 192.168.0.0 - 192.168.255.255 (192.168/16 prefix)
  - Total of 2^16 (65'536) of usable IPv4 addresses.
  - Used in tests for up to 65'536 inside hosts.
- 172.16.0.0 - 172.31.255.255  (172.16/12 prefix)
  - Total of 2^20 (1'048'576) of usable IPv4 addresses.
  - Used in tests for up to 1'048'576 inside hosts.

Calculating address sharing ratio and ports per inside host given the
inside prefix and the outside prefix:

- Inputs
  - in-prefix-length /18, 2^14 = 16'384 addresses
  - out-prefix-length /24 2^8 = 256 addresses
  - usable-port-range = 64'512 ports, 1024-65535
    per [rfc4787]
- Calculated NAT44det bindings
  - sharing-ratio = in-prefix-length / out-prefix-length = 64
  - ports-per-host = usable-port-range / sharing-ratio = 64'512 / 64 = 1008

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

NAT44 Session Scale
~~~~~~~~~~~~~~~~~~~

NAT44 session scale tested is govern by the following logic:

- Number of hosts H[i] = (H[i-1] x 2^2) with H(0)=1'024, i = 1,2,3, ...
  - H[i] = 1'024, 4'096, 16'384, 65'536, 262'144, 1'048'576, ...
- Number of sessions S[i](ports-per-host) = H[i] * ports-per-host
  - ports-per-host = 63, sharing-ratio = 1024

     i |     hosts |   sessions
    ---|-----------|-----------
     0 |     1 024 |     64 512
     1 |     4 096 |    258 048
     2 |    16 384 |  1 032 192
     3 |    65 536 |  4 128 768
     4 |   262 144 | 16 515 072

NAT44 Deterministic
^^^^^^^^^^^^^^^^^^^

CSIT NAT44det performance tests are using sharing-ratio of 1024 with
ports-per-host of 63. Up to 16.5 million sessions are tested.

NAT44det throughput tests are using TRex STL (Stateless) API and traffic
profiles, similar to all other stateless packet forwarding tests like
ip4, ip6 and l2, sending packets in both directions inside-to-outside
and outside-to-inside. See :ref:`data_plane_throughput` for more detail.

Associated CSIT test cases use the following naming scheme to indicate
NAT44det scenario tested:

- ethip4udp-nat44det-h{H}-p{P}-s{S}-[mrr|ndrpdr|soak]
  - {H}, number of inside hosts, H = 1024, 4096, 16384, 65536, 262144.
  - {P}, number of ports per inside host, P = 63.
  - {S}, number of sessions, S = 64.5k, 258k, 1M, 4.1M, 16.5M.
  - [mrr|ndrpdr|soak], MRR, NDRPDR or SOAK test.

NAT44 Endpoint-Dependent
^^^^^^^^^^^^^^^^^^^^^^^^

CSIT NAT44ed performance tests are using sharing-ratio of 1024 with
ports-per-host of 63. Up to 16.5 million sessions are tested.

NAT44ed is benchmarked using following methodologies:

- Uni-directional throughput using *stateless* traffic profile.
- Connections-per-second using *stateful* traffic profile.
- Bi-directional throughput using *stateful* traffic profile.

Uni-directional NAT44ed throughput tests are using TRex STL (Stateless)
APIs and traffic profiles, but with packets sent only in
inside-to-outside direction. Due to indeterministic bindings of outside
to inside (src_addr,src_port) that are created dynamically at flow start
bidirectional testing is not possible with stateless traffic profiles.
See :ref:`data_plane_throughput` for more detail.

Stateful NAT44ed tests are using TRex ASTF (Advanced Stateful) APIs and
traffic profiles, with packets sent in both directions. Tests are run
with both UDP and TCP/IP sessions.

Associated CSIT test cases use the following naming scheme to indicate
NAT44DET case tested:

- Stateless: ethip4udp-nat44ed-h{H}-p{P}-s{S}-udir-[mrr|ndrpdr|soak]
  - {H}, number of inside hosts, H = 1024, 4096, 16384, 65536, 262144.
  - {P}, number of ports per inside host, P = 63.
  - {S}, number of sessions, S = 64.5k, 258k, 1M, 4.1M, 16.5M.
  - udir-[mrr|ndrpdr|soak], unidirectional stateless tests MRR, NDRPDR or SOAK.
- Stateful: ethip4[udp|tcp]-nat44ed-h{H}-p{P}-s{S}-[cps|pps]-[mrr|ndrpdr]
  - [udp|tcp], UDP or TCP/IP sessions
  - {H}, number of inside hosts, H = 1024, 4096, 16384, 65536, 262144.
  - {P}, number of ports per inside host, P = 63.
  - {S}, number of sessions, S = 64.5k, 258k, 1M, 4.1M, 16.5M.
  - [cps|pps], connections-per-second session establishment rate or
    packets-per-second throughput rate.
  - [mrr|ndrpdr], bidirectional stateful tests MRR, NDRPDR.
