
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

3n-alt-xl710
~~~~~~~~~~~~

64b-1t1c-ip4tunnel-base
-----------------------

.. raw:: html

    <center>
    <iframe id="1" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/hdrh-lat-percentile-3n-alt-40ge2p1xl710-64b-1t1c-ethip4vxlan-l2xcbase.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{hdrh-lat-percentile-3n-alt-40ge2p1xl710-64b-1t1c-ethip4vxlan-l2xcbase}
            \label{fig:hdrh-lat-percentile-3n-alt-40ge2p1xl710-64b-1t1c-ethip4vxlan-l2xcbase}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="2" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/hdrh-lat-percentile-3n-alt-40ge2p1xl710-64b-1t1c-ethip4vxlan-l2bdbasemaclrn.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{hdrh-lat-percentile-3n-alt-40ge2p1xl710-64b-1t1c-ethip4vxlan-l2bdbasemaclrn}
            \label{fig:hdrh-lat-percentile-3n-alt-40ge2p1xl710-64b-1t1c-ethip4vxlan-l2bdbasemaclrn}
    \end{figure}
