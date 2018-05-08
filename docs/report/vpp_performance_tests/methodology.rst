Test Methodology
================

Multi-Core and Multi-Threading
------------------------------

**Intel Hyper-Threading** - CSIT |release| performance tests are executed with
SUT servers' Intel XEON processors configured in Intel Hyper-Threading Disabled
mode (BIOS setting). This is the simplest configuration used to establish
baseline single-thread single-core application packet processing and forwarding
performance. Subsequent releases of CSIT will add performance tests with Intel
Hyper-Threading Enabled (requires BIOS settings change and hard reboot of
server).

**Multi-core Tests** - CSIT |release| multi-core tests are executed in the
following VPP thread and core configurations:

#. 1t1c - 1 VPP worker thread on 1 CPU physical core.
#. 2t2c - 2 VPP worker threads on 2 CPU physical cores.
#. 4t4c - 4 VPP worker threads on 4 CPU physical cores.

VPP worker threads are the data plane threads. VPP control thread is
running on a separate non-isolated core together with other Linux
processes. Note that in quite a few test cases running VPP workers on 2
or 4 physical cores hits the I/O bandwidth or packets-per-second limit
of tested NIC.

Section :ref:`throughput_speedup_multi_core` includes a set of graphs
illustrating packet throughout speedup when running VPP on multiple
cores.

Packet Throughput
-----------------

Following values are measured and reported for packet throughput tests:

- NDR binary search per :rfc:`2544`:

  - Packet rate: "RATE: <aggregate packet rate in packets-per-second> pps
    (2x <per direction packets-per-second>)";
  - Aggregate bandwidth: "BANDWIDTH: <aggregate bandwidth in Gigabits per
    second> Gbps (untagged)";

- PDR binary search per :rfc:`2544`:

  - Packet rate: "RATE: <aggregate packet rate in packets-per-second> pps (2x
    <per direction packets-per-second>)";
  - Aggregate bandwidth: "BANDWIDTH: <aggregate bandwidth in Gigabits per
    second> Gbps (untagged)";
  - Packet loss tolerance: "LOSS_ACCEPTANCE <accepted percentage of packets
    lost at PDR rate>";

- NDR and PDR are measured for the following L2 frame sizes (untagged
  Ethernet):

  - IPv4 payload: 64B, IMIX_v4_1 (28x64B,16x570B,4x1518B), 1518B, 9000B;
  - IPv6 payload: 78B, 1518B, 9000B;

- NDR and PDR binary search resolution is determined by the final value of the
  rate change, referred to as the final step:

  - The final step is set to 50kpps for all NIC to NIC tests and all L2
    frame sizes except 9000B (changed from 100kpps used in previous
    releases).

  - The final step is set to 10kpps for all remaining tests, including 9000B
    and all vhost VM and memif Container tests.

All rates are reported from external Traffic Generator perspective.

Maximum Receive Rate (MRR)
--------------------------

MRR tests measure the packet forwarding rate under the maximum
load offered by traffic generator over a set trial duration,
regardless of packet loss. Maximum load for specified Ethernet frame
size is set to the bi-directional link rate.

Current parameters for MRR tests:

- Ethernet frame sizes: 64B (78B for IPv6 tests) for all tests, IMIX for
  selected tests (vhost, memif); all quoted sizes include frame CRC, but
  exclude per frame transmission overhead of 20B (preamble, inter frame
  gap).

- Maximum load offered: 10GE and 40GE link (sub-)rates depending on NIC
  tested, with the actual packet rate depending on frame size,
  transmission overhead and traffic generator NIC forwarding capacity.

  - For 10GE NICs the maximum packet rate load is 2* 14.88 Mpps for 64B,
    a 10GE bi-directional link rate.
  - For 40GE NICs the maximum packet rate load is 2* 18.75 Mpps for 64B,
    a 40GE bi-directional link sub-rate limited by TG 40GE NIC used,
    XL710.

- Trial duration: 10sec.

Similarly to NDR/PDR throughput tests, MRR test should be reporting bi-
directional link rate (or NIC rate, if lower) if tested VPP
configuration can handle the packet rate higher than bi-directional link
rate, e.g. large packet tests and/or multi-core tests.

MRR tests are used for continuous performance trending and for
comparison between releases.

Packet Latency
--------------

TRex Traffic Generator (TG) is used for measuring latency of VPP DUTs. Reported
latency values are measured using following methodology:

- Latency tests are performed at 10%, 50% of discovered NDR rate (non drop rate)
  for each NDR throughput test and packet size (except IMIX).
- TG sends dedicated latency streams, one per direction, each at the rate of
  10kpps at the prescribed packet size; these are sent in addition to the main
  load streams.
- TG reports min/avg/max latency values per stream direction, hence two sets
  of latency values are reported per test case; future release of TRex is
  expected to report latency percentiles.
- Reported latency values are aggregate across two SUTs due to three node
  topology used for all performance tests; for per SUT latency, reported value
  should be divided by two.
- 1usec is the measurement accuracy advertised by TRex TG for the setup used in
  FD.io labs used by CSIT project.
- TRex setup introduces an always-on error of about 2*2usec per latency flow -
  additonal Tx/Rx interface latency induced by TRex SW writing and reading
  packet timestamps on CPU cores without HW acceleration on NICs closer to the
  interface line.

vhostuser with KVM VMs
----------------------

FD.io CSIT performance lab is testing VPP vhost with KVM VMs using following
environment settings:

- Tests with varying Qemu virtio queue (a.k.a. vring) sizes: [vr256] default 256
  descriptors, [vr1024] 1024 descriptors to optimize for packet throughput.

- Tests with varying Linux :abbr:`CFS (Completely Fair Scheduler)` settings:
  [cfs] default settings, [cfsrr1] CFS RoundRobin(1) policy applied to all data
  plane threads handling test packet path including all VPP worker threads and
  all Qemu testpmd poll-mode threads.

- Resulting test cases are all combinations with [vr256,vr1024] and
  [cfs,cfsrr1] settings.

- Adjusted Linux kernel :abbr:`CFS (Completely Fair Scheduler)` scheduler policy
  for data plane threads used in CSIT is documented in
  `CSIT Performance Environment Tuning wiki <https://wiki.fd.io/view/CSIT/csit-perf-env-tuning-ubuntu1604>`_.
  The purpose is to verify performance impact (MRR and NDR/PDR
  throughput) and same test measurements repeatability, by making VPP
  and VM data plane threads less susceptible to other Linux OS system
  tasks hijacking CPU cores running those data plane threads.

Memif with LXC and Docker Containers
------------------------------------

CSIT |release| includes tests taking advantage of VPP memif virtual
interface (shared memory interface) to interconnect VPP running in
Containers. VPP vswitch instance runs in bare-metal user-mode handling
NIC interfaces and connecting over memif (Slave side) to VPPs running in
:abbr:`Linux Container (LXC)` or in Docker Container (DRC) configured
with memif (Master side). LXCs and DRCs run in a priviliged mode with
VPP data plane worker threads pinned to dedicated physical CPU cores per
usual CSIT practice. All VPP instances run the same version of software.
This test topology is equivalent to existing tests with vhost-user and
VMs as described earlier in :ref:`tested_physical_topologies`.

More information about CSIT LXC and DRC setup and control is available
in :ref:`container_orchestration_in_csit`.

Memif with K8s Pods/Containers
------------------------------

CSIT |release| includes tests of VPP topologies running in K8s
orchestrated Pods/Containers and connected over memif virtual
interfaces. In order to provide simple topology coding flexibility and
extensibility container orchestration is done with `Kubernetes
<https://github.com/kubernetes>`_ using `Docker
<https://github.com/docker>`_ images for all container applications
including VPP. `Ligato <https://github.com/ligato>`_ is used for the
Pod/Container networking orchestration that is integrated with K8s,
including memif support.

In these tests VPP vswitch runs in a K8s Pod with Docker Container (DRC)
handling NIC interfaces and connecting over memif to more instances of
VPP running in Pods/DRCs. All DRCs run in a priviliged mode with VPP
data plane worker threads pinned to dedicated physical CPU cores per
usual CSIT practice. All VPP instances run the same version of software.
This test topology is equivalent to existing tests with vhost-user and
VMs as described earlier in :ref:`tested_physical_topologies`.

Further documentation is available in
:ref:`container_orchestration_in_csit`.

IPSec with Intel QAT HW cards
-----------------------------

VPP IPSec performance tests are using DPDK cryptodev device driver in
combination with HW cryptodev devices - Intel QAT 8950 50G - present in
LF FD.io physical testbeds. DPDK cryptodev can be used for all IPSec
data plane functions supported by VPP.

Currently CSIT |release| implements following IPSec test cases:

- AES-GCM, CBC-SHA1 ciphers, in combination with IPv4 routed-forwarding
  with Intel xl710 NIC.
- CBC-SHA1 ciphers, in combination with LISP-GPE overlay tunneling for
  IPv4-over-IPv4 with Intel xl710 NIC.

TRex Traffic Generator Usage
----------------------------

`TRex traffic generator <https://wiki.fd.io/view/TRex>`_ is used for all
CSIT performance tests. TRex stateless mode is used to measure NDR and PDR
throughputs using binary search (NDR and PDR discovery tests) and for quick
checks of DUT performance against the reference NDRs (NDR check tests) for
specific configuration.

TRex is installed and run on the TG compute node. The typical procedure is:

- If the TRex is not already installed on TG, it is installed in the
  suite setup phase - see `TRex intallation`_.
- TRex configuration is set in its configuration file
  ::

  /etc/trex_cfg.yaml

- TRex is started in the background mode
  ::

  $ sh -c 'cd <t-rex-install-dir>/scripts/ && sudo nohup ./t-rex-64 -i -c 7 --iom 0 > /tmp/trex.log 2>&1 &' > /dev/null

- There are traffic streams dynamically prepared for each test, based on traffic
  profiles. The traffic is sent and the statistics obtained using
  :command:`trex_stl_lib.api.STLClient`.

**Measuring packet loss**

- Create an instance of STLClient
- Connect to the client
- Add all streams
- Clear statistics
- Send the traffic for defined time
- Get the statistics

If there is a warm-up phase required, the traffic is sent also before test and
the statistics are ignored.

**Measuring latency**

If measurement of latency is requested, two more packet streams are created (one
for each direction) with TRex flow_stats parameter set to STLFlowLatencyStats. In
that case, returned statistics will also include min/avg/max latency values.

TCP/IP tests with WRK tool
--------------------------

`WRK HTTP benchmarking tool <https://github.com/wg/wrk>`_ is used for
experimental TCP/IP and HTTP tests of VPP TCP/IP stack and built-in
static HTTP server. WRK has been chosen as it is capable of generating
significant TCP/IP and HTTP loads by scaling number of threads across
multi-core processors.

This in turn enables quite high scale benchmarking of the main TCP/IP
and HTTP service including HTTP TCP/IP Connections-Per-Second (CPS),
HTTP Requests-Per-Second and HTTP Bandwidth Throughput.

The initial tests are designed as follows:

- HTTP and TCP/IP Connections-Per-Second (CPS)

  - WRK configured to use 8 threads across 8 cores, 1 thread per core.
  - Maximum of 50 concurrent connections across all WRK threads.
  - Timeout for server responses set to 5 seconds.
  - Test duration is 30 seconds.
  - Expected HTTP test sequence:

    - Single HTTP GET Request sent per open connection.
    - Connection close after valid HTTP reply.
    - Resulting flow sequence - 8 packets: >S,<S-A,>A,>Req,<Rep,>F,<F,> A.

- HTTP Requests-Per-Second

  - WRK configured to use 8 threads across 8 cores, 1 thread per core.
  - Maximum of 50 concurrent connections across all WRK threads.
  - Timeout for server responses set to 5 seconds.
  - Test duration is 30 seconds.
  - Expected HTTP test sequence:

    - Multiple HTTP GET Requests sent in sequence per open connection.
    - Connection close after set test duration time.
    - Resulting flow sequence: >S,<S-A,>A,>Req[1],<Rep[1],..,>Req[n],<Rep[n],>F,<F,>A.
