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

- Inside-addresses, number of inside source addresses
  (representing inside hosts).
- Ports-per-inside-address, number of TCP/UDP source
  ports per inside source address.
- Outside-addresses, number of outside (public) source addresses
  allocated to NAT44.
- Ports-per-outside-address, number of TCP/UDP source
  ports per outside source address. The maximal number of
  ports-per-outside-address usable for NAT is 64 512
  (in non-reserved port range 1024-65535, :rfc:`4787`).
- Sharing-ratio, equal to inside-addresses / outside-addresses.

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
and NAT44ed (Endpoint Dependent).

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

- Number of inside addresses/hosts H[i] = (H[i-1] x 2^2) with H(0)=1 024,
  i = 1,2,3, ...

  - H[i] = 1 024, 4 096, 16 384, 65 536, 262 144, ...

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

The inside-to-outside traffic uses single destination address (20.0.0.0)
and port (1024).
The inside-to-outside traffic covers whole inside address and port range,
the outside-to-inside traffic covers whole outside address and port range.

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

..
    TODO: The -s{S} part is redundant,
    we can save space by removing it.
    TODO: Make traffic profile names resemble suite names more closely.

NAT44 Endpoint-Dependent
^^^^^^^^^^^^^^^^^^^^^^^^

..
    TODO: Is it possible to test a NAT44ed scenario where the outside source
    address and port is limited to just one value?
    In theory, as long as every inside source address&port traffic
    uses a different destination address&port, there will be no conflicts,
    and we could use bidirectional stateless profiles.
    Possibly, VPP requires some amount of outside source address&port
    to remain unused for security reasons. But we can try to see what happens.

In order to excercise NAT44ed ability to translate based on both
source and destination address and port, the inside-to-outside traffic
varies also destination address and port. Destination port is the same
as source port, destination address has the same offset as the source address,
but applied to different subnet (starting with 20.0.0.0).

As the mapping is not deterministic (for security reasons),
we cannot easily use stateless bidirectional traffic profiles.
Outside address and port range is fully covered,
but we do not know which outside-to-inside source address and port to use
to hit an open session of a particular outside address and port.

Therefore, NAT44ed is benchmarked using following methodologies:

- Uni-directional throughput using *stateless* traffic profile.
- Connections-per-second using *stateful* traffic profile.
- Bi-directional PPS (see below) using *stateful* traffic profile.

Uni-directional NAT44ed throughput tests are using TRex STL (Stateless)
APIs and traffic profiles, but with packets sent only in
inside-to-outside direction.
Similarly to NAT44det, NAT44ed uni-directional throughput tests include
a ramp-up phase to establish and verify the presence of required NAT44ed
binding entries.

Stateful NAT44ed tests are using TRex ASTF (Advanced Stateful) APIs and
traffic profiles, with packets sent in both directions. Tests are run
with both UDP and TCP/IP sessions.
As both NAT44ed CPS (connections-per-second) and throughput /
PPS stateful tests measure (also) session opening performance,
they use state reset instead of ramp-up trial.
That is also the reason why PPS tests are not called throughput tests.

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

Stateful traffic profiles
^^^^^^^^^^^^^^^^^^^^^^^^^

WiP.

UDP CPS
~~~~~~~

TCP CPS
~~~~~~~

UDP PPS
~~~~~~~

TCP PPS
~~~~~~~

Ip4base tests
^^^^^^^^^^^^^

Contrary to stateless traffic profiles, we do not have a simple limit
that would guarantee Trex is able to send traffic at specified load.
For that reason, whe have added tests where "nat44ed" is replaced by "ip4base".
Instead of NAT processing, the tests set minimalistic IP4 routes
so packets are forwarded in both inside-to-outside and outside-to-inside
directions.

The packets arrive to server end of Trex with different source address&port
than in nat44ed tests (no translation to outside values is done with ip4base),
but those are not specified in the stateful traffic profiles.
The server end uses the received address&port as destination
for outside-to-inside traffic. Therefore the same stateful traffic profile
work for both nat44ed and ip4base test (of the same scale).

The nat44ed results are displayed together with corresponding ip4base results.
If they are similar, Trex is probably the bottleneck.
If nat44ed result is visibly smaller, it describes the real VPP performance.
