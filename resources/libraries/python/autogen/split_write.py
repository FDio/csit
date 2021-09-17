# Copyright (c) 2021 Cisco and/or its affiliates.
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

"""Module defining functions for layered replacement logic.

Here, layered means that one function performs some replacement,
then calls another function to do other replacements.
As typically the replacements are used to introduce multiple suites
differing in the value after replacement, this is also "splitting"
the regeneration to ever smaller sets of suites, hence the module name.
At the leaves, the edited prolog is written into its target file,
and test cases are added.

TODO: How can we check each suite id is unique,
      when currently the suite generation is run on each directory separately?
"""

from resources.libraries.python.Constants import Constants
from resources.libraries.python.autogen.test_case import write_test_cases


def write_files(state, filename_set):
    """Recursively split, write final prolog and test cases.

    This is a recursive entry point, with many optional arguments
    to track splitting, see EditState class.

    Fail if new suite_id is in the set, else add it there.
    Do not return anything.

    :param state: Curent state of editing and splitting.
    :param filename_set: List of suite filenames encountered so far.
    :type state: EditState
    :type filename_set: Set[str]
    :returns: How many files were written.
    :rtype: int
    """
    if state.test_type_split:
        return split_on_test_type(state, filename_set)
    if state.nic_model_split:
        return split_on_nic_model(state, filename_set)
    if state.nic_driver_split:
        if u"DPDK" in state.prolog:
            return split_on_dpdk_nic_driver(state, filename_set)
        return split_on_vpp_nic_driver(state, filename_set)
    state.check_suite_tag_and_add_suite_id(filename_set)
    # Relying on top level filesystem walker to chdir where the file is.
    with open(state.filename, u"wt") as file_out:
        file_out.write(state.prolog)
        write_test_cases(state, file_out)
    return 1

def split_on_test_type(state, filename_set):
    """Edit suite type, call write_files without test_type_split.

    There is a cycle over supported suite types,
    so write_files is called with each value.

    :param state: Curent state of editing and splitting.
    :param filename_set: List of suite filenames encountered so far.
    :type state: EditState
    :type filename_set: Set[str]
    :returns: How many files were written.
    :rtype: int
    """
    no_files = 0
    for test_type in Constants.PERF_TYPE_TO_KEYWORD:
        # Each iteration needs to be based on state, not tmp_state.
        tmp_state = state.without_test_type_split()
        tmp_state = tmp_state.with_filename_replaced(
            u"ndrpdr", test_type, 1,
            u"File name should contain suite type once.",
        )
        tmp_state = tmp_state.with_prolog_replaced(
            u"ndrpdr".upper(), test_type.upper(), 1,
            u"Suite type should appear once in uppercase (as tag).",
        )
        tmp_state = tmp_state.with_prolog_replaced(
            u"Find NDR and PDR intervals using optimized search",
            Constants.PERF_TYPE_TO_KEYWORD[test_type], 1,
            u"Main search keyword should appear once in suite.",
        )
        tmp_state = tmp_state.with_prolog_replaced(
            Constants.PERF_TYPE_TO_SUITE_DOC_VER[u"ndrpdr"],
            Constants.PERF_TYPE_TO_SUITE_DOC_VER[test_type], 1,
            u"Exact suite type doc not found."
        )
        tmp_state = tmp_state.with_prolog_replaced(
            Constants.PERF_TYPE_TO_TEMPLATE_DOC_VER[u"ndrpdr"],
            Constants.PERF_TYPE_TO_TEMPLATE_DOC_VER[test_type], 1,
            u"Exact template type doc not found.",
        )
        no_files += write_files(tmp_state, filename_set)
    return no_files

def split_on_nic_model(state, filename_set):
    """Edit nic model, call write_files without nic_model_split.

    There is a cycle over supported nic models,
    so write_files is called with each value.

    :param state: Curent state of editing and splitting.
    :param filename_set: List of suite filenames encountered so far.
    :type state: EditState
    :type filename_set: Set[str]
    :returns: How many files were written.
    :rtype: int
    """
    no_files = 0
    for nic_name in Constants.NIC_NAME_TO_CODE:
        # Each iteration needs to be based on state, not tmp_state.
        tmp_state = state.without_nic_model_split()
        tmp_state = tmp_state.with_nic_model_chosen(nic_name)
        tmp_state = tmp_state.with_filename_replaced(
            u"10ge2p1x710", Constants.NIC_NAME_TO_CODE[nic_name], 1,
            u"File name should contain NIC code once.",
        )
        tmp_state = tmp_state.with_prolog_replaced(
            u"Intel-X710", nic_name, 2,
            u"NIC name should appear twice (tag and variable).",
        )
        if tmp_state.prolog.count(u"HW_") == 2:
            # TODO CSIT-1481: Crypto HW should be read
            #      from topology file instead.
            if nic_name in Constants.NIC_NAME_TO_CRYPTO_HW:
                tmp_state = tmp_state.with_prolog_replaced(
                    u"HW_DH895xcc",
                    Constants.NIC_NAME_TO_CRYPTO_HW[nic_name], 1,
                    u"HW crypto name should appear.",
                )
        no_files += write_files(tmp_state, filename_set)
    return no_files


def split_on_dpdk_nic_driver(state, filename_set):
    """Edit nic driver, call write_files without nic_driver_split.

    There is a cycle over supported nic drivers,
    so write_files is called with each value.

    Most edits are common between DPDK and VPP suites,
    living in apply_common_nic_driver_edits.

    :param state: Curent state of editing and splitting.
    :param filename_set: List of suite filenames encountered so far.
    :type state: EditState
    :type filename_set: Set[str]
    :returns: How many files were written.
    :rtype: int
    """
    no_files = 0
    for nic_driver in Constants.DPDK_NIC_NAME_TO_DRIVER[state.nic_model]:
        tmp_state = state.without_nic_driver_split()
        no_files += apply_common_nic_driver_edits(
            nic_driver, tmp_state, filename_set
        )
    return no_files

def split_on_vpp_nic_driver(state, filename_set):
    """Edit nic driver, call write_files without nic_driver_split.

    There is a cycle over supported nic drivers,
    so write_files is called with each value.

    Most edits are common between DPDK and VPP suites,
    living in apply_common_nic_driver_edits.

    :param state: Curent state of editing and splitting.
    :param filename_set: List of suite filenames encountered so far.
    :type state: EditState
    :type filename_set: Set[str]
    :returns: How many files were written.
    :rtype: int
    """
    no_files = 0
    for nic_driver in Constants.NIC_NAME_TO_DRIVER[state.nic_model]:
        # Each iteration needs to be based on state, not tmp_state.
        tmp_state = state.without_nic_driver_split()
        tmp_state = tmp_state.with_prolog_replaced(
            Constants.NIC_DRIVER_TO_VPP_PLUGIN[u"vfio-pci"],
            Constants.NIC_DRIVER_TO_VPP_PLUGIN[nic_driver], 1,
            u"NIC driver plugin should appear once.",
        )
        tmp_state = tmp_state.with_prolog_replaced(
            Constants.NIC_DRIVER_TO_VFS[u"vfio-pci"],
            Constants.NIC_DRIVER_TO_VFS[nic_driver], 1,
            u"NIC VFs argument should appear once.",
        )
        no_files += apply_common_nic_driver_edits(
            nic_driver, tmp_state, filename_set
        )
    return no_files

def apply_common_nic_driver_edits(nic_driver, state, filename_set):
    """Apply edits, call write_files to handle the rest.

    This is the code shared by split_on_*_nic_driver functions.

    :param nic_driver: NIC driver name as selected in split_on_vpp_nic_driver.
    :param state: Curent state of editing and splitting.
    :param filename_set: List of suite filenames encountered so far.
    :type nic_driver: str
    :type state: EditState
    :type filename_set: Set[str]
    :returns: How many files were written.
    :rtype: int
    """
    _, old_suite_id, _ = state.get_iface_and_suite_ids(state.filename)
    # No "for" cycle, split already disabled, so we do not need tmp_state.
    state = state.with_filename_replaced(
        old_suite_id,
        Constants.NIC_DRIVER_TO_SUITE_PREFIX[nic_driver] + old_suite_id,
        1, u"Error adding nic_driver prefix.",
    )
    state = state.with_prolog_replaced(
        u"vfio-pci", nic_driver, 1,
        u"NIC driver name should appear once.",
    )
    state = state.with_prolog_replaced(
        Constants.NIC_DRIVER_TO_TAG[u"vfio-pci"],
        Constants.NIC_DRIVER_TO_TAG[nic_driver], 1,
        u"NIC driver tag should appear once.",
    )
    return write_files(state, filename_set)
