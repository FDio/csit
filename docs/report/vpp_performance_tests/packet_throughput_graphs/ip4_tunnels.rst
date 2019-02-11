
.. raw:: latex

    \clearpage

IPv4 Tunnels
============

Following sections include summary graphs of VPP Phy-to-Phy performance
with IPv4 Overlay Tunnels, including NDR throughput (zero packet loss)
and PDR throughput (<0.5% packet loss).  Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/ip4_tunnels?h=rls1901>`_.

.. toctree::

    ip4_tunnels-3n-hsw-x520
    ip4_tunnels-3n-hsw-x710
    ip4_tunnels-3n-skx-x710
