Experimental: MDR Search
========================

Multiple Drop Rate (MDR) Search is a new search algorithm implemented in
FD.io CSIT project. MDR enables a single search to discover multiple
packet throughput rates each associated with a distinct Packet Loss
Tolerance (PLT) criteria.

Two throughput measurements used in FD.io CSIT are Non-Drop Rate (NDR,
with zero packet loss, PLT=0) and Partial Drop Rate (PDR, with packet
loss rate not greater than the configured non-zero PLT). MDR search
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

The main properties of MDR search:

- MDR is a duration aware multi-phase multi-rate search algorithm.

  - It starts with a quick initial phase to determine optimal search
    starting bounds.
  - Following intermediate phase(s) progress towards defined final
    search criteria.
  - Final phase executes measurements according to the final search
    criteria.

- Initial phase:

  - Uses link rate as a starting transmit rate and discovers the Maximum
    Receive Rate (MRR) used as an input to subsequent phase.

- Intermediate phase(s):

  - Progress towards configured final search criteria i) trial duration,
    ii) interval width and iii) PLT(s).
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

The main benefits of MDR search vs. binary search include:

- In general MDR is likely to execute more search trials overall, but
  less trials at a set final duration.
- In well behaved cases it greatly reduces (>50%) the overall duration
  compared to a single PDR (or NDR) rate binary search duration.
- In all cases MDR yields the same or similar results to binary search.
- Note: both binary search and MDR are susceptible to reporting
  non-repeatable results across multiple runs for very bad behaving
  cases.

Caveats:

- Worst case MDR can take longer than a binary search e.g. in case of
  drastic changes in behaviour for trials at varying durations.

MDR Search Phases
-----------------

Following is a brief description of the current MDR search
implementation in FD.io CSIT .

MDR Parameters
``````````````
1. External inputs

  a) Packet_Loss_Tolerance (PLT) for PDR measurement.
  b) Relative_interval_width for measurement resolution.
  c) Final_trial_duration.

2. Internal inputs

  a) Minimum_trial_duration - starting value for MDR trials.
  b) Fail_rate - a minimum transmit rate to be used. If MDR search
     results in having to use a transmit rate that is lower than fail
     rate, MDR search fails.

Initial phase
`````````````

1. First trial measures MRR.
  a) Offered_transmit_rate = link_rate.
  b) MRR = Measured receive rate.
  c) Trial_duration = minimum_trial_duration.

2. Second trial measures MRR2.
  a) Offered_transmit_rate = MRR.
  b) MRR2 = Measured receive rate.
  c) Trial_duration = minimum_trial_duration.

2. Third trial measures MRR3, if MRR2 is greater than Fail rate
  a) Offered_transmit_rate = MRR2.
  b) MRR3 = Measured receive rate.
  c) Trial_duration = minimum_trial_duration.

Intermediate phase 1
````````````````````

<add text>

Intermediate phase 2
````````````````````

<add text>

Final phase
```````````

<add text>

