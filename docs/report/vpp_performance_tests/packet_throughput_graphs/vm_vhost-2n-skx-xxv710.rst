
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

2n-skx-xxv710
~~~~~~~~~~~~~

..
    64b-2t1c-vhost-base-avf-testpmd
    -------------------------------

    .. raw:: html

        <center>
        <iframe id="101" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-skx-xxv710-64b-2t1c-vhost-base-avf-ndr.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-xxv710-64b-2t1c-vhost-base-avf-ndr}
                \label{fig:2n-skx-xxv710-64b-2t1c-vhost-base-avf-ndr}
        \end{figure}

    .. raw:: latex

        \clearpage

    .. raw:: html

        <center>
        <iframe id="102" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-skx-xxv710-64b-2t1c-vhost-base-avf-pdr.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-xxv710-64b-2t1c-vhost-base-avf-pdr}
                \label{fig:2n-skx-xxv710-64b-2t1c-vhost-base-avf-pdr}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-2t1c-vhost-base-dpdk-vpp
    ----------------------------

    .. raw:: html

        <center>
        <iframe id="111" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-skx-xxv710-64b-2t1c-vhost-base-avf-vpp-ndr.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-xxv710-64b-2t1c-vhost-base-avf-vpp-ndr}
                \label{fig:2n-skx-xxv710-64b-2t1c-vhost-base-avf-vpp-ndr}
        \end{figure}

    .. raw:: latex

        \clearpage

    .. raw:: html

        <center>
        <iframe id="112" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-skx-xxv710-64b-2t1c-vhost-base-avf-vpp-pdr.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-skx-xxv710-64b-2t1c-vhost-base-avf-vpp-pdr}
                \label{fig:2n-skx-xxv710-64b-2t1c-vhost-base-avf-vpp-pdr}
        \end{figure}

    .. raw:: latex

        \clearpage

64b-2t1c-vhost-base-dpdk-testpmd
--------------------------------

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
