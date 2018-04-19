VPP MRR Performance Dashboard
=============================

Description
-----------

Dashboard tables list a summary of per test-case VPP MRR performance trend 
values and detected anomalies (Maximum Receive Rate - received packet rate 
under line rate load). Data comes from trending MRR jobs executed every 12 
hrs (2:00, 14:00 UTC). Trend, trend compliance and anomaly calculations are 
based on a rolling window of <N> samples, currently N=14 covering last 7 days. 
Separate tables are generated for tested VPP worker-thread-core combinations 
(1t1c, 2t2c, 4t4c).

Legend to table:

    - "Test Case": name of CSIT test case, naming convention on
      `CSIT wiki <https://wiki.fd.io/view/CSIT/csit-test-naming>`_.
    - "Throughput Trend [Mpps]": last value of trend calculated over a
      rolling window.
    - "Trend Compliance": calculated based on detected anomalies, listed in
       precedence order - i) "failure" if 3 consecutive outliers,
       ii) "regression" if any regressions, iii) "progression" if any
       progressions, iv) "normal" if data compliant with trend.
    - "Anomaly Value [Mpps]": i) highest outlier if "failure", ii) highest
      regression if "regression", iii) highest progression if "progression",
      iv) "-" if normal i.e. within trend.
    - "Change [%]": "Anomaly Value" vs. "Throughput Trend", "-" if normal.
    - "# Outliers": number of outliers detected within a rolling window.

Tables are listed in sections 1.x. Followed by daily trending graphs in
sections 2.x. Daily trending data used to generate the graphs is listed in
sections 3.x.

VPP worker on 1t1c
------------------

.. include:: ../../../_build/_static/vpp/performance-trending-dashboard-1t1c.rst

VPP worker on 2t2c
------------------

.. include:: ../../../_build/_static/vpp/performance-trending-dashboard-2t2c.rst

VPP worker on 4t4c
------------------

.. include:: ../../../_build/_static/vpp/performance-trending-dashboard-4t4c.rst
