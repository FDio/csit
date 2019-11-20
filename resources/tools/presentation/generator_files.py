# Copyright (c) 2018 Cisco and/or its affiliates.
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

"""Algorithms to generate files.
"""


import logging

from pal_utils import get_files, get_rst_title_char


RST_INCLUDE_TABLE = (u"\n.. only:: html\n\n"
                     u"    .. csv-table::\n"
                     u"        :header-rows: 1\n"
                     u"        :widths: auto\n"
                     u"        :align: center\n"
                     u"        :file: {file_html}\n"
                     u"\n.. only:: latex\n\n"
                     u"\n  .. raw:: latex\n\n"
                     u"      \\csvautolongtable{{{file_latex}}}\n\n")


def generate_files(spec, data):
    """Generate all files specified in the specification file.

    :param spec: Specification read from the specification file.
    :param data: Data to process.
    :type spec: Specification
    :type data: InputData
    """

    generator = {
        u"file_test_results": file_test_results
    }

    logging.info(u"Generating the files ...")
    for file_spec in spec.files:
        try:
            generator[file_spec[u"algorithm"]](file_spec, data)
        except (NameError, KeyError) as err:
            logging.error(
                f"Probably algorithm {file_spec[u'algorithm']} is not defined: "
                f"{repr(err)}"
            )
    logging.info(u"Done.")


def _tests_in_suite(suite_name, tests):
    """Check if the suite includes tests.

    :param suite_name: Name of the suite to be checked.
    :param tests: Set of tests
    :type suite_name: str
    :type tests: pandas.Series
    :returns: True if the suite includes tests.
    :rtype: bool
    """

    for key in tests.keys():
        if suite_name == tests[key][u"parent"]:
            return True
    return False


def file_test_results(file_spec, input_data):
    """Generate the file(s) with algorithms
    - file_test_results
    specified in the specification file.

    :param file_spec: File to generate.
    :param input_data: Data to process.
    :type file_spec: pandas.Series
    :type input_data: InputData
    """

    file_name = f"{file_spec[u'output-file']}{file_spec[u'output-file-ext']}"
    rst_header = file_spec[u"file-header"]

    logging.info(f"  Generating the file {file_name} ...")

    table_lst = get_files(file_spec[u"dir-tables"], u".csv", full_path=True)
    if not table_lst:
        logging.error(
            f"  No tables to include in {file_spec['dir-tables']}. Skipping."
        )
        return

    logging.info(f"    Writing file {file_name}")

    logging.info(
        f"    Creating the tests data set for the "
        f"{file_spec.get(u'type', u'')} {file_spec.get(u'title', u'')}."
    )
    tests = input_data.filter_data(file_spec)
    tests = input_data.merge_data(tests)

    logging.info(
        f"    Creating the suites data set for the "
        f"{file_spec.get(u'type', u'')} {file_spec.get(u'title', u'')}."
    )
    file_spec[u"filter"] = u"all"
    suites = input_data.filter_data(file_spec, data_set=u"suites")
    suites = input_data.merge_data(suites)
    suites.sort_index(inplace=True)

    with open(file_name, u"w") as file_handler:
        file_handler.write(rst_header)
        for suite_longname, suite in suites.items():
            if len(suite_longname.split(".")) <= file_spec[u"data-start-level"]:
                continue

            title_line = \
                get_rst_title_char(
                    suite[u"level"] - file_spec[u"data-start-level"] - 1
                ) * len(suite[u"name"])
            if not (u"-ndrpdr" in suite[u"name"] or
                    u"-mrr" in suite[u"name"] or
                    u"-func" in suite[u"name"] or
                    u"-device" in suite[u"name"]):
                file_handler.write(f"\n{suite[u'name']}\n{title_line}\n")

            if _tests_in_suite(suite[u"name"], tests):
                file_handler.write(f"\n{suite[u'name']}\n{title_line}\n")
                file_handler.write(
                    f"\n{suite[u'doc']}\n".replace(u'|br|', u'\n\n -')
                )
                for tbl_file in table_lst:
                    if suite[u"name"] in tbl_file:
                        file_handler.write(
                            RST_INCLUDE_TABLE.format(
                                file_latex=tbl_file,
                                file_html=tbl_file.split("/")[-1]))

    logging.info(u"  Done.")
