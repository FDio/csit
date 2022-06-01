
.. raw:: latex

    \clearpage

NAT44 IPv4 Routing
==================

Following sections include summary graphs of VPP Phy-to-Phy performance
with IPv4 Routed-Forwarding, including NDR throughput (zero packet loss)
and PDR throughput (<0.5% packet loss). Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/ip4?h=rls2206>`_.

.. toctree::

    nat44-det-bidir
    nat44-ed-unidir
    nat44-ed-udp-cps
    nat44-ed-tcp-cps
    nat44-ed-udp-tput
    nat44-ed-tcp-tput
