.. raw:: latex

    \clearpage

.. _VPP_HDRH_Packet_Latency:

Packet Latency
==============

VPP latency results are generated based on the test data obtained from
|csit-release| NDR-PDR throughput tests executed across physical
testbeds hosted in LF FD.io labs: 3n-skx, 2n-skx, 2n-clx, 3n-tsh, 2n-tx2,
2n-zn2, 2n-aws.

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
    `build logs from FD.io vpp performance job 2n-icx`_,
    `build logs from FD.io vpp performance job 3n-icx`_,
    `build logs from FD.io vpp performance job 2n-aws`_,
    `build logs from FD.io vpp performance job 2n-skx`_,
    `build logs from FD.io vpp performance job 3n-skx`_,
    `build logs from FD.io vpp performance job 2n-clx`_,
    `build logs from FD.io vpp performance job 2n-zn2`_,
    `build logs from FD.io vpp performance job 3n-tsh`_ and
    `build logs from FD.io vpp performance job 2n-tx2`_ with RF
    result files csit-vpp-perf-|srelease|-\*.zip
    `archived here <../../_static/archive/>`_.

.. toctree::
    :maxdepth: 3

    l2
    ip4
    ip6
    srv6
    ip4_tunnels
    nat44
    vm_vhost
    container_memif
    ipsec
