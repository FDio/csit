#!/usr/bin/python3

# Copyright (c) 2024 Cisco and/or its affiliates.
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

The suite generator generates the test suites defined in the configuration file.

The mandatory input information is:
1. Job specification provided as a YAML file.
2. Job name. The test suites are generated for this job. Only one job can be
   specified.

The optional input information is:
3. Test group
4. Output directory
5. Output file name
6. Logging level
7. Create JSON file
8. Create the job specification as an MD file
For more information, see below.

The output is:
1. A directory structure with generated tests, suites and other necessary files
   to run tests usinf Robot Framework.
7. Optionaly the JSON file with expaned specification.
8. Optionaly the job specification defined as a set of tags store in an MD file.

The return code is:
0 - if everything is OK,
1 - if anything went wrong.
"""


import logging
import sys

from argparse import ArgumentParser, RawTextHelpFormatter, BooleanOptionalAction
from json import dumps
from os import path, makedirs

import constants as C

from flat_job_spec import generate_job_spec
from generator import generate_suites
from spec_processor import process_specification


def suite_generator(args) -> int:
    """Suite generator

    Top level function.

    :param args: Parsed CLI arguments.
    :type args: Namespace
    :returns: Return code: 0 - OK, 1 - Not OK.
    :rtype: int
    """

    # Process the comand line arguments
    spec_file = args.specification
    job = args.job.lower()
    test_group = args.test_group.lower()
    output_dir = args.output_dir if args.output_dir else C.DEFAULT_OUTPUT_PATH
    output_file = \
        args.output_file if args.output_file else C.DEFAULT_OUTPUT_FILE
    logging_level = \
        args.logging_level if args.logging_level else C.DEFAULT_LOG_LEVEL
    create_json = args.create_json
    create_md = args.create_flat_spec

    # Set the logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging_level
    )

    logging.debug(
        "\nCommand line parameters:\n"
        f"Specification:   {spec_file}\n"
        f"Job:             {job}\n"
        f"Test group:      {test_group if test_group else 'Not specified'}\n"
        f"Output dir:      {output_dir}\n"
        f"Output file:     {output_file}\n"
        f"Logging level:   {logging_level}\n"
        f"Create JSON:     {create_json}\n"
        f"Create job spec: {create_md}\n"
    )

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
    spec = process_specification(spec_file)
    if not spec:
        logging.error(f"The specification {spec_file} cannot be processed.")
        return 1

    # Write the specification to a JSON file:
    if create_json:
        try:
            with open(path.join(output_dir, f"{output_file}.json"), "wt") as fw:
                fw.write(dumps(spec, sort_keys=True, indent=2))
        except IOError as err:
            logging.error(f"Cannot write the JSON file.\n {err}")
            return 1

    # Generate the job specification as an md file:
    if create_md:
        if generate_job_spec(spec, job, output_dir, output_file, test_group):
            return 1

    # Generate suites:
    return generate_suites(output_dir, spec[job], job, test_group)


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
        "--specification", required=True, type=str,
        help="The path to yaml file specifying the jobs."
    )
    parser.add_argument(
        "--job", required=True, type=str,
        help="The name of the job which will run the generated tests."
    )
    parser.add_argument(
        "--test-group", required=False, type=str, default=str(),
        help=(
            "Optional. If specified, only this test group will be in the\n"
            "generated test suites. If not given, all test groups are included."
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
        "--logging-level", required=False, type=str,
        choices=[i for i in C.LOGGING_LEVEL],
        default=C.DEFAULT_LOG_LEVEL,
        help=f"Optional. Logging level. (default: {C.DEFAULT_LOG_LEVEL})"
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
        "--create-flat-spec", required=False, type=bool, default=False,
        action=BooleanOptionalAction,
        help=(
            "Optional. If set, the specification will be generated also as\n"
            "the old fashioned flat MD file defining tests as a set of tags."
        )
    )
    return parser.parse_args()


if __name__ == "__main__":
    """Entry point if called from cli.
    """
    sys.exit(suite_generator(parse_args()))
