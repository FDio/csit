Experimental: MDR Search
========================

Multiple Drop Rate (MDR) Search is a new search algorithm implemented in
FD.io CSIT project. MDR discovers multiple packet throughput rates in a
single search, with each rate associated with a distinct Packet Loss
Ratio (PLR) criteria.

Two throughput measurements used in FD.io CSIT are Non-Drop Rate (NDR,
with zero packet loss, PLR=0) and Partial Drop Rate (PDR, with packet
loss rate not greater than the configured non-zero PLR). MDR search
discovers NDR and PDR in a single pass reducing required execution time
compared to separate binary searches for NDR and PDR. MDR further
reduces execution time, by relying on shorter trial durations of
intermediate steps, but conducting final measurement at the specified
final trial duration. This results in shorter overall execution time
compared to standard NDR/PDR binary search and guaranteeing the same or
similar results.

If needed MDR can be easily adopted to discover more throughput rates
with different pre-defined PLRs.

.. Note:: Measured throughput rates are *always* bi-directional
   aggregates of two equal (symmetric) uni-directional packet rates
   received and reported by an external traffic generator.

Overview
---------

The main properties of MDR search:

- MDR is a duration aware multi-phase multi-rate search algorithm.

  - It starts with a short initial phase to determine promising starting
    bounds for the search.
  - Subsequent intermediate phase(s) progress towards defined final
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
- In well behaving cases it greatly reduces (>50%) the overall duration
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

MDR Input Parameters
````````````````````

#. *maximum_transmit_rate* - maximum packet transmit rate to be used by
   external traffic generator, limited by either the actual Ethernet
   link rate or traffic generator NIC model capabilities. Sample
   defaults: 2 * 14.88 Mpps 64B 10GE link rate, 2 * 18.75 Mpps 64B 40GE
   NIC maximum rate.
#. *minimum_transmit_rate* - minimum packet transmit rate to be used for
   measurements. MDR search fails if lower transmit rate needs to be
   used to meet search criteria. Default: (?).
#. *final_trial_duration* - required trial duration for final rate
   measurements. Default: 30 sec.
#. *initial_trial_duration* - trial duration for initial MDR phase.
   Default: 1 sec.
#. *final_relative_width* - required measurement resolution expressed as
   (lower_bound, upper_bound) interval width relative to upper_bound.
   Default: 0.5%.
#. *packet_loss_ratio* - maximum acceptable PLR search criteria for
   PDR measurements. Default: 0.5%.
#. *number_of_intermediate_phases* - number of phases between initial
   phase and final phase. Less phases required for well behaving cases,
   more phases required for worse behaving cases. Impacts the overall
   MDR search duration. (editor: can we really make recommendations in
   terms of number of intermediate phases to be used to achieve shorter
   overall MDR search duration times?). Default 2.

Initial phase
`````````````

1. First trial measures MRR.

   a) in: offered_transmit_rate = maximum_transmit_rate.
   b) in: trial_duration = minimum_trial_duration.
   c) do: single trial.
   d) out: mrr = measured receive rate.

2. Second trial measures MRR2.

   a) in: offered_transmit_rate = mrr.
   b) in: trial_duration = minimum_trial_duration.
   c) do: single trial.
   d) out: mrr2 = measured receive rate.

3. Third trial checks if MRR2 is a valid lower_bound.

   a) in: offered_transmit_rate = MRR2.
   b) in: trial_duration = minimum_trial_duration.
   c) do: single trial.
   d) out: verify MRR2 is a valid lower_bound.

Intermediate phase 1
````````````````````

1. Normal sequence

   a) in: ndr_interval = pdr_interval = (mrr, mrr2).
   b) in: target_interval_width = 4 * final_relative_width.
   c) in: trial_duration = minimum_trial_duration.
   d) do: internal search
      - binary search adjusting pdr_interval, ndr_interval.
      - if any interval becomes invalid, go to 2.
   e) out: ndr_interval, pdr_interval.

2. Exception sequence

   a) in: ndr_interval = (?, ?), pdr_interval = (?, ?).
   b) in: trial_duration = minimum_trial_duration.
   c) external search
      - if upper_bound invalid, increase upper_bound.
      - if lower_bound invalid, decrease lower_bound.
      - if ndr_interval or pdr_interval invalid go to c.
   d) out: ndr_interval, pdr_interval.
   e) go to 1.

Intermediate phase 2
````````````````````

1. Normal sequence

   a) in: ndr_interval, pdr_interval.
   b) in: target_interval_width = 2 * final_relative_width.
   c) in: trial_duration = sqrt(final_trial_duration).
   d) internal search
      - binary search adjusting pdr_interval, ndr_interval.
      - if any interval becomes invalid, go to 2.
   d) out: ndr_interval, pdr_interval.

2. Exception sequence

   a) in: ndr_interval = (?, ?), pdr_interval = (?, ?).
   b) in: trial_duration = sqrt(final_trial_duration).
   c) external search
      - if upper_bound invalid, increase upper_bound.
      - if lower_bound invalid, decrease lower_bound.
      - if ndr_interval or pdr_interval invalid go to c.
   d) out: ndr_interval, pdr_interval.
   e) go to 1.

Final phase
```````````

1. Normal sequence

   a) in: ndr_interval, pdr_interval.
   b) in: target_interval_width = final_relative_width.
   c) in: trial_duration = final_trial_duration.
   d) internal search
      - binary search adjusting pdr_interval, ndr_interval.
      - if any interval becomes invalid, go to 2.
   d) out: ndr_interval, pdr_interval. MDR search success.

2. Exception sequence

   a) in: ndr_interval = (?, ?), pdr_interval = (?, ?).
   b) in: trial_duration = final_trial_duration.
   c) external search
      - if upper_bound invalid, increase upper_bound.
      - if lower_bound invalid, decrease lower_bound.
      - if ndr_interval or pdr_interval invalid go to c.
   d) out: ndr_interval, pdr_interval.
   e) go to 1.
