## Performance Tests Job Specifications

## Scope

Following FD.io CSIT test job specifications are provided in this note:

- Select list of performance tests for daily trending and extensive per
  release test coverage (behaviour repeatibility verification, graphs,
  analytics and comparisons).
- Full list of performance tests for per release results reporting.

Next sections list test selection criteria for each group, with testbed
environments listed in round brackets (...).

## Select List Test Jobs

### NICs

- Primary: xxv710 (2n-skx, 3n-skx), xl710 (3n-hsw), x553 (3n-tsh).
- Secondary: x710 (2n-skx, 3n-skx).

### Test Suites

- Primary: all forwarding baseline, all forwarding scale, some feature
  spot checks.
- Secondary: some forwarding base, forwarding maximum scale.

### Frame Sizes

- 64B: ip4, ip4_tunnels, l2, vts, container_memif, vm_vhost.
- 78B: ip6, ip6_tunnels, srv6.
- imix: crypto, nfv_density.

### Processor Cores

- Cores: 1c, 2c, 4c.

## Full List Test Jobs
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
### Test Suite Allocation per Job

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

- Development cycle:
  - Frequency: select-list tests twice a day.
  - Times (UTC): every day starting at 02:00 and 14:00.
  - Duration: jobs are monitored to last no longer than 12hrs.
- Report cycle:
  - Frequency: select-list tests once a day.
  - Times (UTC): Mon, Wed, Fri starting at 02:00.
  - Duration: jobs are monitored to last no longer than 12hrs.

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