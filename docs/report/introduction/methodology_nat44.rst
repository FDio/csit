Network Address Translation IPv4 to IPv4
----------------------------------------

NAT44 Prefix Bindings
^^^^^^^^^^^^^^^^^^^^^

NAT44 prefix bindings should be representative to target applications,
where a number of private IPv4 addresses from the range defined by
:rfc:`1918` is mapped to a smaller set of public IPv4 addresses from the
public range.

Following quantities are used to describe inside to outside IP address
and port bindings scenarios:

- inside-addresses, ports-per-inside-address, number of inside source
  addresses (representing inside hosts) and number of TCP/UDP source
  ports per inside source address.
- outside-addresses, number of outside (public) source addresses
  allocated to NAT44. The maximal number of ports-per-outside-address
  usable for NAT is 64 512 (in non-reserved port range 1024-65535,
  :rfc:`4787`).
- sharing-ratio, equal to inside-addresses / outside-addresses.

CSIT NAT44 tests are designed to take into account the maximum number of
ports (sessions) required per inside host (inside-address) and at the
same time to maximize the use of outside-address range by using all
available outside ports. With this in mind, the following scheme of
NAT44 sharing ratios has been devised for use in CSIT:

+--------------------------+---------------+
| ports-per-inside-address | sharing-ratio |
+==========================+===============+
| 63                       | 1024          |
+--------------------------+---------------+
| 126                      | 512           |
+--------------------------+---------------+
| 252                      | 256           |
+--------------------------+---------------+
| 504                      | 128           |
+--------------------------+---------------+

Initial CSIT NAT44 tests, including associated TG/TRex traffic profiles,
are based on ports-per-inside-address set to 63 and the sharing ratio of
1024. This approach is currently used for all NAT44 tests including
NAT44det (NAT44 deterministic used for Carrier Grade NAT applications)
and NAT44ed.

..
    .. TODO::

    Note that in the latter case, due to overloading of (ouside-address,
    outside-port) tuple for different endpoint destinations the actual
    sharing ratio is likely to different, as it will depend on the
    destination addresses used by NAT'ed flows.

Private address ranges to be used in tests:

- 192.168.0.0 - 192.168.255.255 (192.168/16 prefix)

  - Total of 2^16 (65 536) of usable IPv4 addresses.
  - Used in tests for up to 65 536 inside addresses (inside hosts).

- 172.16.0.0 - 172.31.255.255  (172.16/12 prefix)

  - Total of 2^20 (1 048 576) of usable IPv4 addresses.
  - Used in tests for up to 1 048 576 inside addresses (inside hosts).

NAT44 Session Scale
~~~~~~~~~~~~~~~~~~~

NAT44 session scale tested is govern by the following logic:

- Number of inside addresses/hosts H[i] = (H[i-1] x 2^2) with H(0)=1 024, i = 1,2,3, ...

  - H[i] = 1 024, 4 096, 16 384, 65 536, 262 144, 1 048 576, ...

- Number of sessions S[i](ports-per-host) = H[i] * ports-per-inside-address

  - ports-per-host = 63

+---+---------+------------+
| i |   hosts |   sessions |
+===+=========+============+
| 0 |   1 024 |     64 512 |
+---+---------+------------+
| 1 |   4 096 |    258 048 |
+---+---------+------------+
| 2 |  16 384 |  1 032 192 |
+---+---------+------------+
| 3 |  65 536 |  4 128 768 |
+---+---------+------------+
| 4 | 262 144 | 16 515 072 |
+---+---------+------------+

NAT44 Deterministic
^^^^^^^^^^^^^^^^^^^

NAT44det throughput tests are using TRex STL (Stateless) API and traffic
profiles, similar to all other stateless packet forwarding tests like
ip4, ip6 and l2, sending UDP packets in both directions
inside-to-outside and outside-to-inside. See
:ref:`data_plane_throughput` for more detail.

NAT44det translation entries are created during the ramp-up phase
preceding the throughput test, followed by verification that all entries
are present, before proceeding to the throughput test. This ensures
session setup does not impact the forwarding performance test.

Associated CSIT test cases use the following naming scheme to indicate
NAT44det scenario tested:

- ethip4udp-nat44det-h{H}-p{P}-s{S}-[mrr|ndrpdr|soak]

  - {H}, number of inside hosts, H = 1024, 4096, 16384, 65536, 262144.
  - {P}, number of ports per inside host, P = 63.
  - {S}, number of sessions, S = 64512, 258048, 1032192, 4128768,
    16515072.
  - [mrr|ndrpdr|soak], MRR, NDRPDR or SOAK test.

NAT44 Endpoint-Dependent
^^^^^^^^^^^^^^^^^^^^^^^^

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

Similarly to NAT44det, NAT44ed uni-directional throughput tests include
a ramp-up phase to establish and verify the presence of required NAT44ed
binding entries. NAT44ed CPS (connections-per-second) and throughput /
PPS stateful tests do not have a ramp-up phase.

Stateful NAT44ed tests are using TRex ASTF (Advanced Stateful) APIs and
traffic profiles, with packets sent in both directions. Tests are run
with both UDP and TCP/IP sessions.

Associated CSIT test cases use the following naming scheme to indicate
NAT44DET case tested:

- Stateless: ethip4udp-nat44ed-h{H}-p{P}-s{S}-udir-[mrr|ndrpdr|soak]

  - {H}, number of inside hosts, H = 1024, 4096, 16384, 65536, 262144.
  - {P}, number of ports per inside host, P = 63.
  - {S}, number of sessions, S = 64512, 258048, 1032192, 4128768,
    16515072.
  - udir-[mrr|ndrpdr|soak], unidirectional stateless tests MRR, NDRPDR
    or SOAK.

- Stateful: ethip4[udp|tcp]-nat44ed-h{H}-p{P}-s{S}-[cps|pps]-[mrr|ndrpdr]

  - [udp|tcp], UDP or TCP/IP sessions
  - {H}, number of inside hosts, H = 1024, 4096, 16384, 65536, 262144.
  - {P}, number of ports per inside host, P = 63.
  - {S}, number of sessions, S = 64512, 258048, 1032192, 4128768,
    16515072.
  - [cps|pps], connections-per-second session establishment rate or
    packets-per-second throughput rate.
  - [mrr|ndrpdr], bidirectional stateful tests MRR, NDRPDR.
