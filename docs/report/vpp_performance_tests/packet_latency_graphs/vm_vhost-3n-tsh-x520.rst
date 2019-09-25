
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
    ### 64b-?t?c-vhost-base-ixgbe
    10ge2p1x520-dot1q-l2xcbase-eth-2vhostvr1024-1vm-ndrpdr
    10ge2p1x520-eth-l2xcbase-eth-2vhostvr1024-1vm-ndrpdr
    10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-ndrpdr
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-ndrpdr
    10ge2p1x520-ethip4-ip4base-eth-2vhostvr1024-1vm-ndrpdr

    Tests.Vpp.Perf.Vm Vhost.10Ge2P1X520-Dot1Q-L2Xcbase-Eth-2Vhostvr1024-1Vm-Ndrpdr.64B-1t1c-dot1q-l2xcbase-eth-2vhostvr1024-1vm-ndrpdr
    Tests.Vpp.Perf.Vm Vhost.10Ge2P1X520-Eth-L2Xcbase-Eth-2Vhostvr1024-1Vm-Ndrpdr.64B-1t1c-eth-l2xcbase-eth-2vhostvr1024-1vm-ndrpdr
    Tests.Vpp.Perf.Vm Vhost.10Ge2P1X520-Dot1Q-L2Bdbasemaclrn-Eth-2Vhostvr1024-1Vm-Ndrpdr.64B-1t1c-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-ndrpdr
    Tests.Vpp.Perf.Vm Vhost.10Ge2P1X520-Eth-L2Bdbasemaclrn-Eth-2Vhostvr1024-1Vm-Ndrpdr.64B-1t1c-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-ndrpdr
    Tests.Vpp.Perf.Vm Vhost.10Ge2P1X520-Ethip4-Ip4Base-Eth-2Vhostvr1024-1Vm-Ndrpdr.64B-1t1c-ethip4-ip4base-eth-2vhostvr1024-1vm-ndrpdr

3n-tsh-x520
~~~~~~~~~~~

64b-1t1c-vhost-base-ixgbe
-------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-tsh-x520-64b-1t1c-vhost-base-ixgbe-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-tsh-x520-64b-1t1c-vhost-base-ixgbe-ndr-lat}
            \label{fig:3n-tsh-x520-64b-1t1c-vhost-base-ixgbe-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-vhost-base-ixgbe
-------------------------

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-tsh-x520-64b-2t2c-vhost-base-ixgbe-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-tsh-x520-64b-2t2c-vhost-base-ixgbe-ndr-lat}
            \label{fig:3n-tsh-x520-64b-2t2c-vhost-base-ixgbe-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t4c-vhost-base-ixgbe
-------------------------

.. raw:: html

    <center>
    <iframe id="03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-tsh-x520-64b-4t4c-vhost-base-ixgbe-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-tsh-x520-64b-4t4c-vhost-base-ixgbe-ndr-lat}
            \label{fig:3n-tsh-x520-64b-4t4c-vhost-base-ixgbe-ndr-lat}
    \end{figure}
