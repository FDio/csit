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

Network Function Virtualization (NFV) system designers and operators continuously grapple with the problem of quantifying performance of network services realised with software Network Functions (NF) running on Commercial-Off-The-Shelf (COTS) servers. One of the main challenges is getting repeatable and portable benchmarking results and using them to derive deterministic operating range that is production deployment worthy.

This document specifies benchmarking methodology for NFV network services that aims to address this problem. It defines a framework for measuring performance of multiple NFV services, each composed of multiple software NFs, and running them at a varied service “packing” density on a single server, server cluster.
The aim is to discover deterministic usage range of NFV system. In addition specified framework can be used to compare and contrast different NFV virtualization technologies.

--- middle

# Terminology
[to be added]

# Motivation
## Problem Description
Network Function Virtualization (NFV) system designers and operators continuously grapple with the problem of quantifying performance of network services built with software Network Functions (NF) running on Commercial-Off-The-Shelf (COTS) servers. One of the main challenges is getting repeatable and portable benchmarking results and using them to derive deterministic operating range that is production deployment worthy.
Lack of well defined and standardised NFV technology centric performance framework and metrics makes it hard to address fundamental questions that underpin NFV production deployments:

1. What and how many NFV services can run on a single compute node, cluster?
2. How to choose the best compute resource allocation scheme to maximise service yield per node, per cluster?
3. How do different NF applications compare from the service density perspective?
4. How do NF virtualisation technologies compare e.g. Virtual Machines, Containers?

Getting answers to these points should allow designers to make a data based decision about the best NFV technology and service design that meet requirements of their use cases. Equally, obtaining the benchmarking data underpinning those answers should make it easier for operators to work out expected deterministic operating range of chosen design.

## Proposed Solution
The primary focus of the proposed benchmarking framework is on NFV technologies that are used construct network services. The framework defines a methodology for measuring packet Data-plane performance of multiple NFV services while running them at varied service “packing” densities on a single server and/or server cluster. Most of provided technical detail is Linux specific i.e. host networking and virtualization technologies. However the overall concept and methodology equally apply to any other Operating System.
The aim is to discover a set of deterministic usage ranges that are of interest to NFV system designers and operators. In addition specified framework can be used to compare and contrast different NFV virtualisation technologies.
In order to ensure wide applicability of the benchmarking framework, the approach is to separate NF packet processing from the shared virtualisation infrastructure by decomposing NFV software technology stack as follows:

```
[NFV Service] x [Virtualization Technology] x [Host Networking]
```

This decoupling allows for benchmarking of the same NFV service with different combinations of virtualization infrastructure and host networking technologies and for providing measurement data for comparing and contrasting performance between different combinations, including any future developments and improvements.
Delving deeper into each building block, following evaluation approach is proposed:

1. NFV Service: It is assumed that each NFV service is built of constituent NFs, one or more, and is modelled as a layered set of:
   * network layer: how many NFs and links, their inter-connect topology,
   * service layer: how are the NFs configured, and
   * forwarding path(s): how are packets forwarded.
2. Virtualization Technologies: NFs run in Virtual Machines or in Containers, or just as user-mode processes, using virtual interfaces for exchanging packets.
3. Host Networking: NF Data-plane inter-connectivity to the external network and often between NFs is provided by host Data-plane e.g. with Linux kernel networking, Linux user-mode switch.

NFV services are benchmarked at increasing service densities per server or server cluster. Due to a shared nature of compute environment, critical compute resources are allocated whenever possible to NFs’ Data-plane software threads using a clearly defined scheme, ensuring measurements repeatability.
Following sections specify the details of NFV system and service model, service density, resource allocation and examples applying this framework to VM and Container based NFV services.
Proposed framework is complementary to existing NFV benchmarking industry efforts focusing on vSwitch benchmarking [RFC8204], [ETSI GS NFV-TST009 ] and extends the benchmarking scope to NFV services.

# NFV Service
## Overview
Proposed benchmarking framework for NFV network services relies on a simple high-level abstraction model that captures the way NFV services are constructed.

The model assumes each NFV service is composed of interconnected software NFs, that are configured to process and forward packets. It accommodates kernel-mode and user-mode network options, as is expected to be universal covering both today's and future NFV service designs.

A common misconception is considering NFV service as composed of a single network function, leaving all optimisation and efficiency magic to within the application. However in most cases NFV services consist of more than one NF application, and that is where software “virtual” inter-connectivity and topology of NFs come into play. It is this simple concept that underpins proposed NFV model definition.

## Model Definition
Each NFV benchmarked service is modelled as a layered set, from the bottom up, consisting of:
1. Network Layer
2. Service Layer
3. Forwarding Layer

## Network Layer
Network layer describes the number of network functions per service instance, and how they are inter-connected at a packet layer. Includes all point-to-point links at the lowest packet layer, Layer-2 Ethernet or Layer-3 IP links if Ethernet encapsulation not present. Benchmarking is done through external physical network connections, and network topology must include connectivity to external physical network devices, handled by Host Data-plane. L2 sub-encapsulations (e.g. 802.1q, 802.1ad) and IP overlay encapsulation (e.g. VXLAN, IPSec, GRE) are not represented at this layer.

Theoretically, a large set of possible NFs’ network topologies (e.g. ring, partial-/full-mesh, star, line, tree, ladder) can be realised using software virtualisation topologies. In practice, however, only a few topologies are applicable and in use for NFV. This is due to the fact that most NFV services perform either bumps-in-a-wire packet operations (e.g. security filtering/inspection, monitoring/telemetry) and/or inter-site forwarding decisions (e.g. routing, switching).

With this in mind following two universal NF topologies have been identified for the NFV benchmarking framework:

1. Set of dual-homed NFs: {N} NFs, each connected with two virtual interfaces to Host Data-plane, N=1..Nmax.
2. Dual-homed line of NFs: {N} NFs connected in line, with edge NFs interfacing to Host Data-plane, N=1..Nmax.

In all cases, Nmax is the maximum number of NFs in NFV service. Both topologies are shown in figure below.

[Figure: Set of dual-homed NFs]
[Figure: Dual-homed line of NFs]

## Service Layer
Service layer describes how the network functions are configured and how they are inter-connected at a servicer layer. Combined with network layer topology, service layer determines packet paths thru NFV services.

Service layer includes all packet processing functions at Layer-2, Layer-3 and/or Layer-4-to-7 as appropriate to specific NF and NFV service design. Service level L2 sub-encapsulations (e.g. 802.1q, 802.1ad) and IP overlay encapsulation (e.g. VXLAN, IPSec, GRE) are represented at this layer.
Two common NFV service topology types that correspond to NF topologies described earlier:

* Service Chain:
  * Set of NFs dual-homed to Host Data-plane. Host Data-plane configured with L2 or IP forwarding contexts connecting NFs into a logical service chain.
  * Common deployment options include:
    * L2 in host Data-plane, IPv4/IPv6 function(s) in NFs.
    * IPv4 in host Data-plane, IPv4 function(s) in NFs.
    * IPv6 in host Data-plane, IPv6 function(s) in NFs.
* Service Pipeline:
  * Line of NFs dual-homed to Host Data-plane. Host Data-plane configured with L2 or IP forwarding contexts connecting NFs to external interfaces or another distinct service chain.
  * Common deployment options include:
    * L2 in host Data-plane, IPv4/IPv6 function(s) in NFs.
    * IPv4 in host Data-plane, IPv4 function(s) in NFs.
    * IPv6 in host Data-plane, IPv6 function(s) in NFs.

## Forwarding Path(s)
Forwarding path(s) describes the actual packet forwarding path(s) used for benchmarking, resulting from network layer and service layer configurations.
Two common NFV forwarding paths are:

* Snake Forwarding:
  * [add description]
* Pipeline Forwarding:
  * [add description]

## Putting It Together

Example of a layered NFV service model is a typical IPv4 NF service chain with L2 virtual switch shown in figure.
[add figure per slide 24 in ASCII artwork]

Defined layering applies to services spanning a single node as well as multiple nodes, see figure.
[add figure showing the layering across multiple nodes in ASCII artwork]

# Virtualization Technologies
Assumption is made that benchmarked NFs can run on compute nodes in any Linux supported modes including:
1. Virtual Machines (e.g. KVM), referred in this document as VNFs.
2. Containers (e.g. LXC, Docker), referred to as CNFs.
3. Bare-metal user-mode, referred to as BNFs.

Depending on virtualization technology used, different virtual interface types are available to NFs:
* VNF
  * virtio-vhostuser: fully user-mode interface.
  * virtio-vhostnet: involves kernel-mode backend.
* CNF
  * memif: fully user-mode interface.
  * af_packet: involves kernel-mode backend.


# Host Networking
There is a great choice of Host Data-plane options that can be used for constructing NFV services and facilitating packet connectivity thru NICs with external networks. Examples include:

* Linux Kernel-Mode Networking
* Linux User-Mode Switch
* Virtual Machine Switch
* Linux Container Switch
* Direct Virtual Function
* Direct Physical Function

Analysing properties of each of these options and their Pros/Cons for specified NFV service models is outside the scope of this document.
From all listed options, performance optimised Linux user-mode switch deserves special attention.
Linux user-mode switch decouples NFV service from the underlying NIC hardware, offers rich multi-tenant functionality and most flexibility for supporting NFV services. But in the same time it is consuming compute resources and is harder to benchmark in NFV service density scenarios.
Following sections default to using linux user-mode switch  for these reasons.

# Service Density Matrix
Proposed approach to evaluating maximum NFV service density per compute node is simple. A simple service density matrix is defined as follows:
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
Each of the configurations identified by (Row, Column) is evaluated for NFV service Data-plane performance using existing and/or emerging network benchmarking standards. This may include methodologies specified in RFC2544, ETSI TST VSPERF, mlrsearch-draft or plrsearch-draft.
Host Data-plane is a gateway between the external network and the internal NFV network topologies. Benchmarking packet offered load is generated and received by an external traffic generator per usual benchmarking practice.
Care must be taken to ensure that each service instance is loaded equally.

# Resource Allocation
## Methodology
## Methodology
The most critical compute resource that determines performance of the system is physical processor cores. Other compute resources processor cache hierarchy, memory bandwidth and PCIe bandwidth have lesser impact are left out for further study. Some idea of the impact of other than processor core compute resources can be found in [bdx skx intel cisco technical paper].
Proposed methodology of physical core allocation relies on core-to-thread mapping ratios.
Every performance optimized NFV application has
two sets of software threads: i) main threads, handling application management and control-planes, and ii) data-plane threads, handling data-plane packet processing and forwarding. Hence two separate core-to-thread mapping ratios are proposed for NFV service density exercise, as follows:

* `pcdr4appX` value determines Physical Core to Data-plane Ratio for appX.
* `pcmr4appX` value determines Physical Core to Main Ratio for appX.

Number of physical cores required for the benchmarked application is calculated as follows:

* #pc = pcdr4app1 * #dapp1 + pcmr4app1 * #mapp1
* where
* #pc - total number of physical cores required and used.
* #dapp1 - total number of app1 data-plane thread sets (1 set per app).
* #mapp1 - total number of app1 main thread sets (1 set per app).

## Use case: Linux User-Mode Switch and CNFs/VNFs
Common NFV use case entails use of Linux User-Mode Switch and Network Functions running in VMs (aka VNFs) or in Containers (aka CNFs). Following examples apply defined processor core allocation scheme to this use case.

### Linux User-Mode Switch
A single instance of Linux User-Mode Software (SW) Switch is running in a compute node.
Allocation of processor physical cores to the software switch is as follows:

1. Two mapping ratios are defined and used in software switch
   benchmarking:
   * `pcdr4sw` value determines Physical Core to Data-plane Ratio for SWitch.
   * `pcmr4sw` value determines Physical Core to Main Ratio for SWitch.
2. Target values to be benchmarked:
   * pcdr4sw = [(1:1),(2:1),(4:1)].
   * pcmr4sw = [(1:1),(1:2)].
3. Number of physical cores required for the benchmarked software switch
   is calculated as follows:
   *     #pc = pcdr4sw * #dsw + pcmr4sw * #msw
   * where
   *     #pc - total number of physical cores required and used.
   *     #dsw - total number of switch Data-plane thread sets (1 set per SW switch).
   *     #msw - total number of switch main thread sets (1 set per SW switch).

### CNFs and VNFs
Multiple instances of NFs (CNFs or VNFs) are running in a compute node.
Allocation of processor physical cores per NF instance is as follows:

1. Two mapping ratios are defined and used in NF service matrix
   benchmarking:
   a. `pcdr4nf` value determines Physical Core to Data-plane Ratio for NF.
   b. `pcmr4nf` value determines Physical Core to Main Ratio for NF.
2. Target values to be benchmarked:
   a. pcdr4nf = [(1:1),(1:2),(1:4)].
   b. pcmr4nf = [(1:2),(1:4),(1:8)].
3. Number of physical cores required for the benchmarked NFs' service
   matrix is calculated as follows:
   *     #pc = pcdr4nf * #dnf + pcmr4nf * #mnf
   * where
   *     #pc  - total number of physical cores required and used.
   *     #dnf - total number of NF Data-plane thread sets (1 set per NF instance).
   *     #mnf - total number of NF main thread sets (1 set per per NF instance).

### NFV Service Density Matrix
Network Function View
```
Row:    1..10  number of network service instances
Column: 1..10  number of network functions per service instance
Value:  1..100 total number of network functions within node

SVC   001   002   004   006   008   010
001     1     2     4     6     8    10
002     2     4     8    12    16    20
004     4     8    16    24    32    40
006     6    12    24    36    48    60
008     8    16    32    48    64    80
010    10    20    40    60    80   100
```

Core Usage View
```
Row:          1..10 number of network service instances
Column:       1..10 number of network functions per service instance
Value:        1..NN number of physical processor cores used
Cores Numa0:  pcdr4sw = (1:1), pcmr4sw = (1:1)
              pcdr4nf = (1:1), pcmr4nf = (1:2)
Cores Numa1:  not used

SVC   001   002   004   006   008   010
001     2     3     6     9    12    15
002     3     6    12    18    24    30
004     6    12    24    36    48    60
006     9    18    36    54    72    90
008    12    24    48    72    96   120
010    15    30    60    90   120   150
```

# Service Density Benchmarks
To illustrate defined NFV service density applicability, following sections describe three NFV service topologies that have been benchmarked in open-source as part of CNCF/CNFs initiative [add ref to cncf/cnf github] and in FD.io (http://FD.io) CSIT project [add ref]. All service topologies are based on the same network topology described in the previous section.

## Test Methodology - MRR Throughput
Maximum Receive Rate (MRR) tests measure the packet forwarding rate under the maximum load
offered by traffic generator over a set trial duration, regardless of
packet loss. Maximum load for specified Ethernet frame size is set to
the bi-directional link rate.

## VNF Service Chain (VSC)
VNF Service Chain (VSC) topology with Snake Forwarding is shown in figure.

## CNF Service Chain (CSC)
CNF Service Chain (CSC) topology with Snake Forwarding
is shown in figure.

## CNF Service Pipeline (CSP)
CNF Service Pipeline (CSP) topology with Pipeline Forwarding
is shown in figure.

## Sample Results
### Testbed: FD.io (http://FD.io) CSIT 2n-skx
### Packet.net 2n-skx