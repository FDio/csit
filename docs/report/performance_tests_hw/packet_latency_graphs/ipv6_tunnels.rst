IPv6 Overlay Tunnels
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

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/78B-1t1c-ethip6-ndrdisc-lat50.html"></iframe>

**Figure 1:** IPv6 Overlay Tunnels Latency Measurements

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" *

    10ge2p1x520-ethip6lispip4-ip6base-ndrdisc.robot:| tc01-78B-1t1c-ethip6lispip4-ip6base-ndrdisc
    10ge2p1x520-ethip6lispip6-ip6base-ndrdisc.robot:| tc01-78B-1t1c-ethip6lispip6-ip6base-ndrdisc

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/78B-2t2c-ethip6-ndrdisc-lat50.html"></iframe>

**Figure 2:** IPv6 Overlay Tunnels Latency Measurements

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" *

    10ge2p1x520-ethip6lispip4-ip6base-ndrdisc.robot:| tc07-78B-2t2c-ethip6lispip4-ip6base-ndrdisc
    10ge2p1x520-ethip6lispip6-ip6base-ndrdisc.robot:| tc07-78B-2t2c-ethip6lispip6-ip6base-ndrdisc

.. raw:: html

    <iframe width="700" height="700" frameborder="0" scrolling="no" src="../../_static/78B-4t4c-ethip6-ndrdisc-lat50.html"></iframe>

**Figure 3:** IPv6 Overlay Tunnels Latency Measurements

.. code-block:: bash

    $ csit/tests/perf
    $ grep -E "78B-4t4c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" *

    10ge2p1x520-ethip6lispip4-ip6base-ndrdisc.robot:| tc13-78B-4t4c-ethip6lispip4-ip6base-ndrdisc
    10ge2p1x520-ethip6lispip6-ip6base-ndrdisc.robot:| tc13-78B-4t4c-ethip6lispip6-ip6base-ndrdisc

