---
title: "Overview"
weight: 1
---

# Data Plane Throughput

Network data plane throughput is measured using multiple test methods in
order to obtain representative and repeatable results across the large
set of performance test cases implemented and executed within CSIT.

Following throughput test methods are used:

- MLRsearch - Multiple Loss Ratio search, used in NDRPDR tests.
- PLRsearch - Probabilistic Loss Ratio search, used in SOAK tests.
- MRR - Maximum Receive Rate tests, the method based on FRMOL from RFC 2285.

Description of each test method is followed by generic test properties
shared by all methods.

## NDRPDR Tests

These tests employ MLRsearch to find two conditional throughput values.
NDR for zero loss ratio goal and PDR for 0.5% loss ratio goal.

### Algorithm Details

See [MLRSearch]({{< ref "mlr_search/#MLRsearch" >}}) section for more detail.
MLRsearch is being standardized in IETF in
[draft-ietf-bmwg-mlrsearch](https://datatracker.ietf.org/doc/html/draft-ietf-bmwg-mlrsearch-06).

### Description

Multiple Loss Ratio search (MLRsearch) algorithm can discover multiple
conditional throughputs in a single search,
reducing the overall test execution time compared to a binary search.
In FD.io CSIT, conditional throughputs are discovered for two search goals:
Non-Drop Rate (NDR, zero loss ratio goal)
and Partial Drop Rate (PDR, 0.5% loss ratio goal).
Other inputs are common for both goals:
Goal width is 0.5%, trial duration is 1 second, duration sum goal is 21 seconds
and exceed ratio is 50%.

The main algorithm expresses the conditional throughput based on one-port load.
The results presented in CSIT show aggregate load,
(the value from the search is doubled if the tests uses bidirectional traffic).

### Usage

MLRsearch tests are run to discover NDR and PDR rates for each VPP and
DPDK release covered by CSIT report. Results for small frame sizes
(64B/78B, IMIX) are presented in packet throughput graphs
(Box-and-Whisker Plots) with NDR and PDR rates plotted against the test
cases covering popular VPP packet paths.

Each test is executed at least 10 times to verify measurements
repeatability and results are compared between releases and test
environments. NDR and PDR packet and bandwidth throughput results for
all frame sizes and for all tests are presented in detailed results
tables.

## SOAK Tests

These tests employ PLRsearch to find a critical load value.

### Algorithm Details

See [PLRSearch]({{< ref "plr_search/#PLRsearch" >}}) methodology section for
more detail. PLRsearch is being standardized in IETF in
[draft-vpolak-bmwg-plrsearch](https://tools.ietf.org/html/draft-vpolak-bmwg-plrsearch).

### Description

Probabilistic Loss Ratio search (PLRsearch) tests discovers a packet
throughput rate associated with configured Packet Loss Ratio (PLR)
target for tests run over an extended period of time a.k.a. soak
testing. PLRsearch assumes that system under test is probabilistic in
nature, and not deterministic.

### Usage

PLRsearch are run to discover a critical load for PLR=10^-7^
(close to NDR) for VPP release covered by CSIT report. Results for small
frame sizes (64B/78B) are presented in packet throughput graphs (Box
Plots) for a small subset of baseline tests.

Each soak test lasts 30 minutes and is executed at least twice.

## MRR Tests

### Algorithm Details

See [MRR Throughput]({{< ref "mrr/#MRR" >}})
section for more detail about MRR tests configuration.

FD.io CSIT performance dashboard includes complete description of
[daily performance trending tests]({{< ref "../../trending/analysis" >}})
and [VPP per patch tests]({{< ref "../../per_patch_testing.md" >}}).

### Description

Maximum Receive Rate (MRR) tests are complementary to MLRsearch tests,
as they provide a maximum “raw” throughput benchmark for development and
testing community.

MRR tests measure the packet forwarding rate under the maximum load
offered by traffic generator (dependent on link type and NIC model) over
a set trial duration, regardless of packet loss. Maximum load for
specified Ethernet frame size is set to the bi-directional link rate.

### Usage

MRR tests are much faster than MLRsearch as they rely on
a small set of trials with very short duration. It is this property
that makes them suitable for continuous execution in daily performance
trending jobs enabling detection of performance anomalies (regressions,
progressions) resulting from data plane code changes.

MRR tests are also used for VPP per patch performance jobs verifying
patch performance vs parent. CSIT reports include MRR throughput
comparisons between releases and test environments. Small frame sizes
only (64B/78B, IMIX).

## Generic Test Properties

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
