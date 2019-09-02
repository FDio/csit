
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
    ## 3n-tsh-x520
    ### imix-?t?c-ipsec-ip4routing-base-scale-sw-i40e
    10ge2p1x520-ethip4ipsec4tnlsw-ip4base-int-aes256gcm-ndrpdr
    10ge2p1x520-ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha-ndrpdr
    10ge2p1x520-ethip4ipsec1000tnlsw-ip4base-int-aes256gcm-ndrpdr
    10ge2p1x520-ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha-ndrpdr
    10ge2p1x520-ethip4ipsec10000tnlsw-ip4base-int-aes256gcm-ndrpdr
    10ge2p1x520-ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha-ndrpdr

    Tests.Vpp.Perf.Crypto.10Ge2P1X520-Ethip4Ipsec4Tnlsw-Ip4Base-Int-Aes256Gcm-Ndrpdr.IMIX-1t1c-ethip4ipsec4tnlsw-ip4base-int-aes256gcm-ndrpdr
    Tests.Vpp.Perf.Crypto.10Ge2P1X520-Ethip4Ipsec4Tnlsw-Ip4Base-Int-Aes128Cbc-Hmac512Sha-Ndrpdr.IMIX-1t1c-ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha-ndrpdr
    Tests.Vpp.Perf.Crypto.10Ge2P1X520-Ethip4Ipsec1000Tnlsw-Ip4Base-Int-Aes256Gcm-Ndrpdr.IMIX-1t1c-ethip4ipsec1000tnlsw-ip4base-int-aes256gcm-ndrpdr
    Tests.Vpp.Perf.Crypto.10Ge2P1X520-Ethip4Ipsec1000Tnlsw-Ip4Base-Int-Aes128Cbc-Hmac512Sha-Ndrpdr.IMIX-1t1c-ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha-ndrpdr
    Tests.Vpp.Perf.Crypto.10Ge2P1X520-Ethip4Ipsec10000Tnlsw-Ip4Base-Int-Aes256Gcm-Ndrpdr.IMIX-1t1c-ethip4ipsec10000tnlsw-ip4base-int-aes256gcm-ndrpdr
    Tests.Vpp.Perf.Crypto.10Ge2P1X520-Ethip4Ipsec10000Tnlsw-Ip4Base-Int-Aes128Cbc-Hmac512Sha-Ndrpdr.IMIX-1t1c-ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha-ndrpdr

3n-tsh-x520
~~~~~~~~~~~

imix-1t1c-ipsec-ip4routing-base-scale-sw-i40e
---------------------------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-tsh-x520-imix-1t1c-ipsec-ip4routing-base-scale-sw-i40e-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-tsh-x520-imix-1t1c-ipsec-ip4routing-base-scale-sw-i40e-ndr}
            \label{fig:3n-tsh-x520-imix-1t1c-ipsec-ip4routing-base-scale-sw-i40e-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-tsh-x520-imix-1t1c-ipsec-ip4routing-base-scale-sw-i40e-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-tsh-x520-imix-1t1c-ipsec-ip4routing-base-scale-sw-i40e-pdr}
            \label{fig:3n-tsh-x520-imix-1t1c-ipsec-ip4routing-base-scale-sw-i40e-pdr}
    \end{figure}
