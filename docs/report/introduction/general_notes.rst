General Notes
=============

All CSIT test results listed in this report are sourced and auto-generated
from output.xml Robot Framework (RF) files resulting from LF FD.io Jenkins
jobs execution against VPP-17.01 release artifacts. References are provided
to the original LF FD.io Jenkins job results. However, as LF FD.io Jenkins
infrastructure does not automatically archive all jobs (history record is
provided for the last 30 days or 40 jobs only), additional references are
provided to the RF result files that got archived in FD.io nexus online
storage system.

FD.io CSIT project currently covers multiple FD.io system and sub-system
testing areas and this is  reflected in this report, where each testing area
is listed separately, as follows

#. **VPP Performance Tests** - VPP performance are tests executed in physical
    FD.io testbeds,  focusing on VPP network data plane performance at this stage,
    both for Phy-to-Phy (NIC-to-NIC) and Phy-to-VM-to-Phy (NIC-to-VM-to-NIC)
    forwarding topologies. Tested across a range of NICs, 10GE and 40GE
    interfaces, range of multi-thread and multi-core configurations. VPP
    application runs in host user- mode. TRex is used as a traffic generator.

#. **Testpmd Performance Tests** - VPP is using DPDK code to control and drive
    the NICs and physical interfaces. Testpmd tests are used as a baseline to
    profile the DPDK sub-system of VPP. Testpmd performance tests executed in
    physical FD.io testbeds, focusing on Testpmd data plane performance for Phy-
    to-Phy (NIC-to-NIC). Tests cover a range of NICs, 10GE and 40GE interfaces,
    range of multi-thread and multi-core configurations. Testpmd application runs
    in host user-mode. TRex is used as a traffic generator.

#. **VPP Functional Tests** - VPP functional tests are executed in virtual
    FD.io testbeds focusing on VPP packet processing functionality, including
    network data plane and in -line control plane. Tests cover vNIC-to-vNIC
    vNIC-to-VM-to-vNIC forwarding topologies. Scapy is used as a traffic
    generator.

#. **HoneyComb Functional Tests** - HoneyComb functional tests are executed in
    virtual FD.io testbeds focusing on HoneyComb management and programming
    functionality of VPP. Tests cover a range of CRUD operations executed
    against VPP.

CSIT |release| report does also include VPP unit test results. These tests
have been developed within the FD.io VPP project, and not in CSIT, but they do
complement tests done by CSIT. They are provided mainly as a reference, to
give the reader a more complete view of automated testing executed against
VPP-17.01 release.

FD.io CSIT system is developed using two main coding platforms: Robot
Framework (RF) and Python. CSIT |release| source code for the executed test
suites is available in CSIT branch |release| in the directory
"./tests/<name_of_the_test_suite>". A local copy of CSIT source code can be
obtained by cloning CSIT git repository - "git clone
https://gerrit.fd.io/r/csit". The CSIT testing virtual environment can be run
on a local computer workstation (laptop, server) using Vagrant by following
the instructions in `CSIT tutorials
<https://wiki.fd.io/view/CSIT#Tutorials>`_.