---
title: "FD.io CSIT Logical Topologies"
weight: 4
---

# FD.io CSIT Logical Topologies

CSIT VPP performance tests are executed on physical testbeds. Based on the
packet path thru server SUTs, three distinct logical topology types are used
for VPP DUT data plane testing:

1. NIC-to-NIC switching topologies.
2. VM service switching topologies.
3. Container service switching topologies.

## NIC-to-NIC Switching

The simplest logical topology for software data plane application like
VPP is NIC-to-NIC switching. Tested topologies for 2-Node and 3-Node
testbeds are shown in figures below.

{{< figure src="/cdocs/logical-2n-nic2nic.svg" >}}

{{< figure src="/cdocs/logical-3n-nic2nic.svg" >}}

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

## VM Service Switching

VM service switching topology test cases require VPP DUT to communicate
with Virtual Machines (VMs) over vhost-user virtual interfaces.

Two types of VM service topologies are tested:

1. "Parallel" topology with packets flowing within SUT from NIC(s) via
   VPP DUT to VM, back to VPP DUT, then out thru NIC(s).
2. "Chained" topology (a.k.a. "Snake") with packets flowing within SUT
   from NIC(s) via VPP DUT to VM, back to VPP DUT, then to the next VM,
   back to VPP DUT and so on and so forth until the last VM in a chain,
   then back to VPP DUT and out thru NIC(s).

For each of the above topologies, VPP DUT is tested in a range of L2
or IPv4/IPv6 configurations depending on the test suite. Sample VPP DUT
"Chained" VM service topologies for 2-Node and 3-Node testbeds with each
SUT running N of VM instances is shown in the figures below.

{{< figure src="/cdocs/logical-2n-vm-vhost.svg" >}}

{{< figure src="/cdocs/logical-3n-vm-vhost.svg" >}}

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

## Container Service Switching

Container service switching topology test cases require VPP DUT to
communicate with Containers (Ctrs) over memif virtual interfaces.

Three types of VM service topologies are tested in |csit-release|:

1. "Parallel" topology with packets flowing within SUT from NIC(s) via
   VPP DUT to Container, back to VPP DUT, then out thru NIC(s).
2. "Chained" topology (a.k.a. "Snake") with packets flowing within SUT
   from NIC(s) via VPP DUT to Container, back to VPP DUT, then to the
   next Container, back to VPP DUT and so on and so forth until the
   last Container in a chain, then back to VPP DUT and out thru NIC(s).
3. "Horizontal" topology with packets flowing within SUT from NIC(s) via
   VPP DUT to Container, then via "horizontal" memif to the next
   Container, and so on and so forth until the last Container, then
   back to VPP DUT and out thru NIC(s).

For each of the above topologies, VPP DUT is tested in a range of L2
or IPv4/IPv6 configurations depending on the test suite. Sample VPP DUT
"Chained" Container service topologies for 2-Node and 3-Node testbeds
with each SUT running N of Container instances is shown in the figures
below.

{{< figure src="/cdocs/logical-2n-container-memif.svg" >}}

{{< figure src="/cdocs/logical-3n-container-memif.svg" >}}

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
