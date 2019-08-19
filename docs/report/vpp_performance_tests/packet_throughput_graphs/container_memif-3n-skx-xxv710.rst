
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

64b-2t1c-base_and_features
--------------------------

.. raw:: html

    <center>
    <iframe id="ifrm13" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-skx-x710-64b-2t1c-base_and_features-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{memif-3n-skx-x710-64b-2t1c-base_and_features-ndr}
            \label{fig:memif-3n-skx-x710-64b-2t1c-base_and_features-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="ifrm14" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-skx-x710-64b-2t1c-base_and_features-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{memif-3n-skx-x710-64b-2t1c-base_and_features-pdr}
            \label{fig:memif-3n-skx-x710-64b-2t1c-base_and_features-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base_and_features
--------------------------

.. raw:: html

    <center>
    <iframe id="ifrm15" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-skx-x710-64b-4t2c-base_and_features-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{memif-3n-skx-x710-64b-4t2c-base_and_features-ndr}
            \label{fig:memif-3n-skx-x710-64b-4t2c-base_and_features-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="ifrm16" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/memif-3n-skx-x710-64b-4t2c-base_and_features-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{memif-3n-skx-x710-64b-4t2c-base_and_features-pdr}
            \label{fig:memif-3n-skx-x710-64b-4t2c-base_and_features-pdr}
    \end{figure}
