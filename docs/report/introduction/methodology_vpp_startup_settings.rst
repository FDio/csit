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
#. buffers-per-numa <value> - increases number of buffers allocated, needed
   in scenarios with large number of interfaces and worker threads.
   Value is per CPU socket. Default is 16384. CSIT is setting statically
   107520 buffers per CPU thread (215040 if HTT is enabled). This value is also
   maximum possible amount limited by number of memory mappings in DPDK
   libraries for 2MB Hugepages used in CSIT.

Per Test Settings
~~~~~~~~~~~~~~~~~

List of vpp startup.conf settings applied dynamically per test:

#. corelist-workers <list_of_cores> - list of logical cores to run VPP
   worker data plane threads. Depends on HyperThreading and core per
   test configuration.
#. num-rx-queues <value> - depends on a number of VPP threads and NIC
   interfaces.
#. no-multi-seg - disables multi-segment buffers in DPDK, improves
   packet throughput, but disables Jumbo MTU support. Disabled for all
   tests apart from the ones that require Jumbo 9000B frame support.
#. UIO driver - depends on topology file definition.
#. QAT VFs - depends on NRThreads, each thread = 1QAT VFs.
