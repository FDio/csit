
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
    ### 64b-vts-l2switching-base-i40e
    10ge2p1xxv710-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-noacl-2vhostvr1024-1vm-ndrpdr
    10ge2p1xxv710-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermit-2vhostvr1024-1vm-ndrpdr
    10ge2p1xxv710-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermitreflect-2vhostvr1024-1vm-ndrpdr

2n-skx-xxv710
~~~~~~~~~~~~~

114b-vts-l2switching-base-i40e
------------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-skx-xxv710-114b-vts-l2switching-base-i40e-ndr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-xxv710-114b-vts-l2switching-base-i40e-ndr-tsa}
            \label{fig:2n-skx-xxv710-114b-vts-l2switching-base-i40e-ndr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-skx-xxv710-114b-vts-l2switching-base-i40e-pdr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-xxv710-114b-vts-l2switching-base-i40e-pdr-tsa}
            \label{fig:2n-skx-xxv710-114b-vts-l2switching-base-i40e-pdr-tsa}
    \end{figure}
