IPSec Crypto HW: IP4 Routed-Forwarding
======================================

Following sections include Throughput Speedup Analysis for VPP multi-
core multi-thread configurations with no Hyper-Threading, specifically
for tested 2t2c (2threads, 2cores) and 4t4c scenarios. 1t1c throughput
results are used as a reference for reported speedup ratio.
VPP IPSec encryption is accelerated using DPDK cryptodev
library driving Intel Quick Assist (QAT) crypto PCIe hardware cards.
Performance is reported for VPP running in multiple configurations of
VPP worker thread(s), a.k.a. VPP data plane thread(s), and their
physical CPU core(s) placement.

NDR Throughput
--------------

VPP NDR 64B packet throughput speedup ratio is presented in the graphs
below for 40ge2p1xl710 network interface card.

NIC 40ge2p1xl710
~~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/40ge2p1xl710-64B-ipsechw-tsa-ndrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{40ge2p1xl710-64B-ipsechw-tsa-ndrdisc}
            \label{fig:40ge2p1xl710-64B-ipsechw-tsa-ndrdisc}
    \end{figure}

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/vpp/perf/crypto && grep -E "64B-(1t1c|2t2c|4t4c)-.*ipsec.*-ndrdisc" *
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/crypto
      $ grep -E "64B-(1t1c|2t2c|4t4c)-.*ipsec.*-ndrdisc" *

*Figure 1. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
NDR Throughput for Phy-to-Phy IPSEC HW.*

PDR Throughput
--------------

VPP PDR 64B packet throughput speedup ratio is presented in the graphs
below for 40ge2p1xl710 network interface card.

NIC 40ge2p1xl710
~~~~~~~~~~~~~~~~

VPP PDR 64B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/40ge2p1xl710-64B-ipsechw-tsa-pdrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{40ge2p1xl710-64B-ipsechw-tsa-pdrdisc}
            \label{fig:40ge2p1xl710-64B-ipsechw-tsa-pdrdisc}
    \end{figure}

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/vpp/perf/crypto && grep -E "64B-(1t1c|2t2c|4t4c)-.*ipsec.*-pdrdisc" *
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/crypto
      $ grep -E "64B-(1t1c|2t2c|4t4c)-.*ipsec.*-pdrdisc" *

*Figure 2. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
PDR Throughput for Phy-to-Phy IPSEC HW.*
