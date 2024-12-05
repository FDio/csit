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

"""Generate the test suites defined in the job specification.

Only those defined in the job specification.
"""


import logging

from glob import glob
from itertools import product
from os import path, makedirs, sep
from shutil import copyfile

import constants as C


def _get_suite_type(tmpl_name: str) -> str:
    """Determine the type of suite based on template name.

    :param tmpl_name: Template name
    :type tmpl_name: str
    :returns: Type of suite.
    :rtype: str
    """
    if tmpl_name.endswith("-tg-ndrpdr.robot"):
        return "trex"
    elif "hoststack" in tmpl_name:
        if tmpl_name.endswith("-cps.robot") or tmpl_name.endswith("-rps.robot"):
            # hoststack cps or rps
            return "hoststack_cps_rps"
        elif tmpl_name.endswith("-bps.robot"):
            # hoststack bps
            return "hoststack_bps"
        else:
            raise NotImplementedError(
                f"Processing of {tmpl_name} is not implemented.")
    elif tmpl_name.endswith("-iperf3-mrr.robot"):
        # gso
        return "iperf3"
    elif tmpl_name.endswith("-ndrpdr.robot"):
        # MUST be the last one.
        # General NDRPDR, MRR and SOAK tests. 
        return "default"
    else:
        raise NotImplementedError(
            f"Processing of {tmpl_name} is not implemented.")


def _find_test_tmpl(patern: str, test_tag: str) -> str:
    """Find the right test template based on the test tag.

    To speed up the search process:
    1. Find the candidates based on the file name and only then
    2. look into the files and check the test tag.

    The test tag MUST be lowercase and it MUST be at the end of line, in the
    best case, it is the only tag on the line.

    :param patern: The patern defining the path to the file used by glob.
    :param: test_tag: The test tag as it is defined in the test template.
    :type patern: str
    :type test_tag: str
    :returns: The path to the found test template.
    :rtype: str
    """
    # At first, find the candidates - the test name is in the file name...
    for file_name in glob(patern, recursive=True):
        with open(file_name, "rt") as fr:
            # ... then check the tag inside the file.
            if f"| {test_tag}\n" in fr.read():
                return file_name.removeprefix(C.DIR_TESTS_IN)[1:]


def _generate_suite(src: str, dst: str, test_tag: str, infra: tuple,
                    params: tuple) -> int:
    """Generate a test sute.

    :param src: Path to the template file (suite).
    :param dst: Path to the file where the generated suite is written.
    :param test_tag: Test tag.
    :param infra: NIC, driver.
    :param params: core, framesize, test type.
    :type src: str
    :type dst: str
    :type test_tag: str
    :type infra: tuple
    :type params: tuple
    :returns: Return code: 0 - OK, 1 - Not OK
    :rtype: int
    """
    logging.debug(
        f"Template file:\n{src}\n"
        f"Destination file:\n{dst}\n"
        f"Test name:\n{test_tag}\n"
        f"Infra:\n{infra}\n"
        f"Parameters:\n{params}\n"
    )

    tmpl_lines = list()
    with open(src, "rt") as fr:
        tmpl_lines = [line for line in fr]
    if not tmpl_lines:
        logging.error(f"The template file {src} is empty.")
        return 1

    # Extract the part with copyright, settings, variables and keywords
    new_suite = "".join(tmpl_lines[:tmpl_lines.index(C.TMPL_SEP_TESTS) + 1])

    # Determine the kind of suite:
    try:
        suite_type = _get_suite_type(src)
    except NotImplementedError as err:
        logging.error(err)
        return 1

    # Replace items in template
    try:
        new_suite = \
            C.GEN_SUITE_PARAMS[suite_type](new_suite, infra, params[0][2], dst)
    except (ValueError, KeyError) as err:
        logging.error(repr(err))
        return 1

    # Add tests
    try:
        for param in params:
            new_suite += C.GEN_TEST[suite_type](test_tag, infra, param)
    except (TypeError, KeyError, ValueError) as err:
        logging.error(repr(err))
        return 1

    # Write the generated suite
    try:
        with open(dst, "wt") as fw:
            fw.write(new_suite)
    except IOError as err:
        logging.error(f"Cannot write the file '{dst}'\n{err}")
        return 1

    return 0


def generate_suites(output_dir: str, spec: dict, job: str) -> int:
    """Generate all test suites defined in the specification.

    - job spec must include only one job
    - iterate through tests (items "tests" in dicts in the list)
      - find template robot file (suite) with tests (glob with patern=tag and
        then look inside the file for the tag)
      - replace parameters
      - generate tests with cores/framesizes/nics/drivers/test-types
    - The structure (dirs and files) must be the same as origin, incl __init__
      files.
    - Robot framework runs ALL tests

    :param output_dir: Directory to write the generated suites to.
    :param spec: Job specification.
    :param job: Job which wil run the generated tests.
    :type output_dir: str
    :type spec: dict
    :type job: str
    :returns: Return code: 0 - OK, 1 - Not OK
    :rtype: int
    """

    # The directory where the generated test suites are written
    dir_tests_out = path.join(output_dir, C.DIR_TESTS_OUT)

    # Pre-process spec - generate combinations of params for each test
    tests = dict()
    for group in spec:
        l_params = list()
        l_nic_drv = list()
        for param in C.TEST_PARAMS:
            if param not in group:
                logging.error(f"The parameter '{param}' is mandatory.")
                return 1
            if param == "infra":
                for nic, drv_lst in group[param].items():
                    for drv in drv_lst:
                        l_nic_drv.append((nic, drv))
            elif isinstance(group[param], str):
                l_params.append([group[param], ])
            else:
                l_params.append(group[param])
        for test in group["tests"]:
            if tests.get(test, None) is None:
                tests[test] = dict()
            for nic in l_nic_drv:
                tests[test][nic] = list(product(*l_params))

    dut=job.split("-")[1]
    if dut == "csit":
        dut=job.split("-")[0]
    if "-2n" in job:
        nodes = "2n??-"
    elif "-1n" in job:
        nodes = "1n??-"
    else:  # e.g. 3n has no info about number of nodes
        nodes = str()
    for test_tag, infras in tests.items():
        logging.info(f"Generating testsuites for '{test_tag}' ...")
        # Look for template files
        patern = (
            f"{C.DIR_TESTS_IN}{sep}tests{sep}{dut}{sep}**{sep}{nodes}"
            f"{C.TMPL_NIC}-{test_tag}*.robot"
        )
        full_path = _find_test_tmpl(patern, test_tag)
        if full_path is None:
            logging.warning("The template file not found. SKIPPED")
            continue
        file_path, file_name = path.split(full_path)
        # Create the whole dir structure
        out_path = path.join(dir_tests_out, file_path)
        makedirs(out_path, exist_ok=True)
        # Process the file
        for infra, suite_params in infras.items():
            # Create the file name: change NIC, add driver, change testtype
            nic_drv = infra[0]  # NIC
            if infra[1] not in ("vfio-pci", "tap", "-"):  # driver
                nic_drv += f"-{C.NIC_DRIVER_TO_SUITE_PREFIX[infra[1]]}"
            dst_name = file_name.replace(C.TMPL_NIC, nic_drv).\
                replace(C.TMPL_TTYPE, suite_params[0][2])
            # Generate the content of the suite
            if _generate_suite(src=path.join(C.DIR_TESTS_IN, full_path),
                    dst=path.join(out_path, dst_name), test_tag=test_tag,
                    infra=infra, params=suite_params):
                return 1

        # Add __init__.robot files
        tmp_path = str()
        for dir in full_path.split(sep)[:-1]:
            tmp_path = path.join(tmp_path, dir)
            dst_path = path.join(dir_tests_out, tmp_path, "__init__.robot")
            if path.exists(dst_path):
                continue  # No need to do the same milion times
            src_path = path.join(C.DIR_TESTS_IN, tmp_path, "__init__.robot")
            if path.exists(src_path):  # Is there an init file?
                copyfile(src_path, dst_path)

    return 0
