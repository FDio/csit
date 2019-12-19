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

<!-- List as alternative to table
- 2n-clx
  - Primary: xxv710-avf, xxv710-dpdk, mlx5-rdmacore.
  - Secondary: x710-avf, x710-dpdk.
- 2n-skx
  - Primary: xxv710-avf, xxv710-dpdk.
  - Secondary: x710-avf, x710-dpdk.
- 3n-skx
  - Primary: xxv710-avf, xxv710-dpdk.
  - Secondary: x710-avf, x710-dpdk.
- 3n-hsw
  - Primary: xl710-dpdk.
  - Secondary: none.
- 3n-tsh
  - Primary: x553-dpdk.
  - Secondary: none.
- 2n-dnv
  - Primary: x553-dpdk.
  - Secondary: none.
- 3n-dnv
  - Primary: x553-dpdk.
  - Secondary: none.
-->

- avf: tests with VPP native AVF driver for Intel Fortville NICs.
- dpdk: tests with VPP DPDK driver for Intel Fortville NICs.
- rdmacore: tests with VPP native RDMA-CORE driver for Mellanox
  ConnectX5 NICs.

### Test Combinations

Primary and secondary test sets are defined for the following test
suite, frame size and multi-core combinations:

<!-- TODO Turn sections below into a table. -->

- Test Suites
  - Primary: all forwarding baseline, all forwarding scale, baseline feature path tests.
  - Secondary: part of forwarding base, forwarding maximum scale.
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

#### Primary
##### container_memif

dot1q-l2bdbasemaclrn-eth-2memif-1dcr
ethip4-ip4base-eth-2memif-1dcr
eth-l2bdbasemaclrn-eth-2memif-1dcr

##### crypto

ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
ethip4ipsec1000tnlhw-ip4base-int-aes128cbc-hmac512sha
ethip4ipsec1000tnlhw-ip4base-int-aes256gcm
ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
ethip4ipsec400tnlsw-ip4base-int-aes128cbc-hmac512sha
ethip4ipsec400tnlsw-ip4base-int-aes256gcm

##### ip4

dot1q-ip4base
ethip4-ip4base
ethip4-ip4scale200k
ethip4-ip4scale20k
ethip4-ip4scale2m
ethip4udp-ip4base-iacl50sf-100flows
ethip4udp-ip4base-iacl50sf-100kflows
ethip4udp-ip4base-iacl50sl-100flows
ethip4udp-ip4base-iacl50sl-100kflows
ethip4udp-ip4base-nat44
ethip4udp-ip4base-oacl50sf-100flows
ethip4udp-ip4base-oacl50sf-100kflows
ethip4udp-ip4base-oacl50sl-100flows
ethip4udp-ip4base-oacl50sl-100kflows
ethip4udp-ip4base-udpsrcscale15-nat44
ethip4udp-ip4scale10-udpsrcscale15-nat44
ethip4udp-ip4scale1000-udpsrcscale15-nat44
ethip4-ip4scale200k-rnd
ethip4-ip4scale20k-rnd
ethip4-ip4scale2m-rnd

##### ip4_tunnels

dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan
dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan
ethip4lispip4-ip4base
ethip4lispip6-ip4base
ethip4vxlan-l2bdbasemaclrn
ethip4vxlan-l2xcbase

##### ip6

dot1q-ip6base
ethip6-ip6base
ethip6-ip6scale200k
ethip6-ip6scale20k
ethip6-ip6scale2m
ethip6-ip6base-iacldstbase
- rnd?

##### ip6_tunnels

##### l2

dot1q-l2bdbasemaclrn
eth-l2bdbasemaclrn
eth-l2patch
eth-l2xcbase
dot1q-l2xcbase
eth-l2bdbasemaclrn-iacl50sf-100flows
eth-l2bdbasemaclrn-iacl50sf-100kflows
eth-l2bdbasemaclrn-iacl50sl-100flows
eth-l2bdbasemaclrn-iacl50sl-100kflows
eth-l2bdbasemaclrn-macip-iacl50sl-100flows
eth-l2bdbasemaclrn-macip-iacl50sl-100kflows
eth-l2bdbasemaclrn-oacl50sf-100flows
eth-l2bdbasemaclrn-oacl50sf-100kflows
eth-l2bdbasemaclrn-oacl50sl-100flows
eth-l2bdbasemaclrn-oacl50sl-100kflows
eth-l2bdscale100kmaclrn
eth-l2bdscale10kmaclrn
eth-l2bdscale1mmaclrn
dot1q-l2bdbasemaclrn-gbp

##### lb

##### nfv_density

##### srv6

##### tcp

##### vm_vhost

##### vts

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