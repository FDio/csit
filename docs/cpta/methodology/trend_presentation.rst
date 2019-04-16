Trend Presentation
------------------

Performance Dashboard
`````````````````````

Dashboard tables list a summary of per test-case VPP MRR performance
trend and trend compliance metrics and detected number of anomalies.

Separate tables are generated for each testbed and each tested number of
physical cores for VPP workers (1c, 2c, 4c). Test case names are linked to
respective trending graphs for ease of navigation through the test data.

Failed tests
````````````

The Failed tests tables list the tests which failed over the specified seven-
day period together with the number of fails over the period and last failure
details - Time, VPP-Build-Id and CSIT-Job-Build-Id.

Separate tables are generated for each testbed. Test case names are linked to
respective trending graphs for ease of navigation through the test data.

Trendline Graphs
````````````````

Trendline graphs show measured per run averages of MRR values,
group average values, and detected anomalies.
The graphs are constructed as follows:

- X-axis represents the date in the format MMDD.
- Y-axis represents run-average MRR value in Mpps.
- Markers to indicate anomaly classification:

  - Regression - red circle.
  - Progression - green circle.

- The line shows average MRR value of each group.

In addition the graphs show dynamic labels while hovering over graph
data points, presenting the CSIT build date, measured MRR value, VPP
reference, trend job build ID and the LF testbed ID.
