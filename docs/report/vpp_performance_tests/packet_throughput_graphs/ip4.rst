IPv4 Routed-Forwarding
======================

Following sections include summary graphs of VPP Phy-to-Phy performance
with IPv4 Routed-Forwarding, including NDR throughput (zero packet loss)
and PDR throughput (<0.5% packet loss). Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

NDR Throughput
~~~~~~~~~~~~~~

VPP NDR 64B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-ethip4-ip4-ndrdisc.html"></iframe>

*Figure 1. VPP 1thread 1core - NDR Throughput for Phy-to-Phy IPv4 Routed-Forwarding.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/ip4
    $ grep -P '64B-1t1c-ethip4-ip4(base|scale)[a-z0-9]*(?!-eth-[0-9]vhost).*-ndrdisc' *

    10ge2p1x520-ethip4-ip4base-copwhtlistbase-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-copwhtlistbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-iacldstbase-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-iacldstbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-ipolicemarkbase-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-ipolicemarkbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-ndrdisc
    10ge2p1x520-ethip4-ip4base-snat-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-snat-1u-1p-ndrdisc
    10ge2p1x520-ethip4-ip4scale200k-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4scale200k-ndrdisc
    10ge2p1x520-ethip4-ip4scale20k-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4scale20k-ndrdisc
    10ge2p1x520-ethip4-ip4scale2m-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4scale2m-ndrdisc
    40ge2p1xl710-ethip4-ip4base-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-ndrdisc

VPP NDR 64B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-ethip4-ip4-ndrdisc.html"></iframe>

*Figure 2. VPP 2threads 2cores - NDR Throughput for Phy-to-Phy IPv4
Routed-Forwarding.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/ip4
    $ grep -P '64B-2t2c-ethip4-ip4(base|scale)[a-z0-9]*(?!-eth-[0-9]vhost).*-ndrdisc' *

    10ge2p1x520-ethip4-ip4base-copwhtlistbase-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-copwhtlistbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-iacldstbase-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-iacldstbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-ipolicemarkbase-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-ipolicemarkbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-ndrdisc
    10ge2p1x520-ethip4-ip4scale200k-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4scale200k-ndrdisc
    10ge2p1x520-ethip4-ip4scale20k-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4scale20k-ndrdisc
    10ge2p1x520-ethip4-ip4scale2m-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4scale2m-ndrdisc
    40ge2p1xl710-ethip4-ip4base-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-ndrdisc

PDR Throughput
~~~~~~~~~~~~~~

VPP PDR 64B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-ethip4-ip4-pdrdisc.html"></iframe>

*Figure 3. VPP 1thread 1core - PDR Throughput for Phy-to-Phy IPv4
Routed-Forwarding.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/ip4
    $ grep -P '64B-1t1c-ethip4-ip4(base|scale)[a-z0-9]*(?!-eth-[0-9]vhost).*-pdrdisc' *

    10ge2p1x520-ethip4-ip4base-copwhtlistbase-ndrpdrdisc.robot:| tc02-64B-1t1c-ethip4-ip4base-copwhtlistbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-iacldstbase-ndrpdrdisc.robot:| tc02-64B-1t1c-ethip4-ip4base-iacldstbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-ipolicemarkbase-ndrpdrdisc.robot:| tc02-64B-1t1c-ethip4-ip4base-ipolicemarkbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-ndrpdrdisc.robot:| tc02-64B-1t1c-ethip4-ip4base-pdrdisc
    10ge2p1x520-ethip4-ip4base-snat-ndrpdrdisc.robot:| tc02-64B-1t1c-ethip4-ip4base-snat-1u-1p-pdrdisc
    10ge2p1x520-ethip4-ip4scale200k-ndrpdrdisc.robot:| tc02-64B-1t1c-ethip4-ip4scale200k-pdrdisc
    10ge2p1x520-ethip4-ip4scale20k-ndrpdrdisc.robot:| tc02-64B-1t1c-ethip4-ip4scale20k-pdrdisc
    10ge2p1x520-ethip4-ip4scale2m-ndrpdrdisc.robot:| tc02-64B-1t1c-ethip4-ip4scale2m-pdrdisc

VPP PDR 64B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-ethip4-ip4-pdrdisc.html"></iframe>

*Figure 4. VPP 2thread 2core - PDR Throughput for Phy-to-Phy IPv4
Routed-Forwarding.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/ipv4
    $ grep -P '64B-2t2c-ethip4-ip4(base|scale)[a-z0-9]*(?!-eth-[0-9]vhost).*-pdrdisc' *

    10ge2p1x520-ethip4-ip4base-copwhtlistbase-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-copwhtlistbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-iacldstbase-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-iacldstbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-ipolicemarkbase-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-ipolicemarkbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-pdrdisc
    10ge2p1x520-ethip4-ip4scale200k-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4scale200k-pdrdisc
    10ge2p1x520-ethip4-ip4scale20k-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4scale20k-pdrdisc
    10ge2p1x520-ethip4-ip4scale2m-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4scale2m-pdrdisc
    40ge2p1xl710-ethip4-ip4base-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-pdrdisc

