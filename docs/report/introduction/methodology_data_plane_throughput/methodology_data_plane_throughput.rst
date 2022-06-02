.. _data_plane_throughput:

Data Plane Throughput Tests
---------------------------

Network data plane throughput is measured using multiple test methods in
order to obtain representative and repeatable results across the large
set of performance test cases implemented and executed within CSIT.

Following throughput test methods are used:

- MLRsearch - Multiple Loss Ratio search
- MRR - Maximum Receive Rate
- PLRsearch - Probabilistic Loss Ratio search

..
    TODO: Add RECONF.
    TODO: Link to method-specific pages instead of duplicate info below.

Description of each test method is followed by generic test properties
shared by all methods.

MLRsearch Tests
^^^^^^^^^^^^^^^

Description
~~~~~~~~~~~

Multiple Loss Ratio search (MLRsearch) tests discover multiple packet
throughput rates in a single search, reducing the overall test execution
time compared to a binary search. Each rate is associated with a
distinct Packet Loss Ratio (PLR) criteria. In FD.io CSIT two throughput
rates are discovered: Non-Drop Rate (NDR, with zero packet loss, PLR=0)
and Partial Drop Rate (PDR, with PLR<0.5%). MLRsearch is compliant with
:rfc:`2544`.

Usage
~~~~~

MLRsearch tests are run to discover NDR and PDR rates for each VPP and
DPDK release covered by CSIT report. Results for small frame sizes
(64b/78B, IMIX) are presented in packet throughput graphs
(Box-and-Whisker Plots) with NDR and PDR rates plotted against the test
cases covering popular VPP packet paths.

Each test is executed at least 10 times to verify measurements
repeatability and results are compared between releases and test
environments. NDR and PDR packet and bandwidth throughput results for
all frame sizes and for all tests are presented in detailed results
tables.

Details
~~~~~~~

See :ref:`mlrsearch_algorithm` section for more detail. MLRsearch is
being standardized in IETF in `draft-ietf-bmwg-mlrsearch
<https://datatracker.ietf.org/doc/html/draft-ietf-bmwg-mlrsearch-01>`_.

MRR Tests
^^^^^^^^^

Description
~~~~~~~~~~~

Maximum Receive Rate (MRR) tests are complementary to MLRsearch tests,
as they provide a maximum “raw” throughput benchmark for development and
testing community.

MRR tests measure the packet forwarding rate under the maximum load
offered by traffic generator (dependent on link type and NIC model) over
a set trial duration, regardless of packet loss. Maximum load for
specified Ethernet frame size is set to the bi-directional link rate.

Usage
~~~~~

MRR tests are much faster than MLRsearch as they rely on a single trial
or a small set of trials with very short duration. It is this property
that makes them suitable for continuous execution in daily performance
trending jobs enabling detection of performance anomalies (regressions,
progressions) resulting from data plane code changes.

MRR tests are also used for VPP per patch performance jobs verifying
patch performance vs parent. CSIT reports include MRR throughput
comparisons between releases and test environments. Small frame sizes
only (64b/78B, IMIX).

Details
~~~~~~~

See :ref:`mrr_throughput` section for more detail about MRR tests
configuration.

FD.io CSIT performance dashboard includes complete description of
`daily performance trending tests
<https://s3-docs.fd.io/csit/master/trending/methodology/performance_tests.html>`_
and `VPP per patch tests
<https://s3-docs.fd.io/csit/master/trending/methodology/perpatch_performance_tests.html>`_.

PLRsearch Tests
^^^^^^^^^^^^^^^

Description
~~~~~~~~~~~

Probabilistic Loss Ratio search (PLRsearch) tests discovers a packet
throughput rate associated with configured Packet Loss Ratio (PLR)
criteria for tests run over an extended period of time a.k.a. soak
testing. PLRsearch assumes that system under test is probabilistic in
nature, and not deterministic.

Usage
~~~~~

PLRsearch are run to discover a sustained throughput for PLR=10^-7
(close to NDR) for VPP release covered by CSIT report. Results for small
frame sizes (64b/78B) are presented in packet throughput graphs (Box
Plots) for a small subset of baseline tests.

Each soak test lasts 30 minutes and is executed at least twice. Results are
compared against NDR and PDR rates discovered with MLRsearch.

Details
~~~~~~~

See :ref:`plrsearch` methodology section for more detail. PLRsearch is
being standardized in IETF in `draft-vpolak-bmwg-plrsearch
<https://tools.ietf.org/html/draft-vpolak-bmwg-plrsearch>`_.

Generic Test Properties
^^^^^^^^^^^^^^^^^^^^^^^

All data plane throughput test methodologies share following generic
properties:

- Tested L2 frame sizes (untagged Ethernet):

  - IPv4 payload: 64B, IMIX (28x64B, 16x570B, 4x1518B), 1518B, 9000B.
  - IPv6 payload: 78B, IMIX (28x78B, 16x570B, 4x1518B), 1518B, 9000B.
  - All quoted sizes include frame CRC, but exclude per frame
    transmission overhead of 20B (preamble, inter frame gap).

- Offered packet load is always bi-directional and symmetric.
- All measured and reported packet and bandwidth rates are aggregate
  bi-directional rates reported from external Traffic Generator
  perspective.

..
    TODO: Incorporate ASTF specifics: No IMIX, transactions instead of packets,
    slightly non-symmetric traffic with TCP profiles, unsure max_rate.
    TODO: Mention latency.
