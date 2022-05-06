.. _nat44_methodology:

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

- Number of inside-addresses(hosts) H[i] = (H[i-1] x 2^2) with H(0)=1 024,
  i = 1,2,3, ...

  - H[i] = 1 024, 4 096, 16 384, 65 536, 262 144, ...

- Number of sessions S[i] = H[i] * ports-per-inside-address

  - ports-per-inside-address = 63

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

NAT44det performance tests are using TRex STL (Stateless) API and traffic
profiles, similar to all other stateless packet forwarding tests like
ip4, ip6 and l2, sending UDP packets in both directions
inside-to-outside and outside-to-inside. See
:ref:`data_plane_throughput` for more detail.

The inside-to-outside traffic uses single destination address (20.0.0.0)
and port (1024).
The inside-to-outside traffic covers whole inside address and port range,
the outside-to-inside traffic covers whole outside address and port range.

NAT44det translation entries are created during the ramp-up phase,
followed by verification that all entries are present,
before proceeding to the main measurements of the test.
This ensures session setup does not impact the forwarding performance test.

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
    TODO: Rename nat44det suites so it is clear they are throughput (not cps).
    TODO: Make traffic profile names resemble suite names more closely.

NAT44 Endpoint-Dependent
^^^^^^^^^^^^^^^^^^^^^^^^

In order to excercise NAT44ed ability to translate based on both
source and destination address and port, the inside-to-outside traffic
varies also destination address and port. Destination port is the same
as source port, destination address has the same offset as the source address,
but applied to different subnet (starting with 20.0.0.0).

As the mapping is not deterministic (for security reasons),
we cannot easily use stateless bidirectional traffic profiles.
Inside address and port range is fully covered,
but we do not know which outside-to-inside source address and port to use
to hit an open session.

Therefore, NAT44ed is benchmarked using following methodologies:

- Unidirectional throughput using *stateless* traffic profile.
- Connections-per-second using *stateful* traffic profile.
- Bidirectional PPS (see below) using *stateful* traffic profile.
- Bidirectional throughput (see below) using *stateful* traffic profile.

Unidirectional NAT44ed throughput tests are using TRex STL (Stateless)
APIs and traffic profiles, but with packets sent only in
inside-to-outside direction.
Similarly to NAT44det, NAT44ed unidirectional throughput tests include
a ramp-up phase to establish and verify the presence of required NAT44ed
binding entries. As the sessions have finite duration, the test code
keeps inserting ramp-up trials during the search, if it detects a risk
of sessions timing out. Any zero loss trial visits all sessions,
so it acts also as a ramp-up.

Stateful NAT44ed tests are using TRex ASTF (Advanced Stateful) APIs and
traffic profiles, with packets sent in both directions. Tests are run
with both UDP and TCP/IP sessions.
As both NAT44ed CPS (connections-per-second) and PPS (packets-per-second)
stateful tests measure (also) session opening performance,
they use state reset instead of ramp-up trial.
NAT44ed TPUT (bidirectional throughput) tests use the same traffic profile
as PPS tests, but also prepend ramp-up trials as in the unidirectional tests,
so the test results describe performance without translation entry
creation overhead.

Associated CSIT test cases use the following naming scheme to indicate
NAT44det case tested:

- Stateless: ethip4udp-nat44ed-h{H}-p{P}-s{S}-udir-[mrr|ndrpdr|soak]

  - {H}, number of inside hosts, H = 1024, 4096, 16384, 65536, 262144.
  - {P}, number of ports per inside host, P = 63.
  - {S}, number of sessions, S = 64512, 258048, 1032192, 4128768,
    16515072.
  - udir-[mrr|ndrpdr|soak], unidirectional stateless tests MRR, NDRPDR
    or SOAK.

- Stateful: ethip4[udp|tcp]-nat44ed-h{H}-p{P}-s{S}-[cps|pps|tput]-[mrr|ndrpdr]

  - [udp|tcp], UDP or TCP/IP sessions
  - {H}, number of inside hosts, H = 1024, 4096, 16384, 65536, 262144.
  - {P}, number of ports per inside host, P = 63.
  - {S}, number of sessions, S = 64512, 258048, 1032192, 4128768,
    16515072.
  - [cps|pps|tput], connections-per-second session establishment rate or
    packets-per-second average rate, or packets-per-second rate
    without session establishment.
  - [mrr|ndrpdr], bidirectional stateful tests MRR, NDRPDR.

Stateful traffic profiles
^^^^^^^^^^^^^^^^^^^^^^^^^

There are several important details which distinguish ASTF profiles
from stateless profiles.

General considerations
~~~~~~~~~~~~~~~~~~~~~~

Protocols
_________

ASTF profiles are limited to either UDP or TCP protocol.

Programs
________

Each template in the profile defines two "programs", one for client side
and one for server side.

Each program specifies when that side has to wait until enough data is received
(counted in packets for UDP and in bytes for TCP)
and when to send additional data. Together, the two programs
define a single transaction. Due to packet loss, transaction may take longer,
use more packets (retransmission) or never finish in its entirety.

Instances
_________

Client instance is created according to TPS parameter for the trial,
and sends the first packet of the transaction (in some cases more packets).
Each client instance uses a different source address (see sequencing below)
and random source port. The destination address also comes from a range,
but destination port has to be constant for a given program.

Server instance is created when the first packet arrives to the server side.

Source address and port of the first packet are used as destination address
and port for the server responses. This is the ability we need
when outside surface is not predictable.

When a program reaches its end, the instance is deleted.
This creates possible issues with server instances. If the server instance
does not read all the data client has sent, late data packets
can cause second copy of server instance to be created,
which breaks assumptions on how many packet a transaction should have.

The need for server instances to read all the data reduces the overall
bandwidth TRex is able to create in ASTF mode.

Note that client instances are not created on packets,
so it is safe to end client program without reading all server data
(unless the definition of transaction success requires that).

Sequencing
__________

ASTF profiles offer two modes for choosing source and destination IP addresses
for client programs: seqential and pseudorandom.
In current tests we are using sequential addressing only (if destination
address varies at all).

For client destination UDP/TCP port, we use a single constant value.
(TRex can support multiple program pairs in the same traffic profile,
distinguished by the port number.)

Transaction overlap
___________________

If a transaction takes longer to finish, compared to period implied by TPS,
TRex will have multiple client or server instances active at a time.

During calibration testing we have found this increases CPU utilization,
and for high TPS it can lead to TRex's Rx or Tx buffers becoming full.
This generally leads to duration stretching, and/or packet loss on TRex.

Currently used transactions were chosen to be short, so risk of bad behavior
is decreased. But in MRR tests, where load is computed based on NIC ability,
not TRex ability, anomalous behavior is still possible
(e.g. MRR values being way lower than NDR).

Delays
______

TRex supports adding constant delays to ASTF programs.
This can be useful, for example if we want to separate connection establishment
from data transfer.

But as TRex tracks delayed instances as active, this still results
in higher CPU utilization and reduced performance issues
(as other overlaping transactions). So the current tests do not use any delays.

Keepalives
__________

Both UDP and TCP protocol implementations in TRex programs support keepalive
duration. That means there is a configurable period of keepalive time,
and TRex sends keepalive packets automatically (outside the program)
for the time the program is active (started, not ended yet)
but not sending any packets.

For TCP this is generally not a big deal, as the other side usually
retransmits faster. But for UDP it means a packet loss may leave
the receiving program running.

In order to avoid keepalive packets, keepalive value is set to a high number.
Here, "high number" means that even at maximum scale and minimum TPS,
there are still no keepalive packets sent within the corresponding
(computed) trial duration. This number is kept the same also for
smaller scale traffic profiles, to simplify maintenance.

Transaction success
___________________

The transaction is considered successful at Layer-7 (L7) level
when both program instances close. At this point, various L7 counters
(unofficial name) are updated on TRex.

We found that proper close and L7 counter update can be CPU intensive,
whereas lower-level counters (ipackets, opackets) called L2 counters
can keep up with higher loads.

For some tests, we do not need to confirm the whole transaction was successful.
CPS (connections per second) tests are a typical example.
We care only for NAT44ed creating a session (needs one packet in inside-to-outside
direction per session) and being able to use it (needs one packet
in outside-to-inside direction).

Similarly in PPS (packets per second, combining session creation
with data transfer) tests, we care about NAT44ed ability to forward packets,
we do not care whether aplications (TRex) can fully process them at that rate.

Therefore each type of tests has its own formula (usually just one counter
already provided by TRex) to count "successful enough" transactions
and attempted transactions. Currently, all tests relying on L7 counters
use size-limited profiles, so they know what the count of attempted
transactions should be, but due to duration stretching
TRex might have been unable to send that many packets.
For search purposes, unattempted transactions are treated the same
as attempted but failed transactions.

Sometimes even the number of transactions as tracked by search algorithm
does not match the transactions as defined by ASTF programs.
See PPS profiles below.

UDP CPS
~~~~~~~

This profile uses a minimalistic transaction to verify NAT44ed session has been
created and it allows outside-to-inside traffic.

Client instance sends one packet and ends.
Server instance sends one packet upon creation and ends.

In principle, packet size is configurable,
but currently used tests apply only one value (100 bytes frame).

Transaction counts as attempted when opackets counter increases on client side.
Transaction counts as successful when ipackets counter increases on client side.

TCP CPS
~~~~~~~

This profile uses a minimalistic transaction to verify NAT44ed session has been
created and it allows outside-to-inside traffic.

Client initiates TCP connection. Client waits until connection is confirmed
(by reading zero data bytes). Client ends.
Server accepts the connection. Server waits for indirect confirmation
from client (by waiting for client to initiate close). Server ends.

Without packet loss, the whole transaction takes 7 packets to finish
(4 and 3 per direction, respectively).
From NAT44ed point of view, only the first two are needed to verify
the session got created.

Packet size is not configurable, but currently used tests report
frame size as 64 bytes.

Transaction counts as attempted when tcps_connattempt counter increases
on client side.
Transaction counts as successful when tcps_connects counter increases
on client side.

UDP PPS
~~~~~~~

This profile uses a small transaction of "request-response" type,
with several packets simulating data payload.

Client sends 5 packets and closes immediately.
Server reads all 5 packets (needed to avoid late packets creating new
server instances), then sends 5 packets and closes.
The value 5 was chosen to mirror what TCP PPS (see below) choses.

Packet size is configurable, currently we have tests for 100,
1518 and 9000 bytes frame (to match size of TCP PPS data frames, see below).

As this is a PPS test, we do not track the whole 10 packet transaction.
Similarly to stateless tests, we treat each packet as a "transaction"
for search algorthm packet loss purposes.
Therefore a "transaction" is attempted when opacket counter on client
or server side is increased. Transaction is successful if ipacket counter
on client or server side is increased.

If one of 5 client packets is lost, server instance will get stuck
in the reading phase. This probably decreases TRex performance,
but it leads to more stable results then alternatives.

TCP PPS
~~~~~~~

This profile uses a small transaction of "request-response" type,
with some data amount to be transferred both ways.

Client connects, sends 5 data packets worth of data,
receives 5 data packets worth of data and closes its side of the connection.
Server accepts connection, reads 5 data packets worth of data,
sends 5 data packets worth of data and closes its side of the connection.
Server read is needed to avoid premature close and second server instance.
Client read is not stricly needed, but acks allow TRex to close
the server instance quickly, thus saving CPU and improving performance.

The number 5 of data packets was chosen so TRex is able to send them
in a single burst, even with 9000 byte frame size (TRex has a hard limit
on initial window size).
That leads to 16 packets (9 of them in c2s direction) to be exchanged
if no loss occurs.
The size of data packets is controlled by the traffic profile setting
the appropriate maximum segment size. Due to TRex restrictions,
the minimal size for IPv6 data frame achievable by this method is 70 bytes,
which is more than our usual minimum of 64 bytes.
For that reason, the minimal frame size tested is 100 bytes
(that allows room for eventually adding IPv6 ASTF tests),
1518 bytes and 9000 bytes.

Exactly as in UDP_PPS, ipackets and opackets counters are used for counting
"transactions" (in fact packets).

If packet loss occurs, there can be large transaction overlap, even if most
ASTF programs finish eventually. This can leads to big duration stretching
and somehow uneven rate of packets sent. This makes it hard to interpret
MRR results, but NDR and PDR results tend to be stable enough.

Ip4base tests
^^^^^^^^^^^^^

Contrary to stateless traffic profiles, we do not have a simple limit
that would guarantee TRex is able to send traffic at specified load.
For that reason, we have added tests where "nat44ed" is replaced by "ip4base".
Instead of NAT44ed processing, the tests set minimalistic IPv4 routes,
so that packets are forwarded in both inside-to-outside and outside-to-inside
directions.

The packets arrive to server end of TRex with different source address&port
than in NAT44ed tests (no translation to outside values is done with ip4base),
but those are not specified in the stateful traffic profiles.
The server end (as always) uses the received address&port as destination
for outside-to-inside traffic. Therefore the same stateful traffic profile
works for both NAT44ed and ip4base test (of the same scale).

The NAT44ed results are displayed together with corresponding ip4base results.
If they are similar, TRex is probably the bottleneck.
If NAT44ed result is visibly smaller, it describes the real VPP performance.
