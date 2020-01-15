
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
    ## 3n-hsw-xl710
    ### imix-?t?c-ipsec-ip4routing-base-scale-sw-i40e
    10ge2p1xl710-ethip4ipsec4tnlsw-ip4base-int-aes256gcm-ndrpdr
    10ge2p1xl710-ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha-ndrpdr
    10ge2p1xl710-ethip4ipsec1000tnlsw-ip4base-int-aes256gcm-ndrpdr
    10ge2p1xl710-ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha-ndrpdr
    10ge2p1xl710-ethip4ipsec10000tnlsw-ip4base-int-aes256gcm-ndrpdr
    10ge2p1xl710-ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha-ndrpdr

    ### imix-?t?c-ipsec-ip4routing-base-scale-hw-i40e
    10ge2p1xl710-ethip4ipsec1tnlhw-ip4base-int-aes256gcm-ndrpdr
    10ge2p1xl710-ethip4ipsec1tnlhw-ip4base-int-aes128cbc-hmac512sha-ndrpdr
    10ge2p1xl710-ethip4ipsec1000tnlhw-ip4base-int-aes256gcm-ndrpdr
    10ge2p1xl710-ethip4ipsec1000tnlhw-ip4base-int-aes128cbc-hmac512sha-ndrpdr

3n-hsw-xl710
~~~~~~~~~~~~

imix-1t1c-ipsec-ip4routing-base-scale-sw-i40e
---------------------------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-imix-1t1c-ipsec-ip4routing-base-scale-sw-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-imix-1t1c-ipsec-ip4routing-base-scale-sw-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-hsw-xl710-imix-1t1c-ipsec-ip4routing-base-scale-sw-i40e-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

imix-2t2c-ipsec-ip4routing-base-scale-sw-i40e
---------------------------------------------

.. raw:: html

    <center>
    <iframe id="02 onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-imix-2t2c-ipsec-ip4routing-base-scale-sw-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-imix-2t2c-ipsec-ip4routing-base-scale-sw-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-hsw-xl710-imix-2t2c-ipsec-ip4routing-base-scale-sw-i40e-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

imix-4t4c-ipsec-ip4routing-base-scale-sw-i40e
---------------------------------------------

.. raw:: html

    <center>
    <iframe id="03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-imix-4t4c-ipsec-ip4routing-base-scale-sw-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-imix-4t4c-ipsec-ip4routing-base-scale-sw-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-hsw-xl710-imix-4t4c-ipsec-ip4routing-base-scale-sw-i40e-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

imix-1t1c-ipsec-ip4routing-base-scale-hw-i40e
---------------------------------------------

.. raw:: html

    <center>
    <iframe id="11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-imix-1t1c-ipsec-ip4routing-base-scale-hw-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-imix-1t1c-ipsec-ip4routing-base-scale-hw-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-hsw-xl710-imix-1t1c-ipsec-ip4routing-base-scale-hw-i40e-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

imix-2t2c-ipsec-ip4routing-base-scale-hw-i40e
---------------------------------------------

.. raw:: html

    <center>
    <iframe id="21" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-imix-2t2c-ipsec-ip4routing-base-scale-hw-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-imix-2t2c-ipsec-ip4routing-base-scale-hw-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-hsw-xl710-imix-2t2c-ipsec-ip4routing-base-scale-hw-i40e-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

imix-4t4c-ipsec-ip4routing-base-scale-hw-i40e
---------------------------------------------

.. raw:: html

    <center>
    <iframe id="22" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-imix-4t4c-ipsec-ip4routing-base-scale-hw-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-imix-4t4c-ipsec-ip4routing-base-scale-hw-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-hsw-xl710-imix-4t4c-ipsec-ip4routing-base-scale-hw-i40e-ndr-hdrh-lat-percentile}
    \end{figure}
