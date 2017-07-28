IPSec Crypto HW: IP4 Routed-Forwarding
======================================

This section includes summary graphs of VPP Phy-to-Phy packet latency
with IPSec encryption used in combination with IPv4 routed-forwarding,
with latency measured at 50% of discovered NDR throughput rate. VPP
IPSec encryption is accelerated using DPDK cryptodev library driving
Intel Quick Assist (QAT) crypto PCIe hardware cards. Latency is reported
for VPP running in multiple configurations of VPP worker thread(s),
a.k.a. VPP data plane thread(s), and their physical CPU core(s)
placement.

VPP packet latency in 1t1c setup (1thread, 1core) is presented in the graph
below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-ipsechw-ndrdisc-lat50.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{64B-1t1c-ipsechw-ndrdisc-lat50}
            \label{fig:64B-1t1c-ipsechw-ndrdisc-lat50}
    \end{figure}

*Figure 1. VPP 1thread 1core - packet latency for Phy-to-Phy IPSec HW with IPv4 Routed-Forwarding.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../ && set -x && cd tests/vpp/perf/crypto && grep -E "64B-1t1c-.*ipsec.*-ndrdisc" *
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/crypto
      $ grep -E "64B-1t1c-.*ipsec.*-ndrdisc" *

VPP packet latency in 2t2c setup (2thread, 2core) is presented in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-ipsechw-ndrdisc-lat50.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{64B-2t2c-ipsechw-ndrdisc-lat50}
            \label{fig:64B-2t2c-ipsechw-ndrdisc-lat50}
    \end{figure}

*Figure 2. VPP 2threads 2cores - packet latency for Phy-to-Phy IPSec HW with IPv4 Routed-Forwarding.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../ && set -x && cd tests/vpp/perf/crypto && grep -E "64B-2t2c-.*ipsec.*-ndrdisc" *
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/crypto
      $ grep -E "64B-2t2c-.*ipsec.*-ndrdisc" *
