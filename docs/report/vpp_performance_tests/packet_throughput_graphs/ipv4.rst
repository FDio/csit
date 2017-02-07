IPv4 Routed-Forwarding
======================

Following sections provide a summary of VPP Phy-to-Phy IPv4 Routed-Forwarding
performance illustrating NDR throughput (zero packet loss) and PDR throughput
(<0.5% packet loss). Performance is reported for VPP running in multiple
configurations of VPP worker thread(s), a.k.a. VPP data plane thread (s), and
their physical CPU core(s) placement.

*Title of each graph* is a regex (regular expression) matching all plotted
throughput test cases, *X-axis labels* are indeces of csit-vpp-perf-1701 jobs
that created result output files used as data sources for the graph,
*Y-axis labels* are measured Packets Per Second [pps] values, and the *graph
legend* identifes the plotted test suites.

.. note::

    Data sources for reported test results: i) FD.io test executor jobs
    `csit-vpp-perf-1701-all
    <https://jenkins.fd.io/view/csit/job/csit-vpp-perf-1701-all/>`_ and
    `csit-vpp-perf-1701-long
    <https://jenkins.fd.io/view/csit/job/csit-vpp-perf-1701-long/>`_
    , ii) archived FD.io jobs test result `output files
    <../../_static/archive/>`_.

NDR Throughput
~~~~~~~~~~~~~~

VPP NDR Throughput - running in configuration of **one worker thread (1t) on
one physical core (1c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-ethip4-ip4-ndrdisc.html"></iframe>

*Figure 1. VPP 1thread 1core - NDR Throughput for Phy-to-Phy IPv4 Routed-Forwarding.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-1t1c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" *

    10ge2p1x520-ethip4-ip4base-copwhtlistbase-ndrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-copwhtlistbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-iacldstbase-ndrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-iacldstbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-ipolicemarkbase-ndrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-ipolicemarkbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-ndrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-ndrdisc
    10ge2p1x520-ethip4-ip4scale200k-ndrdisc.robot:| tc01-64B-1t1c-ethip4-ip4scale200k-ndrdisc
    10ge2p1x520-ethip4-ip4scale20k-ndrdisc.robot:| tc01-64B-1t1c-ethip4-ip4scale20k-ndrdisc
    10ge2p1x520-ethip4-ip4scale2m-ndrdisc.robot:| tc01-64B-1t1c-ethip4-ip4scale2m-ndrdisc
    40ge2p1xl710-ethip4-ip4base-ndrdisc.robot:| tc01-64B-1t1c-ethip4-ip4base-ndrdisc

VPP NDR Throughput - running in configuration of **two worker threads (2t) on
two physical cores (2c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-ethip4-ip4-ndrdisc.html"></iframe>

*Figure 2. VPP 2threads 2cores - NDR Throughput for Phy-to-Phy IPv4
Routed-Forwarding.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-2t2c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" *

    10ge2p1x520-ethip4-ip4base-copwhtlistbase-ndrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-copwhtlistbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-iacldstbase-ndrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-iacldstbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-ipolicemarkbase-ndrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-ipolicemarkbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-ndrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-ndrdisc
    10ge2p1x520-ethip4-ip4scale200k-ndrdisc.robot:| tc07-64B-2t2c-ethip4-ip4scale200k-ndrdisc
    10ge2p1x520-ethip4-ip4scale20k-ndrdisc.robot:| tc07-64B-2t2c-ethip4-ip4scale20k-ndrdisc
    10ge2p1x520-ethip4-ip4scale2m-ndrdisc.robot:| tc07-64B-2t2c-ethip4-ip4scale2m-ndrdisc
    40ge2p1xl710-ethip4-ip4base-ndrdisc.robot:| tc07-64B-2t2c-ethip4-ip4base-ndrdisc

VPP NDR Throughput - running in configuration of **four worker threads (4t) on
four physical cores (4c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-4t4c-ethip4-ip4-ndrdisc.html"></iframe>

*Figure 3. VPP 4threads 4cores - NDR Throughput for Phy-to-Phy IPv4
Routed-Forwarding.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-4t4c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" *

    10ge2p1x520-ethip4-ip4base-copwhtlistbase-ndrdisc.robot:| tc13-64B-4t4c-ethip4-ip4base-copwhtlistbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-iacldstbase-ndrdisc.robot:| tc13-64B-4t4c-ethip4-ip4base-iacldstbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-ipolicemarkbase-ndrdisc.robot:| tc13-64B-4t4c-ethip4-ip4base-ipolicemarkbase-ndrdisc
    10ge2p1x520-ethip4-ip4base-ndrdisc.robot:| tc13-64B-4t4c-ethip4-ip4base-ndrdisc
    10ge2p1x520-ethip4-ip4scale200k-ndrdisc.robot:| tc13-64B-4t4c-ethip4-ip4scale200k-ndrdisc
    10ge2p1x520-ethip4-ip4scale20k-ndrdisc.robot:| tc13-64B-4t4c-ethip4-ip4scale20k-ndrdisc
    10ge2p1x520-ethip4-ip4scale2m-ndrdisc.robot:| tc13-64B-4t4c-ethip4-ip4scale2m-ndrdisc
    40ge2p1xl710-ethip4-ip4base-ndrdisc.robot:| tc13-64B-4t4c-ethip4-ip4base-ndrdisc

PDR Throughput
~~~~~~~~~~~~~~

VPP PDR Throughput - running in configuration of **one worker thread (1t) on one
physical core (1c)** - is presented in the figure below. PDR at below 0.5%
packet loss ratio.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-ethip4-ip4-pdrdisc.html"></iframe>

*Figure 4. VPP 1thread 1core - PDR Throughput for Phy-to-Phy IPv4
Routed-Forwarding.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-1t1c-ethip4-ip4[a-z0-9]+-[a-z-]*pdrdisc" *

    10ge2p1x520-ethip4-ip4base-copwhtlistbase-ndrdisc.robot:| tc02-64B-1t1c-ethip4-ip4base-copwhtlistbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-iacldstbase-ndrdisc.robot:| tc02-64B-1t1c-ethip4-ip4base-iacldstbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-ipolicemarkbase-ndrdisc.robot:| tc02-64B-1t1c-ethip4-ip4base-ipolicemarkbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-ndrdisc.robot:| tc02-64B-1t1c-ethip4-ip4base-pdrdisc
    10ge2p1x520-ethip4-ip4scale200k-ndrdisc.robot:| tc02-64B-1t1c-ethip4-ip4scale200k-pdrdisc
    10ge2p1x520-ethip4-ip4scale20k-ndrdisc.robot:| tc02-64B-1t1c-ethip4-ip4scale20k-pdrdisc
    10ge2p1x520-ethip4-ip4scale2m-ndrdisc.robot:| tc02-64B-1t1c-ethip4-ip4scale2m-pdrdisc

VPP PDR Throughput - running in configuration of **two worker threads (2t) on
two physical cores (2c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-ethip4-ip4-pdrdisc.html"></iframe>

*Figure 5. VPP 2thread 2core - PDR Throughput for Phy-to-Phy IPv4
Routed-Forwarding.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-2t2c-ethip4-ip4[a-z0-9]+-[a-z-]*pdrdisc" *

    10ge2p1x520-ethip4-ip4base-copwhtlistbase-ndrdisc.robot:| tc08-64B-2t2c-ethip4-ip4base-copwhtlistbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-iacldstbase-ndrdisc.robot:| tc08-64B-2t2c-ethip4-ip4base-iacldstbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-ipolicemarkbase-ndrdisc.robot:| tc08-64B-2t2c-ethip4-ip4base-ipolicemarkbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-ndrdisc.robot:| tc08-64B-2t2c-ethip4-ip4base-pdrdisc
    10ge2p1x520-ethip4-ip4scale200k-ndrdisc.robot:| tc08-64B-2t2c-ethip4-ip4scale200k-pdrdisc
    10ge2p1x520-ethip4-ip4scale20k-ndrdisc.robot:| tc08-64B-2t2c-ethip4-ip4scale20k-pdrdisc
    10ge2p1x520-ethip4-ip4scale2m-ndrdisc.robot:| tc08-64B-2t2c-ethip4-ip4scale2m-pdrdisc

VPP PDR Throughput - running in configuration of **four worker threads (4t) on
four physical cores (4c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-4t4c-ethip4-ip4-pdrdisc.html"></iframe>

*Figure 6. VPP 4thread 4core - PDR Throughput for Phy-to-Phy IPv4
Routed-Forwarding.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-4t4c-ethip4-ip4[a-z0-9]+-[a-z-]*pdrdisc" *

    10ge2p1x520-ethip4-ip4base-copwhtlistbase-ndrdisc.robot:| tc14-64B-4t4c-ethip4-ip4base-copwhtlistbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-iacldstbase-ndrdisc.robot:| tc14-64B-4t4c-ethip4-ip4base-iacldstbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-ipolicemarkbase-ndrdisc.robot:| tc14-64B-4t4c-ethip4-ip4base-ipolicemarkbase-pdrdisc
    10ge2p1x520-ethip4-ip4base-ndrdisc.robot:| tc14-64B-4t4c-ethip4-ip4base-pdrdisc
    10ge2p1x520-ethip4-ip4scale200k-ndrdisc.robot:| tc14-64B-4t4c-ethip4-ip4scale200k-pdrdisc
    10ge2p1x520-ethip4-ip4scale20k-ndrdisc.robot:| tc14-64B-4t4c-ethip4-ip4scale20k-pdrdisc
    10ge2p1x520-ethip4-ip4scale2m-ndrdisc.robot:| tc14-64B-4t4c-ethip4-ip4scale2m-pdrdisc

