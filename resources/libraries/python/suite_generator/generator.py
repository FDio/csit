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
from string import Template

import constants as C


def _find_test_tmpl(patern: str, test_tag: str) -> str:
    """Find the right test template based on the test tag.

    To speed up the search process:
    1. Find the candidate based on the file name and only then
    2. look ionto the files and check the test tag.

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


def _replace_defensively(text: str, to_replace: str, replace_with: str,
                         how_many: int, in_filename: str, msg: str) -> str:
    """Replace substrings while checking the number of occurrences.

    Return edited copy of the text. Assuming "whole" is really a string,
    or something else with .replace not affecting it.

    :param text: The text to perform replacements on.
    :param to_replace: Substring occurrences of which to replace.
    :param replace_with: Substring to replace occurrences with.
    :param how_many: Number of occurrences to expect.
    :param msg: Error message to raise.
    :param in_filename: File name in which the error occurred.
    :type text: str
    :type to_replace: str
    :type replace_with: str
    :type how_many: int
    :type msg: str
    :type in_filename: str
    :returns: The whole text after replacements are done.
    :rtype: str
    :raises ValueError: If number of occurrences does not match.
    """
    if text.count(to_replace) != how_many:
        raise ValueError(f"{in_filename}: {msg}")
    return text.replace(to_replace, replace_with)


def _generate_suite_params_default(tmpl: str, infra: tuple, test_type: str,
                                   file_name: str) -> str:
    """Generate test parameters, documentation, tags, local template, ...
    for the default (and the most common) test suite - pure ndrpdr, mrr.

    :param tmpl: Suite template.
    :param infra: NIC, driver.
    :param test_type: The test type - ndrpdr, mrr, ...
    :param file_name: The file name for the test suite. It is used here only for
        error messages.
    :type tmpl: str
    :type infra: tuple[str, str]
    :type test_type: str
    :type file_name: str
    :returns: The common part of the suite.
    :rtype: str
    """

    nic, driver = infra

    # Suite tags: test type, driver; the NIC is replaced later
    tmpl = _replace_defensively(
        tmpl, C.TMPL_TTYPE.upper(), test_type.upper(), 1, file_name,
        "Suite type should appear once in uppercase (as a tag)."
    )
    tmpl = _replace_defensively(
        tmpl, C.NIC_DRIVER_TO_TAG[C.TMPL_DRV], C.NIC_DRIVER_TO_TAG[driver], 1,
        file_name, "Driver tag should appear once."
    )

    # Documentation
    tmpl = _replace_defensively(
        tmpl, C.PERF_TYPE_TO_SUITE_DOC_VER[C.TMPL_TTYPE],
        C.PERF_TYPE_TO_SUITE_DOC_VER[test_type], 1, file_name,
        "Exact suite type documentation not found."
    )

    # Variables: NIC name, driver, plugin, NIC VFs
    tmpl = _replace_defensively(
        tmpl, C.NIC_CODE_TO_NAME[C.TMPL_NIC], C.NIC_CODE_TO_NAME[nic], 2,
        file_name, "NIC name should appear twice (tag and variable)."
    )
    tmpl = _replace_defensively(
        tmpl, C.TMPL_DRV, driver, 1, file_name,
        "Driver name should appear once."
    )
    tmpl = _replace_defensively(
        tmpl, C.NIC_DRIVER_TO_PLUGINS[C.TMPL_DRV],
        C.NIC_DRIVER_TO_PLUGINS[driver], 1, file_name,
        "Driver plugin should appear once."
    )
    tmpl = _replace_defensively(
        tmpl, C.NIC_DRIVER_TO_VFS[C.TMPL_DRV],
        C.NIC_DRIVER_TO_VFS[driver], 1, file_name,
        "NIC VFs argument should appear once."
    )
    tmpl = _replace_defensively(
        tmpl, C.NIC_CODE_TO_PFS[C.TMPL_NIC],
        C.NIC_CODE_TO_PFS[nic], 1, file_name,
        "NIC PFs argument should appear once."
    )

    # Local (test) template: Documentation
    tmpl = _replace_defensively(
        tmpl, C.PERF_TYPE_TO_TEMPLATE_DOC_VER[C.TMPL_TTYPE],
        C.PERF_TYPE_TO_TEMPLATE_DOC_VER[test_type], 1, file_name,
        "Exact template type documentation not found."
    )

    # Local (test) template: Keyword performing the search
    tmpl = _replace_defensively(
        tmpl, C.PERF_TYPE_TO_KEYWORD[C.TMPL_TTYPE],
        C.PERF_TYPE_TO_KEYWORD[test_type], 1, file_name,
        "Main search keyword should appear once in the suite."
    )

    return tmpl


def generate_suite_params(tmpl: str, infra: tuple, test_type: str,
                          file_name: str) -> tuple[int, str]:
    """Generate test parameters, documentation, tags, local template, ...

    :param tmpl: Suite template.
    :param infra: NIC, driver.
    :param test_type: The test type - ndrpdr, mrr, ...
    :param file_name: The file name for the test suite. It is used here only for
        error messages.
    :type tmpl: str
    :type infra: tuple[str, str]
    :type test_type: str
    :type file_name: str
    :returns: The common part of the suite.
    :rtype: str
    """

    gen_suite_params = {
        "default": _generate_suite_params_default
    }

    # TODO: Generalize
    suite_type = "default"

    ret_val = 0
    try:
        tmpl = gen_suite_params[suite_type](tmpl, infra, test_type, file_name)
    except (ValueError, KeyError) as err:
        logging.error(err)
        ret_val = 1

    return ret_val, tmpl


def _generate_test_default(test_tag: str, infra: tuple, params: tuple) -> str:
    """Generate test (only one) for the default (and the most common) test
    suite - pure ndrpdr, mrr.

    :param test_tag: Test tag.
    :param infra: NIC, driver.
    :param params: The test parameters - core, framesize, test type.

    :type test_tag: str
    :type infra: tuple[str, str]
    :type params: tuple
    :returns: The test.
    :rtype: str
    """

    test = Template(C.TMPL_TEST)
    cores, frame, test_type = params
    mapping = {
        "suite_id": test_tag,
        "test_type": test_type,
        "driver": "" if infra[1] == "vfio_pci" else f"{infra[1]}-",
        "frame_tag": "IMIX" if frame == "imix" else f"{frame}B",
        "frame_str": "IMIX" if frame == "imix" else f"{frame}b",
        "frame_num": "${IMIX_v4_1}" if frame == "imix" else f"${{{frame}}}",
        "cores_tag": f"{cores}C",
        "cores_str": f"{cores}c",
        "cores_num": f"${{{cores:d}}}"
    }
    return test.safe_substitute(mapping)


def generate_test(test_tag: str, infra: tuple, params: tuple) -> str:
    """Generate test (only one).

    :param test_tag: Test tag.
    :param infra: NIC, driver.
    :param params: The test parameters - core, framesize, test type.

    :type test_tag: str
    :type infra: tuple[str, str]
    :type params: tuple
    :returns: The test.
    :rtype: str
    """

    gen_test = {
        "default": _generate_test_default
    }

    # TODO: Generalize
    suite_type = "default"

    return gen_test[suite_type](test_tag, infra, params)


def generate_suite(src: str, dst: str, test_tag: str, infra: tuple,
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
    # Replace items in template
    rc, new_suite = generate_suite_params(new_suite, infra, params[0][2], dst)
    if rc:
        return 1
    # Add tests
    for param in params:
        new_suite += generate_test(test_tag, infra, param)
    # Write the generated suite
    try:
        with open(dst, "wt") as fw:
            fw.write(new_suite)
    except IOError as err:
        logging.error(f"Cannot write the file '{dst}'\n{err}")
        return 1
    
    return 0


def generate_suites(output_dir: str, spec: dict, job: str,
                    testgroup: str=str()) -> int:
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
    :param testgroup: Optional. The name of the test group. If specified, only
        tests from this test group will be included.
    :type output_dir: str
    :type spec: dict
    :type job: str
    :type testgroup: str
    :returns: Return code: 0 - OK, 1 - Not OK
    :rtype: int
    """

    # The directory where the generated test suites are written
    dir_tests_out = path.join(output_dir, C.DIR_TESTS_OUT)

    # Pre-process spec - generate combinations of params for each test
    tests = dict()
    for group in spec:
        if testgroup and testgroup != group["group-name"]:
            continue
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
            else:
                l_params.append(group[param])
        for test in group["tests"]:
            if tests.get(test, None) is None:
                tests[test] = dict()
            for nic in l_nic_drv:    
                tests[test][nic] = list(product(*l_params))

    dut=job.split("-")[1]
    if "-2n" in job:
        nodes = "2n??-"
    elif "-1n" in job:
        nodes = "1n??-"
    else:
        nodes = str()
    for test_tag, infras in tests.items():
        logging.info(f"Generating testsuites for '{test_tag}' ...")
        # Look for template files
        # TODO: Define the patern: ndrpdr/cpr/rps/...
        # ttype_patern = "-ndrpdr"
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
            if infra[1] != "vfio_pci":  # driver
                nic_drv += f"-{infra[1]}"
            dst_name = file_name.replace(C.TMPL_NIC, nic_drv).\
                replace(C.TMPL_TTYPE, suite_params[0][2])
            # Generate the content (tests) of the suite
            if generate_suite(src=path.join(C.DIR_TESTS_IN, full_path),
                    dst=path.join(out_path, dst_name),test_tag=test_tag,
                    infra=infra,params=suite_params):
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
