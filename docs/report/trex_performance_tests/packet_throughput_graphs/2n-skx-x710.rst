
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

2n-skx-x710
~~~~~~~~~~~

Following sections include summary graphs of Phy-to-Phy performance with
packet routed forwarding, including NDR throughput (zero packet loss)
and PDR throughput (<0.5% packet loss).

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/trex/perf?h=rls2206>`_.

.. raw:: latex

    \clearpage

64b-ip4routing-base-scale
-------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/2n-skx-x710-64b--ip4-base-scale-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-x710-64b--ip4-base-scale-ndr}
            \label{fig:2n-skx-x710-64b--ip4-base-scale-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/2n-skx-x710-64b--ip4-base-scale-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-x710-64b--ip4-base-scale-pdr}
            \label{fig:2n-skx-x710-64b--ip4-base-scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-ip4routing-[udp|tcp]-stf-cps
--------------------------------

.. raw:: html

    <center>
    <iframe id="03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/2n-skx-x710-64b--ip4routing-stf-cps-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-x710-64b--ip4routing-stf-cps-ndr}
            \label{fig:2n-skx-x710-64b--ip4routing-stf-cps-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="04" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/2n-skx-x710-64b--ip4routing-stf-cps-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-x710-64b--ip4routing-stf-cps-pdr}
            \label{fig:2n-skx-x710-64b--ip4routing-stf-cps-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-ip4routing-[udp|tcp]-stf-pps
--------------------------------

.. raw:: html

    <center>
    <iframe id="05" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/2n-skx-x710-64b--ip4routing-stf-pps-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-x710-64b--ip4routing-stf-pps-ndr}
            \label{fig:2n-skx-x710-64b--ip4routing-stf-pps-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="06" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/2n-skx-x710-64b--ip4routing-stf-pps-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-x710-64b--ip4routing-stf-pps-pdr}
            \label{fig:2n-skx-x710-64b--ip4routing-stf-pps-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-ip6routing-base-scale
-------------------------

.. raw:: html

    <center>
    <iframe id="07" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/2n-skx-x710-78b--ip6-base-scale-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-x710-78b--ip6-base-scale-ndr}
            \label{fig:2n-skx-x710-78b--ip6-base-scale-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="08" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/2n-skx-x710-78b--ip6-base-scale-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-x710-78b--ip6-base-scale-pdr}
            \label{fig:2n-skx-x710-78b--ip6-base-scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-l2switching-scale
---------------------

.. raw:: html

    <center>
    <iframe id="09" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/2n-skx-x710-64b--l2-scale-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-x710-64b--l2-scale-ndr}
            \label{fig:2n-skx-x710-64b--l2-scale-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="10" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/2n-skx-x710-64b--l2-scale-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-x710-64b--l2-scale-pdr}
            \label{fig:2n-skx-x710-64b--l2-scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage
