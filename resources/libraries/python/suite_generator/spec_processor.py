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

"""Process the specification provided as a YAML file.
"""


import logging

from copy import deepcopy
from itertools import product
from os import path
from yaml import load, FullLoader, YAMLError

import constants as C


def _get_job_params(in_str: str) -> list:
    """Get the parameters from the name of job.

    The function searches for parameters enclosed by '{' and '}'.
    Typicaly 'node-arch', ...

    :params in_str: Input string
    :type in_str: str
    :returns: A list of parameters found in the input string.
    :rtype: list
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


def process_specification() -> dict:
    """Process the specification provided as a YAML file.

    :param path_to_spec: Path to YAML file with specification.
    :returns: Full specification with all parameters replaced by their values.
    :rtype: dict
    """

    raw_spec = dict()
    for spec_file in ("jobs.yaml", "test_sets.yaml", "test_groups.yaml"):
        path_to_spec = path.join(C.DIR_JOB_SPEC, spec_file)
        try:
            with open(path_to_spec, "r") as file_read:
                spec_part = load(file_read, Loader=FullLoader)
        except IOError as err:
            logging.error(
                f"Not possible to open the file {path_to_spec}\n"
                f"{err}"
            )
            return dict()
        except YAMLError as err:
            logging.error(
                f"An error occurred while parsing the specification file "
                f"{path_to_spec}\n{err}"
            )
            return dict()

        raw_spec.update(spec_part)

    jobs = raw_spec.get("jobs", dict())

    # Expand the "jobs" section, do not add test sets
    spec = dict()
    for job_name in jobs:
        job_params = _get_job_params(job_name)
        job_tmpl = jobs[job_name]

        if not job_params:
            spec[job_name] = deepcopy(job_tmpl)
        else:
            l_opts = list()
            top_params = list()
            for param in job_params:
                try:
                    job_tmpl_param = job_tmpl[param]
                    top_params.append(param)
                except KeyError:
                    continue
                if isinstance(job_tmpl_param, str):
                    l_opts.append([job_tmpl_param, ])
                elif isinstance(job_tmpl_param, list):
                    if param == "node-arch":
                        l_itms = list()
                        for itm in job_tmpl_param:
                            if isinstance(itm, str):
                                l_itms.append(itm)
                            elif isinstance(itm, dict):
                                l_itms.append(list(itm.keys())[0])
                            else:
                                logging.error(
                                    f"{job_name}: "
                                    "Not allowed data type in 'node-arch'."
                                )
                                return dict()
                        l_opts.append(l_itms)
                    else:
                        l_opts.append(job_tmpl_param)
                elif isinstance(job_tmpl_param, dict):
                    l_opts.append(list(job_tmpl_param.keys()))

            opt_combs = product(*l_opts)
            for opt_comb in opt_combs:
                d_params = dict(zip(top_params, opt_comb))
                for param in job_params:
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
                    if top_param not in C.TEST_PARAMS:
                        del spec[new_job_name][top_param]

                    # Get tests, they must be in "node-arch" branch:
                    if top_param == "node-arch":
                        for itm in job_tmpl["node-arch"]:
                            if isinstance(itm, str):
                                if itm == d_params["node-arch"]:
                                    spec[new_job_name]["test-set"] = str()
                            else:  # dict
                                key = list(itm.keys())[0]
                                if key == d_params["node-arch"]:
                                    spec[new_job_name]["test-set"] = itm[key]
    return {
        "jobs": spec,
        "test-sets": raw_spec.get("test-sets", dict()),
        "test-groups": raw_spec.get("test-groups", dict())
    }


def generate_job_spec(spec: dict, job: str, test_set: str,
                      test_type: str) -> dict:
    """Generate a full specification for the required job.

    :param spec: Job specification extracted from the specification file.
    :param job: Job name.
    :param test_set: Test set to be used for the full job specification.
    :param test_type: Test type.
    :type spec: dict
    :type job: str
    :type test_set: str
    :type test_type: str
    :returns: Full job specification.
    :rtype: dict
    """

    try:
        job_spec = spec["jobs"][job]
    except KeyError as err:
        logging.error(f"Job {job} not in specification.\n{err}")
        return dict()
    try:
        test_sets = spec["test-sets"]
    except KeyError as err:
        logging.error(f"No test sets defined.\n{err}")
        return dict()
    try:
        test_groups = spec["test-groups"]
    except KeyError as err:
        logging.error(f"No test groups defined.\n{err}")

    # If the test set is provided from cmd line, replace that in the
    # specification, or add it if there is no test set specified.
    if test_set:
        job_spec["test-set"] = test_set

    # If the test type is provided from cmd line, replace that in the
    # specification, or add it if there is no test set specified.
    if test_type:
        job_spec["test-type"] = test_type

    # Take the required job and add "test-set" and "test-group" sub-structures:
    try:
        job_spec["tests"] = deepcopy(test_sets[job_spec["test-set"]])
        new_tests = list()
        for tests in job_spec["tests"]["tests"]:
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
        job_spec["tests"]["tests"] = deepcopy(new_tests)
    except KeyError as err:
        logging.error(f"{job}: One or more parameters is not defined: {err}.")
        return dict()

    # Add all parameters to test groups:
    for group in job_spec["tests"]["tests"]:
        params = dict()
        for param in job_spec:
            if param not in C.TEST_PARAMS:
                continue
            params[param] = job_spec[param]
        for param in job_spec["tests"]:
            if param not in C.TEST_PARAMS:
                continue
            params[param] = job_spec["tests"][param]
        params.update(group)
        group.update(params)

    return job_spec["tests"]["tests"]
