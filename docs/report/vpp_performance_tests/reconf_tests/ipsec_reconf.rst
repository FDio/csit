
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

.. _ipsec_reconf:

Internet Protocol Security
==========================

Additional information about graph data:

#. **Graph Title**: describes tested VPP packet path.

#. **X-axis Labels**: indices of individual test suites as listed in
   Graph Legend.

#. **Y-axis Labels**: measured Effective Blocked Time [s] values.

#. **Graph Legend**: lists X-axis indices with associated CSIT test
   suites executed to generate graphed test results and the average value
   of packet loss (measured in packets).

#. **Hover Information**: lists minimum, first quartile, median,
   third quartile, and maximum. If either type of outlier is present the
   whisker on the appropriate side is taken to 1.5×IQR from the quartile
   (the "inner fence") rather than the max or min, and individual outlying
   data points are displayed as unfilled circles (for suspected outliers)
   or filled circles (for outliers). (The "outer fence" is 3×IQR from the
   quartile.)

.. note::

    Test results are stored in
    `FD.io test executor vpp performance job 3n-hsw`_ with RF
    result files csit-vpp-perf-|srelease|-\*.zip
    `archived here <../../_static/archive/>`_.

.. raw:: latex

    \clearpage

3n-hsw-xl710
~~~~~~~~~~~~

64b-ethip4ipsec4tnlsw
---------------------

1t1c
::::

.. raw:: html

    <center>
    <iframe id="001" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-64b-1t1c-ethip4ipsec4tnlsw-1atnl-ip4base-reconf.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-64b-1t1c-ethip4ipsec4tnlsw-1atnl-ip4base-reconf}
            \label{fig:3n-hsw-xl710-64b-1t1c-ethip4ipsec4tnlsw-1atnl-ip4base-reconf}
    \end{figure}

.. raw:: latex

    \clearpage

2t2c
::::

.. raw:: html

    <center>
    <iframe id="002" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-64b-2t2c-ethip4ipsec4tnlsw-1atnl-ip4base-reconf.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-64b-2t2c-ethip4ipsec4tnlsw-1atnl-ip4base-reconf}
            \label{fig:3n-hsw-xl710-64b-2t2c-ethip4ipsec4tnlsw-1atnl-ip4base-reconf}
    \end{figure}

.. raw:: latex

    \clearpage

4t4c
::::

.. raw:: html

    <center>
    <iframe id="003" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-64b-4t4c-ethip4ipsec4tnlsw-1atnl-ip4base-reconf.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-64b-4t4c-ethip4ipsec4tnlsw-1atnl-ip4base-reconf}
            \label{fig:3n-hsw-xl710-64b-4t4c-ethip4ipsec4tnlsw-1atnl-ip4base-reconf}
    \end{figure}

.. raw:: latex

    \clearpage

64b-ethip4ipsec1000tnlsw
------------------------

1t1c
::::

.. raw:: html

    <center>
    <iframe id="101" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-64b-1t1c-ethip4ipsec1000tnlsw-1atnl-ip4base-reconf.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-64b-1t1c-ethip4ipsec1000tnlsw-1atnl-ip4base-reconf}
            \label{fig:3n-hsw-xl710-64b-1t1c-ethip4ipsec1000tnlsw-1atnl-ip4base-reconf}
    \end{figure}

.. raw:: latex

    \clearpage

2t2c
::::

.. raw:: html

    <center>
    <iframe id="102" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-64b-2t2c-ethip4ipsec1000tnlsw-1atnl-ip4base-reconf.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-64b-2t2c-ethip4ipsec1000tnlsw-1atnl-ip4base-reconf}
            \label{fig:3n-hsw-xl710-64b-2t2c-ethip4ipsec1000tnlsw-1atnl-ip4base-reconf}
    \end{figure}

.. raw:: latex

    \clearpage

4t4c
::::

.. raw:: html

    <center>
    <iframe id="103" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-64b-4t4c-ethip4ipsec1000tnlsw-1atnl-ip4base-reconf.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-64b-4t4c-ethip4ipsec1000tnlsw-1atnl-ip4base-reconf}
            \label{fig:3n-hsw-xl710-64b-4t4c-ethip4ipsec1000tnlsw-1atnl-ip4base-reconf}
    \end{figure}

.. raw:: latex

    \clearpage

64b-ethip4ipsec60000tnlsw
-------------------------

1t1c
::::

.. raw:: html

    <center>
    <iframe id="201" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-64b-1t1c-ethip4ipsec60000tnlsw-1atnl-ip4base-reconf.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-64b-1t1c-ethip4ipsec60000tnlsw-1atnl-ip4base-reconf}
            \label{fig:3n-hsw-xl710-64b-1t1c-ethip4ipsec60000tnlsw-1atnl-ip4base-reconf}
    \end{figure}

.. raw:: latex

    \clearpage

2t2c
::::

.. raw:: html

    <center>
    <iframe id="202" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-64b-2t2c-ethip4ipsec60000tnlsw-1atnl-ip4base-reconf.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-64b-2t2c-ethip4ipsec60000tnlsw-1atnl-ip4base-reconf}
            \label{fig:3n-hsw-xl710-64b-2t2c-ethip4ipsec60000tnlsw-1atnl-ip4base-reconf}
    \end{figure}

.. raw:: latex

    \clearpage

4t4c
::::

.. raw:: html

    <center>
    <iframe id="203" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/3n-hsw-xl710-64b-4t4c-ethip4ipsec60000tnlsw-1atnl-ip4base-reconf.html"></iframe>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{3n-hsw-xl710-64b-4t4c-ethip4ipsec60000tnlsw-1atnl-ip4base-reconf}
            \label{fig:3n-hsw-xl710-64b-4t4c-ethip4ipsec60000tnlsw-1atnl-ip4base-reconf}
    \end{figure}
