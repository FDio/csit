
.. raw:: latex

    \clearpage

Virtual Topology System
=======================

Following sections include Throughput Speedup Analysis for VPP multi-
core multi-thread configurations with no Hyper-Threading, specifically
for tested 2t2c (2threads, 2cores) and 4t4c scenarios. 1t1c throughput
results are used as a reference for reported speedup ratio. Input data
used for the graphs comes from Phy-to-Phy 64B performance tests with
VM vhost-user, including NDR throughput (zero packet loss) and
PDR throughput (<0.5% packet loss).

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/vts?h=rls1908>`_.

.. toctree::

    vts-3n-skx-xxv710
    vts-3n-hsw-xl710
    vts-3n-tsh-x520
