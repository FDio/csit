
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

.. _packet_throughput_graphs_ip6-2n-dnv-x553:

2n-dnv-x553
~~~~~~~~~~~

78b-1t1c-base
-------------

.. raw:: html

    <center>
    <iframe id="ifrm37" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-dnv-x553-78b-1t1c-base-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-dnv-x553-78b-1t1c-base-ndr}
            \label{fig:ip6-2n-dnv-x553-78b-1t1c-base-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="ifrm38" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-dnv-x553-78b-1t1c-base-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-dnv-x553-78b-1t1c-base-pdr}
            \label{fig:ip6-2n-dnv-x553-78b-1t1c-base-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

78b-2t2c-base
-------------

.. raw:: html

    <center>
    <iframe id="ifrm39" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-dnv-x553-78b-2t2c-base-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-dnv-x553-78b-2t2c-base-ndr}
            \label{fig:ip6-2n-dnv-x553-78b-2t2c-base-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="ifrm40" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip6-2n-dnv-x553-78b-2t2c-base-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip6-2n-dnv-x553-78b-2t2c-base-pdr}
            \label{fig:ip6-2n-dnv-x553-78b-2t2c-base-pdr}
    \end{figure}
