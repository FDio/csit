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
some information, here is the summary.

CSIT uses TRex as the traffic generator, over SSH, bash and Python layers
that add roughly 0.5 second delay between trials.
That is enough to replace all the wait times listed in RFC 2544.

The trial effective duration includes that delay, so as little as 7 trials
is sometimes enough for load classification (instead of 11).

TRex uses multiple worker threads (typically 8) so the traffic
can be bursty on small time scales, but even the small buffers on DUT side
usually make this effect invisible.

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

Max load is computed from known values of per-direction NIC limits,
usually large packets are limited by media bandwidth and small frames
are limited by intrinsid packets-per-second (pps) limits.
Min load is set to 9.001 kpps to ensure enough packets for latency histogram.

If min load is classified as an upper bound for the NDR goal,
the test fails immediatelly (not searching for PDR).
Also, if the search takes too long, the test fails firhout a result.
If max load is classified as a lower bound, this situation is reported
as zero-width irregular result, usually not distinguished from regular results.

Relevant lower bound and relevant upper bound are recorded together with
conditional throughput for both goals, but only the conditional throughput
is presented in our WebUI frontend.

TRex uses lightweight way to count forwarded packets,
so it does not identify duplicate and reordered packets.
Some testbeds contain a link for TRex self-test, the results of such "trex" tests
are measured as separate tests, but they are not influencing real SUT tests.

As different test require different SUT setups, those are lightly documented
on suite descriptions, but CSIT code is the authoritative documentation.

<!--
TODO: Are all requirements addressed in "Deviations from RFC 2544"?

Compliant in principle, but:
+ trial wait times
+ trial time overhead to effdur
+ start+sleep+stop
+ 10us buffer
+ TRex is bursty in principle but not in practice
+ test report shows aggregate values
+ traffic profile details are in code only
+ fails on timeout or irregular NDR
- intermediate phases increase dursum
+ min load 9kbps per direction for latency
+ max load by nic known pps and bps limits
+ hitting that max load is treated as regular result of zero width
+ only conditional throughputs are processed
- (at least PDR is "less discrete")
+ relevant bounds are also stored
+ duplicate and reordered packets are not detected
+ self-test is done for repeatability reasons
- (not for max load reasons)
+ SUT config is in code
+ (only partly in suite documentation)

TODO: Update the above when the below progresses.
-->

## Heuristics

MRR and receive rate at MRR load are used as initial guesses for the search.

All previously measured trials (except the very first one which acts
as a warm-up) are taken into consideration.

At the start of the search, a discrete set of possible loads is pre-computed
and used to avoid rounding errors.

The specified search goals are treated as "final targets",
but receded by "intermediate targets" of smaller duration sum
and larger goal width. This allows the algorithm to quickly converge
towards the "interesting region" where full duration sum is needed.

Generally, smaller candidate loads are measured first.
For more tricks (uneven splits and multiple selection strategies)
see the source of the Python implementation.

# Additional details

There will be future documents linked from here.
For now, there is only an outline of future (ambitious) content.

## History of early versions in CSIT?

### MLRsearch as a class of algorithms

(mutually incompatible)

### Example tests benefiting from different goals?

## Design principles

### Independence of components

### Implementation freedom

#### Optional and implementation-required inputs

#### Reasonable default values

#### Better outputs in future

#### "allowed if makes worse" principle

### Follow intuition, avoid surprises

### Usage

(anomaly detection in trending, comparison tables with low stdev for release)

### Max load and min load

### Size of loss

(does not matter, only binary low-loss vs high-loss)

### Goals used

### Simulator

(PLRsearch fitting functions, exotic goals)

(Example of time savings between RFC2544 and CSIT goal at the same accuracy?)

### Long trials vs many trials

### Conservativeness

### Fail fast

### Timeout

## Measurer questions

### Capabilities

(Traffic profiles specific to TRex, TG TA and Yang)

### Self test

### Warm-up

### Time overhead

### Predicting offered count

### Duration stretching

(start+sleep+stop)

### Burstiness

### Negative loss

### Aggregate limits

(RX+TX, sum over ports, number of queues, CPU limits, baseline vs burst in cloud)

### Other Oload issues

(duplex and other interferences; DUT-DUT links with encapsulation overhead)

## Test report

### Definition

### Alternative units

#### Unidirectional vs bidirectional

#### Bandwidth

## Heuristics

### FRMOL and FRFRMOL

### Intermediate phases

### Relative width

### Discrete loads

### Expansion coefficient

### Uneven splits

### Selector strategies

### Candidate ordering

## DUT behaviors

### Periodic interrupts

### More details on distribution of big and small loss spikes

(performance spectrum as a probabilistic distribution over trial forwarding rate)

(trial results as small population)

(median and other quantiles, "touching" quantiles)

### Exceed probability

(load regions, common patterns seen in practice)

### Large buffers

### Performance decrease due to resource leaks

### Energy mode switching can cause loss inversion?

## Correctness

### Balancing sum from short trials

### Optimistic and pessimistic estimates

### Load is eventually classified

### Gaming is possible but slow

### Brittle heuristics

### Goal ordering

### Discouraged goals

#### Goal Width > Goal Loss Ratio

#### Goal Duration Sum value lower than Goal Final Trial Duration

#### Incomparable goals

(worst case: slow race to bottom)

### When a load can become undecided again?

## Related test procedures

### Latency

### Passive Telemetry

### Active Telemetry

### Comparison with FRMOL

### Comparison with PLRsearch

## Beyond frames

### Transactions

### Fragmentation

### Throttled TCP

### Ramp-up

### Fixed scale

### Reset

### Bisecting for telemetry thresholds

### Bisecting for B2B burst size

## Future improvements

### Return trials at relevant bounds

### Allow flipping the conservativeness?

(return the larger load when Loss Inversion happens)

### Short high-loss trials to affect Conditional Throughput?

### Multiple runs between hard SUT resets

### Duration sum based on misclassification probability

(needs a prior on exceed probability distribution; and error/time balance)

### Heavy loss should be worse than narrow loss

### Predict goodput based on loss and latency

## Examples?

(take a real run and discuss heuristic decisions?)

## Summarize how MLRsearch addressed the Identified Problems?
