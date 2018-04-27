VPP Performance Dashboard
=========================

Description
-----------

Dashboard tables list a summary of latest per test-case VPP Maximum
Receive Rate (MRR) performance trend, trend compliance metrics and
detected number of anomalies. Data samples come from the CSIT VPP
performance trending jobs  executed twice a day, every 12 hrs (02:00,
14:00 UTC). All trend and anomaly evaluation is based on a rolling
window of <N=14> data samples, covering last 7 days.

Legend to table:

    - **Test Case** : name of CSIT test case, naming convention in
      `CSIT wiki <https://wiki.fd.io/view/CSIT/csit-test-naming>`_.
    - **Trend [Mpps]** : last value of trend.
    - **Short-Term Change [%]** : Relative change of last trend value
      vs. last week trend value.
    - **Long-Term Change [%]** : Relative change of last trend value vs.
      maximum of trend values over the last quarter except last week.
    - **Regressions [#]** : Number of regressions detected.
    - **Progressions [#]** : Number of progressions detected.
    - **Outliers [#]** : Number of outliers detected.

MRR tests measure the packet forwarding rate under the maximum load
offered by traffic generator over a set trial duration, regardless of
packet loss.

For more detail about MRR tests, trend and anomaly calculations please
refer to :ref:`trending_methodology` section.

Tested VPP worker-thread-core combinations (1t1c, 2t2c, 4t4c) are listed
in separate tables in section 1.x. Followed by trending methodology in
section 2. and daily trending graphs in sections 3.x. Daily trending
data used is provided in sections 4.x.

VPP worker on 1t1c
------------------

.. include:: ../../../_build/_static/vpp/performance-trending-dashboard-1t1c.rst

VPP worker on 2t2c
------------------

.. include:: ../../../_build/_static/vpp/performance-trending-dashboard-2t2c.rst

VPP worker on 4t4c
------------------

.. include:: ../../../_build/_static/vpp/performance-trending-dashboard-4t4c.rst
