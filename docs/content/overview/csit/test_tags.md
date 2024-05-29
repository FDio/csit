---
title: "Test Tags"
weight: 4
---

# Test Tags

All CSIT test cases are labelled with Robot Framework tags used to allow for
easy test case type identification, test case grouping and selection for
execution. Following sections list currently used CSIT tags and their
descriptions.

## Testbed Topology Tags

**2_NODE_DOUBLE_LINK_TOPO**

    2 nodes connected in a circular topology with two links interconnecting
    the devices.

**2_NODE_SINGLE_LINK_TOPO**

    2 nodes connected in a circular topology with at least one link
    interconnecting devices.

**3_NODE_DOUBLE_LINK_TOPO**

    3 nodes connected in a circular topology with two links interconnecting
    the devices.

**3_NODE_SINGLE_LINK_TOPO**

    3 nodes connected in a circular topology with at least one link
    interconnecting devices.

## Objective Tags

**SKIP_PATCH**

    Test case(s) marked to not run in case of vpp-csit-verify (i.e. VPP
    patch) and csit-vpp-verify jobs (i.e. CSIT patch).

**SKIP_VPP_PATCH**

    Test case(s) marked to not run in case of vpp-csit-verify (i.e. VPP
    patch).

## Environment Tags

**HW_ENV**

    DUTs and TGs are running on bare metal.

**VM_ENV**

    DUTs and TGs are running in virtual environment.

**VPP_VM_ENV**

    DUTs with VPP and capable of running Virtual Machine.

## NIC Model Tags

**NIC_Intel-X520-DA2**

    Intel X520-DA2 NIC.

**NIC_Intel-XL710**

    Intel XL710 NIC.

**NIC_Intel-X710**

    Intel X710 NIC.

**NIC_Intel-XXV710**

    Intel XXV710 NIC.

**NIC_Cisco-VIC-1227**

    VIC-1227 by Cisco.

**NIC_Cisco-VIC-1385**

    VIC-1385 by Cisco.

**NIC_Amazon-Nitro-50G**

    Amazon EC2 ENA NIC.

## Scaling Tags

**FIB_20K**

    2x10,000 entries in single fib table

**FIB_200K**

    2x100,000 entries in single fib table

**FIB_1M**

    2x500,000 entries in single fib table

**FIB_2M**

    2x1,000,000 entries in single fib table

**L2BD_1**

    Test with 1 L2 bridge domain.

**L2BD_10**

    Test with 10 L2 bridge domains.

**L2BD_100**

    Test with 100 L2 bridge domains.

**L2BD_1K**

    Test with 1000 L2 bridge domains.

**VLAN_1**

    Test with 1 VLAN sub-interface.

**VLAN_10**

    Test with 10 VLAN sub-interfaces.

**VLAN_100**

    Test with 100 VLAN sub-interfaces.

**VLAN_1K**

    Test with 1000 VLAN sub-interfaces.

**VXLAN_1**

    Test with 1 VXLAN tunnel.

**VXLAN_10**

    Test with 10 VXLAN tunnels.

**VXLAN_100**

    Test with 100 VXLAN tunnels.

**VXLAN_1K**

    Test with 1000 VXLAN tunnels.

**TNL_{t}**

    IPSec in tunnel mode - {t} tunnels.

**SRC_USER_{u}**

    Traffic flow with {u} unique IPs (users) in one direction.
    {u}=(1,10,100,1000,2000,4000).

**100_FLOWS**

    Traffic stream with 100 unique flows (10 IPs/users x 10 UDP ports) in
    one direction.

**10k_FLOWS**

    Traffic stream with 10 000 unique flows (10 IPs/users x 1000 UDP ports)
    in one direction.

**100k_FLOWS**

    Traffic stream with 100 000 unique flows (100 IPs/users x 1000 UDP
    ports) in one direction.

**HOSTS_{h}**

    Stateless or stateful traffic stream with {h} client source IP4
    addresses, usually with 63 flow differing in source port number.
    Could be UDP or TCP. If NAT is used, the clients are inside.
    Outside IP range can differ.
    {h}=(1024,4096,16384,65536,262144).

**GENEVE4_{t}TUN**

    Test with {t} GENEVE IPv4 tunnel.
    {t}=(1,4,16,64,256,1024)

## Test Category Tags

**DEVICETEST**

    All vpp_device functional test cases.

**PERFTEST**

    All performance test cases.

## VPP Device Type Tags

**SCAPY**

    All test cases that uses Scapy for packet generation and validation.

## Performance Type Tags

**NDRPDR**

    Single test finding both No Drop Rate and Partial Drop Rate
    simultaneously. The search is done by optimized algorithm which
    performs multiple trial runs at different durations and transmit
    rates. The results come from the final trials, which have duration
    of 30 seconds.

**MRR**

    Performance tests where TG sends the traffic at maximum rate (line rate)
    and reports total sent/received packets over trial duration.
    The result is an average of 10 trials of 1 second duration.

**SOAK**

    Performance tests using PLRsearch to find the critical load.

**RECONF**

    Performance tests aimed to measure lost packets (time) when performing
    reconfiguration while full throughput offered load is applied.

## Ethernet Frame Size Tags

These are describing the traffic offered by Traffic Generator,
"primary" traffic in case of asymmetric load.
For traffic between DUTs, or for "secondary" traffic, see ${overhead} value.

**{b}B**

    {b} Bytes frames used for test.

**IMIX**

    IMIX frame sequence (28x 64B, 16x 570B, 4x 1518B) used for test.

## Test Type Tags

**BASE**

    Baseline test cases, no encapsulation, no feature(s) configured in tests.
    No scaling whatsoever, beyond minimum needed for RSS.

**IP4BASE**

    IPv4 baseline test cases, no encapsulation, no feature(s) configured in
    tests. Minimal number of routes. Other quantities may be scaled.

**IP6BASE**

    IPv6 baseline test cases, no encapsulation, no feature(s) configured in
    tests.

**L2XCBASE**

    L2XC baseline test cases, no encapsulation, no feature(s) configured in
    tests.

**L2BDBASE**

    L2BD baseline test cases, no encapsulation, no feature(s) configured in
    tests.

**L2PATCH**

    L2PATCH baseline test cases, no encapsulation, no feature(s) configured
    in tests.

**SCALE**

    Scale test cases. Other tags specify which quantities are scaled.
    Also applies if scaling is set on TG only (e.g. DUT works as IP4BASE).

**ENCAP**

    Test cases where encapsulation is used. Use also encapsulation tag(s).

**FEATURE**

    At least one feature is configured in test cases. Use also feature
    tag(s).

**UDP**

    Tests which use any kind of UDP traffic (STL or ASTF profile).

**TCP**

    Tests which use any kind of TCP traffic (STL or ASTF profile).

**TREX**

    Tests which test trex traffic without any software DUTs in the
    traffic path.

**UDP_UDIR**

    Tests which use unidirectional UDP traffic (STL profile only).

**UDP_BIDIR**

    Tests which use bidirectional UDP traffic (STL profile only).

**UDP_CPS**

    Tests which measure connections per second on minimal UDP
    pseudoconnections. This implies ASTF traffic profile is used.

**TCP_CPS**

    Tests which measure connections per second on empty TCP connections.
    This implies ASTF traffic profile is used.

**TCP_RPS**

    Tests which measure requests per second on empty TCP connections.
    This implies ASTF traffic profile is used.

**UDP_PPS**

    Tests which measure packets per second on lightweight UDP transactions.
    This implies ASTF traffic profile is used.

**TCP_PPS**

    Tests which measure packets per second on lightweight TCP transactions.
    This implies ASTF traffic profile is used.

**HTTP**

    Tests which use traffic formed of valid HTTP requests (and responses).

**LDP_NGINX**

    LDP NGINX is un-modified NGINX with VPP via LD_PRELOAD.

**NF_DENSITY**

    Performance tests that measure throughput of multiple VNF and CNF
    service topologies at different service densities.

## NF Service Density Tags

**CHAIN**

    NF service density tests with VNF or CNF service chain topology(ies).

**PIPE**

    NF service density tests with CNF service pipeline topology(ies).

**NF_L3FWDIP4**

    NF service density tests with DPDK l3fwd IPv4 routing as NF workload.

**NF_VPPIP4**

    NF service density tests with VPP IPv4 routing as NF workload.

**{r}R{c}C**

    Service density matrix locator {r}R{c}C, {r}Row denoting number of
    service instances, {c}Column denoting number of NFs per service
    instance.
    {r}=(1,2,4,6,8,10), {c}=(1,2,4,6,8,10).

**{n}VM{t}T**

    Service density {n}VM{t}T, {n}Number of NF Qemu VMs, {t}Number of
    threads per NF.

**{n}DCR{t}T**

    Service density {n}DCR{t}T, {n}Number of NF Docker containers,
    {t}Number of threads per NF.

**{n}_ADDED_CHAINS**

    {n}Number of chains (or pipelines) added (and/or removed)
    during RECONF test.

## Forwarding Mode Tags

**L2BDMACSTAT**

    VPP L2 bridge-domain, L2 MAC static.

**L2BDMACLRN**

    VPP L2 bridge-domain, L2 MAC learning.

**L2XCFWD**

    VPP L2 point-to-point cross-connect.

**IP4FWD**

    VPP IPv4 routed forwarding.

**IP6FWD**

    VPP IPv6 routed forwarding.

**LOADBALANCER_MAGLEV**

    VPP Load balancer maglev mode.

**LOADBALANCER_L3DSR**

    VPP Load balancer l3dsr mode.

**LOADBALANCER_NAT4**

    VPP Load balancer nat4 mode.

**N2N**

    Mode, where NICs from the same physical server are directly
    connected with a cable.

## Underlay Tags

**IP4UNRLAY**

    IPv4 underlay.

**IP6UNRLAY**

    IPv6 underlay.

**MPLSUNRLAY**

    MPLS underlay.

## Overlay Tags

**L2OVRLAY**

    L2 overlay.

**IP4OVRLAY**

    IPv4 overlay (IPv4 payload).

**IP6OVRLAY**

    IPv6 overlay (IPv6 payload).

## Tagging Tags

**DOT1Q**

    All test cases with dot1q.

**DOT1AD**

    All test cases with dot1ad.

## Encapsulation Tags

**ETH**

    All test cases with base Ethernet (no encapsulation).

**LISP**

    All test cases with LISP.

**LISPGPE**

    All test cases with LISP-GPE.

**LISP_IP4o4**

    All test cases with LISP_IP4o4.

**LISPGPE_IP4o4**

    All test cases with LISPGPE_IP4o4.

**LISPGPE_IP6o4**

    All test cases with LISPGPE_IP6o4.

**LISPGPE_IP4o6**

    All test cases with LISPGPE_IP4o6.

**LISPGPE_IP6o6**

    All test cases with LISPGPE_IP6o6.

**VXLAN**

    All test cases with Vxlan.

**VXLANGPE**

    All test cases with VXLAN-GPE.

**GRE**

    All test cases with GRE.

**GTPU**

    All test cases with GTPU.

**GTPU_HWACCEL**

    All test cases with GTPU_HWACCEL.

**IPSEC**

    All test cases with IPSEC.

**WIREGUARD**

    All test cases with WIREGUARD.

**SRv6**

    All test cases with Segment routing over IPv6 dataplane.

**SRv6_1SID**

    All SRv6 test cases with single SID.

**SRv6_2SID_DECAP**

    All SRv6 test cases with two SIDs and with decapsulation.

**SRv6_2SID_NODECAP**

    All SRv6 test cases with two SIDs and without decapsulation.

**GENEVE**

    All test cases with GENEVE.

**GENEVE_L3MODE**

    All test cases with GENEVE tunnel in L3 mode.

**FLOW**

    All test cases with FLOW.

**FLOW_DIR**

    All test cases with FLOW_DIR.

**FLOW_RSS**

    All test cases with FLOW_RSS.

**NTUPLE**

    All test cases with NTUPLE.

**L2TPV3**

    All test cases with L2TPV3.

**REASSEMBLY**

    All encap/decap tests where MTU induces IP fragmentation and reassembly.

## Interface Tags

**PHY**

    All test cases which use physical interface(s).

**GSO**

    All test cases which uses Generic Segmentation Offload.

**VHOST**

    All test cases which uses VHOST.

**VHOST_1024**

    All test cases which uses VHOST DPDK driver with qemu queue size set
    to 1024.

**VIRTIO**

    All test cases which uses VIRTIO native VPP driver.

**VIRTIO_1024**

    All test cases which uses VIRTIO native VPP driver with qemu queue 
    size set to 1024.

**CFS_OPT**

    All test cases which uses VM with optimised scheduler policy.

**TUNTAP**

    All test cases which uses TUN and TAP.

**AFPKT**

    All test cases which uses AFPKT.

**NETMAP**

    All test cases which uses Netmap.

**MEMIF**

    All test cases which uses Memif.

**SINGLE_MEMIF**

    All test cases which uses only single Memif connection per DUT. One DUT
    instance is running in container having one physical interface exposed
    to container.

**LBOND**

    All test cases which uses link bonding (BondEthernet interface).

**LBOND_DPDK**

    All test cases which uses DPDK link bonding.

**LBOND_VPP**

    All test cases which uses VPP link bonding.

**LBOND_MODE_XOR**

    All test cases which uses link bonding with mode XOR.

**LBOND_MODE_LACP**

    All test cases which uses link bonding with mode LACP.

**LBOND_LB_L34**

    All test cases which uses link bonding with load-balance mode l34.

**LBOND_{n}L**

    All test cases which use {n} link(s) for link bonding.

**DRV_{d}**

    All test cases which NIC Driver for DUT is set to {d}.
    Default is VFIO_PCI.
    {d}=(AVF, RDMA_CORE, VFIO_PCI, AF_XDP).

**TG_DRV_{d}**

    All test cases which NIC Driver for TG is set to {d}.
    Default is IGB_UIO.
    {d}=(RDMA_CORE, IGB_UIO).

**RXQ_SIZE_{n}**

    All test cases which RXQ size (RX descriptors) are set to {n}.
    Default is 0, which means VPP (API) default.

**TXQ_SIZE_{n}**

    All test cases which TXQ size (TX descriptors) are set to {n}.
    Default is 0, which means VPP (API) default.

## Feature Tags

**IACLDST**

    iACL destination.

**ADLALWLIST**

    ADL allowlist.

**NAT44**

    NAT44 configured and tested.

**NAT64**

    NAT44 configured and tested.

**ACL**

    ACL plugin configured and tested.

**IACL**

    ACL plugin configured and tested on input path.

**OACL**

    ACL plugin configured and tested on output path.

**ACL_STATELESS**

    ACL plugin configured and tested in stateless mode
    (permit action).

**ACL_STATEFUL**

    ACL plugin configured and tested in stateful mode
    (permit+reflect action).

**ACL1**

    ACL plugin configured and tested with 1 not-hitting ACE.

**ACL10**

    ACL plugin configured and tested with 10 not-hitting ACEs.

**ACL50**

    ACL plugin configured and tested with 50 not-hitting ACEs.

**SRv6_PROXY**

    SRv6 endpoint to SR-unaware appliance via proxy.

**SRv6_PROXY_STAT**

    SRv6 endpoint to SR-unaware appliance via static proxy.

**SRv6_PROXY_DYN**

    SRv6 endpoint to SR-unaware appliance via dynamic proxy.

**SRv6_PROXY_MASQ**

    SRv6 endpoint to SR-unaware appliance via masquerading proxy.

## Encryption Tags

**IPSECSW**

    Crypto in software.

**IPSECHW**

    Crypto in hardware.

**IPSECTRAN**

    IPSec in transport mode.

**IPSECTUN**

    IPSec in tunnel mode.

**IPSECINT**

    IPSec in interface mode.

**AES**

    IPSec using AES encrytion algorithms.

**AES_128_CBC**

    IPSec using AES 128 CBC algorithms.

**AES_128_CTR**

    IPSec using AES 128 CTR algorithms.

**AES_128_GCM**

    IPSec using AES 128 GCM algorithms.

**AES_128_NULL_GMAC**

    IPSec using AES 128 NULL GMAC algorithms.

**AES_256_CBC**

    IPSec using AES 256 CBC algorithms.

**AES_256_GCM**

    IPSec using AES 256 GCM algorithms.

**AES_256_NULL_GMAC**

    IPSec using AES 256 NULL GMAC algorithms.

**HMAC**

    IPSec using HMAC integrity/authorization algorithms.

**HMAC_SHA_96**

    IPSec using HMAC SHA 96 integrity algorithms.

**HMAC_SHA_256**

    IPSec using HMAC SHA 256 integrity algorithms.

**HMAC_SHA_512**

    IPSec using HMAC SHA 512 integrity algorithms.

**UDP_ENCAP**

    Encapsulate IPsec traffic in UDP.

**ANTI_REPLAY**

    Enable IPsec Anti-Replay functionality.

**SCHEDULER**

    IPSec using crypto sw scheduler engine.

**FASTPATH**

    IPSec policy mode with spd fast path enabled.

## Client-Workload Tags

**VM**

    All test cases which use at least one virtual machine.

**LXC**

    All test cases which use Linux container and LXC utils.

**DRC**

    All test cases which use at least one Docker container.

**DOCKER**

    All test cases which use Docker as container manager.

**APP**

    All test cases with specific APP use.

## Container Orchestration Tags

**{n}VSWITCH**

    {n} VPP running in {n} Docker container(s) acting as a VSWITCH.
    {n}=(1).

**{n}VNF**

    {n} VPP running in {n} Docker container(s) acting as a VNF work load.
    {n}=(1).

## Multi-Threading Tags

**STHREAD**

    Dynamic tag.
    All test cases using single poll mode thread.

**MTHREAD**

    Dynamic tag.
    All test cases using more then one poll mode driver thread.

**{n}NUMA**

    All test cases with packet processing on {n} socket(s). {n}=(1,2).

**{c}C**

    {c} worker thread pinned to {c} dedicated physical core; or if
    HyperThreading is enabled, {c}*2 worker threads each pinned to
    a separate logical core within 1 dedicated physical core. Main
    thread pinned to core 1.
    {t}=(1,2,4).

**{t}T{c}C**

    *Dynamic tag*.
    {t} worker threads pinned to {c} dedicated physical cores. Main thread
    pinned to core 1. By default CSIT is configuring same amount of receive
    queues per interface as worker threads. 
    {t}=(1,2,4,8),
    {c}=(1,2,4).
