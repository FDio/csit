VM vhost Connections
====================
Following sections include Throughput Speedup Analysis for VPP multi-
core multi-thread configurations with no Hyper-Threading, specifically
for tested 2t2c (2threads, 2cores) and 4t4c scenarios. 1t1c throughput
results are used as a reference for reported speedup ratio. Input data
used for the graphs comes from Phy-to-Phy 64B performance tests with
VM vhost-user, including NDR throughput (zero packet loss) and
PDR throughput (<0.5% packet loss).

NDR Throughput
--------------

VPP NDR 64B packet throughput speedup ratio is presented in the graphs
below for 10ge2p1x520, 10ge2p1x710 and 40ge2p1xl710 network interface cards.

NIC 10ge2p1x520
~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/10ge2p1x520-64B-vhost-sel1-tsa-ndrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{10ge2p1x520-64B-vhost-sel1-tsa-ndrdisc}
            \label{fig:10ge2p1x520-64B-vhost-sel1-tsa-ndrdisc}
    \end{figure}

*Figure 1a. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
NDR Throughput for Phy-to-Phy VM vhost-user selected TCs.*

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/10ge2p1x520-64B-vhost-sel2-tsa-ndrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{10ge2p1x520-64B-vhost-sel2-tsa-ndrdisc}
            \label{fig:10ge2p1x520-64B-vhost-sel2-tsa-ndrdisc}
    \end{figure}

*Figure 1b. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
NDR Throughput for Phy-to-Phy VM vhost-user selected TCs.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/vpp/perf/vm_vhost && grep -E "64B-(1t1c|2t2c|4t4c)-.*vhost.*-ndrdisc" 10ge2p1x520*
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/vm_vhost
      $ grep -E "64B-(1t1c|2t2c|4t4c)-.*vhost.*-ndrdisc" 10ge2p1x520*

NIC 10ge2p1x710
~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/10ge2p1x710-64B-vhost-sel2-tsa-ndrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{10ge2p1x710-64B-vhost-sel2-tsa-ndrdisc}
            \label{fig:10ge2p1x710-64B-vhost-sel2-tsa-ndrdisc}
    \end{figure}

*Figure 2. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
NDR Throughput for Phy-to-Phy VM vhost-user selected TCs.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/vpp/perf/vm_vhost && grep -E "64B-(1t1c|2t2c|4t4c)-.*vhost.*-ndrdisc" 10ge2p1x710*
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/vm_vhost
      $ grep -E "64B-(1t1c|2t2c|4t4c)-.*vhost.*-ndrdisc" 10ge2p1x710*

NIC 40ge2p1xl710
~~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/40ge2p1xl710-64B-vhost-sel1-tsa-ndrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{40ge2p1xl710-64B-vhost-sel1-tsa-ndrdisc}
            \label{fig:40ge2p1xl710-64B-vhost-sel1-tsa-ndrdisc}
    \end{figure}

*Figure 3a. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
NDR Throughput for Phy-to-Phy VM vhost-user selected TCs.*

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/40ge2p1xl710-64B-vhost-sel2-tsa-ndrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{40ge2p1xl710-64B-vhost-sel2-tsa-ndrdisc}
            \label{fig:40ge2p1xl710-64B-vhost-sel2-tsa-ndrdisc}
    \end{figure}

*Figure 3b. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
NDR Throughput for Phy-to-Phy VM vhost-user selected TCs.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/vpp/perf/vm_vhost && grep -E "64B-(1t1c|2t2c|4t4c)-.*vhost.*-ndrdisc" 40ge2p1xl710*
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/vm_vhost
      $ grep -E "64B-(1t1c|2t2c|4t4c)-.*vhost.*-ndrdisc" 40ge2p1xl710*

PDR Throughput
--------------

VPP PDR 64B packet throughput speedup ratio is presented in the graphs
below for 10ge2p1x520, 10ge2p1x710 and 40ge2p1xl710 network interface cards.

NIC 10ge2p1x520
~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/10ge2p1x520-64B-vhost-sel1-tsa-pdrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{10ge2p1x520-64B-vhost-sel1-tsa-pdrdisc}
            \label{fig:10ge2p1x520-64B-vhost-sel1-tsa-pdrdisc}
    \end{figure}

*Figure 4a. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
PDR Throughput for Phy-to-Phy VM vhost-user selected TCs.*

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/10ge2p1x520-64B-vhost-sel2-tsa-pdrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{10ge2p1x520-64B-vhost-sel2-tsa-pdrdisc}
            \label{fig:10ge2p1x520-64B-vhost-sel2-tsa-pdrdisc}
    \end{figure}

*Figure 4b. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
PDR Throughput for Phy-to-Phy VM vhost-user selected TCs.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/vpp/perf/vm_vhost && grep -E "64B-(1t1c|2t2c|4t4c)-.*vhost.*-pdrdisc" 10ge2p1x520*
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/vm_vhost
      $ grep -E "64B-(1t1c|2t2c|4t4c)-.*vhost.*-pdrdisc" 10ge2p1x520*

NIC 10ge2p1x710
~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/10ge2p1x710-64B-vhost-sel2-tsa-pdrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{10ge2p1x710-64B-vhost-sel2-tsa-pdrdisc}
            \label{fig:10ge2p1x710-64B-vhost-sel2-tsa-pdrdisc}
    \end{figure}

*Figure 5. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
PDR Throughput for Phy-to-Phy VM vhost-user selected TCs.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/vpp/perf/vm_vhost && grep -E "64B-(1t1c|2t2c|4t4c)-.*vhost.*-pdrdisc" 10ge2p1x710*
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/vm_vhost
      $ grep -E "64B-(1t1c|2t2c|4t4c)-.*vhost.*-pdrdisc" 10ge2p1x710*

NIC 40ge2p1xl710
~~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/40ge2p1xl710-64B-vhost-sel1-tsa-pdrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{40ge2p1xl710-64B-vhost-sel1-tsa-pdrdisc}
            \label{fig:40ge2p1xl710-64B-vhost-sel1-tsa-pdrdisc}
    \end{figure}

*Figure 6a. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
PDR Throughput for Phy-to-Phy VM vhost-user selected TCs.*

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/40ge2p1xl710-64B-vhost-sel2-tsa-pdrdisc.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{40ge2p1xl710-64B-vhost-sel2-tsa-pdrdisc}
            \label{fig:40ge2p1xl710-64B-vhost-sel2-tsa-pdrdisc}
    \end{figure}

*Figure 6b. Throughput Speedup Analysis - Multi-Core Speedup Ratio - Normalized
PDR Throughput for Phy-to-Phy VM vhost-user selected TCs.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../../../../ && set +x && cd tests/vpp/perf/vm_vhost && grep -E "64B-(1t1c|2t2c|4t4c)-.*vhost.*-pdrdisc" 40ge2p1xl710*
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/vm_vhost
      $ grep -E "64B-(1t1c|2t2c|4t4c)-.*vhost.*-pdrdisc" 40ge2p1xl710*
