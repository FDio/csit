
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

IPSec IPv4 Routing
==================

Following sections include summary graphs of VPP Phy-to-Phy performance with
IPSec encryption used in combination with IPv4 routed-forwarding,
including NDR throughput (zero packet loss) and PDR throughput (<0.5%
packet loss). VPP IPSec encryption is accelerated using DPDK cryptodev
library driving Intel Quick Assist (QAT) crypto PCIe hardware cards.
Performance is reported for VPP running in multiple configurations of
VPP worker thread(s), a.k.a. VPP data plane thread(s), and their
physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/crypto?h=rls1810>`_.

.. toctree::

    ipsec-3n-hsw-xl710
