Overview
========

.. _tested_physical_topologies:

(editor: remove above tag: ".. _tested_physical_topologies:")

For description of physical testbeds used for VPP performance tests
please refer to :ref:`physical_testbeds`.

Logical Topologies
------------------

CSIT VPP performance tests are executed on physical testbeds described
in :ref:`physical_testbeds`. Based on the packet path thru SUT, three
distinct logical topology types are used for VPP DUT data plane testing:

#. NIC-to-NIC switching topologies.
#. VM service switching topologies.
#. Container service switching topologies.

NIC-to-NIC Switching
~~~~~~~~~~~~~~~~~~~~

The most baseline logical topology for software data plane application
like VPP is NIC-to-NIC switching. Tested topologies for 2-Node and
3-Node testbeds are shown in figures below.

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

SUTs run VPP application in Linux user-mode as a Device Under Test
(DUT). TG runs TRex application. Physical connectivity between SUTs and
TG is provided using different NIC models that need to be tested for
performance.

From SUT and DUT perspective, all performance tests involve forwarding
packets between two physical Ethernet ports (10GE, 25GE, 40GE, 100GE).
In most cases both physical ports on SUT are located on the same NIC.
The only exception is 100GE NIC, where only one port per NIC can be
driven at linerate due to PCIe Gen3 x16 slot bandwidth limiations.

Note that reported DUT (VPP) performance results are specific to the
SUTs tested. SUTs with other processor than the ones used in FD.io lab
are likely to yield different results. A good rule of thumb, that can be
applied to estimate VPP packet thoughput for NIC-to-NIC switching
topology, is to expect the forwarding performance to be proportional to
CPU core frequency, assuming CPU is the only limiting factor and all
other SUT parameters are equivalent to FD.io CSIT environment.

VM Service Switching
~~~~~~~~~~~~~~~~~~~~

VM service switching topology test cases require DUT (VPP) to
communicate with VirtualMachines (VMs) over vhost-user virtual
interfaces.

Two types of VM service topologies are tested in CSIT |release|:

#. "Parallel" topology with packets flowing from NIC via DUT (VPP) to
   VM and back to VPP and NIC.

#. "Chained" topology (a.k.a. "Snake") with packets flowing via DUT
   (VPP) to VM, back to DUT, then to the next VM, back to DUT and so on
   and so forth until the last VM in a chain, then back to DUT and NIC.

For each of the above topologies, DUT (VPP) is tested in a range of L2
or IPv4/IPv6 configurations depending on the test suite. Sample DUT
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

In above "Chained" VM topologies, packets are switched by DUT multiple
times: twice for a single VM, three times for two VMs, N+1 times for N
VMs. Hence the external throughput rates measured by TG and listed in
this report must be multiplied by (N+1) to represent the actual DUT
aggregate packet forwarding rate.

For "Parallel" service topology packets are always switched twice by DUT
per service chain.

Note that reported DUT (VPP) performance results are specific to the
SUTs tested. SUTs with other processor than the ones used in FD.io lab
are likely to yield different results. Similarly to NIC-to-NIC switching
topology, here one can also expect the forwarding performance to be
proportional to CPU core frequency, assuming CPU is the only limiting
factor and all other SUT parameters are equivalent to FD.io CSIT
environment. However due to much higher dependency on intensive memory
operations and sensitivity to Linux kernel scheduler settings and
behaviour, this estimation may not always yield good enough accuracy.

Container Service Switching
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Container service switching topology test cases require DUT (VPP) to
communicate with Containers (Ctrs) over memif virtual interfaces.

Three types of VM service topologies are tested in CSIT |release|:

#. "Parallel" topology with packets flowing from NIC via DUT (VPP) to
   Container and back to VPP and NIC.

#. "Chained" topology (a.k.a. "Snake") with packets flowing via DUT
   (VPP) to Container, back to DUT, then to the next Container, back to
   DUT and so on and so forth until the last Container in a chain, then
   back to DUT and NIC.

#. "Horizontal" topology with packets flowing via DUT (VPP) to
   Container, then via "horizontal" memif to the next Container, and so
   on until the last Container, then back to DUT and NIC.

For each of the above topologies, DUT (VPP) is tested in a range of L2
or IPv4/IPv6 configurations depending on the test suite. Sample DUT
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

In above "Chained" Container topologies, packets are switched by DUT
multiple times: twice for a single Container, three times for two
Containers, N+1 times for N Containers. Hence the external throughput
rates measured by TG and listed in this report must be multiplied by
(N+1) to represent the actual DUT aggregate packet forwarding rate.

For a "Parallel" and "Horizontal" service topologies packets are always
switched by DUT twice per service chain.

Note that reported DUT (VPP) performance results are specific to the
SUTs tested. SUTs with other processor than the ones used in FD.io lab
are likely to yield different results. One can expect the forwarding
performance to be proportional to CPU core frequency, assuming CPU is
the only limiting factor and all other SUT parameters are equivalent to
FD.io CSIT environment. However due to much higher dependency on
intensive memory operations and sensitivity to Linux kernel scheduler
settings and behaviour, this estimation may not always yield good enough
accuracy.

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
and system functional tests, introduced in CSIT rls1701.

The naming should be intuitive for majority of the tests. Complete description
of CSIT test naming convention is provided on :ref:`csit_test_naming`.
