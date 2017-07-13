IPv6 Routed-Forwarding
======================

Following sections include summary graphs of VPP Phy-to-Phy performance
with IPv6 Routed-Forwarding, including NDR throughput (zero packet loss)
and PDR throughput (<0.5% packet loss). Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

NDR Throughput
~~~~~~~~~~~~~~

VPP NDR 78B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/78B-1t1c-ethip6-ip6-ndrdisc.html"></iframe>

*Figure 1. VPP 1thread 1core - NDR Throughput for Phy-to-Phy IPv6
Routed-Forwarding.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/ip6
    $ grep -E "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" *

    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrpdrdisc.robot:| tc01-78B-1t1c-ethip6-ip6base-copwhtlistbase-ndrdisc
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrpdrdisc.robot:| tc01-78B-1t1c-ethip6-ip6base-iacldstbase-ndrdisc
    10ge2p1x520-ethip6-ip6base-ndrpdrdisc.robot:| tc01-78B-1t1c-ethip6-ip6base-ndrdisc
    10ge2p1x520-ethip6-ip6scale200k-ndrpdrdisc.robot:| tc01-78B-1t1c-ethip6-ip6scale200k-ndrdisc
    10ge2p1x520-ethip6-ip6scale20k-ndrpdrdisc.robot:| tc01-78B-1t1c-ethip6-ip6scale20k-ndrdisc
    10ge2p1x520-ethip6-ip6scale2m-ndrpdrdisc.robot:| tc01-78B-1t1c-ethip6-ip6scale2m-ndrdisc
    40ge2p1xl710-ethip6-ip6base-ndrpdrdisc.robot:| tc01-78B-1t1c-ethip6-ip6base-ndrdisc

VPP NDR 78B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/78B-2t2c-ethip6-ip6-ndrdisc.html"></iframe>

*Figure 2. VPP 2threads 2cores - NDR Throughput for Phy-to-Phy IPv6
Routed-Forwarding.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/ip6
    $ grep -E "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" *

    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrpdrdisc.robot:| tc07-78B-2t2c-ethip6-ip6base-copwhtlistbase-ndrdisc
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrpdrdisc.robot:| tc07-78B-2t2c-ethip6-ip6base-iacldstbase-ndrdisc
    10ge2p1x520-ethip6-ip6base-ndrpdrdisc.robot:| tc07-78B-2t2c-ethip6-ip6base-ndrdisc
    10ge2p1x520-ethip6-ip6scale200k-ndrpdrdisc.robot:| tc07-78B-2t2c-ethip6-ip6scale200k-ndrdisc
    10ge2p1x520-ethip6-ip6scale20k-ndrpdrdisc.robot:| tc07-78B-2t2c-ethip6-ip6scale20k-ndrdisc
    10ge2p1x520-ethip6-ip6scale2m-ndrpdrdisc.robot:| tc07-78B-2t2c-ethip6-ip6scale2m-ndrdisc
    40ge2p1xl710-ethip6-ip6base-ndrpdrdisc.robot:| tc07-78B-2t2c-ethip6-ip6base-ndrdisc

PDR Throughput
~~~~~~~~~~~~~~

VPP PDR 78B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/78B-1t1c-ethip6-ip6-pdrdisc.html"></iframe>

*Figure 3. VPP 1thread 1core - PDR Throughput for Phy-to-Phy IPv6
Routed-Forwarding.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/ip6
    $ grep -E "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" *

    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrpdrdisc.robot:| tc02-78B-1t1c-ethip6-ip6base-copwhtlistbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrpdrdisc.robot:| tc02-78B-1t1c-ethip6-ip6base-iacldstbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-ndrpdrdisc.robot:| tc02-78B-1t1c-ethip6-ip6base-pdrdisc
    10ge2p1x520-ethip6-ip6scale200k-ndrpdrdisc.robot:| tc02-78B-1t1c-ethip6-ip6scale200k-pdrdisc
    10ge2p1x520-ethip6-ip6scale20k-ndrpdrdisc.robot:| tc02-78B-1t1c-ethip6-ip6scale20k-pdrdisc
    10ge2p1x520-ethip6-ip6scale2m-ndrpdrdisc.robot:| tc02-78B-1t1c-ethip6-ip6scale2m-pdrdisc

VPP PDR 78B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/78B-2t2c-ethip6-ip6-pdrdisc.html"></iframe>

*Figure 4. VPP 2thread 2core - PDR Throughput for Phy-to-Phy IPv6
Routed-Forwarding.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/ip6
    $ grep -E "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" *

    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrpdrdisc.robot:| tc08-78B-2t2c-ethip6-ip6base-copwhtlistbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrpdrdisc.robot:| tc08-78B-2t2c-ethip6-ip6base-iacldstbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-ndrpdrdisc.robot:| tc08-78B-2t2c-ethip6-ip6base-pdrdisc
    10ge2p1x520-ethip6-ip6scale200k-ndrpdrdisc.robot:| tc08-78B-2t2c-ethip6-ip6scale200k-pdrdisc
    10ge2p1x520-ethip6-ip6scale20k-ndrpdrdisc.robot:| tc08-78B-2t2c-ethip6-ip6scale20k-pdrdisc
    10ge2p1x520-ethip6-ip6scale2m-ndrpdrdisc.robot:| tc08-78B-2t2c-ethip6-ip6scale2m-pdrdisc
