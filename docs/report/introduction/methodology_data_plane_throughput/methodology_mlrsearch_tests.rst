.. _mlrsearch_algorithm:

MLRsearch Tests
---------------

Overview
~~~~~~~~

Multiple Loss Ratio search (MLRsearch) tests use an optimized search algorithm
implemented in FD.io CSIT project. MLRsearch discovers any number of
loss ratio loads in a single search.

Two loss ratio goals are of interest in FD.io CSIT, leading to Non-Drop Rate
(NDR, loss ratio goal is exact zero) and Partial Drop Rate
(PDR, non-zero loss ratio goal, currently 0.5%).

MLRsearch discovers all the loads in a single pass, reducing required time
duration compared to separate `binary search`_es for each rate. Overall
search time is reduced even further by relying on shorter trial
durations of intermediate steps, with only the final measurements
conducted at the specified final trial duration. This results in the
shorter overall execution time when compared to standard NDR/PDR binary
search, while guaranteeing similar results.

.. Note:: All throughput rates are *always* bi-directional
   aggregates of two equal (symmetric) uni-directional packet rates
   received and reported by an external traffic generator.

Search Implementation
~~~~~~~~~~~~~~~~~~~~~

Detailed description of the MLRsearch algorithm is included in the IETF
draft `draft-ietf-bmwg-mlrsearch-01
<https://datatracker.ietf.org/doc/html/draft-ietf-bmwg-mlrsearch-01>`_
(older version, update when newer is available)
that is in the process of being standardized in the IETF Benchmarking
Methodology Working Group (BMWG).

MLRsearch is also available as a `PyPI (Python Package Index) library
<https://pypi.org/project/MLRsearch/>`_.

Algorithm highlights
~~~~~~~~~~~~~~~~~~~~

MRR and receive rate at MRR load are used as initial guesses for the search.

All previously measured trials (except the very first one which can act
as a warm-up) are taken into consideration, unless superseded
by a trial at the same load but higher duration.

Integer units are used internally, even though inputs are floating point numbers.

For every loss ratio goal, two tightest bounds (from results of large enough
trial duration) form an interval.

Exit condition is given by that interval reaching low enough relative width.

The integer unit does not correspond to a load in packets per second,
but to a logarithm of that load (so exit condition is absolute difference
in integer units).

Small enough width is achieved by bisecting the current interval.

The bisection can be uneven, to save measurements based on information theory.

Switching to higher trial duration may require to re-measure
at a load from previous trial duration.

When the re-measurement does not confirm previous bound classification
(e.g. tightest lower bound at shorted trial duration becomes
a newest tightest upper bound upon re-measurement),
external search is used to find close enough bound of the lost type.
External search is a generalization of the first stage of `exponential search`_.

Shorter trial durations use double (in integer units) width goal,
because one bisection is always safe before risking external search.

Smaller loss ratios are found first (NDR with final trial duration)
before search for higher loss ratios resumes (shorter trial durations
for PDR).

Other heuristics are there, aimed to prevent unneccessarily narrow intervals,
and to handle corner cases around min and max load.

Deviations from RFC 2544
~~~~~~~~~~~~~~~~~~~~~~~~

CSIT does not have any explicit wait times before and after trial traffic.

Small differences between intended and offered load are tolerated,
mainly due to varios time overheads preventing precise measurement
of the traffic duration (and TRex can sometimes suffer from duration stretching).

The final trial duration is only 30s (10s for reconf tests).

.. _binary search: https://en.wikipedia.org/wiki/Binary_search
.. _exponential search: https://en.wikipedia.org/wiki/Exponential_search
