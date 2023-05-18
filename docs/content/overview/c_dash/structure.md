---
title: "Structure"
weight: 2
---

# Structure

The structure of C-Docs consist of:

- Performance Trending
- Per Release Performance
- Per Release Performance Comparisons
- Per Release Coverage Data
- Test Job Statistics
- Failures and Anomalies
- Documentation

## Performance Trending

Performance trending shows measured per run averages of MRR values, NDR or PDR
values, user-selected telemetry metrics, group average values, and detected
anomalies.

In addition the graphs show dynamic labels while hovering over graph data
points. By clicking on data samples, the user gets detailed information and for
lateny graphs also high dynamic range histogram of measured latency.
Latency by percentile distribution plots are used to show packet latency
percentiles at different packet rate load levels:
- No-Load, latency streams only,
- Low-Load at 10% PDR,
- Mid-Load at 50% PDR and
- High-Load at 90% PDR.

## Per Release Performance

Per release performance section presents the graphs based on the results data
obtained from the release test jobs. In order to verify benchmark results
repeatibility selected, CSIT performance tests are executed multiple times
(target: 10 times) on each physical testbed type. Box-and-Whisker plots are used
to display variations in measured throughput and latency (PDR tests only)
values.

In addition the graphs show dynamic labels while hovering over graph data
points. By clicking on data samples or the box, the user gets detailed
information and for lateny graphs also high dynamic range histogram of measured
latency.
Latency by percentile distribution plots are used to show packet latency
percentiles at different packet rate load levels:
- No-Load, latency streams only,
- Low-Load at 10% PDR,
- Mid-Load at 50% PDR and
- High-Load at 90% PDR.

## Per Release Performance Comparisons

Relative comparison of packet throughput (NDR, PDR and MRR) and latency (PDR)
between user-selected releases, test beds, NICs, ... is calculated from results
of tests running on physical test beds, in 1-core, 2-core and 4-core
configurations.

Listed mean and standard deviation values are computed based on a series of the
same tests executed against respective VPP releases to verify test results
repeatability, with percentage change calculated for mean values. Note that the
standard deviation is quite high for a small number of packet throughput tests,
what indicates poor test results repeatability and makes the relative change of
mean throughput value not fully representative for these tests. The root causes
behind poor results repeatability vary between the test cases.

## Per Release Coverage Data

Detailed result tables generated from CSIT test job executions. The coverage
tests include also tests which are not run in iterative performance builds.
The tables present NDR and PDR packet throughput (packets per seconf and bits
per second) and latency percentiles (microseconds) at different packet rate load
levels:
- No-Load, latency streams only,
- Low-Load at 10% PDR,
- Mid-Load at 50% PDR and
- High-Load at 90% PDR.

## Test Job Statistics

The elementary statistical data (number of passed and failed tests and the
duration) of all daily and weekly trending performace jobs.
In addition the graphs show dynamic labels while hovering over graph data
points with detailed information. By clicking on the graph, user gets the job
summary with the list of failed tests.

## Failures and Anomalies

The presented tables list
- last build summary,
- failed tests,
- progressions and
- regressions

for all daily and weekly trending performance jobs.

## Documentation

This documentation describing the methodology, infrastructure and release notes
for each CSIT release.
