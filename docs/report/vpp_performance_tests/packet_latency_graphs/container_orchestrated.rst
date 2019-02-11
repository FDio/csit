
.. raw:: latex

    \clearpage

K8s Container Memif
===================

This section includes summary graphs of VPP Phy-to-Phy packet latency
with CContainer Orchestrated Topologies measured at 100% of discovered NDR
throughput rate. Latency is reported for VPP running in multiple configurations
of VPP worker thread(s), a.k.a. VPP data plane thread(s), and their
physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/kubernetes/perf/container_memif?h=rls1901>`_.

.. toctree::

    container_orchestrated-3n-hsw-x520
    container_orchestrated-3n-hsw-x710
