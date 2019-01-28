---
title: NFV Service Density Benchmarking
# abbrev: nf-svc-density
docname: draft-mkonstan-nf-service-density-00
date: 2019-xx-xx

ipr: trust200902
area: ops
wg: Benchmarking Working Group
kw: Internet-Draft
cat: info

coding: us-ascii
pi:    # can use array (if all yes) or hash here
#  - toc
#  - sortrefs
#  - symrefs
  toc: yes
  sortrefs:   # defaults to yes
  symrefs: yes

author:
      -
        ins: M. Konstantynowicz
        name: Maciek Konstantynowicz
        org: Cisco Systems
        role: editor
        email: mkonstan@cisco.com
      -
        ins: P. Mikus
        name: Peter Mikus
        org: Cisco Systems
        role: editor
        email: pmikus@cisco.com

normative:
  RFC2544:
  RFC8174:

informative:

--- abstract

Network Function Virtualization (NFV) system designers and operators
continuously grapple with the problem of qualifying performance of
network services realised with software Network Functions (NF) running
on Commercial-Off-The-Shelf (COTS) servers. One of the main challenges
is getting repeatable and portable benchmarking results and using them
to derive deterministic operating range that is production deployment
worthy.

This document specifies benchmarking methodology for NFV services that
aims to address this problem space. It defines a framework for measuring
performance of multiple NFV services, each composed of multiple software
NFs, and running them at a varied service “packing” density on a single
server.

The aim is to discover deterministic usage range of NFV system. In
addition specified framework can be used to compare and contrast
different NFV virtualization technologies.

--- middle

# Terminology

[TODO to be completed]

* NFV service instance - ..
* Performance optimized network application - .. e.g. FD.io VPP (Vector
  Packet Processor).
* ..

# Motivation

## Problem Description

Network Function Virtualization (NFV) system designers and operators
continuously grapple with the problem of qualifying performance of
network services realised with software Network Functions (NF) running
on Commercial-Off-The-Shelf (COTS) servers. One of the main challenges
is getting repeatable and portable benchmarking results and using them
to derive deterministic operating range that is production deployment
worthy.

Lack of well defined and standardised NFV centric performance
methodology and metrics makes it hard to address fundamental questions
that underpin NFV production deployments:

1. What and how many NFV services can run on a single compute node?
2. How to choose the best compute resource allocation scheme to maximise
   service yield per node?
3. How do different NF applications compare from the service density
   perspective?
4. How do the virtualisation technologies compare e.g. Virtual Machines,
   Containers?

Getting answers to these points should allow designers to make a data
based decision about the NFV technology and service design best suited
to meet requirements of their use cases. Equally, obtaining the
benchmarking data underpinning those answers should make it easier for
operators to work out expected deterministic operating range of chosen
design.

## Proposed Solution

The primary focus of the proposed benchmarking methodology is on NFV
technologies used to construct network services. More specifically to
measure packet data-plane performance of multiple NFV services while
running them at varied service “packing” densities on a single server.

The aim is to discover a set of deterministic usage ranges that are of
interest to NFV system designers and operators. In addition, specified
methodology can be used to compare and contrast different NFV
virtualisation technologies.

In order to ensure wide applicability of the benchmarking methodology,
the approach is to separate NFV service packet processing from the
shared virtualisation infrastructure by decomposing the software
technology stack into three building blocks:

```
    [NFV Service] x [Virtualization Technology] x [Host Networking]
```

Proposed methodology is complementary to existing NFV benchmarking
industry efforts focusing on vSwitch benchmarking [RFC8204], [ETSI GS
NFV-TST009 ] and extends the benchmarking scope to NFV services.

# NFV Service

It is assumed that each NFV service is built of one or more constituent
NFs and is described by: topology, configuration and resulting packet
path(s).

## Topology

NFV topology describes the number of network functions per service
instance, and their inter-connections at packet layer. Includes all
point-to-point packet links, Layer-2 Ethernet or Layer-3 IP.
Benchmarking is done through external physical network connections, and
network topology must include connectivity to external physical network
devices, handled by Host data-plane. L2 sub- encapsulations (e.g.
802.1q, 802.1ad) and IP overlay encapsulation (e.g. VXLAN, IPSec, GRE)
are not represented at this layer.

Theoretically, a large set of possible NFV topologies can be realised
using software virtualisation topologies, e.g. ring, partial -/full-
mesh, star, line, tree, ladder. In practice however, only a few
topologies are in the actual use as NFV services mostly perform either
bumps-in-a-wire packet operations (e.g. security filtering/inspection,
monitoring/telemetry) and/or inter-site forwarding decisions (e.g.
routing, switching).

Two main NFV topologies have been identified so far for NFV service
density benchmarking:

1. Chain topology: a set of NFs connect to host data-plane with minimum
   of two virtual interfaces each, enabling host data-plane to
   facilitate NF to NF service chain forwarding and provide connectivity
   with external network.

2. Pipeline topology: a set of NFs connect to each other in a line
   fashion with edge NFs homed to host data-plane. Host data-plane
   provides connectivity with external network.

Each set of NFs forms an independent NFV service instance, with multiple
sets present in the host.

Both topologies are shown in figure below.

[TODO Figure: Chain and pipeline NF topologies]

## Configuration

NFV configuration includes all packet processing functions in NFs and
host data-plane including Layer-2, Layer-3 and/or Layer-4-to-7
processing as appropriate to specific NF and NFV service design. L2 sub-
interface encapsulations (e.g. 802.1q, 802.1ad) and IP overlay
encapsulation (e.g. VXLAN, IPSec, GRE) are represented here too.

NFV configuration determines logical network connectivity that is
Layer-2 and/or IPv4/IPv6 switching/routing modes, as well as NFV service
specific aspects. In the context of NFV density benchmarking methodology
the initial focus is on the former.

Building on the two identified NFV topologies, two common NFV
configurations are considered:

1. Chain configuration:
   * Relies on chain topology to form NFV service chains.
   * Packet forwarding designs:
     * L2 switching in host data-plane, IPv4/IPv6 routing in NFs.
     * IPv4/IPv6 routing in host data-plane and in NFs.
2. Pipeline configuration:
   * Relies on pipeline topology to form NFV service pipelines.
   * Packet forwarding designs:
     * L2 cross-connect in host data-plane, IPv4/IPv6 routing in NFs.
     * L2 switching in host data-plane, IPv4/IPv6 routing in NFs.
     * IPv4/IPv6 routing in host data-plane and in NFs.

## Packet Path(s)

NFV packet path(s) describe the actual packet forwarding path(s) used
for benchmarking, resulting from NFV topology and configuration. They
are aimed to resemble true packet forwarding actions during the NFV
service lifecycle.

Based on the specified NFV topologies and configurations two NFV packet
paths are taken for benchmarking:

1. Snake packet path
   * Requires chain topology and configuration.
   * Packets enter the NFV chain through one edge NF and progress to the
     other edge NF of the chain.
   * Within the chain, packets follow a zigzagging "snake" path entering
     and leaving host data-plane as they progress through the NF chain.
   * Host data-plane is involved in packet forwarding operations between
     NIC interfaces and edge NFs, as well as between NFs in the chain.

2. Pipeline packet path
   * Requires pipeline topology and configuration.
   * Packets enter the NFV chain through one edge NF and progress to the
     other edge NF of the pipeline.
   * Within the chain, packets follow a straight path entering and
     leaving subsequent NFs as they progress through the NF pipeline.
   * Host data-plane is involved in packet forwarding operations between
     NIC interfaces and edge NFs only.

In all cases packets enter NFV system via shared physical NIC interfaces
controlled by shared host data-plane, are then associated with specific
NFV service (based on service discriminator) and subsequently are cross-
connected/switched/routed by host data-plane to and through NF
topologies per one of above listed schemes.

# Virtualization Technology

NFV services are built of composite isolated NFs, with virtualisation
technology providing the workload isolation. Following virtualisation
technology types are considered for NFV service density benchmarking:

1. Virtual Machines (VMs)
   * Relying on host hypervisor technology e.g. KVM, ESXi, Xen.
   * NFs running in VMs are referred to as VNFs.
2. Containers
   * Relying on Linux container technology e.g. LXC, Docker.
   * NFs running in Containers are referred to as CNFs.

Different virtual interface types are available to VNFs and CNFs:

1. VNF
   * virtio-vhostuser: fully user-mode based virtual interface.
   * virtio-vhostnet: involves kernel-mode based backend.
2. CNF
   * memif: fully user-mode based virtual interface.
   * af_packet: involves kernel-mode based backend.
   * [add more common ones]

# Host Networking

Host networking data-plane is the central shared resource that underpins
creation of NFV services.

Assuming that NIC interface resources are shared, here is the list of
widely available host data-plane options for providing packet
connectivity to/from NICs and constructing NFV chain and pipeline
topologies and configurations:

* Linux Kernel-Mode Networking.
* Linux User-Mode vSwitch.
* Virtual Machine vSwitch.
* Linux Container vSwitch.
* SRIOV NIC Virtual Function - note: restricted support for chain and
  pipeline topologies, as it requires hair-pinning through the NIC and
  oftentimes also through external physical switch.

Analysing properties of each of these options and their Pros/Cons for
specified NFV topologies and configurations is outside the scope of this
document.

From all listed options, performance optimised Linux user-mode vswitch
deserves special attention. Linux user-mode switch decouples NFV service
from the underlying NIC hardware, offers rich multi-tenant functionality
and most flexibility for supporting NFV services. But in the same time
it is consuming compute resources and is harder to benchmark in NFV
service density scenarios.

Following sections focus on using Linux user-mode switch for these
reasons.

# NFV Service Density Matrix

NFV services are benchmarked at increasing service densities per server
node. Due to a shared nature of compute environment, critical compute
resources are allocated whenever possible to NFs’ Data- plane software
threads using a clearly defined scheme, ensuring measurements
repeatability.

Following sections specify the details of NFV system and service model,
service density, resource allocation and examples applying this
framework to VM and Container based NFV services.

Proposed approach to evaluating maximum NFV service density per compute
node is simple. A simple service density matrix is defined as follows:

```
Row:    1..10  Network Service Instances.
Column: 1..10  Network Functions per Service Instance.
Value:  1..100 Network Functions
SVC   001   002   004   006   008   010
001     1     2     4     6     8    10
002     2     4     8    12    16    20
004     4     8    16    24    32    40
006     6    12    24    36    48    60
008     8    16    32    48    64    80
010    10    20    40    60    80   100
```

Each of the configurations identified by (Row, Column) is evaluated for
NFV service Data-plane performance using existing and/or emerging
network benchmarking standards. This may include methodologies specified
in RFC2544, ETSI TST VSPERF, mlrsearch-draft or plrsearch-draft. Host
Data-plane is a gateway between the external network and the internal
NFV network topologies. Benchmarking packet offered load is generated
and received by an external traffic generator per usual benchmarking
practice.

[TODO address Vratko comment: Therefore this Draft does not describe (at
leas up to line 299) a complete benchmarking methodology, just a SUT
configuration part for any (two-port) methodology.

We are not describing how to prepare SUT with ARP. We allow testing for
latency, jitter and other quantities not related to throughput. We do
not support datacenter cases like TG sending traffic to two ports where
SUT has only one outgoing port. Need to add this as a list of caveats of
what's not covered.]

Care must be taken to ensure that each service instance is
loaded equally.

[TODO Vratko comment: ... but details are not described here any
further. We probably should mention RSS and rx queues at least when
presenting fd.io results.]

# Compute Resource Allocation

The most critical compute resource that determines performance of the
system is physical processor cores. Other compute resources including
processor cache hierarchy, memory bandwidth and PCIe bandwidth have
lesser impact and as such are left out for further study. Some idea of
the impact of other than processor core compute resources can be found
in [bdx_skx_intel_cisco_technical_paper].

Specific ratios are defined for mapping software threads of vswitch and
VNFs/CNFs to physical cores, with separate ratios defined for main
control threads and data-plane threads.

[TODO add a note about core pinning]

If NFV service density benchmarking is run on server nodes with
Symmetric Multi-Threading (SMT) (e.g. Intel Hyper-Threading) for higher
performance and efficiency, each physical core is associated with a pair
of sibling logical cores corresponding to the hyper-threads.

Following mapping ratio scheme of software thread to logical and
physical cores is proposed as part of this methodology (below assumes
SMT/HT is enabled):

* vSwitch
  * Data-plane on a single core
    * (data:core) = (1:1) => 2dt:2lc(1pc) - 2 data threads on dedicated
      2 sibling logical cores (1 physical core).
    * (main:core) = (1:0.5) => 1mt:1lc(0.5pc) - 1 main thread on shared
      physical core.
  * Data-plane on two cores
    * (data:core) = (1:2) => 4dt:4lc(2pc) - 4 data threads on dedicated
      4 sibling logical cores (2 physical cores).
    * (main:core) = (1:0.5) => 1mt:1lc(0.5pc) - 1 main thread on shared
      physical core.
  * Data-plane on four cores
    * (data:core) = (1:4) => 8dt:8lc(4pc) - 8 data threads on dedicated
      8 sibling logical cores (4 physical cores).
    * (main:core) = (1:0.5) => 1mt:1lc(0.5pc) - 1 main thread on shared
      physical core.

* VNF and CNF
  * Data-plane on a single core
    * (data:core) = (1:1) => 2dt:2lc(1pc) - 2 data threads on dedicated
      2 sibling logical cores (1 physical core).
    * (main:core) = (1:0.5) => 1mt:1lc(0.5pc) - 1 main thread on shared
      physical core.
  * Data-plane on a half of a core
    * (data:core) = (1:0.5) => 1dt:1lc(0.5pc) - 1 data thread on a
      dedicated 1 sibling logical core (0.5 physical core).
    * (main:core) = (1:0.5) => 1mt:1lc(0.5pc) - 1 main thread on shared
      physical core.

Maximum benchmarked NFV service densities are limited by a number of
physical cores per NUMA.

A sample processor physical core usage view is shown below.

```
NFV Service Density - Core Usage View
Row:          1..10 number of network service instances
Column:       1..10 number of network functions per service instance
Value:        1..NN number of physical processor cores used for NFs
Cores Numa0:  vswitch: (data:core) = (1:1), (main:core) = (1:0.5)
              nf: (data:core) = (1:1), (main:core) = (1:0.5)
Cores Numa1:  not used

SVC   001   002   004   006   008   010
001     2     3     6     9    12    15
002     3     6    12    18    24    30
004     6    12    24    36    48    60
006     9    18    36    54    72    90
008    12    24    48    72    96   120
010    15    30    60    90   120   150
```

# NFV Service Density Benchmarks

[TODO Section to be completed]

To illustrate defined NFV service density applicability, following
sections describe three NFV service topologies that have been
benchmarked in open-source as part of CNCF/CNFs initiative [add ref to
cncf/cnf github] and in FD.io (http://FD.io) CSIT project [add ref]. All
service topologies are based on the same network topology described in
the previous section.

## Test Methodology - MRR Throughput

[TODO Section to be completed]

Maximum Receive Rate (MRR) tests measure the packet forwarding rate
under the maximum load offered by traffic generator over a set trial
duration, regardless of packet loss. Maximum load for specified Ethernet
frame size is set to the bi-directional link rate.

## VNF Service Chain (VSC)

[TODO Section to be completed]

VNF Service Chain (VSC) topology with Snake Forwarding is shown in
figure.

## CNF Service Chain (CSC)

[TODO Section to be completed]

CNF Service Chain (CSC) topology with Snake Forwarding is shown in
figure.

## CNF Service Pipeline (CSP)

[TODO Section to be completed]

CNF Service Pipeline (CSP) topology with Pipeline Forwarding
is shown in figure.

## Sample Results

[TODO Section to be completed]

### Testbed: FD.io (http://FD.io) CSIT 2n-skx

[TODO Section to be completed]

### Packet.net 2n-skx

[TODO Section to be completed]
