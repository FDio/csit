---
title: "VPP Startup Settings"
weight: 17
---

# VPP Startup Settings

CSIT code manipulates a number of VPP settings in startup.conf for
optimized performance. List of common settings applied to all tests and
test dependent settings follows.

## Common Settings

List of VPP startup.conf settings applied to all tests:

1. heap-size <value> - set separately for ip4, ip6, stats, main
   depending on scale tested.
2. no-tx-checksum-offload - disables UDP / TCP TX checksum offload in
   DPDK. Typically needed for use faster vector PMDs (together with
   no-multi-seg).
3. buffers-per-numa <value> - sets a number of memory buffers allocated
   to VPP per CPU socket. VPP default is 16384. Needs to be increased for
   scenarios with large number of interfaces and worker threads. To
   accommodate for scale tests, CSIT is setting it to the maximum possible
   value corresponding to the limit of DPDK memory mappings (currently
   256). For Xeon Skylake platforms configured with 2MB hugepages and VPP
   data-size and buffer-size defaults (2048B and 2496B respectively), this
   results in value of 215040 (256 * 840 = 215040, 840 * 2496B buffers fit
   in 2MB hugepage).

## Per Test Settings

List of vpp startup.conf settings applied dynamically per test:

1. corelist-workers <list_of_cores> - list of logical cores to run VPP
   worker data plane threads. Depends on HyperThreading and core per
   test configuration.
2. num-rx-queues <value> - depends on a number of VPP threads and NIC
   interfaces.
3. no-multi-seg - disables multi-segment buffers in DPDK, improves
   packet throughput, but disables Jumbo MTU support. Disabled for all
   tests apart from the ones that require Jumbo 9000B frame support.
4. UIO driver - depends on topology file definition.
5. QAT VFs - depends on NRThreads, each thread = 1QAT VFs.
