
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

IPv6 Routing
============

Following sections include summary graphs of VPP Phy-to-Phy performance
with IPv6 Routed-Forwarding, including NDR throughput (zero packet loss)
and PDR throughput (<0.5% packet loss). Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/ip6?h=rls1810>`_.

.. raw:: latex

    \clearpage

3n-hsw-x520
~~~~~~~~~~~

78b-1t1c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-3n-hsw-x520-78b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x520-78b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x520-78b-1t1c-base_and_scale-ndr}
            \label{fig:ip6-3n-hsw-x520-78b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-3n-hsw-x520-78b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x520-78b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x520-78b-1t1c-base_and_scale-pdr}
            \label{fig:ip6-3n-hsw-x520-78b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-2t2c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-3n-hsw-x520-78b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x520-78b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x520-78b-2t2c-base_and_scale-ndr}
            \label{fig:ip6-3n-hsw-x520-78b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-3n-hsw-x520-78b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm04" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x520-78b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x520-78b-2t2c-base_and_scale-pdr}
            \label{fig:ip6-3n-hsw-x520-78b-2t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-1t1c-base_and_features
--------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-3n-hsw-x520-78b-1t1c-base_and_features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm05" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x520-78b-1t1c-base_and_features-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x520-78b-1t1c-base_and_features-ndr}
            \label{fig:ip6-3n-hsw-x520-78b-1t1c-base_and_features-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-3n-hsw-x520-78b-1t1c-base_and_features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm06" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x520-78b-1t1c-base_and_features-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x520-78b-1t1c-base_and_features-pdr}
            \label{fig:ip6-3n-hsw-x520-78b-1t1c-base_and_features-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-2t2c-base_and_features
--------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-3n-hsw-x520-78b-2t2c-base_and_features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm07" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x520-78b-2t2c-base_and_features-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x520-78b-2t2c-base_and_features-ndr}
            \label{fig:ip6-3n-hsw-x520-78b-2t2c-base_and_features-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-3n-hsw-x520-78b-2t2c-base_and_features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm08" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x520-78b-2t2c-base_and_features-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x520-78b-2t2c-base_and_features-pdr}
            \label{fig:ip6-3n-hsw-x520-78b-2t2c-base_and_features-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-x710
~~~~~~~~~~~

78b-1t1c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-3n-hsw-x710-78b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm09" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x710-78b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x710-78b-1t1c-base_and_scale-ndr}
            \label{fig:ip6-3n-hsw-x710-78b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-3n-hsw-x710-78b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm10" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x710-78b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x710-78b-1t1c-base_and_scale-pdr}
            \label{fig:ip6-3n-hsw-x710-78b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-2t2c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-3n-hsw-x710-78b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x710-78b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x710-78b-2t2c-base_and_scale-ndr}
            \label{fig:ip6-3n-hsw-x710-78b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-3n-hsw-x710-78b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm12" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x710-78b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x710-78b-2t2c-base_and_scale-pdr}
            \label{fig:ip6-3n-hsw-x710-78b-2t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-1t1c-base_and_features
--------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-3n-hsw-x710-78b-1t1c-base_and_features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm13" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x710-78b-1t1c-base_and_features-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x710-78b-1t1c-base_and_features-ndr}
            \label{fig:ip6-3n-hsw-x710-78b-1t1c-base_and_features-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-3n-hsw-x710-78b-1t1c-base_and_features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm14" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x710-78b-1t1c-base_and_features-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x710-78b-1t1c-base_and_features-pdr}
            \label{fig:ip6-3n-hsw-x710-78b-1t1c-base_and_features-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-2t2c-base_and_features
--------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-3n-hsw-x710-78b-2t2c-base_and_features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm15" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x710-78b-2t2c-base_and_features-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x710-78b-2t2c-base_and_features-ndr}
            \label{fig:ip6-3n-hsw-x710-78b-2t2c-base_and_features-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-3n-hsw-x710-78b-2t2c-base_and_features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm16" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x710-78b-2t2c-base_and_features-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x710-78b-2t2c-base_and_features-pdr}
            \label{fig:ip6-3n-hsw-x710-78b-2t2c-base_and_features-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-xl710
~~~~~~~~~~~~

78b-1t1c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-3n-hsw-xl710-78b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm17" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-xl710-78b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-xl710-78b-1t1c-base_and_scale-ndr}
            \label{fig:ip6-3n-hsw-xl710-78b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-3n-hsw-xl710-78b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm18" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-xl710-78b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-xl710-78b-1t1c-base_and_scale-pdr}
            \label{fig:ip6-3n-hsw-xl710-78b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-2t2c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-3n-hsw-xl710-78b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm19" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-xl710-78b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-xl710-78b-2t2c-base_and_scale-ndr}
            \label{fig:ip6-3n-hsw-xl710-78b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-3n-hsw-xl710-78b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm20" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-xl710-78b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-xl710-78b-2t2c-base_and_scale-pdr}
            \label{fig:ip6-3n-hsw-xl710-78b-2t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

3n-skx-x710
~~~~~~~~~~~

78b-2t1c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-3n-skx-x710-78b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm21" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-skx-x710-78b-2t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-skx-x710-78b-2t1c-base_and_scale-ndr}
            \label{fig:ip6-3n-skx-x710-78b-2t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-3n-skx-x710-78b-2t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm22" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-skx-x710-78b-2t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-skx-x710-78b-2t1c-base_and_scale-pdr}
            \label{fig:ip6-3n-skx-x710-78b-2t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-4t2c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-3n-skx-x710-78b-4t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm23" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-skx-x710-78b-4t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-skx-x710-78b-4t2c-base_and_scale-ndr}
            \label{fig:ip6-3n-skx-x710-78b-4t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-3n-skx-x710-78b-4t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm24" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-skx-x710-78b-4t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-skx-x710-78b-4t2c-base_and_scale-pdr}
            \label{fig:ip6-3n-skx-x710-78b-4t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-2t1c-base_and_features
--------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-3n-skx-x710-78b-2t1c-base_and_features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm25" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-skx-x710-78b-2t1c-base_and_features-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-skx-x710-78b-2t1c-base_and_features-ndr}
            \label{fig:ip6-3n-skx-x710-78b-2t1c-base_and_features-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-3n-skx-x710-78b-2t1c-base_and_features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm26" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-skx-x710-78b-2t1c-base_and_features-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-skx-x710-78b-2t1c-base_and_features-pdr}
            \label{fig:ip6-3n-skx-x710-78b-2t1c-base_and_features-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-4t2c-base_and_features
--------------------------

..
    .. raw:: html

        <center><b>

    :index:`Packet Throughput: ip6-3n-skx-x710-78b-4t2c-base_and_features-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm27" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-skx-x710-78b-4t2c-base_and_features-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-skx-x710-78b-4t2c-base_and_features-ndr}
                \label{fig:ip6-3n-skx-x710-78b-4t2c-base_and_features-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

:index:`Packet Throughput: ip6-3n-skx-x710-78b-4t2c-base_and_features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm28" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-skx-x710-78b-4t2c-base_and_features-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-skx-x710-78b-4t2c-base_and_features-pdr}
            \label{fig:ip6-3n-skx-x710-78b-4t2c-base_and_features-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

2n-skx-x710
~~~~~~~~~~~

78b-2t1c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-2n-skx-x710-78b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm29" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-skx-x710-78b-2t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-skx-x710-78b-2t1c-base_and_scale-ndr}
            \label{fig:ip6-2n-skx-x710-78b-2t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-2n-skx-x710-78b-2t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm30" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-skx-x710-78b-2t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-skx-x710-78b-2t1c-base_and_scale-pdr}
            \label{fig:ip6-2n-skx-x710-78b-2t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-4t2c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-2n-skx-x710-78b-4t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm31" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-skx-x710-78b-4t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-skx-x710-78b-4t2c-base_and_scale-ndr}
            \label{fig:ip6-2n-skx-x710-78b-4t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-2n-skx-x710-78b-4t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm32" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-skx-x710-78b-4t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-skx-x710-78b-4t2c-base_and_scale-pdr}
            \label{fig:ip6-2n-skx-x710-78b-4t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

2n-skx-xxv710
~~~~~~~~~~~~~

78b-2t1c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-2n-skx-xxv710-78b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm33" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-skx-xxv710-78b-2t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-skx-xxv710-78b-2t1c-base_and_scale-ndr}
            \label{fig:ip6-2n-skx-xxv710-78b-2t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-2n-skx-xxv710-78b-2t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm34" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-skx-xxv710-78b-2t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-skx-xxv710-78b-2t1c-base_and_scale-pdr}
            \label{fig:ip6-2n-skx-xxv710-78b-2t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-4t2c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-2n-skx-xxv710-78b-4t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm35" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-skx-xxv710-78b-4t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-skx-xxv710-78b-4t2c-base_and_scale-ndr}
            \label{fig:ip6-2n-skx-xxv710-78b-4t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-2n-skx-xxv710-78b-4t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm36" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-skx-xxv710-78b-4t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-skx-xxv710-78b-4t2c-base_and_scale-pdr}
            \label{fig:ip6-2n-skx-xxv710-78b-4t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

.. _packet_throughput_graphs_ip6-2n-dnv-x553:

2n-dnv-x553
~~~~~~~~~~~

78b-1t1c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-2n-dnv-x553-78b-1t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm37" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-dnv-x553-78b-1t1c-base-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-dnv-x553-78b-1t1c-base-ndr}
            \label{fig:ip6-2n-dnv-x553-78b-1t1c-base-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-2n-dnv-x553-78b-1t1c-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm38" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-dnv-x553-78b-1t1c-base-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-dnv-x553-78b-1t1c-base-pdr}
            \label{fig:ip6-2n-dnv-x553-78b-1t1c-base-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-2t2c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip6-2n-dnv-x553-78b-2t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm39" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-dnv-x553-78b-2t2c-base-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-dnv-x553-78b-2t2c-base-ndr}
            \label{fig:ip6-2n-dnv-x553-78b-2t2c-base-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip6-2n-dnv-x553-78b-2t2c-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm40" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-dnv-x553-78b-2t2c-base-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-dnv-x553-78b-2t2c-base-pdr}
            \label{fig:ip6-2n-dnv-x553-78b-2t2c-base-pdr}
    \end{figure}
