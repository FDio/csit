# Copyright (c) 2017 Cisco and/or its affiliates.
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

from utils import get_files, get_rst_title_char


def generate_files(spec, data):
    """Generate all files specified in the specification file.

    :param spec: Specification read from the specification file.
    :param data: Data to process.
    :type spec: Specification
    :type data: InputData
    """

    logging.info("Generating the files ...")
    for file_spec in spec.files:
        try:
            eval(file_spec["algorithm"])(file_spec, data)
        except NameError:
            logging.error("The algorithm '{0}' is not defined.".
                          format(file_spec["algorithm"]))
    logging.info("Done.")


def file_test_results(file_spec, input_data):
    """Generate the file(s) with algorithm: file_test_results specified in the
    specification file.

    :param file_spec: File to generate.
    :param input_data: Data to process.
    :type file_spec: pandas.Series
    :type input_data: InputData
    """

    def tests_in_suite(suite_name, tests):
        """Check if the suite includes tests.

        :param suite_name: Name of the suite to be checked.
        :param tests: Set of tests
        :type suite_name: str
        :type tests: pandas.Series
        :returns: True if the suite includes tests.
        :rtype: bool
        """

        for key in tests.keys():
            if suite_name == tests[key]["parent"]:
                return True
        return False

    file_name = "{0}{1}".format(file_spec["output-file"],
                                file_spec["output-file-ext"])
    rst_header = file_spec["file-header"]
    rst_include_table = ("\n.. csv-table::\n"
                         "    :header-rows: 1\n"
                         "    :widths: auto\n"
                         "    :align: center\n"
                         "    :file: {file}\n\n")

    logging.info("  Generating the file {0} ...".format(file_name))

    table_lst = get_files(file_spec["dir-tables"], ".csv", full_path=False)
    if len(table_lst) == 0:
        logging.error("  No tables to include in '{0}'. Skipping.".
                      format(file_spec["dir-tables"]))
        return None

    job = file_spec["data"].keys()[0]
    build = str(file_spec["data"][job][0])

    logging.info("    Writing file '{0}'".format(file_name))

    suites = input_data.suites(job, build)[file_spec["data-start-level"]:]
    suites.sort_index(inplace=True)

    with open(file_name, "w") as file_handler:
        file_handler.write(rst_header)
        for suite_longname, suite in suites.iteritems():
            suite_name = suite["name"]
            file_handler.write("\n{0}\n{1}\n".format(
                suite_name, get_rst_title_char(
                    suite["level"] - file_spec["data-start-level"] - 1) *
                            len(suite_name)))
            file_handler.write("\n{0}\n".format(
                suite["doc"].replace('|br|', '\n\n -')))
            if tests_in_suite(suite_name, input_data.tests(job, build)):
                for tbl_file in table_lst:
                    if suite_name in tbl_file:
                        file_handler.write(rst_include_table.
                                           format(file=tbl_file))

    logging.info("  Done.")
