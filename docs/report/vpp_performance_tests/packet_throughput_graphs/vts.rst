VTS
===

Following sections include summary graphs of VPP Phy-to-VM(s)-to-Phy
performance with VM virtio and VPP vhost-user virtual interfaces,
including NDR throughput (zero packet loss) and PDR throughput (<0.5%
packet loss). Performance is reported for VPP running in multiple
configurations of VPP worker thread(s), a.k.a. VPP data plane thread(s),
and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/vts?h=rls1807>`_.

3n-hsw-x520
~~~~~~~~~~~

64b-1t1c
--------

.. raw:: html

    <center><b>

:index:`Throughput: vts-3n-hsw-x520-64b-1t1c-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vts-3n-hsw-x520-64b-1t1c-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vts-3n-hsw-x520-64b-1t1c-ndr}
            \label{fig:vts-3n-hsw-x520-64b-1t1c-ndr}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Throughput: vts-3n-hsw-x520-64b-1t1c-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vts-3n-hsw-x520-64b-1t1c-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vts-3n-hsw-x520-64b-1t1c-pdr}
            \label{fig:vts-3n-hsw-x520-64b-1t1c-pdr}
    \end{figure}

64b-2t2c
--------

.. raw:: html

    <center><b>

:index:`Throughput: vts-3n-hsw-x520-64b-2t2c-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vts-3n-hsw-x520-64b-2t2c-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vts-3n-hsw-x520-64b-2t2c-ndr}
            \label{fig:vts-3n-hsw-x520-64b-2t2c-ndr}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Throughput: vts-3n-hsw-x520-64b-2t2c-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vts-3n-hsw-x520-64b-2t2c-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vts-3n-hsw-x520-64b-2t2c-pdr}
            \label{fig:vts-3n-hsw-x520-64b-2t2c-pdr}
    \end{figure}
