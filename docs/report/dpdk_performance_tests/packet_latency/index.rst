
.. raw:: latex

    \clearpage

Packet Latency
==============

DPDK Testpmd and L3fwd latency results are generated based on the test
data obtained from |csit-release| NDR-PDR throughput tests executed
across physical testbeds hosted in LF FD.io labs: 2n-icx, 3n-icx, 3n-skx, 2n-
skx, 2n-clx, 3n-dnv, 2n-dnv, 3n-tsh, 2n-tx2.

Latency by percentile distribution plots are used to show packet latency
percentiles at different packet rate load levels: i) No-Load latency
streams only, ii) Low-Load at 10% PDR, iii) Mid-Load at 50% PDR and iv)
High-Load at 90% PDR.

For more details, see :ref:`latency_methodology`.

Additional information about graph data:

#. **Graph Title**: describes tested DUT packet path.

#. **X-axis Labels**: percentile of packets.

#. **Y-axis Labels**: measured one-way packet latency values in [uSec].

#. **Graph Legend**: list of latency tests at different packet rate load
   level.

#. **Hover Information**: packet rate load level, stream direction
   (East-West, West-East), percentile, one-way latency.

.. note::

    Test results are stored in
    `build logs from FD.io dpdk performance job 2n-icx`_,
    `build logs from FD.io dpdk performance job 3n-icx`_,
    `build logs from FD.io dpdk performance job 2n-skx`_,
    `build logs from FD.io dpdk performance job 2n-clx`_,
    `build logs from FD.io dpdk performance job 3n-skx`_,
    `build logs from FD.io dpdk performance job 2n-zn2`_,
    `build logs from FD.io dpdk performance job 3n-alt`_,
    `build logs from FD.io dpdk performance job 3n-tsh`_ and
    `build logs from FD.io dpdk performance job 2n-tx2`_ with RF
    result files csit-dpdk-perf-|srelease|-\*.zip
    `archived here <../../_static/archive/>`_.

.. toctree::
    :maxdepth: 3

    2n-icx-xxv710
    3n-icx-xxv710
    2n-skx-xxv710
    3n-skx-xxv710
    2n-clx-xxv710
    2n-zn2-xxv710
    3n-alt-xl710
    3n-tsh-x520
    2n-tx2-xl710
