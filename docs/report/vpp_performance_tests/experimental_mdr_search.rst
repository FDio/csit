Experimental: MDR Search
========================

Multiple Drop Rate (MDR) Search is a new search algorithm implemented in
FD.io CSIT project. MDR is a single search for discovering multiple
packet (and bandwidth) throughput rates compliant with different set
Packet Loss Rate (PLR) criteria.

Two throughput measurements used in FD.io CSIT are Non-Drop Rate (NDR,
with zero packet loss) and Partial Drop Rate (PDR, with packet loss
below a pre-defined PLR). MDR search discovers NDR and PDR in a single
pass reducing required execution time compared to separate binary
searches for NDR and PDR. MDR further reduces execution time, by relying
on lower trial durations of intermediate steps, but still conducting
final measurement at the specified final trial duration. This results in
shorter overall execution time compared to standard NDR/PDR binary
search, still guaranteeing the same or similar results.

If needed MDR can be easily adopted to discover more throughput rates
with different pre-defined PLRs.

Overview
---------

Here a list of the key properties of MDR search:

- Mulitple phases, current implementation has 3 phases.
- Initial phase uses link rate as a starting transmit rate, discovering
  Maximum Receive Rate (MRR).
- Sub-sequent phases consist of external and internal searches:

  - External search - uses transmit rates outside the interval(
    lower_bound,upper_bound), when interval is invalid i.e. when search
    criteria like PLR or measurement resolution are violated.
  - Internal search - binary search with transmit rates within the
    interval(lower_bound,upper_bound).

- Phases start with short test trial durations and converge towards the
  set final duration.
- Phases start with a large width interval(lower_bound,upper_bound) and
  converge towards the set (usually small) width goal that determines
  measurement resolution.
- Final phase is executed with a set final test trial duration.

The main benefits vs. binary search include:

- In general MDR makes less trials at a set final duration, but may make
  more trials overall at lower trial duration.
- In well behaved cases it greatly reduces (>>50%) the overall duration
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

Middle phase(s)
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