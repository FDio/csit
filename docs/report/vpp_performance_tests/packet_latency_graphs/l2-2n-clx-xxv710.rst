
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
    ### 64b-?t?c-l2switching-base-avf
    2n1l-10ge2p1xxv710-avf-eth-l2patch-ndrpdr
    2n1l-10ge2p1xxv710-avf-eth-l2xcbase-ndrpdr
    2n1l-10ge2p1xxv710-avf-dot1q-l2bdbasemaclrn-ndrpdr
    2n1l-10ge2p1xxv710-avf-eth-l2bdbasemaclrn-ndrpdr
    2n1l-10ge2p1xxv710-avf-dot1q-l2bdbasemaclrn-gbp-ndrpdr

    ### 64b-?t?c-l2switching-base-i40e
    2n1l-10ge2p1xxv710-eth-l2patch-ndrpdr
    2n1l-10ge2p1xxv710-dot1q-l2xcbase-ndrpdr
    2n1l-10ge2p1xxv710-eth-l2xcbase-ndrpdr
    2n1l-10ge2p1xxv710-dot1q-l2bdbasemaclrn-ndrpdr
    2n1l-10ge2p1xxv710-eth-l2bdbasemaclrn-ndrpdr

    ### 64b-?t?c-l2switching-base-scale-i40e
    2n1l-10ge2p1xxv710-eth-l2bdbasemaclrn-ndrpdr
    2n1l-10ge2p1xxv710-eth-l2bdscale10kmaclrn-ndrpdr
    2n1l-10ge2p1xxv710-eth-l2bdscale100kmaclrn-ndrpdr
    2n1l-10ge2p1xxv710-eth-l2bdscale1mmaclrn-ndrpdr

2n-clx-xxv710
~~~~~~~~~~~~~

64b-2t1c-l2switching-base-avf
-----------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-clx-xxv710-64b-2t1c-l2switching-base-avf-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-xxv710-64b-2t1c-l2switching-base-avf-ndr-lat}
            \label{fig:2n-clx-xxv710-64b-2t1c-l2switching-base-avf-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-l2switching-base-avf
-----------------------------

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-clx-xxv710-64b-4t2c-l2switching-base-avf-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-xxv710-64b-4t2c-l2switching-base-avf-ndr-lat}
            \label{fig:2n-clx-xxv710-64b-4t2c-l2switching-base-avf-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-8t4c-l2switching-base-avf
-----------------------------

.. raw:: html

    <center>
    <iframe id="03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-clx-xxv710-64b-8t4c-l2switching-base-avf-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-xxv710-64b-8t4c-l2switching-base-avf-ndr-lat}
            \label{fig:2n-clx-xxv710-64b-8t4c-l2switching-base-avf-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-l2switching-base-i40e
------------------------------

.. raw:: html

    <center>
    <iframe id="11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-clx-xxv710-64b-2t1c-l2switching-base-i40e-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-xxv710-64b-2t1c-l2switching-base-i40e-ndr-lat}
            \label{fig:2n-clx-xxv710-64b-2t1c-l2switching-base-i40e-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-l2switching-base-i40e
------------------------------

.. raw:: html

    <center>
    <iframe id="12" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-clx-xxv710-64b-4t2c-l2switching-base-i40e-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-xxv710-64b-4t2c-l2switching-base-i40e-ndr-lat}
            \label{fig:2n-clx-xxv710-64b-4t2c-l2switching-base-i40e-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-8t4c-l2switching-base-i40e
------------------------------

.. raw:: html

    <center>
    <iframe id="13" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-clx-xxv710-64b-8t4c-l2switching-base-i40e-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-xxv710-64b-8t4c-l2switching-base-i40e-ndr-lat}
            \label{fig:2n-clx-xxv710-64b-8t4c-l2switching-base-i40e-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-l2switching-base-scale-i40e
------------------------------------

.. raw:: html

    <center>
    <iframe id="21" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-clx-xxv710-64b-2t1c-l2switching-base-scale-i40e-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-xxv710-64b-2t1c-l2switching-base-scale-i40e-ndr-lat}
            \label{fig:2n-clx-xxv710-64b-2t1c-l2switching-base-scale-i40e-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-l2switching-base-scale-i40e
------------------------------------

.. raw:: html

    <center>
    <iframe id="22" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-clx-xxv710-64b-4t2c-l2switching-base-scale-i40e-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-xxv710-64b-4t2c-l2switching-base-scale-i40e-ndr-lat}
            \label{fig:2n-clx-xxv710-64b-4t2c-l2switching-base-scale-i40e-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-8t4c-l2switching-base-scale-i40e
------------------------------------

.. raw:: html

    <center>
    <iframe id="23" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-clx-xxv710-64b-8t4c-l2switching-base-scale-i40e-ndr-lat.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-xxv710-64b-8t4c-l2switching-base-scale-i40e-ndr-lat}
            \label{fig:2n-clx-xxv710-64b-8t4c-l2switching-base-scale-i40e-ndr-lat}
    \end{figure}
