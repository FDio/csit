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

"""Generate particular test suites.
"""


from string import Template

import constants as C


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
        raise ValueError(f"{in_filename}: Parameter '{to_replace}': {msg}")
    return text.replace(to_replace, replace_with)


def generate_suite_params_default(tmpl: str, infra: tuple, test_type: str,
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
    if "DPDK" not in tmpl:
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


def generate_suite_params_trex(tmpl: str, infra: tuple, test_type: str,
                               file_name: str) -> str:
    """Generate test parameters, documentation, tags, local template, ...
    for the TRex test suite - pure ndrpdr, mrr.

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

    nic = infra[0]

    # Suite tags: test type; the NIC is replaced later
    tmpl = _replace_defensively(
        tmpl, C.TMPL_TTYPE.upper(), test_type.upper(), 1, file_name,
        "Suite type should appear once in uppercase (as tag)."
    )

    # Documentation
    tmpl = _replace_defensively(
        tmpl, C.PERF_TYPE_TO_SUITE_DOC_VER["ndrpdr"],
        C.PERF_TYPE_TO_SUITE_DOC_VER[test_type], 1, file_name,
        "Exact suite type doc not found."
    )

    # Variables: NIC name, plugin, NIC VFs
    tmpl = _replace_defensively(
        tmpl, C.NIC_CODE_TO_NAME[C.TMPL_NIC], C.NIC_CODE_TO_NAME[nic], 2,
        file_name, "NIC name should appear twice (tag and variable)."
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


def generate_suite_params_iperf3(tmpl: str, infra: tuple, test_type: str,
                                 file_name: str) -> str:
    """Generate test parameters, documentation, tags, local template, ...
    for the GSO (iperf3) test suite.

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

    nic = infra[0]
    _ = test_type

    # Variables: NIC name, plugin, NIC VFs
    tmpl = _replace_defensively(
        tmpl, C.NIC_CODE_TO_NAME[C.TMPL_NIC], C.NIC_CODE_TO_NAME[nic], 2,
        file_name, "NIC name should appear twice (tag and variable)."
    )

    return tmpl


def generate_suite_params_hoststack_cps_rps(tmpl: str, infra: tuple,
        test_type: str, file_name: str) -> str:
    """Generate test parameters, documentation, tags, local template, ...
    for the hoststack cps and rps test suite.

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


    TODO
    """

    nic = infra[0]
    _ = test_type

    # Variables: NIC name, plugin, NIC VFs
    tmpl = _replace_defensively(
        tmpl, C.NIC_CODE_TO_NAME[C.TMPL_NIC], C.NIC_CODE_TO_NAME[nic], 2,
        file_name, "NIC name should appear twice (tag and variable)."
    )

    return tmpl


def generate_suite_params_hoststack_bps(tmpl: str, infra: tuple,
        test_type: str, file_name: str) -> str:
    """Generate test parameters, documentation, tags, local template, ...
    for the hoststack bps test suite.

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


    TODO
    """

    nic = infra[0]
    _ = test_type

    # Variables: NIC name, plugin, NIC VFs
    tmpl = _replace_defensively(
        tmpl, C.NIC_CODE_TO_NAME[C.TMPL_NIC], C.NIC_CODE_TO_NAME[nic], 2,
        file_name, "NIC name should appear twice (tag and variable)."
    )

    return tmpl


def generate_test_default(test_tag: str, infra: tuple, params: tuple) -> str:
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

    test = Template(C.TMPL_TEST["default"])
    (cores, frame), test_type = params
    mapping = {
        "suite_id": test_tag,
        "test_type": test_type,
        "driver": C.NIC_DRIVER_TO_SUITE_PREFIX[infra[1]],
        "frame_tag": "IMIX" if frame == "imix" else f"{frame}B",
        "frame_str": "IMIX" if frame == "imix" else f"{frame}b",
        "frame_num": "IMIX_v4_1" if frame == "imix" else f"${{{frame}}}",
        "cores_tag": f"{cores}C",
        "cores_str": f"{cores}c",
        "cores_num": f"${{{cores:d}}}"
    }
    return test.safe_substitute(mapping)


def generate_test_trex(test_tag: str, infra: tuple, params: tuple) -> str:
    """Generate test (only one) for the TRex test suite - pure ndrpdr, mrr.

    :param test_tag: Test tag.
    :param infra: NIC, driver.
    :param params: The test parameters - core, framesize, test type.
    :type test_tag: str
    :type infra: tuple[str, str]
    :type params: tuple
    :returns: The test.
    :rtype: str
    """

    test = Template(C.TMPL_TEST["trex"])
    (_, frame), test_type = params
    _ = infra
    mapping = {
        "suite_id": test_tag,
        "test_type": test_type,
        "frame_tag": "IMIX" if frame == "imix" else f"{frame}B",
        "frame_str": "IMIX" if frame == "imix" else f"{frame}b",
        "frame_num": "IMIX_v4_1" if frame == "imix" else f"${{{frame}}}"
    }
    return test.safe_substitute(mapping)


def generate_test_iperf3(test_tag: str, infra: tuple, params: tuple) -> str:
    """Generate test (only one) for the GSO (iperf3) test suite.

    :param test_tag: Test tag.
    :param infra: NIC, driver.
    :param params: The test parameters - core, framesize, test type.
    :type test_tag: str
    :type infra: tuple[str, str]
    :type params: tuple
    :returns: The test.
    :rtype: str
    """

    test = Template(C.TMPL_TEST["iperf3"])
    (cores, frame), _ = params
    _ = infra
    mapping = {
        "suite_id": test_tag,
        "frame_num": "IMIX_v4_1" if frame == "imix" else f"${{{frame}}}",
        "cores_tag": f"{cores}C",
        "cores_str": f"{cores}c",
        "cores_num": f"${{{cores:d}}}"
    }
    return test.safe_substitute(mapping)


def generate_test_hoststack_cps_rps(test_tag: str, infra: tuple,
        params: tuple) -> str:
    """Generate test (only one) for the hoststack cps and rps test suite.

    :param test_tag: Test tag.
    :param infra: NIC, driver.
    :param params: The test parameters - core, framesize, test type.
    :type test_tag: str
    :type infra: tuple[str, str]
    :type params: tuple
    :returns: The test.
    :rtype: str


    TODO
    """

    test = Template(C.TMPL_TEST["hoststack_cps_rps"])
    (cores, frame), _ = params
    _ = infra
    mapping = {
        "suite_id": test_tag,
        "frame_tag": "IMIX" if frame == "imix" else f"{frame}B",
        "frame_str": "IMIX" if frame == "imix" else f"{frame}b",
        "frame_num": "IMIX_v4_1" if frame == "imix" else f"${{{frame}}}",
        "cores_tag": f"{cores}C",
        "cores_str": f"{cores}c",
        "cores_num": f"${{{cores:d}}}"
    }
    return test.safe_substitute(mapping)


def generate_test_hoststack_bps(test_tag: str, infra: tuple,
        params: tuple) -> str:
    """Generate test (only one) for the hoststack bps test suite.

    :param test_tag: Test tag.
    :param infra: NIC, driver.
    :param params: The test parameters - core, framesize, test type.
    :type test_tag: str
    :type infra: tuple[str, str]
    :type params: tuple
    :returns: The test.
    :rtype: str


    TODO
    """

    test = Template(C.TMPL_TEST["hoststack_bps"])
    (cores, frame), _ = params
    _ = infra
    mapping = {
        "suite_id": test_tag,
        "frame_str": "IMIX" if frame == "imix" else f"{frame}b",
        "cores_tag": f"{cores}C",
        "cores_str": f"{cores}c",
        "cores_num": f"${{{cores:d}}}"
    }
    return test.safe_substitute(mapping)
