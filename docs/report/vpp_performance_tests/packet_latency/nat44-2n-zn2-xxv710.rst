
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

2n-zn2-xxv710
~~~~~~~~~~~~~

64b-2t1c-ethip4udp-nat44det-avf
-------------------------------

.. raw:: html

    <center>
    <iframe id="hdrh-lat-percentile-2n-zn2-25ge2p1xxv710-64b-2t1c-avf-ethip4udp-ip4scale1000-udpsrcscale15-nat44" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/hdrh-lat-percentile-2n-zn2-25ge2p1xxv710-64b-2t1c-avf-ethip4udp-nat44det-h1024-p63-s64512.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{hdrh-lat-percentile-2n-zn2-25ge2p1xxv710-64b-2t1c-avf-ethip4udp-nat44det-h1024-p63-s64512}
            \label{fig:hdrh-lat-percentile-2n-zn2-25ge2p1xxv710-64b-2t1c-avf-ethip4udp-nat44det-h1024-p63-s64512}
    \end{figure}
