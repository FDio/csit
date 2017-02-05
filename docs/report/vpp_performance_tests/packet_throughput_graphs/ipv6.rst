IPv6 Routed-Forwarding
======================

Following sections provide a summary of VPP Phy-to-Phy IPv6 Routed-Forwarding
performance illustrating NDR throughput (zero packet loss) and PDR throughput
(<0.5% packet loss). Performance is reported for VPP running in multiple
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

NDR Throughput
~~~~~~~~~~~~~~

VPP NDR Throughput - running in configuration of **one worker thread (1t) on
one physical core (1c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/78B-1t1c-ethip6-ip6-ndrdisc.html"></iframe>

*Figure 1. VPP 1thread 1core - NDR Throughput for Phy-to-Phy IPv6
Routed-Forwarding.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" *

    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrdisc.robot:| tc01-78B-1t1c-ethip6-ip6base-copwhtlistbase-ndrdisc
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrdisc.robot:| tc01-78B-1t1c-ethip6-ip6base-iacldstbase-ndrdisc
    10ge2p1x520-ethip6-ip6base-ndrdisc.robot:| tc01-78B-1t1c-ethip6-ip6base-ndrdisc
    10ge2p1x520-ethip6-ip6scale200k-ndrdisc.robot:| tc01-78B-1t1c-ethip6-ip6scale200k-ndrdisc
    10ge2p1x520-ethip6-ip6scale20k-ndrdisc.robot:| tc01-78B-1t1c-ethip6-ip6scale20k-ndrdisc
    10ge2p1x520-ethip6-ip6scale2m-ndrdisc.robot:| tc01-78B-1t1c-ethip6-ip6scale2m-ndrdisc
    40ge2p1xl710-ethip6-ip6base-ndrdisc.robot:| tc01-78B-1t1c-ethip6-ip6base-ndrdisc

VPP NDR Throughput - running in configuration of **two worker threads (2t) on
two physical cores (2c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/78B-2t2c-ethip6-ip6-ndrdisc.html"></iframe>

*Figure 2. VPP 2threads 2cores - NDR Throughput for Phy-to-Phy IPv6
Routed-Forwarding.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:
.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" *

    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrdisc.robot:| tc07-78B-2t2c-ethip6-ip6base-copwhtlistbase-ndrdisc
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrdisc.robot:| tc07-78B-2t2c-ethip6-ip6base-iacldstbase-ndrdisc
    10ge2p1x520-ethip6-ip6base-ipolicemarkbase-ndrdisc.robot:| tc07-78B-2t2c-ethip6-ip6base-ipolicemarkbase-ndrdisc
    10ge2p1x520-ethip6-ip6base-ndrdisc.robot:| tc07-78B-2t2c-ethip6-ip6base-ndrdisc
    10ge2p1x520-ethip6-ip6scale200k-ndrdisc.robot:| tc07-78B-2t2c-ethip6-ip6scale200k-ndrdisc
    10ge2p1x520-ethip6-ip6scale20k-ndrdisc.robot:| tc07-78B-2t2c-ethip6-ip6scale20k-ndrdisc
    10ge2p1x520-ethip6-ip6scale2m-ndrdisc.robot:| tc07-78B-2t2c-ethip6-ip6scale2m-ndrdisc
    40ge2p1xl710-ethip6-ip6base-ndrdisc.robot:| tc07-78B-2t2c-ethip6-ip6base-ndrdisc

VPP NDR Throughput - running in configuration of **four worker threads (4t) on
four physical cores (4c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/78B-4t4c-ethip6-ip6-ndrdisc.html"></iframe>

*Figure 3. VPP 4threads 4cores - NDR Throughput for Phy-to-Phy IPv6
Routed-Forwarding.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-4t4c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" *

    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrdisc.robot:| tc13-78B-4t4c-ethip6-ip6base-copwhtlistbase-ndrdisc
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrdisc.robot:| tc13-78B-4t4c-ethip6-ip6base-iacldstbase-ndrdisc
    10ge2p1x520-ethip6-ip6base-ndrdisc.robot:| tc13-78B-4t4c-ethip6-ip6base-ndrdisc
    10ge2p1x520-ethip6-ip6scale200k-ndrdisc.robot:| tc13-78B-4t4c-ethip6-ip6scale200k-ndrdisc
    10ge2p1x520-ethip6-ip6scale20k-ndrdisc.robot:| tc13-78B-4t4c-ethip6-ip6scale20k-ndrdisc
    10ge2p1x520-ethip6-ip6scale2m-ndrdisc.robot:| tc13-78B-4t4c-ethip6-ip6scale2m-ndrdisc
    40ge2p1xl710-ethip6-ip6base-ndrdisc.robot:| tc13-78B-4t4c-ethip6-ip6base-ndrdisc

PDR Throughput
~~~~~~~~~~~~~~

VPP PDR Throughput - running in configuration of **one worker thread (1t) on one
physical core (1c)** - is presented in the figure below. PDR at below 0.5%
packet loss ratio.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/78B-1t1c-ethip6-ip6-pdrdisc.html"></iframe>

*Figure 4. VPP 1thread 1core - PDR Throughput for Phy-to-Phy IPv6
Routed-Forwarding.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" *

    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrdisc.robot:| tc02-78B-1t1c-ethip6-ip6base-copwhtlistbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrdisc.robot:| tc02-78B-1t1c-ethip6-ip6base-iacldstbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-ndrdisc.robot:| tc02-78B-1t1c-ethip6-ip6base-pdrdisc
    10ge2p1x520-ethip6-ip6scale200k-ndrdisc.robot:| tc02-78B-1t1c-ethip6-ip6scale200k-pdrdisc
    10ge2p1x520-ethip6-ip6scale20k-ndrdisc.robot:| tc02-78B-1t1c-ethip6-ip6scale20k-pdrdisc
    10ge2p1x520-ethip6-ip6scale2m-ndrdisc.robot:| tc02-78B-1t1c-ethip6-ip6scale2m-pdrdisc

VPP PDR Throughput - running in configuration of **two worker threads (2t) on
two physical cores (2c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/78B-2t2c-ethip6-ip6-pdrdisc.html"></iframe>

*Figure 5. VPP 2thread 2core - PDR Throughput for Phy-to-Phy IPv6
Routed-Forwarding.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" *

    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrdisc.robot:| tc08-78B-2t2c-ethip6-ip6base-copwhtlistbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrdisc.robot:| tc08-78B-2t2c-ethip6-ip6base-iacldstbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-ndrdisc.robot:| tc08-78B-2t2c-ethip6-ip6base-pdrdisc
    10ge2p1x520-ethip6-ip6scale200k-ndrdisc.robot:| tc08-78B-2t2c-ethip6-ip6scale200k-pdrdisc
    10ge2p1x520-ethip6-ip6scale20k-ndrdisc.robot:| tc08-78B-2t2c-ethip6-ip6scale20k-pdrdisc
    10ge2p1x520-ethip6-ip6scale2m-ndrdisc.robot:| tc08-78B-2t2c-ethip6-ip6scale2m-pdrdisc

VPP PDR Throughput - running in configuration of **four worker threads (4t) on
four physical cores (4c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/78B-4t4c-ethip6-ip6-pdrdisc.html"></iframe>

*Figure 6. VPP 4thread 4core - PDR Throughput for Phy-to-Phy IPv6
Routed-Forwarding.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-4t4c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" *

    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrdisc.robot:| tc14-78B-4t4c-ethip6-ip6base-copwhtlistbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrdisc.robot:| tc14-78B-4t4c-ethip6-ip6base-iacldstbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-ndrdisc.robot:| tc14-78B-4t4c-ethip6-ip6base-pdrdisc
    10ge2p1x520-ethip6-ip6scale200k-ndrdisc.robot:| tc14-78B-4t4c-ethip6-ip6scale200k-pdrdisc
    10ge2p1x520-ethip6-ip6scale20k-ndrdisc.robot:| tc14-78B-4t4c-ethip6-ip6scale20k-pdrdisc
    10ge2p1x520-ethip6-ip6scale2m-ndrdisc.robot:| tc14-78B-4t4c-ethip6-ip6scale2m-pdrdisc


