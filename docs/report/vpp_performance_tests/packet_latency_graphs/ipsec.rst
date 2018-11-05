
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

IPSec IPv4 Routing
==================

This section includes summary graphs of VPP Phy-to-Phy packet latency
with IPSec encryption used in combination with IPv4 routed-forwarding,
with latency measured at 100% of discovered NDR throughput rate. VPP
IPSec encryption is accelerated using DPDK cryptodev library driving
Intel Quick Assist (QAT) crypto PCIe hardware cards. Latency is reported
for VPP running in multiple configurations of VPP worker thread(s),
a.k.a. VPP data plane thread(s), and their physical CPU core(s)
placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/crypto?h=rls1810>`_.

.. raw:: latex

    \clearpage

3n-hsw-xl710
~~~~~~~~~~~~

64b-1t1c-base
--------------

.. raw:: html

    <center><b>

:index:`Packet Latency: ipsec-3n-hsw-xl710-64b-1t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ipsec-3n-hsw-xl710-64b-1t1c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ipsec-3n-hsw-xl710-64b-1t1c-base-ndr-lat}
            \label{fig:ipsec-3n-hsw-xl710-64b-1t1c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base
-------------

.. raw:: html

    <center><b>

:index:`Packet Latency: ipsec-3n-hsw-xl710-64b-2t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ipsec-3n-hsw-xl710-64b-2t2c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ipsec-3n-hsw-xl710-64b-2t2c-base-ndr-lat}
            \label{fig:ipsec-3n-hsw-xl710-64b-2t2c-base-ndr-lat}
    \end{figure}

3n-hsw-xl710
~~~~~~~~~~~~

64b-1t1c-scale
--------------

.. raw:: html

    <center><b>

:index:`Packet Latency: ipsec-3n-hsw-xl710-64b-1t1c-scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ipsec-3n-hsw-xl710-64b-1t1c-scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ipsec-3n-hsw-xl710-64b-1t1c-scale-ndr-lat}
            \label{fig:ipsec-3n-hsw-xl710-64b-1t1c-scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-scale
--------------

.. raw:: html

    <center><b>

:index:`Packet Latency: ipsec-3n-hsw-xl710-64b-2t2c-scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm04" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ipsec-3n-hsw-xl710-64b-2t2c-scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ipsec-3n-hsw-xl710-64b-2t2c-scale-ndr-lat}
            \label{fig:ipsec-3n-hsw-xl710-64b-2t2c-scale-ndr-lat}
    \end{figure}

3n-hsw-xl710
~~~~~~~~~~~~

64b-1t1c-sw
-----------

.. raw:: html

    <center><b>

:index:`Packet Latency: ipsec-3n-hsw-xl710-64b-1t1c-sw-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm05" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ipsec-3n-hsw-xl710-64b-1t1c-sw-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ipsec-3n-hsw-xl710-64b-1t1c-sw-ndr-lat}
            \label{fig:ipsec-3n-hsw-xl710-64b-1t1c-sw-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-sw
-----------

.. raw:: html

    <center><b>

:index:`Packet Latency: ipsec-3n-hsw-xl710-64b-2t2c-sw-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm06" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ipsec-3n-hsw-xl710-64b-2t2c-sw-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ipsec-3n-hsw-xl710-64b-2t2c-sw-ndr-lat}
            \label{fig:ipsec-3n-hsw-xl710-64b-2t2c-sw-ndr-lat}
    \end{figure}
