
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

3n-hsw-x520
~~~~~~~~~~~

114b-1t1c
---------

.. raw:: html

    <center><b>

:index:`Packet Latency: vts-3n-hsw-x520-114b-1t1c-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vts-3n-hsw-x520-114b-1t1c-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vts-3n-hsw-x520-114b-1t1c-ndr-lat}
            \label{fig:vts-3n-hsw-x520-114b-1t1c-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

114b-2t2c
---------

.. raw:: html

    <center><b>

:index:`Packet Latency: vts-3n-hsw-x520-114b-2t2c-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vts-3n-hsw-x520-114b-2t2c-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vts-3n-hsw-x520-114b-2t2c-ndr-lat}
            \label{fig:vts-3n-hsw-x520-114b-2t2c-ndr-lat}
    \end{figure}
