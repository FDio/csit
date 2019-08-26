
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
    ### 64b-?t?c-ip4tunnel-base-scale-i40e
    10ge2p1xxv710-ethip4vxlan-l2xcbase-ndrpdr
    10ge2p1xxv710-ethip4vxlan-l2bdbasemaclrn-ndrpdr
    10ge2p1xxv710-dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan-ndrpdr
    10ge2p1xxv710-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan-ndrpdr

    Tests.Vpp.Perf.Ip4 Tunnels.25Ge2P1Xxv710-Ethip4Vxlan-L2Xcbase-Ndrpdr.64B-2t1c-ethip4vxlan-l2xcbase-ndrpdr
    Tests.Vpp.Perf.Ip4 Tunnels.25Ge2P1Xxv710-Ethip4Vxlan-L2Bdbasemaclrn-Ndrpdr.64B-2t1c-ethip4vxlan-l2bdbasemaclrn-ndrpdr
    Tests.Vpp.Perf.Ip4 Tunnels.25Ge2P1Xxv710-Dot1Q--Ethip4Vxlan-L2Bdscale1L2Bd1Vlan1Vxlan-Ndrpdr.64B-2t1c-dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan-ndrpdr
    Tests.Vpp.Perf.Ip4 Tunnels.25Ge2P1Xxv710-Dot1Q--Ethip4Vxlan-L2Bdscale100L2Bd100Vlan100Vxlan-Ndrpdr.64B-2t1c-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan-ndrpdr

3n-skx-xxv710
~~~~~~~~~~~~~

64b-2t1c-ip4tunnel-base-scale-i40e
----------------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-2t1c-ip4tunnel-base-scale-i40e-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-2t1c-ip4tunnel-base-scale-i40e-ndr}
            \label{fig:3n-skx-xxv710-64b-2t1c-ip4tunnel-base-scale-i40e-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-2t1c-ip4tunnel-base-scale-i40e-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-2t1c-ip4tunnel-base-scale-i40e-pdr}
            \label{fig:3n-skx-xxv710-64b-2t1c-ip4tunnel-base-scale-i40e-pdr}
    \end{figure}
