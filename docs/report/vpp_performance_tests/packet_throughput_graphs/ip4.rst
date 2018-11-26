
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

Following sections include summary graphs of VPP Phy-to-Phy performance
with IPv4 Routed-Forwarding, including NDR throughput (zero packet loss)
and PDR throughput (<0.5% packet loss). Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/ip4?h=rls1810>`_.

.. raw:: latex

    \clearpage

3n-hsw-x520
~~~~~~~~~~~

64b-1t1c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr}
            \label{fig:ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-1t1c-base_and_scale-pdr}
            \label{fig:ip4-3n-hsw-x520-64b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr}
            \label{fig:ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm04" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-2t2c-base_and_scale-pdr}
            \label{fig:ip4-3n-hsw-x520-64b-2t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-features
-----------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-1t1c-features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm05" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-1t1c-features-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-1t1c-features-ndr}
            \label{fig:ip4-3n-hsw-x520-64b-1t1c-features-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-1t1c-features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm06" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-1t1c-features-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-1t1c-features-pdr}
            \label{fig:ip4-3n-hsw-x520-64b-1t1c-features-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-features
-----------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-2t2c-features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm07" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-2t2c-features-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-2t2c-features-ndr}
            \label{fig:ip4-3n-hsw-x520-64b-2t2c-features-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-2t2c-features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm08" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-2t2c-features-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-2t2c-features-pdr}
            \label{fig:ip4-3n-hsw-x520-64b-2t2c-base_and_scale-features}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-features-nat44
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-1t1c-features-nat44-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm09" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-1t1c-features-nat44-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-1t1c-features-nat44-ndr}
            \label{fig:ip4-3n-hsw-x520-64b-1t1c-features-nat44-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-1t1c-features-nat44-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm10" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-1t1c-features-nat44-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-1t1c-features-nat44-pdr}
            \label{fig:ip4-3n-hsw-x520-64b-1t1c-features-nat44-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-features-nat44
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-2t2c-features-nat44-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-2t2c-features-nat44-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-2t2c-features-nat44-ndr}
            \label{fig:ip4-3n-hsw-x520-64b-2t2c-features-nat44-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-2t2c-features-nat44-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm12" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-2t2c-features-nat44-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-2t2c-features-nat44-pdr}
            \label{fig:ip4-3n-hsw-x520-64b-2t2c-base_and_scale-features-nat44}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-features-iacl
----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-1t1c-features-iacl-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm13" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-1t1c-features-iacl-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-1t1c-features-iacl-ndr}
            \label{fig:ip4-3n-hsw-x520-64b-1t1c-features-iacl-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-1t1c-features-iacl-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm14" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-1t1c-features-iacl-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-1t1c-features-iacl-pdr}
            \label{fig:ip4-3n-hsw-x520-64b-1t1c-features-iacl-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-features-iacl
----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-2t2c-features-iacl-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm15" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-2t2c-features-iacl-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-2t2c-features-iacl-ndr}
            \label{fig:ip4-3n-hsw-x520-64b-2t2c-features-iacl-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-2t2c-features-iacl-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm16" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-2t2c-features-iacl-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-2t2c-features-iacl-pdr}
            \label{fig:ip4-3n-hsw-x520-64b-2t2c-base_and_scale-features-iacl}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-features-oacl
----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-1t1c-features-oacl-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm17" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-1t1c-features-oacl-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-1t1c-features-oacl-ndr}
            \label{fig:ip4-3n-hsw-x520-64b-1t1c-features-oacl-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-1t1c-features-oacl-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm18" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-1t1c-features-oacl-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-1t1c-features-oacl-pdr}
            \label{fig:ip4-3n-hsw-x520-64b-1t1c-features-oacl-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-features-oacl
----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-2t2c-features-oacl-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm19" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-2t2c-features-oacl-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-2t2c-features-oacl-ndr}
            \label{fig:ip4-3n-hsw-x520-64b-2t2c-features-oacl-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x520-64b-2t2c-features-oacl-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm20" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x520-64b-2t2c-features-oacl-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x520-64b-2t2c-features-oacl-pdr}
            \label{fig:ip4-3n-hsw-x520-64b-2t2c-base_and_scale-features-oacl}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-x710
~~~~~~~~~~~

64b-1t1c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm21" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr}
            \label{fig:ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm22" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-1t1c-base_and_scale-pdr}
            \label{fig:ip4-3n-hsw-x710-64b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm23" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr}
            \label{fig:ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm24" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-2t2c-base_and_scale-pdr}
            \label{fig:ip4-3n-hsw-x710-64b-2t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-features
-----------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-1t1c-features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm25" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-1t1c-features-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-1t1c-features-ndr}
            \label{fig:ip4-3n-hsw-x710-64b-1t1c-features-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-1t1c-features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm26" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-1t1c-features-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-1t1c-features-pdr}
            \label{fig:ip4-3n-hsw-x710-64b-1t1c-features-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-features
-----------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-2t2c-features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm27" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-2t2c-features-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-2t2c-features-ndr}
            \label{fig:ip4-3n-hsw-x710-64b-2t2c-features-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-2t2c-features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm28" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-2t2c-features-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-2t2c-features-pdr}
            \label{fig:ip4-3n-hsw-x710-64b-2t2c-base_and_scale-features}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-features-nat44
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-1t1c-features-nat44-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm29" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-1t1c-features-nat44-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-1t1c-features-nat44-ndr}
            \label{fig:ip4-3n-hsw-x710-64b-1t1c-features-nat44-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-1t1c-features-nat44-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm30" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-1t1c-features-nat44-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-1t1c-features-nat44-pdr}
            \label{fig:ip4-3n-hsw-x710-64b-1t1c-features-nat44-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-features-nat44
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-2t2c-features-nat44-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm31" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-2t2c-features-nat44-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-2t2c-features-nat44-ndr}
            \label{fig:ip4-3n-hsw-x710-64b-2t2c-features-nat44-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-2t2c-features-nat44-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm32" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-2t2c-features-nat44-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-2t2c-features-nat44-pdr}
            \label{fig:ip4-3n-hsw-x710-64b-2t2c-base_and_scale-features-nat44}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-features-iacl
----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-1t1c-features-iacl-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm33" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-1t1c-features-iacl-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-1t1c-features-iacl-ndr}
            \label{fig:ip4-3n-hsw-x710-64b-1t1c-features-iacl-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-1t1c-features-iacl-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm34" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-1t1c-features-iacl-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-1t1c-features-iacl-pdr}
            \label{fig:ip4-3n-hsw-x710-64b-1t1c-features-iacl-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-features-iacl
----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-2t2c-features-iacl-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm35" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-2t2c-features-iacl-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-2t2c-features-iacl-ndr}
            \label{fig:ip4-3n-hsw-x710-64b-2t2c-features-iacl-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-x710-64b-2t2c-features-iacl-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm36" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-2t2c-features-iacl-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-2t2c-features-iacl-pdr}
            \label{fig:ip4-3n-hsw-x710-64b-2t2c-base_and_scale-features-iacl}
    \end{figure}

..
    .. raw:: latex

        \clearpage

    64b-1t1c-features-oacl
    ----------------------

    .. raw:: html

        <center><b>

    :index:`Packet Throughput: ip4-3n-hsw-x710-64b-1t1c-features-oacl-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm37" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-1t1c-features-oacl-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-1t1c-features-oacl-ndr}
                \label{fig:ip4-3n-hsw-x710-64b-1t1c-features-oacl-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Packet Throughput: ip4-3n-hsw-x710-64b-1t1c-features-oacl-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm38" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-1t1c-features-oacl-pdr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-1t1c-features-oacl-pdr}
                \label{fig:ip4-3n-hsw-x710-64b-1t1c-features-oacl-pdr}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-2t2c-features-oacl
    ----------------------

    .. raw:: html

        <center><b>

    :index:`Packet Throughput: ip4-3n-hsw-x710-64b-2t2c-features-oacl-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm39" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-2t2c-features-oacl-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-2t2c-features-oacl-ndr}
                \label{fig:ip4-3n-hsw-x710-64b-2t2c-features-oacl-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Packet Throughput: ip4-3n-hsw-x710-64b-2t2c-features-oacl-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm40" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-x710-64b-2t2c-features-oacl-pdr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-x710-64b-2t2c-features-oacl-pdr}
                \label{fig:ip4-3n-hsw-x710-64b-2t2c-base_and_scale-features-oacl}
        \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-xl710
~~~~~~~~~~~~

64b-1t1c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm41" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr}
            \label{fig:ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm42" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr}
            \label{fig:ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm43" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr}
            \label{fig:ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm44" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr}
            \label{fig:ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

3n-skx-x710
~~~~~~~~~~~

64b-2t1c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm45" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr}
            \label{fig:ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-skx-x710-64b-2t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm46" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-2t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-2t1c-base_and_scale-pdr}
            \label{fig:ip4-3n-skx-x710-64b-2t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-skx-x710-64b-4t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm47" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-4t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-4t2c-base_and_scale-ndr}
            \label{fig:ip4-3n-skx-x710-64b-4t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-skx-x710-64b-4t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm48" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-4t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-4t2c-base_and_scale-pdr}
            \label{fig:ip4-3n-skx-x710-64b-4t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-features
-----------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-skx-x710-64b-2t1c-features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm49" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-2t1c-features-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-2t1c-features-ndr}
            \label{fig:ip4-3n-skx-x710-64b-2t1c-features-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-skx-x710-64b-2t1c-features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm50" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-2t1c-features-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-2t1c-features-pdr}
            \label{fig:ip4-3n-skx-x710-64b-2t1c-features-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-features
-----------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-skx-x710-64b-4t2c-features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm51" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-4t2c-features-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-4t2c-features-ndr}
            \label{fig:ip4-3n-skx-x710-64b-4t2c-features-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-skx-x710-64b-4t2c-features-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm52" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-4t2c-features-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-4t2c-features-pdr}
            \label{fig:ip4-3n-skx-x710-64b-4t2c-base_and_scale-features}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-features-nat44
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-skx-x710-64b-2t1c-features-nat44-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm53" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-2t1c-features-nat44-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-2t1c-features-nat44-ndr}
            \label{fig:ip4-3n-skx-x710-64b-2t1c-features-nat44-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-skx-x710-64b-2t1c-features-nat44-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm54" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-2t1c-features-nat44-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-2t1c-features-nat44-pdr}
            \label{fig:ip4-3n-skx-x710-64b-2t1c-features-nat44-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-features-nat44
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-skx-x710-64b-4t2c-features-nat44-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm55" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-4t2c-features-nat44-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-4t2c-features-nat44-ndr}
            \label{fig:ip4-3n-skx-x710-64b-4t2c-features-nat44-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-skx-x710-64b-4t2c-features-nat44-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm56" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-4t2c-features-nat44-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-4t2c-features-nat44-pdr}
            \label{fig:ip4-3n-skx-x710-64b-4t2c-base_and_scale-features-nat44}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-features-iacl
----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-skx-x710-64b-2t1c-features-iacl-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm57" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-2t1c-features-iacl-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-2t1c-features-iacl-ndr}
            \label{fig:ip4-3n-skx-x710-64b-2t1c-features-iacl-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-skx-x710-64b-2t1c-features-iacl-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm58" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-2t1c-features-iacl-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-2t1c-features-iacl-pdr}
            \label{fig:ip4-3n-skx-x710-64b-2t1c-features-iacl-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-features-iacl
----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-3n-skx-x710-64b-4t2c-features-iacl-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm59" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-4t2c-features-iacl-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-4t2c-features-iacl-ndr}
            \label{fig:ip4-3n-skx-x710-64b-4t2c-features-iacl-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-3n-skx-x710-64b-4t2c-features-iacl-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm60" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-4t2c-features-iacl-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-4t2c-features-iacl-pdr}
            \label{fig:ip4-3n-skx-x710-64b-4t2c-base_and_scale-features-iacl}
    \end{figure}

..
    .. raw:: latex

        \clearpage

    64b-2t1c-features-oacl
    ----------------------

    .. raw:: html

        <center><b>

    :index:`Packet Throughput: ip4-3n-skx-x710-64b-2t1c-features-oacl-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm61" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-2t1c-features-oacl-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-2t1c-features-oacl-ndr}
                \label{fig:ip4-3n-skx-x710-64b-2t1c-features-oacl-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Packet Throughput: ip4-3n-skx-x710-64b-2t1c-features-oacl-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm62" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-2t1c-features-oacl-pdr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-2t1c-features-oacl-pdr}
                \label{fig:ip4-3n-skx-x710-64b-2t1c-features-oacl-pdr}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-4t2c-features-oacl
    ----------------------

    .. raw:: html

        <center><b>

    :index:`Packet Throughput: ip4-3n-skx-x710-64b-4t2c-features-oacl-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm63" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-4t2c-features-oacl-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-4t2c-features-oacl-ndr}
                \label{fig:ip4-3n-skx-x710-64b-4t2c-features-oacl-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Packet Throughput: ip4-3n-skx-x710-64b-4t2c-features-oacl-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm64" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-4t2c-features-oacl-pdr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-4t2c-features-oacl-pdr}
                \label{fig:ip4-3n-skx-x710-64b-4t2c-base_and_scale-features-oacl}
        \end{figure}

.. raw:: latex

    \clearpage

2n-skx-x710
~~~~~~~~~~~

64b-2t1c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-2n-skx-x710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm65" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-x710-64b-2t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-x710-64b-2t1c-base_and_scale-ndr}
            \label{fig:ip4-2n-skx-x710-64b-2t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-2n-skx-x710-64b-2t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm66" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-x710-64b-2t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-x710-64b-2t1c-base_and_scale-pdr}
            \label{fig:ip4-2n-skx-x710-64b-2t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-2n-skx-x710-64b-4t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm67" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-x710-64b-4t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-x710-64b-4t2c-base_and_scale-ndr}
            \label{fig:ip4-2n-skx-x710-64b-4t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-2n-skx-x710-64b-4t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm68" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-x710-64b-4t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-x710-64b-4t2c-base_and_scale-pdr}
            \label{fig:ip4-2n-skx-x710-64b-4t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

2n-skx-xxv710
~~~~~~~~~~~~~

64b-2t1c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm69" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr}
            \label{fig:ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm70" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-pdr}
            \label{fig:ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm71" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-ndr}
            \label{fig:ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm72" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-pdr}
            \label{fig:ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

.. _packet_throughput_graphs_ip4-2n-dnv-x553:

2n-dnv-x553
~~~~~~~~~~~

64b-1t1c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-2n-dnv-x553-64b-1t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm73" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-dnv-x553-64b-1t1c-base-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-dnv-x553-64b-1t1c-base-ndr}
            \label{fig:ip4-2n-dnv-x553-64b-1t1c-base-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-2n-dnv-x553-64b-1t1c-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm74" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-dnv-x553-64b-1t1c-base-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-dnv-x553-64b-1t1c-base-pdr}
            \label{fig:ip4-2n-dnv-x553-64b-1t1c-base-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: ip4-2n-dnv-x553-64b-2t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm75" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-dnv-x553-64b-2t2c-base-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-dnv-x553-64b-2t2c-base-ndr}
            \label{fig:ip4-2n-dnv-x553-64b-2t2c-base-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: ip4-2n-dnv-x553-64b-2t2c-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm76" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-2n-dnv-x553-64b-2t2c-base-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-2n-dnv-x553-64b-2t2c-base-pdr}
            \label{fig:ip4-2n-dnv-x553-64b-2t2c-base-pdr}
    \end{figure}
