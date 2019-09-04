
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
    ### 64b-l2switching-base-avf
    10ge2p1xxv710-avf-eth-l2patch-ndrpdr
    10ge2p1xxv710-avf-eth-l2xcbase-ndrpdr
    10ge2p1xxv710-avf-eth-l2bdbasemaclrn-ndrpdr

    ### 64b-l2switching-base-i40e
    10ge2p1xxv710-dot1q-l2xcbase-ndrpdr
    10ge2p1xxv710-eth-l2xcbase-ndrpdr
    10ge2p1xxv710-dot1q-l2bdbasemaclrn-ndrpdr
    10ge2p1xxv710-eth-l2bdbasemaclrn-ndrpdr

    ### 64b-l2switching-base-scale-i40e
    10ge2p1xxv710-eth-l2patch-ndrpdr
    10ge2p1xxv710-eth-l2xcbase-ndrpdr
    10ge2p1xxv710-eth-l2bdbasemaclrn-ndrpdr
    10ge2p1xxv710-eth-l2bdscale10kmaclrn-ndrpdr
    10ge2p1xxv710-eth-l2bdscale100kmaclrn-ndrpdr
    10ge2p1xxv710-eth-l2bdscale1mmaclrn-ndrpdr

    ###  64b-features-l2switching-base-i40e
    10ge2p1xxv710-eth-l2bdbasemaclrn-ndrpdr
    10ge2p1xxv710-eth-l2bdbasemaclrn-iacl50sf-10kflows-ndrpdr
    10ge2p1xxv710-eth-l2bdbasemaclrn-iacl50sl-10kflows-ndrpdr
    10ge2p1xxv710-eth-l2bdbasemaclrn-oacl50sf-10kflows-ndrpdr
    10ge2p1xxv710-eth-l2bdbasemaclrn-oacl50sl-10kflows-ndrpdr
    10ge2p1xxv710-eth-l2bdbasemaclrn-macip-iacl50sl-10kflows-ndrpdr

3n-skx-xxv710
~~~~~~~~~~~~~

64b-l2switching-base-avf
-----------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-l2switching-base-avf-ndr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-l2switching-base-avf-ndr-tsa}
            \label{fig:3n-skx-xxv710-64b-l2switching-base-avf-ndr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-l2switching-base-avf-pdr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-l2switching-base-avf-pdr-tsa}
            \label{fig:3n-skx-xxv710-64b-l2switching-base-avf-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-l2switching-base-i40e
------------------------------

.. raw:: html

    <center>
    <iframe id="11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-l2switching-base-i40e-ndr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-l2switching-base-i40e-ndr-tsa}
            \label{fig:3n-skx-xxv710-64b-l2switching-base-i40e-ndr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="12" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-l2switching-base-i40e-pdr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-l2switching-base-i40e-pdr-tsa}
            \label{fig:3n-skx-xxv710-64b-l2switching-base-i40e-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-l2switching-base-scale-i40e
------------------------------------

.. raw:: html

    <center>
    <iframe id="21" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-l2switching-base-scale-i40e-ndr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-l2switching-base-scale-i40e-ndr-tsa}
            \label{fig:3n-skx-xxv710-64b-l2switching-base-scale-i40e-ndr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="22" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-l2switching-base-scale-i40e-pdr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-l2switching-base-scale-i40e-pdr-tsa}
            \label{fig:3n-skx-xxv710-64b-l2switching-base-scale-i40e-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-features-l2switching-base-i40e
--------------------------------------

.. raw:: html

    <center>
    <iframe id="31" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-features-l2switching-base-i40e-ndr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-features-l2switching-base-i40e-ndr-tsa}
            \label{fig:3n-skx-xxv710-64b-features-l2switching-base-i40e-ndr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="32" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-skx-xxv710-64b-features-l2switching-base-i40e-pdr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-skx-xxv710-64b-features-l2switching-base-i40e-pdr-tsa}
            \label{fig:3n-skx-xxv710-64b-features-l2switching-base-i40e-pdr-tsa}
    \end{figure}
