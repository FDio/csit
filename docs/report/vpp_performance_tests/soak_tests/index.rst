
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

.. _`soak tests`:

Soak Tests
==========

Long duration (30 minutes per test) soak tests are executed
using :ref:`plrsearch` algorithm. As the tests take long time,
only 12 test cases were executed, two runs each.

Additional information about graph data:

#. **Graph Title**: describes type of tests and soak test duration.

#. **X-axis Labels**: indices of test suites.

#. **Y-axis Labels**: estimated lower bounds for critical rate value in [Mpps].

#. **Graph Legend**: list of X-axis indices with CSIT test cases.

#. **Hover Information**: in general lists minimum, first quartile, median,
   third quartile, and maximum. As only two samples are used,
   minimum and maximum are not distinguished from quartiles.

.. note::

    Test results are stored in
    `build logs from FD.io vpp performance job 2n-skx`_ and
    `build logs from FD.io vpp performance job 2n-clx`_ with RF
    result files csit-vpp-perf-|srelease|-\*.zip
    `archived here <../../_static/archive/>`_.

.. raw:: latex

    \clearpage

2n-clx
------

.. raw:: html

    <center>
    <iframe id="ifrm01" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/soak-test-1.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{soak-test-1}
            \label{fig:soak-test-1}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="ifrm02" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/soak-test-2.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{soak-test-2}
            \label{fig:soak-test-2}
    \end{figure}

.. raw:: latex

    \clearpage

2n-skx
------

.. raw:: html

    <center>
    <iframe id="ifrm101" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/soak-test-2n-skx-1.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{soak-test-2n-skx-1}
            \label{fig:soak-test-2n-skx-1}
    \end{figure}

.. raw:: latex

    \clearpage

.. raw:: html

    <center>
    <iframe id="ifrm102" onload="setIframeHeight(this.id)" width="700" frameborder="0" scrolling="no" src="../../_static/vpp/soak-test-2n-skx-2.html"></iframe>
    <p><br></p>
    </center>

.. raw:: latex

    \begin{figure}[H]
        \centering
            \graphicspath{{../_build/_static/vpp/}}
            \includegraphics[clip, trim=0cm 0cm 5cm 0cm, width=0.70\textwidth]{soak-test-2n-skx-2}
            \label{fig:soak-test-2n-skx-2}
    \end{figure}
