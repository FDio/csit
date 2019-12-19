## Performance Tests Job Specifications

## Scope

This note includes FD.io CSIT test specifications for the following
Jenkins test job groups:

- **Trending Daily** group of performance tests for daily MRR trending
  and contiuous verification.

- **Trending Weekly** group of performance tests for weekly MRR, NDR,
  PDR trending and contiuous verification.

- **Report Iterative** group of performance tests for per release
  iterative test execution and analysis including results
  repeatibility (stdev), multi-core linearity, latency percentile
  graphs.

- **Report Coverage** group of performance tests covering all working
  test combinations for target platforms.

Next sections describe test case selection criteria for each job group.

The number of physical testbed instances hosted in FD.io CSIT labs
varies per testbed type, enabling different degrees of parallel test
execution.  Therefore test sets are defined on a per testbed type basis.

## Trending Daily

Daily test jobs are executed twice a day (every 12 hours), therefore
their total execution time must be less than 12 hours. This restricts
number of tests that can be executed per each job run. We took approach
of defining a primary and secondary test sets, with the former
receiving a larger test coverage compared to the latter.

### NIC and Driver Combinations

Primary and secondary NIC-driver combinations are defined per testbed
type.

Testbed type | Primary                              | Secondary
-------------|--------------------------------------|-------------------
2n-clx       | xxv710-avf,xxv710-dpdk,mlx5-rdmacore | x710-avf,x710-dpdk
2n-skx       | xxv710-avf,xxv710-dpdk               | x710-avf,x710-dpdk
3n-skx       | xxv710-avf,xxv710-dpdk               | x710-avf,x710-dpdk
3n-hsw       | xl710-dpdk                           | none
3n-tsh       | x553-dpdk                            | none
2n-dnv       | x553-dpdk                            | none
3n-dnv       | x553-dpdk                            | none

- avf: tests with VPP native AVF driver for Intel Fortville NICs.
- dpdk: tests with VPP DPDK driver for Intel Fortville NICs.
- rdmacore: tests with VPP native RDMA-CORE driver for Mellanox
  ConnectX5 NICs.

### Test Combinations

Primary and secondary test sets are defined for the following test
suite, frame size and multi-core combinations:

<!-- TODO Turn sections below into a table. -->

- Suite Groups
- Frame Sizes
  - Primary:
    - 64B: ip4, ip4_tunnels, l2, vts, container_memif, vm_vhost.
    - 78B: ip6, ip6_tunnels, srv6.
    - imix: crypto.
    - 1518B: crypto.
  - Secondary:
    - 64B: ip4, l2.
    - 78B: ip6.
- Processor Cores
  - Primary: 1c, 2c, 4c.
  - Secondary: 1c, 2c, 4c.

#### Suite Groups
<!-- TODO Below proposal of suite group tags for job selection -->
[2nt|3nt]-fwg-[bsl|scl|scm|sch]
  2nt - 2-node testbed
  3nt - 3-node testbed
  fwg - forwarding L2, IPv4, IPv6
  bsl - baseline, 2-10 entries
  scl - scale low, 10k-20k entries
  scm - scale medium, 100k-200k entries
  sch - scale high, 1m-2m entries

3nt-cry-[isa|qat]-[int|spd]-[gcm-cbc]-[bsl|scl|scm|sch]
  3nt - 3-node testbed
  cry - crypto IPsec
  isa - software instruction set architecture for crypto
  qat - hardware Quick Assist Technology PCIe card for crypto
  int - IPsec tunnel interface
  spd - IPsec policy with Security Policy Database
  gcm - Galois/Counter Mode mode of operation
  cbc - Cipher Block Chaining mode of operation
  bsl - baseline, 1-4 tunnels
  scl - scale low, 40-400 tunnels
  scm - scale medium, 1k-10k tunnels
  sch - scale high, 20k-60k tunnels

3nt-tun-fwg-[bsl|scl]
  3nt - 3-node testbed
  tun - tunnel IPv4, IPv6
  fwg - forwarding L2, IPv4, IPv6
  bsl - baseline, 1-10 tunnels
  scl - scalelow, 100-1k tunnels

[2nt|3nt]-fwg-vmv-[bsl|enc]
  2nt - 2-node testbed
  3nt - 3-node testbed
  fwg - L2, IPv4 forwarding
  vmv - vm vhost
  bsl - baseline untagged only
  enc - encapsulations including dot1q, lbvpplacp, vxlan

[2nt|3nt]-fwg-ctm-[bsl|enc]
  2nt - 2-node testbed
  3nt - 3-node testbed
  fwg - L2, IPv4 forwarding
  ctm - container memif
  bsl - baseline untagged only
  enc - encapsulations including dot1q

2nt-[ssc|ssp]-ctm-ip4-[bsl|scl|scm|sch]
  2nt - 2-node testbed
  ssc - switched-L2 service chain
  ssp - switched-L2 service pipeline
  ctm - container memif
  ip4 - vpp ip4 in container
  bsl - baseline, 1 service [ssc|ssp], 1-2 containers
  scl - scale low, 1 service [ssc|ssp], 4-10 containers
  scm - scale medium, 2-4 services [ssc|ssp], 2-24 containers
  sch - scale high, 6-10 services [ssc|ssp], 6-24 containers

2nt-ssc-ctm-cry-[bsl|scl|scm|sch]
  2nt - 2-node testbed
  ssc - switched-L2 service chain
  ctm - container memif
  cry - vpp IPsec ISA GCM crypto in container
  bsl - baseline, 4 tunnels
  scl - scale low, 40-400 tunnels
  scm - scale medium, 1k-10k tunnels
  sch - scale high, 20k-60k tunnels

2nt-ssc-vmv-ip4-[bsl|scl|scm|sch]
  2nt - 2-node testbed
  ssc - switched-L2 service chain
  vmv - vm vhost
  ip4 - vpp ip4 in container
  bsl - baseline, 1 service sch, 1-2 VMs
  scl - scale low, 1 service sch, 4-10 VMs
  scm - scale medium, 2-4 services sch, 2-24 VMs
  sch - scale high, 6-10 services sch, 6-24 VMs

2nt-tun-ssc-vmv-l2x-[bsl|scl|scm|sch|rcf]
  2nt - 2-node testbed
  tun - IPv4 tunnel VXLAN
  ssc - switched-L2 service chain
  vmv - vm vhost
  l2x - L2 cross-connect with dpdk testpmd in VM
  bsl - baseline, 1 service sch, 1-2 VMs
  scl - scale low, 1 service sch, 4-10 VMs
  scm - scale medium, 2-4 services sch, 2-24 VMs
  sch - scale high, 6-10 services sch, 6-24 VMs
  rcf - reconfig tests

3nt-fwg-[acl|mip]-[bsl|scl|scm]
  3nt - 3-node testbed
  fwg - forwarding L2, IPv4, IPv6
  acl - input and output access-control-list
  mip - mac ip acl
  bsl - baseline, 1 acl, 100-100kflows
  scl - scale low, 10 acl, 100-100k flows
  scm - scale medium, 50 acl, 100-100k flows

3nt-fwg-nat-[bsl|scl|scm|sch]
  3nt - 3-node testbed
  fwg - forwarding L2, IPv4, IPv6
  nat - NAT44 address translation
  bsl - baseline, 1 user
  scl - scale low, 10-100 users
  scm - scale medium, 1k-4k users

3nt-fwg-vts-bsl
  3nt - 3-node testbed
  fwg - L2 forwarding
  vts - IPv4 VXLAN tunnel with iacl VTS profiles
  bsl - baseline

3nt-sr6-fwg-[enc|pxy]
  3nt - 3-node testbed
  sr6 - SRv6 encapsulation
  fwg - forwarding IPv6
  enc - srv6 sid encapsulation, decapsulation
  pxy - srv6 proxy modes with container memifs

2nt-lba-bsl
  2nt - 2-node testbed
  lba - load-balancer
  bsl - baseline l3dsr, maglev, nat4 modes

2nt-tcphttp-bsl
  2nt - 2-node testbed
  tcphttp - tcp http tests with vpp built-in http test loop server
  bsl - baseline cps and rps tests

[2n|3nt]-fwg-fea-bsl
  2nt - 2-node testbed
  3nt - 3-node testbed
  fwg - forwarding L2, IPv4, IPv6
  fea - other features including COP-whitelist, iacl-destination, ipolicer
  bsl - baseline

<!-- Below content is to be updated

## Full Set of Test Jobs
### NICs

- Primary: xxv710 (2n-skx, 3n-skx), xl710 (3n-hsw), x553 (3n-tsh).
- Secondary: x520 (3n-hsw), x710 (skx, hsw), vic1227 (3n-hsw), vic1385
  (3n-hsw).

### Test Suites

- Primary: all tests.
- Secondary: some forwarding base, forwarding maximum scale.

### Frame Sizes

- 64B: ip4, ip4_tunnels, l2, vts, container_memif, vm_vhost, crypto.
- 78B: ip6, ip6_tunnels, srv6.
- imix: all including crypto and nfv_density.
- 1518B: ip4, ip4_tunnels, ip6, ip6_tunnels, srv6, l2, vts,
  container_memif, vm_vhost, crypto.
- 9000B: ip4, ip4_tunnels, ip6, ip6_tunnels, srv6, l2, vts,
  container_memif, vm_vhost, crypto.
  - no vic1227, no vic1385 due to lack of support for 9000B.

### Processor Cores

  - Cores: 1c, 2c, 4c.

## Test Job Definitions
### Test Suite Selection per Job

In order to avoid multi-day jobs executing the tests, following is a
simple approach to split tests across exclusive job executions:

- Separate jobs per (testbed environment, nic model, test-directory)
- Each job executes tests for:
  - All specified frame sizes.
  - All specified cores.

### Report Jobs

Patches defining RF Tag Selectors for each group are:

- select-list: https://gerrit.fd.io/r/c/csit/+/21146
  - Execution frequency: 10 times for report.
- full-list: https://gerrit.fd.io/r/c/csit/+/21438
  - Incomplete definition.
  - Execution frequency: Once for report.
- nfv_density: https://gerrit.fd.io/r/c/csit/+/21361
  - Execution frequency: 5..10 times for report.
- tcp: https://gerrit.fd.io/r/c/csit/+/21456
  - Execution frequency: 10 times for report.

### Daily Trending Jobs

Frequency of executing daily trending jobs differs between the
development cycle and report generation cycle. In the latter case the
frequency gets reduced in order to allocated more of a (limited)
physical testbed resource to tests required for report and reduce the
time required to complete data collection for report.

- Daily tests
  - Development cycle:
    - Frequency: vpp select-list MRR tests twice a day.
    - Times (UTC): every day starting at 02:00 and 14:00.
    - Duration: jobs are monitored to last no longer than 12 hrs.
  - Report cycle:
    - Frequency: vpp select-list MRR tests once a day.
    - Times (UTC): every Monday and Thursday starting at 02:00.
    - Duration: jobs are monitored to last no longer than 12 hrs.
- Weekly tests
  - Development cycle:
    - Frequency: dpdk tests and vpp select-list NDR/PDR (MLRsearch) tests once a week.
    - Times (UTC): every Sunday at 02:00.
    - Duration: jobs are monitored to last no longer than 24 hrs.
  - Report cycle:
    - Same as in development cycle.

## Exceptions
### Tests Failing Due to Known Issues

- KernelVM: 9000B frames are failing
  - https://jira.fd.io/browse/CSIT-1532

## TODOs

- Add test types
  - mlrsearch
  - mrr
  - plrsearch
  - http/tcp
  - nfvdensity
    - vpp-ip4
    - vpp-ipsec

- Analyse trending testbed load - PM, MK
  - 3x 3n-hsw
  - 2x 3n-skx
    - tunnel tests only
  - 4x 2n-skx

- Future
  - Add weekly ndrpdr jobs and report-like comparisons to previous release

-->