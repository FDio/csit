
.. raw:: latex

    \clearpage

Virtual Topology System
=======================

This section includes summary graphs of VPP Phy-to-VM(s)-to-Phy packet
latency with with VM virtio and VPP vhost-user virtual interfaces
measured at 100% of discovered NDR throughput rate. Latency is reported
for VPP running in multiple configurations of VPP worker thread(s),
a.k.a. VPP data plane thread(s), and their physical CPU core(s)
placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/vts?h=rls1908>`_.

.. toctree::

    vts-3n-skx-xxv710
    vts-3n-hsw-xl710
    vts-3n-tsh-x520
