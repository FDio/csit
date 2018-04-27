Experimental: MDR Search
========================

Multiple Drop Rate (MDR) Search is a new search algorithm implemented in
FD.io CSIT project. MDR enables a single search to discover multiple
packet throughput rates each associated with a distinct Packet Loss
Tolerance (PLT) criteria.

Two throughput measurements used in FD.io CSIT are Non-Drop Rate (NDR,
with zero packet loss, PLT=0) and Partial Drop Rate (PDR, with non-zero
packet loss rate that is below configured non-zero PLT). MDR search
discovers NDR and PDR in a single pass reducing required execution time
compared to separate binary searches for NDR and PDR. MDR further
reduces execution time, by relying on lower trial durations of
intermediate steps, but still conducting final measurement at the
specified final trial duration. This results in shorter overall
execution time compared to standard NDR/PDR binary search, still
guaranteeing the same or similar results.

If needed MDR can be easily adopted to discover more throughput rates
with different pre-defined PLRs.

Overview
---------

Here a list of the key properties of MDR search:

- Multiple phases, each with distinct goals.
- Initial phase uses link rate as a starting transmit rate and discovers
  the Maximum Receive Rate (MRR) used as input to subsequent phases.
- Subsequent phases progress towards configured final search targets
  i) trial duration, ii) interval width and iii) PLT(s).

  - Start with short trial durations and converge towards the
    final trial duration.
  - Start with a large (lower_bound, upper_bound) interval width and
    converge towards the final interval width (usually small), that
    determines measurement resolution.
  - Use internal and external searches:

    - Internal search - binary search with transmit rates within the
      (lower_bound, upper_bound) interval.
    - External search - transmit rates outside the (lower_bound,
      upper_bound) interval. Used in cases when at specific trial
      duration the interval becomes invalid i.e. results are above PLT.

- Final phase is executed with a final test trial duration and
  interval width goal.

The main benefits vs. binary search include:

- In general MDR is likely to execute more search trials overall, but
  less trials at a set final duration.
- In well behaved cases it greatly reduces (>50%) the overall duration
  compared to a single PDR (or NDR) rate binary search duration.
- In all cases MDR yields the same or similar results to binary search.
- Note: both binary search and MDR are susceptible to reporting
  non-repeatable results across multiple runs for very bad behaving
  cases.

Gotchas:

- Worst case MDR can take longer than a binary search e.g. in case of
  drastic changes in behaviour for trials at varying durations.

MDR Search Phases
-----------------

<add text>

Initial phase
`````````````

<add text>

Subsequent phase(s)
```````````````
<add text>

Final phase
```````````
<add text>

Sample Results
--------------

Results and efficiency comparison between the new MDR search and NDR/PDR
binary searches currently implemented in FD.io CSIT.

<add text>
<add table with MDR results and comparison to NDR/PDR (values found,
final trial duration, total search duration>