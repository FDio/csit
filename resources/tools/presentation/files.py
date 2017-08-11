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


def generate_files(config, data):
    """Generate all files specified in the specification file.

    :param config: Configuration read from the specification file.
    :param data: Data to process.
    :type config: Configuration
    :type data: InputData
    """

    logging.info("Generating the files ...")
    for file_spec in config.files:
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

    file_name = "{0}{1}".format(file_spec["output-file"],
                                file_spec["output-file-ext"])
    rst_header = "\n.. |br| raw:: html\n    <br />\n"
    rst_include_table = "\n.. csv-table::\n" \
                        "    :align: center\n" \
                        "    :file: {file}\n\n"

    logging.info("  Generating the file {0} ...".format(file_name))

    table_lst = get_files(file_spec["dir-tables"], ".csv")
    if len(table_lst) == 0:
        logging.error("  No tables to include in '{0}'. Skipping.".
                      format(file_spec["dir-tables"]))
        return None

    data = input_data.filter_data(file_spec, data_set="suites")

    job = file_spec["data"].keys()[0]
    build = str(file_spec["data"][job][0])

    logging.info("    Writing file '{0}'".format(file_name))
    if "parents" in file_spec["chapters"]:
        parents = set()
        for suite in data[job][build]:
            parents.add(suite["parent"])
        with open(file_name, "w") as file_handler:
            file_handler.write(rst_header)
            for parent in parents:
                level = file_spec["start-level"]
                for chapter in file_spec["chapters"]:
                    if chapter == "parents":
                        file_handler.write("\n{0}\n{1}\n".format(
                            parent, get_rst_title_char(level) * len(parent)))
                    elif chapter == "suites":
                        for suite in data[job][build].keys():
                            if data[job][build][suite]["parent"] in parent:
                                file_handler.write("\n{0}\n{1}\n".format(
                                    suite,
                                    get_rst_title_char(level + 1) * len(suite)))
                                file_handler.write("\n{0}\n".format(
                                    data[job][build][suite]["doc"]))
                                for tbl_file in table_lst:
                                    if suite in tbl_file:
                                        file_handler.write(
                                            rst_include_table.format(
                                                file=tbl_file))
                    else:
                        logging.error(
                            "  The chapter '{0}' is not defined. Skipped.")
    else:
        with open(file_name, "w") as file_handler:
            file_handler.write(rst_header)
            level = file_spec["start-level"]
            for suite in data[job][build].keys():
                file_handler.write("\n{0}\n{1}\n".format(
                    suite, get_rst_title_char(level) * len(suite)))
                file_handler.write("\n{0}\n".format(
                    data[job][build][suite]["doc"]))
                for tbl_file in table_lst:
                    if suite in tbl_file:
                        file_handler.write(rst_include_table.
                                           format(file=tbl_file))
    logging.info("  Done.")
