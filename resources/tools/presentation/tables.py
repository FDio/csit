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

"""Algorithms to generate tables.
"""


import logging

from errors import PresentationError
from utils import mean, stdev, relative_change


def generate_tables(config, data):
    """Generate all tables specified in the specification file.

    :param config: Configuration read from the specification file.
    :param data: Data to process.
    :type config: Configuration
    :type data: InputData
    """

    logging.info("Generating the tables ...")
    for table in config.tables:
        try:
            eval(table["algorithm"])(table, data)
        except NameError:
            logging.error("The algorithm '{0}' is not defined.".
                          format(table["algorithm"]))
    logging.info("Done.")


def table_details(table, input_data):
    """Generate the table(s) with algorithm: table_detailed_test_results
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the table {0} ...".
                 format(table.get("title", "")))

    # Transform the data
    data = input_data.filter_data(table)

    # Prepare the header of the tables
    header = list()
    for column in table["columns"]:
        header.append('"{0}"'.format(str(column["title"]).replace('"', '""')))

    # Generate the data for the table according to the model in the table
    # specification

    job = table["data"].keys()[0]
    build = str(table["data"][job][0])
    for suite_name in input_data.suites(job, build).keys():
        # Generate data
        table_lst = list()
        for test in data[job][build].keys():
            if data[job][build][test]["parent"] in suite_name:
                row_lst = list()
                for column in table["columns"]:
                    try:
                        row_lst.append('"{0}"'.format(
                            str(data[job][build][test][column["data"].
                                split(" ")[1]]).replace('"', '""')))
                    except KeyError:
                        row_lst.append("No data")
                table_lst.append(row_lst)

        # Write the data to file
        if table_lst:
            file_name = "{0}_{1}{2}".format(table["output-file"], suite_name,
                                            table["output-file-ext"])
            logging.info("      Writing file: '{}'".format(file_name))
            with open(file_name, "w") as file_handler:
                file_handler.write(",".join(header) + "\n")
                for item in table_lst:
                    file_handler.write(",".join(item) + "\n")

    logging.info("  Done.")


def table_performance_improvements(table, input_data):
    """Generate the table(s) with algorithm: table_performance_improvements
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    def _write_line_to_file(file_handler, data):
        """Write a line to the .csv file.

        :param file_handler: File handler for the csv file. It must be open for
         writing text.
        :param data: Item to be written to the file.
        :type file_handler: BinaryIO
        :type data: list
        """

        line_lst = list()
        for item in data:
            if isinstance(item["data"], str):
                line_lst.append(item["data"])
            elif isinstance(item["data"], float):
                line_lst.append("{:.1f}".format(item["data"]))
        file_handler.write(",".join(line_lst) + "\n")

    logging.info("  Generating the table {0} ...".
                 format(table.get("title", "")))

    # Read the template
    file_name = table.get("template", None)
    if file_name:
        try:
            tmpl = _read_csv_template(file_name)
        except PresentationError:
            logging.error("  The template '{0}' does not exist. Skipping the "
                          "table.".format(file_name))
            return None
    else:
        logging.error("The template is not defined. Skipping the table.")
        return None

    # Transform the data
    data = input_data.filter_data(table)

    # Prepare the header of the tables
    header = list()
    for column in table["columns"]:
        header.append(column["title"])

    # Generate the data for the table according to the model in the table
    # specification
    tbl_lst = list()
    for tmpl_item in tmpl:
        tbl_item = list()
        for column in table["columns"]:
            cmd = column["data"].split(" ")[0]
            args = column["data"].split(" ")[1:]
            if cmd == "template":
                try:
                    val = float(tmpl_item[int(args[0])])
                except ValueError:
                    val = tmpl_item[int(args[0])]
                tbl_item.append({"data": val})
            elif cmd == "data":
                job = args[0]
                operation = args[1]
                data_lst = list()
                for build in data[job]:
                    try:
                        data_lst.append(float(build[tmpl_item[0]]["throughput"]
                                              ["value"]) / 1000000)
                    except KeyError:
                        pass
                if data_lst:
                    tbl_item.append({"data": eval(operation)(data_lst)})
            elif cmd == "operation":
                operation = args[0]
                nr1 = tbl_item[int(args[1])]["data"]
                nr2 = tbl_item[int(args[2])]["data"]
                if nr1 and nr2:
                    tbl_item.append({"data": eval(operation)(nr1, nr2)})
                else:
                    tbl_item.append({"data": None})
            else:
                logging.error("Not supported command {0}. Skipping the table.".
                              format(cmd))
                return None
        tbl_lst.append(tbl_item)

    # Sort the table according to the relative change
    tbl_lst.sort(key=lambda rel: rel[-1]["data"], reverse=True)

    # Create the tables and write them to the files
    file_names = [
        "{0}_ndr_top{1}".format(table["output-file"], table["output-file-ext"]),
        "{0}_pdr_top{1}".format(table["output-file"], table["output-file-ext"]),
        "{0}_ndr_low{1}".format(table["output-file"], table["output-file-ext"]),
        "{0}_pdr_low{1}".format(table["output-file"], table["output-file-ext"])
    ]

    for file_name in file_names:
        logging.info("    Writing the file '{0}'".format(file_name))
        with open(file_name, "w") as file_handler:
            file_handler.write(",".join(header) + "\n")
            for item in tbl_lst:
                if "ndr_top" in file_name \
                        and "ndr" in item[1]["data"] \
                        and item[-1]["data"] >= 10:
                    _write_line_to_file(file_handler, item)
                elif "pdr_top" in file_name \
                        and "pdr" in item[1]["data"] \
                        and item[-1]["data"] >= 10:
                    _write_line_to_file(file_handler, item)
                elif "ndr_low" in file_name \
                        and "ndr" in item[1]["data"] \
                        and item[-1]["data"] < 10:
                    _write_line_to_file(file_handler, item)
                elif "pdr_low" in file_name \
                        and "pdr" in item[1]["data"] \
                        and item[-1]["data"] < 10:
                    _write_line_to_file(file_handler, item)

    logging.info("  Done.")


def _read_csv_template(file_name):
    """Read the template from a .csv file.

    :param file_name: Name / full path / relative path of the file to read.
    :type file_name: str
    :returns: Data from the template as list (lines) of lists (items on line).
    :rtype: list
    :raises: PresentationError if it is not possible to read the file.
    """

    try:
        with open(file_name, 'r') as csv_file:
            tmpl_data = list()
            for line in csv_file:
                tmpl_data.append(line[:-1].split(","))
        return tmpl_data
    except IOError as err:
        raise PresentationError(str(err), level="ERROR")
