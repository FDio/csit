
.. raw:: latex

    \clearpage

IPv6 Routing
============

Following sections include Throughput Speedup Analysis for VPP multi-
core multi-thread configurations with no Hyper-Threading, specifically
for tested 2t2c (2threads, 2cores) and 4t4c scenarios. 1t1c throughput
results are used as a reference for reported speedup ratio. Input data
used for the graphs comes from Phy-to-Phy 78B performance tests with VPP
IPv6 Routed-Forwarding, including NDR throughput (zero packet loss) and
PDR throughput (<0.5% packet loss).

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/ip6?h=rls1807>`_.

3n-hsw-x520
~~~~~~~~~~~

78b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup: ip6-3n-hsw-x520-78b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x520-78b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x520-78b-base_and_scale-ndr-tsa}
            \label{fig:ip6-3n-hsw-x520-78b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup: ip6-3n-hsw-x520-78b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x520-78b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x520-78b-base_and_scale-pdr-tsa}
            \label{fig:ip6-3n-hsw-x520-78b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-x710
~~~~~~~~~~~

78b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup: ip6-3n-hsw-x710-78b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x710-78b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x710-78b-base_and_scale-ndr-tsa}
            \label{fig:ip6-3n-hsw-x710-78b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup: ip6-3n-hsw-x710-78b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x710-78b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x710-78b-base_and_scale-pdr-tsa}
            \label{fig:ip6-3n-hsw-x710-78b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-xl710
~~~~~~~~~~~~

78b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup: ip6-3n-hsw-xl710-78b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-xl710-78b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-xl710-78b-base_and_scale-ndr-tsa}
            \label{fig:ip6-3n-hsw-xl710-78b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup: ip6-3n-hsw-xl710-78b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-xl710-78b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-xl710-78b-base_and_scale-pdr-tsa}
            \label{fig:ip6-3n-hsw-xl710-78b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

78b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: ip6-3n-hsw-xl710-78b-1t1c-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-xl710-78b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-xl710-78b-features-ndr-tsa}
            \label{fig:ip6-3n-hsw-xl710-78b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup: ip6-3n-hsw-xl710-78b-1t1c-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-xl710-78b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-xl710-78b-features-pdr-tsa}
            \label{fig:ip6-3n-hsw-xl710-78b-features-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

3n-skx-x710
~~~~~~~~~~~

78b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup: ip6-3n-skx-x710-78b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-skx-x710-78b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-skx-x710-78b-base_and_scale-ndr-tsa}
            \label{fig:ip6-3n-skx-x710-78b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup: ip6-3n-skx-x710-78b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-skx-x710-78b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-skx-x710-78b-base_and_scale-pdr-tsa}
            \label{fig:ip6-3n-skx-x710-78b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

2n-skx-x710
~~~~~~~~~~~

78b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup: ip6-2n-skx-x710-78b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-skx-x710-78b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-skx-x710-78b-base_and_scale-ndr-tsa}
            \label{fig:ip6-2n-skx-x710-78b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup: ip6-2n-skx-x710-78b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-skx-x710-78b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-skx-x710-78b-base_and_scale-pdr-tsa}
            \label{fig:ip6-2n-skx-x710-78b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

2n-skx-xxv710
~~~~~~~~~~~~~

78b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup: ip6-2n-skx-xxv710-78b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-skx-xxv710-78b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-skx-xxv710-78b-base_and_scale-ndr-tsa}
            \label{fig:ip6-2n-skx-xxv710-78b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup: ip6-2n-skx-xxv710-78b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-skx-xxv710-78b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-skx-xxv710-78b-base_and_scale-pdr-tsa}
            \label{fig:ip6-2n-skx-xxv710-78b-base_and_scale-pdr-tsa}
    \end{figure}
