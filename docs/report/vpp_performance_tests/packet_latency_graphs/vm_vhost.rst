VM vhost Connections
====================

This section includes summary graphs of VPP Phy-to-VM(s)-to-Phy packet
latency with with VM virtio and VPP vhost-user virtual interfaces
measured at 50% of discovered NDR throughput rate. Latency is reported
for VPP running in multiple configurations of VPP worker thread(s),
a.k.a. VPP data plane thread(s), and their physical CPU core(s)
placement.

VPP packet latency in 1t1c setup (1thread, 1core) is presented in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-vhost-sel1-ndrdisc-lat50.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{64B-1t1c-vhost-sel1-ndrdisc-lat50}
            \label{fig:64B-1t1c-vhost-sel1-ndrdisc-lat50}
    \end{figure}

*Figure 1a. VPP 1thread 1core - packet latency for Phy-to-VM-to-Phy VM
vhost-user selected TCs (ipv4).*

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-vhost-sel2-ndrdisc-lat50.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{64B-1t1c-vhost-sel2-ndrdisc-lat50}
            \label{fig:64B-1t1c-vhost-sel2-ndrdisc-lat50}
    \end{figure}

*Figure 1b. VPP 1thread 1core - packet latency for Phy-to-VM-to-Phy VM
vhost-user selected TCs (l2).*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../ && set -x && cd tests/vpp/perf/vm_vhost && grep -E "64B-1t1c-.*vhost.*-ndrdisc" *
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/vm_vhost
      $ grep -E "64B-1t1c-.*vhost.*-ndrdisc" *

VPP packet latency in 2t2c setup (2thread, 2core) is presented in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-vhost-sel1-ndrdisc-lat50.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{64B-2t2c-vhost-sel1-ndrdisc-lat50}
            \label{fig:64B-2t2c-vhost-sel1-ndrdisc-lat50}
    \end{figure}

*Figure 2a. VPP 2threads 2cores - packet latency for Phy-to-VM-to-Phy VM
vhost-user selected TCs (ipv4).*

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-vhost-sel2-ndrdisc-lat50.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{64B-2t2c-vhost-sel2-ndrdisc-lat50}
            \label{fig:64B-2t2c-vhost-sel2-ndrdisc-lat50}
    \end{figure}

*Figure 2b. VPP 2threads 2cores - packet latency for Phy-to-VM-to-Phy VM
vhost-user selected TCs (l2).*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. only:: html

   .. program-output:: cd ../../ && set -x && cd tests/vpp/perf/vm_vhost && grep -E "64B-2t2c-.*vhost.*-ndrdisc" *
      :shell:

.. only:: latex

   .. code-block:: bash

      $ cd tests/vpp/perf/vm_vhost
      $ grep -E "64B-2t2c-.*vhost.*-ndrdisc" *
