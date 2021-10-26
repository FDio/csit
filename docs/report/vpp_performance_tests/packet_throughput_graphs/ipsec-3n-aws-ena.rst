
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

3n-aws-nitro50g
~~~~~~~~~~~~~~~

imix-2t1c-ipsec-ip4routing-scale-sw-ena
---------------------------------------

.. raw:: html

    <center>
    <iframe id="01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-aws-nitro50g-imix-2t1c-ipsec-ip4routing-scale-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-aws-nitro50g-imix-2t1c-ipsec-ip4routing-scale-ndr}
            \label{fig:3n-aws-nitro50g-imix-2t1c-ipsec-ip4routing-scale-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-aws-nitro50g-imix-2t1c-ipsec-ip4routing-scale-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-aws-nitro50g-imix-2t1c-ipsec-ip4routing-scale-pdr}
            \label{fig:3n-aws-nitro50g-imix-2t1c-ipsec-ip4routing-scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

1518b-2t1c-ipsec-ip4routing-scale-sw-ena
----------------------------------------

.. raw:: html

    <center>
    <iframe id="101" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-aws-nitro50g-1518b-2t1c-ipsec-ip4routing-scale-ndr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-aws-nitro50g-1518b-2t1c-ipsec-ip4routing-scale-ndr}
            \label{fig:3n-aws-nitro50g-1518b-2t1c-ipsec-ip4routing-scale-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="102" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-aws-nitro50g-1518b-2t1c-ipsec-ip4routing-scale-pdr.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-aws-nitro50g-1518b-2t1c-ipsec-ip4routing-scale-pdr}
            \label{fig:3n-aws-nitro50g-1518b-2t1c-ipsec-ip4routing-scale-pdr}
    \end{figure}
