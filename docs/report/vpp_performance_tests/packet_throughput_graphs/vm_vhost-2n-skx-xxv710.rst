
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
    ## 2n-skx-xxv710
    ### 64b-?t?c-vhost-base-dpdk
    2n1l-10ge2p1xxv710-eth-l2xcbase-eth-2vhostvr1024-1vm-ndrpdr
    2n1l-10ge2p1xxv710-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-ndrpdr
    2n1l-10ge2p1xxv710-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-ndrpdr
    2n1l-10ge2p1xxv710-ethip4-ip4base-eth-2vhostvr1024-1vm-ndrpdr

    Tests.Vpp.Perf.Vm Vhost.2N1L-25Ge2P1Xxv710-Eth-L2Xcbase-Eth-2Vhostvr1024-1Vm-Ndrpdr.64B-2t1c-eth-l2xcbase-eth-2vhostvr1024-1vm-ndrpdr
    Tests.Vpp.Perf.Vm Vhost.2N1L-25Ge2P1Xxv710-Dot1Q-L2Bdbasemaclrn-Eth-2Vhostvr1024-1Vm-Ndrpdr.64B-2t1c-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-ndrpdr
    Tests.Vpp.Perf.Vm Vhost.2N1L-25Ge2P1Xxv710-Eth-L2Bdbasemaclrn-Eth-2Vhostvr1024-1Vm-Ndrpdr.64B-2t1c-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-ndrpdr
    Tests.Vpp.Perf.Vm Vhost.2N1L-25Ge2P1Xxv710-Ethip4-Ip4Base-Eth-2Vhostvr1024-1Vm-Ndrpdr.64B-2t1c-ethip4-ip4base-eth-2vhostvr1024-1vm-ndrpdr

    Tests.Vpp.Perf.Vm Vhost.2N1L-25Ge2P1Xxv710-Eth-L2Xcbase-Eth-2Vhostvr1024-1Vm-Vppl2Xc-Ndrpdr.64B-2t1c-eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-ndrpdr
    Tests.Vpp.Perf.Vm Vhost.2N1L-25Ge2P1Xxv710-Dot1Q-L2Bdbasemaclrn-Eth-2Vhostvr1024-1Vm-Vppl2Xc-Ndrpdr.64B-2t1c-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-ndrpdr
    Tests.Vpp.Perf.Vm Vhost.2N1L-25Ge2P1Xxv710-Eth-L2Bdbasemaclrn-Eth-2Vhostvr1024-1Vm-Vppl2Xc-Ndrpdr.64B-2t1c-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-ndrpdr
    Tests.Vpp.Perf.Vm Vhost.2N1L-25Ge2P1Xxv710-Ethip4-Ip4Base-Eth-2Vhostvr1024-1Vm-Vppip4-Ndrpdr.64B-2t1c-ethip4-ip4base-eth-2vhostvr1024-1vm-vppip4-ndrpdr

2n-skx-xxv710
~~~~~~~~~~~~~

64b-2t1c-vhost-base-dpdk-testpmd
--------------------------------

..
    .. raw:: html

        <center>
        <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-skx-xxv710-64b-2t1c-vhost-base-dpdk-ndr.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-xxv710-64b-2t1c-vhost-base-dpdk-ndr}
                \label{fig:2n-skx-xxv710-64b-2t1c-vhost-base-dpdk-ndr}
        \end{figure}

    .. raw:: latex

        \clearpage

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-skx-xxv710-64b-2t1c-vhost-base-dpdk-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-xxv710-64b-2t1c-vhost-base-dpdk-pdr}
            \label{fig:2n-skx-xxv710-64b-2t1c-vhost-base-dpdk-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-vhost-base-dpdk-vpp
----------------------------

..
    .. raw:: html

        <center>
        <iframe id="11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-skx-xxv710-64b-2t1c-vhost-base-dpdk-vpp-ndr.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-xxv710-64b-2t1c-vhost-base-dpdk-vpp-ndr}
                \label{fig:2n-skx-xxv710-64b-2t1c-vhost-base-dpdk-vpp-ndr}
        \end{figure}

    .. raw:: latex

        \clearpage

.. raw:: html

    <center>
    <iframe id="12" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-skx-xxv710-64b-2t1c-vhost-base-dpdk-vpp-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-xxv710-64b-2t1c-vhost-base-dpdk-vpp-pdr}
            \label{fig:2n-skx-xxv710-64b-2t1c-vhost-base-dpdk-vpp-pdr}
    \end{figure}
