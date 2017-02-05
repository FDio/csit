IPv4 Overlay Tunnels
====================

This section provides a summary of VPP Phy-to-Phy IPv4 Overlay Tunnels
performance illustrating packet latency measured at 50% of discovered NDR
throughput rate. Latency is reported for VPP running in multiple
configurations of VPP worker thread(s), a.k.a. VPP data plane thread (s), and
their physical CPU core(s) placement.

Title of each graph is a regex (regular expression) matching all plotted
test case throughput measurements.

.. note::

    Data sources for reported test results: i) FD.io test executor jobs
    `csit-vpp-perf-1701-all
    <https://jenkins.fd.io/view/csit/job/csit-vpp-perf-1701-all/>`_ and
    `csit-vpp-perf-1701-long
    <https://jenkins.fd.io/view/csit/job/csit-vpp-perf-1701-long/>`_
    , ii) archived FD.io jobs test result `output files
    <../../_static/archive/>`_.

VPP packet latency - running in configuration of **one worker thread (1t) on one
physical core (1c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-ethip4-ndrdisc-lat50.html"></iframe>

*Figure 1. VPP 1thread 1core - packet latency for Phy-to-Phy IPv4 Overlay Tunnels.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" *

    10ge2p1x520-ethip4lispip4-ip4base-ndrdisc.robot:| tc01-64B-1t1c-ethip4lispip4-ip4base-ndrdisc
    10ge2p1x520-ethip4lispip6-ip4base-ndrdisc.robot:| tc01-64B-1t1c-ethip4lispip6-ip4base-ndrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-ndrdisc.robot:| tc01-64B-1t1c-ethip4vxlan-l2bdbasemaclrn-ndrdisc
    10ge2p1x520-ethip4vxlan-l2xcbase-ndrdisc.robot:| tc01-64B-1t1c-ethip4vxlan-l2xcbase-ndrdisc

VPP packet latency - running in configuration of **two worker threads (2t) on two
physical cores (2c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-ethip4-ndrdisc-lat50.html"></iframe>

*Figure 2. VPP 2threads 2cores - packet latency for Phy-to-Phy IPv4 Overlay Tunnels.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" *

    10ge2p1x520-ethip4lispip4-ip4base-ndrdisc.robot:| tc07-64B-2t2c-ethip4lispip4-ip4base-ndrdisc
    10ge2p1x520-ethip4lispip6-ip4base-ndrdisc.robot:| tc07-64B-2t2c-ethip4lispip6-ip4base-ndrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-ndrdisc.robot:| tc07-64B-2t2c-ethip4vxlan-l2bdbasemaclrn-ndrdisc
    10ge2p1x520-ethip4vxlan-l2xcbase-ndrdisc.robot:| tc07-64B-2t2c-ethip4vxlan-l2xcbase-ndrdisc

VPP packet latency - running in configuration of **four worker threads (4t) on four
physical cores (4c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-4t4c-ethip4-ndrdisc-lat50.html"></iframe>

*Figure 3. VPP 4threads 4cores - packet latency for Phy-to-Phy IPv4 Overlay Tunnels.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-4t4c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" *

    10ge2p1x520-ethip4lispip4-ip4base-ndrdisc.robot:| tc13-64B-4t4c-ethip4lispip4-ip4base-ndrdisc
    10ge2p1x520-ethip4lispip6-ip4base-ndrdisc.robot:| tc13-64B-4t4c-ethip4lispip6-ip4base-ndrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-ndrdisc.robot:| tc13-64B-4t4c-ethip4vxlan-l2bdbasemaclrn-ndrdisc
    10ge2p1x520-ethip4vxlan-l2xcbase-ndrdisc.robot:| tc13-64B-4t4c-ethip4vxlan-l2xcbase-ndrdisc

