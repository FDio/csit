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
        u"file_test_results": file_test_results,
        u"file_test_results_html": file_test_results_html
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


def file_test_results(file_spec, input_data, frmt=u"rst"):
    """Generate the file(s) with algorithms
    - file_test_results
    specified in the specification file.

    :param file_spec: File to generate.
    :param input_data: Data to process.
    :param frmt: Format can be: rst or html
    :type file_spec: pandas.Series
    :type input_data: InputData
    :type frmt: str
    """

    base_file_name = f"{file_spec[u'output-file']}"
    rst_header = file_spec.get(u"file-header", u"")
    start_lvl = file_spec.get(u"data-start-level", 4)

    logging.info(f"  Generating the file {base_file_name} ...")

    if frmt == u"html":
        table_lst = get_files(file_spec[u"dir-tables"], u".rst", full_path=True)
    elif frmt == u"rst":
        table_lst = get_files(file_spec[u"dir-tables"], u".csv", full_path=True)
    else:
        return
    if not table_lst:
        logging.error(
            f"  No tables to include in {file_spec[u'dir-tables']}. Skipping."
        )
        return

    logging.info(
        f"    Creating the tests data set for the "
        f"{file_spec.get(u'type', u'')} {file_spec.get(u'title', u'')}."
    )

    tests = input_data.filter_data(
        file_spec,
        params=[u"name", u"parent", u"doc", u"type", u"level"],
        continue_on_error=True
    )
    if tests.empty:
        return
    tests = input_data.merge_data(tests)
    tests.sort_index(inplace=True)

    suites = input_data.filter_data(
        file_spec,
        continue_on_error=True,
        data_set=u"suites"
    )
    if suites.empty:
        return
    suites = input_data.merge_data(suites)

    file_name = u""
    for suite_longname, suite in suites.items():

        suite_lvl = len(suite_longname.split(u"."))
        if suite_lvl < start_lvl:
            # Not interested in this suite
            continue

        if suite_lvl == start_lvl:
            # Our top-level suite
            chapter = suite_longname.split(u'.')[-1]
            file_name = f"{base_file_name}/{chapter}.rst"
            logging.info(f"    Writing file {file_name}")
            with open(f"{base_file_name}/index.rst", u"a") as file_handler:
                file_handler.write(f"    {chapter}\n")
            with open(file_name, u"a") as file_handler:
                file_handler.write(rst_header)

        title_line = get_rst_title_char(suite[u"level"] - start_lvl + 2) * \
            len(suite[u"name"])
        with open(file_name, u"a") as file_handler:
            if not (u"-ndrpdr" in suite[u"name"] or
                    u"-mrr" in suite[u"name"] or
                    u"-dev" in suite[u"name"]):
                file_handler.write(f"\n{suite[u'name']}\n{title_line}\n")

            if _tests_in_suite(suite[u"name"], tests):
                file_handler.write(f"\n{suite[u'name']}\n{title_line}\n")
                file_handler.write(
                    f"\n{suite[u'doc']}\n".replace(u'|br|', u'\n\n -')
                )
                for tbl_file in table_lst:
                    if suite[u"name"] in tbl_file:
                        if frmt == u"html":
                            file_handler.write(
                                f"\n.. include:: {tbl_file.split(u'/')[-1]}\n"
                            )
                        elif frmt == u"rst":
                            file_handler.write(
                                RST_INCLUDE_TABLE.format(
                                    file_latex=tbl_file,
                                    file_html=tbl_file.split(u"/")[-1])
                            )

    logging.info(u"  Done.")


def file_test_results_html(file_spec, input_data):
    """Generate the file(s) with algorithms
    - file_test_results_html
    specified in the specification file.

    :param file_spec: File to generate.
    :param input_data: Data to process.
    :type file_spec: pandas.Series
    :type input_data: InputData
    """
    file_test_results(file_spec, input_data, frmt=u"html")
