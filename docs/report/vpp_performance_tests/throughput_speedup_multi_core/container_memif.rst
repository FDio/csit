
.. raw:: latex

    \clearpage

LXC/DRC Container Memif
=======================

Following sections include Throughput Speedup Analysis for VPP multi-
core multi-thread configurations with no Hyper-Threading, specifically
for tested 2t2c (2threads, 2cores) and 4t4c scenarios. 1t1c throughput
results are used as a reference for reported speedup ratio.
Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/container_memif?h=rls1901>`_.

.. toctree::

    container_memif-3n-skx-x710

..
    container_memif-3n-hsw-x520
    container_memif-3n-hsw-x710
    container_memif-3n-hsw-xl710
    container_memif-2n-skx-x710
    container_memif-2n-skx-xxv710
