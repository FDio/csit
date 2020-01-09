
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
    ## 2n-clx-xxv710
    ### 64b-?t?c-memif-base-i40e
    2n1l-10ge2p1xxv710-eth-l2xcbase-eth-2memif-1dcr-ndrpdr
    2n1l-10ge2p1xxv710-dot1q-l2bdbasemaclrn-eth-2memif-1dcr-ndrpdr
    2n1l-10ge2p1xxv710-eth-l2bdbasemaclrn-eth-2memif-1dcr-ndrpdr
    2n1l-10ge2p1xxv710-ethip4-ip4base-eth-2memif-1dcr-ndrpdr

2n-clx-xxv710
~~~~~~~~~~~~~

64b-2t1c-memif-base-i40e
------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-clx-xxv710-64b-2t1c-memif-base-i40e-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-xxv710-64b-2t1c-memif-base-i40e-ndr}
            \label{fig:2n-clx-xxv710-64b-2t1c-memif-base-i40e-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-clx-xxv710-64b-2t1c-memif-base-i40e-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-xxv710-64b-2t1c-memif-base-i40e-pdr}
            \label{fig:2n-clx-xxv710-64b-2t1c-memif-base-i40e-pdr}
    \end{figure}
