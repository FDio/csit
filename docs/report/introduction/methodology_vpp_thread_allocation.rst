.. _vpp_thread_allocation_methodology:

VPP Thread Allocation
---------------------

In CSIT, VPP default configuration for corelist-workers and num-rx-queues is
being overriden for every test case.

List of VPP startup.conf configuration items affected:

#. corelist-workers <list_of_cores> - list of logical cores to run VPP
   worker data plane threads. Depends on HyperThreading and core per
   test configuration.
#. num-rx-queues <value> - depends on a number of VPP threads and NIC
   interfaces.

While this configuration items allows CSIT to globally configure VPP resource
allocation there is a need to create virtual context in CSIT to be able to
handle resource management per testcase.

Thread Virtual Context
~~~~~~~~~~~~~~~~~~~~~~

CSIT in rls2106 introduced the virtual context that separates the thread usage
for data plane threads and feature plane threads.

#. data plane threads - Threads isolated and used for VPP data plane packet
   processing.
#. feature plane threads - Threads isolated and used for VPP features. E.g.
   IPSec async crypto workers.

Number of RX Queues
~~~~~~~~~~~~~~~~~~~

As of rls2106 CSIT is configuring the same amount of RX queue threads as number
of data plane threads for every testcase and all physical and virtual
interfaces.
