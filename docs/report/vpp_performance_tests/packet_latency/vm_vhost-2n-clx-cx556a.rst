
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

2n-clx-cx556a
~~~~~~~~~~~~~

64b-2t1c-vhost-base-rdma-testpmd
--------------------------------

.. raw:: html

    <center>
    <iframe id="1" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/hdrh-lat-percentile-2n-clx-100ge2p1cx556a-64b-2t1c-rdma-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{hdrh-lat-percentile-2n-clx-100ge2p1cx556a-64b-2t1c-rdma-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm}
            \label{fig:hdrh-lat-percentile-2n-clx-100ge2p1cx556a-64b-2t1c-rdma-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-vhost-base-rdma-vpp
----------------------------

.. raw:: html

    <center>
    <iframe id="1" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/hdrh-lat-percentile-2n-clx-100ge2p1cx556a-64b-2t1c-rdma-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{hdrh-lat-percentile-2n-clx-100ge2p1cx556a-64b-2t1c-rdma-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc}
            \label{fig:hdrh-lat-percentile-2n-clx-100ge2p1cx556a-64b-2t1c-rdma-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-vhost-base-mlx5-testpmd
--------------------------------

.. raw:: html

    <center>
    <iframe id="11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/hdrh-lat-percentile-2n-clx-100ge2p1cx556a-64b-2t1c-mlx5-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{hdrh-lat-percentile-2n-clx-100ge2p1cx556a-64b-2t1c-mlx5-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm}
            \label{fig:hdrh-lat-percentile-2n-clx-100ge2p1cx556a-64b-2t1c-mlx5-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-vhost-base-mlx5-vpp
----------------------------

.. raw:: html

    <center>
    <iframe id="11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/hdrh-lat-percentile-2n-clx-100ge2p1cx556a-64b-2t1c-mlx5-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{hdrh-lat-percentile-2n-clx-100ge2p1cx556a-64b-2t1c-mlx5-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc}
            \label{fig:hdrh-lat-percentile-2n-clx-100ge2p1cx556a-64b-2t1c-mlx5-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc}
    \end{figure}
