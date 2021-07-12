.. _per_thread_resources_methodology:

Per Thread Resources
--------------------

CSIT test framework is managing mapping of the following resources per
thread:

#. Cores, physical cores allocated as pairs of sibling logical cores
   (lcores) if server in HyperThreading/SMT mode, or as single lcores
   if server not in HyperThreading/SMT mode.
#. Receive Queues (RxQ), packet receive queues allocated on each
   physical and logical interface tested.
#. Transmit Queues(TxQ), packet transmit queues allocated on each
   physical and logical interface tested.

Approach to mapping per thread resources depends on the application/DUT
tested (VPP or DPDK apps) and associated thread types, as follows:

#. Data plane workers, used for data plane packet processing.

   - Cores, data plane workers are tested in 1, 2 and 4 physical core
     configurations in poll-mode, with workers running on either single
     hyper-thread or sibling hyper-threads per physical core. Result is
     a set of {T}t{C}c thread-core configurations, where{T} stands for
     a number of threads, and {C} for a number of physical cores, with
     tested configurations encoded in CSIT test case names,
     e.g. "1t1c", "2t2c", "4t4c" for not Hyper-Thread setup,
     and "2t1c", "4t2c", "8t4c" for Hyper-Threaded one.
   - Interface Receive Queues (RxQ), in CSIT rls2106 number of RxQs used
     on each physical or virtual interface is equal to the number of
     data plane workers. In other words each worker has a dedicated RxQ
     on each interface tested. This ensures packet processing load to
     be equal for each worker, subject to RSS flow load balancing
     efficacy.
   - Interface Transmit Queues (TxQ), number of TxQs used on each
     physical or virtual interface is equal to the number of data plane
     workers. In other words each worker has a dedicated TxQ on each
     interface tested.
   - Applies to VPP and DPDK Testpmd and L3Fwd.

#. Feature workers (e.g. IPsec async crypto workers), dedicated to
   specific feature processing.

   - Cores, feature workers are tested in 1, 2 and 4 physical core
     configurations in poll-mode, with workers running on either single
     hyper-thread or sibling hyper-threads per physical core. For tests
     with feature workers a total number of cores used for data plane
     workers and features workers is encoded in CSIT test case names,
     e.g. "1t1c", "2t2c", "4t4c" for not Hyper-Thread setup,
     and "2t1c", "4t2c", "8t4c" for Hyper-Threaded one.
   - RxQ and TxQ, no RxQs and no TxQs are used by feature workers.
   - Applies to VPP only.

#. Management/main workers, control plane and management.

   - Cores, single lcore not in interrupt mode.
   - RxQ, single RxQ per interface.
   - TxQ, single TxQ per interface.
   - Applies to VPP only.

VPP Thread Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

Mapping of cores and RxQs to VPP data plane worker threads is done in
the VPP startup.conf during test suite setup:

#. `corelist-workers <list_of_cores>` - list of logical cores to run VPP
   data plane workers and feature workers. The actual lcores'
   allocations depends on HyperThreading/SMT server configuration and
   per test core configuration.

   - For tests without feature workers, by default, all CPU cores
     configured in startup.conf are used for data plane workers. 
   - For tests with feature workers, CSIT Core Virtual Context code
     (TODO add pointer) distributes lcores across data plane and
     feature workers. 

#. `num-rx-queues <value>` - Number of Rx queues used per interface.

Mapping of TxQs to VPP data plane worker threads follows the default
setting of one TxQ per interface per data plane worker.

DPDK Thread Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

Mapping of cores and RxQs to DPDK Testpmd/L3Fwd data plane worker
threads is done in the startup CLI:

#. `nb-cores=N` - Number of forwarding cores, where 1 <= N <= "number of
   cores". Depends on HyperThreading and core per test configuration.
#. `rxq=N` - Number of RX queues per port to N.

