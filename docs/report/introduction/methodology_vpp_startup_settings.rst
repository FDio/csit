VPP Startup Settings
--------------------

CSIT code manipulates a number of VPP settings in startup.conf for optimized
performance. List of common settings applied to all tests and test
dependent settings follows.

See `VPP startup.conf`_
for a complete set and description of listed settings.

Common Settings
~~~~~~~~~~~~~~~

List of vpp startup.conf settings applied to all tests:

#. heap-size <value> - set separately for ip4, ip6, stats, main
   depending on scale tested.
#. no-tx-checksum-offload - disables UDP / TCP TX checksum offload in DPDK.
   Typically needed for use faster vector PMDs (together with
   no-multi-seg).
#. socket-mem <value>,<value> - memory per numa. (Not required anymore
   due to VPP code changes, should have been removed already in CSIT-18.10.)

Per Test Settings
~~~~~~~~~~~~~~~~~

List of vpp startup.conf settings applied dynamically per test:

#. corelist-workers <list_of_cores> - list of logical cores to run VPP
   worker data plane threads. Depends on HyperThreading and core per
   test configuration.
#. num-rx-queues <value> - depends on a number of VPP threads and NIC
   interfaces.
#. num-rx-desc/num-tx-desc - number of rx/tx descriptors for specific
   NICs, incl. xl710, x710, xxv710.
#. num-mbufs <value> - increases number of buffers allocated, needed
   only in scenarios with large number of interfaces and worker threads.
   Value is per CPU socket. Default is 16384.
#. no-multi-seg - disables multi-segment buffers in DPDK, improves
   packet throughput, but disables Jumbo MTU support. Disabled for all
   tests apart from the ones that require Jumbo 9000B frame support.
#. UIO driver - depends on topology file definition.
#. QAT VFs - depends on NRThreads, each thread = 1QAT VFs.
