
.. raw:: latex

    \clearpage

K8s Container Memif
===================

Following sections include summary graphs of VPP Phy-to-Phy performance
with Container Orchestrated Topologies, including NDR throughput (zero packet
loss) and PDR throughput (<0.5% packet loss). Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/kubernetes/perf/container_memif?h=rls1810>`_.

.. toctree::

    container_orchestrated-3n-hsw-x520
    container_orchestrated-3n-hsw-x710
