
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

TCP/IP with iperf3
~~~~~~~~~~~~~~~~~~

.. todo::
    Add introduction

.. raw:: latex

    \clearpage

1460b-1t1c-xl710-base-scale
---------------------------

.. raw:: html

    <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../../_static/vpp/3n-hsw-xl710-1460b-1t1c-eth-ip4tcp-ldpreload-iperf3-bps.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-1460b-1t1c-eth-ip4tcp-ldpreload-iperf3-bps}
            \label{fig:3n-hsw-xl710-1460b-1t1c-eth-ip4tcp-ldpreload-iperf3-bps}
    \end{figure}

.. raw:: latex

    \clearpage

1460b-1t1c-xl710-nsim-base-scale
--------------------------------

.. raw:: html

    <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../../_static/vpp/3n-hsw-xl710-1460b-1t1c-eth-ip4tcp-nsim-ldpreload-iperf3-bps.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-1460b-1t1c-eth-ip4tcp-nsim-ldpreload-iperf3-bps}
            \label{fig:3n-hsw-xl710-1460b-1t1c-eth-ip4tcp-nsim-ldpreload-iperf3-bps}
    \end{figure}
