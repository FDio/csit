#!/usr/bin/python3

# Copyright (c) 2025 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
===============
Suite Generator
===============

The suite generator generates the test suites defined in the specification file
and chosen by command-line parameters.

Input
=====

The mandatory input information is:
1. Job name (string). The test suites are generated for this job. Only one job
   can be specified.
2. Directory to store generated tests.

The optional or mandatory input information, depending on the job type, is:
3. Test set (string). Mandatory for on-demand jobs (iterative, coverage, bisect,
   ...). Specifies the tests to run. Only one test set can be specified.
   If the test set is not specified as command-line parameter, it must be
   specified in the specification file.
4. Test type (string). Mandatory for some of on-demand jobs. Only one test type
   from this list can be specified:
   - mrr,
   - ndrpdr,
   - hoststack
   - soak.

The optional input information is (if it is not provided, the values specified
in constants.py are used):
5. Output directory (string). Directory to store generated files. If not given,
   the default directory is used.
6. Output file name (string). The name of output file:
   - transformed and expanded yaml file to json.
   If not given, the default name is used.
6. Create JSON file (boolean). If set, the processed specification will be
   writen to the output directory as a JSON file.
7. Logging level (string). One of "NOTSET", "DEBUG", "INFO", "WARNING", "ERROR",
   "CRITICAL". The default value is "INFO".

Output
======

The output is:
1. A directory structure with generated tests, suites and other necessary files
   to run tests using Robot Framework.
2. Optionaly the JSON file with expaned specification.

The return code is:
0 - if everything is OK,
1 - if anything went wrong.

Job specification
=================

The jobs are specified in the specification YAML files. There are three files
specifying:
1. test groups (test_groups.yaml)
2. test sets (test_sets.yaml)
3. jobs (jobs.yaml)
The default location is the directory `resources/job_specifications/`.

Test groups
-----------

The test group is a named list of tests defined by their test tag. It is the
elementary part of the job specification.

Size of a test group:

+-------------+--------------+---------+
| Name        | Abbreviation | Size    |
+=============+==============+=========+
| small       |           sm |  1 -  2 |
| medium      |           md |  3 -  4 |
| large       |           lg |  5 -  8 |
| extra large |           xl |  9 - 16 |
| 2x large    |          xxl | 17 - 32 |
+-------------+--------------+---------+

Example:

  trex-ip4-sm:
    - ethip4-ip4base-tg
    - ethip4-ip4scale20k-tg
  trex-nat44-cps-md:
    - ethip4tcp-ip4base-h1024-p63-s64512-cps-tg
    - ethip4tcp-ip4base-h262144-p63-s16515072-cps-tg
    - ethip4tcp-ip4base-h1024-p63-s64512-cps-tg
    - ethip4tcp-ip4base-h262144-p63-s16515072-cps-tg

Test sets
---------

A test set consists of:
- test parameters (infra, core, framesize) and
- test groups, optionally with test parameters.

The test parameters are:
- number of cores (list),
- framesize (list),
- infrastructure - NIC and driver (dictionary).

The test parameters can be defined for the whole test set and/or for each test
group separately.

Examples:

1. Definition of parameters

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

In this example, parameters defined outside `tests` (core, framesize, infra)
are valid for all test groups listed in `tests`, but parameters defined directly
for a test group (ip6-sm in this example) are valid only for this test group and
overwrite parameters defined for the test set.

2. Parameters defined outside of test sets

  2n-spr-dpdk-iterative:
    tests:
      - dpdk-small

In this example, no parameters are defined, so parameters defined in the section
`jobs` are used.

3. Driver not defined

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

In this example, no drivers ("-") are defined as these tests do not need them to
specify.

4. Cores not defined

  csit-trex-perf-report-coverage-{stream}-{node-arch}:
    stream:
      - "2506"
    test-type: ndrpdr
    framesize: [64, 1518, 9000, "imix"]
    core: ["-", ]
    node-arch:
      - 2n-icx: 2n-icx-trex-coverage
      - 2n-spr: 2n-spr-trex-coverage

In this example, no cores ("-") are defined as these tests do not need them to
specify.

5. Extended "framesize" parameter

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

If we need to run limited or extended number of cores for particular framesize,
we can specify them as a list for chosen framesize. In this example:

framesize:
  - 78             Cores defined in the job will be applied.
  - 1518: [1, 2]   Only [1, 2] cores will be aplied.
  - 9000: [1, ]    Only [1, ] core will be aplied.
  - imix           Cores defined in the job will be applied.

For more examples, see the specification yaml files. 

Jobs
----

A job consists of:
- job parameters
  - test-type (string),
  - stream (list),
  - node-arch (list),
  - ... any other.
- global test parameters, see above.

A special parameter is the `node-arch` whitch asignes a test set to the testbed.
It is a list of testbeds defined for the job. The items can be strings or
dictionaries:

    "node-arch": [
        "2n-icx",
        {
            "2n-spr": "2n-spr-vpp-iterative"
        }
    ]

- The testbed `2n-icx` is defined for this job but without a test set. The test
  set must be specified as a command-line parameter. This approach is typical
  for iterative, coverage, verify, etc jobs which can run more then one test
  set.
- The testbed `2n-spr` is defined for this job with a test set. This test set
  can be changed by a command-line parameter. This approach is used with daily
  and weekly jobs as they run always the same test set.

Examples:

1. daily, weekly

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

In this example, we defined 9 jobs, one for each item in the `node-arch` list.

There are four parameters to completly define a test. One of them, `test-type`,
is always common for all tests, so it is defined in the job specification.
The rest, `core`, `framesize` and `infra` can vary from test to test, but all
must be defined, no matter on which level (job, test set).

2. iterative

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

In this example, we defined 24 jobs as each `node-arch` has two `stream`s.
Four items in `node-arch` list have assigned their test sets (they can be
re-defined by command-line argument) and the rest must be assigned by
command-line argument.

Processing of the specification
-------------------------------

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

Triggering
==========

The Suite generator is launched from Jenkins / Github Actions either as a
periodical job (daily, weekly, ...) or on-demand job (iterative, coverage,
verify, bisect, ...).

Periodical jobs
---------------

Main characteristics:
- no trigger,
- detected "daily" or "weekly" in the job name,
- job name e.g.: csit-dpdk-perf-mrr-weekly-master-2n-grc.

Parameters:
- job-name - mandatory.
- test-set - optional, the test-set must be specified in the specification,
  if provided, it is replaced.
- test-type - optional, the test-type must be specified in the specification,
  if provided, it is replaced.

Robot Framework parameters (relevant to Suite generator):
- directory with generated tests
- runs all tests

Example:

1. Periodical jobs

./suite_generator.py --gen-tests-dir generated --job csit-trex-perf-ndrpdr-weekly-master-2n-spr
./suite_generator.py --gen-tests-dir generated --job csit-vpp-perf-mrr-daily-master-2n-icx

Generates tests for the job "csit-trex-perf-ndrpdr-weekly-master-2n-spr" and
stores them in "generated" directory.
As these jobs are periodical jobs, no more parameters are needed.

On-demand jobs
--------------

Main characteristics:
- started by a gerrit trigger, examples of currently used triggers:
  - jobs for the report:
    - csit-vpp-report-iter-2n-aws-perftest vpp-mrr-00
    - csit-dpdk-report-iter-2n-icx-perftest dpdk-ndrpdr-00
    - csit-vpp-report-cov-2n-aws-perftest vpp-00
    - csit-vpp-report-cov-2n-icx-perftest ip4-05
  - verify jobs:
    - csit-2n-zn2-perftest <tags>
    - vpp-csit-verify-perf-master-ubuntu2404-aarch64-2n-grc <tags>
  - bisect jobs:
    - bisecttest-2n-spr d35f7f098 <tags>
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

1.

./suite_generator.py --gen-tests-dir generated --job csit-vpp-perf-report-iterative-2506-2n-icx
./suite_generator.py --gen-tests-dir generated --job csit-vpp-perf-report-iterative-2506-2n-icx --test-type ndrpdr
./suite_generator.py --gen-tests-dir generated --job csit-vpp-perf-report-coverage-2506-2n-spr --test-set 2n-spr-vpp-cov-ip4-00

Transformation of gerrit trigges to command-line parameters
-----------------------------------------------------------

1.  jobs for the report - iterative:

Old trigger:
  csit-vpp-report-iter-2n-aws-perftest vpp-mrr-00
  csit-vpp-report-iter-2n-aws-perftest vpp-ndrpdr-00
  csit-vpp-report-iter-2n-icx-perftest vpp-gso-mrr-00
  csit-vpp-report-iter-2n-icx-perftest vpp-soak-00
  csit-vpp-report-iter-2n-icx-perftest vpp-hoststack-00

Parameters:



2.  jobs for the report - coverage:

Old trigger:
  csit-vpp-report-cov-2n-grc-perftest ip4-04

Parameters:



3. Verify jobs

Old trigger:
  csit-2n-zn2-perftest <tags>
  vpp-csit-verify-perf-master-ubuntu2404-aarch64-2n-grc <tags>

Parameters:



4. Bisect jobs:

Old trigger:
  bisecttest-2n-spr d35f7f098 <tags>

Parameters:







Notes
=====

To be removed before merge.

Hints:
clear; ./suite_generator.py --gen-tests-dir generated --job csit-trex-perf-ndrpdr-weekly-master-2n-spr
clear; ./suite_generator.py --gen-tests-dir generated --job csit-vpp-perf-mrr-daily-master-2n-icx
clear; ./suite_generator.py --gen-tests-dir generated --job csit-vpp-perf-report-iterative-2506-2n-icx
clear; ./suite_generator.py --gen-tests-dir generated --job csit-vpp-perf-report-iterative-2506-2n-icx --test-type ndrpdr
clear; ./suite_generator.py --gen-tests-dir generated --job csit-vpp-perf-report-coverage-2506-2n-spr --test-set 2n-spr-vpp-cov-ip4-00

"""


import logging
import sys

from argparse import ArgumentParser, RawTextHelpFormatter, BooleanOptionalAction
from json import dumps
from os import path, makedirs

import constants as C

from generator import generate_suites
from spec_processor import process_specification, generate_job_spec


def suite_generator(args) -> int:
    """Suite generator

    Top level function.

    :param args: Parsed CLI arguments.
    :type args: Namespace
    :returns: Return code: 0 - OK, 1 - Not OK.
    :rtype: int
    """

    # Process the comand line arguments
    job = args.job.lower()
    test_dir = args.gen_tests_dir
    test_set = args.test_set.lower()
    test_type = args.test_type.lower()
    output_dir = args.output_dir if args.output_dir else C.DEFAULT_OUTPUT_PATH
    output_file = \
        args.output_file if args.output_file else C.DEFAULT_OUTPUT_FILE
    create_json = args.create_json
    # TODO: Remove
    # create_md = args.create_flat_spec
    logging_level = \
        args.logging_level if args.logging_level else C.DEFAULT_LOG_LEVEL

    # Set the logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging_level
    )

    logging.debug(
        "\nCommand line parameters:\n"
        f"Job:             {job}\n"
        f"Test output dir: {test_dir}\n"
        f"Test set:        {test_set if test_set else 'Not specified'}\n"
        f"Test type:       {test_type if test_type else 'Not specified'}\n"
        f"Output dir:      {output_dir}\n"
        f"Output file:     {output_file}\n"
        f"Logging level:   {logging_level}\n"
        f"Create JSON:     {create_json}\n"
        # TODO: Remove
        # f"Create job spec: {create_md}\n"
    )

    try:
        makedirs(test_dir, exist_ok=False)
        logging.debug(f"Directory '{test_dir}' created successfully.")
    except FileExistsError:
        logging.info(f"The directory '{test_dir}' exists, it will be reused.")
    except OSError as err:
        logging.error(f"The directory '{test_dir}' cannot be created.\n{err}")
        return 1

    try:
        makedirs(output_dir, exist_ok=False)
        logging.debug(f"Directory '{output_dir}' created successfully.")
    except FileExistsError:
        logging.info(
            f"The directory '{output_dir}' exists, it will be reused "
            f"but not emptied. Existing files will be overwritten, new files "
            f"will be added."
        )
    except OSError as err:
        logging.error(f"The directory '{output_dir}' cannot be created.\n{err}")
        return 1

    # Generate the job specification as a JSON structure:
    spec = process_specification()
    if not spec:
        logging.error(
            f"The specification in {C.DIR_JOB_SPEC} cannot be processed."
        )
        return 1

    # Write the specification to a JSON file:
    if create_json:
        try:
            with open(path.join(output_dir, f"{output_file}.json"), "wt") as fw:
                fw.write(dumps(spec, sort_keys=True, indent=2))
        except IOError as err:
            logging.error(f"Cannot write the JSON file.\n {err}")
            return 1

    job_spec = generate_job_spec(spec, job, test_set, test_type)
    if not job_spec:
        return 1

    # Generate suites:
    return generate_suites(test_dir, job_spec, job)


def parse_args():
    """Parse the command line arguments.

    :returns: Parsed command line arguments.
    :rtype: Namespace
    """
    parser = ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        description=__doc__
    )
    parser.add_argument(
        "--job", required=True, type=str,
        help="The name of the job which will run the generated tests."
    )
    parser.add_argument(
        "--gen-tests-dir", required=True, type=str,
        help=("Directory to store generated tests.")
    )
    parser.add_argument(
        "--test-set", required=False, type=str, default=str(),
        help=(
            "Test set (on-demand jobs (iterative, coverage, bisect, ...)).\n"
            "Specifies the tests to run. Only one test set can be specified.\n"
            "If the test set is not specified as command-line parameter, it\n"
            "must be specified in the specification file."
        )
    )
    parser.add_argument(
        "--test-type", required=False, type=str, default=str(),
        help=(
            "Optional. If not specified, the test type from specification is\n"
            "used.\n"
            "Mandatory for on-demand (iterative, coverage, bisect, ...) jobs."
        )
    )
    parser.add_argument(
        "--output-dir", required=False, type=str, default=str(),
        help=(
            "Optional. Directory to store generated files. If not given, the\n"
            "default directory is used."
        )
    )
    parser.add_argument(
        "--output-file", required=False, type=str, default=str(),
        help=(
            "Optional. The name of output file(s):\n"
            "1. transformed and expanded yaml file to json, and\n"
            "2. generated job specifications (if requested) in text format.\n"
            "   The file extension is 'md'.\n"
            "If not given, the default name is used."
        )
    )
    parser.add_argument(
        "--create-json", required=False, type=bool, default=False,
        action=BooleanOptionalAction,
        help=(
            "Optional. If set, the processed specification will be writen to\n"
            "the output directory as a JSON file."
        )
    )

    parser.add_argument(
        "--logging-level", required=False, type=str,
        choices=[i for i in C.LOGGING_LEVEL],
        default=C.DEFAULT_LOG_LEVEL,
        help=f"Optional. Logging level. (default: {C.DEFAULT_LOG_LEVEL})"
    )
    return parser.parse_args()


if __name__ == "__main__":
    """Entry point if called from cli.
    """
    sys.exit(suite_generator(parse_args()))
