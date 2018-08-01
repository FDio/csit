Performance Test Methodology
============================

Throughput
----------

Packet and bandwidth throughput are measured in accordance with
:rfc:`2544`, using FD.io CSIT Multiple Loss Ratio search (MLRsearch), an
optimized binary search algorithm, that measures SUT/DUT throughput at
different Packet Loss Ratio (PLR) values.

Following MLRsearch values are measured across a range of L2 frame sizes
and reported:

- **Non Drop Rate (NDR)**: packet and bandwidth throughput at PLR=0%.

  - **Aggregate packet rate**: NDR_LOWER <bi-directional packet rate>
    pps.
  - **Aggregate bandwidth rate**: NDR_LOWER <bi-directional bandwidth
    rate> Gbps.

- **Partial Drop Rate (PDR)**: packet and bandwidth throughput at
  PLR=0.5%.

  - **Aggregate packet rate**: PDR_LOWER <bi-directional packet rate>
    pps.
  - **Aggregate bandwidth rate**: PDR_LOWER <bi-directional bandwidth
    rate> Gbps.

NDR and PDR are measured for the following L2 frame sizes (untagged
Ethernet):

- IPv4 payload: 64B, IMIX_v4_1 (28x64B, 16x570B, 4x1518B), 1518B, 9000B.
- IPv6 payload: 78B, 1518B, 9000B.

All rates are reported from external Traffic Generator perspective.

.. _mlrsearch_algorithm:

MLRsearch Algorithm
-------------------

Multiple Loss Rate search (MLRsearch) is a new search algorithm
implemented in FD.io CSIT project. MLRsearch discovers multiple packet
throughput rates in a single search, with each rate associated with a
distinct Packet Loss Ratio (PLR) criteria.

Two throughput measurements used in FD.io CSIT are Non-Drop Rate (NDR,
with zero packet loss, PLR=0) and Partial Drop Rate (PDR, with packet
loss rate not greater than the configured non-zero PLR). MLRsearch
discovers NDR and PDR in a single pass reducing required execution time
compared to separate binary searches for NDR and PDR. MLRsearch reduces
execution time even further by relying on shorter trial durations
of intermediate steps, with only the final measurements
conducted at the specified final trial duration.
This results in the shorter overall search
execution time when compared to a standard NDR/PDR binary search,
while guaranteeing the same or similar results.

If needed, MLRsearch can be easily adopted to discover more throughput rates
with different pre-defined PLRs.

.. Note:: All throughput rates are *always* bi-directional
   aggregates of two equal (symmetric) uni-directional packet rates
   received and reported by an external traffic generator.

Overview
~~~~~~~~

The main properties of MLRsearch:

- MLRsearch is a duration aware multi-phase multi-rate search algorithm.

  - Initial phase determines promising starting interval for the search.
  - Intermediate phases progress towards defined final search criteria.
  - Final phase executes measurements according to the final search
    criteria.

- *Initial phase*:

  - Uses link rate as a starting transmit rate and discovers the Maximum
    Receive Rate (MRR) used as an input to the first intermediate phase.

- *Intermediate phases*:

  - Start with initial trial duration (in the first phase) and converge
    geometrically towards the final trial duration (in the final phase).
  - Track two values for NDR and two for PDR.

    - The values are called (NDR or PDR) lower_bound and upper_bound.
    - Each value comes from a specific trial measurement
      (most recent for that transmit rate),
      and as such the value is associated with that measurement's duration and loss.
    - A bound can be invalid, for example if NDR lower_bound
      has been measured with nonzero loss.
    - Invalid bounds are not real boundaries for the searched value,
      but are needed to track interval widths.
    - Valid bounds are real boundaries for the searched value.
    - Each non-initial phase ends with all bounds valid.

  - Start with a large (lower_bound, upper_bound) interval width and
    geometrically converge towards the width goal (measurement resolution)
    of the phase. Each phase halves the previous width goal.
  - Use internal and external searches:

    - External search - measures at transmit rates outside the (lower_bound,
      upper_bound) interval. Activated when a bound is invalid,
      to search for a new valid bound by doubling the interval width.
      It is a variant of `exponential search`_.
    - Internal search - `binary search`_, measures at transmit rates within the
      (lower_bound, upper_bound) valid interval, halving the interval width.

- *Final phase* is executed with the final test trial duration, and the final
  width goal that determines resolution of the overall search.
  Intermediate phases together with the final phase are called non-initial phases.

The main benefits of MLRsearch vs. binary search include:

- In general MLRsearch is likely to execute more search trials overall, but
  less trials at a set final duration.
- In well behaving cases it greatly reduces (>50%) the overall duration
  compared to a single PDR (or NDR) binary search duration,
  while finding multiple drop rates.
- In all cases MLRsearch yields the same or similar results to binary search.
- Note: both binary search and MLRsearch are susceptible to reporting
  non-repeatable results across multiple runs for very bad behaving
  cases.

Caveats:

- Worst case MLRsearch can take longer than a binary search e.g. in case of
  drastic changes in behaviour for trials at varying durations.

Search Implementation
~~~~~~~~~~~~~~~~~~~~~

Following is a brief description of the current MLRsearch
implementation in FD.io CSIT.

Input Parameters
````````````````

#. *maximum_transmit_rate* - maximum packet transmit rate to be used by
   external traffic generator, limited by either the actual Ethernet
   link rate or traffic generator NIC model capabilities. Sample
   defaults: 2 * 14.88 Mpps for 64B 10GE link rate,
   2 * 18.75 Mpps for 64B 40GE NIC maximum rate.
#. *minimum_transmit_rate* - minimum packet transmit rate to be used for
   measurements. MLRsearch fails if lower transmit rate needs to be
   used to meet search criteria. Default: 2 * 10 kpps (could be higher).
#. *final_trial_duration* - required trial duration for final rate
   measurements. Default: 30 sec.
#. *initial_trial_duration* - trial duration for initial MLRsearch phase.
   Default: 1 sec.
#. *final_relative_width* - required measurement resolution expressed as
   (lower_bound, upper_bound) interval width relative to upper_bound.
   Default: 0.5%.
#. *packet_loss_ratio* - maximum acceptable PLR search criteria for
   PDR measurements. Default: 0.5%.
#. *number_of_intermediate_phases* - number of phases between the initial
   phase and the final phase. Impacts the overall MLRsearch duration.
   Less phases are required for well behaving cases, more phases
   may be needed to reduce the overall search duration for worse behaving cases.
   Default (2). (Value chosen based on limited experimentation to date.
   More experimentation needed to arrive to clearer guidelines.)

Initial phase
`````````````

1. First trial measures at maximum rate and discovers MRR.

   a. *in*: trial_duration = initial_trial_duration.
   b. *in*: offered_transmit_rate = maximum_transmit_rate.
   c. *do*: single trial.
   d. *out*: measured loss ratio.
   e. *out*: mrr = measured receive rate.

2. Second trial measures at MRR and discovers MRR2.

   a. *in*: trial_duration = initial_trial_duration.
   b. *in*: offered_transmit_rate = MRR.
   c. *do*: single trial.
   d. *out*: measured loss ratio.
   e. *out*: mrr2 = measured receive rate.

3. Third trial measures at MRR2.

   a. *in*: trial_duration = initial_trial_duration.
   b. *in*: offered_transmit_rate = MRR2.
   c. *do*: single trial.
   d. *out*: measured loss ratio.

Non-initial phases
``````````````````

1. Main loop:

   a. *in*: trial_duration for the current phase.
      Set to initial_trial_duration for the first intermediate phase;
      to final_trial_duration for the final phase;
      or to the element of interpolating geometric sequence
      for other intermediate phases.
      For example with two intermediate phases, trial_duration
      of the second intermediate phase is the geometric average
      of initial_strial_duration and final_trial_duration.
   b. *in*: relative_width_goal for the current phase.
      Set to final_relative_width for the final phase;
      doubled for each preceding phase.
      For example with two intermediate phases,
      the first intermediate phase uses quadruple of final_relative_width
      and the second intermediate phase uses double of final_relative_width.
   c. *in*: ndr_interval, pdr_interval from the previous main loop iteration
      or the previous phase.
      If the previous phase is the initial phase, both intervals have
      lower_bound = MRR2, uper_bound = MRR.
      Note that the initial phase is likely to create intervals with invalid bounds.
   d. *do*: According to the procedure described in point 2,
      either exit the phase (by jumping to 1.g.),
      or prepare new transmit rate to measure with.
   e. *do*: Perform the trial measurement at the new transmit rate
      and trial_duration, compute its loss ratio.
   f. *do*: Update the bounds of both intervals, based on the new measurement.
      The actual update rules are numerous, as NDR external search
      can affect PDR interval and vice versa, but the result
      agrees with rules of both internal and external search.
      For example, any new measurement below an invalid lower_bound
      becomes the new lower_bound, while the old measurement
      (previously acting as the invalid lower_bound)
      becomes a new and valid upper_bound.
      Go to next iteration (1.c.), taking the updated intervals as new input.
   g. *out*: current ndr_interval and pdr_interval.
      In the final phase this is also considered
      to be the result of the whole search.
      For other phases, the next phase loop is started
      with the current results as an input.

2. New transmit rate (or exit) calculation (for 1.d.):

   - If there is an invalid bound then prepare for external search:

     - *If* the most recent measurement at NDR lower_bound transmit rate
       had the loss higher than zero, then
       the new transmit rate is NDR lower_bound
       decreased by two NDR interval widths.
     - Else, *if* the most recent measurement at PDR lower_bound
       transmit rate had the loss higher than PLR, then
       the new transmit rate is PDR lower_bound
       decreased by two PDR interval widths.
     - Else, *if* the most recent measurement at NDR upper_bound
       transmit rate had no loss, then
       the new transmit rate is NDR upper_bound
       increased by two NDR interval widths.
     - Else, *if* the most recent measurement at PDR upper_bound
       transmit rate had the loss lower or equal to PLR, then
       the new transmit rate is PDR upper_bound
       increased by two PDR interval widths.
   - If interval width is higher than the current phase goal:

     - Else, *if* NDR interval does not meet the current phase width goal,
       prepare for internal search. The new transmit rate is
       (NDR lower bound + NDR upper bound) / 2.
     - Else, *if* PDR interval does not meet the current phase width goal,
       prepare for internal search. The new transmit rate is
       (PDR lower bound + PDR upper bound) / 2.
   - Else, *if* some bound has still only been measured at a lower duration,
     prepare to re-measure at the current duration (and the same transmit rate).
     The order of priorities is:

     - NDR lower_bound,
     - PDR lower_bound,
     - NDR upper_bound,
     - PDR upper_bound.
   - *Else*, do not prepare any new rate, to exit the phase.
     This ensures that at the end of each non-initial phase
     all intervals are valid, narrow enough, and measured
     at current phase trial duration.

Implementation Deviations
~~~~~~~~~~~~~~~~~~~~~~~~~

This document so far has been describing a simplified version of MLRsearch algorithm.
The full algorithm as implemented contains additional logic,
which makes some of the details (but not general ideas) above incorrect.
Here is a short description of the additional logic as a list of principles,
explaining their main differences from (or additions to) the simplified description,
but without detailing their mutual interaction.

1. *Logarithmic transmit rate.*
   In order to better fit the relative width goal,
   the interval doubling and halving is done differently.
   For example, the middle of 2 and 8 is 4, not 5.
2. *Optimistic maximum rate.*
   The increased rate is never higher than the maximum rate.
   Upper bound at that rate is always considered valid.
3. *Pessimistic minimum rate.*
   The decreased rate is never lower than the minimum rate.
   If a lower bound at that rate is invalid,
   a phase stops refining the interval further (until it gets re-measured).
4. *Conservative interval updates.*
   Measurements above current upper bound never update a valid upper bound,
   even if drop ratio is low.
   Measurements below current lower bound always update any lower bound
   if drop ratio is high.
5. *Ensure sufficient interval width.*
   Narrow intervals make external search take more time to find a valid bound.
   If the new transmit increased or decreased rate would result in width
   less than the current goal, increase/decrease more.
   This can happen if the measurement for the other interval
   makes the current interval too narrow.
   Similarly, take care the measurements in the initial phase
   create wide enough interval.
6. *Timeout for bad cases.*
   The worst case for MLRsearch is when each phase converges to intervals
   way different than the results of the previous phase.
   Rather than suffer total search time several times larger
   than pure binary search, the implemented tests fail themselves
   when the search takes too long (given by argument *timeout*).

Maximum Receive Rate MRR
------------------------

MRR tests measure the packet forwarding rate under the maximum
load offered by traffic generator over a set trial duration,
regardless of packet loss. Maximum load for specified Ethernet frame
size is set to the bi-directional link rate.

Current parameters for MRR tests:

- Ethernet frame sizes: 64B (78B for IPv6), IMIX, 1518B, 9000B; all
  quoted sizes include frame CRC, but exclude per frame transmission
  overhead of 20B (preamble, inter frame gap).

- Maximum load offered: 10GE and 40GE link (sub-)rates depending on NIC
  tested, with the actual packet rate depending on frame size,
  transmission overhead and traffic generator NIC forwarding capacity.

  - For 10GE NICs the maximum packet rate load is 2* 14.88 Mpps for 64B,
    a 10GE bi-directional link rate.
  - For 25GE NICs the maximum packet rate load is 2* 18.75 Mpps for 64B,
    a 25GE bi-directional link sub-rate limited by TG 25GE NIC used,
    XXV710.
  - For 40GE NICs the maximum packet rate load is 2* 18.75 Mpps for 64B,
    a 40GE bi-directional link sub-rate limited by TG 40GE NIC used,
    XL710. Packet rate for other tested frame sizes is limited by PCIe
    Gen3 x8 bandwidth limitation of ~50Gbps.

- Trial duration: 10sec.

Similarly to NDR/PDR throughput tests, MRR test should be reporting bi-
directional link rate (or NIC rate, if lower) if tested VPP
configuration can handle the packet rate higher than bi-directional link
rate, e.g. large packet tests and/or multi-core tests.

MRR tests are used for continuous performance trending and for
comparison between releases. Daily trending job tests subset of frame
sizes, focusing on 64B (78B for IPv6) for all tests and IMIX for
selected tests (vhost, memif).

Packet Latency
--------------

TRex Traffic Generator (TG) is used for measuring latency of VPP DUTs.
Reported latency values are measured using following methodology:

- Latency tests are performed at 100% of discovered NDR and PDR rates
  for each throughput test and packet size (except IMIX).
- TG sends dedicated latency streams, one per direction, each at the
  rate of 9 kpps at the prescribed packet size; these are sent in
  addition to the main load streams.
- TG reports min/avg/max latency values per stream direction, hence two
  sets of latency values are reported per test case; future release of
  TRex is expected to report latency percentiles.
- Reported latency values are aggregate across two SUTs due to three
  node topology used for all performance tests; for per SUT latency,
  reported value should be divided by two.
- 1usec is the measurement accuracy advertised by TRex TG for the setup
  used in FD.io labs used by CSIT project.
- TRex setup introduces an always-on error of about 2*2usec per latency
  flow additonal Tx/Rx interface latency induced by TRex SW writing and
  reading packet timestamps on CPU cores without HW acceleration on NICs
  closer to the interface line.

Multi-Core Speedup
------------------

All performance tests are executed with single processor core and with
multiple cores scenarios.

Intel Hyper-Threading (HT)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Intel Xeon processors used in FD.io CSIT can operate either in HT
Disabled mode (single logical core per each physical core) or in HT
Enabled mode (two logical cores per each physical core). HT setting is
applied in BIOS and requires server SUT reload for it to take effect,
making it impractical for continuous changes of HT mode of operation.

|csit-release| performance tests are executed with server SUTs' Intel
XEON processors configured with Intel Hyper-Threading Disabled for all
Xeon Haswell testbeds (3n-hsw) and with Intel Hyper-Threading Enabled
for all Xeon Skylake testbeds.

More information about physical testbeds is provided in
:ref:`tested_physical_topologies`.

Multi-core Tests
~~~~~~~~~~~~~~~~

|csit-release| multi-core tests are executed in the following VPP worker
thread and physical core configurations:

#. Intel Xeon Haswell testbeds (3n-hsw) with Intel HT disabled
   (1 logical CPU core per each physical core):

  #. 1t1c - 1 VPP worker thread on 1 physical core.
  #. 2t2c - 2 VPP worker threads on 2 physical cores.
  #. 4t4c - 4 VPP worker threads on 4 physical cores.

#. Intel Xeon Skylake testbeds (2n-skx, 3n-skx) with Intel HT enabled
   (2 logical CPU cores per each physical core):

  #. 2t1c - 2 VPP worker threads on 1 physical core.
  #. 4t2c - 4 VPP worker threads on 2 physical cores.
  #. 8t4c - 8 VPP worker threads on 4 physical cores.

VPP worker threads are the data plane threads running on isolated
logical cores. With Intel HT enabled VPP workers are placed as sibling
threads on each used physical core. VPP control threads (main, stats)
are running on a separate non-isolated core together with other Linux
processes.

In all CSIT tests care is taken to ensure that each VPP worker handles
the same amount of received packet load and does the same amount of
packet processing work. This is achieved by evenly distributing per
interface type (e.g. physical, virtual) receive queues over VPP workers
using default VPP round- robin mapping and by loading these queues with
the same amount of packet flows.

If number of VPP workers is higher than number of physical or virtual
interfaces, multiple receive queues are configured on each interface.
NIC Receive Side Scaling (RSS) for physical interfaces and multi-queue
for virtual interfaces are used for this purpose.

Section :ref:`throughput_speedup_multi_core` includes a set of graphs
illustrating packet throughout speedup when running VPP worker threads
on multiple cores. Note that in quite a few test cases running VPP
workers on 2 or 4 physical cores hits the I/O bandwidth or packets-per-
second limit of tested NIC.

VPP Startup Settings
--------------------

CSIT code manipulates a number of VPP settings in startup.conf for optimized
performance. List of common settings applied to all tests and test
dependent settings follows.

See `VPP startup.conf <https://git.fd.io/vpp/tree/src/vpp/conf/startup.conf?h=stable/1807>`_
for a complete set and description of listed settings.

Common Settings
~~~~~~~~~~~~~~~

List of vpp startup.conf settings applied to all tests:

#. heap-size <value> - set separately for ip4, ip6, stats, main
   depending on scale tested.
#. no-tx-checksum-offload - disables UDP / TCP TX checksum offload in DPDK.
   Typically needed for use faster vector PMDs (together with
   no-multi-seg).
#. socket-mem <value>,<value> - memory per numa. (Not required anymore
   due to VPP code changes, should be removed in CSIT-18.10.)

Per Test Settings
~~~~~~~~~~~~~~~~~

List of vpp startup.conf settings applied dynamically per test:

#. corelist-workers <list_of_cores> - list of logical cores to run VPP
   worker data plane threads. Depends on HyperThreading and core per
   test configuration.
#. num-rx-queues <value> - depends on a number of VPP threads and NIC
   interfaces.
#. num-rx-desc/num-tx-desc - number of rx/tx descriptors for specific
   NICs, incl. xl710, x710, xxv710.
#. num-mbufs <value> - increases number of buffers allocated, needed
   only in scenarios with large number of interfaces and worker threads.
   Value is per CPU socket. Default is 16384.
#. no-multi-seg - disables multi-segment buffers in DPDK, improves
   packet throughput, but disables Jumbo MTU support. Disabled for all
   tests apart from the ones that require Jumbo 9000B frame support.
#. UIO driver - depends on topology file definition.
#. QAT VFs - depends on NRThreads, each thread = 1QAT VFs.

KVM VMs vhost-user
------------------

FD.io CSIT performance lab is testing VPP vhost with KVM VMs using
following environment settings:

- Tests with varying Qemu virtio queue (a.k.a. vring) sizes: [vr256]
  default 256 descriptors, [vr1024] 1024 descriptors to optimize for
  packet throughput.
- Tests with varying Linux :abbr:`CFS (Completely Fair Scheduler)`
  settings: [cfs] default settings, [cfsrr1] CFS RoundRobin(1) policy
  applied to all data plane threads handling test packet path including
  all VPP worker threads and all Qemu testpmd poll-mode threads.
- Resulting test cases are all combinations with [vr256,vr1024] and
  [cfs,cfsrr1] settings.
- Adjusted Linux kernel :abbr:`CFS (Completely Fair Scheduler)`
  scheduler policy for data plane threads used in CSIT is documented in
  `CSIT Performance Environment Tuning wiki <https://wiki.fd.io/view/CSIT/csit-perf-env-tuning-ubuntu1604>`_.
- The purpose is to verify performance impact (MRR and NDR/PDR
  throughput) and same test measurements repeatability, by making VPP
  and VM data plane threads less susceptible to other Linux OS system
  tasks hijacking CPU cores running those data plane threads.

LXC/DRC Container Memif
-----------------------

|csit-release| includes tests taking advantage of VPP memif virtual
interface (shared memory interface) to interconnect VPP running in
Containers. VPP vswitch instance runs in bare-metal user-mode handling
NIC interfaces and connecting over memif (Slave side) to VPPs running in
:abbr:`Linux Container (LXC)` or in Docker Container (DRC) configured
with memif (Master side). LXCs and DRCs run in a priviliged mode with
VPP data plane worker threads pinned to dedicated physical CPU cores per
usual CSIT practice. All VPP instances run the same version of software.
This test topology is equivalent to existing tests with vhost-user and
VMs as described earlier in :ref:`tested_logical_topologies`.

In addition to above vswitch tests, a single memif interface test is
executed. It runs in a simple topology of two VPP container instances
connected over memif interface in order to verify standalone memif
interface performance.

More information about CSIT LXC and DRC setup and control is available
in :ref:`container_orchestration_in_csit`.

K8s Container Memif
-------------------

|csit-release| includes tests of VPP topologies running in K8s
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

IPSec on Intel QAT
------------------

VPP IPSec performance tests are using DPDK cryptodev device driver in
combination with HW cryptodev devices - Intel QAT 8950 50G - present in
LF FD.io physical testbeds. DPDK cryptodev can be used for all IPSec
data plane functions supported by VPP.

Currently |csit-release| implements following IPSec test cases:

- AES-GCM, CBC-SHA1 ciphers, in combination with IPv4 routed-forwarding
  with Intel xl710 NIC.
- CBC-SHA1 ciphers, in combination with LISP-GPE overlay tunneling for
  IPv4-over-IPv4 with Intel xl710 NIC.

TRex Traffic Generator
----------------------

Usage
~~~~~

`TRex traffic generator <https://wiki.fd.io/view/TRex>`_ is used for all
CSIT performance tests. TRex stateless mode is used to measure NDR and
PDR throughputs using binary search (NDR and PDR discovery tests) and
for quick checks of DUT performance against the reference NDRs (NDR
check tests) for specific configuration.

TRex is installed and run on the TG compute node. The typical procedure
is:

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

Measuring Packet Loss
~~~~~~~~~~~~~~~~~~~~~

Following sequence is followed to measure packet loss:

- Create an instance of STLClient.
- Connect to the client.
- Add all streams.
- Clear statistics.
- Send the traffic for defined time.
- Get the statistics.

If there is a warm-up phase required, the traffic is sent also before
test and the statistics are ignored.

Measuring Latency
~~~~~~~~~~~~~~~~~

If measurement of latency is requested, two more packet streams are
created (one for each direction) with TRex flow_stats parameter set to
STLFlowLatencyStats. In that case, returned statistics will also include
min/avg/max latency values.

HTTP/TCP with WRK tool
----------------------

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
    - Resulting flow sequence - 8 packets: >Syn, <Syn-Ack, >Ack, >Req,
      <Rep, >Fin, <Fin, >Ack.

- HTTP Requests-Per-Second

  - WRK configured to use 8 threads across 8 cores, 1 thread per core.
  - Maximum of 50 concurrent connections across all WRK threads.
  - Timeout for server responses set to 5 seconds.
  - Test duration is 30 seconds.
  - Expected HTTP test sequence:

    - Multiple HTTP GET Requests sent in sequence per open connection.
    - Connection close after set test duration time.
    - Resulting flow sequence: >Syn, <Syn-Ack, >Ack, >Req[1], <Rep[1],
      .., >Req[n], <Rep[n], >Fin, <Fin, >Ack.

.. _binary search: https://en.wikipedia.org/wiki/Binary_search
.. _exponential search: https://en.wikipedia.org/wiki/Exponential_search
.. _estimation of standard deviation: https://en.wikipedia.org/wiki/Unbiased_estimation_of_standard_deviation
.. _simplified error propagation formula: https://en.wikipedia.org/wiki/Propagation_of_uncertainty#Simplification
