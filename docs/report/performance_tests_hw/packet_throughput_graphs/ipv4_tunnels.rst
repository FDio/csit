IPv4 Overlay Tunnels
====================

.. note::

    Source of data `csit-vpp-perf-1701-all
    <https://jenkins.fd.io/view/csit/job/csit-vpp-perf-1701-all/>`_ and
    `csit-vpp-perf-1701-long
    <https://jenkins.fd.io/view/csit/job/csit-vpp-perf-1701-long/>`_.

NDR Throughput Measurements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-1t1c-ethip4-ndrdisc.html"></iframe>

**Figure 1:** IPv4 Overlay Tunnels NDR Throughput Measurements

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" *

    10ge2p1x520-ethip4lispip4-ip4base-ndrdisc.robot:| tc01-64B-1t1c-ethip4lispip4-ip4base-ndrdisc
    10ge2p1x520-ethip4lispip6-ip4base-ndrdisc.robot:| tc01-64B-1t1c-ethip4lispip6-ip4base-ndrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-ndrdisc.robot:| tc01-64B-1t1c-ethip4vxlan-l2bdbasemaclrn-ndrdisc
    10ge2p1x520-ethip4vxlan-l2xcbase-ndrdisc.robot:| tc01-64B-1t1c-ethip4vxlan-l2xcbase-ndrdisc

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-2t2c-ethip4-ndrdisc.html"></iframe>

**Figure 2:** IPv4 Overlay Tunnels NDR Throughput Measurements

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" *

    10ge2p1x520-ethip4lispip4-ip4base-ndrdisc.robot:| tc07-64B-2t2c-ethip4lispip4-ip4base-ndrdisc
    10ge2p1x520-ethip4lispip6-ip4base-ndrdisc.robot:| tc07-64B-2t2c-ethip4lispip6-ip4base-ndrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-ndrdisc.robot:| tc07-64B-2t2c-ethip4vxlan-l2bdbasemaclrn-ndrdisc
    10ge2p1x520-ethip4vxlan-l2xcbase-ndrdisc.robot:| tc07-64B-2t2c-ethip4vxlan-l2xcbase-ndrdisc

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-4t4c-ethip4-ndrdisc.html"></iframe>

**Figure 3:** IPv4 Overlay Tunnels NDR Throughput Measurements

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-4t4c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" *

    10ge2p1x520-ethip4lispip4-ip4base-ndrdisc.robot:| tc13-64B-4t4c-ethip4lispip4-ip4base-ndrdisc
    10ge2p1x520-ethip4lispip6-ip4base-ndrdisc.robot:| tc13-64B-4t4c-ethip4lispip6-ip4base-ndrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-ndrdisc.robot:| tc13-64B-4t4c-ethip4vxlan-l2bdbasemaclrn-ndrdisc
    10ge2p1x520-ethip4vxlan-l2xcbase-ndrdisc.robot:| tc13-64B-4t4c-ethip4vxlan-l2xcbase-ndrdisc

PDR Throughput Measurements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-1t1c-ethip4-pdrdisc.html"></iframe>

**Figure 1:** IPv4 Overlay Tunnels PDR Throughput Measurements

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-pdrdisc" *

    10ge2p1x520-ethip4lispip4-ip4base-ndrdisc.robot:| tc02-64B-1t1c-ethip4lispip4-ip4base-pdrdisc
    10ge2p1x520-ethip4lispip6-ip4base-ndrdisc.robot:| tc02-64B-1t1c-ethip4lispip6-ip4base-pdrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-ndrdisc.robot:| tc02-64B-1t1c-ethip4vxlan-l2bdbasemaclrn-pdrdisc
    10ge2p1x520-ethip4vxlan-l2xcbase-ndrdisc.robot:| tc02-64B-1t1c-ethip4vxlan-l2xcbase-pdrdisc

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-2t2c-ethip4-pdrdisc.html"></iframe>

**Figure 2:** IPv4 Overlay Tunnels PDR Throughput Measurements

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-pdrdisc" *

    10ge2p1x520-ethip4lispip4-ip4base-ndrdisc.robot:| tc08-64B-2t2c-ethip4lispip4-ip4base-pdrdisc
    10ge2p1x520-ethip4lispip6-ip4base-ndrdisc.robot:| tc08-64B-2t2c-ethip4lispip6-ip4base-pdrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-ndrdisc.robot:| tc08-64B-2t2c-ethip4vxlan-l2bdbasemaclrn-pdrdisc
    10ge2p1x520-ethip4vxlan-l2xcbase-ndrdisc.robot:| tc08-64B-2t2c-ethip4vxlan-l2xcbase-pdrdisc

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-4t4c-ethip4-pdrdisc.html"></iframe>

**Figure 3:** IPv4 Overlay Tunnels PDR Throughput Measurements

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "64B-4t4c-ethip4[a-z0-9]+-[a-z0-9]*-pdrdisc" *

    10ge2p1x520-ethip4lispip4-ip4base-ndrdisc.robot:| tc14-64B-4t4c-ethip4lispip4-ip4base-pdrdisc
    10ge2p1x520-ethip4lispip6-ip4base-ndrdisc.robot:| tc14-64B-4t4c-ethip4lispip6-ip4base-pdrdisc
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-ndrdisc.robot:| tc14-64B-4t4c-ethip4vxlan-l2bdbasemaclrn-pdrdisc
    10ge2p1x520-ethip4vxlan-l2xcbase-ndrdisc.robot:| tc14-64B-4t4c-ethip4vxlan-l2xcbase-pdrdisc

