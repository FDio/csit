Container Orchestrated Topologies
=================================

This section includes summary graphs of VPP Phy-to-Phy packet latency
with CContainer Orchestrated Topologies measured at 50% of discovered NDR
throughput rate. Latency is reported for VPP running in multiple configurations
of VPP worker thread(s), a.k.a. VPP data plane thread(s), and their
physical CPU core(s) placement.

VPP packet latency in 1t1c setup (1thread, 1core) is presented in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-container-orchestrated-ndrdisc-lat50.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{64B-1t1c-container-orchestrated-ndrdisc-lat50}
            \label{fig:64B-1t1c-container-orchestrated-ndrdisc-lat50}
    \end{figure}

*Figure 1. VPP 1thread 1core - packet latency for Phy-to-Phy L2 Ethernet
Switching (base).*

CSIT source code for the test cases used for above plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/kubernetes/perf/container_memif?h=rls1804>`_.

VPP packet latency in 2t2c setup (2thread, 2core) is presented in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-container-orchestrated-ndrdisc-lat50.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{64B-2t2c-container-orchestrated-ndrdisc-lat50}
            \label{fig:64B-2t2c-container-orchestrated-ndrdisc-lat50}
    \end{figure}

*Figure 2. VPP 2threads 2cores - packet latency for Phy-to-Phy L2 Ethernet
Switching (base).*

CSIT source code for the test cases used for above plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/kubernetes/perf/container_memif?h=rls1804>`_.
