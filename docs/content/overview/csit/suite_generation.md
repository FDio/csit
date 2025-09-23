---
title: "Suite Generation"
weight: 5
---

# Suite Generation

The suite generator generates the test suites defined in the specification files
and chosen by command-line parameters.

## Input

The mandatory input information is:
1. **Job name** (string). The test suites are generated for this job. Only one job
   can be specified.
2. **Directory** to store generated tests.

The optional or mandatory input information, depending on the job type, is:

3. **Trigger parameters** (string). Mandatory for on-demand jobs (iterative,
   coverage, bisect, ...). This string includes information directly from the
   gerrit trigger. To distinguish between information for the Robot (e.g. tags),
   the information for the suite generator starts with the hash tag #. E.g.:

   csit-vpp-report-iter-2n-aws-perftest #2n-aws-vpp-iterative #ndrpdr

   If we include all neccessary information to this string, we do not need to
   use "Test set" and "Test type" parameters described below.
4. Test set (string). Mandatory for on-demand jobs (iterative, coverage, bisect,
   ...). Specifies the tests to run. Only one test set can be specified.
   If the test set is not specified as command-line parameter, it must be
   specified in the specification file.
5. Test type (string). Mandatory for some of on-demand jobs. Only one test type
   from this list can be specified:
   - mrr,
   - ndrpdr,
   - hoststack
   - soak.

The optional input information is (if it is not provided, the values specified
in constants.py are used):

6. Output directory (string). Directory to store generated files. If not given,
   the default directory is used.
7. Output file name (string). The name of output file for transformed and
   expanded yaml file to json. If not given, the default name is used.
8. Create JSON file (boolean). If set, the processed specification will be
   writen to the output directory as a JSON file. The default value is "False".
9.  Logging level (string). One of "NOTSET", "DEBUG", "INFO", "WARNING", "ERROR",
   "CRITICAL". The default value is "INFO".

## Output

The output is:
1. A directory structure with generated tests, suites and other necessary files
   to run tests using Robot Framework.
2. Optionaly the JSON file with expaned specification.

The return code is:
- 0 - if everything is OK,
- 1 - if anything went wrong.

## Job specification

The jobs are specified in the specification YAML files. There are at least three
files specifying:
1. test groups (test_groups.yaml)
2. test sets (ts_topo-arch.yaml)
3. jobs (jobs.yaml)

The default location is the directory `resources/job_specifications/`.

### Test groups

The test group is a named list of tests defined by their test tags. It is the
elementary part of the job specification.

Size of a test group:

| Name        | Abbreviation | Size    |
|-------------|--------------|---------|
| small       |           sm |  1 -  2 |
| medium      |           md |  3 -  4 |
| large       |           lg |  5 -  8 |
| extra large |           xl |  9 - 16 |
| 2x large    |          xxl | 17 - 32 |

It is not recommended to use 2xl or larger test groups.

Example:

```
  trex-ip4-sm:
    - ethip4-ip4base-tg
    - ethip4-ip4scale20k-tg
  trex-nat44-cps-md:
    - ethip4tcp-ip4base-h1024-p63-s64512-cps-tg
    - ethip4tcp-ip4base-h262144-p63-s16515072-cps-tg
    - ethip4tcp-ip4base-h1024-p63-s64512-cps-tg
    - ethip4tcp-ip4base-h262144-p63-s16515072-cps-tg
```

### Test sets

A test set consists of:
- test parameters (infra, core, framesize) and
- test groups, optionally with test parameters.

The test parameters are:
- number of cores (list),
- framesize (list or dictionary),
- infrastructure - NIC and driver (dictionary).

The test parameters can be defined for the whole test set and/or for each test
group separately.

Examples:

1. Definition of parameters

```
  2n-aws-vpp-iterative:
    core: [1, 2]
    framesize: [64, 1518]
    infra:
      nitro-50g:
        - vfio-pci
    tests:
      - ip4-sm
      - ip6-sm:
          framesize: [78, 1518]
      - l2-md
```

In this example, parameters defined outside `tests` (core, framesize, infra)
are valid for all test groups listed in `tests`, but parameters defined directly
for a test group (ip6-sm in this example) are valid only for this test group and
overwrite parameters defined for the whole test set.

2. Parameters defined outside of test sets

```
  2n-spr-dpdk-iterative:
    tests:
      - dpdk-small
```

In this example, no parameters are defined, so parameters defined in the section
`jobs` are used.

3. Driver not defined

```
  2n-spr-trex-iterative:
    infra:
      100ge2p1e810cq:
        - "-"
      200ge2p1cx7veat:
        - "-"
    tests:
      - trex-ip4-sm
      - trex-nat44-cps-md
      - trex-nat44-tput-md:
          framesize: [100, ]
      - trex-ip6-sm:
          framesize: [78, ]
      - trex-l2-sm
```

In this example, no drivers ("-") are defined as these tests do not need them to
specify.

4. Cores not defined

```
  csit-trex-perf-report-coverage-{stream}-{node-arch}:
    stream:
      - "2506"
    test-type: ndrpdr
    framesize: [64, 1518, 9000, "imix"]
    core: ["-", ]
    node-arch:
      - 2n-icx: 2n-icx-trex-coverage
      - 2n-spr: 2n-spr-trex-coverage
```

In this example, no cores ("-") are defined as these tests do not need them to
specify.

5. Extended "framesize" parameter

```
  2n-emr-vpp-cov-ip6-00:
    infra:
      100ge2p1e810cq:
        - avf
        - vfio-pci
    framesize:
      - 78
      - 1518: [1, 2]
      - 9000: [1, ]
      - imix
    tests:
      - ip6-acl-md
```

If we need to run limited or extended number of cores for particular framesize,
we can specify them as a list for chosen framesize. In this example:

framesize:
  - `78`             Cores defined in the job will be applied.
  - `1518: [1, 2]`   Only [1, 2] cores will be aplied.
  - `9000: [1, ]`    Only [1, ] core will be aplied.
  - `imix`           Cores defined in the job will be applied.

For more examples, see the specification yaml files. 

### Jobs

A job consists of:
- job parameters
  - test-type (string),
  - stream (list),
  - node-arch (list),
  - ... any other.
- global test parameters, see above.

A special parameter is the `node-arch` which assignes a test set to the
testbed. It is a list of testbeds defined for the job. The items can be strings
or dictionaries:

```
node-arch:
  - 2n-icx,
  - 2n-spr: 2n-spr-vpp-iterative
```

- The testbed `2n-icx` is defined for this job but without a test set. The test
  set MUST be specified as a command-line parameter. This approach is typical
  for on-demand jobs (iterative, coverage, verify, etc) which can run more then
  one test set.
- The testbed `2n-spr` is defined for this job with a test set. This test set
  CAN be changed by a command-line parameter. This approach is used with
  periodical (daily and weekly) jobs as they run always the same test set.

Examples:

1. daily, weekly

```
  csit-vpp-perf-mrr-daily-master-{node-arch}:
    test-type: mrr
    framesize:
      - 64b
    core: [1, 2, 4]
    node-arch:
      - 2n-icx: 2n-icx-vpp-iterative
      - 2n-spr: 2n-spr-vpp-iterative
      - 2n-zn2: 2n-zn2-vpp-iterative
      - 3n-alt: 3n-alt-vpp-iterative
      - 3n-icx: 3n-icx-vpp-iterative
      - 3n-icxd: 3n-icxd-vpp-iterative
      - 3n-snr: 3n-snr-vpp-iterative
      - 3na-spr: 3na-spr-vpp-iterative
      - 3nb-spr: 3nb-spr-vpp-iterative
```

In this example, we defined 9 jobs, one for each item in the `node-arch` list.

There are four parameters to completly define a test. One of them, `test-type`,
is always common for all tests, so it is defined in the job specification.
The rest, `core`, `framesize` and `infra` can vary from test to test, but all
must be defined, no matter on which level (job, test set).

2. iterative

```
  csit-vpp-perf-report-iterative-{stream}-{node-arch}:
    stream:
      - "2502"
      - "2410"
    framesize:
      - 64
    core: [1, 2, 4]
    node-arch:
      - 2n-aws: 2n-aws-vpp-iterative
      - 2n-c6in: 2n-c6in-vpp-iterative
      - 2n-c7gn: 2n-c7gn-vpp-iterative
      - 2n-icx
      - 2n-spr
      - 2n-zn2
      - 3n-alt
      - 3n-icx
      - 3n-icxd
      - 3n-snr
      - 3na-spr
      - 3nb-spr: 3nb-spr-vpp-iterative
```

In this example, we defined 24 jobs as each `node-arch` has two `stream`s.
Four items in `node-arch` list have assigned their test sets (they can be
re-defined by command-line argument) and the rest must be assigned by
command-line argument.

### Processing of the specification

There are three levels of specification:
1. jobs - top level
2. tests-sets
3. test-groups - bottom level

The specification is processed from top to down and only for required job
specified by the command line parameter.
The test set specified in the job is replaced by its definition, and the test
groups in it are replaced by their definitions. Then we set all parameters
(`test-type`, `core`, `framesize` and `infra`) for each test, again, from top to
down, overwriting top values by bottom values. So, if e.g. framesize is
specified on all levels, the lowest one is used.

## Triggering

The Suite generator is launched from Jenkins / Github Actions either as a
periodical job (daily, weekly, ...) or on-demand job (iterative, coverage,
verify, bisect, ...).

### Periodical jobs

Main characteristics:
- no trigger,
- detected "daily" or "weekly" in the job name,
- job name e.g.: csit-dpdk-perf-mrr-weekly-master-2n-grc.

Parameters:
- job-name - mandatory.

Robot Framework parameters (relevant to Suite generator):
- directory with generated tests
- runs all tests

Example:

1. Periodical jobs

```
./suite_generator.py --gen-tests-dir generated --job csit-trex-perf-ndrpdr-weekly-master-2n-spr
./suite_generator.py --gen-tests-dir generated --job csit-vpp-perf-mrr-daily-master-2n-icx
```

Generates tests for the job "csit-trex-perf-ndrpdr-weekly-master-2n-spr" and
stores them in "generated" directory.
As these jobs are periodical jobs, no more parameters are needed.

### On-demand jobs

Main characteristics:
- started by a gerrit trigger, examples of currently used triggers:
  - jobs for the report:
    - csit-vpp-report-iter-2n-aws-perftest `test-set`
    - csit-dpdk-report-iter-2n-icx-perftest `test-set`
    - csit-vpp-report-cov-2n-aws-perftest `test-set`
    - csit-vpp-report-cov-2n-icx-perftest `test-set`
  - verify jobs:
    - csit-2n-zn2-perftest `tags`
  - bisect jobs:
    - bisecttest-2n-spr d35f7f098 `tags`
- job name, e.g.:
  - report:
    - csit-dpdk-perf-report-coverage-2410-2n-icx
  - verify:
    - csit-vpp-perf-verify-master-2n-zn2
  - bisect:
    - vpp-csit-bisect-master-ubuntu2404-x86_64-2n-spr

Parameters:
- job-name - mandatory
- test-set - optional
  - Mandatory for iterative and coverage jobs.
  - By default all verify and bisect jobs use "iterative" test set
  - If needed, one of "coverage" test sets can be specified as command line
    parameter.
- test-type - optional
  - Default: mrr
  - If needed, test type can be specified as command line parameter.

Robot Framework parameters (relevant to Suite generator):
- directory with tests
- set of tags for verify and bisect jobs

Examples:

```
./suite_generator.py --gen-tests-dir generated --job csit-vpp-perf-report-iterative-2506-2n-icx
./suite_generator.py --gen-tests-dir generated --job csit-vpp-perf-report-iterative-2506-2n-icx --test-type ndrpdr
./suite_generator.py --gen-tests-dir generated --job csit-vpp-perf-report-coverage-2506-2n-spr --test-set 2n-spr-vpp-cov-ip4-00
```
