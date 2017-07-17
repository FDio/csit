IPSec Crypto HW: IP4 Routed-Forwarding
======================================

Following sections include summary graphs of VPP Phy-to-Phy performance with
IPSec encryption used in combination with IPv4 routed-forwarding,
including NDR throughput (zero packet loss) and PDR throughput (<0.5%
packet loss). VPP IPSec encryption is accelerated using DPDK cryptodev
library driving Intel Quick Assist (QAT) crypto PCIe hardware cards.
Performance is reported for VPP running in multiple configurations of
VPP worker thread(s), a.k.a. VPP data plane thread(s), and their
physical CPU core(s) placement.

Note: only 1,000 scale IPSec tunnel test cases are plotted. Single IPSec
tunnel test cases are listed in regex outputs, but marked {NOT PLOTTED}
due to the current limitation of auto-plotting scripts. For all test
result data please refere to **Detailed Test Results** section.

NDR Throughput
~~~~~~~~~~~~~~

VPP NDR 64B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-ipsechw-ndrdisc.html"></iframe>

*Figure 1. VPP 1thread 1core - NDR Throughput for Phy-to-Phy IPSEC HW.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. program-output:: cd ../../ && set -x && cd tests/vpp/perf/crypto && grep -E "64B-1t1c-.*ipsec.*-ndrdisc" *
   :shell:

VPP NDR 64B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-ipsechw-ndrdisc.html"></iframe>

*Figure 2. VPP 2threads 2cores - NDR Throughput for Phy-to-Phy IPSEC HW.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. program-output:: cd ../../ && set -x && cd tests/vpp/perf/crypto && grep -E "64B-2t2c-.*ipsec.*-ndrdisc" *
   :shell:

PDR Throughput
~~~~~~~~~~~~~~

VPP PDR 64B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-ipsechw-pdrdisc.html"></iframe>

*Figure 3. VPP 1thread 1core - PDR Throughput for Phy-to-Phy IPSEC HW.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. program-output:: cd ../../ && set -x && cd tests/vpp/perf/crypto && grep -E "64B-1t1c-.*ipsec.*-pdrdisc" *
   :shell:

VPP PDR 64B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-ipsechw-pdrdisc.html"></iframe>

*Figure 4. VPP 2thread 2core - PDR Throughput for Phy-to-Phy IPSEC HW.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. program-output:: cd ../../ && set -x && cd tests/vpp/perf/crypto && grep -E "64B-2t2c-.*ipsec.*-pdrdisc" *
   :shell:
