.. _mlrsearch_algorithm:

MLRsearch Tests
---------------

Overview
~~~~~~~~

Multiple Loss Rate search (MLRsearch) tests use a new search algorithm
implemented in FD.io CSIT project. MLRsearch discovers multiple packet
throughput rates in a single search, with each rate associated with
different Packet Loss Ratio (PLR) criteria.

Two throughput measurements used in FD.io CSIT are Non-Drop Rate (NDR,
with zero packet loss, PLR=0) and Partial Drop Rate (PDR, with packet
loss rate not greater than the configured non-zero PLR).

MLRsearch discovers NDR and PDR in a single pass, reducing required time
duration compared to separate binary searches for NDR and PDR. Overall
search time is reduced even further by relying on shorter trial
durations of intermediate steps, with only the final measurements
conducted at the specified final trial duration. This results in the
shorter overall execution time when compared to standard NDR/PDR binary
search, while guaranteeing similar results.

If needed, MLRsearch can be easily adopted to discover more throughput
rates with different pre-defined PLRs.

.. Note:: All throughput rates are *always* bi-directional
   aggregates of two equal (symmetric) uni-directional packet rates
   received and reported by an external traffic generator.

Search Implementation
~~~~~~~~~~~~~~~~~~~~~

Detailed description of the MLRsearch algorithm is included in the IETF
draft `draft-vpolak-mkonstan-mlrsearch
<https://tools.ietf.org/html/draft-vpolak-mkonstan-bmwg-mlrsearch>`_
that is in the process of being standardized in the IETF Benchmarking
Methodology Working Group (BMWG).

MLRsearch is also available as a `PyPI (Python Package Index) library
<https://pypi.org/project/MLRsearch/>`_.

Implementation Deviations
~~~~~~~~~~~~~~~~~~~~~~~~~

FD.io CSIT implementation of MLRsearch so far is fully based on the -01
version of the `draft-vpolak-mkonstan-mlrsearch-01
<https://tools.ietf.org/html/draft-vpolak-mkonstan-bmwg-mlrsearch-01>`_.

.. _binary search: https://en.wikipedia.org/wiki/Binary_search
.. _exponential search: https://en.wikipedia.org/wiki/Exponential_search
.. _estimation of standard deviation: https://en.wikipedia.org/wiki/Unbiased_estimation_of_standard_deviation
.. _simplified error propagation formula: https://en.wikipedia.org/wiki/Propagation_of_uncertainty#Simplification
