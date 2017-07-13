IPv6 Routed-Forwarding
======================

This section includes summary graphs of VPP Phy-to-Phy packet latency
with IPv6 Routed-Forwarding measured at 50% of discovered NDR throughput
rate. Latency is reported for VPP running in multiple configurations of
VPP worker thread(s), a.k.a. VPP data plane thread(s), and their
physical CPU core(s) placement.

VPP packet latency in 1t1c setup (1thread, 1core) is presented in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/78B-1t1c-ethip6-ip6-ndrdisc-lat50.html"></iframe>

*Figure 1. VPP 1thread 1core - packet latency for Phy-to-Phy IPv6 Routed-Forwarding.*

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

VPP packet latency in 2t2c setup (2thread, 2core) is presented in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/78B-2t2c-ethip6-ip6-ndrdisc-lat50.html"></iframe>

*Figure 2. VPP 2threads 2cores - packet latency for Phy-to-Phy IPv6 Routed-Forwarding.*

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

