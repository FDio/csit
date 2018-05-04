IPv6 Overlay Tunnels
====================

Following sections include Throughput Speedup Analysis for VPP multi-
core multi-thread configurations with no Hyper-Threading, specifically
for tested 2t2c (2threads, 2cores) and 4t4c scenarios. 1t1c throughput
results are used as a reference for reported speedup ratio.
Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

NDR Throughput
--------------

VPP NDR 64B packet throughput speedup ratio is presented in the graphs
below for 10ge2p1x520 network interface card.

NIC 10ge2p1x520
~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/10ge2p1x520-78B-ethip6-tsa-ndrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{10ge2p1x520-78B-ethip6-tsa-ndrdisc}
            \label{fig:10ge2p1x520-78B-ethip6-tsa-ndrdisc}
    \end{figure}

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/vpp/perf/ip6_tunnels && grep -E "78B-(1t1c|2t2c|4t4c)-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" *
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/ip6_tunnels
      $ grep -E "78B-(1t1c|2t2c|4t4c)-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" *

*Figure 1. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
NDR Throughput for Phy-to-Phy IPv6 Overlay Tunnels.*

PDR Throughput
--------------

VPP PDR 64B packet throughput speedup ratio is presented in the graphs
below for 10ge2p1x520 network interface card.

NIC 10ge2p1x520
~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/10ge2p1x520-78B-ethip6-tsa-pdrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{10ge2p1x520-78B-ethip6-tsa-pdrdisc}
            \label{fig:10ge2p1x520-78B-ethip6-tsa-pdrdisc}
    \end{figure}

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/vpp/perf/ip6_tunnels && grep -E "78B-(1t1c|2t2c|4t4c)-ethip6[a-z0-9]+-[a-z0-9]*-pdrdisc" *
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/ip6_tunnels
      $ grep -E "78B-(1t1c|2t2c|4t4c)-ethip6[a-z0-9]+-[a-z0-9]*-pdrdisc" *

*Figure 2. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
PDR Throughput for Phy-to-Phy IPv6 Overlay Tunnels.*
