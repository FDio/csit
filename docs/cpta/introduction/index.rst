VPP MRR Performance Dashboard
=============================

Description
-----------

Dashboard tables list a summary of per test-case VPP MRR performance trend
values and detected anomalies (Maximum Receive Rate - received packet rate
under line rate load). Data comes from trending MRR jobs executed every 12 hrs
(2:00, 14:00 UTC). Trend and anomaly calculations are done over a rolling
window of <N> samples, currently with N=14 covering last 7 days. Separate
tables are generated for tested VPP worker-thread-core combinations (1t1c,
2t2c, 4t4c).

Legend to table:

    - "Test case": name of CSIT test case, naming convention here
      `CSIT/csit-test-naming <https://wiki.fd.io/view/CSIT/csit-test-naming>`_
    - "Thput trend [Mpps]": last value of trend over rolling window.
    - "Anomaly value [Mpps]": in precedence - i) highest outlier if 3
      consecutive outliers, ii) highest regression if regressions detected,
      iii) highest progression if progressions detected, iv) nil if normal i.e.
      within trend.
    - "Anomaly vs. Trend [%]": anomaly value vs. trend value.
    - "Classification": outlier, regression, progression, normal - observed
      over a rolling window.
    - "# Outliers": number of outliers detected.

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

