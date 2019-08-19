
.. raw:: latex

    \clearpage

SRv6 Routing
============

Following sections include summary graphs of VPP Phy-to-Phy performance
with SRv6, including NDR throughput (zero packet loss)
and PDR throughput (<0.5% packet loss). Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/srv6?h=rls1908>`_.

.. toctree::

    srv6-3n-skx-xxv710
    srv6-3n-hsw-xl710
