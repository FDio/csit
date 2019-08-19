
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
    ### 64b-?t?c-ip4routing-base-scale-avf
    2n1l-10ge2p1xxv710-avf-dot1q-ip4base-ndrpdr
    2n1l-10ge2p1xxv710-avf-ethip4-ip4base-ndrpdr
    2n1l-10ge2p1xxv710-avf-ethip4-ip4scale20k-ndrpdr
    2n1l-10ge2p1xxv710-avf-ethip4-ip4scale200k-ndrpdr
    2n1l-10ge2p1xxv710-avf-ethip4-ip4scale2m-ndrpdr

    ### 64b-?t?c-ip4routing-base-scale-i40e
    2n1l-10ge2p1xxv710-dot1q-ip4base-ndrpdr
    2n1l-10ge2p1xxv710-ethip4-ip4base-ndrpdr
    2n1l-10ge2p1xxv710-ethip4-ip4scale20k-ndrpdr
    2n1l-10ge2p1xxv710-ethip4-ip4scale200k-ndrpdr
    2n1l-10ge2p1xxv710-ethip4-ip4scale2m-ndrpdr

    ### 64b-?t?c-features-ip4routing-base-i40e
    2n1l-10ge2p1xxv710-ethip4-ip4base-ndrpdr
    2n1l-10ge2p1xxv710-ethip4udp-ip4base-iacl50sf-10kflows-ndrpdr
    2n1l-10ge2p1xxv710-ethip4udp-ip4base-iacl50sl-10kflows-ndrpdr
    2n1l-10ge2p1xxv710-ethip4udp-ip4base-oacl50sf-10kflows-ndrpdr
    2n1l-10ge2p1xxv710-ethip4udp-ip4base-oacl50sl-10kflows-ndrpdr
    2n1l-10ge2p1xxv710-ethip4udp-ip4base-nat44-ndrpdr

2n-skx-xxv710
~~~~~~~~~~~~~

64b-2t1c-ip4routing-base-scale-avf
----------------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-skx-xxv710-64b-2t1c-ip4routing-base-scale-avf-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-xxv710-64b-2t1c-ip4routing-base-scale-avf-ndr}
            \label{fig:2n-skx-xxv710-64b-2t1c-ip4routing-base-scale-avf-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-skx-xxv710-64b-2t1c-ip4routing-base-scale-avf-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-xxv710-64b-2t1c-ip4routing-base-scale-avf-pdr}
            \label{fig:2n-skx-xxv710-64b-2t1c-ip4routing-base-scale-avf-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-ip4routing-base-scale-i40e
-----------------------------------




64b-2t1c-features-ip4routing-base-i40e
--------------------------------------
