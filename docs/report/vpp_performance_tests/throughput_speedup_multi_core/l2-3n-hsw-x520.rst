
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

3n-hsw-x520
~~~~~~~~~~~

..
    64b-base_and_scale
    ------------------

    .. raw:: html

        <center>
        <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2sw-3n-hsw-x520-64b-base_and_scale-ndr-tsa.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2sw-3n-hsw-x520-64b-base_and_scale-ndr-tsa}
                \label{fig:l2sw-3n-hsw-x520-64b-base_and_scale-ndr-tsa}
        \end{figure}

    .. raw:: latex

        \clearpage

    .. raw:: html

        <center>
        <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2sw-3n-hsw-x520-64b-base_and_scale-pdr-tsa.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2sw-3n-hsw-x520-64b-base_and_scale-pdr-tsa}
                \label{fig:l2sw-3n-hsw-x520-64b-base_and_scale-pdr-tsa}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-features
    ------------

    .. raw:: html

        <center>
        <iframe id="ifrm03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2sw-3n-hsw-x520-64b-features-ndr-tsa.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2sw-3n-hsw-x520-64b-features-ndr-tsa}
                \label{fig:l2sw-3n-hsw-x520-64b-features-ndr-tsa}
        \end{figure}

    .. raw:: latex

        \clearpage

    .. raw:: html

        <center>
        <iframe id="ifrm04" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2sw-3n-hsw-x520-64b-features-pdr-tsa.html"></iframe>
        <p><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2sw-3n-hsw-x520-64b-features-pdr-tsa}
                \label{fig:l2sw-3n-hsw-x520-64b-features-pdr-tsa}
        \end{figure}


64b-features-oacl
-----------------

.. raw:: html

    <center>
    <iframe id="ifrm07" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2sw-3n-hsw-x520-64b-features-oacl-ndr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2sw-3n-hsw-x520-64b-features-oacl-ndr-tsa}
            \label{fig:l2sw-3n-hsw-x520-64b-features-oacl-ndr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="ifrm08" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2sw-3n-hsw-x520-64b-features-oacl-pdr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2sw-3n-hsw-x520-64b-features-oacl-pdr-tsa}
            \label{fig:l2sw-3n-hsw-x520-64b-features-oacl-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-features-macip
------------------

.. raw:: html

    <center>
    <iframe id="ifrm09" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2sw-3n-hsw-x520-64b-features-macip-ndr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2sw-3n-hsw-x520-64b-features-macip-ndr-tsa}
            \label{fig:l2sw-3n-hsw-x520-64b-features-macip-ndr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="ifrm10" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2sw-3n-hsw-x520-64b-features-macip-pdr-tsa.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2sw-3n-hsw-x520-64b-features-macip-pdr-tsa}
            \label{fig:l2sw-3n-hsw-x520-64b-features-macip-pdr-tsa}
    \end{figure}
