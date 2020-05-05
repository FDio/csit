Mellanox NIC
------------

Performance test results using Mellanox ConnectX5 2p100GE are reported for
2-Node Xeon Cascade Lake physical testbed type present in FD.io labs. For
description of physical testbeds used please refer to
:ref:`tested_physical_topologies`.

Mellanox NIC settings
~~~~~~~~~~~~~~~~~~~~~

Mellanox ConnectX5 NIC settings are following recommendations from
[DpdkPerformanceReport]_, [MellanoxDpdkGuide]_ and [MellanoxDpdkBits]_.
Specifically:

- Flow Control OFF:
  ::

      $ ethtool -A $netdev rx off tx off


- Change PCI MaxReadReq to 1024B for each port of each NIC:
  ::

      $ setpci -s $PORT_PCI_ADDRESS 68.w=3BCD

- Set CQE COMPRESSION to "AGGRESSIVE":
  ::

      $ mlxconfig -d $PORT_PCI_ADDRESS set CQE_COMPRESSION=1

Mellanox :abbr:`OFED (OpenFabrics Enterprise Distribution)` driver of version
4.6-1.0.1.1 is installed and used to manage the NIC settings.

TG and SUT settings
~~~~~~~~~~~~~~~~~~~

For the TG and SUT environment settings please refer to
:ref:`_vpp_test_environment` and :ref:`_dpdk_test_environment`.

Links
~~~~~

.. [DpdkPerformanceReport] `DPDK 19.11 performance report <http://static.dpdk.org/doc/perf/DPDK_19_11_Mellanox_NIC_performance_report.pdf>`
.. [MellanoxDpdkGuide] `Mellanox DPDK guide <https://www.mellanox.com/related-docs/prod_software/MLNX_DPDK_Quick_Start_Guide_v16.11_3.0.pdf>`
.. [MellanoxDpdkBits] `Mellanox DPDK bits <https://community.mellanox.com/s/article/mellanox-dpdk>`
