
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
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/container_memif?h=rls2206>`_.

.. toctree::

    container_memif-2n-icx-xxv710
    container_memif-2n-skx-xxv710
    container_memif-2n-clx-xxv710
    container_memif-2n-clx-cx556a
    container_memif-2n-zn2-xxv710
    container_memif-2n-zn2-cx556a
