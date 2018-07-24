MLRsearch Algorithm
===================

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
---------

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
---------------------

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
-------------------------

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

Test Effectiveness Comparison
-----------------------------

Introduction
````````````

CSIT release 1804 contains two test suites that use the new MLRsearch
to enable comparison against existing CSIT NDR and PDR binary searches.
The suites got chosen based on the level of consistency of their
historical NDR/PDR results:

#. *10Ge2P1X520-Ethip4-Ip4Base-Ndrpdr* - yielding very consistent binary
   search results.
#. *10Ge2P1X520-Eth-L2Bdbasemaclrn-Eth-2Vhostvr1024-1Vm-Ndrpdr* - yielding
   somewhat inconsistent results.

Here "inconsistent" means the values found differ between runs,
even though the setup and the test are exactly the same.

The search part of CSIT binary search tests requires a single 5-second warmup
and each trial measurement is set to 10 seconds.

New tests with MLRsearch do not have any warmup, as initial measurements
are not critical to the final result.

Fairness of the following comparison has been achieved
by setting MLRsearch final relative width to values causing the width to match
the binary NDR/PDR result.
Each search algorithm has been run with three different
(final) trial durations: 10s, 30s and 60s.

Tables below compares overall test duration between the search tests.
For simplicity only data for single thread 64B packet tests is listed,
as it takes the longest in all cases.

Data in tables is based on result of 6 runs.

Tables
``````

.. note:: The comparison was done for the MLRsearch code
          before https://gerrit.fd.io/r/12761

.. table:: Table 1. Search part of test duration.

   ==========================  ==========  ===========  ===========  ==========  ===========  ===========
   Duration+-avgdev [s]        IP4 10s     IP4 30s      IP4 60s      Vhost 10s   Vhost 30s    Vhost 60s
   ==========================  ==========  ===========  ===========  ==========  ===========  ===========
   MLRsearch (both intervals)  50.8+-1.2   109.0+-10.0  202.8+-11.7  80.5+-9.0   201.9+-20.6  474.9+-58.2
   NDR binary                  98.9+-0.1   278.6+-0.1   548.8+-0.1   119.8+-0.1  339.3+-0.1   669.6+-0.2
   PDR binary                  98.9+-0.1   278.6+-0.1   548.8+-0.1   119.7+-0.1  339.3+-0.1   669.5+-0.1
   NDR+PDR sum                 197.8+-0.1  557.2+-0.2   1097.6+-0.1  239.5+-0.1  678.7+-0.1   1339.2+-0.1
   ==========================  ==========  ===========  ===========  ==========  ===========  ===========

.. note:: Here "avgdev" is the estimated difference between
   the average duration computed from the limited sample
   and a true average duration as its hypothetical limit for infinite samples.
   To get the usual "standard deviation" of duration, "avgdev" has to be multiplied
   by the square root of the number of samples.
   For the subtle details see `estimation of standard deviation`_,
   we used zero ACF and c4==1.

.. table:: Table 2. MLRsearch duration as percentage of NDR duration.

   ==========================================  =========  =========  =========  =========  =========  =========
   Fraction+-stdev [%]                         IP4 10s    IP4 30s    IP4 60s    Vhost 10s  Vhost 30s  Vhost 60s
   ==========================================  =========  =========  =========  =========  =========  =========
   MLRsearch duration divided by NDR duration  51.4+-1.2  39.1+-3.6  37.0+-2.1  67.2+-7.5  59.5+-6.1  70.9+-8.7
   ==========================================  =========  =========  =========  =========  =========  =========

.. note:: Here "stdev" is standard deviation as computed by the
   `simplified error propagation formula`_.

Conclusions
```````````

In consistent tests, MLRsearch is on average more than 50% faster
than a single NDR binary search (even though MLRsearch also detects PDR).

One exception is 10 second final trial duration,
where MLRsearch is (only) almost 50% faster than NDR binary search.
Most probably presence of 2 intermediate phases (instead of just 1) hurts there.

In inconsistent tests MLRsearch is still somewhat faster than NDR binary search,
but it is not by 50%, and it is hard to quantify as MLRsearch samples have wildly
varying durations.

Search Time Graphs
------------------

The following graphs were created from the data gathered from comparison runs,
for the vhost tests.
The vertical axis has always the same values,
zoomed into the interesting part of the search space.
The faint blue vertical lines separate the phases of MLRsearch.
The bound lines are sloped just to help locate the previous value,
in reality the bounds are updated instantly at the end of the measurement.

The graphs do not directly show when a particular bound is invalid.
However this can be gleaned indirectly by identifying
that the measurement does not satisfy that bound's validity conditions
(see point 2a).
Also, the external search follows, and the measurement previously acting
as and invalid upper or lower bound starts acting instead
as a valid lower or upper bound, respectively.

The following three graphs are for MLRsearch with 10 second final trial duration,
showing different behavior in this inconsistent test,
and different amount of "work" done by each phase.
Also the horizontal axis has the same scaling here.

.. image:: MDR_10_1.svg
.. image:: MDR_10_2.svg
.. image:: MDR_10_3.svg

The next graph is for MLRsearch with 60 second final trial duration,
to showcase the final phase takes the most of the overall search time.
The scaling of the horizontal axis is different.

.. image:: MDR_60.svg

Finally, here are two graphs showing NDR and PDR binary searches.
The trial duration is again 60 seconds,
but scaling of horizontal axis is once again different.
This shows the binary search spends most time measuring outside
the interesting rate region.

.. image:: NDR_60.svg
.. image:: PDR_60.svg

.. _binary search: https://en.wikipedia.org/wiki/Binary_search
.. _exponential search: https://en.wikipedia.org/wiki/Exponential_search
.. _estimation of standard deviation: https://en.wikipedia.org/wiki/Unbiased_estimation_of_standard_deviation
.. _simplified error propagation formula: https://en.wikipedia.org/wiki/Propagation_of_uncertainty#Simplification
