
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

3n-hsw-x710
~~~~~~~~~~~

78b-1t1c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: ip6-3n-hsw-x710-78b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x710-78b-1t1c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x710-78b-1t1c-base_and_scale-ndr-lat}
            \label{fig:ip6-3n-hsw-x710-78b-1t1c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

78b-2t2c-base_and_scale
-----------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: ip6-3n-hsw-x710-78b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm04" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-3n-hsw-x710-78b-2t2c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-3n-hsw-x710-78b-2t2c-base_and_scale-ndr-lat}
            \label{fig:ip6-3n-hsw-x710-78b-2t2c-base_and_scale-ndr-lat}
    \end{figure}
