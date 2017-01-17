IPv4 Routed-Forwarding
======================

.. note::

    Source of data `csit-vpp-perf-1701-all
    <https://jenkins.fd.io/view/csit/job/csit-vpp-perf-1701-all/>`_ and
    `csit-vpp-perf-1701-long
    <https://jenkins.fd.io/view/csit/job/csit-vpp-perf-1701-long/>`_.

NDR Throughput Measurements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-1t1c-ethip4-ip4-ndrdisc.html"></iframe>

**Figure 1:** IPv4 Routed-Forwarding NDR Throughput Measurements

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

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-2t2c-ethip4-ip4-ndrdisc.html"></iframe>

**Figure 2:** IPv4 Routed-Forwarding NDR Throughput Measurements

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

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-4t4c-ethip4-ip4-ndrdisc.html"></iframe>

**Figure 3:** IPv4 Routed-Forwarding NDR Throughput Measurements

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

PDR Throughput Measurements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-1t1c-ethip4-ip4-pdrdisc.html"></iframe>

**Figure 1:** IPv4 Routed-Forwarding PDR Throughput Measurements

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

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-2t2c-ethip4-ip4-pdrdisc.html"></iframe>

**Figure 2:** IPv4 Routed-Forwarding PDR Throughput Measurements

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

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-4t4c-ethip4-ip4-pdrdisc.html"></iframe>

**Figure 3:** IPv4 Routed-Forwarding PDR Throughput Measurements

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

