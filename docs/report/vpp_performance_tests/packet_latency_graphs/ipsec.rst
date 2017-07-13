IPSec Crypto HW: IP4 Routed-Forwarding
======================================

This section includes summary graphs of VPP Phy-to-Phy packet latency
with IPSec encryption used in combination with IPv4 routed-forwarding,
with latency measured at 50% of discovered NDR throughput rate. VPP
IPSec encryption is accelerated using DPDK cryptodev library driving
Intel Quick Assist (QAT) crypto PCIe hardware cards. Latency is reported
for VPP running in multiple configurations of VPP worker thread(s),
a.k.a. VPP data plane thread(s), and their physical CPU core(s)
placement.

VPP packet latency in 1t1c setup (1thread, 1core) is presented in the graph
below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-ipsechw-ndrdisc-lat50.html"></iframe>

*Figure 1. VPP 1thread 1core - packet latency for Phy-to-Phy IPSec HW with IPv4 Routed-Forwarding.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/crypto
    $ grep -E "64B-1t1c-.*ipsec.*-ndrdisc" *

    40ge2p1xl710-ethip4ipsecbasetnl-ip4base-int-aes-gcm-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecbasetnl-ip4base-int-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecbasetnl-ip4base-int-cbc-sha1-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecbasetnl-ip4base-int-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecbasetnl-ip4base-tnl-aes-gcm-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecbasetnl-ip4base-tnl-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecscale1000tnl-ip4base-int-aes-gcm-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecscale1000tnl-ip4base-int-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscale1000tnl-ip4base-int-cbc-sha1-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecscale1000tnl-ip4base-int-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecscale1000tnl-ip4base-tnl-aes-gcm-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecscale1000tnl-ip4base-tnl-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscale1000tnl-ip4base-tnl-cbc-sha1-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecscale1000tnl-ip4base-tnl-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrdisc


VPP packet latency in 2t2c setup (2thread, 2core) is presented in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-ipsechw-ndrdisc-lat50.html"></iframe>

*Figure 2. VPP 2threads 2cores - packet latency for Phy-to-Phy IPSec HW with IPv4 Routed-Forwarding.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. code-block:: bash

    $ cd $CSIT/tests/vpp/perf/crypto
    $ grep -E "64B-2t2c-.*ipsec.*-ndrdisc" *

    40ge2p1xl710-ethip4ipsecbasetnl-ip4base-int-aes-gcm-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4ipsecbasetnl-ip4base-int-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecbasetnl-ip4base-int-cbc-sha1-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4ipsecbasetnl-ip4base-int-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecbasetnl-ip4base-tnl-aes-gcm-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4ipsecbasetnl-ip4base-tnl-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecscale1000tnl-ip4base-int-aes-gcm-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4ipsecscale1000tnl-ip4base-int-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscale1000tnl-ip4base-int-cbc-sha1-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4ipsecscale1000tnl-ip4base-int-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecscale1000tnl-ip4base-tnl-aes-gcm-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4ipsecscale1000tnl-ip4base-tnl-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscale1000tnl-ip4base-tnl-cbc-sha1-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4ipsecscale1000tnl-ip4base-tnl-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrdisc

