
.. raw:: latex

    \clearpage

IPv4 Routing
============

This section includes summary graphs of VPP Phy-to-Phy packet latency
with IPv4 Routed-Forwarding measured at 100% of discovered NDR throughput
rate. Latency is reported for VPP running in multiple configurations of
VPP worker thread(s), a.k.a. VPP data plane thread(s), and their
physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/ip4?h=rls1908>`_.

.. toctree::

    ip4-2n-skx-xxv710
    ip4-2n-skx-x710
    ip4-3n-skx-xxv710
    ip4-3n-skx-x710
    ip4-3n-hsw-xl710
