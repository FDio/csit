
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

1n-aws-ena
~~~~~~~~~~

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/trex/perf?h=rls2210>`_.

.. raw:: latex

    \clearpage

64b-ip4routing-base-scale
-------------------------

.. raw:: html

    <center>
    <iframe id="hdrh-lat-percentile-1n-aws-50ge1P1ena-64b--ethip4-ip4base-tg" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/hdrh-lat-percentile-1n-aws-50ge1P1ena-64b--ethip4-ip4base-tg.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{hdrh-lat-percentile-1n-aws-50ge1P1ena-64b--ethip4-ip4base-tg}
            \label{fig:hdrh-lat-percentile-1n-aws-50ge1P1ena-64b--ethip4-ip4base-tg}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="hdrh-lat-percentile-1n-aws-50ge1P1ena-64b--ethip4-ip4scale2m-tg" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/hdrh-lat-percentile-1n-aws-50ge1P1ena-64b--ethip4-ip4scale2m-tg.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{hdrh-lat-percentile-1n-aws-50ge1P1ena-64b--ethip4-ip4scale2m-tg}
            \label{fig:hdrh-lat-percentile-1n-aws-50ge1P1ena-64b--ethip4-ip4scale2m-tg}
    \end{figure}

.. raw:: latex

    \clearpage

78b-ip6routing-base-scale
-------------------------

.. raw:: html

    <center>
    <iframe id="hdrh-lat-percentile-1n-aws-50ge1P1ena-78b--ethip6-ip6base-tg" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/hdrh-lat-percentile-1n-aws-50ge1P1ena-78b--ethip6-ip6base-tg.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{hdrh-lat-percentile-1n-aws-50ge1P1ena-78b--ethip6-ip6base-tg}
            \label{fig:hdrh-lat-percentile-1n-aws-50ge1P1ena-78b--ethip6-ip6base-tg}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="hdrh-lat-percentile-1n-aws-50ge1P1ena-78b--ethip6-ip6scale2m-tg" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/trex/hdrh-lat-percentile-1n-aws-50ge1P1ena-78b--ethip6-ip6scale2m-tg.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/trex/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{hdrh-lat-percentile-1n-aws-50ge1P1ena-78b--ethip6-ip6scale2m-tg}
            \label{fig:hdrh-lat-percentile-1n-aws-50ge1P1ena-78b--ethip6-ip6scale2m-tg}
    \end{figure}
