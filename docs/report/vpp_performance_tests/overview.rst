Overview
========

.. _tested_physical_topologies:

Tested Physical Topologies
--------------------------

CSIT VPP performance tests are executed on physical baremetal servers hosted by
:abbr:`LF (Linux Foundation)` FD.io project. Testbed physical topology is shown
in the figure below.::

        +------------------------+           +------------------------+
        |                        |           |                        |
        |  +------------------+  |           |  +------------------+  |
        |  |                  |  |           |  |                  |  |
        |  |                  <----------------->                  |  |
        |  |       DUT1       |  |           |  |       DUT2       |  |
        |  +--^---------------+  |           |  +---------------^--+  |
        |     |                  |           |                  |     |
        |     |            SUT1  |           |  SUT2            |     |
        +------------------------+           +------------------^-----+
              |                                                 |
              |                                                 |
              |                  +-----------+                  |
              |                  |           |                  |
              +------------------>    TG     <------------------+
                                 |           |
                                 +-----------+

SUT1 and SUT2 are two System Under Test servers (Cisco UCS C240, each with two
Intel XEON CPUs), TG is a Traffic Generator (TG, another Cisco UCS C240, with
two Intel XEON CPUs). SUTs run VPP SW application in Linux user-mode as a
Device Under Test (DUT). TG runs TRex SW application as a packet Traffic
Generator. Physical connectivity between SUTs and to TG is provided using
different NIC models that need to be tested for performance. Currently
installed and tested NIC models include:

#. 2port10GE X520-DA2 Intel.
#. 2port10GE X710 Intel.
#. 2port10GE VIC1227 Cisco.
#. 2port40GE VIC1385 Cisco.
#. 2port40GE XL710 Intel.

From SUT and DUT perspective, all performance tests involve forwarding packets
between two physical Ethernet ports (10GE or 40GE). Due to the number of
listed NIC models tested and available PCI slot capacity in SUT servers, in
all of the above cases both physical ports are located on the same NIC. In
some test cases this results in measured packet throughput being limited not
by VPP DUT but by either the physical interface or the NIC capacity.

Going forward CSIT project will be looking to add more hardware into FD.io
performance labs to address larger scale multi-interface and multi-NIC
performance testing scenarios.

For service chain topology test cases that require DUT (VPP) to communicate with
VirtualMachines (VMs) or with Linux/Docker Containers (Ctrs) over
vhost-user/memif interfaces, N of VM/Ctr instances are created on SUT1
and SUT2. Three types of service chain topologies are tested in CSIT |release|:

#. "Parallel" topology with packets flowing from NIC via DUT (VPP) to
   VM/Container and back to VPP and NIC;

#. "Chained" topology (a.k.a. "Snake") with packets flowing via DUT (VPP) to
   VM/Container, back to DUT, then to the next VM/Container, back to DUT and
   so on until the last VM/Container in a chain, then back to DUT and NIC;

#. "Horizontal" topology with packets flowing via DUT (VPP) to Container,
   then via "horizontal" memif to the next Container, and so on until the
   last Container, then back to DUT and NIC. "Horizontal" topology is not
   supported for VMs;

For each of the above topologies, DUT (VPP) is tested in a range of L2
or IPv4/IPv6 configurations depending on the test suite. A sample DUT
"Chained" service topology with N of VM/Ctr instances is shown in the
figure below. Packet flow thru the DUTs and VMs/Ctrs is marked with
``***``::

        +-------------------------+           +-------------------------+
        | +---------+ +---------+ |           | +---------+ +---------+ |
        | |VM/Ctr[1]| |VM/Ctr[N]| |           | |VM/Ctr[1]| |VM/Ctr[N]| |
        | |  *****  | |  *****  | |           | |  *****  | |  *****  | |
        | +--^---^--+ +--^---^--+ |           | +--^---^--+ +--^---^--+ |
        |   *|   |*     *|   |*   |           |   *|   |*     *|   |*   |
        | +--v---v-------v---v--+ |           | +--v---v-------v---v--+ |
        | |  *   *       *   *  |*|***********|*|  *   *       *   *  | |
        | |  *   *********   ***<-|-----------|->***   *********   *  | |
        | |  *    DUT1          | |           | |       DUT2       *  | |
        | +--^------------------+ |           | +------------------^--+ |
        |   *|                    |           |                    |*   |
        |   *|            SUT1    |           |  SUT2              |*   |
        +-------------------------+           +-------------------------+
            *|                                                     |*
            *|                                                     |*
            *|                    +-----------+                    |*
            *|                    |           |                    |*
            *+-------------------->    TG     <--------------------+*
            **********************|           |**********************
                                  +-----------+

In above "Chained" topology, packets are switched by DUT multiple times:
twice for a single VM/Ctr, three times for two VMs/Ctrs, N+1 times for N
VMs/Ctrs. Hence the external throughput rates measured by TG and listed
in this report must be multiplied by (N+1) to represent the actual DUT
aggregate packet forwarding rate.

For a "Parallel" and "Horizontal" service topologies packets are always
switched by DUT twice per service chain.

Note that reported DUT (VPP) performance results are specific to the SUTs
tested. Current :abbr:`LF (Linux Foundation)` FD.io SUTs are based on Intel
XEON E5-2699v3 2.3GHz CPUs. SUTs with other CPUs are likely to yield different
results. A good rule of thumb, that can be applied to estimate VPP packet
thoughput for Phy-to-Phy (NIC-to-NIC, PCI-to-PCI) topology, is to expect
the forwarding performance to be proportional to CPU core frequency,
assuming CPU is the only limiting factor and all other SUT parameters
equivalent to FD.io CSIT environment. The same rule of thumb can be also
applied for Phy-to-VM/Ctr-to-Phy (NIC-to-VM/Ctr-to-NIC) topology, but due to
much higher dependency on intensive memory operations and sensitivity to Linux
kernel scheduler settings and behaviour, this estimation may not always yield
good enough accuracy.

For detailed FD.io CSIT testbed specification and topology, as well as
configuration and setup of SUTs and DUTs testbeds please refer to
:ref:`test_environment`.

Similar SUT compute node can be arrived to in a standalone VPP setup by using a
`vpp-config configuration tool
<https://wiki.fd.io/view/VPP/Configuration_Tool>`_ developed within the
VPP project using CSIT recommended settings and scripts.

Performance Tests Coverage
--------------------------

Performance tests are split into two main categories:

- Throughput discovery - discovery of packet forwarding rate using binary search
  in accordance to :rfc:`2544`.

  - NDR - discovery of Non Drop Rate packet throughput, at zero packet loss;
    followed by one-way packet latency measurements at 10%, 50% and 100% of
    discovered NDR throughput.
  - PDR - discovery of Partial Drop Rate, with specified non-zero packet loss
    currently set to 0.5%; followed by one-way packet latency measurements at
    100% of discovered PDR throughput.

CSIT |release| includes following performance test suites, listed per NIC type:

- 2port10GE X520-DA2 Intel

  - **L2XC** - L2 Cross-Connect switched-forwarding of untagged, dot1q, dot1ad
    VLAN tagged Ethernet frames.
  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
    with MAC learning; disabled MAC learning i.e. static MAC tests to be added.
  - **L2BD Scale** - L2 Bridge-Domain switched-forwarding of untagged Ethernet
    frames with MAC learning; disabled MAC learning i.e. static MAC tests to be
    added with 20k, 200k and 2M FIB entries.
  - **IPv4** - IPv4 routed-forwarding.
  - **IPv6** - IPv6 routed-forwarding.
  - **IPv4 Scale** - IPv4 routed-forwarding with 20k, 200k and 2M FIB entries.
  - **IPv6 Scale** - IPv6 routed-forwarding with 20k, 200k and 2M FIB entries.
  - **VMs with vhost-user** - virtual topologies with 1 VM and service chains
    of 2 VMs using vhost-user interfaces, with VPP forwarding modes incl. L2
    Cross-Connect, L2 Bridge-Domain, VXLAN with L2BD, IPv4 routed-forwarding.
  - **COP** - IPv4 and IPv6 routed-forwarding with COP address security.
  - **ACL** - L2 Bridge-Domain switched-forwarding and IPv4 and IPv6 routed-
    forwarding with iACL and oACL IP address, MAC address and L4 port security.
  - **LISP** - LISP overlay tunneling for IPv4-over-IPv4, IPv6-over-IPv4,
    IPv6-over-IPv6, IPv4-over-IPv6 in IPv4 and IPv6 routed-forwarding modes.
  - **VXLAN** - VXLAN overlay tunnelling integration with L2XC and L2BD.
  - **QoS Policer** - ingress packet rate measuring, marking and limiting
    (IPv4).
  - **NAT** - (Source) Network Address Translation tests with varying
    number of users and ports per user.
  - **Container memif connections** - VPP memif virtual interface tests to
    interconnect VPP instances with L2XC and L2BD.
  - **Container K8s Orchestrated Topologies** - Container topologies connected
    over the memif virtual interface.
  - **SRv6** - Segment Routing IPv6 tests.

- 2port40GE XL710 Intel

  - **L2XC** - L2 Cross-Connect switched-forwarding of untagged Ethernet frames.
  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
    with MAC learning.
  - **IPv4** - IPv4 routed-forwarding.
  - **IPv6** - IPv6 routed-forwarding.
  - **VMs with vhost-user** - virtual topologies with 1 VM and service chains
    of 2 VMs using vhost-user interfaces, with VPP forwarding modes incl. L2
    Cross-Connect, L2 Bridge-Domain, VXLAN with L2BD, IPv4 routed-forwarding.
  - **IPSecSW** - IPSec encryption with AES-GCM, CBC-SHA1 ciphers, in
    combination with IPv4 routed-forwarding.
  - **IPSecHW** - IPSec encryption with AES-GCM, CBC-SHA1 ciphers, in
    combination with IPv4 routed-forwarding. Intel QAT HW acceleration.
  - **IPSec+LISP** - IPSec encryption with CBC-SHA1 ciphers, in combination
    with LISP-GPE overlay tunneling for IPv4-over-IPv4.
  - **VPP TCP/IP stack** - tests of VPP TCP/IP stack used with VPP built-in HTTP
    server.
  - **Container memif connections** - VPP memif virtual interface tests to
    interconnect VPP instances with L2XC and L2BD.

- 2port10GE X710 Intel

  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
    with MAC learning.
  - **VMs with vhost-user** - virtual topologies with 1 VM using vhost-user
    interfaces, with VPP forwarding modes incl. L2 Bridge-Domain.
  - **Container memif connections** - VPP memif virtual interface tests to
    interconnect VPP instances with L2XC and L2BD.
  - **Container K8s Orchestrated Topologies** - Container topologies connected
    over the memif virtual interface.

- 2port10GE VIC1227 Cisco

  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
    with MAC learning.

- 2port40GE VIC1385 Cisco

  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
     with MAC learning.

Execution of performance tests takes time, especially the throughput discovery
tests. Due to limited HW testbed resources available within FD.io labs hosted
by :abbr:`LF (Linux Foundation)`, the number of tests for NICs other than X520
(a.k.a. Niantic) has been limited to few baseline tests. CSIT team expect the
HW testbed resources to grow over time, so that complete set of performance
tests can be regularly and(or) continuously executed against all models of
hardware present in FD.io labs.

Performance Tests Naming
------------------------

CSIT |release| follows a common structured naming convention for all performance
and system functional tests, introduced in CSIT |release-1|.

The naming should be intuitive for majority of the tests. Complete description
of CSIT test naming convention is provided on :ref:`csit_test_naming`.
