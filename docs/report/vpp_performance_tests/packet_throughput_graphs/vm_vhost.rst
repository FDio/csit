
.. raw:: latex

    \clearpage

KVM VMs vhost-user
==================

Following sections include summary graphs of VPP Phy-to-VM(s)-to-Phy
performance with VM virtio and VPP vhost-user virtual interfaces,
including NDR throughput (zero packet loss) and PDR throughput (<0.5%
packet loss). Performance is reported for VPP running in multiple
configurations of VPP worker thread(s), a.k.a. VPP data plane thread(s),
and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/vm_vhost?h=rls1807>`_.

3n-hsw-x520
~~~~~~~~~~~

64b-1t1c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Throughput: vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-ndr}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Throughput: vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-pdr}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Throughput: vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-ndr}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Throughput: vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-pdr}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Throughput: vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr}
            \label{fig:vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Throughput: vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-pdr}
            \label{fig:vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Throughput: vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr}
            \label{fig:vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Throughput: vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-pdr}
            \label{fig:vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-x710
~~~~~~~~~~~

64b-1t1c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Throughput: vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-ndr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Throughput: vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-pdr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Throughput: vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-ndr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Throughput: vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-pdr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Throughput: vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr}
            \label{fig:vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Throughput: vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-pdr}
            \label{fig:vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Throughput: vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr}
            \label{fig:vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Throughput: vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-pdr}
            \label{fig:vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-xl710
~~~~~~~~~~~~

64b-1t1c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Throughput: vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr}
            \label{fig:vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Throughput: vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr}
            \label{fig:vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Throughput: vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr}
            \label{fig:vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Throughput: vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr}
            \label{fig:vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Throughput: vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr}
            \label{fig:vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Throughput: vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr}
            \label{fig:vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Throughput: vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr}
            \label{fig:vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Throughput: vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr}
            \label{fig:vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr}
    \end{figure}
