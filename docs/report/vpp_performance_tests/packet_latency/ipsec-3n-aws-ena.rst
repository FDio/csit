
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


3n-aws-ena
~~~~~~~~~~

1518b-2t1c-ipsec-ip4routing-scale-sw-ena
----------------------------------------

.. raw:: html

    <center>
    <iframe id="1" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/hdrh-lat-percentile-3n-aws-50ge1p1ena-1518b-2t1c-ethip4ipsec40tnlsw-ip4base-int-aes256gcm.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{hdrh-lat-percentile-3n-aws-50ge1p1ena-1518b-2t1c-ethip4ipsec40tnlsw-ip4base-int-aes256gcm}
            \label{fig:hdrh-lat-percentile-3n-aws-50ge1p1ena-1518b-2t1c-ethip4ipsec40tnlsw-ip4base-int-aes256gcm}
    \end{figure}
