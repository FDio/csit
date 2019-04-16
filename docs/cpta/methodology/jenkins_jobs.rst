Jenkins Jobs
------------

Performance Trending (PT)
`````````````````````````

CSIT PT runs regular performance test jobs measuring and collecting MRR
data per test case. PT is designed as follows:

1. PT job triggers:

   a) Periodic e.g. twice a day.
   b) On-demand gerrit triggered.

2. Measurements and data calculations per test case:

  a) Max Received Rate (MRR) - for each trial measurement,
     send packets at link rate for trial duration,
     count total received packets, divide by trial duration.

3. Archive MRR values per test case.
4. Archive all counters collected at MRR.

Performance Analysis (PA)
`````````````````````````

CSIT PA runs performance analysis
including anomaly detection as described above.
PA is defined as follows:

1. PA job triggers:

   a) By PT jobs at their completion.
   b) On-demand gerrit triggered.

2. Download and parse archived historical data and the new data:

   a) Download RF output.xml files from latest PT job and compressed
      archived data from nexus.
   b) Parse out the data filtering test cases listed in PA specification
      (part of CSIT PAL specification file).

3. Re-calculate new groups and their averages.

4. Evaluate new test data:

   a) If the existing group is prolonged => Result = Pass,
      Reason = Normal.
   b) If a new group is detected with lower average =>
      Result = Fail, Reason = Regression.
   c) If a new group is detected with higher average =>
      Result = Pass, Reason = Progression.

5. Generate and publish results

   a) Relay evaluation result to job result.
   b) Generate a new set of trend summary dashboard, list of failed
      tests and graphs.
   c) Publish trend dashboard and graphs in html format on
      https://docs.fd.io/.
   d) Generate an alerting email. This email is sent by Jenkins to
      csit-report@lists.fd.io
