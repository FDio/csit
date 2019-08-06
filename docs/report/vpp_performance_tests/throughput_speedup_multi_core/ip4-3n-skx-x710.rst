
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

3n-skx-x710
~~~~~~~~~~~

64b-base_and_scale
------------------

.. raw:: html

    <center>
    <iframe id="ifrm23" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-base_and_scale-ndr-tsa}
            \label{fig:ip4-3n-skx-x710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="ifrm24" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-base_and_scale-pdr-tsa}
            \label{fig:ip4-3n-skx-x710-64b-base_and_scale-pdr-tsa}
    \end{figure}

..
    .. raw:: latex

        \clearpage

    64b-features
    ------------

    .. raw:: html

        <center>
        <iframe id="ifrm25" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-features-ndr-tsa.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-features-ndr-tsa}
                \label{fig:ip4-3n-skx-x710-64b-features-ndr-tsa}
        \end{figure}

    .. raw:: latex

        \clearpage

    .. raw:: html

        <center>
        <iframe id="ifrm26" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-features-pdr-tsa.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-features-pdr-tsa}
                \label{fig:ip4-3n-skx-x710-64b-features-pdr-tsa}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-features-nat44
    ------------------

    .. raw:: html

        <center>
        <iframe id="ifrm27" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-features-nat44-ndr-tsa.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-features-nat44-ndr-tsa}
                \label{fig:ip4-3n-skx-x710-64b-features-nat44-ndr-tsa}
        \end{figure}

    .. raw:: latex

        \clearpage

    .. raw:: html

        <center>
        <iframe id="ifrm28" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-features-nat44-pdr-tsa.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-features-nat44-pdr-tsa}
                \label{fig:ip4-3n-skx-x710-64b-features-nat44-pdr-tsa}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-features-iacl
    -----------------

    .. raw:: html

        <center>
        <iframe id="ifrm29" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-features-iacl-ndr-tsa.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-features-iacl-ndr-tsa}
                \label{fig:ip4-3n-skx-x710-64b-features-iacl-ndr-tsa}
        \end{figure}

    .. raw:: latex

        \clearpage

    .. raw:: html

        <center>
        <iframe id="ifrm30" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/ip4-3n-skx-x710-64b-features-iacl-pdr-tsa.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{ip4-3n-skx-x710-64b-features-iacl-pdr-tsa}
                \label{fig:ip4-3n-skx-x710-64b-features-iacl-pdr-tsa}
        \end{figure}
