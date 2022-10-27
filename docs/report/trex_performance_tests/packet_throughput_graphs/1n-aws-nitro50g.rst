
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

1n-aws-nitro50g
~~~~~~~~~~~~~~~

Following sections include summary graphs of Phy-to-Phy performance with
packet routed forwarding, including NDR throughput (zero packet loss)
and PDR throughput (<0.5% packet loss).

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/trex/perf?h=rls2210>`_.

.. raw:: latex

    \clearpage

64b-ip4routing-base-scale
-------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/1n-aws-nitro50g-64b--ip4-base-scale-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{1n-aws-nitro50g-64b--ip4-base-scale-ndr}
            \label{fig:1n-aws-nitro50g-64b--ip4-base-scale-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/1n-aws-nitro50g-64b--ip4-base-scale-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{1n-aws-nitro50g-64b--ip4-base-scale-pdr}
            \label{fig:1n-aws-nitro50g-64b--ip4-base-scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-ip6routing-base-scale
-------------------------

.. raw:: html

    <center>
    <iframe id="07" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/1n-aws-nitro50g-78b--ip6-base-scale-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{1n-aws-nitro50g-78b--ip6-base-scale-ndr}
            \label{fig:1n-aws-nitro50g-78b--ip6-base-scale-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="08" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/1n-aws-nitro50g-78b--ip6-base-scale-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{1n-aws-nitro50g-78b--ip6-base-scale-pdr}
            \label{fig:1n-aws-nitro50g-78b--ip6-base-scale-pdr}
    \end{figure}
