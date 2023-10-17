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
Thus, instead of final trial duration, a duration sum (20s) is prescribed.
This allows the algorithm to make a decision sooner,
when the results are quite one-sided.
Also, only one half of the trial results is required to meet
the loss ratio requirement, making the conditional throughput more stable.
The conditional throughput in this case is the forwarding rate
averaged over all good trials at relevant lower bound intended load.

MLRsearch discovers all the loads in a single pass, reducing required time
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

All previously measured trials (except the very first one which can act
as a warm-up) are taken into consideration.

For every loss ratio goal, the relevant upper and lower bound
(intended loads, among loads of large enough duration sum) form an interval.
Exit condition is given by that interval reaching low enough relative width.
Small enough width is achieved by bisecting the current interval.
The bisection can be uneven, to save measurements based on information theory.

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
are likely higher than RFC 2544 throughput (especiall for less stable tests).

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

[^1]: [binary search](https://en.wikipedia.org/wiki/Binary_search)
[^2]: [exponential search](https://en.wikipedia.org/wiki/Exponential_search)
