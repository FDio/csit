
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
    ### 78b-?t?c-srv6-ip6routing-base-i40e
    10ge2p1xxv710-ethip6ip6-ip6base-srv6enc1sid-ndrpdr
    10ge2p1xxv710-ethip6srhip6-ip6base-srv6enc2sids-ndrpdr
    10ge2p1xxv710-ethip6srhip6-ip6base-srv6enc2sids-nodecaps-ndrpdr
    10ge2p1xxv710-ethip6srhip6-ip6base-srv6proxy-dyn-ndrpdr
    10ge2p1xxv710-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
    10ge2p1xxv710-ethip6srhip6-ip6base-srv6proxy-stat-ndrpdr

    Tests.Vpp.Perf.Srv6.25Ge2P1Xxv710-Ethip6Ip6-Ip6Base-Srv6Enc1Sid-Ndrpdr.78B-2t1c-ethip6ip6-ip6base-srv6enc1sid-ndrpdr
    Tests.Vpp.Perf.Srv6.25Ge2P1Xxv710-Ethip6Srhip6-Ip6Base-Srv6Enc2Sids-Ndrpdr.78B-2t1c-ethip6srhip6-ip6base-srv6enc2sids-ndrpdr
    Tests.Vpp.Perf.Srv6.25Ge2P1Xxv710-Ethip6Srhip6-Ip6Base-Srv6Enc2Sids-Nodecaps-Ndrpdr.78B-2t1c-ethip6srhip6-ip6base-srv6enc2sids-nodecaps-ndrpdr
    Tests.Vpp.Perf.Srv6.25Ge2P1Xxv710-Ethip6Srhip6-Ip6Base-Srv6Proxy-Dyn-Ndrpdr.78B-2t1c-ethip6srhip6-ip6base-srv6proxy-dyn-ndrpdr
    Tests.Vpp.Perf.Srv6.25Ge2P1Xxv710-Ethip6Srhip6-Ip6Base-Srv6Proxy-Masq-Ndrpdr.78B-2t1c-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
    Tests.Vpp.Perf.Srv6.25Ge2P1Xxv710-Ethip6Srhip6-Ip6Base-Srv6Proxy-Stat-Ndrpdr.78B-2t1c-ethip6srhip6-ip6base-srv6proxy-stat-ndrpdr

3n-skx-xxv710
~~~~~~~~~~~~~

78b-2t1c-srv6-ip6routing-base-i40e
----------------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-78b-2t1c-srv6-ip6routing-base-i40e-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-78b-2t1c-srv6-ip6routing-base-i40e-ndr}
            \label{fig:3n-skx-xxv710-78b-2t1c-srv6-ip6routing-base-i40e-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-78b-2t1c-srv6-ip6routing-base-i40e-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-78b-2t1c-srv6-ip6routing-base-i40e-pdr}
            \label{fig:3n-skx-xxv710-78b-2t1c-srv6-ip6routing-base-i40e-pdr}
    \end{figure}
