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
Generates a list of tests for a job from the given specificaton in YAML format.


Hints (to be deleted):
clear; ./job_specs.py --specification ../../../job_specs/job_specifications.yaml --job csit-vpp-perf-report-iterative-2402-2n-icx --test-type mrr --test-group ip4-base --output-dir ./out
clear; ./job_specs.py --specification ../../../job_specs/job_specifications.yaml --job csit-vpp-perf-report-iterative-2402-2n-icx --test-type mrr --output-dir ./out --output-file spec
clear; ./job_specs.py --specification ../../../job_specs/job_specifications.yaml --job all --output-dir ./out
clear; ./job_specs.py --specification ../../../job_specs/job_specifications.yaml --job all --output-dir ./out --test-type mrr
"""


import logging
import sys

from argparse import ArgumentParser, RawTextHelpFormatter
from copy import deepcopy
from itertools import product
from json import dumps
from os import path, makedirs
from pprint import pformat
from yaml import load, FullLoader, YAMLError


# Logging level.
LOGGING_LEVEL = logging.INFO

# Parameters of test(s) applied to the test groups. Their order in this tuple
# defines the order in the output MD file.
TEST_PARAMS = ("core", "framesize", "test-type", "infra")

# Default path for generated files.
DEFAULT_OUTPUT_PATH = "."
# Default filename for generated files.
DEFAULT_OUTPUT_FILE = "job_spec"


def process_specification(path_to_spec: str) -> dict:
    """
    """

    def get_job_params(in_str:str) -> list:
        """
        """
        params = list()
        idx_end = 0
        while True:
            idx = in_str.find("{", idx_end)
            if idx == -1:
                break
            idx_end = in_str.find("}", idx)
            if idx_end == -1:
                break
            params.append(in_str[idx+1:idx_end])
        return params

    spec = dict()
    raw_spec = None
    try:
        with open(path_to_spec, "r") as file_read:
            raw_spec = load(file_read, Loader=FullLoader)
    except IOError as err:
        logging.error(
            f"Not possible to open the file {path_to_spec}\n"
            f"{err}"
        )
    except YAMLError as err:
        logging.error(
            f"An error occurred while parsing the specification file "
            f"{path_to_spec}\n{err}"
        )
    if not raw_spec:
         return spec

    jobs = raw_spec.get("jobs", dict())
    infra = raw_spec.get("test-to-infra", dict())
    test_groups = raw_spec.get("tests", dict())
    for job_name in jobs:
        params = get_job_params(job_name)
        job_tmpl = jobs[job_name]

        if not params:
            spec[job_name] = deepcopy(job_tmpl)
        else:
            l_opts = list()
            top_params = list()
            for param in params:
                try:
                    job_tmpl_param = job_tmpl[param]
                    top_params.append(param)
                except KeyError:
                    continue
                if isinstance(job_tmpl_param, str):
                    l_opts.append([job_tmpl_param, ])
                elif isinstance(job_tmpl_param, list):
                    l_opts.append(job_tmpl_param)
                elif isinstance(job_tmpl_param, dict):
                    l_opts.append(list(job_tmpl_param.keys()))
            opt_combs = product(*l_opts)
            for opt_comb in opt_combs:
                d_params = dict(zip(top_params, opt_comb))
                for param in params:
                    if param in d_params:
                        continue
                    for top_param in top_params:
                        top_val = job_tmpl[top_param]
                        if isinstance(top_val, dict):
                            try:
                                val = top_val[d_params[top_param]].\
                                    get(param, None)
                            except AttributeError:
                                logging.error(
                                    f"{job_name}: The parameter '{param}' must "
                                    f"be defined."
                                )
                                return dict()
                            if val is not None:
                                d_params[param] = val
                                continue
                try:
                    new_job_name = job_name.format(**d_params)
                except KeyError as err:
                    logging.error(
                        f"{job_name}: One or more parameters is not defined: "
                        f"{err}."
                    )
                    return dict()
                spec[new_job_name] = deepcopy(job_tmpl)
                for top_param in top_params:
                    # Delete top parameters, they are not needed anymore:
                    del spec[new_job_name][top_param]
                    # Get tests, they must be in "node-arch" branch:
                    if top_param == "node-arch":
                        tests = job_tmpl["node-arch"][d_params["node-arch"]]
                        if isinstance(tests, str):
                            spec[new_job_name]["tests"] = tests
                        elif isinstance(tests, dict):
                            spec[new_job_name]["tests"] = tests["tests"]

    # Add "test-to-infra" and "tests" sub-structures:
    for job in spec:
        try:
            spec[job]["tests"] = deepcopy(infra[spec[job]["tests"]])
            new_tests = list()
            for tests in spec[job]["tests"]["tests"]:
                new_test = dict()
                if isinstance(tests, str):
                    new_test = {"tests": test_groups[tests]}
                    new_test["group-name"] = tests
                elif isinstance(tests, dict):
                    for key in tests:
                        new_test["tests"] = test_groups[key]
                        new_test["group-name"] = key
                        new_test.update(tests[key])
                else:
                    return dict()
                new_tests.append(new_test)
            spec[job]["tests"]["tests"] = deepcopy(new_tests)
        except KeyError as err:
            logging.error(
                f"{job_name}: One or more parameters is not defined: {err}."
            )
            return dict()

    # Add all parameters to test groups:
    for job in spec:
        for group in spec[job]["tests"]["tests"]:
            params = dict()
            for param in spec[job]:
                if param not in TEST_PARAMS:
                    continue
                params[param] = spec[job][param]
            for param in spec[job]["tests"]:
                if param not in TEST_PARAMS:
                    continue
                params[param] = spec[job]["tests"][param]
            params.update(group)
            group.update(params)

    # Remove redundant information:
    specification = dict()
    for job in spec:
        specification[job] = spec[job]["tests"]["tests"]

    return specification


def generate_job_spec(
        spec: dict,
        job: str,
        testtype: str=str(),
        testgroup: str=str(),
        outputdir: str=str(),
        outputfile: str=str()
    ) -> int:
    """
    """
    if job not in spec:
        logging.error(f"Job {job} not in specification.")
        return 1
    
    logging.info(f"Generating job specification for '{job}'...")
    if testtype:
        logging.info(f"Test type: {testtype}")

    job_spec = str()
    count = 0
    for itm in spec[job]:
        if testgroup and testgroup != itm["group-name"]:
            continue
        l_params = list()
        for param in TEST_PARAMS:
            if param not in itm:
                logging.error(f"The parameter '{param}' is mandatory.")
                return 1
            if param == "infra":
                tmp_lst = list()
                for nic, drv_lst in itm[param].items():
                    for drv in drv_lst:
                        drv = f"drv_{drv}" if drv != "-" else "-"
                        tmp_lst.append(f"{nic} AND {drv}")
                l_params.append(tmp_lst)
            elif param == "core":
                l_params.append(
                    [f"{c}c" if c != "-" else "-" for c in itm[param]]
                )
            elif param == "test-type":
                if not testtype:
                    l_params.append(itm[param])
                else:
                    l_params.append([testtype, ])
            else:
                l_params.append(itm[param])
        l_params.append(itm["tests"])
        for comb in product(*l_params):
            job_spec += " AND ".join(comb) + "\n"
            count += 1
    logging.debug(f"\n{job_spec}")
    logging.info(f"Number of tests in job specification: {count}")

    # Write the job spec as md file:
    try:
        with open(path.join(outputdir, f"{outputfile}.md"), "wt") as f_w:
            f_w.write(job_spec)
    except IOError as err:
        logging.error(f"Cannot write the JSON file.\n {err}")
        return 1

    return 0


def generate_all_job_specs(
        spec: dict,
        testtype: str=str(),
        testgroup: str=str(),
        outputdir: str=str(),
        outputfile: str=str()
    ) -> int:
    """
    """
    for job in spec:
        if generate_job_spec(
                spec=spec,
                job=job,
                testtype=testtype,
                testgroup=testgroup,
                outputdir=outputdir,
                outputfile=f"{outputfile}_{job}"
            ):
            return 1
    return 0


if __name__ == "__main__":
    """Entry point if called from cli.
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=LOGGING_LEVEL
    )
    parser = ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        description=__doc__
    )
    parser.add_argument(
        "--specification", required=True, type=str,
        help="The yaml file specifying the jobs."
    )
    parser.add_argument(
        "--job", required=True, type=str,
        help=(
            "The name of the job to be included in the specification. If 'all'\n"
            "is used, specifications for all jobs in the yaml file are\n"
            "generated. If 'none', only json file is generated."
        )
    )
    parser.add_argument(
        "--test-group", required=False, type=str, default=str(),
        help=(
            "The test group which will be in the generated specification.\n"
            "If not given, all test groups are included."
        )
    )
    parser.add_argument(
        "--test-type", required=False, type=str, default=str(),
        help=(
            "The type of tests in generated specification. If not given, the\n"
            "tests are generated for all test types specified in the input\n"
            "yaml file."
        )
    )
    parser.add_argument(
        "--output-dir", required=False, type=str, default=str(),
        help=(
            "Directory to store generated files. If not given, the current\n"
            "working directory is used."
        )
    )
    parser.add_argument(
        "--output-file", required=False, type=str, default=str(),
        help=(
            "The name of output file(s):\n"
            "1. transformed and expanded yaml file to json, and\n"
            "2. generated job speciofications in text format. The file\n"
            "   extension is 'md'.\n"
            "If not given, the default name is used."
        )
    )
    args = parser.parse_args()

    logging.info(
        "\n"
        f"Specification: {args.specification}\n"
        f"Job:           {args.job.lower()}\n"
        f"Test group:    {args.test_group.lower()}\n"
        f"Test type:     {args.test_type.lower()}\n"
        f"Output dir:    {args.output_dir}\n"
        f"Output file:   {args.output_file}\n"
    )

    # Check CLI arguments:
    output_dir = args.output_dir if args.output_dir else DEFAULT_OUTPUT_PATH
    output_file = args.output_file if args.output_file else DEFAULT_OUTPUT_FILE

    try: 
        makedirs(output_dir, exist_ok=False) 
        logging.debug(f"Directory '{output_dir}' created successfully.") 
    except FileExistsError:
        logging.info(f"The directory '{output_dir}' exists, it will be reused.")
    except OSError as err:
        logging.error(f"The directory '{output_dir}' cannot be created.\n{err}")
        sys.exit(1)

    # Generate job specification as a JSON structure:
    spec = process_specification(args.specification)
    logging.debug(f"\n{pformat(spec)}")
    if not spec:
        sys.exit(1)
    
    # Write specification to a JSON file:
    try:
        with open(path.join(output_dir, f"{output_file}.json"), "wt") as f_w:
            f_w.write(dumps(spec, sort_keys=True, indent=2))
    except IOError as err:
        logging.error(f"Cannot write the JSON file.\n {err}")
        sys.exit(1)

    # Generate job specification as a txt file:
    if args.job.lower() == "none":
        pass
    elif args.job.lower() == "all":
        if generate_all_job_specs(
                spec=spec,
                testtype=args.test_type.lower(),
                testgroup=args.test_group.lower(),
                outputdir=output_dir,
                outputfile=output_file
            ):
            sys.exit(1)
    else:
        if generate_job_spec(
                spec=spec,
                job=args.job.lower(),
                testtype=args.test_type.lower(),
                testgroup=args.test_group.lower(),
                outputdir=output_dir,
                outputfile=output_file
            ):
            sys.exit(1)

    logging.info("Job specification(s) sucessfully generated.")
    sys.exit(0)
