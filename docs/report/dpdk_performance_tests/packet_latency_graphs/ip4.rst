
.. raw:: latex

    \clearpage

.. raw:: html

    <script type="text/javascript">

        function getDocHeight(doc) {
            doc = doc || document;
            var body = doc.body, html = doc.documentElement;
            var height = Math.max( body.scrollHeight, body.offsetHeight,
                html.clientHeight, html.scrollHeight, html.offsetHeight );
            return height;
        }

        function setIframeHeight(id) {
            var ifrm = document.getElementById(id);
            var doc = ifrm.contentDocument? ifrm.contentDocument:
                ifrm.contentWindow.document;
            ifrm.style.visibility = 'hidden';
            ifrm.style.height = "10px"; // reset to minimal height ...
            // IE opt. for bing/msn needs a bit added or scrollbar appears
            ifrm.style.height = getDocHeight( doc ) + 4 + "px";
            ifrm.style.visibility = 'visible';
        }

    </script>

L3fwd
=====

This section includes summary graphs of L3FWD Phy-to-Phy performance with packet
routed forwarding measured at 100% of discovered NDR throughput rate. Latency is
reported for L3FWD running in multiple configurations of L3FWD pmd thread(s),
a.k.a. L3FWD data plane thread(s), and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/dpdk/perf?h=rls1810>`_.

.. raw:: latex

    \clearpage

3n-hsw-x520
~~~~~~~~~~~

64b-1t1c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Latency: l3fwd-3n-hsw-x520-64b-1t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/l3fwd-3n-hsw-x520-64b-1t1c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/dpdk/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l3fwd-3n-hsw-x520-64b-1t1c-base-ndr-lat}
            \label{fig:l3fwd-3n-hsw-x520-64b-1t1c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Latency: l3fwd-3n-hsw-x520-64b-2t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/l3fwd-3n-hsw-x520-64b-2t2c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/dpdk/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l3fwd-3n-hsw-x520-64b-2t2c-base-ndr-lat}
            \label{fig:l3fwd-3n-hsw-x520-64b-2t2c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-x710
~~~~~~~~~~~

64b-1t1c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Latency: l3fwd-3n-hsw-x710-64b-1t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/l3fwd-3n-hsw-x710-64b-1t1c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/dpdk/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l3fwd-3n-hsw-x710-64b-1t1c-base-ndr-lat}
            \label{fig:l3fwd-3n-hsw-x710-64b-1t1c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Latency: l3fwd-3n-hsw-x710-64b-2t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm04" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/l3fwd-3n-hsw-x710-64b-2t2c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/dpdk/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l3fwd-3n-hsw-x710-64b-2t2c-base-ndr-lat}
            \label{fig:l3fwd-3n-hsw-x710-64b-2t2c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-xl710
~~~~~~~~~~~~

64b-1t1c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Latency: l3fwd-3n-hsw-xl710-64b-1t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm05" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/l3fwd-3n-hsw-xl710-64b-1t1c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/dpdk/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l3fwd-3n-hsw-xl710-64b-1t1c-base-ndr-lat}
            \label{fig:l3fwd-3n-hsw-xl710-64b-1t1c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Latency: l3fwd-3n-hsw-xl710-64b-2t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm06" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/l3fwd-3n-hsw-xl710-64b-2t2c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/dpdk/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l3fwd-3n-hsw-xl710-64b-2t2c-base-ndr-lat}
            \label{fig:l3fwd-3n-hsw-xl710-64b-2t2c-base-ndr-lat}
    \end{figure}

..
    .. raw:: latex

        \clearpage

    3n-skx-x710
    ~~~~~~~~~~~

    64b-2t1c-base
    -------------

    .. raw:: html

        <center><b>

    :index:`Packet Latency: l3fwd-3n-skx-x710-64b-2t1c-base-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm07" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/l3fwd-3n-skx-x710-64b-2t1c-base-ndr-lat.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/dpdk/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l3fwd-3n-skx-x710-64b-2t1c-base-ndr-lat}
                \label{fig:l3fwd-3n-skx-x710-64b-2t1c-base-ndr-lat}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-4t2c-base
    -------------

    .. raw:: html

        <center><b>

    :index:`Packet Latency: l3fwd-3n-skx-x710-64b-4t2c-base-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm08" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/l3fwd-3n-skx-x710-64b-4t2c-base-ndr-lat.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/dpdk/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l3fwd-3n-skx-x710-64b-4t2c-base-ndr-lat}
                \label{fig:l3fwd-3n-skx-x710-64b-4t2c-base-ndr-lat}
        \end{figure}

    .. raw:: latex

        \clearpage

    3n-skx-xxv710
    ~~~~~~~~~~~~~

    64b-2t1c-base
    -------------

    .. raw:: html

        <center><b>

    :index:`Packet Latency: l3fwd-3n-skx-xxv710-64b-2t1c-base-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm09" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/l3fwd-3n-skx-xxv710-64b-2t1c-base-ndr-lat.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/dpdk/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l3fwd-3n-skx-xxv710-64b-2t1c-base-ndr-lat}
                \label{fig:l3fwd-3n-skx-xxv710-64b-2t1c-base-ndr-lat}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-4t2c-base
    -------------

    .. raw:: html

        <center><b>

    :index:`Packet Latency: l3fwd-3n-skx-xxv710-64b-4t2c-base-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm10" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/l3fwd-3n-skx-xxv710-64b-4t2c-base-ndr-lat.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/dpdk/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l3fwd-3n-skx-xxv710-64b-4t2c-base-ndr-lat}
                \label{fig:l3fwd-3n-skx-xxv710-64b-4t2c-base-ndr-lat}
        \end{figure}

.. raw:: latex

    \clearpage

2n-skx-x710
~~~~~~~~~~~

64b-2t1c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Latency: l3fwd-2n-skx-x710-64b-2t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/l3fwd-2n-skx-x710-64b-2t1c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/dpdk/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l3fwd-2n-skx-x710-64b-2t1c-base-ndr-lat}
            \label{fig:l3fwd-2n-skx-x710-64b-2t1c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Latency: l3fwd-2n-skx-x710-64b-4t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm12" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/l3fwd-2n-skx-x710-64b-4t2c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/dpdk/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l3fwd-2n-skx-x710-64b-4t2c-base-ndr-lat}
            \label{fig:l3fwd-2n-skx-x710-64b-4t2c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

2n-skx-xxv710
~~~~~~~~~~~~~

64b-2t1c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Latency: l3fwd-2n-skx-xxv710-64b-2t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm13" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/l3fwd-2n-skx-xxv710-64b-2t1c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/dpdk/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l3fwd-2n-skx-xxv710-64b-2t1c-base-ndr-lat}
            \label{fig:l3fwd-2n-skx-xxv710-64b-2t1c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Latency: l3fwd-2n-skx-xxv710-64b-4t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm14" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/l3fwd-2n-skx-xxv710-64b-4t2c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/dpdk/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l3fwd-2n-skx-xxv710-64b-4t2c-base-ndr-lat}
            \label{fig:l3fwd-2n-skx-xxv710-64b-4t2c-base-ndr-lat}
    \end{figure}
