---
title: "Job Triggering"
weight: 6
---

# Job Triggering

... or how to run the tests.

The trigger consist of
  - trigger name,
  - tags (optional),
  - trigger parameters for the suite generator (optional) - each parameter
    starts with the hash tag "#" and parameters are separated by the white
    space.

## On-demand jobs

### Report

Both iterative and coverage jobs are triggered by user from github action panel.

#### Iterative jobs

Default values:
  - iterative test set - the same as it is used for periodical jobs
  - test type: mrr

Mandatory workflow parameters:
  - no mandatory parameters - default values are used in that case

Optional workflow parameters:
  - test set
  - test type

Examples:

1. <no input>
   - Generates default test set and default test type.

2. #ndrpdr
   - Generates default test set and ndrpdr tests.

3. #2n-emr-vpp-hoststack

   #2n-emr-vpp-hoststack #hoststack
   - Generates hoststack test set.
   - It is not necessary to specify the test type as it is defined in the name
     of the test set, so both examples are equal and correct.

#### Coverage jobs

Default values:
  - test type: ndrpdr

Mandatory workflow parameters:
  - test set

Optional workflow parameters:
  - test type, default value: ndrpdr

Examples:

1. #2n-emr-vpp-cov-ip4-00
   - Generates the defined test set, ndrpdr tests.

### Development

#### Verify jobs

Trigger name:
  - gha-run csit-`dut`-`node`-`arch` perftest `tags`

Default values:
  - iterative test set - the same as it is used for periodical jobs
  - test type: mrr

Mandatory trigger parameters:
  - no mandatory parameters - default values are used in that case

Optional trigger parameters:
  - test set
  - test type

Examples:

1. gha-run csit-vpp-2n-emr perftest `tags`
   - Generates iterative mrr tests, runs only those selected by tags.

2. gha-run csit-vpp-2n-emr perftest `tags` #2n-emr-vpp-cov-ip4-00 #ndrpdr
   - Generates defined test set, ndrpdr tests, runs only those selected by tags.

#### Bisect jobs

Trigger name:
  - gha-run csit-`dut`-`node`-`arch` bisecttest `commit` `tags`

Default values:
  - iterative test set - the same as it is used for periodical jobs
  - test type: mrr

Mandatory trigger parameters:
  - no mandatory parameters - default values are used in that case

Optional trigger parameters:
  - test set
  - test type

Examples:

1. gha-run csit-vpp-2n-emr bisecttest `commit` `tags`
   - Generates iterative mrr tests, runs only those selected by tags.

2. gha-run csit-vpp-2n-emr bisecttest `commit` `tags` #2n-emr-vpp-cov-ip4-00 #ndrpdr
   - Generates defined test set, ndrpdr tests, runs only those selected by tags.

#### Special cases

##### Tox

If the job name includes the string "tox", all tests defined in all test sets
are generated. Tox job does not run any tests.

##### generate-all

If the string "generate-all" is in the trigger, all tests defined in all test
sets for the given testbed are generated.

This can be used with verify or bisect jobs if you do not know which test set
includes required test(s). Be careful and use proper tags to specify the
test(s).

Examples:

1. gha-run csit-vpp-2n-emr perftest `tags` #generate-all
   - Generates all tests specified in all test sets for 2n-emr testbed, runs
     only those selected by tags.

1. gha-run csit-vpp-2n-emr bisecttest `commit` `tags` #generate-all
   - Generates all tests specified in all test sets for 2n-emr testbed, runs
     only those selected by tags.

## Periodical jobs

The user does not use these jobs as they are periodicaly triggered by Jenkins.
