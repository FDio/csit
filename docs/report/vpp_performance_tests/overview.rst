Overview
========

For description of physical testbeds used for VPP performance tests
please refer to :ref:`physical_testbeds`.

Logical Topologies
------------------

CSIT VPP performance tests are executed on physical testbeds described
in :ref:`physical_testbeds`. Based on the packet path thru server SUTs,
three distinct logical topology types are used for VPP DUT data plane
testing:

#. NIC-to-NIC switching topologies.
#. VM service switching topologies.
#. Container service switching topologies.

NIC-to-NIC Switching
~~~~~~~~~~~~~~~~~~~~

The simplest logical topology for software data plane application like
VPP is NIC-to-NIC switching. Tested topologies for 2-Node and 3-Node
testbeds are shown in figures below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/vpp_performance_tests/logical-2n-nic2nic}
            \label{fig:logical-2n-nic2nic}
        \end{figure}

.. only:: html

    .. figure:: logical-2n-nic2nic.svg
        :alt: logical-2n-nic2nic
        :align: center


.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/vpp_performance_tests/logical-3n-nic2nic}
            \label{fig:logical-3n-nic2nic}
        \end{figure}

.. only:: html

    .. figure:: logical-3n-nic2nic.svg
        :alt: logical-3n-nic2nic
        :align: center

Server Systems Under Test (SUT) run VPP application in Linux user-mode
as a Device Under Test (DUT). Server Traffic Generator (TG) runs T-Rex
application. Physical connectivity between SUTs and TG is provided using
different drivers and NIC models that need to be tested for performance
(packet/bandwidth throughput and latency).

From SUT and DUT perspectives, all performance tests involve forwarding
packets between two (or more) physical Ethernet ports (10GE, 25GE, 40GE,
100GE). In most cases both physical ports on SUT are located on the same
NIC. The only exceptions are link bonding and 100GE tests. In the latter
case only one port per NIC can be driven at linerate due to PCIe Gen3
x16 slot bandwidth limiations. 100GE NICs are not supported in PCIe Gen3
x8 slots.

Note that reported VPP DUT performance results are specific to the SUTs
tested. SUTs with other processors than the ones used in FD.io lab are
likely to yield different results. A good rule of thumb, that can be
applied to estimate VPP packet thoughput for NIC-to-NIC switching
topology, is to expect the forwarding performance to be proportional to
processor core frequency for the same processor architecture, assuming
processor is the only limiting factor and all other SUT parameters are
equivalent to FD.io CSIT environment.

VM Service Switching
~~~~~~~~~~~~~~~~~~~~

VM service switching topology test cases require VPP DUT to communicate
with Virtual Machines (VMs) over vhost-user virtual interfaces.

Two types of VM service topologies are tested in CSIT |release|:

#. "Parallel" topology with packets flowing within SUT from NIC(s) via
   VPP DUT to VM, back to VPP DUT, then out thru NIC(s).

#. "Chained" topology (a.k.a. "Snake") with packets flowing within SUT
   from NIC(s) via VPP DUT to VM, back to VPP DUT, then to the next VM,
   back to VPP DUT and so on and so forth until the last VM in a chain,
   then back to VPP DUT and out thru NIC(s).

For each of the above topologies, VPP DUT is tested in a range of L2
or IPv4/IPv6 configurations depending on the test suite. Sample VPP DUT
"Chained" VM service topologies for 2-Node and 3-Node testbeds with each
SUT running N of VM instances is shown in the figures below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/vpp_performance_tests/logical-2n-vm-vhost}
            \label{fig:logical-2n-vm-vhost}
        \end{figure}

.. only:: html

    .. figure:: logical-2n-vm-vhost.svg
        :alt: logical-2n-vm-vhost
        :align: center


.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/vpp_performance_tests/logical-3n-vm-vhost}
            \label{fig:logical-3n-vm-vhost}
        \end{figure}

.. only:: html

    .. figure:: logical-3n-vm-vhost.svg
        :alt: logical-3n-vm-vhost
        :align: center

In "Chained" VM topologies, packets are switched by VPP DUT multiple
times: twice for a single VM, three times for two VMs, N+1 times for N
VMs. Hence the external throughput rates measured by TG and listed in
this report must be multiplied by N+1 to represent the actual VPP DUT
aggregate packet forwarding rate.

For "Parallel" service topology packets are always switched twice by VPP
DUT per service chain.

Note that reported VPP DUT performance results are specific to the SUTs
tested. SUTs with other processor than the ones used in FD.io lab are
likely to yield different results. Similarly to NIC-to-NIC switching
topology, here one can also expect the forwarding performance to be
proportional to processor core frequency for the same processor
architecture, assuming processor is the only limiting factor. However
due to much higher dependency on intensive memory operations in VM
service chained topologies and sensitivity to Linux scheduler settings
and behaviour, this estimation may not always yield good enough
accuracy.

Container Service Switching
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Container service switching topology test cases require VPP DUT to
communicate with Containers (Ctrs) over memif virtual interfaces.

Three types of VM service topologies are tested in CSIT |release|:

#. "Parallel" topology with packets flowing within SUT from NIC(s) via
   VPP DUT to Container, back to VPP DUT, then out thru NIC(s).

#. "Chained" topology (a.k.a. "Snake") with packets flowing within SUT
   from NIC(s) via VPP DUT to Container, back to VPP DUT, then to the
   next Container, back to VPP DUT and so on and so forth until the
   last Container in a chain, then back to VPP DUT and out thru NIC(s).

#. "Horizontal" topology with packets flowing within SUT from NIC(s) via
   VPP DUT to Container, then via "horizontal" memif to the next
   Container, and so on and so forth until the last Container, then
   back to VPP DUT and out thru NIC(s).

For each of the above topologies, VPP DUT is tested in a range of L2
or IPv4/IPv6 configurations depending on the test suite. Sample VPP DUT
"Chained" Container service topologies for 2-Node and 3-Node testbeds
with each SUT running N of Container instances is shown in the figures
below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/vpp_performance_tests/logical-2n-container-memif}
            \label{fig:logical-2n-container-memif}
        \end{figure}

.. only:: html

    .. figure:: logical-2n-container-memif.svg
        :alt: logical-2n-container-memif
        :align: center


.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/vpp_performance_tests/logical-3n-container-memif}
            \label{fig:logical-3n-container-memif}
        \end{figure}

.. only:: html

    .. figure:: logical-3n-container-memif.svg
        :alt: logical-3n-container-memif
        :align: center

In "Chained" Container topologies, packets are switched by VPP DUT
multiple times: twice for a single Container, three times for two
Containers, N+1 times for N Containers. Hence the external throughput
rates measured by TG and listed in this report must be multiplied by N+1
to represent the actual VPP DUT aggregate packet forwarding rate.

For a "Parallel" and "Horizontal" service topologies packets are always
switched by VPP DUT twice per service chain.

Note that reported VPP DUT performance results are specific to the SUTs
tested. SUTs with other processor than the ones used in FD.io lab are
likely to yield different results. Similarly to NIC-to-NIC switching
topology, here one can also expect the forwarding performance to be
proportional to processor core frequency for the same processor
architecture, assuming processor is the only limiting factor. However
due to much higher dependency on intensive memory operations in
Container service chained topologies and sensitivity to Linux scheduler
settings and behaviour, this estimation may not always yield good enough
accuracy.

Performance Tests Coverage
--------------------------

Performance tests measure following metrics for tested VPP DUT
topologies and configurations:

- Packet Throughput: measured in accordance with :rfc:`2544`, using
  FD.io CSIT Multiple Loss Ratio search (MLRsearch), an optimized binary
  search algorithm, producing throughput at different Packet Loss Ratio
  (PLR) values:

  - Non Drop Rate (NDR): packet throughput at PLR=0%.
  - Partial Drop Rate (PDR): packet throughput at PLR=0.5%.

- One-Way Packet Latency: measured at different offered packet loads:

  - 100% of discovered NDR throughput.
  - 100% of discovered PDR throughput.

- Maximum Receive Rate (MRR): measure packet forwarding rate under the
  maximum load offered by traffic generator over a set trial duration,
  regardless of packet loss. Maximum load for specified Ethernet frame
  size is set to the bi-directional link rate.

CSIT |release| includes following performance test areas covered across
a range of NIC drivers and NIC models:

+-----------------------+----------------------------------------------+
| Test Area             |  Description                                 |
+=======================+==============================================+
| ACL                   | L2 Bridge-Domain switching and               |
|                       | IPv4and IPv6 routing with iACL and oACL IP   |
|                       | address, MAC address and L4 port security.   |
+-----------------------+----------------------------------------------+
| COP                   | IPv4 and IPv6 routing with COP address       |
|                       | security.                                    |
+-----------------------+----------------------------------------------+
| IPv4                  | IPv4 routing.                                |
+-----------------------+----------------------------------------------+
| IPv6                  | IPv6 routing.                                |
+-----------------------+----------------------------------------------+
| IPv4 Scale            | IPv4 routing with 20k, 200k and 2M FIB       |
|                       | entries.                                     |
+-----------------------+----------------------------------------------+
| IPv6 Scale            | IPv6 routing with 20k, 200k and 2M FIB       |
|                       | entries.                                     |
+-----------------------+----------------------------------------------+
| IPSecHW               | IPSec encryption with AES-GCM, CBC-SHA1      |
|                       | ciphers, in combination with IPv4 routing.   |
|                       | Intel QAT HW acceleration.                   |
+-----------------------+----------------------------------------------+
| IPSec+LISP            | IPSec encryption with CBC-SHA1 ciphers, in   |
|                       | combination with LISP-GPE overlay tunneling  |
|                       | for IPv4-over-IPv4.                          |
+-----------------------+----------------------------------------------+
| IPSecSW               | IPSec encryption with AES-GCM, CBC-SHA1      |
|                       | ciphers, in combination with IPv4 routing.   |
+-----------------------+----------------------------------------------+
| K8s Containers Memif  | K8s orchestrated container VPP service chain |
|                       | topologies connected over the memif virtual  |
|                       | interface.                                   |
+-----------------------+----------------------------------------------+
| KVM VMs vhost-user    | Virtual topologies with service              |
|                       | chains of 1 and 2 VMs using vhost-user       |
|                       | interfaces, with different VPP forwarding    |
|                       | modes incl. L2XC, L2BD, VXLAN with L2BD,     |
|                       | IPv4 routing.                                |
+-----------------------+----------------------------------------------+
| L2BD                  | L2 Bridge-Domain switching of untagged       |
|                       | Ethernet frames with MAC learning; disabled  |
|                       | MAC learning i.e. static MAC tests to be     |
|                       | added.                                       |
+-----------------------+----------------------------------------------+
| L2BD Scale            | L2 Bridge-Domain switching of untagged       |
|                       | Ethernet frames with MAC learning; disabled  |
|                       | MAC learning i.e. static MAC tests to be     |
|                       | added with 20k, 200k and 2M FIB entries.     |
+-----------------------+----------------------------------------------+
| L2XC                  | L2 Cross-Connect switching of untagged,      |
|                       | dot1q, dot1ad VLAN tagged Ethernet frames.   |
+-----------------------+----------------------------------------------+
| LISP                  | LISP overlay tunneling for IPv4-over-IPv4,   |
|                       | IPv6-over-IPv4, IPv6-over-IPv6,              |
|                       | IPv4-over-IPv6 in IPv4 and IPv6 routing      |
|                       | modes.                                       |
+-----------------------+----------------------------------------------+
| LXC/DRC Containers    | Container VPP memif virtual interface tests  |
| Memif                 | with different VPP forwarding modes incl.    |
|                       | L2XC, L2BD.                                  |
+-----------------------+----------------------------------------------+
| NAT                   | (Source) Network Address Translation tests   |
|                       | with varying number of users and ports per   |
|                       | user.                                        |
+-----------------------+----------------------------------------------+
| QoS Policer           | Ingress packet rate measuring, marking and   |
|                       | limiting (IPv4).                             |
+-----------------------+----------------------------------------------+
| SRv6 Routing          | Segment Routing IPv6 tests.                  |
+-----------------------+----------------------------------------------+
| VPP TCP/IP stack      | Tests of VPP TCP/IP stack used with VPP      |
|                       | built-in HTTP server.                        |
+-----------------------+----------------------------------------------+
| VXLAN                 | VXLAN overlay tunnelling integration with    |
|                       | L2XC and L2BD.                               |
+-----------------------+----------------------------------------------+

Execution of performance tests takes time, especially the throughput
tests. Due to limited HW testbed resources available within FD.io labs
hosted by :abbr:`LF (Linux Foundation)`, the number of tests for some
NIC models has been limited to few baseline tests.

Performance Tests Naming
------------------------

FD.io CSIT |release| follows a common structured naming convention for
all performance and system functional tests, introduced in CSIT rls1701.

The naming should be intuitive for majority of the tests. Complete
description of FD.io CSIT test naming convention is provided on
:ref:`csit_test_naming`.
