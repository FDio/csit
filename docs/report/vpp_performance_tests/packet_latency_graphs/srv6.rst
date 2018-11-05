
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

SRv6 Routing
============

This section includes summary graphs of VPP Phy-to-Phy packet latency
with SRv6 measured at 100% of discovered NDR throughput
rate. Latency is reported for VPP running in multiple configurations of
VPP worker thread(s), a.k.a. VPP data plane thread(s), and their
physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/srv6?h=rls1810>`_.

.. raw:: latex

    \clearpage

3n-hsw-x520
~~~~~~~~~~~

78b-1t1c-features
-----------------

.. raw:: html

    <center><b>

:index:`Packet Latency: srv6-3n-hsw-x520-78b-1t1c-features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/srv6-3n-hsw-x520-78b-1t1c-features-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{srv6-3n-hsw-x520-78b-1t1c-features-ndr-lat}
            \label{fig:srv6-3n-hsw-x520-78b-1t1c-features-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

78b-2t2c-features
-----------------

.. raw:: html

    <center><b>

:index:`Packet Latency: srv6-3n-hsw-x520-78b-2t2c-features-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/srv6-3n-hsw-x520-78b-2t2c-features-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{srv6-3n-hsw-x520-78b-2t2c-features-ndr-lat}
            \label{fig:srv6-3n-hsw-x520-78b-2t2c-features-ndr-lat}
    \end{figure}
