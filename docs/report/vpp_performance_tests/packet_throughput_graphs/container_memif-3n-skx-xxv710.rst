
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
    ### 64b-?t?c-memif-base-i40e
    10ge2p1xxv710-eth-l2xcbase-eth-2memif-1lxc-ndrpdr
    10ge2p1xxv710-eth-l2xcbase-eth-2memif-1dcr-ndrpdr
    10ge2p1xxv710-dot1q-l2bdbasemaclrn-eth-2memif-1dcr-ndrpdr
    10ge2p1xxv710-eth-l2bdbasemaclrn-eth-2memif-1lxc-ndrpdr
    10ge2p1xxv710-ethip4-ip4base-eth-2memif-1dcr-ndrpdr

    Tests.Vpp.Perf.Container Memif.25Ge2P1Xxv710-Eth-L2Xcbase-Eth-2Memif-1Lxc-Ndrpdr.64B-2t1c-eth-l2xcbase-eth-2memif-1lxc-ndrpdr
    Tests.Vpp.Perf.Container Memif.25Ge2P1Xxv710-Eth-L2Xcbase-Eth-2Memif-1Dcr-Ndrpdr.64B-2t1c-eth-l2xcbase-eth-2memif-1dcr-ndrpdr
    Tests.Vpp.Perf.Container Memif.25Ge2P1Xxv710-Dot1Q-L2Bdbasemaclrn-Eth-2Memif-1Dcr-Ndrpdr.64B-2t1c-dot1q-l2bdbasemaclrn-eth-2memif-1dcr-ndrpdr
    Tests.Vpp.Perf.Container Memif.25Ge2P1Xxv710-Eth-L2Bdbasemaclrn-Eth-2Memif-1Lxc-Ndrpdr.64B-2t1c-eth-l2bdbasemaclrn-eth-2memif-1lxc-ndrpdr
    Tests.Vpp.Perf.Container Memif.25Ge2P1Xxv710-Ethip4-Ip4Base-Eth-2Memif-1Dcr-Ndrpdr.64B-2t1c-ethip4-ip4base-eth-2memif-1dcr-ndrpdr

3n-skx-xxv710
~~~~~~~~~~~~~

64b-2t1c-memif-base-i40e
------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-2t1c-memif-base-i40e-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-2t1c-memif-base-i40e-ndr}
            \label{fig:3n-skx-xxv710-64b-2t1c-memif-base-i40e-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-2t1c-memif-base-i40e-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-2t1c-memif-base-i40e-pdr}
            \label{fig:3n-skx-xxv710-64b-2t1c-memif-base-i40e-pdr}
    \end{figure}
