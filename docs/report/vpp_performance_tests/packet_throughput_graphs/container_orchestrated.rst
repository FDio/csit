Container Orchestrated Topologies
=================================

Following sections include summary graphs of VPP Phy-to-Phy performance
with Container Orchestrated Topologies, including NDR throughput (zero packet
loss) and PDR throughput (<0.5% packet loss). Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

NDR Throughput
~~~~~~~~~~~~~~

VPP NDR 64B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-container_orchestrated-ndrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{64B-1t1c-container_orchestrated-ndrdisc}
            \label{fig:64B-1t1c-container_orchestrated-ndrdisc}
    \end{figure}

*Figure 1. VPP 1thread 1core - NDR Throughput for Phy-to-Phy L2 Ethernet
Switching (base).*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set -x && cd tests/kubernetes/perf/container_memif && grep -E "64B-1t1c-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*ndrdisc" *
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/kubernetes/perf/container_memif
      $ grep -E "64B-1t1c-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*ndrdisc" *

VPP NDR 64B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-container_orchestrated-ndrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{64B-2t2c-container_orchestrated-ndrdisc}
            \label{fig:64B-2t2c-container_orchestrated-ndrdisc}
    \end{figure}

*Figure 2. VPP 2threads 2cores - NDR Throughput for Phy-to-Phy L2 Ethernet
Switching (base).*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set -x && cd tests/kubernetes/perf/container_memif && grep -E "64B-2t2c-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*ndrdisc" *
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/kubernetes/perf/container_memif
      $ grep -E "64B-2t2c-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*ndrdisc" *


PDR Throughput
~~~~~~~~~~~~~~

VPP PDR 64B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-container_orchestrated-pdrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{64B-1t1c-container_orchestrated-pdrdisc}
            \label{fig:64B-1t1c-container_orchestrated-pdrdisc}
    \end{figure}

*Figure 3. VPP 1thread 1core - PDR Throughput for Phy-to-Phy L2 Ethernet
Switching (base).*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set -x && cd tests/kubernetes/perf/container_memif && grep -E "64B-1t1c-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*pdrdisc" *
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/kubernetes/perf/container_memif
      $ grep -E "64B-1t1c-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*pdrdisc" *

VPP PDR 64B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-container_orchestrated-pdrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{64B-2t2c-container_orchestrated-pdrdisc}
            \label{fig:64B-2t2c-container_orchestrated-pdrdisc}
    \end{figure}

*Figure 4. VPP 2thread 2core - PDR Throughput for Phy-to-Phy L2 Ethernet
Switching (base).*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set -x && cd tests/kubernetes/perf/container_memif && grep -E "64B-2t2c-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*pdrdisc" *
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/kubernetes/perf/container_memif
      $ grep -E "64B-2t2c-(eth|dot1q|dot1ad)-[1-9]drc(l2xcbase|l2bdbasemaclrn)-.*pdrdisc" *
