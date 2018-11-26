
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
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/ip4?h=rls1810>`_.

.. raw:: latex

    \clearpage

3n-hsw-x520
~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-hsw-x520-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4-3n-hsw-x520-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-hsw-x520-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4-3n-hsw-x520-64b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-hsw-x520-64b-features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-features-ndr-tsa}
            \label{fig:ip4-3n-hsw-x520-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-hsw-x520-64b-features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm04" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-features-pdr-tsa}
            \label{fig:ip4-3n-hsw-x520-64b-features-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-features-nat44
------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-hsw-x520-64b-features-nat44-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm05" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-features-nat44-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-features-nat44-ndr-tsa}
            \label{fig:ip4-3n-hsw-x520-64b-features-nat44-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-hsw-x520-64b-features-nat44-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm06" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-features-nat44-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-features-nat44-pdr-tsa}
            \label{fig:ip4-3n-hsw-x520-64b-features-nat44-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-features-iacl
-----------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-hsw-x520-64b-features-iacl-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm07" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-features-iacl-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-features-iacl-ndr-tsa}
            \label{fig:ip4-3n-hsw-x520-64b-features-iacl-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-hsw-x520-64b-features-iacl-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm08" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-features-iacl-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-features-iacl-pdr-tsa}
            \label{fig:ip4-3n-hsw-x520-64b-features-iacl-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-features-oacl
-----------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-hsw-x520-64b-features-oacl-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm09" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-features-oacl-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-features-oacl-ndr-tsa}
            \label{fig:ip4-3n-hsw-x520-64b-features-oacl-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-hsw-x520-64b-features-oacl-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm10" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-features-oacl-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-features-oacl-pdr-tsa}
            \label{fig:ip4-3n-hsw-x520-64b-features-oacl-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-x710
~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-hsw-x710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4-3n-hsw-x710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-hsw-x710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm12" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4-3n-hsw-x710-64b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-hsw-x710-64b-features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm13" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-features-ndr-tsa}
            \label{fig:ip4-3n-hsw-x710-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-hsw-x710-64b-features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm14" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-features-pdr-tsa}
            \label{fig:ip4-3n-hsw-x710-64b-features-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-features-nat44
------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-hsw-x710-64b-features-nat44-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm15" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-features-nat44-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-features-nat44-ndr-tsa}
            \label{fig:ip4-3n-hsw-x710-64b-features-nat44-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-hsw-x710-64b-features-nat44-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm16" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-features-nat44-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-features-nat44-pdr-tsa}
            \label{fig:ip4-3n-hsw-x710-64b-features-nat44-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-features-iacl
-----------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-hsw-x710-64b-features-iacl-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm17" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-features-iacl-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-features-iacl-ndr-tsa}
            \label{fig:ip4-3n-hsw-x710-64b-features-iacl-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-hsw-x710-64b-features-iacl-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm18" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-features-iacl-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-features-iacl-pdr-tsa}
            \label{fig:ip4-3n-hsw-x710-64b-features-iacl-pdr-tsa}
    \end{figure}

..
    .. raw:: latex

        \clearpage

    64b-features-oacl
    -----------------

    .. raw:: html

        <center><b>

    :index:`Speedup Multi-core: ip4-3n-hsw-x710-64b-features-oacl-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm19" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-features-oacl-ndr-tsa.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-features-oacl-ndr-tsa}
                \label{fig:ip4-3n-hsw-x710-64b-features-oacl-ndr-tsa}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Speedup Multi-core: ip4-3n-hsw-x710-64b-features-oacl-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm20" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-features-oacl-pdr-tsa.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-features-oacl-pdr-tsa}
                \label{fig:ip4-3n-hsw-x710-64b-features-oacl-pdr-tsa}
        \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-xl710
~~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-hsw-xl710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm21" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-xl710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-xl710-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4-3n-hsw-xl710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-hsw-xl710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm22" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-xl710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-xl710-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4-3n-hsw-xl710-64b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

3n-skx-x710
~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-skx-x710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm23" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4-3n-skx-x710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-skx-x710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm24" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4-3n-skx-x710-64b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-features
------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-skx-x710-64b-features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm25" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-features-ndr-tsa}
            \label{fig:ip4-3n-skx-x710-64b-features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-skx-x710-64b-features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm26" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-features-pdr-tsa}
            \label{fig:ip4-3n-skx-x710-64b-features-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-features-nat44
------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-skx-x710-64b-features-nat44-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm27" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-features-nat44-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-features-nat44-ndr-tsa}
            \label{fig:ip4-3n-skx-x710-64b-features-nat44-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-skx-x710-64b-features-nat44-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm28" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-features-nat44-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-features-nat44-pdr-tsa}
            \label{fig:ip4-3n-skx-x710-64b-features-nat44-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-features-iacl
-----------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-skx-x710-64b-features-iacl-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm29" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-features-iacl-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-features-iacl-ndr-tsa}
            \label{fig:ip4-3n-skx-x710-64b-features-iacl-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-skx-x710-64b-features-iacl-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm30" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-features-iacl-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-features-iacl-pdr-tsa}
            \label{fig:ip4-3n-skx-x710-64b-features-iacl-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-features-nat44
------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-3n-skx-x710-64b-features-nat44-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm31" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-features-nat44-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-features-nat44-ndr-tsa}
            \label{fig:ip4-3n-skx-x710-64b-features-nat44-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-3n-skx-x710-64b-features-nat44-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm32" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-features-nat44-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-features-nat44-pdr-tsa}
            \label{fig:ip4-3n-skx-x710-64b-features-nat44-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

2n-skx-x710
~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-2n-skx-x710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm33" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-x710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-x710-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4-2n-skx-x710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-2n-skx-x710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm34" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-x710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-x710-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4-2n-skx-x710-64b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

2n-skx-xxv710
~~~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-2n-skx-xxv710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm35" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-xxv710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-xxv710-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4-2n-skx-xxv710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-2n-skx-xxv710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm36" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-xxv710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-xxv710-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4-2n-skx-xxv710-64b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

.. _speedup_graphs_ip4-2n-dnv-x553:

2n-dnv-x553
~~~~~~~~~~~

64b-base
--------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4-2n-dnv-x553-64b-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm37" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-dnv-x553-64b-base-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-dnv-x553-64b-base-ndr-tsa}
            \label{fig:ip4-2n-dnv-x553-64b-base-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4-2n-dnv-x553-64b-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm38" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-dnv-x553-64b-base-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-dnv-x553-64b-base-pdr-tsa}
            \label{fig:ip4-2n-dnv-x553-64b-base-pdr-tsa}
    \end{figure}
