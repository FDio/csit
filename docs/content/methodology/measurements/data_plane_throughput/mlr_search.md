---
title: "MLR Search"
weight: 2
---

# MLR Search

## Specification

Detailed description of the MLRsearch specification is included in the IETF draft
[draft-ietf-bmwg-mlrsearch](https://datatracker.ietf.org/doc/html/draft-ietf-bmwg-mlrsearch)
that is in the process of being standardized in the IETF Benchmarking
Methodology Working Group (BMWG).

MLRsearch is also available as a
[PyPI (Python Package Index) library](https://pypi.org/project/MLRsearch/).

## Search Goals

In CSIT we use two search goals, traditionally called NDR (non-drop rate)
and PDR (partial drop rate):

NDR:

* Goal Initial Trial Duration = 1 second

* Goal Final Trial Duration = 1 second

* Goal Duration Sum = 21 seconds

* Goal Loss Ratio = 0.0%

* Goal Exceed Ratio = 50%

* Goal Width = 0.5%

PDR:

* Goal Initial Trial Duration = 1 second

* Goal Final Trial Duration = 1 second

* Goal Duration Sum = 21 seconds

* Goal Loss Ratio = 0.5%

* Goal Exceed Ratio = 50%

* Goal Width = 0.5%

## Test Report Information

The MLRsearch specification requires (or recommends) the test report to contain
specific information, here is the summary.

CSIT uses TRex as the traffic generator, over SSH, bash and Python layers
that add roughly 0.5 second delay between trials.
That is enough to replace all the wait times listed in RFC 2544.

The trial effective duration includes that delay, so as little as 7 trials
is sometimes enough for load classification (instead of 11).

TRex uses multiple worker threads (typically 8) so the traffic
can be bursty on small time scales, but even the small buffers on DUT side
usually make this effect invisible.

All traffic profiles generate ethernet frames that carry IPv4 or IPv6 packets,
in minority of tests also containing VLAN tags (dot1q or dot1ad).
For convenience, the rest of this description uses "packet" where MLRsearch
specification expects "frame".

TRex is usually precise in the number of packets sent,
but in high-performance setups it may show "duration stretching"
where it takes considerably longer than the intended duration
to send all the traffic. To combat this behavior, CSIT applies
"start+sleep+stop" approach, which can cause some number of packets
to remain unsent. We allow 10 microseconds worth of traffic to be missing
to allow for not all TRex workers starting at the same time,
but larger values are included in trial loss ratio.

Most our tests use symmetric bidirectional traffic profiles,
and the results are presented as aggregate values, e.g. east-west plust west-east.
Other specifics of traffic profiles are too numerous to be listed here,
CSIT code is the authoritative documentation.

Max load is computed from known values of per-direction NIC limits.
Usually, large packet traffic is limited by media bandwidth,
and small frame traffic is limited by per-port packets-per-second (pps) limits.
Min load is set to 9.001 kpps to ensure enough packets for latency histogram.

If min load is classified as an upper bound for the NDR goal,
the test fails immediatelly (not searching for PDR).
Also, if the search takes too long, the test fails fithout a result.
If max load is classified as a lower bound, this situation is reported
as zero-width irregular result, otherwise not distinguished
from regular results in the frontend presentation.

Relevant lower bound and relevant upper bound are recorded together with
conditional throughput for both goals, but only the conditional throughput
values are is presented in our WebUI frontend.

TRex uses a lightweight way to count forwarded packets,
so it does not identify duplicate and reordered packets.
Some testbeds contain a link for TRex self-test, the results of such "trex" tests
are measured as separate tests, but they are not influencing real SUT tests.

As different tests require different SUT setups, those are lightly documented
on suite descriptions, but CSIT code is the authoritative documentation.

## Heuristics

MLRsearch specification giver large freedom for implementations.
The CSIT implementation applies many heuristic in order to save search time.
Here is a short summary.

Before the search starts, a discrete set of possible loads is pre-computed
and used to avoid rounding errors.

The very first trial is done at max load, but acts as a warm-up,
its results are ignored. All other 1-second trial results
are used for load classification.

MRR (forwarding rate at max load) and the forwarding rate at MRR load
are used as initial candidate loads at the start of regular search.

The specified search goals are treated as "final targets",
but preceded by "intermediate targets" of smaller duration sum (4.58s and 1s)
and larger goal width (double and quadruple, respectively).
This allows the algorithm to quickly converge
towards the "interesting region" where full duration sum is needed.

Generally, smaller candidate loads are measured first.
For more tricks (e.g. uneven splits and multiple selection strategies)
see the source of the Python implementation.

# Additional details

There will be future documents linked from here.

For now, there is only an outline of future (ambitious) content.
Items in parenthesis are hints on what content will be in the parent subsection.

Outline:

* History of early versions in CSIT

    * MLRsearch as a class of algorithms

        * (Older Python library versions were mutually incompatible,
          both witch each other and with early versions
          of MLRsearch IETF document.)

    * Example tests benefiting from different goals?

* Design principles

    * Independence of components

        * (Programming languages, asynchronous calls via Manager.)

    * Implementation freedom

        * Optional and implementation-required inputs

        * Reasonable default values

        * Better outputs in future

        * "allowed if makes worse" principle

            * (Some requirements ensure fairness when benchmarking is done
              by business competition. They are not needed and just waste time
              if benchmarking is done in "home lab". For example,
              decreasing wait time can only hurt results by turning bigger latency
              into frame loss.)

    * Follow intuition, avoid surprises

    * Usage

        * (anomaly detection in trending,
          comparison tables with low stdev for release)

    * Max load and min load

    * Size of loss

        * (does not matter, only binary low-loss vs high-loss)

    * Goals used

        * (Why 50% exceed ratio is so good.)

    * Simulator

        * (PLRsearch fitting functions, exotic goals)

        * (Example of time savings between RFC2544 and CSIT goal
          at the same accuracy?)

    * Long trials vs many trials

        * (Many trials offer better flexibility and avoid issues with handling
          long-vs-short results fairly.)

        * (Mention reconfiguration tests still use long trial with zero tolerance?)

    * Conservativeness

        * (Some performance bugs manifest as infrequent big loss spikes.)

        * (Is conservativeness still as important when exceed ratio is 50%?)

    * Fail fast

        * (If min load is an upper bound for one goal,
          bail out to save time on broken tests.)

    * Timeout

        * (If SUT behavior suddenly becomes erratic, it could prolong the duration
          of a "job run" that tests many different SUT settings and traffic profiles.
          To control such duration spikes, CSIT test fails if search result
          is not found reasonably fast.)

* Measurer questions

    * Capabilities

        * (Traffic profiles specific to TRex, TG TA and Yang)

    * Self test

    * Warm-up

    * Time overhead

    * Predicting offered count

    * Duration stretching

        * (start+sleep+stop)

    * Burstiness

    * Negative loss

        * (Typically, misconfigured SUT can produce small number of unexpected
          additional packets, for example with IPv6 autonegotiation not disabled.)

        * (Implementations can decide to either allow or treat as artificial losses.)

        * (Rarely, excess of packets may signal wait times between trials
          is too low and SUT buffers too high.)

    * Aggregate limits

        * (RX+TX, sum over ports, number of queues, CPU limits,
          baseline vs burst in cloud)

    * Other Oload issues

        * (duplex and other interferences;
          DUT-DUT links with encapsulation overhead)

* Test report

    * Definition

    * Alternative units

        * Unidirectional vs bidirectional

        * Bandwidth

* Heuristics

    * FRMOL and FRFRMOL

    * Intermediate targets

    * Relative width

    * Discrete loads

    * Expansion coefficient

    * Uneven splits

    * Selector strategies

    * Candidate ordering

* DUT behaviors

    * Periodic interrupts

    * More details on distribution of big and small loss spikes

        * (performance spectrum as a probabilistic distribution
          over trial forwarding rate)

        * (trial results as small population)

        * (median and other quantiles, "touching" quantiles)

    * Exceed probability

        * (load regions, common patterns seen in practice)

    * Large buffers

    * Performance decrease due to resource leaks

    * Energy mode switching can cause loss inversion?

* Correctness

    * Balancing sum from short trials

    * Optimistic and pessimistic estimates

    * Load is eventually classified

    * Gaming is possible but slow

    * Brittle heuristics

    * Goal ordering

    * Discouraged goals

        * Goal Width > Goal Loss Ratio

        * Goal Duration Sum < Goal Final Trial Duration

        * Incomparable goals

            * (worst case: slow race to bottom)

    * When a load can become undecided again?

* Related test procedures

    * Latency

    * Passive Telemetry

    * Active Telemetry

    * Comparison with FRMOL

    * Comparison with PLRsearch

* Beyond frames

    * Transactions

    * Fragmentation

    * Throttled TCP

    * Fixed scale

        * (NAT performance depends on session table size.)

        * (Trials should be long enough to hit all sessions?)

    * Ramp-up

        * (NAT slow-fast path example: Before testing fast path,
      we need a slow enough trial to ensure SUT started tracking all sessions.)

        * (Session counting as verification ramp-up was successful.)

        * (Issues with sessions timing out before real search starts
          or during search. Check is needed for both start and end of trial.)

        * (Heuristics to avoid ramp-ups, e.g. when observing zero loss
          on large enough trial.)

    * Reset

        * (NAT slow-fast path example: When testing slow path, session table
          needs to be explicitly dropped.)

    * Bisecting for telemetry thresholds

    * Bisecting for B2B burst size

* Future improvements

    * Return trials at relevant bounds

    * Allow flipping the conservativeness?

        * (return the larger load when Loss Inversion happens)

    * Short high-loss trials to affect Conditional Throughput?

    * Multiple runs between hard SUT resets

        * (Example: RSS key randomized at start but not between trials.)

    * Duration sum based on misclassification probability

        * (the idea is to decide early on one-sided results
          and late on balanced results)

        * (needs a prior on exceed probability distribution;
          and a posterior condition reflecting the error/time balance)

    * Heavy loss should be worse than narrow loss

        * (larger discussion on similarities with SLA)

    * Predict goodput based on loss and latency?

* Examples?

    * (take a real run and discuss heuristic decisions?)

* Summarize how MLRsearch addressed the Identified Problems
