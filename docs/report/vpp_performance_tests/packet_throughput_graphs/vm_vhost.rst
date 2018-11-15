
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

.. _KVM_VMs_vhost:

KVM VMs vhost-user
==================

Following sections include summary graphs of VPP Phy-to-VM(s)-to-Phy
performance with VM virtio and VPP vhost-user virtual interfaces,
including NDR throughput (zero packet loss) and PDR throughput (<0.5%
packet loss). Performance is reported for VPP running in multiple
configurations of VPP worker thread(s), a.k.a. VPP data plane thread(s),
and their physical CPU core(s) placement.

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

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x520-64b-1t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-1t1c-base-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-1t1c-base-ndr}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-1t1c-base-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x520-64b-1t1c-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-1t1c-base-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-1t1c-base-pdr}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-1t1c-base-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x520-64b-2t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm03" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-2t2c-base-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-2t2c-base-ndr}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-2t2c-base-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x520-64b-2t2c-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm04" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-2t2c-base-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-2t2c-base-pdr}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-2t2c-base-pdr}
    \end{figure}

..
    .. raw:: latex

        \clearpage

    64b-1t1c-base_and_scale-l2sw
    ----------------------------

    .. raw:: html

        <center><b>

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm05" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-ndr}
                \label{fig:vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm06" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-pdr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-pdr}
                \label{fig:vhost-l2sw-3n-hsw-x520-64b-1t1c-base_and_scale-pdr}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-2t2c-base_and_scale-l2sw
    ----------------------------

    .. raw:: html

        <center><b>

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm07" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-ndr}
                \label{fig:vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm08" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-pdr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-pdr}
                \label{fig:vhost-l2sw-3n-hsw-x520-64b-2t2c-base_and_scale-pdr}
        \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x520-64b-1t1c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm09" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-1t1c-base-vm-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-1t1c-base-vm-ndr}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-1t1c-base-vm-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x520-64b-1t1c-base-vm-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm10" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-1t1c-base-vm-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-1t1c-base-vm-pdr}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-1t1c-base-vm-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x520-64b-2t2c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm11" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-2t2c-base-vm-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-2t2c-base-vm-ndr}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-2t2c-base-vm-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x520-64b-2t2c-base-vm-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm12" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-2t2c-base-vm-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-2t2c-base-vm-pdr}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-2t2c-base-vm-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm13" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr}
            \label{fig:vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm14" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-pdr}
            \label{fig:vhost-ip4-3n-hsw-x520-64b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm15" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr}
            \label{fig:vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm16" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-pdr}
            \label{fig:vhost-ip4-3n-hsw-x520-64b-2t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-x710
~~~~~~~~~~~

64b-1t1c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x710-64b-1t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm17" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-1t1c-base-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-1t1c-base-ndr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-1t1c-base-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x710-64b-1t1c-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm18" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-1t1c-base-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-1t1c-base-pdr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-1t1c-base-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x710-64b-2t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm19" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-2t2c-base-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-2t2c-base-ndr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-2t2c-base-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x710-64b-2t2c-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm20" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-2t2c-base-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-2t2c-base-pdr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-2t2c-base-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm21" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-ndr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm22" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-pdr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm23" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-ndr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm24" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-pdr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-2t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x710-64b-1t1c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm25" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-1t1c-base-vm-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-1t1c-base-vm-ndr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-1t1c-base-vm-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x710-64b-1t1c-base-vm-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm26" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-1t1c-base-vm-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-1t1c-base-vm-pdr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-1t1c-base-vm-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x710-64b-2t2c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm27" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-2t2c-base-vm-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-2t2c-base-vm-ndr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-2t2c-base-vm-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-hsw-x710-64b-2t2c-base-vm-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm28" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-2t2c-base-vm-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-2t2c-base-vm-pdr}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-2t2c-base-vm-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-1t1c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm29" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr}
            \label{fig:vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm30" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-pdr}
            \label{fig:vhost-ip4-3n-hsw-x710-64b-1t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t2c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm31" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr}
            \label{fig:vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm32" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-pdr}
            \label{fig:vhost-ip4-3n-hsw-x710-64b-2t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

..
    3n-hsw-xl710
    ~~~~~~~~~~~~

    64b-1t1c-base-l2sw
    ------------------

    .. raw:: html

        <center><b>

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm33" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-ndr}
                \label{fig:vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm34" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-pdr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-pdr}
                \label{fig:vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-pdr}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-2t2c-base-l2sw
    ------------------

    .. raw:: html

        <center><b>

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm35" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-ndr}
                \label{fig:vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm36" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-pdr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-pdr}
                \label{fig:vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-pdr}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-1t1c-base_and_scale-l2sw
    ----------------------------

    .. raw:: html

        <center><b>

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm37" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr}
                \label{fig:vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm38" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr}
                \label{fig:vhost-l2sw-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-2t2c-base_and_scale-l2sw
    ----------------------------

    .. raw:: html

        <center><b>

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm39" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr}
                \label{fig:vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm40" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr}
                \label{fig:vhost-l2sw-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-1t1c-base-vm-l2sw
    ---------------------

    .. raw:: html

        <center><b>

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-vm-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm41" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-vm-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-vm-ndr}
                \label{fig:vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-vm-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-vm-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm42" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-vm-pdr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-vm-pdr}
                \label{fig:vhost-l2sw-3n-hsw-xl710-64b-1t1c-base-vm-pdr}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-2t2c-base-vm-l2sw
    ---------------------

    .. raw:: html

        <center><b>

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-vm-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm43" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-vm-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-vm-ndr}
                \label{fig:vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-vm-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Packet Throughput: vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-vm-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm44" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-vm-pdr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-vm-pdr}
                \label{fig:vhost-l2sw-3n-hsw-xl710-64b-2t2c-base-vm-pdr}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-1t1c-base_and_scale-ip4
    ---------------------------

    .. raw:: html

        <center><b>

    :index:`Packet Throughput: vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm45" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr}
                \label{fig:vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Packet Throughput: vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm46" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr}
                \label{fig:vhost-ip4-3n-hsw-xl710-64b-1t1c-base_and_scale-pdr}
        \end{figure}

    .. raw:: latex

        \clearpage

    64b-2t2c-base_and_scale-ip4
    ---------------------------

    .. raw:: html

        <center><b>

    :index:`Packet Throughput: vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr`

    .. raw:: html

        </b>
        <iframe id="ifrm47" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr}
                \label{fig:vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-ndr}
        \end{figure}

    .. raw:: html

        <center><b>

    .. raw:: latex

        \clearpage

    :index:`Packet Throughput: vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr`

    .. raw:: html

        </b>
        <iframe id="ifrm48" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr.html"></iframe>
        <p><br><br></p>
        </center>

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_build/_static/vpp/}}
                \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr}
                \label{fig:vhost-ip4-3n-hsw-xl710-64b-2t2c-base_and_scale-pdr}
        \end{figure}

.. raw:: latex

    \clearpage

3n-skx-x710
~~~~~~~~~~~

64b-2t1c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-skx-x710-64b-2t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm49" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-2t1c-base-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-2t1c-base-ndr}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-2t1c-base-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-skx-x710-64b-2t1c-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm50" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-2t1c-base-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-2t1c-base-pdr}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-2t1c-base-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-skx-x710-64b-4t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm51" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-4t2c-base-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-4t2c-base-ndr}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-4t2c-base-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-skx-x710-64b-4t2c-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm52" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-4t2c-base-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-4t2c-base-pdr}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-4t2c-base-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-skx-x710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm53" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-2t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-2t1c-base_and_scale-ndr}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-2t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-skx-x710-64b-2t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm54" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-2t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-2t1c-base_and_scale-pdr}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-2t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-skx-x710-64b-4t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm55" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-4t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-4t2c-base_and_scale-ndr}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-4t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-skx-x710-64b-4t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm56" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-4t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-4t2c-base_and_scale-pdr}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-4t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-skx-x710-64b-2t1c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm57" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-2t1c-base-vm-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-2t1c-base-vm-ndr}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-2t1c-base-vm-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-skx-x710-64b-2t1c-base-vm-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm58" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-2t1c-base-vm-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-2t1c-base-vm-pdr}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-2t1c-base-vm-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-3n-skx-x710-64b-4t2c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm59" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-4t2c-base-vm-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-4t2c-base-vm-ndr}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-4t2c-base-vm-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-3n-skx-x710-64b-4t2c-base-vm-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm60" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-3n-skx-x710-64b-4t2c-base-vm-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-skx-x710-64b-4t2c-base-vm-pdr}
            \label{fig:vhost-l2sw-3n-skx-x710-64b-4t2c-base-vm-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm61" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr}
            \label{fig:vhost-ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-ip4-3n-skx-x710-64b-2t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm62" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-skx-x710-64b-2t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-skx-x710-64b-2t1c-base_and_scale-pdr}
            \label{fig:vhost-ip4-3n-skx-x710-64b-2t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-ip4-3n-skx-x710-64b-4t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm63" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-skx-x710-64b-4t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-skx-x710-64b-4t2c-base_and_scale-ndr}
            \label{fig:vhost-ip4-3n-skx-x710-64b-4t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-ip4-3n-skx-x710-64b-4t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm64" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-3n-skx-x710-64b-4t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-skx-x710-64b-4t2c-base_and_scale-pdr}
            \label{fig:vhost-ip4-3n-skx-x710-64b-4t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

2n-skx-x710
~~~~~~~~~~~

64b-2t1c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-2n-skx-x710-64b-2t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm65" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-2t1c-base-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-2t1c-base-ndr}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-2t1c-base-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-2n-skx-x710-64b-2t1c-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm66" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-2t1c-base-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-2t1c-base-pdr}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-2t1c-base-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-2n-skx-x710-64b-4t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm67" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-4t2c-base-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-4t2c-base-ndr}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-4t2c-base-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-2n-skx-x710-64b-4t2c-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm68" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-4t2c-base-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-4t2c-base-pdr}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-4t2c-base-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-2n-skx-x710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm69" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-2t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-2t1c-base_and_scale-ndr}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-2t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-2n-skx-x710-64b-2t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm70" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-2t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-2t1c-base_and_scale-pdr}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-2t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-2n-skx-x710-64b-4t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm71" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-4t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-4t2c-base_and_scale-ndr}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-4t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-2n-skx-x710-64b-4t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm72" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-4t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-4t2c-base_and_scale-pdr}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-4t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-2n-skx-x710-64b-2t1c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm73" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-2t1c-base-vm-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-2t1c-base-vm-ndr}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-2t1c-base-vm-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-2n-skx-x710-64b-2t1c-base-vm-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm74" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-2t1c-base-vm-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-2t1c-base-vm-pdr}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-2t1c-base-vm-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-2n-skx-x710-64b-4t2c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm75" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-4t2c-base-vm-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-4t2c-base-vm-ndr}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-4t2c-base-vm-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-2n-skx-x710-64b-4t2c-base-vm-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm76" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-x710-64b-4t2c-base-vm-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-x710-64b-4t2c-base-vm-pdr}
            \label{fig:vhost-l2sw-2n-skx-x710-64b-4t2c-base-vm-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-ip4-2n-skx-x710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm77" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-2n-skx-x710-64b-2t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-2n-skx-x710-64b-2t1c-base_and_scale-ndr}
            \label{fig:vhost-ip4-2n-skx-x710-64b-2t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-ip4-2n-skx-x710-64b-2t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm78" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-2n-skx-x710-64b-2t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-2n-skx-x710-64b-2t1c-base_and_scale-pdr}
            \label{fig:vhost-ip4-2n-skx-x710-64b-2t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-ip4-2n-skx-x710-64b-4t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm79" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-2n-skx-x710-64b-4t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-2n-skx-x710-64b-4t2c-base_and_scale-ndr}
            \label{fig:vhost-ip4-2n-skx-x710-64b-4t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-ip4-2n-skx-x710-64b-4t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm80" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-2n-skx-x710-64b-4t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-2n-skx-x710-64b-4t2c-base_and_scale-pdr}
            \label{fig:vhost-ip4-2n-skx-x710-64b-4t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

2n-skx-xxv710
~~~~~~~~~~~~~

64b-2t1c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm81" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-ndr}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm82" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-pdr}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base-l2sw
------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm83" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-ndr}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm84" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-pdr}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm85" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-2n-skx-xxv710-64b-2t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm86" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-2t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-2t1c-base_and_scale-pdr}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-2t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base_and_scale-l2sw
----------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-2n-skx-xxv710-64b-4t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm87" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-4t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-4t2c-base_and_scale-ndr}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-4t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-2n-skx-xxv710-64b-4t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm88" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-4t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-4t2c-base_and_scale-pdr}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-4t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm89" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-vm-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-vm-ndr}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-vm-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-vm-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm90" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-vm-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-vm-pdr}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-2t1c-base-vm-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base-vm-l2sw
---------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-vm-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm91" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-vm-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-vm-ndr}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-vm-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-vm-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm92" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-vm-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-vm-pdr}
            \label{fig:vhost-l2sw-2n-skx-xxv710-64b-4t2c-base-vm-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-2t1c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm93" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr}
            \label{fig:vhost-ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm94" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-pdr}
            \label{fig:vhost-ip4-2n-skx-xxv710-64b-2t1c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage

64b-4t2c-base_and_scale-ip4
---------------------------

.. raw:: html

    <center><b>

:index:`Packet Throughput: vhost-ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm95" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-ndr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-ndr}
            \label{fig:vhost-ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-ndr}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Packet Throughput: vhost-ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm96" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/vhost-ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-pdr.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-pdr}
            \label{fig:vhost-ip4-2n-skx-xxv710-64b-4t2c-base_and_scale-pdr}
    \end{figure}

.. raw:: latex

    \clearpage
