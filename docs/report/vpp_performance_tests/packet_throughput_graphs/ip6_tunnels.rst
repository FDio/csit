IPv6 Overlay Tunnels
====================

Following sections include summary graphs of VPP Phy-to-Phy performance
with IPv6 Overlay Tunnels, including NDR throughput (zero packet loss)
and PDR throughput (<0.5% packet loss). Performance is reported for VPP
running in multiple configurations of VPP worker thread(s), a.k.a. VPP
data plane thread(s), and their physical CPU core(s) placement.

NDR Throughput
~~~~~~~~~~~~~~

VPP NDR 78B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/78B-1t1c-ethip6-ndrdisc.html"></iframe>

*Figure 1. VPP 1thread 1core - NDR Throughput for Phy-to-Phy IPv6 Overlay
Tunnels.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/ip6_tunnels
    $ grep -E "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" *

    10ge2p1x520-ethip6lispip4-ip6base-ndrdisc.robot:| tc01-78B-1t1c-ethip6lispip4-ip6base-ndrdisc
    10ge2p1x520-ethip6lispip6-ip6base-ndrdisc.robot:| tc01-78B-1t1c-ethip6lispip6-ip6base-ndrdisc

VPP NDR 78B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/78B-2t2c-ethip6-ndrdisc.html"></iframe>

*Figure 2. VPP 2threads 2cores - NDR Throughput for Phy-to-Phy IPv6 Overlay
Tunnels.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/ip6_tunnels
    $ grep -E "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" *

    10ge2p1x520-ethip6lispip4-ip6base-ndrdisc.robot:| tc07-78B-2t2c-ethip6lispip4-ip6base-ndrdisc
    10ge2p1x520-ethip6lispip6-ip6base-ndrdisc.robot:| tc07-78B-2t2c-ethip6lispip6-ip6base-ndrdisc

PDR Throughput
~~~~~~~~~~~~~~

VPP PDR 78B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/78B-1t1c-ethip6-pdrdisc.html"></iframe>

*Figure 3. VPP 1thread 1core - PDR Throughput for Phy-to-Phy IPv6 Overlay
Tunnels.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/ip6_tunnels
    $ grep -E "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-pdrdisc" *

    10ge2p1x520-ethip6lispip4-ip6base-ndrdisc.robot:| tc02-78B-1t1c-ethip6lispip4-ip6base-pdrdisc
    10ge2p1x520-ethip6lispip6-ip6base-ndrdisc.robot:| tc02-78B-1t1c-ethip6lispip6-ip6base-pdrdisc

VPP PDR 78B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/78B-2t2c-ethip6-pdrdisc.html"></iframe>

*Figure 4. VPP 2thread 2core - PDR Throughput for Phy-to-Phy IPv6 Overlay
Tunnels.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/ip6_tunnels
    $ grep -E "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-pdrdisc" *

    10ge2p1x520-ethip6lispip4-ip6base-ndrdisc.robot:| tc08-78B-2t2c-ethip6lispip4-ip6base-pdrdisc
    10ge2p1x520-ethip6lispip6-ip6base-ndrdisc.robot:| tc08-78B-2t2c-ethip6lispip6-ip6base-pdrdisc
