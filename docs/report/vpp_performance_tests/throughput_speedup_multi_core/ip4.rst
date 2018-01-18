IPv4 Routed-Forwarding
======================

Following sections include Throughput Speedup Analysis - Multi-Core Speedup
Ratio for 1t1c (1thread, 1core), 2t2c and 4t4c setup. The input data used for
graphs is VPP Phy-to-Phy performance with IPv4 Routed-Forwarding, including NDR
throughput (zero packet loss) and PDR throughput (<0.5% packet loss).
The speedup factor is the normalized throughput to throughput for 64B on 1 core,
showed as 1.

NDR Throughput
--------------

VPP NDR 64B packet throughput speedup is presented in the graphs below for
10ge2p1x520 and 40ge2p1xl710 network interface controllers.

NIC 10ge2p1x520
~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/10ge2p1x520-64B-ip4-tsa-ndrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{10ge2p1x520-64B-ip4-tsa-ndrdisc}
            \label{fig:10ge2p1x520-64B-ip4-tsa-ndrdisc}
    \end{figure}

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/vpp/perf/ip4 && grep -E '64B-(1t1c|2t2c|4t4c)-ethip4-ip4(base|scale[a-z0-9]*)*-ndrdisc' 10ge2p1x520*
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/ip4
      $ grep -E '64B-(1t1c|2t2c|4t4c)-ethip4-ip4(base|scale[a-z0-9]*)*-ndrdisc' 10ge2p1x520*

*Figure 1. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
NDR Throughput for Phy-to-Phy IPv4 Routed-Forwarding used.*

NIC 40ge2p1xl710
~~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/40ge2p1xl710-64B-ip4-tsa-ndrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{40ge2p1xl710-64B-ip4-tsa-ndrdisc}
            \label{fig:40ge2p1xl710-64B-ip4-tsa-ndrdisc}
    \end{figure}

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/vpp/perf/ip4 && grep -P '64B-(1t1c|2t2c|4t4c)-ethip4-ip4(base|scale[a-z0-9]*)*-ndrdisc' 40ge2p1xl710*
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/ip4
      $ grep -P '64B-(1t1c|2t2c|4t4c)-ethip4-ip4(base|scale[a-z0-9]*)*-ndrdisc' 40ge2p1xl710*

*Figure 2. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
NDR Throughput for Phy-to-Phy IPv4 Routed-Forwarding used.*

PDR Throughput
--------------

VPP NDR 64B packet throughput speedup is presented in the graphs below for
10ge2p1x520 and 40ge2p1xl710 network interface controllers. PDR measured for
0.5% packet loss ratio.

NIC 10ge2p1x520
~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/10ge2p1x520-64B-ip4-tsa-pdrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{10ge2p1x520-64B-ip4-tsa-pdrdisc}
            \label{fig:10ge2p1x520-64B-ip4-tsa-pdrdisc}
    \end{figure}

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/vpp/perf/ip4 && grep -E '64B-(1t1c|2t2c|4t4c)-ethip4-ip4(base|scale[a-z0-9]*)*-ndrdisc' 10ge2p1x520*
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/ip4
      $ grep -E '64B-(1t1c|2t2c|4t4c)-ethip4-ip4(base|scale[a-z0-9]*)*-ndrdisc' 10ge2p1x520*

*Figure 3. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
PDR Throughput for Phy-to-Phy IPv4 Routed-Forwarding used.*
