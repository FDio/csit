Crypto in hardware: IP4FWD, IP6FWD
==================================

This section provides a summary of VPP Phy-to-Phy IPSEC HW
performance illustrating packet latency measured at 50% of discovered NDR
throughput rate. Latency is reported for VPP running in multiple
configurations of VPP worker thread(s), a.k.a. VPP data plane thread (s), and
their physical CPU core(s) placement.

*Title of each graph* is a regex (regular expression) matching all plotted
latency test cases, *X-axis labels* are indeces of csit-vpp-perf-1704 jobs
that created result output files used as data sources for the graph,
*Y-axis labels* are measured packet Latency [uSec] values, and the *graph
legend* identifes the plotted test suites.

.. note::

    Data sources for reported test results: i) FD.io test executor jobs
    `csit-vpp-perf-1704-all
    <https://jenkins.fd.io/view/csit/job/csit-vpp-perf-1704-all/>`_ ,
    ii) archived FD.io jobs test result `output files
    <../../_static/archive/>`_.

VPP packet latency - running in configuration of **one worker thread (1t) on one
physical core (1c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-ipsechw-ndrdisc-lat50.html"></iframe>

*Figure 1. VPP 1thread 1core - packet latency for Phy-to-Phy IPSEC HW.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-1t1c-.*ipsec*" *

    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-aes-gcm-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecscale1ip4-ip4base-interfaces-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-aes-gcm-ndrpdrdisc.robot:| tc03-64B-1t1c-ethip4ipsecscale1000ip4-ip4base-interfaces-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-cbc-sha1-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecscale1ip4-ip4base-interfaces-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-cbc-sha1-ndrpdrdisc.robot:| tc03-64B-1t1c-ethip4ipsecscale1000ip4-ip4base-interfaces-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-aes-gcm-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecscale1ip4-ip4base-tunnels-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-aes-gcm-ndrpdrdisc.robot:| tc03-64B-1t1c-ethip4ipsecscale1000ip4-ip4base-tunnels-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-cbc-sha1-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsecscale1ip4-ip4base-tunnels-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-cbc-sha1-ndrpdrdisc.robot:| tc03-64B-1t1c-ethip4ipsecscale1000ip4-ip4base-tunnels-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrpdrdisc.robot:| tc01-64B-1t1c-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrdisc

VPP packet latency - running in configuration of **two worker threads (2t) on two
physical cores (2c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-ipsechw-ndrdisc-lat50.html"></iframe>

*Figure 2. VPP 2threads 2cores - packet latency for Phy-to-Phy IPSEC HW.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-2t2c-.*ipsec*" *

    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-aes-gcm-ndrpdrdisc.robot:| tc13-64B-2t2c-ethip4ipsecscale1ip4-ip4base-interfaces-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-aes-gcm-ndrpdrdisc.robot:| tc15-64B-2t2c-ethip4ipsecscale1000ip4-ip4base-interfaces-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-cbc-sha1-ndrpdrdisc.robot:| tc13-64B-2t2c-ethip4ipsecscale1ip4-ip4base-interfaces-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-interfaces-cbc-sha1-ndrpdrdisc.robot:| tc15-64B-2t2c-ethip4ipsecscale1000ip4-ip4base-interfaces-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-aes-gcm-ndrpdrdisc.robot:| tc13-64B-2t2c-ethip4ipsecscale1ip4-ip4base-tunnels-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-aes-gcm-ndrpdrdisc.robot:| tc15-64B-2t2c-ethip4ipsecscale1000ip4-ip4base-tunnels-aes-gcm-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-cbc-sha1-ndrpdrdisc.robot:| tc13-64B-2t2c-ethip4ipsecscale1ip4-ip4base-tunnels-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsecscaleip4-ip4base-tunnels-cbc-sha1-ndrpdrdisc.robot:| tc15-64B-2t2c-ethip4ipsecscale1000ip4-ip4base-tunnels-cbc-sha1-ndrdisc
    40ge2p1xl710-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrpdrdisc.robot:| tc07-64B-2t2c-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrdisc

