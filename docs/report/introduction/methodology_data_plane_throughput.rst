Data Plane Throughput
---------------------

Network data plane packet and bandwidth throughput are measured using
multiple methods in order to obtain representative and repeatable
results across the large set of performance test cases implemented and
executed within CSIT. Following throughput test methods are used:

#. MLRsearch: Multiple Loss Ratio search

   - **Description**: MLRsearch discovers multiple packet throughput
     rates in a single search, reducing the overall test execution
     time compared to a binary search. Each rate associated with a
     distinct Packet Loss Ratio (PLR) criteria. In FD.io CSIT two
     throughput rates are discovered: Non-Drop Rate (NDR, with zero
     packet loss, PLR=0) and Partial Drop Rate (PDR, with PLR<0.5%).
     MLRsearch is compliant with :rfc:`2544`.
   - **Usage**: MLRsearch tests are run to discover NDR and PDR rates
     for each VPP and DPDK release covered by CSIT report. Results for
     small frame sizes (64b/78B, IMIX) are presented in packet
     throughput graphs (Box-and-Whisker Plots) with NDR and PDR rates
     plotted against the test cases covering popular VPP packet paths.
     Each test is executed at least 10 times to verify measurements
     repeatability and results are compared between releases and test
     environments. NDR and PDR packet and bandwidth throughput results
     for all frame sizes and for all tests are presented in detailed
     results tables.
   - **References**: See :ref:`mlrsearch_algorithm` for more detailed
     description of MLRsearch tests. MLRsearch is being standardized
     in IETF with `draft-vpolak-mkonstan-mlrsearch
     <https://tools.ietf.org/html/draft-vpolak-mkonstan-bmwg-mlrsearch>`_.

#. MRR Measurements: Maximum Receive Rate

   - **Description**: MRR tests are complementary to MLRsearch tests,
     as they provide a maximum “raw” throughput benchmark for
     development and testing community. MRR tests measure the packet
     forwarding rate under the maximum load offered by traffic
     generator over a set trial duration, regardless of packet loss.
     Maximum load for specified Ethernet frame size is set to the
     bi-directional link rate.
   - **Usage**: MRR tests are much faster than MLRsearch as they rely
     on a single trial or a small set of trials with very short
     duration. It is this property that makes them suitable for
     continuous execution in daily performance trending jobs enabling
     detection of performance anomalies (regressions, progressions)
     resulting from data plane code changes. MRR tests are also used
     for VPP per patch performance jobs verifying patch performance
     vs. parent. CSIT reports include MRR throughput comparisons
     between releases and test environments. Small frame sizes only
     (64b/78B, IMIX).
   - **References**: See :ref:`mrr_throughput` for more detailed
     description of MRR tests configuration used for daily performance
     trending jobs. VPP per patch test methodology is available on
     `FD.io CSIT trending pages
     <https://docs.fd.io/csit/master/trending/methodology/perpatch_performance_tests.html>`_.

#. PLRsearch: Probabilistic Loss Ratio search

   - **Description**: PLRsearch discovers a packet throughput rate
     associated with configured Packet Loss Ratio (PLR) criteria for
     tests run over an extended period of time a.k.a. soak testing.
     PLRsearch assumes that system under test is probabilistic in
     nature, and not deterministic.
   - **Usage**: PLRsearch are run to discover a sustained throughput
     for PLR=10^-7 (close to NDR) for VPP release covered by CSIT
     report. Results for small frame sizes (64b/78B) are presented in
     packet throughput graphs (Box Plots) for a small subset of
     baseline tests. Each soak test lasts 2hrs and is executed at
     least twice. Results are compared against NDR and PDR rates
     discovered with MLRsearch.
   - **References**: See :ref:`plrsearch_algorithm` for more detailed
     description of PLRsearch tests. PLRsearch is being standardized
     in IETF with `draft-vpolak-bmwg-plrsearch
     <https://tools.ietf.org/html/draft-vpolak-bmwg-plrsearch>`_.

All of the listed data plane throughput test methodologies share following properties:

- Tested L2 frame sizes (untagged Ethernet):

  - IPv4 payload: 64B, IMIX (28x64B, 16x570B, 4x1518B), 1518B, 9000B.
  - IPv6 payload: 78B, IMIX (28x78B, 16x570B, 4x1518B), 1518B, 9000B.

- All measured rates are aggregate bi-directional rates reported from
  external Traffic Generator perspective.