
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
    ## 3n-dnv-x553
    ### 64b-?t?c-ip4tunnel-base-scale-ixgbe
    10ge2p1x520-ethip4vxlan-l2xcbase-ndrpdr
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-ndrpdr
    10ge2p1x520-dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan-ndrpdr
    10ge2p1x520-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan-ndrpdr

    Tests.Vpp.Perf.Ip4 Tunnels.10Ge2P1X553-Ethip4Vxlan-L2Xcbase-Ndrpdr.64B-1t1c-ethip4vxlan-l2xcbase-ndrpdr
    Tests.Vpp.Perf.Ip4 Tunnels.10Ge2P1X553-Ethip4Vxlan-L2Bdbasemaclrn-Ndrpdr.64B-1t1c-ethip4vxlan-l2bdbasemaclrn-ndrpdr
    Tests.Vpp.Perf.Ip4 Tunnels.10Ge2P1X553-Dot1Q--Ethip4Vxlan-L2Bdscale1L2Bd1Vlan1Vxlan-Ndrpdr.64B-1t1c-dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan-ndrpdr
    Tests.Vpp.Perf.Ip4 Tunnels.10Ge2P1X553-Dot1Q--Ethip4Vxlan-L2Bdscale100L2Bd100Vlan100Vxlan-Ndrpdr.64B-1t1c-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan-ndrpdr

3n-dnv-x553
~~~~~~~~~~~

64b-ip4tunnel-base-ixgbe
------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-dnv-x553-64b-ip4tunnel-base-scale-ixgbe-ndr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-dnv-x553-64b-ip4tunnel-base-scale-ixgbe-ndr-tsa}
            \label{fig:3n-dnv-x553-64b-ip4tunnel-base-scale-ixgbe-ndr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-dnv-x553-64b-ip4tunnel-base-scale-ixgbe-pdr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-dnv-x553-64b-ip4tunnel-base-scale-ixgbe-pdr-tsa}
            \label{fig:3n-dnv-x553-64b-ip4tunnel-base-scale-ixgbe-pdr-tsa}
    \end{figure}
