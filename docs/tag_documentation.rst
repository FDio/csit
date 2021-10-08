CSIT Tags
=========

All CSIT test cases are labelled with Robot Framework tags used to allow for
easy test case type identification, test case grouping and selection for
execution. Following sections list currently used CSIT tags and their
descriptions.

Testbed Topology Tags
---------------------

.. topic:: 2_NODE_DOUBLE_LINK_TOPO

    2 nodes connected in a circular topology with two links interconnecting
    the devices.

.. topic:: 2_NODE_SINGLE_LINK_TOPO

    2 nodes connected in a circular topology with at least one link
    interconnecting devices.

.. topic:: 3_NODE_DOUBLE_LINK_TOPO

    3 nodes connected in a circular topology with two links interconnecting
    the devices.

.. topic:: 3_NODE_SINGLE_LINK_TOPO

    3 nodes connected in a circular topology with at least one link
    interconnecting devices.

Objective Tags
--------------

.. topic:: SKIP_PATCH

    Test case(s) marked to not run in case of vpp-csit-verify (i.e. VPP patch)
    and csit-vpp-verify jobs (i.e. CSIT patch).

.. topic:: SKIP_VPP_PATCH

    Test case(s) marked to not run in case of vpp-csit-verify (i.e. VPP patch).

Environment Tags
----------------

.. topic:: HW_ENV

    DUTs and TGs are running on bare metal.

.. topic:: VM_ENV

    DUTs and TGs are running in virtual environment.

.. topic:: VPP_VM_ENV

    DUTs with VPP and capable of running Virtual Machine.

NIC Model Tags
--------------

.. topic:: NIC_Intel-X520-DA2

    Intel X520-DA2 NIC.

.. topic:: NIC_Intel-XL710

    Intel XL710 NIC.

.. topic:: NIC_Intel-X710

    Intel X710 NIC.

.. topic:: NIC_Intel-XXV710

    Intel XXV710 NIC.

.. topic:: NIC_Cisco-VIC-1227

    VIC-1227 by Cisco.

.. topic:: NIC_Cisco-VIC-1385

    VIC-1385 by Cisco.

.. topic:: NIC_Amazon-Nitro-50G

    Amazon EC2 ENA NIC.

Scaling Tags
------------

.. topic:: FIB_20K

    2x10,000 entries in single fib table

.. topic:: FIB_200K

    2x100,000 entries in single fib table

.. topic:: FIB_2M

    2x1,000,000 entries in single fib table

.. topic:: L2BD_1

    Test with 1 L2 bridge domain.

.. topic:: L2BD_10

    Test with 10 L2 bridge domains.

.. topic:: L2BD_100

    Test with 100 L2 bridge domains.

.. topic:: L2BD_1K

    Test with 1000 L2 bridge domains.

.. topic:: VLAN_1

    Test with 1 VLAN sub-interface.

.. topic:: VLAN_10

    Test with 10 VLAN sub-interfaces.

.. topic:: VLAN_100

    Test with 100 VLAN sub-interfaces.

.. topic:: VLAN_1K

    Test with 1000 VLAN sub-interfaces.

.. topic:: VXLAN_1

    Test with 1 VXLAN tunnel.

.. topic:: VXLAN_10

    Test with 10 VXLAN tunnels.

.. topic:: VXLAN_100

    Test with 100 VXLAN tunnels.

.. topic:: VXLAN_1K

    Test with 1000 VXLAN tunnels.

.. topic:: TNL_{t}

    IPSec in tunnel mode - {t} tunnels.

.. topic:: SRC_USER_{u}

    Traffic flow with {u} unique IPs (users) in one direction.
    {u}=(1,10,100,1000,2000,4000).

.. topic:: 100_FLOWS

    Traffic stream with 100 unique flows (10 IPs/users x 10 UDP ports) in one
    direction.

.. topic:: 10k_FLOWS

    Traffic stream with 10 000 unique flows (10 IPs/users x 1000 UDP ports) in
    one direction.

.. topic:: 100k_FLOWS

    Traffic stream with 100 000 unique flows (100 IPs/users x 1000 UDP ports) in
    one direction.

.. topic:: HOSTS_{h}

    Stateless or stateful traffic stream with {h} client source IP4 addresses,
    usually with 63 flow differing in source port number. Could be UDP or TCP.
    If NAT is used, the clients are inside. Outside IP range can differ.
    {h}=(1024,4096,16384,65536,262144).

.. topic:: GENEVE4_{t}TUN

    Test with {t} GENEVE IPv4 tunnel. {t}=(1,4,16,64,256,1024)

Test Category Tags
------------------

.. topic:: DEVICETEST

    All vpp_device functional test cases.

.. topic:: PERFTEST

    All performance test cases.

VPP Device Type Tags
--------------------

.. topic:: SCAPY

    All test cases that uses Scapy for packet generation and validation.

Performance Type Tags
---------------------

.. topic:: NDRPDR

    Single test finding both No Drop Rate and Partial Drop Rate simultaneously.
    The search is done by optimized algorithm which performs
    multiple trial runs at different durations and transmit rates.
    The results come from the final trials, which have duration of 30 seconds.

.. topic:: MRR

    Performance tests where TG sends the traffic at maximum rate (line rate)
    and reports total sent/received packets over trial duration.
    The result is an average of 10 trials of 1 second duration.

.. topic:: SOAK

    Performance tests using PLRsearch to find the critical load.

.. topic:: RECONF

    Performance tests aimed to measure lost packets (time) when performing
    reconfiguration while full throughput offered load is applied.

Ethernet Frame Size Tags
------------------------

These are describing the traffic offered by Traffic Generator,
"primary" traffic in case of asymmetric load.
For traffic between DUTs, or for "secondary" traffic, see ${overhead} value.

.. topic:: {b}B

    {b} Bytes frames used for test.

.. topic:: IMIX

    IMIX frame sequence (28x 64B, 16x 570B, 4x 1518B) used for test.

Test Type Tags
--------------

.. topic:: BASE

    Baseline test cases, no encapsulation, no feature(s) configured in tests.
    No scaling whatsoever, beyond minimum needed for RSS.

.. topic:: IP4BASE

    IPv4 baseline test cases, no encapsulation, no feature(s) configured in
    tests. Minimal number of routes. Other quantities may be scaled.

.. topic:: IP6BASE

    IPv6 baseline test cases, no encapsulation, no feature(s) configured in
    tests.

.. topic:: L2XCBASE

    L2XC baseline test cases, no encapsulation, no feature(s) configured in
    tests.

.. topic:: L2BDBASE

    L2BD baseline test cases, no encapsulation, no feature(s) configured in
    tests.

.. topic:: L2PATCH

    L2PATCH baseline test cases, no encapsulation, no feature(s) configured in
    tests.

.. topic:: SCALE

    Scale test cases. Other tags specify which quantities are scaled.
    Also applies if scaling is set on TG only (e.g. DUT works as IP4BASE).

.. topic:: ENCAP

    Test cases where encapsulation is used. Use also encapsulation tag(s).

.. topic:: FEATURE

    At least one feature is configured in test cases. Use also feature tag(s).

.. topic:: UDP

    Tests which use any kind of UDP traffic (STL or ASTF profile).

.. topic:: TCP

    Tests which use any kind of TCP traffic (STL or ASTF profile).

.. topic:: TREX

    Tests which test trex traffic without any software DUTs in the traffic path.

..
    TODO: Should we define tags STL and ASTF?

.. topic:: UDP_UDIR

    Tests which use unidirectional UDP traffic (STL profile only).

.. topic:: UDP_BIDIR

    Tests which use bidirectional UDP traffic (STL profile only).

.. topic:: UDP_CPS

    Tests which measure connections per second on minimal UDP pseudoconnections.
    This implies ASTF traffic profile is used.
    This tag selects specific output processing in PAL.

.. topic:: TCP_CPS

    Tests which measure connections per second on empty TCP connections.
    This implies ASTF traffic profile is used.
    This tag selects specific output processing in PAL.

.. topic:: TCP_RPS

    Tests which measure requests per second on empty TCP connections.
    This implies ASTF traffic profile is used.
    This tag selects specific output processing in PAL.

.. topic:: UDP_PPS

    Tests which measure packets per second on lightweight UDP transactions.
    This implies ASTF traffic profile is used.
    This tag selects specific output processing in PAL.

.. topic:: TCP_PPS

    Tests which measure packets per second on lightweight TCP transactions.
    This implies ASTF traffic profile is used.
    This tag selects specific output processing in PAL.

.. topic:: HTTP

    Tests which use traffic formed of valid HTTP requests (and responses).

..
    TODO: Add HTTP tag to the current hoststack tests.
    TODO: Document other tags already used by hoststack tests.

.. topic:: LDP_NGINX

    LDP NGINX is un-modified NGINX with VPP via LD_PRELOAD.

.. topic:: NF_DENSITY

    Performance tests that measure throughput of multiple VNF and CNF
    service topologies at different service densities.

NF Service Density Tags
-----------------------

.. topic:: CHAIN

    NF service density tests with VNF or CNF service chain topology(ies).

.. topic:: PIPE

    NF service density tests with CNF service pipeline topology(ies).

.. topic:: NF_L3FWDIP4

    NF service density tests with DPDK l3fwd IPv4 routing as NF workload.

.. topic:: NF_VPPIP4

    NF service density tests with VPP IPv4 routing as NF workload.

.. topic:: {r}R{c}C

    Service density matrix locator {r}R{c}C, {r}Row denoting number of
    service instances, {c}Column denoting number of NFs per service
    instance. {r}=(1,2,4,6,8,10), {c}=(1,2,4,6,8,10).

.. topic:: {n}VM{t}T

    Service density {n}VM{t}T, {n}Number of NF Qemu VMs, {t}Number of threads
    per NF.

.. topic:: {n}DCRt}T

    Service density {n}DCR{t}T, {n}Number of NF Docker containers, {t}Number of
    threads per NF.

.. topic:: {n}_ADDED_CHAINS

    {n}Number of chains (or pipelines) added (and/or removed)
    during RECONF test.

Forwarding Mode Tags
--------------------

.. topic:: L2BDMACSTAT

    VPP L2 bridge-domain, L2 MAC static.

.. topic:: L2BDMACLRN

    VPP L2 bridge-domain, L2 MAC learning.

.. topic:: L2XCFWD

    VPP L2 point-to-point cross-connect.

.. topic:: IP4FWD

    VPP IPv4 routed forwarding.

.. topic:: IP6FWD

    VPP IPv6 routed forwarding.

.. topic:: LOADBALANCER_MAGLEV

    VPP Load balancer maglev mode.

.. topic:: LOADBALANCER_L3DSR

    VPP Load balancer l3dsr mode.

.. topic:: LOADBALANCER_NAT4

    VPP Load balancer nat4 mode.

.. topic:: N2N

    Mode, where NICs from the same physical server are directly
    connected with a cable.

Underlay Tags
-------------

.. topic:: IP4UNRLAY

    IPv4 underlay.

.. topic:: IP6UNRLAY

    IPv6 underlay.

.. topic:: MPLSUNRLAY

    MPLS underlay.

Overlay Tags
------------

.. topic:: L2OVRLAY

    L2 overlay.

.. topic:: IP4OVRLAY

    IPv4 overlay (IPv4 payload).

.. topic:: IP6OVRLAY

    IPv6 overlay (IPv6 payload).

Tagging Tags
------------

.. topic:: DOT1Q

    All test cases with dot1q.

.. topic:: DOT1AD

    All test cases with dot1ad.

Encapsulation Tags
------------------

.. topic:: ETH

    All test cases with base Ethernet (no encapsulation).

.. topic:: LISP

    All test cases with LISP.

.. topic:: LISPGPE

    All test cases with LISP-GPE.

.. topic:: LISP_IP4o4

    All test cases with LISP_IP4o4.

.. topic:: LISPGPE_IP4o4

    All test cases with LISPGPE_IP4o4.

.. topic:: LISPGPE_IP6o4

    All test cases with LISPGPE_IP6o4.

.. topic:: LISPGPE_IP4o6

    All test cases with LISPGPE_IP4o6.

.. topic:: LISPGPE_IP6o6

    All test cases with LISPGPE_IP6o6.

.. topic:: VXLAN

    All test cases with Vxlan.

.. topic:: VXLANGPE

    All test cases with VXLAN-GPE.

.. topic:: GRE

    All test cases with GRE.

.. topic:: GTPU

    All test cases with GTPU.

.. topic:: IPSEC

    All test cases with IPSEC.

.. topic:: SRv6

    All test cases with Segment routing over IPv6 dataplane.

.. topic:: SRv6_1SID

    All SRv6 test cases with single SID.

.. topic:: SRv6_2SID_DECAP

    All SRv6 test cases with two SIDs and with decapsulation.

.. topic:: SRv6_2SID_NODECAP

    All SRv6 test cases with two SIDs and without decapsulation.

.. topic:: GENEVE

    All test cases with GENEVE.

.. topic:: GENEVE_L3MODE

    All test cases with GENEVE tunnel in L3 mode.

.. topic:: FLOW

    All test cases with FLOW.

.. topic:: NTUPLE

    All test cases with NTUPLE.

.. topic:: L2TPV3

    All test cases with L2TPV3.

Interface Tags
--------------

.. topic:: PHY

    All test cases which use physical interface(s).

.. topic:: GSO

    All test cases which uses Generic Segmentation Offload.

.. topic:: VHOST

    All test cases which uses VHOST.

.. topic:: VHOST_1024

    All test cases which uses VHOST DPDK driver with qemu queue size set
    to 1024.

.. topic:: VIRTIO

    All test cases which uses VIRTIO native VPP driver.

.. topic:: VIRTIO_1024

    All test cases which uses VIRTIO native VPP driver with qemu queue size set
    to 1024.

.. topic:: CFS_OPT

    All test cases which uses VM with optimised scheduler policy.

.. topic:: TUNTAP

    All test cases which uses TUN and TAP.

.. topic:: AFPKT

    All test cases which uses AFPKT.

.. topic:: NETMAP

    All test cases which uses Netmap.

.. topic:: MEMIF

    All test cases which uses Memif.

.. topic:: SINGLE_MEMIF

    All test cases which uses only single Memif connection per DUT. One DUT
    instance is running in container having one physical interface exposed to
    container.

.. topic:: LBOND

    All test cases which uses link bonding (BondEthernet interface).

.. topic:: LBOND_DPDK

    All test cases which uses DPDK link bonding.

.. topic:: LBOND_VPP

    All test cases which uses VPP link bonding.

.. topic:: LBOND_MODE_XOR

    All test cases which uses link bonding with mode XOR.

.. topic:: LBOND_MODE_LACP

    All test cases which uses link bonding with mode LACP.

.. topic:: LBOND_LB_L34

    All test cases which uses link bonding with load-balance mode l34.

.. topic:: LBOND_{n}L

    All test cases which use {n} link(s) for link bonding.

.. topic:: DRV_{d}

    All test cases which NIC Driver for DUT is set to {d}. Default is VFIO_PCI.
    {d}=(AVF, RDMA_CORE, VFIO_PCI, AF_XDP).

.. topic:: TG_DRV_{d}

    All test cases which NIC Driver for TG is set to {d}. Default is IGB_UIO.
    {d}=(RDMA_CORE, IGB_UIO).

.. topic:: RXQ_SIZE_{n}

    All test cases which RXQ size (RX descriptors) are set to {n}. Default is 0,
    which means VPP (API) default.

.. topic:: TXQ_SIZE_{n}

    All test cases which TXQ size (TX descriptors) are set to {n}. Default is 0,
    which means VPP (API) default.

Feature Tags
------------

.. topic:: IACLDST

    iACL destination.

.. topic:: ADLALWLIST

    ADL allowlist.

.. topic:: NAT44

    NAT44 configured and tested.

.. topic:: NAT64

    NAT44 configured and tested.

.. topic:: ACL

    ACL plugin configured and tested.

.. topic:: IACL

    ACL plugin configured and tested on input path.

.. topic:: OACL

    ACL plugin configured and tested on output path.

.. topic:: ACL_STATELESS

    ACL plugin configured and tested in stateless mode (permit action).

.. topic:: ACL_STATEFUL

    ACL plugin configured and tested in stateful mode (permit+reflect action).

.. topic:: ACL1

    ACL plugin configured and tested with 1 not-hitting ACE.

.. topic:: ACL10

    ACL plugin configured and tested with 10 not-hitting ACEs.

.. topic:: ACL50

    ACL plugin configured and tested with 50 not-hitting ACEs.

.. topic:: SRv6_PROXY

    SRv6 endpoint to SR-unaware appliance via proxy.

.. topic:: SRv6_PROXY_STAT

    SRv6 endpoint to SR-unaware appliance via static proxy.

.. topic:: SRv6_PROXY_DYN

    SRv6 endpoint to SR-unaware appliance via dynamic proxy.

.. topic:: SRv6_PROXY_MASQ

    SRv6 endpoint to SR-unaware appliance via masquerading proxy.

Encryption Tags
---------------

.. topic:: IPSECSW

    Crypto in software.

.. topic:: IPSECHW

    Crypto in hardware.

.. topic:: IPSECTRAN

    IPSec in transport mode.

.. topic:: IPSECTUN

    IPSec in tunnel mode.

.. topic:: IPSECINT

    IPSec in interface mode.

.. topic:: AES

    IPSec using AES algorithms.

.. topic:: AES_128_CBC

    IPSec using AES 128 CBC algorithms.

.. topic:: AES_128_GCM

    IPSec using AES 128 GCM algorithms.

.. topic:: AES_256_GCM

    IPSec using AES 256 GCM algorithms.

.. topic:: HMAC

    IPSec using HMAC integrity algorithms.

.. topic:: HMAC_SHA_256

    IPSec using HMAC SHA 256 integrity algorithms.

.. topic:: HMAC_SHA_512

    IPSec using HMAC SHA 512 integrity algorithms.

.. topic:: SCHEDULER

    IPSec using crypto sw scheduler engine.

Client-Workload Tags
--------------------

.. topic:: VM

    All test cases which use at least one virtual machine.

.. topic:: LXC

    All test cases which use Linux container and LXC utils.

.. topic:: DRC

    All test cases which use at least one Docker container.

.. topic:: DOCKER

    All test cases which use Docker as container manager.

.. topic:: APP

    All test cases with specific APP use.

Container Orchestration Tags
----------------------------

.. topic:: {n}VSWITCH

    {n} VPP running in {n} Docker container(s) acting as a VSWITCH.
    {n}=(1).

.. topic:: {n}VNF

    {n} VPP running in {n} Docker container(s) acting as a VNF work load.
    {n}=(1).

Multi-Threading Tags
--------------------

.. topic:: STHREAD

   *Dynamic tag*.
   All test cases using single poll mode thread.

.. topic:: MTHREAD

   *Dynamic tag*.
    All test cases using more then one poll mode driver thread.

.. topic:: {n}NUMA

    All test cases with packet processing on {n} socket(s). {n}=(1,2).

.. topic:: {c}C

    {c} worker thread pinned to {c} dedicated physical core; or if
    HyperThreading is enabled, {c}*2 worker threads each pinned to a separate
    logical core within 1 dedicated physical core. Main thread pinned to core 1.
    {t}=(1,2,4).

.. topic:: {t}T{c}C

   *Dynamic tag*.
    {t} worker threads pinned to {c} dedicated physical cores. Main thread
    pinned to core 1. By default CSIT is configuring same amount of receive
    queues per interface as worker threads. {t}=(1,2,4,8), {t}=(1,2,4).
