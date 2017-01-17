IPv6 Routed-Forwarding
======================

.. note::

    Source of data `csit-vpp-perf-1701-all
    <https://jenkins.fd.io/view/csit/job/csit-vpp-perf-1701-all/>`_ and
    `csit-vpp-perf-1701-long
    <https://jenkins.fd.io/view/csit/job/csit-vpp-perf-1701-long/>`_.

NDR Throughput Measurements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/78B-1t1c-ethip6-ip6-ndrdisc.html"></iframe>

**Figure 1:** IPv6 Routed-Forwarding NDR Throughput Measurements

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

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/78B-2t2c-ethip6-ip6-ndrdisc.html"></iframe>

**Figure 2:** IPv6 Routed-Forwarding NDR Throughput Measurements

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

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/78B-4t4c-ethip6-ip6-ndrdisc.html"></iframe>

**Figure 3:** IPv6 Routed-Forwarding NDR Throughput Measurements

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

PDR Throughput Measurements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/78B-1t1c-ethip6-ip6-pdrdisc.html"></iframe>

**Figure 1:** IPv6 Routed-Forwarding PDR Throughput Measurements

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" *

    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrdisc.robot:| tc02-78B-1t1c-ethip6-ip6base-copwhtlistbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrdisc.robot:| tc02-78B-1t1c-ethip6-ip6base-iacldstbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-ndrdisc.robot:| tc02-78B-1t1c-ethip6-ip6base-pdrdisc
    10ge2p1x520-ethip6-ip6scale200k-ndrdisc.robot:| tc02-78B-1t1c-ethip6-ip6scale200k-pdrdisc
    10ge2p1x520-ethip6-ip6scale20k-ndrdisc.robot:| tc02-78B-1t1c-ethip6-ip6scale20k-pdrdisc
    10ge2p1x520-ethip6-ip6scale2m-ndrdisc.robot:| tc02-78B-1t1c-ethip6-ip6scale2m-pdrdisc

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/78B-2t2c-ethip6-ip6-pdrdisc.html"></iframe>

**Figure 2:** IPv6 Routed-Forwarding PDR Throughput Measurements

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" *

    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrdisc.robot:| tc08-78B-2t2c-ethip6-ip6base-copwhtlistbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrdisc.robot:| tc08-78B-2t2c-ethip6-ip6base-iacldstbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-ndrdisc.robot:| tc08-78B-2t2c-ethip6-ip6base-pdrdisc
    10ge2p1x520-ethip6-ip6scale200k-ndrdisc.robot:| tc08-78B-2t2c-ethip6-ip6scale200k-pdrdisc
    10ge2p1x520-ethip6-ip6scale20k-ndrdisc.robot:| tc08-78B-2t2c-ethip6-ip6scale20k-pdrdisc
    10ge2p1x520-ethip6-ip6scale2m-ndrdisc.robot:| tc08-78B-2t2c-ethip6-ip6scale2m-pdrdisc

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/78B-4t4c-ethip6-ip6-pdrdisc.html"></iframe>

**Figure 3:** IPv6 Routed-Forwarding PDR Throughput Measurements

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-4t4c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" *

    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrdisc.robot:| tc14-78B-4t4c-ethip6-ip6base-copwhtlistbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrdisc.robot:| tc14-78B-4t4c-ethip6-ip6base-iacldstbase-pdrdisc
    10ge2p1x520-ethip6-ip6base-ndrdisc.robot:| tc14-78B-4t4c-ethip6-ip6base-pdrdisc
    10ge2p1x520-ethip6-ip6scale200k-ndrdisc.robot:| tc14-78B-4t4c-ethip6-ip6scale200k-pdrdisc
    10ge2p1x520-ethip6-ip6scale20k-ndrdisc.robot:| tc14-78B-4t4c-ethip6-ip6scale20k-pdrdisc
    10ge2p1x520-ethip6-ip6scale2m-ndrdisc.robot:| tc14-78B-4t4c-ethip6-ip6scale2m-pdrdisc

