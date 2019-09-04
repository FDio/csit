
.. raw:: latex

    \clearpage

IPSec IPv4 Routing
==================

This section includes summary graphs of VPP Phy-to-Phy packet latency
with IPSec encryption used in combination with IPv4 routed-forwarding,
with latency measured at 100% of discovered NDR throughput rate. VPP
IPSec encryption is accelerated using DPDK cryptodev library driving
Intel Quick Assist (QAT) crypto PCIe hardware cards. Latency is reported
for VPP running in multiple configurations of VPP worker thread(s),
a.k.a. VPP data plane thread(s), and their physical CPU core(s)
placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/crypto?h=rls1908>`_.

.. toctree::

    ipsec-3n-skx-xxv710
    ipsec-3n-hsw-xl710
    ipsec-3n-tsh-x520
