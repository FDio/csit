LXC/DRC Container Memif
=======================

Following sections include Throughput Speedup Analysis for VPP multi-
core multi-thread configurations with no Hyper-Threading, specifically
for tested 2t2c (2threads, 2cores) and 4t4c scenarios. 1t1c throughput
results are used as a reference for reported speedup ratio.
Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/container_memif?h=rls1807>`_.

3n-hsw-x520
~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-hsw-x520-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-hsw-x520-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-hsw-x520-64b-base_and_scale-ndr-tsa}
            \label{fig:memif-3n-hsw-x520-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-hsw-x520-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-hsw-x520-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-hsw-x520-64b-base_and_scale-pdr-tsa}
            \label{fig:memif-3n-hsw-x520-64b-base_and_scale-pdr-tsa}
    \end{figure}

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-hsw-x520-64b-1t1c-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-hsw-x520-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-hsw-x520-64b-features-ndr-tsa}
            \label{fig:memif-3n-hsw-x520-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-hsw-x520-64b-1t1c-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-hsw-x520-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-hsw-x520-64b-features-pdr-tsa}
            \label{fig:memif-3n-hsw-x520-64b-features-pdr-tsa}
    \end{figure}

3n-hsw-x710
~~~~~~~~~~~

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-hsw-x710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-hsw-x710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-hsw-x710-64b-base_and_scale-ndr-tsa}
            \label{fig:memif-3n-hsw-x710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-hsw-x710-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-hsw-x710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-hsw-x710-64b-base_and_scale-pdr-tsa}
            \label{fig:memif-3n-hsw-x710-64b-base_and_scale-pdr-tsa}
    \end{figure}

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-hsw-x710-64b-1t1c-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-hsw-x710-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-hsw-x710-64b-features-ndr-tsa}
            \label{fig:memif-3n-hsw-x710-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-hsw-x710-64b-1t1c-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-hsw-x710-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-hsw-x710-64b-features-pdr-tsa}
            \label{fig:memif-3n-hsw-x710-64b-features-pdr-tsa}
    \end{figure}

3n-hsw-xl710
~~~~~~~~~~~~

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-hsw-xl710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-hsw-xl710-64b-base_and_scale-ndr-tsa}
            \label{fig:memif-3n-hsw-xl710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-hsw-xl710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-hsw-xl710-64b-base_and_scale-pdr-tsa}
            \label{fig:memif-3n-hsw-xl710-64b-base_and_scale-pdr-tsa}
    \end{figure}

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-hsw-xl710-64b-1t1c-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-hsw-xl710-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-hsw-xl710-64b-features-ndr-tsa}
            \label{fig:memif-3n-hsw-xl710-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-hsw-xl710-64b-1t1c-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-hsw-xl710-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-hsw-xl710-64b-features-pdr-tsa}
            \label{fig:memif-3n-hsw-xl710-64b-features-pdr-tsa}
    \end{figure}

3n-skx-x710
~~~~~~~~~~~

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-skx-xl710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-skx-xl710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-skx-xl710-64b-base_and_scale-ndr-tsa}
            \label{fig:memif-3n-skx-xl710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-skx-xl710-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-skx-xl710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-skx-xl710-64b-base_and_scale-pdr-tsa}
            \label{fig:memif-3n-skx-xl710-64b-base_and_scale-pdr-tsa}
    \end{figure}

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-skx-xl710-64b-1t1c-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-skx-xl710-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-skx-xl710-64b-features-ndr-tsa}
            \label{fig:memif-3n-skx-xl710-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-skx-xl710-64b-1t1c-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-skx-xl710-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-skx-xl710-64b-features-pdr-tsa}
            \label{fig:memif-3n-skx-xl710-64b-features-pdr-tsa}
    \end{figure}

3n-skx-xxv710
~~~~~~~~~~~~~

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-skx-xxv710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-skx-xxv710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-skx-xxv710-64b-base_and_scale-ndr-tsa}
            \label{fig:memif-3n-skx-xxv710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-skx-xxv710-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-skx-xxv710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-skx-xxv710-64b-base_and_scale-pdr-tsa}
            \label{fig:memif-3n-skx-xxv710-64b-base_and_scale-pdr-tsa}
    \end{figure}

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-skx-xxv710-64b-1t1c-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-skx-xxv710-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-skx-xxv710-64b-features-ndr-tsa}
            \label{fig:memif-3n-skx-xxv710-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: memif-3n-skx-xxv710-64b-1t1c-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-skx-xxv710-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-3n-skx-xxv710-64b-features-pdr-tsa}
            \label{fig:memif-3n-skx-xxv710-64b-features-pdr-tsa}
    \end{figure}

2n-skx-x710
~~~~~~~~~~~

.. raw:: html

    <center><b>

:index:`Speedup: memif-2n-skx-x710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-2n-skx-x710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-2n-skx-x710-64b-base_and_scale-ndr-tsa}
            \label{fig:memif-2n-skx-x710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: memif-2n-skx-x710-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-2n-skx-x710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-2n-skx-x710-64b-base_and_scale-pdr-tsa}
            \label{fig:memif-2n-skx-x710-64b-base_and_scale-pdr-tsa}
    \end{figure}

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: memif-2n-skx-x710-64b-1t1c-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-2n-skx-x710-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-2n-skx-x710-64b-features-ndr-tsa}
            \label{fig:memif-2n-skx-x710-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: memif-2n-skx-x710-64b-1t1c-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-2n-skx-x710-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-2n-skx-x710-64b-features-pdr-tsa}
            \label{fig:memif-2n-skx-x710-64b-features-pdr-tsa}
    \end{figure}

2n-skx-xxv710
~~~~~~~~~~~~~

.. raw:: html

    <center><b>

:index:`Speedup: memif-2n-skx-xxv710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-2n-skx-xxv710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-2n-skx-xxv710-64b-base_and_scale-ndr-tsa}
            \label{fig:memif-2n-skx-xxv710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: memif-2n-skx-xxv710-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-2n-skx-xxv710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-2n-skx-xxv710-64b-base_and_scale-pdr-tsa}
            \label{fig:memif-2n-skx-xxv710-64b-base_and_scale-pdr-tsa}
    \end{figure}

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup: memif-2n-skx-xxv710-64b-1t1c-features-ndr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-2n-skx-xxv710-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-2n-skx-xxv710-64b-features-ndr-tsa}
            \label{fig:memif-2n-skx-xxv710-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

:index:`Speedup: memif-2n-skx-xxv710-64b-1t1c-features-pdr`

.. raw:: html

    </b>
    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/memif-2n-skx-xxv710-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{memif-2n-skx-xxv710-64b-features-pdr-tsa}
            \label{fig:memif-2n-skx-xxv710-64b-features-pdr-tsa}
    \end{figure}
