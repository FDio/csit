---
title: "MLR Search"
weight: 2
---

# MLR Search

## Overview

Multiple Loss Ratio search (MLRsearch) tests use an optimized search algorithm
implemented in FD.io CSIT project. MLRsearch discovers conditional throughput
corresponding to any number of loss ratio goals, within a single search.

Two loss ratio goals are of interest in FD.io CSIT, leading to Non-Drop Rate
(NDR, loss ratio goal is exact zero) and Partial Drop Rate
(PDR, 0.5% loss ratio goal).
Instead of a single long trial, a sequence of short (1s) trials is done.
Thus, instead of final trial duration, a duration sum (21s) is prescribed.
This allows the algorithm to make a decision sooner,
when the results are quite one-sided.
Also, only one half of the trial results is required to meet
the loss ratio requirement, making the conditional throughput more stable.
The conditional throughput in this case is in principle the median forwarding rate
among all trials at the relevant lower bound intended load.
In practice, the search stops when missing trial results cannot
disprove the load as a lower bound, so conditional throughput
is the worst forwarding rate among the measured good trials.

MLRsearch discovers all the loads in single search, reducing required time
duration compared to separate `binary search`es[^1] for each rate. Overall
search time is reduced even further by relying on shorter trial
duration sums for intermediate targets, with only measurements for
final targets require the full duration sum. This results in the
shorter overall execution time when compared to standard NDR/PDR binary
search, while guaranteeing similar results.

    Note: The conditional throughput is *always* reported by Robot code
    as a bi-directional aggregate of two (usually symmetric)
    uni-directional packet rates received and reported by an
    external traffic generator (TRex), unless the test specifically requires
    unidirectional traffic. The underlying Python library uses
    unidirectional values instead, as min and max load are given for those.

## Search Implementation

Detailed description of the MLRsearch algorithm is included in the IETF
draft
[draft-ietf-bmwg-mlrsearch](https://datatracker.ietf.org/doc/html/draft-ietf-bmwg-mlrsearch)
that is in the process of being standardized in the IETF Benchmarking
Methodology Working Group (BMWG).

MLRsearch is also available as a
[PyPI (Python Package Index) library](https://pypi.org/project/MLRsearch/).

## Algorithm highlights

MRR and receive rate at MRR load are used as initial guesses for the search.

All previously measured trials (except the very first one which acts
as a warm-up) are taken into consideration.

For every loss ratio goal, the relevant upper and lower bound
(intended loads, among loads of large enough duration sum) form an interval.
Exit condition is given by that interval reaching low enough relative width.
Small enough width is achieved by bisecting the current interval.
The bisection can be uneven, to save measurements based on information theory.
The width value is 0.5%, the same as PDR goal loss ratio,
as smaller values may report PDR conditional throughput smaller than NDR.

Switching to higher trial duration sum generally requires additional trials
at a load from previous duration sum target.
When this refinement does not confirm previous bound classification
(e.g. a lower bound for preceding target
becomes an upper bound of the new target due to new trail results),
external search is used to find close enough bound of the lost type.
External search is a generalization of the first stage of
`exponential search`[^2].

A preceding target uses double of the next width goal,
because one bisection is always safe before risking external search.

As different search targets are interested at different loads,
lower intended load are measured first,
as that approach saves more time when trial results are not very consistent.
Other heuristics are there, aimed to prevent unneccessarily narrow intervals,
and to handle corner cases around min and max load.

## Deviations from RFC 2544

RFC 2544 implies long final trial duration (just one long trial is needed
for classification to lower or uper bound, so exceed ratio does not matter).
With 1s trials and 0.5 exceed ratio, NDR values reported by CSIT
are likely higher than RFC 2544 throughput (especially for less stable tests).

CSIT does not have any explicit wait times before and after trial traffic.
(But the TRex-based measurer takes almost half a second between targets.)

Small difference between intended load and offered load is tolerated,
mainly due to various time overheads preventing precise measurement
of the traffic duration (and TRex can sometimes suffer from duration
stretching). Large difference is reported as unsent packets
(measurement is forcibly stopped after given time), counted as
a packet loss, so search focuses on loads actually achievable by TRex.

In some tests, negative loss count is observed (TRex sees more packets
coming back to it than TRex sent this trial). CSIT code treats that
as a packet loss (as if VPP duplicated the packets),
but TRex does not check other packets for duplication
(as many traffic profiles generate non-unique packets).

<!--
TODO: Are all requirements addressed in "Deviations from RFC 2544"?

Compliant in principle, but:
trial wait times, trial time overhead to effdur, start+sleep+stop,
10us buffer, TRex is bursty in principle but not in practice,
test report shows aggregate values, traffic profile details are in code only,
fails on timeout or irregular NDR, 21s dursum, intermediate phases increase dursum,
min load 9kbps per direction for latency, max load by nic known pps and bps limits,
hitting that max load is treated as regular result of zero width,
only conditional throughputs are processed (at least PDR is "less discrete"),
relevant bounds are also stored, duplicate and reordered packets are not detected,
self-test is done for repeatability reasons (not for max load reasons),
SUT config is in code (only partly in suite documentation).
-->

## Details beyond specification

### History of early versions in CSIT?

#### MLRsearch as a class of algorithms

(mutually incompatible)

#### Example tests benefiting from different goals?

### Design principles

#### Independence of components

#### Implementation freedom

##### Optional and implementation-required inputs

##### Reasonable default values

##### Better outputs in future

##### "allowed if makes worse" principle

#### Follow intuition, avoid surprises

#### Usage

(anomaly detection in trending, comparison tables with low stdev for release)

#### Max load and min load

#### Size of loss

(does not matter, only binary low-loss vs high-loss)

#### Goals used

#### Simulator

(PLRsearch fitting functions, exotic goals)

(Example of time savings between RFC2544 and CSIT goal at the same accuracy?)

#### Long trials vs many trials

#### Conservativeness

#### Fail fast

#### Timeout

### Measurer questions

#### Capabilities

(Traffic profiles specific to TRex, TG TA and Yang)

#### Self test

#### Warm-up

#### Time overhead

#### Predicting offered count

#### Duration stretching

(start+sleep+stop)

#### Burstiness

#### Negative loss

#### Aggregate limits

(RX+TX, sum over ports, number of queues, CPU limits, baseline vs burst in cloud)

#### Other Oload issues

(duplex and other interferences; DUT-DUT links with encapsulation overhead)

### Test report

#### Definition

#### Alternative units

##### Unidirectional vs bidirectional

##### Bandwidth

### Heuristics

#### FRMOL and FRFRMOL

#### Intermediate phases

#### Relative width

#### Discrete loads

#### Expansion coefficient

#### Uneven splits

#### Selector strategies

#### Candidate ordering

### DUT behaviors

#### Periodic interrupts

#### More details on distribution of big and small loss spikes

(performance spectrum as a probabilistic distribution over trial forwarding rate)
(trial results as small population)
(median and other quantiles, "touching" quantiles)

#### Exceed probability

(load regions, common patterns seen in practice)

#### Large buffers

#### Performance decrease due to resource leaks

#### Energy mode switching can cause loss inversion?

### Correctness

#### Balancing sum from short trials

#### Optimistic and pessimistic estimates

#### Load is eventually classified

#### Gaming is possible but slow

#### Brittle heuristics

#### Goal ordering

#### Discouraged goals

##### Goal Width > Goal Loss Ratio

##### Goal Duration Sum value lower than Goal Final Trial Duration

##### Incomparable goals

(worst case: slow race to bottom)

#### When a load can become undecided again?

### Related test procedures

#### Latency

#### Passive Telemetry

#### Active Telemetry

#### Comparison with FRMOL

#### Comparison with PLRsearch

### Beyond frames

#### Transactions

#### Fragmentation

#### Throttled TCP

#### Ramp-up

#### Fixed scale

#### Reset

#### Bisecting for telemetry thresholds

#### Bisecting for B2B burst size

### Future improvements

#### Return trials at relevant bounds

#### Allow flipping the conservativeness?

(return the larger load when Loss Inversion happens)

#### Short high-loss trials to affect Conditional Throughput?

#### Multiple runs between hard SUT resets

#### Duration sum based on misclassification probability

(needs a prior on exceed probability distribution; and error/time balance)

#### Heavy loss should be worse than narrow loss

#### Predict goodput based on loss and latency

### Examples?

(take a real run and discuss heuristic decisions?)

### Summarize how MLRsearch addressed the Identified Problems?

[^1]: [binary search](https://en.wikipedia.org/wiki/Binary_search)
[^2]: [exponential search](https://en.wikipedia.org/wiki/Exponential_search)
