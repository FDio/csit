IPv6 Overlay Tunnels
====================

This section includes summary graphs of VPP Phy-to-Phy packet latency
with IPv6 Overlay Tunnels measured at 50% of discovered NDR throughput
rate. Latency is reported for VPP running in multiple configurations of
VPP worker thread(s), a.k.a. VPP data plane thread(s), and their
physical CPU core(s) placement.

VPP packet latency in 1t1c setup (1thread, 1core) is presented in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/78B-1t1c-ethip6-ndrdisc-lat50.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{78B-1t1c-ethip6-ndrdisc-lat50}
            \label{fig:78B-1t1c-ethip6-ndrdisc-lat50}
    \end{figure}

*Figure 1. VPP 1thread 1core - packet latency for Phy-to-Phy IPv6 Overlay Tunnels.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../ && set -x && cd tests/vpp/perf/ip6_tunnels && grep -E "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" *
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/ip6_tunnels
      $ grep -E "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" *

VPP packet latency in 2t2c setup (2thread, 2core) is presented in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/78B-2t2c-ethip6-ndrdisc-lat50.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{78B-2t2c-ethip6-ndrdisc-lat50}
            \label{fig:78B-2t2c-ethip6-ndrdisc-lat50}
    \end{figure}

*Figure 2. VPP 2threads 2cores - packet latency for Phy-to-Phy IPv6 Overlay Tunnels.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../ && set -x && cd tests/vpp/perf/ip6_tunnels && grep -E "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" *
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/ip6_tunnels
      $ grep -E "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" *

