.. _per_thread_resources_methodology:

Per Thread Resources
--------------------

CSIT test framework is managing mapping of the following resources per
thread:

#. Cores, physical cores (pcores) allocated as pairs of sibling logical cores
   (lcores) if server in HyperThreading/SMT mode, or as single lcores
   if server not in HyperThreading/SMT mode. Note that if server's
   processors are running in HyperThreading/SMT mode sibling lcores are
   always used.
#. Receive Queues (RxQ), packet receive queues allocated on each
   physical and logical interface tested.
#. Transmit Queues(TxQ), packet transmit queues allocated on each
   physical and logical interface tested.

Approach to mapping per thread resources depends on the application/DUT
tested (VPP or DPDK apps) and associated thread types, as follows:

#. Data-plane workers, used for data-plane packet processing, when no
   feature workers present.

   - Cores: data-plane workers are typically tested in 1, 2 and 4 pcore
     configurations, running on single lcore per pcore or on sibling
     lcores per pcore. Result is a set of {T}t{C}c thread-core
     configurations, where{T} stands for a total number of threads
     (lcores), and {C} for a total number of pcores. Tested
     configurations are encoded in CSIT test case names,
     e.g. "1c", "2c", "4c", and test tags "2T1C"(or "1T1C"), "4T2C"
     (or "2T2C"), "8T4C" (or "4T4C").
   - Interface Receive Queues (RxQ): as of CSIT-2106 release, number of
     RxQs used on each physical or virtual interface is equal to the
     number of data-plane workers. In other words each worker has a
     dedicated RxQ on each interface tested. This ensures packet
     processing load to be equal for each worker, subject to RSS flow
     load balancing efficacy. Note: Before CSIT-2106 total number of
     RxQs across all interfaces of specific type was equal to the
     number of data-plane workers.
   - Interface Transmit Queues (TxQ): number of TxQs used on each
     physical or virtual interface is equal to the number of data-plane
     workers. In other words each worker has a dedicated TxQ on each
     interface tested.
   - Applies to VPP and DPDK Testpmd and L3Fwd.

#. Data-plane and feature workers (e.g. IPsec async crypto workers), the
   latter dedicated to specific feature processing.

   - Cores: data-plane and feature workers are tested in 2, 3 and 4
     pcore configurations, running on single lcore per pcore or on
     sibling lcores per pcore. This results in a two sets of
     thread-core combinations separated by "-", {T}t{C}c-{T}t{C}c, with
     the leading set denoting total number of threads (lcores) and
     pcores used for data-plane workers, and the trailing set denoting
     total number of lcores and pcores used for feature workers.
     Accordingly, tested configurations are encoded in CSIT test case
     names, e.g. "1c-1c", "1c-2c", "1c-3c", and test tags "2T1C_2T1C"
     (or "1T1C_1T1C"), "2T1C_4T2C"(or "1T1C_2T2C"), "2T1C_6T3C"
     (or "1T1C_3T3C").
   - RxQ and TxQ: no RxQs and no TxQs are used by feature workers.
   - Applies to VPP only.

#. Management/main worker, control plane and management.

   - Cores: single lcore.
   - RxQ: not used (VPP default behaviour).
   - TxQ: single TxQ per interface, allocated but not used
     (VPP default behaviour).
   - Applies to VPP only.

VPP Thread Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

Mapping of cores and RxQs to VPP data-plane worker threads is done in
the VPP startup.conf during test suite setup:

#. `corelist-workers <list_of_cores>`: List of logical cores to run VPP
   data-plane workers and feature workers. The actual lcores'
   allocations depends on HyperThreading/SMT server configuration and
   per test core configuration.

   - For tests without feature workers, by default, all CPU cores
     configured in startup.conf are used for data-plane workers.
   - For tests with feature workers, CSIT code distributes lcores across
     data-plane and feature workers.

#. `num-rx-queues <value>`: Number of Rx queues used per interface.

Mapping of TxQs to VPP data-plane worker threads uses the default VPP
setting of one TxQ per interface per data-plane worker.

DPDK Thread Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

Mapping of cores and RxQs to DPDK Testpmd/L3Fwd data-plane worker
threads is done in the startup CLI:

#. `-l <list_of_cores>` - List of logical cores to run DPDK
   application.
#. `nb-cores=<N>` - Number of forwarding cores.
#. `rxq=<N>` - Number of Rx queues used per interface.
