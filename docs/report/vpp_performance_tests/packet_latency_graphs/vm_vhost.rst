VM vhost Connections
====================

This section provides a summary of VPP Phy-to-VM-to-Phy VM vhost-user
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

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-vhost-ndrdisc-lat50.html"></iframe>

*Figure 1. VPP 1thread 1core - packet latency for Phy-to-VM-to-Phy VM vhost-user.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-1t1c-.*vhost.*-ndrdisc" *

    10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc01-64B-1t1c-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-dot1q-l2xcbase-eth-2vhost-1vm-ndrdisc.robot:| tc01-64B-1t1c-eth-l2xcbase-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-ethip4-ip4base-eth-2vhost-1vm-ndrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc01-64B-1t1c-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc01-64B-1t1c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-eth-l2xcbase-eth-2vhost-1vm-ndrdisc.robot:| tc01-64B-1t1c-eth-l2xcbase-eth-2vhost-1vm-ndrdisc
    10ge2p1x710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc01-64B-1t1c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    40ge2p1xl710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc01-64B-1t1c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc

VPP packet latency - running in configuration of **two worker threads (2t) on two
physical cores (2c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-vhost-ndrdisc-lat50.html"></iframe>

*Figure 2. VPP 2threads 2cores - packet latency for Phy-to-VM-to-Phy VM vhost-user.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-2t2c-.*vhost.*-ndrdisc" *

    10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc07-64B-2t2c-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-dot1q-l2xcbase-eth-2vhost-1vm-ndrdisc.robot:| tc07-64B-2t2c-eth-l2xcbase-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-ethip4-ip4base-eth-2vhost-1vm-ndrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc07-64B-2t2c-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc07-64B-2t2c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-eth-l2xcbase-eth-2vhost-1vm-ndrdisc.robot:| tc07-64B-2t2c-eth-l2xcbase-eth-2vhost-1vm-ndrdisc
    10ge2p1x710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc07-64B-2t2c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    40ge2p1xl710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc07-64B-2t2c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc

