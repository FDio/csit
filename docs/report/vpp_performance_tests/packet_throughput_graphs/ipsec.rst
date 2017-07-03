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

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/crypto
    $ grep -E "64B-1t1c-.*ipsec.*-ndrdisc" *

    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-aes-gcm-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecscale1ip4-ip4base-interfaces-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-aes-gcm-ndrpdrdisc.robot:| tc03-64B-1t1c-ethip4ipsecscale1000ip4-ip4base-interfaces-aes-gcm-ndrdisc
    {NOT PLOTTED} 40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-cbc-sha1-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecscale1ip4-ip4base-interfaces-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-cbc-sha1-ndrpdrdisc.robot:| tc03-64B-1t1c-ethip4ipsecscale1000ip4-ip4base-interfaces-cbc-sha1-ndrdisc
    {NOT PLOTTED} 40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-aes-gcm-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecscale1ip4-ip4base-tunnels-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-aes-gcm-ndrpdrdisc.robot:| tc03-64B-1t1c-ethip4ipsecscale1000ip4-ip4base-tunnels-aes-gcm-ndrdisc
    {NOT PLOTTED} 40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-cbc-sha1-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecscale1ip4-ip4base-tunnels-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-cbc-sha1-ndrpdrdisc.robot:| tc03-64B-1t1c-ethip4ipsecscale1000ip4-ip4base-tunnels-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrdisc


VPP NDR 64B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-ipsechw-ndrdisc.html"></iframe>

*Figure 2. VPP 2threads 2cores - NDR Throughput for Phy-to-Phy IPSEC HW.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/crypto
    $ grep -E "64B-2t2c-.*ipsec.*-ndrdisc" *

    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-aes-gcm-ndrpdrdisc.robot:| tc13-64B-2t2c-ethip4ipsecscale1ip4-ip4base-interfaces-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-aes-gcm-ndrpdrdisc.robot:| tc15-64B-2t2c-ethip4ipsecscale1000ip4-ip4base-interfaces-aes-gcm-ndrdisc
    {NOT PLOTTED} 40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-cbc-sha1-ndrpdrdisc.robot:| tc13-64B-2t2c-ethip4ipsecscale1ip4-ip4base-interfaces-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-cbc-sha1-ndrpdrdisc.robot:| tc15-64B-2t2c-ethip4ipsecscale1000ip4-ip4base-interfaces-cbc-sha1-ndrdisc
    {NOT PLOTTED} 40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-aes-gcm-ndrpdrdisc.robot:| tc13-64B-2t2c-ethip4ipsecscale1ip4-ip4base-tunnels-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-aes-gcm-ndrpdrdisc.robot:| tc15-64B-2t2c-ethip4ipsecscale1000ip4-ip4base-tunnels-aes-gcm-ndrdisc
    {NOT PLOTTED} 40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-cbc-sha1-ndrpdrdisc.robot:| tc13-64B-2t2c-ethip4ipsecscale1ip4-ip4base-tunnels-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-cbc-sha1-ndrpdrdisc.robot:| tc15-64B-2t2c-ethip4ipsecscale1000ip4-ip4base-tunnels-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrdisc

PDR Throughput
~~~~~~~~~~~~~~

VPP PDR 64B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-ipsechw-pdrdisc.html"></iframe>

*Figure 3. VPP 1thread 1core - PDR Throughput for Phy-to-Phy IPSEC HW.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/crypto
    $ grep -E "64B-1t1c-.*ipsec.*-pdrdisc" *

    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-aes-gcm-ndrpdrdisc.robot:| tc02-64B-1t1c-ethip4ipsecscale1ip4-ip4base-interfaces-aes-gcm-pdrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-aes-gcm-ndrpdrdisc.robot:| tc04-64B-1t1c-ethip4ipsecscale1000ip4-ip4base-interfaces-aes-gcm-pdrdisc
    {NOT PLOTTED} 40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-cbc-sha1-ndrpdrdisc.robot:| tc02-64B-1t1c-ethip4ipsecscale1ip4-ip4base-interfaces-cbc-sha1-pdrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-cbc-sha1-ndrpdrdisc.robot:| tc04-64B-1t1c-ethip4ipsecscale1000ip4-ip4base-interfaces-cbc-sha1-pdrdisc
    {NOT PLOTTED} 40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-aes-gcm-ndrpdrdisc.robot:| tc02-64B-1t1c-ethip4ipsecscale1ip4-ip4base-tunnels-aes-gcm-pdrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-aes-gcm-ndrpdrdisc.robot:| tc04-64B-1t1c-ethip4ipsecscale1000ip4-ip4base-tunnels-aes-gcm-pdrdisc
    {NOT PLOTTED} 40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-cbc-sha1-ndrpdrdisc.robot:| tc02-64B-1t1c-ethip4ipsecscale1ip4-ip4base-tunnels-cbc-sha1-pdrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-cbc-sha1-ndrpdrdisc.robot:| tc04-64B-1t1c-ethip4ipsecscale1000ip4-ip4base-tunnels-cbc-sha1-pdrdisc
    40ge2p1xl710-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrpdrdisc.robot:| tc02-64B-1t1c-ethip4ipsectptlispgpe-ip4base-cbc-sha1-pdrdisc


VPP PDR 64B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-ipsechw-pdrdisc.html"></iframe>

*Figure 4. VPP 2thread 2core - PDR Throughput for Phy-to-Phy IPSEC HW.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/crypto
    $ grep -E "64B-2t2c-.*ipsec.*-pdrdisc" *

    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-aes-gcm-ndrpdrdisc.robot:| tc14-64B-2t2c-ethip4ipsecscale1ip4-ip4base-interfaces-aes-gcm-pdrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-aes-gcm-ndrpdrdisc.robot:| tc16-64B-2t2c-ethip4ipsecscale1000ip4-ip4base-interfaces-aes-gcm-pdrdisc
    {NOT PLOTTED} 40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-cbc-sha1-ndrpdrdisc.robot:| tc14-64B-2t2c-ethip4ipsecscale1ip4-ip4base-interfaces-cbc-sha1-pdrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-cbc-sha1-ndrpdrdisc.robot:| tc16-64B-2t2c-ethip4ipsecscale1000ip4-ip4base-interfaces-cbc-sha1-pdrdisc
    {NOT PLOTTED} 40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-aes-gcm-ndrpdrdisc.robot:| tc14-64B-2t2c-ethip4ipsecscale1ip4-ip4base-tunnels-aes-gcm-pdrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-aes-gcm-ndrpdrdisc.robot:| tc16-64B-2t2c-ethip4ipsecscale1000ip4-ip4base-tunnels-aes-gcm-pdrdisc
    {NOT PLOTTED} 40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-cbc-sha1-ndrpdrdisc.robot:| tc14-64B-2t2c-ethip4ipsecscale1ip4-ip4base-tunnels-cbc-sha1-pdrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-cbc-sha1-ndrpdrdisc.robot:| tc16-64B-2t2c-ethip4ipsecscale1000ip4-ip4base-tunnels-cbc-sha1-pdrdisc
    40ge2p1xl710-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrpdrdisc.robot:| tc08-64B-2t2c-ethip4ipsectptlispgpe-ip4base-cbc-sha1-pdrdisc

