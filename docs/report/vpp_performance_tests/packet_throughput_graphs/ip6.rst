
.. raw:: latex

    \clearpage

IPv6 Routing
============

Following sections include summary graphs of VPP Phy-to-Phy performance
with IPv6 Routed-Forwarding, including NDR throughput (zero packet loss)
and PDR throughput (<0.5% packet loss). Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/ip6?h=rls2206>`_.

.. toctree::

    ip6-2n-icx-xxv710
    ip6-3n-icx-xxv710
    ip6-2n-skx-xxv710
    ip6-2n-skx-x710
    ip6-3n-skx-xxv710
    ip6-3n-skx-x710
    ip6-2n-clx-xxv710
    ip6-2n-clx-x710
    ip6-2n-clx-cx556a
    ip6-2n-zn2-xxv710
    ip6-2n-zn2-x710
    ip6-2n-zn2-cx556a
    ip6-3n-alt-xl710
    ip6-3n-tsh-x520
    ip6-2n-tx2-xl710
    ip6-2n-dnv-x553
    ip6-3n-dnv-x553
    ip6-2n-aws-nitro50g
