
.. raw:: latex

    \clearpage

LXC/DRC Container Memif
=======================

Following sections include summary graphs of VPP Phy-to-Phy performance
with Container memif Connections, including NDR throughput (zero packet loss)
and PDR throughput (<0.5% packet loss). Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/container_memif?h=rls1908>`_.

.. toctree::

    container_memif-2n-skx-xxv710
    container_memif-3n-skx-xxv710
