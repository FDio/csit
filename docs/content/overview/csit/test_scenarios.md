---
title: "Test Scenarios"
weight: 2
---

# Test Scenarios

FD.io CSIT Dashboard includes multiple test scenarios of VPP
centric applications, topologies and use cases. In addition it also
covers baseline tests of DPDK sample applications. Tests are executed in
physical (performance tests) and virtual environments (functional
tests).

Brief overview of test scenarios covered in this documentation:

1. **VPP Performance**: VPP performance tests are executed in physical
   FD.io testbeds, focusing on VPP network data plane performance in
   NIC-to-NIC switching topologies. VPP application runs in
   bare-metal host user-mode handling NICs. TRex is used as a traffic generator.
2. **VPP Vhostuser Performance with KVM VMs**: VPP VM service switching
   performance tests using vhostuser virtual interface for
   interconnecting multiple NF-in-VM instances. VPP vswitch
   instance runs in bare-metal user-mode handling NICs and connecting
   over vhost-user interfaces to VM instances each running VPP with virtio
   virtual interfaces. Similarly to VPP Performance, tests are run across a
   range of configurations. TRex is used as a traffic generator.
3. **VPP Memif Performance with LXC and Docker Containers**: VPP
   Container service switching performance tests using memif virtual
   interface for interconnecting multiple VPP-in-container instances.
   VPP vswitch instance runs in bare-metal user-mode handling NICs and
   connecting over memif (Slave side) interfaces to more instances of
   VPP running in LXC or in Docker Containers, both with memif
   interfaces (Master side). Similarly to VPP Performance, tests are
   run across a range of configurations. TRex is used as a traffic
   generator.
4. **DPDK Performance**: VPP uses DPDK to drive the NICs and physical
   interfaces. DPDK performance tests are used as a baseline to
   profile performance of the DPDK sub-system. Two DPDK applications
   are tested: Testpmd and L3fwd. DPDK tests are executed in the same
   testing environment as VPP tests. DPDK Testpmd and L3fwd
   applications run in host user-mode. TRex is used as a traffic
   generator.
5. **T-Rex Performance**: T-Rex perfomance tests are executed in physical
   FD.io testbeds, focusing on T-Rex data plane performance in NIC-to-NIC
   loopback topologies.
6. **VPP Functional**: VPP functional tests are executed in virtual
   FD.io testbeds, focusing on VPP packet processing functionality,
   including both network data plane and in-line control plane. Tests
   cover vNIC-to-vNIC vNIC-to-nestedVM-to-vNIC forwarding topologies.
   Scapy is used as a traffic generator.

All CSIT test data included in this report is auto-generated from Robot
Framework json output files produced by Linux Foundation FD.io Jenkins jobs
executed against {{< release_vpp >}} artifacts.

FD.io CSIT system is developed using two main coding platforms: Robot
Framework and Python. {{< release_csit >}} source code for the executed test
suites is available in corresponding CSIT branch in the directory
`./tests/<name_of_the_test_suite>`. A local copy of CSIT source code
can be obtained by cloning CSIT git repository - `git clone
https://gerrit.fd.io/r/csit`.
