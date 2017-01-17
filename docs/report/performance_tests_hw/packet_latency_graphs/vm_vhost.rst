VM vhost Connections
====================

.. note::

    Source of data `csit-vpp-perf-1701-all
    <https://jenkins.fd.io/view/csit/job/csit-vpp-perf-1701-all/>`_ and
    `csit-vpp-perf-1701-long
    <https://jenkins.fd.io/view/csit/job/csit-vpp-perf-1701-long/>`_.

.. note::

    Latency data are captured at 50% of NDR rate.

Latency Measurements
~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-1t1c-vhost-ndrdisc-lat50.html"></iframe>

**Figure 1:** VM vhost Connections Latency Measurements

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

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-2t2c-vhost-ndrdisc-lat50.html"></iframe>

**Figure 2:** VM vhost Connections Latency Measurements

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

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/64B-4t4c-vhost-ndrdisc-lat50.html"></iframe>

**Figure 3:** VM vhost Connections Latency Measurements

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
