.. _mlrsearch_algorithm:

MLRsearch Tests
---------------

Overview
~~~~~~~~

Multiple Loss Rate search (MLRsearch) tests use specific search algorithm
implemented in FD.io CSIT project. MLRsearch discovers multiple packet
throughput rates in a single search, each rate is associated with a
different Packet Loss Ratio (PLR) criteria.

Two packet loss criteria used in FD.io CSIT are Non-Drop Rate (NDR,
with zero packet loss, PLR=0) and Partial Drop Rate (PDR, with packet
loss rate not greater than the configured non-zero PLR).

MLRsearch discovers intended loads acting as upper bound and lower bound
for each configured loss ratio. It does that in a single pass, thus
reducing required time duration compared to separate `binary search`_es
for each ratio separately. Overall
search time is reduced even further by relying on shorter trial
durations in intermediate steps, with only the final measurements
conducted at the specified final trial duration. This approach leads to
shorter overall execution times, compared to standard binary search (per ratio),
while still satisfying RFC2544.

.. Note:: All throughput rates are *always* aggregates, usually consisting
   of of two equal (symmetric) uni-directional packet rates
   received and reported by an external traffic generator.

Search Implementation
~~~~~~~~~~~~~~~~~~~~~

Detailed description of the MLRsearch algorithm is included in the IETF
draft `draft-ietf-bmwg-mlrsearch
<https://tools.ietf.org/html/draft-ietf-bmwg-mlrsearch-01>`_
that is in the process of being standardized in the IETF Benchmarking
Methodology Working Group (BMWG).

MLRsearch is also available as a `PyPI (Python Package Index) library
<https://pypi.org/project/MLRsearch/>`_.

Implementation Deviations
~~~~~~~~~~~~~~~~~~~~~~~~~

FD.io CSIT implementation of MLRsearch so far is fully based on a description
which will be released as next draft version.

.. _binary search: https://en.wikipedia.org/wiki/Binary_search
