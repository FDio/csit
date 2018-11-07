
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

IPv4 Tunnels
============

Following sections include Throughput Speedup Analysis for VPP multi-
core multi-thread configurations with no Hyper-Threading, specifically
for tested 2t2c (2threads, 2cores) and 4t4c scenarios. 1t1c throughput
results are used as a reference for reported speedup ratio.
Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/ip4_tunnels?h=rls1810>`_.

.. raw:: latex

    \clearpage

3n-hsw-x520
~~~~~~~~~~~

..
    64b-base_and_scale
    ------------------

    .. raw:: html

        <center><b>

    :index:`Speedup Multi-core: ip4tun-3n-hsw-x520-64b-base_and_scale-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4tun-3n-hsw-x520-64b-base_and_scale-ndr-tsa.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4tun-3n-hsw-x520-64b-base_and_scale-ndr-tsa}
                \label{fig:ip4tun-3n-hsw-x520-64b-base_and_scale-ndr-tsa}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Speedup Multi-core: ip4tun-3n-hsw-x520-64b-base_and_scale-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4tun-3n-hsw-x520-64b-base_and_scale-pdr-tsa.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4tun-3n-hsw-x520-64b-base_and_scale-pdr-tsa}
                \label{fig:ip4tun-3n-hsw-x520-64b-base_and_scale-pdr-tsa}
        \end{figure}

    .. raw:: latex

        \clearpage

64b-base_and_features
---------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4tun-3n-hsw-x520-64b-base_and_features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4tun-3n-hsw-x520-64b-base_and_features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4tun-3n-hsw-x520-64b-base_and_features-ndr-tsa}
            \label{fig:ip4tun-3n-hsw-x520-64b-base_and_features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4tun-3n-hsw-x520-64b-base_and_features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm04" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4tun-3n-hsw-x520-64b-base_and_features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4tun-3n-hsw-x520-64b-base_and_features-pdr-tsa}
            \label{fig:ip4tun-3n-hsw-x520-64b-base_and_features-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-x710
~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4tun-3n-hsw-x710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm05" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4tun-3n-hsw-x710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4tun-3n-hsw-x710-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4tun-3n-hsw-x710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4tun-3n-hsw-x710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm06" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4tun-3n-hsw-x710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4tun-3n-hsw-x710-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4tun-3n-hsw-x710-64b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-base_and_features
---------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4tun-3n-hsw-x710-64b-base_and_features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm07" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4tun-3n-hsw-x710-64b-base_and_features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4tun-3n-hsw-x710-64b-base_and_features-ndr-tsa}
            \label{fig:ip4tun-3n-hsw-x710-64b-base_and_features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4tun-3n-hsw-x710-64b-base_and_features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm08" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4tun-3n-hsw-x710-64b-base_and_features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4tun-3n-hsw-x710-64b-base_and_features-pdr-tsa}
            \label{fig:ip4tun-3n-hsw-x710-64b-base_and_features-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

3n-skx-x710
~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4tun-3n-skx-x710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm09" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4tun-3n-skx-x710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4tun-3n-skx-x710-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4tun-3n-skx-x710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4tun-3n-skx-x710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm10" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4tun-3n-skx-x710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4tun-3n-skx-x710-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4tun-3n-skx-x710-64b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-base_and_features
---------------------

.. raw:: html

    <center><b>

:index:`Speedup Multi-core: ip4tun-3n-skx-x710-64b-base_and_features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4tun-3n-skx-x710-64b-base_and_features-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4tun-3n-skx-x710-64b-base_and_features-ndr-tsa}
            \label{fig:ip4tun-3n-skx-x710-64b-base_and_features-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup Multi-core: ip4tun-3n-skx-x710-64b-base_and_features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm12" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4tun-3n-skx-x710-64b-base_and_features-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4tun-3n-skx-x710-64b-base_and_features-pdr-tsa}
            \label{fig:ip4tun-3n-skx-x710-64b-base_and_features-pdr-tsa}
    \end{figure}
