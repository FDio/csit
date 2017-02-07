IPv6 Overlay Tunnels
====================

This section provides a summary of VPP Phy-to-Phy IPv6 Overlay Tunnels
performance illustrating packet latency measured at 50% of discovered NDR
throughput rate. Latency is reported for VPP running in multiple
configurations of VPP worker thread(s), a.k.a. VPP data plane thread (s), and
their physical CPU core(s) placement.

*Title of each graph* is a regex (regular expression) matching all plotted
latency test cases, *X-axis labels* are indeces of csit-vpp-perf-1701 jobs
that created result output files used as data sources for the graph,
*Y-axis labels* are measured packet Latency [uSec] values, and the *graph
legend* identifes the plotted test suites.

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

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/78B-1t1c-ethip6-ndrdisc-lat50.html"></iframe>

*Figure 1. VPP 1thread 1core - packet latency for Phy-to-Phy IPv6 Overlay Tunnels.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" *

    10ge2p1x520-ethip6lispip4-ip6base-ndrdisc.robot:| tc01-78B-1t1c-ethip6lispip4-ip6base-ndrdisc
    10ge2p1x520-ethip6lispip6-ip6base-ndrdisc.robot:| tc01-78B-1t1c-ethip6lispip6-ip6base-ndrdisc

VPP packet latency - running in configuration of **two worker threads (2t) on two
physical cores (2c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/78B-2t2c-ethip6-ndrdisc-lat50.html"></iframe>

*Figure 2. VPP 2threads 2cores - packet latency for Phy-to-Phy IPv6 Overlay Tunnels.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" *

    10ge2p1x520-ethip6lispip4-ip6base-ndrdisc.robot:| tc07-78B-2t2c-ethip6lispip4-ip6base-ndrdisc
    10ge2p1x520-ethip6lispip6-ip6base-ndrdisc.robot:| tc07-78B-2t2c-ethip6lispip6-ip6base-ndrdisc

VPP packet latency - running in configuration of **four worker threads (4t) on four
physical cores (4c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/78B-4t4c-ethip6-ndrdisc-lat50.html"></iframe>

*Figure 3. VPP 4threads 4cores - packet latency for Phy-to-Phy IPv6 Overlay Tunnels.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-4t4c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" *

    10ge2p1x520-ethip6lispip4-ip6base-ndrdisc.robot:| tc13-78B-4t4c-ethip6lispip4-ip6base-ndrdisc
    10ge2p1x520-ethip6lispip6-ip6base-ndrdisc.robot:| tc13-78B-4t4c-ethip6lispip6-ip6base-ndrdisc


