General Notes
=============

All CSIT test results listed in this report are sourced and auto-generated
from :file:`output.xml` :abbr:`RF (Robot Framework)` files resulting from
:abbr:`LF (Linux Foundation)` FD.io Jenkins jobs execution against |vpp-release|
release artifacts. References are provided to the original :abbr:`LF (Linux
Foundation)` FD.io Jenkins job results. However, as :abbr:`LF (Linux
Foundation)` FD.io Jenkins infrastructure does not automatically archive all jobs
(history record is provided for the last 30 days or 40 jobs only), additional
references are provided to the :abbr:`RF (Robot Framework)` result files that
got archived in FD.io nexus online storage system.

FD.io CSIT project currently covers multiple FD.io system and sub-system
testing areas and this is reflected in this report, where each testing area
is listed separately, as follows:

#. **VPP Performance Tests** - VPP performance tests are executed in physical
   FD.io testbeds, focusing on VPP network data plane performance at this stage,
   both for Phy-to-Phy (NIC-to-NIC) and Phy-to-VM-to-Phy (NIC-to-VM-to-NIC)
   forwarding topologies. Tested across a range of NICs, 10GE and 40GE
   interfaces, range of multi-thread and multi-core configurations. VPP
   application runs in host user-mode. TRex is used as a traffic generator.

#. **Container memif connections** -  VPP memif virtual interface (shared memory
   interface) tests to interconnect VPP instances. VPP vswitch instance runs in
   bare-metal user-mode handling Intel x520 NIC 10GbE interfaces and connecting
   over memif (Master side) virtual interfaces to more instances of VPP running
   in LXC or in Docker Containers, both with memif virtual interfaces (Slave
   side). Tested across a range of NICs, 10GE and 40GE interfaces, range of
   multi-thread and multi-core configurations. VPP application runs in host
   user-mode. TRex is used as a traffic generator.

#. **Container Orchestrated Performance Tests** - CSIT |release| introduced new
   tests of Container topologies connected over the memif virtual interface
   (shared memory interface). For these tests VPP vswitch instance runs in a
   Docker Container handling Intel x520 NIC 10GbE interfaces and connecting over
   memif (Master side) virtual interfaces to more instances of VPP running in
   Docker Containers with memif virtual interfaces (Slave side). Tested across a
   range of multi-thread and multi-core configurations. VPP application runs in
   host user-mode. TRex is used as a traffic generator.

#. **DPDK Performance Tests** - VPP is using DPDK code to control and drive
   the NICs and physical interfaces. Testpmd tests are used as a baseline to
   profile the DPDK sub-system of VPP. DPDK performance tests executed in
   physical FD.io testbeds, focusing on Testpmd/L3FWD data plane performance for
   Phy-to-Phy (NIC-to-NIC). Tests cover a range of NICs, 10GE and 40GE
   interfaces, range of multi-thread and multi-core configurations.
   Testpmd/L3FWD application runs in host user-mode. TRex is used as a traffic
   generator.

#. **VPP Functional Tests** - VPP functional tests are executed in virtual
   FD.io testbeds focusing on VPP packet processing functionality, including
   network data plane and in -line control plane. Tests cover vNIC-to-vNIC
   vNIC-to-VM-to-vNIC forwarding topologies. Scapy is used as a traffic
   generator.

#. **Honeycomb Functional Tests** - Honeycomb functional tests are executed in
   virtual FD.io testbeds, focusing on Honeycomb management and programming
   functionality of VPP. Tests cover a range of CRUD operations executed
   against VPP.

#. **Honeycomb Performance Tests** - Honeycomb performance tests are executed in
   physical FD.io testbeds, focusing on the performance of Honeycomb management
   and programming functionality of VPP. Tests cover a range of CRUD operations
   executed against VPP.

#. **NSH_SFC Functional Tests** - NSH_SFC functional tests are executed in
   virtual FD.io testbeds focusing on NSH_SFC of VPP. Tests cover a range of
   CRUD operations executed against VPP.

In addition to above, CSIT |release| report does also include VPP unit test
results. VPP unit tests are developed within the FD.io VPP project and as they
complement CSIT system functional tests, they are provided mainly as a reference
and to provide a more complete view of automated testing executed against
|vpp-release|.

FD.io CSIT system is developed using two main coding platforms :abbr:`RF (Robot
Framework)` and Python. CSIT |release| source code for the executed test
suites is available in CSIT branch |release| in the directory
:file:`./tests/<name_of_the_test_suite>`. A local copy of CSIT source code
can be obtained by cloning CSIT git repository - :command:`git clone
https://gerrit.fd.io/r/csit`. The CSIT testing virtual environment can be run
on a local computer workstation (laptop, server) using Vagrant by following
the instructions in `CSIT tutorials
<https://wiki.fd.io/view/CSIT#Tutorials>`_.
