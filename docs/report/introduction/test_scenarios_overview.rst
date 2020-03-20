Test Scenarios
==============

The FD.io |csit-release| report includes multiple test scenarios of VPP-centric
applications, topologies and use cases. In addition, it also
covers baseline tests of DPDK sample applications. Performance tests are
executed in physical testbeds, whereas functional tests run in virtual
environments.

Brief overview of test scenarios covered in this report:

#. **VPP Performance**: VPP performance tests are executed in physical
   FD.io testbeds, focusing on VPP network data plane performance in
   NIC-to-NIC switching topologies. Tested across Intel Xeon Haswell
   and Skylake servers, ARM, Denverton, a range of NICs (10GE, 25GE, 40GE) and
   multi-thread/multi-core configurations. VPP application runs in bare-metal
   host user-mode handling NICs. TRex is used as traffic generator.

#. **VPP Vhostuser Performance with KVM VMs**: VPP VM service switching
   performance tests using vhostuser virtual interface for
   interconnecting multiple NF-in-VM instances. A VPP vswitch
   instance runs in bare-metal user-mode, handling NIC interfaces, and connects
   over vhost-user interfaces to VM instances, each running VPP with virtio
   virtual interfaces. Similarly to VPP Performance, tests are run across a
   range of configurations. TRex is used as traffic generator.

#. **VPP Memif Performance with LXC and Docker Containers**: VPP
   Container service switching performance tests using memif virtual
   interface for interconnecting multiple VPP-in-container instances.
   A VPP vswitch instance runs in bare-metal user-mode, handling NIC interfaces
   and connects over memif (Slave side) interfaces to other instances of
   VPP. The latter run either in LXC or in Docker Containers, both with memif
   (Master side) interfaces. Similarly to VPP Performance, tests are
   run across a range of configurations. TRex is used as traffic
   generator.

#. **DPDK Performance**: VPP uses DPDK to drive the NICs and physical
   interfaces. DPDK performance tests are used as a baseline to
   profile performance of the DPDK sub-system. Two DPDK applications
   are tested: Testpmd and L3fwd. DPDK tests are executed in the same
   testing environment as VPP tests. DPDK Testpmd and L3fwd
   applications run in host user-mode. TRex is used as traffic
   generator.

#. **VPP Functional**: VPP functional tests are executed in virtual
   FD.io testbeds, focusing on VPP packet processing functionality,
   including both network data plane and in-line control plane. Tests
   cover vNIC-to-vNIC and vNIC-to-nestedVM-to-vNIC forwarding topologies.
   Scapy is used as traffic generator.

All CSIT test data included in this report is auto-
generated from :abbr:`RF (Robot Framework)` :file:`output.xml` files
produced by :abbr:`LF (Linux Foundation)` FD.io Jenkins jobs executed
against |vpp-release| artifacts. References are provided to the
original FD.io Jenkins job results and all archived source files.

The FD.io CSIT system is developed using two main coding platforms: :abbr:`RF
(Robot Framework)` and Python3.6. |csit-release| source code for the executed
test suites is available in CSIT branch |release| in the directory
:file:`./tests/<name_of_the_test_suite>`. A local copy of CSIT source code
can be obtained by cloning CSIT git repository - :command:`git clone
https://gerrit.fd.io/r/csit`.
