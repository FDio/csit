
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

Following sections include Throughput Speedup Analysis for VPP multi-
core multi-thread configurations with no Hyper-Threading, specifically
for tested 2t2c (2threads, 2cores) and 4t4c scenarios. 1t1c throughput
results are used as a reference for reported speedup ratio. Input data
used for the graphs comes from Phy-to-Phy 64B performance tests with
VM vhost-user, including NDR throughput (zero packet loss) and
PDR throughput (<0.5% packet loss).

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/vm_vhost?h=rls1807>`_.

3n-hsw-x520
~~~~~~~~~~~

64b-base_and_scale-l2sw
-----------------------

.. raw:: html

    <center><b>

:index:`Speedup: vhost-l2sw-3n-hsw-x520-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no"src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-base_and_scale-ndr-tsa}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup: vhost-l2sw-3n-hsw-x520-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no"src="../../_static/vpp/vhost-l2sw-3n-hsw-x520-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x520-64b-base_and_scale-pdr-tsa}
            \label{fig:vhost-l2sw-3n-hsw-x520-64b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-base_and_scale-ip4
----------------------

.. raw:: html

    <center><b>

:index:`Speedup: vhost-ip4-3n-hsw-x520-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no"src="../../_static/vpp/vhost-ip4-3n-hsw-x520-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x520-64b-base_and_scale-ndr-tsa}
            \label{fig:vhost-ip4-3n-hsw-x520-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup: vhost-ip4-3n-hsw-x520-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no"src="../../_static/vpp/vhost-ip4-3n-hsw-x520-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x520-64b-base_and_scale-pdr-tsa}
            \label{fig:vhost-ip4-3n-hsw-x520-64b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-x710
~~~~~~~~~~~

64b-base_and_scale-l2sw
-----------------------

.. raw:: html

    <center><b>

:index:`Speedup: vhost-l2sw-3n-hsw-x710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no"src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-base_and_scale-ndr-tsa}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup: vhost-l2sw-3n-hsw-x710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no"src="../../_static/vpp/vhost-l2sw-3n-hsw-x710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-x710-64b-base_and_scale-pdr-tsa}
            \label{fig:vhost-l2sw-3n-hsw-x710-64b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-base_and_scale-ip4
----------------------

.. raw:: html

    <center><b>

:index:`Speedup: vhost-ip4-3n-hsw-x710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no"src="../../_static/vpp/vhost-ip4-3n-hsw-x710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x710-64b-base_and_scale-ndr-tsa}
            \label{fig:vhost-ip4-3n-hsw-x710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup: vhost-ip4-3n-hsw-x710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no"src="../../_static/vpp/vhost-ip4-3n-hsw-x710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-x710-64b-base_and_scale-pdr-tsa}
            \label{fig:vhost-ip4-3n-hsw-x710-64b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

3n-hsw-xl710
~~~~~~~~~~~~

64b-base_and_scale-l2sw
-----------------------

.. raw:: html

    <center><b>

:index:`Speedup: vhost-l2sw-3n-hsw-xl710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no"src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-base_and_scale-ndr-tsa}
            \label{fig:vhost-l2sw-3n-hsw-xl710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup: vhost-l2sw-3n-hsw-xl710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no"src="../../_static/vpp/vhost-l2sw-3n-hsw-xl710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-l2sw-3n-hsw-xl710-64b-base_and_scale-pdr-tsa}
            \label{fig:vhost-l2sw-3n-hsw-xl710-64b-base_and_scale-pdr-tsa}
    \end{figure}

.. raw:: latex

    \clearpage

64b-base_and_scale-ip4
----------------------

.. raw:: html

    <center><b>

:index:`Speedup: vhost-ip4-3n-hsw-xl710-64b-base_and_scale-ndr`

.. raw:: html

    </b>
    <iframe id="ifrm" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no"src="../../_static/vpp/vhost-ip4-3n-hsw-xl710-64b-base_and_scale-ndr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-xl710-64b-base_and_scale-ndr-tsa}
            \label{fig:vhost-ip4-3n-hsw-xl710-64b-base_and_scale-ndr-tsa}
    \end{figure}

.. raw:: html

    <center><b>

.. raw:: latex

    \clearpage

:index:`Speedup: vhost-ip4-3n-hsw-xl710-64b-base_and_scale-pdr`

.. raw:: html

    </b>
    <iframe id="ifrm" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no"src="../../_static/vpp/vhost-ip4-3n-hsw-xl710-64b-base_and_scale-pdr-tsa.html"></iframe>
    <p><br><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 8cm 5cm 0cm, width=0.70\textwidth]{vhost-ip4-3n-hsw-xl710-64b-base_and_scale-pdr-tsa}
            \label{fig:vhost-ip4-3n-hsw-xl710-64b-base_and_scale-pdr-tsa}
    \end{figure}
