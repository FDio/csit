
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
    ### 64b-?t?c-ip4routing-base-scale-ixgbe
    10ge2p1x520-dot1q-ip4base-ndrpdr
    10ge2p1x520-ethip4-ip4base-ndrpdr
    10ge2p1x520-ethip4-ip4scale20k-ndrpdr
    10ge2p1x520-ethip4-ip4scale200k-ndrpdr
    10ge2p1x520-ethip4-ip4scale2m-ndrpdr

    Tests.Vpp.Perf.Ip4.10Ge2P1X520-Dot1Q-Ip4Base-Ndrpdr.64B-1t1c-dot1q-ip4base-ndrpdr
    Tests.Vpp.Perf.Ip4.10Ge2P1X520-Ethip4-Ip4Base-Ndrpdr.64B-1t1c-ethip4-ip4base-ndrpdr
    Tests.Vpp.Perf.Ip4.10Ge2P1X520-Ethip4-Ip4Scale20K-Ndrpdr.64B-1t1c-ethip4-ip4scale20k-ndrpdr
    Tests.Vpp.Perf.Ip4.10Ge2P1X520-Ethip4-Ip4Scale200K-Ndrpdr.64B-1t1c-ethip4-ip4scale200k-ndrpdr
    Tests.Vpp.Perf.Ip4.10Ge2P1X520-Ethip4-Ip4Scale2M-Ndrpdr.64B-1t1c-ethip4-ip4scale2m-ndrpdr

    ### 64b-?t?c-features-ip4routing-base-ixgbe
    10ge2p1x520-ethip4-ip4base-ndrpdr
    10ge2p1x520-ethip4udp-ip4base-iacl50sf-10kflows-ndrpdr
    10ge2p1x520-ethip4udp-ip4base-iacl50sl-10kflows-ndrpdr
    10ge2p1x520-ethip4udp-ip4base-oacl50sf-10kflows-ndrpdr
    10ge2p1x520-ethip4udp-ip4base-oacl50sl-10kflows-ndrpdr
    10ge2p1x520-ethip4udp-ip4base-nat44-ndrpdr

    Tests.Vpp.Perf.Ip4.10Ge2P1X520-Ethip4-Ip4Base-Ndrpdr.64B-1t1c-ethip4-ip4base-ndrpdr
    Tests.Vpp.Perf.Ip4.10Ge2P1X520-Ethip4Udp-Ip4Base-Iacl50Sf-10Kflows-Ndrpdr.64B-1t1c-ethip4udp-ip4base-iacl50sf-10kflows-ndrpdr
    Tests.Vpp.Perf.Ip4.10Ge2P1X520-Ethip4Udp-Ip4Base-Iacl50Sl-10Kflows-Ndrpdr.64B-1t1c-ethip4udp-ip4base-iacl50sl-10kflows-ndrpdr
    Tests.Vpp.Perf.Ip4.10Ge2P1X520-Ethip4Udp-Ip4Base-Oacl50Sf-10Kflows-Ndrpdr.64B-1t1c-ethip4udp-ip4base-oacl50sf-10kflows-ndrpdr
    Tests.Vpp.Perf.Ip4.10Ge2P1X520-Ethip4Udp-Ip4Base-Oacl50Sl-10Kflows-Ndrpdr.64B-1t1c-ethip4udp-ip4base-oacl50sl-10kflows-ndrpdr
    Tests.Vpp.Perf.Ip4.10Ge2P1X520-Ethip4Udp-Ip4Base-Nat44-Ndrpdr.64B-1t1c-ethip4udp-ip4base-nat44-ndrpdr

3n-tsh-x520
~~~~~~~~~~~

64b-1t1c-ip4routing-base-scale-ixgbe
------------------------------------

.. raw:: html

    <center>
    <iframe id="11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-tsh-x520-64b-1t1c-ip4routing-base-scale-ixgbe-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-tsh-x520-64b-1t1c-ip4routing-base-scale-ixgbe-ndr-lat}
            \label{fig:3n-tsh-x520-64b-1t1c-ip4routing-base-scale-ixgbe-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-ip4routing-base-scale-ixgbe
------------------------------------

.. raw:: html

    <center>
    <iframe id="12" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-tsh-x520-64b-2t2c-ip4routing-base-scale-ixgbe-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-tsh-x520-64b-2t2c-ip4routing-base-scale-ixgbe-ndr-lat}
            \label{fig:3n-tsh-x520-64b-2t2c-ip4routing-base-scale-ixgbe-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t4c-ip4routing-base-scale-ixgbe
------------------------------------

.. raw:: html

    <center>
    <iframe id="13" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-tsh-x520-64b-4t4c-ip4routing-base-scale-ixgbe-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-tsh-x520-64b-4t4c-ip4routing-base-scale-ixgbe-ndr-lat}
            \label{fig:3n-tsh-x520-64b-4t4c-ip4routing-base-scale-ixgbe-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-features-ip4routing-base-ixgbe
--------------------------------------

.. raw:: html

    <center>
    <iframe id="21" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-tsh-x520-64b-1t1c-features-ip4routing-base-ixgbe-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-tsh-x520-64b-1t1c-features-ip4routing-base-ixgbe-ndr-lat}
            \label{fig:3n-tsh-x520-64b-1t1c-features-ip4routing-base-ixgbe-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-features-ip4routing-base-ixgbe
--------------------------------------

.. raw:: html

    <center>
    <iframe id="22" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-tsh-x520-64b-2t2c-features-ip4routing-base-ixgbe-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-tsh-x520-64b-2t2c-features-ip4routing-base-ixgbe-ndr-lat}
            \label{fig:3n-tsh-x520-64b-2t2c-features-ip4routing-base-ixgbe-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t4c-features-ip4routing-base-ixgbe
--------------------------------------

.. raw:: html

    <center>
    <iframe id="23" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-tsh-x520-64b-4t4c-features-ip4routing-base-ixgbe-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-tsh-x520-64b-4t4c-features-ip4routing-base-ixgbe-ndr-lat}
            \label{fig:3n-tsh-x520-64b-4t4c-features-ip4routing-base-ixgbe-ndr-lat}
    \end{figure}
