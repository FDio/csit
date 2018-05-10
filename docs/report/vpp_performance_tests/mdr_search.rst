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
implementation in FD.io CSIT.

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

1. First trial measures at maximum rate and discovers MRR.

   a) in: trial_duration = initial_trial_duration.
   b) in: offered_transmit_rate = maximum_transmit_rate.
   c) do: single trial.
   d) out: measured loss ratio.
   e) out: mrr = measured receive rate.

2. Second trial measures at MRR and discovers MRR2.

   a) in: trial_duration = initial_trial_duration.
   b) in: offered_transmit_rate = MRR.
   c) do: single trial.
   d) out: measured loss ratio.
   e) out: mrr2 = measured receive rate.

3. Third trial measures at MRR2.

   a) in: trial_duration = initial_trial_duration.
   b) in: offered_transmit_rate = MRR2.
   c) do: single trial.
   d) out: measured loss ratio.

Intermediate phases
```````````````````

1. Main loop.
   a) in: trial_duration for the current phase.
      initial_trial_duration for first intermediate phase,
      final_trial_duration for the final phase,
      geometric average of the two durations for the middle phase.
   b) in: relative_width_goal for the current phase.
      final_relative_width for the final phase,
      double of final_relative_width for the middle phase,
      quadruple of final_relative_width for the first intermediate phase.
   c) in: ndr_interval, pdr_interval from previous loop iteration or previous phase.
      If the previous phase is the initial phase, both intervals have
      lower_bound = MRR2, uper_bound = MRR.
   d) do: If a lower_bound (ndr first) is invalid, prepare a new (decreased) transmit rate to measure at.
      The decreased rate is 3 * lower_bound - 2 * upper_bound, so the new interval will have double width.
      Go to i).
   e) do: If an upper_bound (ndr first) is invalid, prepare a new (increased) transmit rate to measure at.
      The increased rate is 3 * upper_bound - 2 * lower_bound, so the new interval will have double width.
      Go to i).
   f) do: If both bounds are valid, but an interval does not meet the current width goal,
      prepare a new (middle) transmit rate to measure at.
      The middle rate is (lower bound + upper bound) / 2, so the new interval will have half width.
      Go to i).
   g) do: If some bound has still only been measured at a lower duration, prepare to re-measure
      at the current duration (and the same transmit rate).
      Lower bounds first, ndr before pdr otherwise.
      Go to i).
   h) This is only reached when a phase has reached its exit criteria.
      Go to k).
   i) do: Perform the trial measurement at the prepared transmit rate and trial_duration,
      and classify its loss ratio.
   j) do: Update bounds of both intervals, according to the classified measurement.
      Go to next iteration c), taking the updated intervals as new input.
   k) out: the updated ndr_interval and pdr_interval.
      In final phase this is also considered as the result of the whole search.
      For other phases, the next phase loop is started with the current results as an input.

Implementation details
----------------------

The algorithm as implemented contains additional details
omitted from the description above.
Here is a short description of them, without detailing their mutual interaction.

1) Logarithmic transmit rate.
   In order to better fit the relative width goal, the interval doubling and halving
   is done differently. For example, middle of 2 and 8 is 4, not 5.
2) Optimistic maximum rate.
   The increased rate is never higher than maximum rate, upper bound at that rate is always considered valid.
3) Pessimistic minimum rate.
   The decreased rate is never lower than minimum rate, if a lower bound at that rate is invalid,
   a phase stops refining the interval further (until it gets re-measured).
4) Conservative interval updates.
   Measurements above current upper bound never update a valid upper bound, even if drop ratio is low.
   Measurements below current lower bound always update any lower bound if drop ratio is high.
5) Ensure sufficient interval width.
   If the prepared increased or decreased rate will result in width less than the current goal,
   increase/decrease more. This can happen if measurement for the other interval makes the current interval too narrow.
   Similarly, take care the measurements in the initiah phase create wide enough interval.
