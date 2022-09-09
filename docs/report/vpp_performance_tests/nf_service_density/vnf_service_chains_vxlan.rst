
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

.. _vnf_service_chains_tunnels:

VNF Service Chains Tunnels
==========================

.. todo::

    Add introduction.

Additional information about graph data:

#. **Graph Title**: describes tested packet path including VNF workload
   running in each VM.

#. **X-axis Labels**: VNFs per service chain.

#. **Y-axis Labels**: number of service chains.

#. **Z-axis Color Scale**: lists 64B/IMIX Packet Throughput
   (mean MRR/NDR/PDR value) in Mpps or the Relative Difference.

#. **Hover Information**: specific test substring listing vhost-chain-vm
   combinations, number of runs executed, mean MRR/NDR/PDR throughput in Mpps,
   standard deviation for both configurations and their relative difference.

.. note::

    Test results are stored in
    `build logs from FD.io vpp performance job 2n-icx`_,
    `build logs from FD.io vpp performance job 2n-clx`_ with RF
    result files csit-vpp-perf-|srelease|-\*.zip
    `archived here <../../_static/archive/>`_.

.. raw:: latex

    \clearpage

2n-icx-xxv710-mrr
~~~~~~~~~~~~~~~~~

imix-2t1c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="icx01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-icx-xxv710-imix-2t1c-base-vsc-vxlan-mrr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-icx-xxv710-imix-2t1c-base-vsc-vxlan-mrr}
            \label{fig:l2bd-2n-icx-xxv710-imix-2t1c-base-vsc-vxlan-mrr}
    \end{figure}

.. raw:: latex

    \clearpage

imix-4t2c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="icx02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-icx-xxv710-imix-4t2c-base-vsc-vxlan-mrr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-icx-xxv710-imix-4t2c-base-vsc-vxlan-mrr}
            \label{fig:l2bd-2n-icx-xxv710-imix-4t2c-base-vsc-vxlan-mrr}
    \end{figure}

.. raw:: latex

    \clearpage

imix-8t4c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="icx03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-icx-xxv710-imix-8t4c-base-vsc-vxlan-mrr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-icx-xxv710-imix-8t4c-base-vsc-vxlan-mrr}
            \label{fig:l2bd-2n-icx-xxv710-imix-8t4c-base-vsc-vxlan-mrr}
    \end{figure}

.. raw:: latex

    \clearpage

2n-icx-xxv710-ndr
~~~~~~~~~~~~~~~~~

imix-2t1c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="icx07" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-icx-xxv710-imix-2t1c-base-vsc-vxlan-ndr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-icx-xxv710-imix-2t1c-base-vsc-vxlan-ndr}
            \label{fig:l2bd-2n-icx-xxv710-imix-2t1c-base-vsc-vxlan-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

imix-4t2c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="icx08" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-icx-xxv710-imix-4t2c-base-vsc-vxlan-ndr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-icx-xxv710-imix-4t2c-base-vsc-vxlan-ndr}
            \label{fig:l2bd-2n-icx-xxv710-imix-4t2c-base-vsc-vxlan-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

imix-8t4c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="icx09" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-icx-xxv710-imix-8t4c-base-vsc-vxlan-ndr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-icx-xxv710-imix-8t4c-base-vsc-vxlan-ndr}
            \label{fig:l2bd-2n-icx-xxv710-imix-8t4c-base-vsc-vxlan-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

2n-icx-xxv710-pdr
~~~~~~~~~~~~~~~~~

imix-2t1c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="icx13" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-icx-xxv710-imix-2t1c-base-vsc-vxlan-pdr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-icx-xxv710-imix-2t1c-base-vsc-vxlan-pdr}
            \label{fig:l2bd-2n-icx-xxv710-imix-2t1c-base-vsc-vxlan-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

imix-4t2c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="icx14" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-icx-xxv710-imix-4t2c-base-vsc-vxlan-pdr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-icx-xxv710-imix-4t2c-base-vsc-vxlan-pdr}
            \label{fig:l2bd-2n-icx-xxv710-imix-4t2c-base-vsc-vxlan-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

imix-8t4c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="icx15" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-icx-xxv710-imix-8t4c-base-vsc-vxlan-pdr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-icx-xxv710-imix-8t4c-base-vsc-vxlan-pdr}
            \label{fig:l2bd-2n-icx-xxv710-imix-8t4c-base-vsc-vxlan-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

2n-clx-xxv710-mrr
~~~~~~~~~~~~~~~~~

imix-2t1c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="ifrm204" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-clx-xxv710-imix-2t1c-base-vsc-vxlan-mrr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-clx-xxv710-imix-2t1c-base-vsc-vxlan-mrr}
            \label{fig:l2bd-2n-clx-xxv710-imix-2t1c-base-vsc-vxlan-mrr}
    \end{figure}

.. raw:: latex

    \clearpage

imix-4t2c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="ifrm205" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-clx-xxv710-imix-4t2c-base-vsc-vxlan-mrr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-clx-xxv710-imix-4t2c-base-vsc-vxlan-mrr}
            \label{fig:l2bd-2n-clx-xxv710-imix-4t2c-base-vsc-vxlan-mrr}
    \end{figure}

.. raw:: latex

    \clearpage

imix-8t4c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="ifrm206" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-clx-xxv710-imix-8t4c-base-vsc-vxlan-mrr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-clx-xxv710-imix-8t4c-base-vsc-vxlan-mrr}
            \label{fig:l2bd-2n-clx-xxv710-imix-8t4c-base-vsc-vxlan-mrr}
    \end{figure}

.. raw:: latex

    \clearpage

2n-clx-xxv710-ndr
~~~~~~~~~~~~~~~~~

imix-2t1c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="ifrm210" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-clx-xxv710-imix-2t1c-base-vsc-vxlan-ndr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-clx-xxv710-imix-2t1c-base-vsc-vxlan-ndr}
            \label{fig:l2bd-2n-clx-xxv710-imix-2t1c-base-vsc-vxlan-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

imix-4t2c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="ifrm211" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-clx-xxv710-imix-4t2c-base-vsc-vxlan-ndr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-clx-xxv710-imix-4t2c-base-vsc-vxlan-ndr}
            \label{fig:l2bd-2n-clx-xxv710-imix-4t2c-base-vsc-vxlan-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

imix-8t4c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="ifrm212" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-clx-xxv710-imix-8t4c-base-vsc-vxlan-ndr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-clx-xxv710-imix-8t4c-base-vsc-vxlan-ndr}
            \label{fig:l2bd-2n-clx-xxv710-imix-8t4c-base-vsc-vxlan-ndr}
    \end{figure}

.. raw:: latex

    \clearpage

2n-clx-xxv710-pdr
~~~~~~~~~~~~~~~~~

imix-2t1c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="ifrm216" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-clx-xxv710-imix-2t1c-base-vsc-vxlan-pdr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-clx-xxv710-imix-2t1c-base-vsc-vxlan-pdr}
            \label{fig:l2bd-2n-clx-xxv710-imix-2t1c-base-vsc-vxlan-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

imix-4t2c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="ifrm217" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-clx-xxv710-imix-4t2c-base-vsc-vxlan-pdr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-clx-xxv710-imix-4t2c-base-vsc-vxlan-pdr}
            \label{fig:l2bd-2n-clx-xxv710-imix-4t2c-base-vsc-vxlan-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

imix-8t4c-eth-l2bd
------------------

.. raw:: html

    <center>
    <iframe id="ifrm218" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/l2bd-2n-clx-xxv710-imix-8t4c-base-vsc-vxlan-pdr.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{l2bd-2n-clx-xxv710-imix-8t4c-base-vsc-vxlan-pdr}
            \label{fig:l2bd-2n-clx-xxv710-imix-8t4c-base-vsc-vxlan-pdr}
    \end{figure}
