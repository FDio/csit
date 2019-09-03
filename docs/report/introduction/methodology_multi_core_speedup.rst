Multi-Core Speedup
------------------

All performance tests are executed with both single processor core and with
multiple cores scenarios.

Intel Hyper-Threading (HT)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Intel Xeon processors used in FD.io CSIT can operate either in HT
Disabled mode (single logical core per each physical core) or in HT
Enabled mode (two logical cores per each physical core). HT setting is
applied in BIOS and requires server SUT reload for it to take effect,
making it impractical for continuous changes of HT mode of operation.

|csit-release| performance tests are executed with server SUTs' Intel
XEON processors configured with Intel Hyper-Threading Disabled for all
Xeon Haswell testbeds (3n-hsw) and with Intel Hyper-Threading Enabled
for all Xeon Skylake testbeds.

More information about physical testbeds is provided in
:ref:`tested_physical_topologies`.

Multi-core Tests
~~~~~~~~~~~~~~~~

|csit-release| multi-core tests are executed in the following VPP worker
thread and physical core configurations:

#. Intel Xeon Haswell testbeds (3n-hsw) with Intel HT disabled
   (1 logical CPU core per each physical core):

  #. 1t1c - 1 VPP worker thread on 1 physical core.
  #. 2t2c - 2 VPP worker threads on 2 physical cores.
  #. 4t4c - 4 VPP worker threads on 4 physical cores.

#. Intel Xeon Skylake testbeds (2n-skx, 3n-skx) with Intel HT enabled
   (2 logical CPU cores per each physical core):

  #. 2t1c - 2 VPP worker threads on 1 physical core.
  #. 4t2c - 4 VPP worker threads on 2 physical cores.
  #. 8t4c - 8 VPP worker threads on 4 physical cores.

VPP worker threads are the data plane threads running on isolated
logical cores. With Intel HT enabled, VPP workers are placed as sibling
threads on each used physical core. VPP control threads (main, stats)
are running on a separate, non-isolated core, together with other Linux
processes.

In all CSIT tests, care is taken to ensure that each VPP worker handles
the same amount of received packet load and does the same amount of
packet processing work. This is achieved by evenly distributing per
interface type (e.g. physical, virtual) receive queues over VPP workers,
using default VPP round-robin mapping, and by loading these queues with
the same amount of packet flows.

If number of VPP workers is higher than number of physical or virtual
interfaces, multiple receive queues are configured on each interface.
NIC Receive Side Scaling (RSS) for physical interfaces and multi-queue
for virtual interfaces are used for this purpose.

Section :ref:`throughput_speedup_multi_core` includes a set of graphs
illustrating packet throughout speedup when running VPP worker threads
on multiple cores. Note that in quite a few test cases, running VPP
workers on 2 or 4 physical cores hits the I/O bandwidth
or packets-per-second limit of the tested NIC.
