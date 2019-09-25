
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
    ## 3n-skx-x710
    ### 64b-?t?c-ip4routing-base-scale-avf-i40e
    10ge2p1x710-avf-ethip4-ip4base-ndrpdr
    10ge2p1x710-avf-ethip4-ip4scale2m-ndrpdr
    10ge2p1x710-dot1q-ip4base-ndrpdr
    10ge2p1x710-ethip4-ip4base-ndrpdr
    10ge2p1x710-ethip4-ip4scale2m-ndrpdr

    Tests.Vpp.Perf.Ip4.10Ge2P1X710-Avf-Eth-Ip4Base-Ndrpdr.64B-2t1c-avf-eth-ip4base-ndrpdr
    Tests.Vpp.Perf.Ip4.10Ge2P1X710-Ethip4-Ip4Base-Ndrpdr.64B-2t1c-ethip4-ip4base-ndrpdr

3n-skx-x710
~~~~~~~~~~~

64b-2t1c-ip4routing-base-scale-avf-i40e
---------------------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-x710-64b-2t1c-ip4routing-base-scale-avf-i40e-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr}
            \label{fig:ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-x710-64b-2t1c-ip4routing-base-scale-avf-i40e-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-2t1c-base_and_scale-pdr}
            \label{fig:ip4-3n-skx-x710-64b-2t1c-base_and_scale-pdr}
    \end{figure}
