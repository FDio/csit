VM vhost Connections
====================

This section includes summary graphs of VPP Phy-to-VM(s)-to-Phy packet
latency with with VM virtio and VPP vhost-user virtual interfaces
measured at 50% of discovered NDR throughput rate. Latency is reported
for VPP running in multiple configurations of VPP worker thread(s),
a.k.a. VPP data plane thread(s), and their physical CPU core(s)
placement.

VPP packet latency in 1t1c setup (1thread, 1core) is presented in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-vhost-ndrdisc-lat50.html"></iframe>

*Figure 1. VPP 1thread 1core - packet latency for Phy-to-VM-to-Phy VM vhost-user.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/vm_vhost
    $ grep -E "64B-1t1c-.*vhost.*-ndrdisc" *

    10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrpdrdisc.robot:| tc01-64B-1t1c-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-dot1q-l2xcbase-eth-2vhost-1vm-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2xcbase-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-ethip4-ip4base-eth-2vhostvr1024-1vm-cfsrr1-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-eth-2vhostvr1024-1vm-cfsrr1-ndrdisc
    10ge2p1x520-ethip4-ip4base-eth-2vhostvr1024-1vm-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-eth-2vhostvr1024-1vm-ndrdisc
    10ge2p1x520-ethip4-ip4base-eth-2vhostvr256-1vm-cfsrr1-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-eth-2vhostvr256-1vm-cfsrr1-ndrdisc
    10ge2p1x520-ethip4-ip4base-eth-2vhostvr256-1vm-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-eth-2vhostvr256-1vm-ndrdisc
    10ge2p1x520-ethip4-ip4base-eth-4vhost-2vm-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-eth-4vhost-2vm-ndrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-cfsrr1-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-cfsrr1-ndrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-ndrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhostvr256-1vm-cfsrr1-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2bdbasemaclrn-eth-2vhostvr256-1vm-cfsrr1-ndrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhostvr256-1vm-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2bdbasemaclrn-eth-2vhostvr256-1vm-ndrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-4vhost-2vm-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2bdbasemaclrn-eth-4vhost-2vm-ndrdisc
    10ge2p1x520-eth-l2xcbase-eth-2vhostvr1024-1vm-cfsrr1-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2xcbase-eth-2vhostvr1024-1vm-cfsrr1-ndrdisc
    10ge2p1x520-eth-l2xcbase-eth-2vhostvr1024-1vm-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2xcbase-eth-2vhostvr1024-1vm-ndrdisc
    10ge2p1x520-eth-l2xcbase-eth-2vhostvr256-1vm-cfsrr1-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2xcbase-eth-2vhostvr256-1vm-cfsrr1-ndrdisc
    10ge2p1x520-eth-l2xcbase-eth-2vhostvr256-1vm-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2xcbase-eth-2vhostvr256-1vm-ndrdisc
    10ge2p1x520-eth-l2xcbase-eth-4vhost-2vm-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2xcbase-eth-4vhost-2vm-ndrdisc
    10ge2p1x710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    40ge2p1xl710-ethip4-ip4base-eth-4vhost-2vm-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-ip4base-eth-4vhost-2vm-ndrdisc
    40ge2p1xl710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    40ge2p1xl710-eth-l2bdbasemaclrn-eth-4vhost-2vm-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2bdbasemaclrn-eth-4vhost-2vm-ndrdisc
    40ge2p1xl710-eth-l2xcbase-eth-4vhost-2vm-ndrpdrdisc.robot:| tc01-64B-1t1c-eth-l2xcbase-eth-4vhost-2vm-ndrdisc

VPP packet latency in 2t2c setup (2thread, 2core) is presented in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-vhost-ndrdisc-lat50.html"></iframe>

*Figure 2. VPP 2threads 2cores - packet latency for Phy-to-VM-to-Phy VM vhost-user.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/vm_vhost
    $ grep -E "64B-2t2c-.*vhost.*-ndrdisc" *

    10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrpdrdisc.robot:| tc07-64B-2t2c-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-dot1q-l2xcbase-eth-2vhost-1vm-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2xcbase-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-ethip4-ip4base-eth-2vhostvr1024-1vm-cfsrr1-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-eth-2vhostvr1024-1vm-cfsrr1-ndrdisc
    10ge2p1x520-ethip4-ip4base-eth-2vhostvr1024-1vm-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-eth-2vhostvr1024-1vm-ndrdisc
    10ge2p1x520-ethip4-ip4base-eth-2vhostvr256-1vm-cfsrr1-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-eth-2vhostvr256-1vm-cfsrr1-ndrdisc
    10ge2p1x520-ethip4-ip4base-eth-2vhostvr256-1vm-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-eth-2vhostvr256-1vm-ndrdisc
    10ge2p1x520-ethip4-ip4base-eth-4vhost-2vm-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-eth-4vhost-2vm-ndrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-cfsrr1-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-cfsrr1-ndrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-ndrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhostvr256-1vm-cfsrr1-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2bdbasemaclrn-eth-2vhostvr256-1vm-cfsrr1-ndrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhostvr256-1vm-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2bdbasemaclrn-eth-2vhostvr256-1vm-ndrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-4vhost-2vm-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2bdbasemaclrn-eth-4vhost-2vm-ndrdisc
    10ge2p1x520-eth-l2xcbase-eth-2vhostvr1024-1vm-cfsrr1-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2xcbase-eth-2vhostvr1024-1vm-cfsrr1-ndrdisc
    10ge2p1x520-eth-l2xcbase-eth-2vhostvr1024-1vm-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2xcbase-eth-2vhostvr1024-1vm-ndrdisc
    10ge2p1x520-eth-l2xcbase-eth-2vhostvr256-1vm-cfsrr1-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2xcbase-eth-2vhostvr256-1vm-cfsrr1-ndrdisc
    10ge2p1x520-eth-l2xcbase-eth-2vhostvr256-1vm-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2xcbase-eth-2vhostvr256-1vm-ndrdisc
    10ge2p1x520-eth-l2xcbase-eth-4vhost-2vm-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2xcbase-eth-4vhost-2vm-ndrdisc
    10ge2p1x710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    40ge2p1xl710-ethip4-ip4base-eth-4vhost-2vm-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-ip4base-eth-4vhost-2vm-ndrdisc
    40ge2p1xl710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    40ge2p1xl710-eth-l2bdbasemaclrn-eth-4vhost-2vm-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2bdbasemaclrn-eth-4vhost-2vm-ndrdisc
    40ge2p1xl710-eth-l2xcbase-eth-4vhost-2vm-ndrpdrdisc.robot:| tc07-64B-2t2c-eth-l2xcbase-eth-4vhost-2vm-ndrdisc

