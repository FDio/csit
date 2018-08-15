Test Scenarios Overview
=======================

FD.io CSIT report includes multiple test scenarios of a number of VPP
centric applications, topologies and use cases. In addition it also
covers baseline tests of DPDK sample applications. Tests are executed
executed in physical (performance tests) and virtual environments
(functional tests).

Following list provides a brief overview of test scenarios covered in
this report:

#. **VPP Performance**: VPP performance tests are executed in physical
   FD.io testbeds, focusing on VPP network data plane performance in
   NIC-to-NIC switching topologies. Tested across Intel Xeon Haswell
   and Skylake servers, range of NICs (10GE, 25GE, 40GE) and multi-
   thread/multi-core configurations. VPP application runs in bare-metal
   host user-mode handling NICs. TRex is used as a traffic generator.

#. **VPP Vhostuser Performance with KVM VMs**: VPP VM service switching
   performance tests using vhostuser virtual interface for
   interconnecting multiple Testpmd-in-VM instances. VPP vswitch
   instance runs in bare-metal user-mode handling NICs and connecting
   over vhost-user interfaces to VM instances each running DPDK
   Testpmd with virtio virtual interfaces. Similarly to VPP
   Performance, tests are run across a range of configurations. TRex
   is used as a traffic generator.

#. **VPP Memif Performance with LXC and Docker Containers**: VPP
   Container service switching performance tests using memif virtual
   interface for interconnecting multiple VPP-in-container instances.
   VPP vswitch instance runs in bare-metal user-mode handling NICs and
   connecting over memif (Slave side) interfaces to more instances of
   VPP running in LXC or in Docker Containers, both with memif
   interfaces (Master side). Similarly to VPP Performance, tests are
   run across a range of configurations. TRex is used as a traffic
   generator.

#. **K8s Container/Pod Topologies Performance**: VPP container
   performance tests using memif for interconnecting VPP-in-
   Container/Pod instances orchestrated by K8s integrated with `Ligato
   <https://github.com/ligato>`_ for container networking. TRex is
   used as a traffic generator.

#. **DPDK Performance**: VPP uses DPDK to drive the NICs and physical
   interfaces. DPDK performance tests are used as a baseline to
   profile performance of the DPDK sub-system. Two DPDK applications
   are tested: Testpmd and L3fwd. DPDK tests are executed in the same
   testing environment as VPP tests. DPDK Testpmd and L3fwd
   applications run in host user-mode. TRex is used as a traffic
   generator.

#. **VPP Functional**: VPP functional tests are executed in virtual
   FD.io testbeds, focusing on VPP packet processing functionality,
   including both network data plane and in-line control plane. Tests
   cover vNIC-to-vNIC vNIC-to-nestedVM-to-vNIC forwarding topologies.
   Scapy is used as a traffic generator.

#. **Honeycomb Functional**: Honeycomb functional tests are executed in
   virtual FD.io testbeds, focusing on Honeycomb management and
   programming functionality of VPP. Tests cover a range of CRUD
   operations executed against VPP.

#. **NSH_SFC Functional**: NSH_SFC functional tests are executed in
   virtual FD.io testbeds focusing on VPP nsh-plugin data plane
   functionality. Scapy is used as a traffic generator.

#. **DMM Functional**: DMM functional tests are executed in virtual
   FD.io testbeds demonstrating a single server (DUT1) and single
   client (DUT2) scenario using DMM framework and Linux kernel TCP/IP
   stack.

All CSIT test results listed in this report are sourced and auto-
generated from :abbr:`RF (Robot Framework)` :file:`output.xml` files
resulting from :abbr:`LF (Linux Foundation)` FD.io Jenkins jobs executed
against |vpp-release| release artifacts. References are provided to the
original FD.io Jenkins job results. Additional references are provided
to the :abbr:`RF (Robot Framework)` result files that got archived in
FD.io Nexus online storage system.

FD.io CSIT system is developed using two main coding platforms: :abbr:`RF (Robot
Framework)` and Python2.7. |csit-release| source code for the executed test
suites is available in CSIT branch |release| in the directory
:file:`./tests/<name_of_the_test_suite>`. A local copy of CSIT source code
can be obtained by cloning CSIT git repository - :command:`git clone
https://gerrit.fd.io/r/csit`.
