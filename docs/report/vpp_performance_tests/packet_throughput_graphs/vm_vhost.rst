VM vhost Connections
====================

Following sections provide a summary of VPP Phy-to-VM-to-Phy VM vhost-user
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

VPP NDR Throughput - running in configuration of **one worker thread (1t) on one
physical core (1c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-vhost-ndrdisc.html"></iframe>

*Figure 1. VPP 1thread 1core - NDR Throughput for Phy-to-VM-to-Phy VM
vhost-user.*

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

VPP NDR Throughput - running in configuration of **two worker threads (2t) on
two physical cores (2c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-vhost-ndrdisc.html"></iframe>

*Figure 2. VPP 2threads 2cores - NDR Throughput for Phy-to-VM-to-Phy VM
vhost-user.*

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

VPP NDR Throughput - running in configuration of **four worker threads (4t) on
four physical cores (4c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-4t4c-vhost-ndrdisc.html"></iframe>

*Figure 3. VPP 4threads 4cores - NDR Throughput for Phy-to-VM-to-Phy VM
vhost-user.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-4t4c-.*vhost.*-ndrdisc" *

    10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc13-64B-4t4c-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-dot1q-l2xcbase-eth-2vhost-1vm-ndrdisc.robot:| tc13-64B-4t4c-eth-l2xcbase-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-ethip4-ip4base-eth-2vhost-1vm-ndrdisc.robot:| tc13-64B-4t4c-ethip4-ip4base-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc13-64B-4t4c-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc13-64B-4t4c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    10ge2p1x520-eth-l2xcbase-eth-2vhost-1vm-ndrdisc.robot:| tc13-64B-4t4c-eth-l2xcbase-eth-2vhost-1vm-ndrdisc
    10ge2p1x710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc13-64B-4t4c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc
    40ge2p1xl710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc13-64B-4t4c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc

PDR Throughput
~~~~~~~~~~~~~~

VPP PDR Throughput - running in configuration of **one worker thread (1t) on one
physical core (1c)** - is presented in the figure below. PDR at below 0.5%
packet loss ratio.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-vhost-pdrdisc.html"></iframe>

*Figure 4. VPP 1thread 1core - PDR Throughput for Phy-to-VM-to-Phy VM
vhost-user.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-1t1c-.*vhost.*-pdrdisc" *

    10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc02-64B-1t1c-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-dot1q-l2xcbase-eth-2vhost-1vm-ndrdisc.robot:| tc02-64B-1t1c-eth-l2xcbase-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-ethip4-ip4base-eth-2vhost-1vm-ndrdisc.robot:| tc02-64B-1t1c-ethip4-ip4base-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc02-64B-1t1c-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc02-64B-1t1c-eth-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-eth-l2xcbase-eth-2vhost-1vm-ndrdisc.robot:| tc02-64B-1t1c-eth-l2xcbase-eth-2vhost-1vm-pdrdisc
    10ge2p1x710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc02-64B-1t1c-eth-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc
    40ge2p1xl710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc02-64B-1t1c-eth-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc

VPP PDR Throughput - running in configuration of **two worker threads (2t) on
two physical cores (2c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-vhost-pdrdisc.html"></iframe>

*Figure 5. VPP 2thread 2core - PDR Throughput for Phy-to-VM-to-Phy VM
vhost-user.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-2t2c-.*vhost.*-pdrdisc" *

    10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc08-64B-2t2c-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-dot1q-l2xcbase-eth-2vhost-1vm-ndrdisc.robot:| tc08-64B-2t2c-eth-l2xcbase-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-ethip4-ip4base-eth-2vhost-1vm-ndrdisc.robot:| tc08-64B-2t2c-ethip4-ip4base-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc08-64B-2t2c-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc08-64B-2t2c-eth-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-eth-l2xcbase-eth-2vhost-1vm-ndrdisc.robot:| tc08-64B-2t2c-eth-l2xcbase-eth-2vhost-1vm-pdrdisc
    10ge2p1x710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc08-64B-2t2c-eth-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc
    40ge2p1xl710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc08-64B-2t2c-eth-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc

VPP PDR Throughput - running in configuration of **four worker threads (4t) on
four physical cores (4c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/vpp/64B-4t4c-vhost-pdrdisc.html"></iframe>

*Figure 6. VPP 4thread 4core - PDR Throughput for Phy-to-VM-to-Phy VM
vhost-user.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-4t4c-.*vhost.*-pdrdisc" *

    10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc14-64B-4t4c-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-dot1q-l2xcbase-eth-2vhost-1vm-ndrdisc.robot:| tc14-64B-4t4c-eth-l2xcbase-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-ethip4-ip4base-eth-2vhost-1vm-ndrdisc.robot:| tc14-64B-4t4c-ethip4-ip4base-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc14-64B-4t4c-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc14-64B-4t4c-eth-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc
    10ge2p1x520-eth-l2xcbase-eth-2vhost-1vm-ndrdisc.robot:| tc14-64B-4t4c-eth-l2xcbase-eth-2vhost-1vm-pdrdisc
    10ge2p1x710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc14-64B-4t4c-eth-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc
    40ge2p1xl710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot:| tc14-64B-4t4c-eth-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc

