IPv4 Routing
============

Following sections include Throughput Speedup Analysis for VPP multi-
core multi-thread configurations with no Hyper-Threading, specifically
for tested 2t2c (2threads, 2cores) and 4t4c scenarios. 1t1c throughput
results are used as a reference for reported speedup ratio. Input data
used for the graphs comes from Phy-to-Phy 64B performance tests with VPP
IPv4 Routed-Forwarding, including NDR throughput (zero packet loss) and
PDR throughput (<0.5% packet loss).

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/ip4?h=rls1807>`_.

3n-hsw-x520
~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-hsw-x520-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4-3n-hsw-x520-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-hsw-x520-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4-3n-hsw-x520-64b-base_and_scale-pdr-tsa}
    \end{figure}

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-hsw-x520-64b-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-features-ndr-tsa}
            \label{fig:ip4-3n-hsw-x520-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-hsw-x520-64b-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-features-pdr-tsa}
            \label{fig:ip4-3n-hsw-x520-64b-features-pdr-tsa}
    \end{figure}

3n-hsw-x710
~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-hsw-x710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4-3n-hsw-x710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-hsw-x710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4-3n-hsw-x710-64b-base_and_scale-pdr-tsa}
    \end{figure}

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-hsw-x710-64b-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-features-ndr-tsa}
            \label{fig:ip4-3n-hsw-x710-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-hsw-x710-64b-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-features-pdr-tsa}
            \label{fig:ip4-3n-hsw-x710-64b-features-pdr-tsa}
    \end{figure}

3n-hsw-xl710
~~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-hsw-xl710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-xl710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-xl710-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4-3n-hsw-xl710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-hsw-xl710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-xl710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-xl710-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4-3n-hsw-xl710-64b-base_and_scale-pdr-tsa}
    \end{figure}

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-hsw-xl710-64b-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-xl710-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-xl710-64b-features-ndr-tsa}
            \label{fig:ip4-3n-hsw-xl710-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-hsw-xl710-64b-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-xl710-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-xl710-64b-features-pdr-tsa}
            \label{fig:ip4-3n-hsw-xl710-64b-features-pdr-tsa}
    \end{figure}

3n-skx-x710
~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-skx-xl710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-xl710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-xl710-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4-3n-skx-xl710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-skx-xl710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-xl710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-xl710-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4-3n-skx-xl710-64b-base_and_scale-pdr-tsa}
    \end{figure}

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-skx-xl710-64b-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-xl710-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-xl710-64b-features-ndr-tsa}
            \label{fig:ip4-3n-skx-xl710-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-skx-xl710-64b-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-xl710-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-xl710-64b-features-pdr-tsa}
            \label{fig:ip4-3n-skx-xl710-64b-features-pdr-tsa}
    \end{figure}

3n-skx-xxv710
~~~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-skx-xxv710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-xxv710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-xxv710-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4-3n-skx-xxv710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-skx-xxv710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-xxv710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-xxv710-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4-3n-skx-xxv710-64b-base_and_scale-pdr-tsa}
    \end{figure}

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-skx-xxv710-64b-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-xxv710-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-xxv710-64b-features-ndr-tsa}
            \label{fig:ip4-3n-skx-xxv710-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: ip4-3n-skx-xxv710-64b-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-xxv710-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-xxv710-64b-features-pdr-tsa}
            \label{fig:ip4-3n-skx-xxv710-64b-features-pdr-tsa}
    \end{figure}

2n-skx-x710
~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup: ip4-2n-skx-x710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-x710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-x710-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4-2n-skx-x710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: ip4-2n-skx-x710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-x710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-x710-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4-2n-skx-x710-64b-base_and_scale-pdr-tsa}
    \end{figure}

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: ip4-2n-skx-x710-64b-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-x710-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-x710-64b-features-ndr-tsa}
            \label{fig:ip4-2n-skx-x710-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: ip4-2n-skx-x710-64b-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-x710-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-x710-64b-features-pdr-tsa}
            \label{fig:ip4-2n-skx-x710-64b-features-pdr-tsa}
    \end{figure}

2n-skx-xxv710
~~~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup: ip4-2n-skx-xxv710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-xxv710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-xxv710-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4-2n-skx-xxv710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: ip4-2n-skx-xxv710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-xxv710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-xxv710-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4-2n-skx-xxv710-64b-base_and_scale-pdr-tsa}
    \end{figure}

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: ip4-2n-skx-xxv710-64b-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-xxv710-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-xxv710-64b-features-ndr-tsa}
            \label{fig:ip4-2n-skx-xxv710-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: ip4-2n-skx-xxv710-64b-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-xxv710-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-xxv710-64b-features-pdr-tsa}
            \label{fig:ip4-2n-skx-xxv710-64b-features-pdr-tsa}
    \end{figure}
