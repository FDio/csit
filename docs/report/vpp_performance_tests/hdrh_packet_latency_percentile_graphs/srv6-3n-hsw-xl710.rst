
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
    ### 78b-?t?c-srv6-ip6routing-base-i40e
    10ge2p1xl710-ethip6ip6-ip6base-srv6enc1sid-ndrpdr
    10ge2p1xl710-ethip6srhip6-ip6base-srv6enc2sids-ndrpdr
    10ge2p1xl710-ethip6srhip6-ip6base-srv6enc2sids-nodecaps-ndrpdr
    10ge2p1xl710-ethip6srhip6-ip6base-srv6proxy-dyn-ndrpdr
    10ge2p1xl710-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr
    10ge2p1xl710-ethip6srhip6-ip6base-srv6proxy-stat-ndrpdr

3n-hsw-xl710
~~~~~~~~~~~~

78b-1t1c-srv6-ip6routing-base-i40e
----------------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-78b-1t1c-srv6-ip6routing-base-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-78b-1t1c-srv6-ip6routing-base-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-hsw-xl710-78b-1t1c-srv6-ip6routing-base-i40e-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

78b-2t2c-srv6-ip6routing-base-i40e
----------------------------------

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-78b-2t2c-srv6-ip6routing-base-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-78b-2t2c-srv6-ip6routing-base-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-hsw-xl710-78b-2t2c-srv6-ip6routing-base-i40e-ndr-hdrh-lat-percentile}
    \end{figure}

.. raw:: latex

    \clearpage

78b-4t4c-srv6-ip6routing-base-i40e
----------------------------------

.. raw:: html

    <center>
    <iframe id="03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-78b-4t4c-srv6-ip6routing-base-i40e-ndr-hdrh-lat-percentile.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-78b-4t4c-srv6-ip6routing-base-i40e-ndr-hdrh-lat-percentile}
            \label{fig:3n-hsw-xl710-78b-4t4c-srv6-ip6routing-base-i40e-ndr-hdrh-lat-percentile}
    \end{figure}
