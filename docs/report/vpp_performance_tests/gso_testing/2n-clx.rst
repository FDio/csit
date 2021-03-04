
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

2n-clx
~~~~~~

.. todo::
    Add introduction

.. raw:: latex

    \clearpage

1t1c
----

.. raw:: html

    <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-clx-128kb-1t1c-ip4routing-iperf3.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-128kb-1t1c-ip4routing-iperf3}
            \label{fig:2n-clx-128kb-1t1c-ip4routing-iperf3}
    \end{figure}

..
    .. raw:: latex

        \clearpage

    2t2c
    ----

    .. raw:: html

        <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-clx-128kb-2t2c-ip4routing-iperf3.html"></iframe>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-128kb-2t2c-ip4routing-iperf3}
                \label{fig:2n-clx-128kb-2t2c-ip4routing-iperf3}
        \end{figure}

    .. raw:: latex

        \clearpage

    4t4c
    ----

    .. raw:: html

        <iframe id="ifrm03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/2n-clx-128kb-4t4c-ip4routing-iperf3.html"></iframe>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-128kb-4t4c-ip4routing-iperf3}
                \label{fig:2n-clx-128kb-4t4c-ip4routing-iperf3}
        \end{figure}
