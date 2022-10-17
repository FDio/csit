Trend Presentation
^^^^^^^^^^^^^^^^^^

Failed tests
~~~~~~~~~~~~

The Failed tests tables list the tests which failed during the last test run.
Separate tables are generated for each testbed.

Regressions and progressions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These tables list tests which encountered a regression or progression during the
specified time period, which is currently set to the last 21 days.

Trendline Graphs
~~~~~~~~~~~~~~~~

Trendline graphs show measured per run averages of MRR values, NDR or PDR
values, group average values, and detected anomalies.
The graphs are constructed as follows:

- X-axis represents the date in the format MMDD.
- Y-axis represents run-average MRR value, NDR or PDR values in Mpps. For PDR
  tests also a graph with average latency at 50% PDR [us] is generated.
- Markers to indicate anomaly classification:

  - Regression - red circle.
  - Progression - green circle.

- The line shows average MRR value of each group.

In addition the graphs show dynamic labels while hovering over graph data
points, presenting the CSIT build date, measured value, VPP reference, trend job
build ID and the LF testbed ID.
