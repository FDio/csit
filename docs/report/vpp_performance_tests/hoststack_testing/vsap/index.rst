
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

VSAP with ldpreload
~~~~~~~~~~~~~~~~~~~

.. todo::
    Add introduction

.. raw:: latex

    \clearpage

2t1c-cx556a-base-scale-cps
--------------------------

.. raw:: html

    <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../../_static/vpp/2n-clx-cx556a-0b-2t1c-eth-ip4tcphttp-ldpreload-nginx-cps.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-cx556a-0b-2t1c-eth-ip4tcphttp-ldpreload-nginx-cps}
            \label{fig:2n-clx-cx556a-0b-2t1c-eth-ip4tcphttp-ldpreload-nginx-cps}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../../_static/vpp/2n-clx-cx556a-64b-2t1c-eth-ip4tcphttp-ldpreload-nginx-cps.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-cx556a-64b-2t1c-eth-ip4tcphttp-ldpreload-nginx-cps}
            \label{fig:2n-clx-cx556a-64b-2t1c-eth-ip4tcphttp-ldpreload-nginx-cps}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <iframe id="ifrm03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../../_static/vpp/2n-clx-cx556a-1024b-2t1c-eth-ip4tcphttp-ldpreload-nginx-cps.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-cx556a-1024b-2t1c-eth-ip4tcphttp-ldpreload-nginx-cps}
            \label{fig:2n-clx-cx556a-1024b-2t1c-eth-ip4tcphttp-ldpreload-nginx-cps}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <iframe id="ifrm04" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../../_static/vpp/2n-clx-cx556a-2048b-2t1c-eth-ip4tcphttp-ldpreload-nginx-cps.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-cx556a-2048b-2t1c-eth-ip4tcphttp-ldpreload-nginx-cps}
            \label{fig:2n-clx-cx556a-2048b-2t1c-eth-ip4tcphttp-ldpreload-nginx-cps}
    \end{figure}

.. raw:: latex

    \clearpage

2t1c-cx556a-base-scale-rps
--------------------------

.. raw:: html

    <iframe id="ifrm01r" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../../_static/vpp/2n-clx-cx556a-0b-2t1c-eth-ip4tcphttp-ldpreload-nginx-rps.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-cx556a-0b-2t1c-eth-ip4tcphttp-ldpreload-nginx-rps}
            \label{fig:2n-clx-cx556a-0b-2t1c-eth-ip4tcphttp-ldpreload-nginx-rps}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <iframe id="ifrm02r" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../../_static/vpp/2n-clx-cx556a-64b-2t1c-eth-ip4tcphttp-ldpreload-nginx-rps.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-cx556a-64b-2t1c-eth-ip4tcphttp-ldpreload-nginx-rps}
            \label{fig:2n-clx-cx556a-64b-2t1c-eth-ip4tcphttp-ldpreload-nginx-rps}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <iframe id="ifrm03r" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../../_static/vpp/2n-clx-cx556a-1024b-2t1c-eth-ip4tcphttp-ldpreload-nginx-rps.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-cx556a-1024b-2t1c-eth-ip4tcphttp-ldpreload-nginx-rps}
            \label{fig:2n-clx-cx556a-1024b-2t1c-eth-ip4tcphttp-ldpreload-nginx-rps}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <iframe id="ifrm04r" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../../_static/vpp/2n-clx-cx556a-2048b-2t1c-eth-ip4tcphttp-ldpreload-nginx-rps.html"></iframe>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{2n-clx-cx556a-2048b-2t1c-eth-ip4tcphttp-ldpreload-nginx-rps}
            \label{fig:2n-clx-cx556a-2048b-2t1c-eth-ip4tcphttp-ldpreload-nginx-rps}
    \end{figure}
