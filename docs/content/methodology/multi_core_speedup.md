---
bookToc: false
title: "Multi-Core Speedup"
weight: 13
---

# Multi-Core Speedup

All performance tests are executed with single physical core and with
multiple cores scenarios.

## Intel Hyper-Threading (HT)

Intel Xeon processors used in FD.io CSIT can operate either in HT
Disabled mode (single logical core per each physical core) or in HT
Enabled mode (two logical cores per each physical core). HT setting is
applied in BIOS and requires server SUT reload for it to take effect,
making it impractical for continuous changes of HT mode of operation.

Performance tests are executed with server SUTs' Intel XEON processors
configured with Intel Hyper-Threading Enabled for all Xeon
Cascadelake and Xeon Icelake testbeds.

## Multi-core Tests

Multi-core tests are executed in the following VPP worker thread and physical
core configurations:

#. Intel Xeon Icelake and Cascadelake testbeds (2n-icx, 3n-icx, 2n-clx)
   with Intel HT enabled (2 logical CPU cores per each physical core):

  #. 2t1c - 2 VPP worker threads on 1 physical core.
  #. 4t2c - 4 VPP worker threads on 2 physical cores.
  #. 8t4c - 8 VPP worker threads on 4 physical cores.

VPP worker threads are the data plane threads running on isolated
logical cores. With Intel HT enabled VPP workers are placed as sibling
threads on each used physical core. VPP control threads (main, stats)
are running on a separate non-isolated core together with other Linux
processes.

In all CSIT tests care is taken to ensure that each VPP worker handles
the same amount of received packet load and does the same amount of
packet processing work. This is achieved by evenly distributing per
interface type (e.g. physical, virtual) receive queues over VPP workers
using default VPP round-robin mapping and by loading these queues with
the same amount of packet flows.

If number of VPP workers is higher than number of physical or virtual
interfaces, multiple receive queues are configured on each interface.
NIC Receive Side Scaling (RSS) for physical interfaces and multi-queue
for virtual interfaces are used for this purpose.