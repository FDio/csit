## Performance Tests Job Specifications

## Scope

This note includes FD.io CSIT test specifications for the following
Jenkins test job groups:

- **Trending Daily Set** of tests for daily performance trending and
  verification.
- **Trending Weekly Set** of tests for weekly performance trending and
  verification.
- **Report Extensive Set** of tests for per release extensive performance
  coverage (64B/IMIX repeatibility verification, throughput / multi-core
  / latency graphs and comparisons).
- **Report Full Set** of tests for per release detailed performance
  results reporting.

Next sections list per job group test case selection criteria and the
motivation behind this selection for each of the physical testbed
environments hosted in LFN FD.io labs.

## Trending Daily Set

Daily test jobs are executed twice a day (every 12 hours), therefore
their total execution time must be less than 12 hours. This restricts
number of tests that can be executed per each job run. We took approach
of defining a primary and secondary sub-sets of tests, with the former
receiving a larger test coverage compared to the latter.

The sub-sets are defined on a per testbed type basis, due to different
number of physical instances per type (more instances enable higher
degree of parallel execution).

Note that the primary and secondary sub-sets of a daily set do not cover
all tests productized in CSIT simply due to insufficient time budget
available.


### Testbed-NIC-Driver Combinations

Primary and secondary sub-sets of Testbed-NIC-Driver combinations are
listed below.

- 2n-clx
  - Primary: xxv710-avf (see Note-1), xxv710-dpdk (see Note-2),
    (TODO) mlx4-rdmacore (see Note-3).
  - Secondary: x710-avf (see Note-1), x710-dpdk (see Note-2).
- 2n-skx
  - Primary: xxv710-avf, xxv710-dpdk.
  - Secondary: x710-avf, x710-dpdk.
- 3n-skx
  - Primary: xxv710-avf, xxv710-dpdk.
  - Secondary: x710-avf, x710-dpdk.
- 3n-hsw
  - Primary: xl710-avf, xl710-dpdk.
- 3n-tsh
  - Primary: x553-dpdk.
- 2n-dnv
  - Primary: (TODO).
- 3n-dnv
  - Primary: (TODO).

Note-1: xxv710-avf, x710-avf use VPP native AVF driver for Fortville
i40e NICs.

Note-2: xxv710-dpdk, x710-dpdk use VPP DPDK driver for Fortville i40e
NICs.

Note-3: mlx4-rdmacore use VPP native RDMA-CORE driver for Mellanox
ConnectX4 NICs.

### Test Cases

Test cases are selected from a set of listed test suite categories,
frame sizes and core combinations.

#### Test Suites

- Primary: all forwarding baseline, all forwarding scale, part of feature
  path tests.
- Secondary: part of forwarding base, forwarding maximum scale.

### Frame Sizes

- 64B: ip4, ip4_tunnels, l2, vts, container_memif, vm_vhost.
- 78B: ip6, ip6_tunnels, srv6.
- imix: crypto, nfv_density.
- 1518B: crypto.

### Processor Cores

- Cores: 1c, 2c, 4c.

## (Editor note: Below sections are TODO - pls review only until this
   line!)

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

## END OF DOCUMENT