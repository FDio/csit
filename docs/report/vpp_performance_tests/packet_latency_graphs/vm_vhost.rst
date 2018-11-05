
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

KVM VMs vhost-user
==================

This section includes summary graphs of VPP Phy-to-VM(s)-to-Phy packet
latency with with VM virtio and VPP vhost-user virtual interfaces
measured at 100% of discovered NDR throughput rate. Latency is reported
for VPP running in multiple configurations of VPP worker thread(s),
a.k.a. VPP data plane thread(s), and their physical CPU core(s)
placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/vm_vhost?h=rls1810>`_.

.. raw:: latex

    \clearpage

3n-hsw-x520
~~~~~~~~~~~

64b-1t1c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-x520-64b-1t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-1t1c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-1t1c-base-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-1t1c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-x520-64b-4t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-4t2c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-4t2c-base-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-4t2c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm04" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-x520-64b-1t1c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm05" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-1t1c-base-vm-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-1t1c-base-vm-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-1t1c-base-vm-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-x520-64b-2t2c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm06" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-2t2c-base-vm-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-2t2c-base-vm-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-2t2c-base-vm-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm07" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr-lat}
            \label{fig:vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm08" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr-lat}
            \label{fig:vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-x710
~~~~~~~~~~~

64b-1t1c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-x710-64b-1t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm09" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-1t1c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-1t1c-base-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-1t1c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-x710-64b-2t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm10" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-2t2c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-2t2c-base-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-2t2c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm12" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-x710-64b-1t1c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm13" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-1t1c-base-vm-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-1t1c-base-vm-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-1t1c-base-vm-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-x710-64b-2t2c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm14" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-2t2c-base-vm-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-2t2c-base-vm-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-2t2c-base-vm-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm15" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr-lat}
            \label{fig:vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm16" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr-lat}
            \label{fig:vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-xl710
~~~~~~~~~~~~

64b-1t1c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm17" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm18" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm19" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm20" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm21" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-vm-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-vm-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-vm-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm22" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-vm-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-vm-ndr-lat}
            \label{fig:vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-vm-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm23" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr-lat}
            \label{fig:vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm24" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr-lat}
            \label{fig:vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr-lat}
    \end{figure}

3n-skx-x710
~~~~~~~~~~~

64b-2t1c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-skx-x710-64b-2t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm25" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-2t1c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-2t1c-base-ndr-lat}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-2t1c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-skx-x710-64b-2t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm26" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-2t2c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-2t2c-base-ndr-lat}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-2t2c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-skx-x710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm27" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-2t1c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-2t1c-base_and_scale-ndr-lat}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-2t1c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-skx-x710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm28" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-2t2c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-2t2c-base_and_scale-ndr-lat}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-2t2c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-skx-x710-64b-2t1c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm29" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-2t1c-base-vm-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-2t1c-base-vm-ndr-lat}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-2t1c-base-vm-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-3n-skx-x710-64b-2t2c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm30" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-2t2c-base-vm-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-2t2c-base-vm-ndr-lat}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-2t2c-base-vm-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm31" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr-lat}
            \label{fig:vhost-ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-ip4-3n-skx-x710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm32" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-skx-x710-64b-2t2c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-skx-x710-64b-2t2c-base_and_scale-ndr-lat}
            \label{fig:vhost-ip4-3n-skx-x710-64b-2t2c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

2n-skx-x710
~~~~~~~~~~~

64b-2t1c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-2n-skx-x710-64b-2t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm33" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-2t1c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-2t1c-base-ndr-lat}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-2t1c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-2n-skx-x710-64b-2t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm34" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-2t2c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-2t2c-base-ndr-lat}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-2t2c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-2n-skx-x710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm35" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-2t1c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-2t1c-base_and_scale-ndr-lat}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-2t1c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-2n-skx-x710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm36" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-2t2c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-2t2c-base_and_scale-ndr-lat}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-2t2c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-2n-skx-x710-64b-2t1c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm37" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-2t1c-base-vm-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-2t1c-base-vm-ndr-lat}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-2t1c-base-vm-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-2n-skx-x710-64b-2t2c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm38" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-2t2c-base-vm-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-2t2c-base-vm-ndr-lat}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-2t2c-base-vm-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-ip4-2n-skx-x710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm39" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-2n-skx-x710-64b-2t1c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-2n-skx-x710-64b-2t1c-base_and_scale-ndr-lat}
            \label{fig:vhost-ip4-2n-skx-x710-64b-2t1c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-ip4-2n-skx-x710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm40" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-2n-skx-x710-64b-2t2c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-2n-skx-x710-64b-2t2c-base_and_scale-ndr-lat}
            \label{fig:vhost-ip4-2n-skx-x710-64b-2t2c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

2n-skx-xxv710
~~~~~~~~~~~~~

64b-2t1c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm41" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-ndr-lat}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-2n-skx-xxv710-64b-2t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm42" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-2t2c-base-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-2t2c-base-ndr-lat}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-2t2c-base-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm43" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr-lat}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-2n-skx-xxv710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm44" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-2t2c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-2t2c-base_and_scale-ndr-lat}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-2t2c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm45" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-vm-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-vm-ndr-lat}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-vm-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-l2sw-2n-skx-xxv710-64b-2t2c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm46" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-2t2c-base-vm-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-2t2c-base-vm-ndr-lat}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-2t2c-base-vm-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm47" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr-lat}
            \label{fig:vhost-ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Latency: vhost-ip4-2n-skx-xxv710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm48" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-2n-skx-xxv710-64b-2t2c-base_and_scale-ndr-lat.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-2n-skx-xxv710-64b-2t2c-base_and_scale-ndr-lat}
            \label{fig:vhost-ip4-2n-skx-xxv710-64b-2t2c-base_and_scale-ndr-lat}
    \end{figure}

.. raw:: latex

    \clearpage
