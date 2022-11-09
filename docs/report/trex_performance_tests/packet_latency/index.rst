
.. raw:: latex

    \clearpage

Packet Latency
==============

TRex latency results are generated based on the test
data obtained from |csit-release| NDR-PDR throughput tests executed
across physical testbeds hosted in LF FD.io labs: 2n-skx.

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
    `build logs from FD.io trex performance job 2n-icx`_.

.. toctree::
    :maxdepth: 3

    2n-icx-e810cq

..
    1n-aws-nitro50g
