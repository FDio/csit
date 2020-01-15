
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

..
    ## 3n-skx-xxv710
    ### 64b-?t?c-ip4routing-base-scale-avf
    10ge2p1xxv710-avf-eth-ip4base-ndrpdr
    10ge2p1xxv710-avf-ethip4-ip4scale20k-ndrpdr
    10ge2p1xxv710-avf-ethip4-ip4scale200k-ndrpdr
    10ge2p1xxv710-avf-ethip4-ip4scale2m-ndrpdr

    ### 64b-?t?c-ip4routing-base-scale-i40e
    10ge2p1xxv710-dot1q-ip4base-ndrpdr
    10ge2p1xxv710-ethip4-ip4base-ndrpdr
    10ge2p1xxv710-ethip4-ip4scale20k-ndrpdr
    10ge2p1xxv710-ethip4-ip4scale200k-ndrpdr
    10ge2p1xxv710-ethip4-ip4scale2m-ndrpdr

    ### 64b-?t?c-features-ip4routing-base-i40e
    10ge2p1xxv710-ethip4-ip4base-ndrpdr
    10ge2p1xxv710-ethip4udp-ip4base-iacl50sf-10kflows-ndrpdr
    10ge2p1xxv710-ethip4udp-ip4base-iacl50sl-10kflows-ndrpdr
    10ge2p1xxv710-ethip4udp-ip4base-oacl50sf-10kflows-ndrpdr
    10ge2p1xxv710-ethip4udp-ip4base-oacl50sl-10kflows-ndrpdr
    10ge2p1xxv710-ethip4udp-ip4base-nat44-ndrpdr

3n-skx-xxv710
~~~~~~~~~~~~~

64b-2t1c-ip4routing-base-scale-avf
----------------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-2t1c-ip4routing-base-scale-avf-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-2t1c-ip4routing-base-scale-avf-ndr-hdrh-lat-percentile}
            \label{fig:3n-skx-xxv710-64b-2t1c-ip4routing-base-scale-avf-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-ip4routing-base-scale-avf
----------------------------------

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-4t2c-ip4routing-base-scale-avf-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-4t2c-ip4routing-base-scale-avf-ndr-hdrh-lat-percentile}
            \label{fig:3n-skx-xxv710-64b-4t2c-ip4routing-base-scale-avf-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

64b-8t4c-ip4routing-base-scale-avf
----------------------------------

.. raw:: html

    <center>
    <iframe id="03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-8t4c-ip4routing-base-scale-avf-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-8t4c-ip4routing-base-scale-avf-ndr-hdrh-lat-percentile}
            \label{fig:3n-skx-xxv710-64b-8t4c-ip4routing-base-scale-avf-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-ip4routing-base-scale-i40e
-----------------------------------

.. raw:: html

    <center>
    <iframe id="11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-2t1c-ip4routing-base-scale-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-2t1c-ip4routing-base-scale-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-skx-xxv710-64b-2t1c-ip4routing-base-scale-i40e-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-ip4routing-base-scale-i40e
-----------------------------------

.. raw:: html

    <center>
    <iframe id="12" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-4t2c-ip4routing-base-scale-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-4t2c-ip4routing-base-scale-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-skx-xxv710-64b-4t2c-ip4routing-base-scale-i40e-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

64b-8t4c-ip4routing-base-scale-i40e
-----------------------------------

.. raw:: html

    <center>
    <iframe id="13" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-8t4c-ip4routing-base-scale-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-8t4c-ip4routing-base-scale-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-skx-xxv710-64b-8t4c-ip4routing-base-scale-i40e-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-features-ip4routing-base-i40e
--------------------------------------

.. raw:: html

    <center>
    <iframe id="21" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-2t1c-features-ip4routing-base-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-2t1c-features-ip4routing-base-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-skx-xxv710-64b-2t1c-features-ip4routing-base-i40e-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-features-ip4routing-base-i40e
--------------------------------------

.. raw:: html

    <center>
    <iframe id="22" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-2t1c-features-ip4routing-base-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-2t1c-features-ip4routing-base-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-skx-xxv710-64b-2t1c-features-ip4routing-base-i40e-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

64b-8t4c-features-ip4routing-base-i40e
--------------------------------------

.. raw:: html

    <center>
    <iframe id="23" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-8t4c-features-ip4routing-base-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-8t4c-features-ip4routing-base-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-skx-xxv710-64b-8t4c-features-ip4routing-base-i40e-ndr-hdrh-lat-percentile}
    \end{figure}
