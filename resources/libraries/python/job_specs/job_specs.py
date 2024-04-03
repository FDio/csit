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

csit/resources/job_specs/job_specifications.yaml
./job_specs.py --specification ../../../job_specs/job_specifications.yaml --job job
"""


import logging
import sys

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from yaml import load, FullLoader, YAMLError
from itertools import product
from copy import deepcopy
from pprint import pformat


LOGGING_LEVEL = logging.INFO


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
                            val = top_val[d_params[top_param]].get(param, None)
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
                    # get tests, they must be in "node-arch" branch:
                    if top_param == "node-arch":
                        tests = job_tmpl["node-arch"][d_params["node-arch"]]
                        if isinstance(tests, str):
                            spec[new_job_name]["tests"] = tests
                        elif isinstance(tests, dict):
                            spec[new_job_name]["tests"] = tests["tests"]
                # Add parameters read from top parameters:
                spec[new_job_name].update(d_params)

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

    return spec


def get_job_specification(spec: dict, job: str) -> dict:
    """
    """
    return spec.get(job, dict())


if __name__ == "__main__":
    """Entry point if called from cli.
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=LOGGING_LEVEL
    )
    parser = ArgumentParser(
        description="",
        formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--specification", required=True, type=str,
        help=""
    )
    parser.add_argument(
        "--job", required=True, type=str,
        help=""
    )
    parser.add_argument(
        "--testgroup", required=False, type=str,
        help=""
    )
    args = parser.parse_args()

    logging.debug(
        "\n"
        f"specification: {args.specification}\n"
        f"job:           {args.job}\n"
        f"test group:    {args.testgroup}"
    )

    spec = process_specification(args.specification)
    logging.info(f"\n{pformat(spec)}")
    if not spec:
        sys.exit(1)

    job_spec = get_job_specification(spec, args.job)
    logging.debug(f"\n{pformat(job_spec)}")
    if not job_spec:
        sys.exit(1)
