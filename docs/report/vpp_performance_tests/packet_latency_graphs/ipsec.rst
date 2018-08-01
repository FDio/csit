IPSec IPv4 Routing
==================

This section includes summary graphs of VPP Phy-to-Phy packet latency
with IPSec encryption used in combination with IPv4 routed-forwarding,
with latency measured at 100% of discovered NDR throughput rate. VPP
IPSec encryption is accelerated using DPDK cryptodev library driving
Intel Quick Assist (QAT) crypto PCIe hardware cards. Latency is reported
for VPP running in multiple configurations of VPP worker thread(s),
a.k.a. VPP data plane thread(s), and their physical CPU core(s)
placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/crypto?h=rls1807>`_.

3n-hsw-xl710
~~~~~~~~~~~~

64b-1t1c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Latency: ipsec-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ipsec-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ipsec-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr-lat}
            \label{fig:ipsec-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr-lat}
    \end{figure}

64b-2t2c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Latency: ipsec-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ipsec-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ipsec-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr-lat}
            \label{fig:ipsec-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr-lat}
    \end{figure}
