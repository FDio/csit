Container Orchestrated Topologies
=================================

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
below for 10ge2p1x520 and 10ge2p1x710 network interface cards.

NIC 10ge2p1x520
~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/10ge2p1x520-64B-container-orchestrated-tsa-ndrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{10ge2p1x520-64B-container-orchestrated-tsa-ndrdisc}
            \label{fig:10ge2p1x520-64B-container-orchestrated-tsa-ndrdisc}
    \end{figure}

*Figure 1. VPP 1thread 1core - NDR Throughput for Phy-to-Phy L2 Ethernet
Switching (base).*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/kubernetes/perf/container_memif && grep -E "64B-(1t1c|2t2c|4t4c)-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*ndrdisc" 10ge2p1x520*
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/kubernetes/perf/container_memif
      $ grep -E "64B-(1t1c|2t2c|4t4c)-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*ndrdisc" 10ge2p1x520*

NIC 10ge2p1x710
~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/10ge2p1x710-64B-container-orchestrated-tsa-ndrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{10ge2p1x710-64B-container-orchestrated-tsa-ndrdisc}
            \label{fig:10ge2p1x710-64B-container-orchestrated-tsa-ndrdisc}
    \end{figure}

*Figure 2. VPP 1thread 1core - NDR Throughput for Phy-to-Phy L2 Ethernet
Switching (base).*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/kubernetes/perf/container_memif && grep -E "64B-(1t1c|2t2c|4t4c)-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*ndrdisc" 10ge2p1x710*
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/kubernetes/perf/container_memif
      $ grep -E "64B-(1t1c|2t2c|4t4c)-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*ndrdisc" 10ge2p1x710*

PDR Throughput
--------------

VPP PDR 64B packet throughput speedup ratio is presented in the graphs
below for 10ge2p1x520 and 10ge2p1x710 network interface cards.

NIC 10ge2p1x520
~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/10ge2p1x520-64B-container-orchestrated-tsa-pdrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{10ge2p1x520-64B-container-orchestrated-tsa-pdrdisc}
            \label{fig:10ge2p1x520-64B-container-orchestrated-tsa-pdrdisc}
    \end{figure}

*Figure 3. VPP 1thread 1core - NDR Throughput for Phy-to-Phy L2 Ethernet
Switching (base).*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/kubernetes/perf/container_memif && grep -E "64B-(1t1c|2t2c|4t4c)-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*pdrdisc" 10ge2p1x520*
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/kubernetes/perf/container_memif
      $ grep -E "64B-(1t1c|2t2c|4t4c)-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*pdrdisc" 10ge2p1x520*

NIC 10ge2p1x710
~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/10ge2p1x710-64B-container-orchestrated-tsa-pdrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{10ge2p1x710-64B-container-orchestrated-tsa-pdrdisc}
            \label{fig:10ge2p1x710-64B-container-orchestrated-tsa-pdrdisc}
    \end{figure}

*Figure 4. VPP 1thread 1core - NDR Throughput for Phy-to-Phy L2 Ethernet
Switching (base).*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/kubernetes/perf/container_memif && grep -E "64B-(1t1c|2t2c|4t4c)-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*pdrdisc" 10ge2p1x710*
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/kubernetes/perf/container_memif
      $ grep -E "64B-(1t1c|2t2c|4t4c)-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*pdrdisc" 10ge2p1x710*
