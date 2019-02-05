NFV Service Density
-------------------

Network Function Virtualization (NFV) service density tests focus on
measuring total per server throughput at varied NFV service “packing”
densities with vswitch providing host dataplane. The goal is to compare
and contrast performance of a shared vswitch for different network
topologies and virtualization technologies, and their impact on vswitch
performance and efficiency in a range of NFV service configurations.

Each NFV service instance consists of a set of Network Functions (NFs),
running in VMs (VNFs) or in Containers (CNFs), that are connected into a
virtual network topology using VPP vswitch running in Linux user-mode.
Multiple service instances share the vswitch that in turn provides per
service chain forwarding context(s). In order to provide a most complete
picture, each network topology and service configuration is tested in
different service density setups by varying two parameters:

- Number of service instances (e.g. 1,2,4..10).
- Number of NFs per service instance (e.g. 1,2,4..10).

The initial implementation of NFV service density tests in
|csit-release| is using two NF applications:

- VNF: DPDK L3fwd running in KVM VM, configured with /8 IPv4 prefix
  routing. L3fwd got chosen as a lightweight fast IPv4 VNF application,
  and follows CSIT approach of using DPDK sample applications in VMs for
  performance testing.
- CNF: VPP running in Docker Container, configured with /24 IPv4 prefix
  routing. VPP got chosen as a fast IPv4 NF application that supports
  required memif interface (L3fwd does not). This is similar to all
  other Container tests in CSIT that use VPP.

Tests are designed such that in all tested cases VPP vswitch is the most
stressed application, as for each flow vswitch is processing each packet
multiple times, whereas VNFs and CNFs process each packets only once. To
that end, all VNFs and CNFs are allocated enough resources to not become
a bottleneck.

Service Configurations
~~~~~~~~~~~~~~~~~~~~~~

Following NFV network topologies and service configurations are tested:

- VNF Service Chains (VSC) with L2 vswitch

  - *Network Topology*: Sets of VNFs dual-homed to VPP vswitch over
    virtio-vhost links. Each set belongs to separate service instance.
  - *Service Configuration*: VPP L2 bridge-domain contexts form logical
    service chains of VNF sets and connect each chain to physical
    interfaces.

- CNF Service Chains (CSC) with L2 vswitch

  - *Network Topology*: Sets of CNFs dual-homed to VPP vswitch over
    memif links. Each set belongs to separate service instance.
  - *Service Configuration*: VPP L2 bridge-domain contexts form logical
    service chains of CNF sets and connect each chain to physical
    interfaces.

- CNF Service Pipelines (CSP) with L2 vswitch

  - *Network Topology*: Sets of CNFs connected into pipelines over a
    series of memif links, with edge CNFs single-homed to VPP vswitch
    over memif links. Each set belongs to separate service instance.
  - *Service Configuration*: VPP L2 bridge-domain contexts connect each
    CNF pipeline to physical interfaces.

Core Mapping Ratios
~~~~~~~~~~~~~~~~~~~

CSIT defines specific ratios for mapping physical cores (with associated
pair of sibling logical cores) to software threads of vSwitch and
VNFs/CNFs, with separate ratios defined for main control threads and
data-plane threads.

Following core mapping ratios are tested in |csit-release|:

- vSwitch

  - (core:data) = (1:1), (2:1)
  - (core:main) = (1:1)

- VNF and CNF

  - (core:data) = (1:1)
  - (core:main) = (1:2)

Maximum tested service densities are limited by a number of physical
cores per NUMA. |csit-release| allocates cores within NUMA0. Support for
multi NUMA tests is to be added in future release.