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

While this configuration items allows CSIT to  globally configure VPP resources
allocation there is a need to create virtual context in CSIT to be able to
handle resource management per testcase

Virtual context
~~~~~~~~~~~~~~~

CSIT rls2106 introduced the virtual context that separate the thread usage for
data plane threads and feature plane threads.

#. data plane threads
#. feature plane threads

Number of RX queues
~~~~~~~~~~~~~~~~~~~

CSIT as of rls2106 CSIT is configuring same amount of RX queue thraeds as number
of data plane threads.

