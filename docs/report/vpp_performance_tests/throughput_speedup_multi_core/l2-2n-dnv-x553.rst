
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
    ### 64b-?t?c-l2switching-base-scale-ixgbe
    10ge2p1x520-eth-l2patch-ndrpdr
    10ge2p1x520-eth-l2xcbase-ndrpdr
    10ge2p1x520-eth-l2bdbasemaclrn-ndrpdr
    10ge2p1x520-eth-l2bdscale10kmaclrn-ndrpdr
    10ge2p1x520-eth-l2bdscale100kmaclrn-ndrpdr
    10ge2p1x520-eth-l2bdscale1mmaclrn-ndrpdr

    Tests.Vpp.Perf.L2.2N1L-10Ge2P1X553-Eth-L2Patch-Ndrpdr.64B-1t1c-eth-l2patch-ndrpdr
    Tests.Vpp.Perf.L2.2N1L-10Ge2P1X553-Eth-L2Xcbase-Ndrpdr.64B-1t1c-eth-l2xcbase-ndrpdr
    Tests.Vpp.Perf.L2.2N1L-10Ge2P1X553-Eth-L2Bdbasemaclrn-Ndrpdr.64B-1t1c-eth-l2bdbasemaclrn-ndrpdr

2n-dnv-x553
~~~~~~~~~~~

64b-l2switching-base-ixgbe
--------------------------

.. raw:: html

    <center>
    <iframe id="11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-dnv-x553-64b-l2switching-base-ixgbe-ndr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-dnv-x553-64b-l2switching-base-ixgbe-ndr-tsa}
            \label{fig:2n-dnv-x553-64b-l2switching-base-ixgbe-ndr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="12" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-dnv-x553-64b-l2switching-base-ixgbe-pdr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-dnv-x553-64b-l2switching-base-ixgbe-pdr-tsa}
            \label{fig:2n-dnv-x553-64b-l2switching-base-ixgbe-pdr-tsa}
    \end{figure}
