.. _mlrsearch_algorithm:

MLRsearch Tests
^^^^^^^^^^^^^^^

Overview
~~~~~~~~

Multiple Loss Rate search (MLRsearch) tests use new search algorithm
implemented in FD.io CSIT project. MLRsearch discovers any number of packet
throughput rates in a single search, with each rate associated with a
different Packet Loss Ratio (PLR) criteria.

Two throughput rates of interest in FD.io CSIT are Non-Drop Rate (NDR,
with zero packet loss, PLR=0) and Partial Drop Rate (PDR, with packet
loss rate not greater than the configured non-zero PLR, currently 0.5%).

MLRsearch discovers all the rates in a single pass, reducing required time
duration compared to separate `binary search`_ for each rate. Overall
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
that is in the process of being standardized in the IETF Benchmarking
Methodology Working Group (BMWG).

MLRsearch is also available as a `PyPI (Python Package Index) library
<https://pypi.org/project/MLRsearch/>`_.

Implementation Deviations
~~~~~~~~~~~~~~~~~~~~~~~~~

FD.io CSIT implementation of MLRsearch is currently fully based on the -01`
version of the `draft-ietf-bmwg-mlrsearch
<https://datatracker.ietf.org/doc/html/draft-ietf-bmwg-mlrsearch-01>`_,
the PyPI version is slightly older.

.. _binary search: https://en.wikipedia.org/wiki/Binary_search
