
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

3n-skx-x710
~~~~~~~~~~~

64b-2t1c-sw-int
---------------

.. raw:: html

    <center>
    <iframe id="ifrm05" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ipsec-int-3n-skx-x710-64b-2t1c-sw-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ipsec-int-3n-skx-x710-64b-2t1c-sw-ndr-lat}
            \label{fig:ipsec-int-3n-skx-x710-64b-2t1c-sw-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-sw-int
---------------

.. raw:: html

    <center>
    <iframe id="ifrm06" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ipsec-int-3n-skx-x710-64b-4t2c-sw-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ipsec-int-3n-skx-x710-64b-4t2c-sw-ndr-lat}
            \label{fig:ipsec-int-3n-skx-x710-64b-4t2c-sw-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-sw-tnl
---------------

.. raw:: html

    <center>
    <iframe id="ifrm07" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ipsec-tnl-3n-skx-x710-64b-2t1c-sw-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ipsec-tnl-3n-skx-x710-64b-2t1c-sw-ndr-lat}
            \label{fig:ipsec-tnl-3n-skx-x710-64b-2t1c-sw-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-sw-tnl
---------------

.. raw:: html

    <center>
    <iframe id="ifrm08" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ipsec-tnl-3n-skx-x710-64b-4t2c-sw-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ipsec-tnl-3n-skx-x710-64b-4t2c-sw-ndr-lat}
            \label{fig:ipsec-tnl-3n-skx-x710-64b-4t2c-sw-ndr-lat}
    \end{figure}
