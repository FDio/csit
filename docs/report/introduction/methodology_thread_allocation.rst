.. _thread_allocation_methodology:

Thread Allocation
-----------------

In CSIT, default configuration for workers and number of RX queues per port
is being overriden for every test case.

List of VPP startup.conf configuration items affected:

#. corelist-workers <list_of_cores> - list of logical cores to run VPP
   worker data plane threads. Depends on HyperThreading and core per
   test configuration.
#. num-rx-queues <value> - Number of RX queues per port to value.

List of DPDK testpmd/l3fwd startup parameters affected:

#. nb-cores=N - Number of forwarding cores, where 1 <= N <= "number of cores".
   Depends on HyperThreading and core per test configuration.
#. rxq=N - Number of RX queues per port to N.

While this configuration items allows CSIT to globally configure resource
allocation there is a need to create virtual context in CSIT to be able to
handle resource management in more granular way.

Core Virtual Context
~~~~~~~~~~~~~~~~~~~~

CSIT in rls2106 introduced the virtual context that splits the cores to data
plane and feature plane cores.

#. data plane cores - Cores isolated and used for data plane packet
   forwarding.
#. feature plane cores - Cores isolated and used for features processing. E.g.
   IPSec async crypto workers.

By default, if not specified, all CPU cores specified by testcase are classified
as data plane cores. Configuration of data plane core count, not higher then
the total number of physical cores used by single instance of NF, can be done on
suite level. Feature plane cores can be configured on suite level or are
automatically derived from total number of cores without data plane cores.

Number of threads for each type of core depends on HyperThreading settings
of the SUT.

Number of RX Queues
~~~~~~~~~~~~~~~~~~~

As of rls2106 CSIT is configuring the same amount of RX queues as number
of data plane threads for every testcase and all physical and virtual
interfaces.
