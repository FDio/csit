IPv4 Routed-Forwarding
======================

This section includes summary graphs of VPP Phy-to-Phy packet latency
with IPv4 Routed-Forwarding measured at 50% of discovered NDR throughput
rate. Latency is reported for VPP running in multiple configurations of
VPP worker thread(s), a.k.a. VPP data plane thread(s), and their
physical CPU core(s) placement.

VPP packet latency in 1t1c setup (1thread, 1core) is presented in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-ethip4-ip4-ndrdisc-lat50.html"></iframe>

*Figure 1. VPP 1thread 1core - packet latency for Phy-to-Phy IPv4 Routed-Forwarding.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/ipv4
    $ grep -P '64B-1t1c-ethip4-ip4(base|scale)[a-z0-9]*(?!-eth-[0-9]vhost).*-ndrdisc' *

    10ge2p1x520-ethip4-ip4base-copwhtlistbase-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-copwhtlistbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-iacldstbase-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-iacldstbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-ipolicemarkbase-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-ipolicemarkbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-ndrdisc
    10ge2p1x520-ethip4-ip4base-snat-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-snat-1u-1p-ndrdisc
    10ge2p1x520-ethip4-ip4scale200k-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4scale200k-ndrdisc
    10ge2p1x520-ethip4-ip4scale20k-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4scale20k-ndrdisc
    10ge2p1x520-ethip4-ip4scale2m-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4scale2m-ndrdisc
    10ge2p1x520-ethip4-ip4scale-snat-ndrpdrdisc.robot:| tc11-64B-1t1c-ethip4-ip4base-snat-4000u-15p-ndrdisc
    40ge2p1xl710-ethip4-ip4base-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-ndrdisc

VPP packet latency in 2t2c setup (2thread, 2core) is presented in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-ethip4-ip4-ndrdisc-lat50.html"></iframe>

*Figure 2. VPP 2threads 2cores - packet latency for Phy-to-Phy IPv4 Routed-Forwarding.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/ipv4
    $ grep -P '64B-2t2c-ethip4-ip4(base|scale)[a-z0-9]*(?!-eth-[0-9]vhost).*-ndrdisc' *

    10ge2p1x520-ethip4-ip4base-copwhtlistbase-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-copwhtlistbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-iacldstbase-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-iacldstbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-ipolicemarkbase-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-ipolicemarkbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-ndrdisc
    10ge2p1x520-ethip4-ip4scale200k-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4scale200k-ndrdisc
    10ge2p1x520-ethip4-ip4scale20k-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4scale20k-ndrdisc
    10ge2p1x520-ethip4-ip4scale2m-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4scale2m-ndrdisc
    40ge2p1xl710-ethip4-ip4base-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-ndrdisc
