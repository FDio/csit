General Notes
=============

All CSIT test results listed in this report are sourced and auto-
generated from :abbr:`RF (Robot Framework)` :file:`output.xml` files
resulting from :abbr:`LF (Linux Foundation)` FD.io Jenkins jobs executed
against |vpp-release| release artifacts. References are provided to the
original FD.io Jenkins job results. Additional references are provided
to the :abbr:`RF (Robot Framework)` result files that got archived in
FD.io Nexus online storage system.

FD.io CSIT project covers multiple FD.io system and sub-system testing
areas with this report listing each of them separately, as follows:

#. **VPP Performance**: VPP performance tests are executed in physical
   FD.io testbeds, focusing on VPP network data plane performance,
   both for Phy-to-Phy (NIC-to-NIC) and Phy-to-VM-to-Phy (NIC-to-VM-
   to-NIC) data plane topologies. Tested across a range of NICs, 10GE,
   25GE and 40GE interfaces, range of multi-thread and multi-core
   configurations. VPP application runs in host user-mode. TRex is
   used as a traffic generator.

#. **VPP memif Performance with LXC and Docker Containers**: VPP memif virtual interface performance tests with interconnected multiple VPP instances running in containers. VPP vswitch instance runs in bare-metal user-mode handling Intel x520 NIC 10GbE, Intel x710 NIC 10GbE, Intel xl710 NIC 40GbE interfaces and connecting over memif (Slave side) virtual interfaces to more instances of VPP running in LXC or in Docker Containers, both with memif virtual interfaces (Master side). Tested across a range of multi-thread and multi-core configurations. TRex is used as a traffic generator.

#. **Container Topologies Orchestrated by K8s - Performance**: CSIT Container topologies connected over the memif virtual interface (shared memory interface). For these tests VPP vswitch instance runs in a Docker Container handling Intel x520 NIC 10GbE, Intel x710 NIC 10GbE interfaces and connecting over memif virtual interfaces to more instances of VPP running in Docker Containers with memif virtual interfaces. All containers are orchestrated by Kubernetes, with `Ligato <https://github.com/ligato>`_ for container networking. TRex is used as a traffic generator.

#. **DPDK Performance**: VPP is using DPDK code to control and drive the NICs and physical interfaces. Tests are used as a baseline to profile performance of the DPDK sub-system. DPDK tests are executed in physical FD.io testbeds, focusing on Testpmd/L3FWD data plane performance for Phy-to-Phy (NIC-to-NIC). Tested across a range of NICs, 10GE, 25GE and 40GE interfaces, range of multi-thread and multi-core configurations. Testpmd/L3FWD application runs in host user-mode. TRex is used as a traffic generator.

#. **VPP Functional**: VPP functional tests are executed in virtual FD.io testbeds focusing on VPP packet processing functionality, including network data plane and in -line control plane. Tests cover vNIC-to-vNIC vNIC-to-VM-to-vNIC forwarding topologies. Scapy is used as a traffic generator.

#. **Honeycomb Functional**: Honeycomb functional tests are executed in virtual FD.io testbeds, focusing on Honeycomb management and programming functionality of VPP. Tests cover a range of CRUD operations executed against VPP.

#. **NSH_SFC Functional**: NSH_SFC functional tests are executed in virtual FD.io testbeds focusing on NSH_SFC of VPP. Tests cover a range of CRUD operations executed against VPP.

#. **DMM Functional**: DMM functional tests are executed in virtual FD.io testbeds demonstrates single server[DUT1] and single client[DUT2] scenario using DMM framework and kernel tcp/ip stack.

FD.io CSIT system is developed using two main coding platforms :abbr:`RF (Robot
Framework)` and Python2.7. |csit-release| source code for the executed test
suites is available in CSIT branch |release| in the directory
:file:`./tests/<name_of_the_test_suite>`. A local copy of CSIT source code
can be obtained by cloning CSIT git repository - :command:`git clone
https://gerrit.fd.io/r/csit`.
