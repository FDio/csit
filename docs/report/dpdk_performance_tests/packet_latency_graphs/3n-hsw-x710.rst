
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

This section includes summary graphs of Phy-to-Phy performance with packet
routed forwarding measured at 100% of discovered NDR throughput rate.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/dpdk/perf?h=rls1908>`_.

.. raw:: latex

    \clearpage

64b-1t1c-base
-------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/3n-hsw-x710-64b-1t1c-base-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/dpdk/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-x710-64b-1t1c-base-ndr-lat}
            \label{fig:3n-hsw-x710-64b-1t1c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base
-------------

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/3n-hsw-x710-64b-2t2c-base-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/dpdk/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-x710-64b-2t2c-base-ndr-lat}
            \label{fig:3n-hsw-x710-64b-2t2c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t4c-base
-------------

.. raw:: html

    <center>
    <iframe id="03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/dpdk/3n-hsw-x710-64b-4t4c-base-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/dpdk/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-x710-64b-4t4c-base-ndr-lat}
            \label{fig:3n-hsw-x710-64b-4t4c-base-ndr-lat}
    \end{figure}
