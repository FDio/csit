NFV Service Density
-------------------

Network Function Virtualization (NFV) service density tests focus on
measuring total per-server throughput at varied NFV service “packing”
densities, with vswitch providing host dataplane. The goal is to compare
and contrast performance of a shared vswitch across different network
topologies and virtualization technologies, and their impact on vswitch
performance and efficiency in a range of NFV service configurations.

Each NFV service instance consists of a set of Network Functions (NFs),
running in VMs (VNFs) or in Containers (CNFs). They are connected into a
virtual network topology using VPP vswitch running in Linux user-mode.
Multiple service instances share the vswitch that in turn provides
per-service chain forwarding context(s). In order to provide a most-complete
picture, each network topology and service configuration is tested in
different service density setups by varying the following two parameters:

- Number of service instances (e.g. 1,2,4..10).
- Number of NFs per service instance (e.g. 1,2,4..10).

Implementation of NFV service density tests in |csit-release| is using two NF
applications:

- VNF: VPP of the same version as vswitch running in KVM VM, configured with /8
  IPv4 prefix routing.
- CNF: VPP of the same version as vswitch running in Docker Container,
  configured with /8 IPv4 prefix routing.

Tests are designed such that in all tested cases, VPP vswitch is the most
stressed application. This is because for each flow, vswitch processes each
packet multiple times, whereas VNFs and CNFs process each packets only once.
To that end, all VNFs and CNFs are allocated enough resources to not become
a bottleneck.

Service Configurations
~~~~~~~~~~~~~~~~~~~~~~

Following NFV network topologies and configurations are tested:

- VNF Service Chains (VSC) with L2 vswitch

  - *Network Topology*: Sets of VNFs dual-homed to VPP vswitch over
    virtio-vhost links. Each set belongs to a separate service instance.
  - *Network Configuration*: VPP L2 bridge-domain contexts form logical
    service chains of VNF sets and connect each chain to physical
    interfaces.

- CNF Service Chains (CSC) with L2 vswitch

  - *Network Topology*: Sets of CNFs dual-homed to VPP vswitch over
    memif links. Each set belongs to a separate service instance.
  - *Network Configuration*: VPP L2 bridge-domain contexts form logical
    service chains of CNF sets and connect each chain to physical
    interfaces.

- CNF Service Pipelines (CSP) with L2 vswitch

  - *Network Topology*: Sets of CNFs connected into pipelines over a
    series of memif links, with edge CNFs single-homed to VPP vswitch
    over memif links. Each set belongs to a separate service instance.
  - *Network Configuration*: VPP L2 bridge-domain contexts connect each
    CNF pipeline to physical interfaces.

Thread-to-Core Mapping
~~~~~~~~~~~~~~~~~~~~~~

CSIT defines specific ratios for mapping software threads of vswitch and
VNFs/CNFs to physical cores, with separate ratios defined for main
control threads and data-plane threads.

In |csit-release|, NFV service density tests run on Intel Xeon testbeds
with Intel Hyper-Threading enabled, thus each physical core is associated
with a pair of sibling logical cores corresponding to the hyper-threads.

|csit-release| executes tests with the following mapping ratios of
software thread to physical core:

- vSwitch

  - Data-plane on single core

    - (main:core) = (1:1) => 1mt1c - 1 main thread on 1 core.
    - (data:core) = (1:1) => 2dt1c - 2 Data-plane Threads on 1 Core.

  - Data-plane on two cores

    - (main:core) = (1:1) => 1mt1c - 1 Main Thread on 1 Core.
    - (data:core) = (1:2) => 4dt2c - 4 Data-plane Threads on 2 Cores.

- VNF and CNF

  - Data-plane on single core

    - (main:core) = (2:1) => 2mt1c - 2 Main Threads on 1 Core, 1 Thread
      per NF, core shared between two NFs.
    - (data:core) = (1:1) => 2dt1c - 2 Data-plane Threads on 1 Core per
      NF.

  - Data-plane on single logical core (Two NFs per physical core)

    - (main:core) = (2:1) => 2mt1c - 2 Main Threads on 1 Core, 1 Thread
      per NF, core shared between two NFs.
    - (data:core) = (2:1) => 2dt1c - 2 Data-plane Threads on 1 Core, 1
      Thread per NF, core shared between two NFs.

Maximum tested service densities are limited by the number of physical
cores per NUMA. |csit-release| allocates cores within NUMA0. Support for
multi-NUMA tests is to be added in a future release.
