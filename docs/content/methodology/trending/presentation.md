---
title: "Presentation"
weight: 2
---

# Trend Presentation

## Failed tests

The [Failed tests tables](https://csit.fd.io/news/) list the tests which failed
during the last test run. Separate tables are generated for each testbed.

## Regressions and progressions

[These tables](https://csit.fd.io/news/) list tests which encountered
a regression or progression during the specified time period, which is currently
set to the last 1, 7, and 130 days.

## Trendline Graphs

[Trendline graphs](https://csit.fd.io/trending/) show measured per run averages
of MRR values, NDR or PDR values, user-selected telemetry metrics, group average
values, and detected anomalies. The graphs are constructed as follows:

- X-axis represents the date in the format MMDD.
- Y-axis represents run-average MRR value, NDR or PDR values in Mpps or selected
  metrics. For PDR tests also a graph with average latency at 50% PDR [us] is
  generated.
- Markers to indicate anomaly classification:
  - Regression - red circle.
  - Progression - green circle.
- The line shows average value of each group.

In addition the graphs show dynamic labels while hovering over graph data
points, presenting the CSIT build date, measured value, VPP reference, trend job
build ID and the LF testbed ID.
