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
import csv
import prettytable
import pandas as pd

from string import replace
from math import isnan
from xml.etree import ElementTree as ET

from errors import PresentationError
from utils import mean, stdev, relative_change, remove_outliers, split_outliers


def generate_tables(spec, data):
    """Generate all tables specified in the specification file.

    :param spec: Specification read from the specification file.
    :param data: Data to process.
    :type spec: Specification
    :type data: InputData
    """

    logging.info("Generating the tables ...")
    for table in spec.tables:
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
    try:
        suites = input_data.suites(job, build)
    except KeyError:
        logging.error("    No data available. The table will not be generated.")
        return

    for suite_longname, suite in suites.iteritems():
        # Generate data
        suite_name = suite["name"]
        table_lst = list()
        for test in data[job][build].keys():
            if data[job][build][test]["parent"] in suite_name:
                row_lst = list()
                for column in table["columns"]:
                    try:
                        col_data = str(data[job][build][test][column["data"].
                                       split(" ")[1]]).replace('"', '""')
                        if column["data"].split(" ")[1] in ("vat-history",
                                                            "show-run"):
                            col_data = replace(col_data, " |br| ", "",
                                               maxreplace=1)
                            col_data = " |prein| {0} |preout| ".\
                                format(col_data[:-5])
                        row_lst.append('"{0}"'.format(col_data))
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


def table_merged_details(table, input_data):
    """Generate the table(s) with algorithm: table_merged_details
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
    data = input_data.merge_data(data)
    data.sort_index(inplace=True)

    suites = input_data.filter_data(table, data_set="suites")
    suites = input_data.merge_data(suites)

    # Prepare the header of the tables
    header = list()
    for column in table["columns"]:
        header.append('"{0}"'.format(str(column["title"]).replace('"', '""')))

    for _, suite in suites.iteritems():
        # Generate data
        suite_name = suite["name"]
        table_lst = list()
        for test in data.keys():
            if data[test]["parent"] in suite_name:
                row_lst = list()
                for column in table["columns"]:
                    try:
                        col_data = str(data[test][column["data"].
                                       split(" ")[1]]).replace('"', '""')
                        if column["data"].split(" ")[1] in ("vat-history",
                                                            "show-run"):
                            col_data = replace(col_data, " |br| ", "",
                                               maxreplace=1)
                            col_data = " |prein| {0} |preout| ".\
                                format(col_data[:-5])
                        row_lst.append('"{0}"'.format(col_data))
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
                # Remove -?drdisc from the end
                if item["data"].endswith("drdisc"):
                    item["data"] = item["data"][:-8]
                line_lst.append(item["data"])
            elif isinstance(item["data"], float):
                line_lst.append("{:.1f}".format(item["data"]))
            elif item["data"] is None:
                line_lst.append("")
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
                jobs = args[0:-1]
                operation = args[-1]
                data_lst = list()
                for job in jobs:
                    for build in data[job]:
                        try:
                            data_lst.append(float(build[tmpl_item[0]]
                                                  ["throughput"]["value"]))
                        except (KeyError, TypeError):
                            # No data, ignore
                            continue
                if data_lst:
                    tbl_item.append({"data": (eval(operation)(data_lst)) /
                                             1000000})
                else:
                    tbl_item.append({"data": None})
            elif cmd == "operation":
                operation = args[0]
                try:
                    nr1 = float(tbl_item[int(args[1])]["data"])
                    nr2 = float(tbl_item[int(args[2])]["data"])
                    if nr1 and nr2:
                        tbl_item.append({"data": eval(operation)(nr1, nr2)})
                    else:
                        tbl_item.append({"data": None})
                except (IndexError, ValueError, TypeError):
                    logging.error("No data for {0}".format(tbl_item[0]["data"]))
                    tbl_item.append({"data": None})
                    continue
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
                if isinstance(item[-1]["data"], float):
                    rel_change = round(item[-1]["data"], 1)
                else:
                    rel_change = item[-1]["data"]
                if "ndr_top" in file_name \
                        and "ndr" in item[0]["data"] \
                        and rel_change >= 10.0:
                    _write_line_to_file(file_handler, item)
                elif "pdr_top" in file_name \
                        and "pdr" in item[0]["data"] \
                        and rel_change >= 10.0:
                    _write_line_to_file(file_handler, item)
                elif "ndr_low" in file_name \
                        and "ndr" in item[0]["data"] \
                        and rel_change < 10.0:
                    _write_line_to_file(file_handler, item)
                elif "pdr_low" in file_name \
                        and "pdr" in item[0]["data"] \
                        and rel_change < 10.0:
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


def table_performance_comparison(table, input_data):
    """Generate the table(s) with algorithm: table_performance_comparison
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the table {0} ...".
                 format(table.get("title", "")))

    # Transform the data
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the tables
    try:
        header = ["Test case",
                  "{0} Throughput [Mpps]".format(table["reference"]["title"]),
                  "{0} stdev [Mpps]".format(table["reference"]["title"]),
                  "{0} Throughput [Mpps]".format(table["compare"]["title"]),
                  "{0} stdev [Mpps]".format(table["compare"]["title"]),
                  "Change [%]"]
        header_str = ",".join(header) + "\n"
    except (AttributeError, KeyError) as err:
        logging.error("The model is invalid, missing parameter: {0}".
                      format(err))
        return

    # Prepare data to the table:
    tbl_dict = dict()
    for job, builds in table["reference"]["data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].iteritems():
                if tbl_dict.get(tst_name, None) is None:
                    name = "{0}-{1}".format(tst_data["parent"].split("-")[0],
                                            "-".join(tst_data["name"].
                                                     split("-")[1:]))
                    tbl_dict[tst_name] = {"name": name,
                                          "ref-data": list(),
                                          "cmp-data": list()}
                try:
                    tbl_dict[tst_name]["ref-data"].\
                        append(tst_data["throughput"]["value"])
                except TypeError:
                    pass  # No data in output.xml for this test

    for job, builds in table["compare"]["data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].iteritems():
                try:
                    tbl_dict[tst_name]["cmp-data"].\
                        append(tst_data["throughput"]["value"])
                except KeyError:
                    pass
                except TypeError:
                    tbl_dict.pop(tst_name, None)

    tbl_lst = list()
    for tst_name in tbl_dict.keys():
        item = [tbl_dict[tst_name]["name"], ]
        if tbl_dict[tst_name]["ref-data"]:
            data_t = remove_outliers(tbl_dict[tst_name]["ref-data"],
                                     outlier_const=table["outlier-const"])
            # TODO: Specify window size.
            if data_t:
                item.append(round(mean(data_t) / 1000000, 2))
                item.append(round(stdev(data_t) / 1000000, 2))
            else:
                item.extend([None, None])
        else:
            item.extend([None, None])
        if tbl_dict[tst_name]["cmp-data"]:
            data_t = remove_outliers(tbl_dict[tst_name]["cmp-data"],
                                     outlier_const=table["outlier-const"])
            # TODO: Specify window size.
            if data_t:
                item.append(round(mean(data_t) / 1000000, 2))
                item.append(round(stdev(data_t) / 1000000, 2))
            else:
                item.extend([None, None])
        else:
            item.extend([None, None])
        if item[1] is not None and item[3] is not None:
            item.append(int(relative_change(float(item[1]), float(item[3]))))
        if len(item) == 6:
            tbl_lst.append(item)

    # Sort the table according to the relative change
    tbl_lst.sort(key=lambda rel: rel[-1], reverse=True)

    # Generate tables:
    # All tests in csv:
    tbl_names = ["{0}-ndr-1t1c-full{1}".format(table["output-file"],
                                               table["output-file-ext"]),
                 "{0}-ndr-2t2c-full{1}".format(table["output-file"],
                                               table["output-file-ext"]),
                 "{0}-ndr-4t4c-full{1}".format(table["output-file"],
                                               table["output-file-ext"]),
                 "{0}-pdr-1t1c-full{1}".format(table["output-file"],
                                               table["output-file-ext"]),
                 "{0}-pdr-2t2c-full{1}".format(table["output-file"],
                                               table["output-file-ext"]),
                 "{0}-pdr-4t4c-full{1}".format(table["output-file"],
                                               table["output-file-ext"])
                 ]
    for file_name in tbl_names:
        logging.info("      Writing file: '{0}'".format(file_name))
        with open(file_name, "w") as file_handler:
            file_handler.write(header_str)
            for test in tbl_lst:
                if (file_name.split("-")[-3] in test[0] and    # NDR vs PDR
                        file_name.split("-")[-2] in test[0]):  # cores
                    test[0] = "-".join(test[0].split("-")[:-1])
                    file_handler.write(",".join([str(item) for item in test]) +
                                       "\n")

    # All tests in txt:
    tbl_names_txt = ["{0}-ndr-1t1c-full.txt".format(table["output-file"]),
                     "{0}-ndr-2t2c-full.txt".format(table["output-file"]),
                     "{0}-ndr-4t4c-full.txt".format(table["output-file"]),
                     "{0}-pdr-1t1c-full.txt".format(table["output-file"]),
                     "{0}-pdr-2t2c-full.txt".format(table["output-file"]),
                     "{0}-pdr-4t4c-full.txt".format(table["output-file"])
                     ]

    for i, txt_name in enumerate(tbl_names_txt):
        txt_table = None
        logging.info("      Writing file: '{0}'".format(txt_name))
        with open(tbl_names[i], 'rb') as csv_file:
            csv_content = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in csv_content:
                if txt_table is None:
                    txt_table = prettytable.PrettyTable(row)
                else:
                    txt_table.add_row(row)
            txt_table.align["Test case"] = "l"
        with open(txt_name, "w") as txt_file:
            txt_file.write(str(txt_table))

    # Selected tests in csv:
    input_file = "{0}-ndr-1t1c-full{1}".format(table["output-file"],
                                               table["output-file-ext"])
    with open(input_file, "r") as in_file:
        lines = list()
        for line in in_file:
            lines.append(line)

    output_file = "{0}-ndr-1t1c-top{1}".format(table["output-file"],
                                               table["output-file-ext"])
    logging.info("      Writing file: '{0}'".format(output_file))
    with open(output_file, "w") as out_file:
        out_file.write(header_str)
        for i, line in enumerate(lines[1:]):
            if i == table["nr-of-tests-shown"]:
                break
            out_file.write(line)

    output_file = "{0}-ndr-1t1c-bottom{1}".format(table["output-file"],
                                                  table["output-file-ext"])
    logging.info("      Writing file: '{0}'".format(output_file))
    with open(output_file, "w") as out_file:
        out_file.write(header_str)
        for i, line in enumerate(lines[-1:0:-1]):
            if i == table["nr-of-tests-shown"]:
                break
            out_file.write(line)

    input_file = "{0}-pdr-1t1c-full{1}".format(table["output-file"],
                                               table["output-file-ext"])
    with open(input_file, "r") as in_file:
        lines = list()
        for line in in_file:
            lines.append(line)

    output_file = "{0}-pdr-1t1c-top{1}".format(table["output-file"],
                                               table["output-file-ext"])
    logging.info("      Writing file: '{0}'".format(output_file))
    with open(output_file, "w") as out_file:
        out_file.write(header_str)
        for i, line in enumerate(lines[1:]):
            if i == table["nr-of-tests-shown"]:
                break
            out_file.write(line)

    output_file = "{0}-pdr-1t1c-bottom{1}".format(table["output-file"],
                                                  table["output-file-ext"])
    logging.info("      Writing file: '{0}'".format(output_file))
    with open(output_file, "w") as out_file:
        out_file.write(header_str)
        for i, line in enumerate(lines[-1:0:-1]):
            if i == table["nr-of-tests-shown"]:
                break
            out_file.write(line)


def table_performance_comparison_mrr(table, input_data):
    """Generate the table(s) with algorithm: table_performance_comparison_mrr
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the table {0} ...".
                 format(table.get("title", "")))

    # Transform the data
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the tables
    try:
        header = ["Test case",
                  "{0} Throughput [Mpps]".format(table["reference"]["title"]),
                  "{0} stdev [Mpps]".format(table["reference"]["title"]),
                  "{0} Throughput [Mpps]".format(table["compare"]["title"]),
                  "{0} stdev [Mpps]".format(table["compare"]["title"]),
                  "Change [%]"]
        header_str = ",".join(header) + "\n"
    except (AttributeError, KeyError) as err:
        logging.error("The model is invalid, missing parameter: {0}".
                      format(err))
        return

    # Prepare data to the table:
    tbl_dict = dict()
    for job, builds in table["reference"]["data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].iteritems():
                if tbl_dict.get(tst_name, None) is None:
                    name = "{0}-{1}".format(tst_data["parent"].split("-")[0],
                                            "-".join(tst_data["name"].
                                                     split("-")[1:]))
                    tbl_dict[tst_name] = {"name": name,
                                          "ref-data": list(),
                                          "cmp-data": list()}
                try:
                    tbl_dict[tst_name]["ref-data"].\
                        append(tst_data["result"]["throughput"])
                except TypeError:
                    pass  # No data in output.xml for this test

    for job, builds in table["compare"]["data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].iteritems():
                try:
                    tbl_dict[tst_name]["cmp-data"].\
                        append(tst_data["result"]["throughput"])
                except KeyError:
                    pass
                except TypeError:
                    tbl_dict.pop(tst_name, None)

    tbl_lst = list()
    for tst_name in tbl_dict.keys():
        item = [tbl_dict[tst_name]["name"], ]
        if tbl_dict[tst_name]["ref-data"]:
            data_t = remove_outliers(tbl_dict[tst_name]["ref-data"],
                                     outlier_const=table["outlier-const"])
            # TODO: Specify window size.
            if data_t:
                item.append(round(mean(data_t) / 1000000, 2))
                item.append(round(stdev(data_t) / 1000000, 2))
            else:
                item.extend([None, None])
        else:
            item.extend([None, None])
        if tbl_dict[tst_name]["cmp-data"]:
            data_t = remove_outliers(tbl_dict[tst_name]["cmp-data"],
                                     outlier_const=table["outlier-const"])
            # TODO: Specify window size.
            if data_t:
                item.append(round(mean(data_t) / 1000000, 2))
                item.append(round(stdev(data_t) / 1000000, 2))
            else:
                item.extend([None, None])
        else:
            item.extend([None, None])
        if item[1] is not None and item[3] is not None and item[1] != 0:
            item.append(int(relative_change(float(item[1]), float(item[3]))))
        if len(item) == 6:
            tbl_lst.append(item)

    # Sort the table according to the relative change
    tbl_lst.sort(key=lambda rel: rel[-1], reverse=True)

    # Generate tables:
    # All tests in csv:
    tbl_names = ["{0}-1t1c-full{1}".format(table["output-file"],
                                           table["output-file-ext"]),
                 "{0}-2t2c-full{1}".format(table["output-file"],
                                           table["output-file-ext"]),
                 "{0}-4t4c-full{1}".format(table["output-file"],
                                           table["output-file-ext"])
                 ]
    for file_name in tbl_names:
        logging.info("      Writing file: '{0}'".format(file_name))
        with open(file_name, "w") as file_handler:
            file_handler.write(header_str)
            for test in tbl_lst:
                if file_name.split("-")[-2] in test[0]:  # cores
                    test[0] = "-".join(test[0].split("-")[:-1])
                    file_handler.write(",".join([str(item) for item in test]) +
                                       "\n")

    # All tests in txt:
    tbl_names_txt = ["{0}-1t1c-full.txt".format(table["output-file"]),
                     "{0}-2t2c-full.txt".format(table["output-file"]),
                     "{0}-4t4c-full.txt".format(table["output-file"])
                     ]

    for i, txt_name in enumerate(tbl_names_txt):
        txt_table = None
        logging.info("      Writing file: '{0}'".format(txt_name))
        with open(tbl_names[i], 'rb') as csv_file:
            csv_content = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in csv_content:
                if txt_table is None:
                    txt_table = prettytable.PrettyTable(row)
                else:
                    txt_table.add_row(row)
            txt_table.align["Test case"] = "l"
        with open(txt_name, "w") as txt_file:
            txt_file.write(str(txt_table))


def table_performance_trending_dashboard(table, input_data):
    """Generate the table(s) with algorithm: table_performance_comparison
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the table {0} ...".
                 format(table.get("title", "")))

    # Transform the data
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the tables
    header = ["Test Case",
              "Throughput Trend [Mpps]",
              "Long Trend Compliance",
              "Trend Compliance",
              "Top Anomaly [Mpps]",
              "Change [%]",
              "Outliers [Number]"
              ]
    header_str = ",".join(header) + "\n"

    # Prepare data to the table:
    tbl_dict = dict()
    for job, builds in table["data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].iteritems():
                if tbl_dict.get(tst_name, None) is None:
                    name = "{0}-{1}".format(tst_data["parent"].split("-")[0],
                                            "-".join(tst_data["name"].
                                                     split("-")[1:]))
                    tbl_dict[tst_name] = {"name": name,
                                          "data": dict()}
                try:
                    tbl_dict[tst_name]["data"][str(build)] =  \
                        tst_data["result"]["throughput"]
                except (TypeError, KeyError):
                    pass  # No data in output.xml for this test

    tbl_lst = list()
    for tst_name in tbl_dict.keys():
        if len(tbl_dict[tst_name]["data"]) > 2:

            pd_data = pd.Series(tbl_dict[tst_name]["data"])
            win_size = min(pd_data.size, table["window"])
            # Test name:
            name = tbl_dict[tst_name]["name"]

            median = pd_data.rolling(window=win_size, min_periods=2).median()
            median_idx = pd_data.size - table["long-trend-window"]
            median_idx = 0 if median_idx < 0 else median_idx
            max_median = max(median.values[median_idx:])
            trimmed_data, _ = split_outliers(pd_data, outlier_const=1.5,
                                             window=win_size)
            stdev_t = pd_data.rolling(window=win_size, min_periods=2).std()

            rel_change_lst = [None, ]
            classification_lst = [None, ]
            median_lst = [None, ]
            sample_lst = [None, ]
            first = True
            for build_nr, value in pd_data.iteritems():
                if first:
                    first = False
                    continue
                # Relative changes list:
                if not isnan(value) \
                        and not isnan(median[build_nr]) \
                        and median[build_nr] != 0:
                    rel_change_lst.append(round(
                        relative_change(float(median[build_nr]), float(value)),
                        2))
                else:
                    rel_change_lst.append(None)

                # Classification list:
                if isnan(trimmed_data[build_nr]) \
                        or isnan(median[build_nr]) \
                        or isnan(stdev_t[build_nr]) \
                        or isnan(value):
                    classification_lst.append("outlier")
                elif value < (median[build_nr] - 3 * stdev_t[build_nr]):
                    classification_lst.append("regression")
                elif value > (median[build_nr] + 3 * stdev_t[build_nr]):
                    classification_lst.append("progression")
                else:
                    classification_lst.append("normal")
                sample_lst.append(value)
                median_lst.append(median[build_nr])

            last_idx = len(classification_lst) - 1
            first_idx = last_idx - int(table["evaluated-window"])
            if first_idx < 0:
                first_idx = 0

            nr_outliers = 0
            consecutive_outliers = 0
            failure = False
            for item in classification_lst[first_idx:]:
                if item == "outlier":
                    nr_outliers += 1
                    consecutive_outliers += 1
                    if consecutive_outliers == 3:
                        failure = True
                else:
                    consecutive_outliers = 0

            if failure:
                classification = "failure"
            elif "regression" in classification_lst[first_idx:]:
                classification = "regression"
            elif "progression" in classification_lst[first_idx:]:
                classification = "progression"
            else:
                classification = "normal"

            if classification == "normal":
                index = len(classification_lst) - 1
            else:
                tmp_classification = "outlier" if classification == "failure" \
                    else classification
                index = None
                for idx in range(first_idx, len(classification_lst)):
                    if classification_lst[idx] == tmp_classification:
                        if rel_change_lst[idx]:
                            index = idx
                            break
                if index is None:
                    continue
                for idx in range(index+1, len(classification_lst)):
                    if classification_lst[idx] == tmp_classification:
                        if rel_change_lst[idx]:
                            if (abs(rel_change_lst[idx]) >
                                    abs(rel_change_lst[index])):
                                index = idx

            logging.debug("{}".format(name))
            logging.debug("sample_lst: {} - {}".
                          format(len(sample_lst), sample_lst))
            logging.debug("median_lst: {} - {}".
                          format(len(median_lst), median_lst))
            logging.debug("rel_change: {} - {}".
                          format(len(rel_change_lst), rel_change_lst))
            logging.debug("classn_lst: {} - {}".
                          format(len(classification_lst), classification_lst))
            logging.debug("index:      {}".format(index))
            logging.debug("classifica: {}".format(classification))

            try:
                trend = round(float(median_lst[-1]) / 1000000, 2) \
                    if not isnan(median_lst[-1]) else '-'
                sample = round(float(sample_lst[index]) / 1000000, 2) \
                    if not isnan(sample_lst[index]) else '-'
                rel_change = rel_change_lst[index] \
                    if rel_change_lst[index] is not None else '-'
                if not isnan(max_median):
                    if not isnan(sample_lst[index]):
                        long_trend_threshold = \
                            max_median * (table["long-trend-threshold"] / 100)
                        if sample_lst[index] < long_trend_threshold:
                            long_trend_classification = "failure"
                        else:
                            long_trend_classification = 'normal'
                    else:
                        long_trend_classification = "failure"
                else:
                    long_trend_classification = '-'
                tbl_lst.append([name,
                                trend,
                                long_trend_classification,
                                classification,
                                '-' if classification == "normal" else sample,
                                '-' if classification == "normal" else
                                rel_change,
                                nr_outliers])
            except IndexError as err:
                logging.error("{}".format(err))
                continue

    # Sort the table according to the classification
    tbl_sorted = list()
    for long_trend_class in ("failure", '-'):
        tbl_long = [item for item in tbl_lst if item[2] == long_trend_class]
        for classification in \
                ("failure", "regression", "progression", "normal"):
            tbl_tmp = [item for item in tbl_long if item[3] == classification]
            tbl_tmp.sort(key=lambda rel: rel[0])
            tbl_sorted.extend(tbl_tmp)

    file_name = "{0}{1}".format(table["output-file"], table["output-file-ext"])

    logging.info("      Writing file: '{0}'".format(file_name))
    with open(file_name, "w") as file_handler:
        file_handler.write(header_str)
        for test in tbl_sorted:
            file_handler.write(",".join([str(item) for item in test]) + '\n')

    txt_file_name = "{0}.txt".format(table["output-file"])
    txt_table = None
    logging.info("      Writing file: '{0}'".format(txt_file_name))
    with open(file_name, 'rb') as csv_file:
        csv_content = csv.reader(csv_file, delimiter=',', quotechar='"')
        for row in csv_content:
            if txt_table is None:
                txt_table = prettytable.PrettyTable(row)
            else:
                txt_table.add_row(row)
        txt_table.align["Test case"] = "l"
    with open(txt_file_name, "w") as txt_file:
        txt_file.write(str(txt_table))


def table_performance_trending_dashboard_html(table, input_data):
    """Generate the table(s) with algorithm:
    table_performance_trending_dashboard_html specified in the specification
    file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the table {0} ...".
                 format(table.get("title", "")))

    try:
        with open(table["input-file"], 'rb') as csv_file:
            csv_content = csv.reader(csv_file, delimiter=',', quotechar='"')
            csv_lst = [item for item in csv_content]
    except KeyError:
        logging.warning("The input file is not defined.")
        return
    except csv.Error as err:
        logging.warning("Not possible to process the file '{0}'.\n{1}".
                        format(table["input-file"], err))
        return

    # Table:
    dashboard = ET.Element("table", attrib=dict(width="100%", border='0'))

    # Table header:
    tr = ET.SubElement(dashboard, "tr", attrib=dict(bgcolor="#7eade7"))
    for idx, item in enumerate(csv_lst[0]):
        alignment = "left" if idx == 0 else "center"
        th = ET.SubElement(tr, "th", attrib=dict(align=alignment))
        th.text = item

    # Rows:
    for r_idx, row in enumerate(csv_lst[1:]):
        background = "#D4E4F7" if r_idx % 2 else "white"
        tr = ET.SubElement(dashboard, "tr", attrib=dict(bgcolor=background))

        # Columns:
        for c_idx, item in enumerate(row):
            alignment = "left" if c_idx == 0 else "center"
            td = ET.SubElement(tr, "td", attrib=dict(align=alignment))
            # Name:
            url = "../trending/"
            file_name = ""
            anchor = "#"
            feature = ""
            if c_idx == 0:
                if "memif" in item:
                    file_name = "container_memif.html"

                elif "vhost" in item:
                    if "l2xcbase" in item or "l2bdbasemaclrn" in item:
                        file_name = "vm_vhost_l2.html"
                    elif "ip4base" in item:
                        file_name = "vm_vhost_ip4.html"

                elif "ipsec" in item:
                    file_name = "ipsec.html"

                elif "ethip4lispip" in item or "ethip4vxlan" in item:
                    file_name = "ip4_tunnels.html"

                elif "ip4base" in item or "ip4scale" in item:
                    file_name = "ip4.html"
                    if "iacl" in item or "snat" in item or "cop" in item:
                        feature = "-features"

                elif "ip6base" in item or "ip6scale" in item:
                    file_name = "ip6.html"

                elif "l2xcbase" in item or "l2xcscale" in item \
                        or "l2bdbasemaclrn" in item or "l2bdscale" in item \
                        or "l2dbbasemaclrn" in item or "l2dbscale" in item:
                    file_name = "l2.html"
                    if "iacl" in item:
                        feature = "-features"

                if "x520" in item:
                    anchor += "x520-"
                elif "x710" in item:
                    anchor += "x710-"
                elif "xl710" in item:
                    anchor += "xl710-"

                if "64b" in item:
                    anchor += "64b-"
                elif "78b" in item:
                    anchor += "78b"
                elif "imix" in item:
                    anchor += "imix-"
                elif "9000b" in item:
                    anchor += "9000b-"
                elif "1518" in item:
                    anchor += "1518b-"

                if "1t1c" in item:
                    anchor += "1t1c"
                elif "2t2c" in item:
                    anchor += "2t2c"
                elif "4t4c" in item:
                    anchor += "4t4c"

                url = url + file_name + anchor + feature

                ref = ET.SubElement(td, "a", attrib=dict(href=url))
                ref.text = item

            if c_idx == 3:
                if item == "regression":
                    td.set("bgcolor", "#eca1a6")
                elif item == "failure":
                    td.set("bgcolor", "#d6cbd3")
                elif item == "progression":
                    td.set("bgcolor", "#bdcebe")
            if c_idx > 0:
                td.text = item

    try:
        with open(table["output-file"], 'w') as html_file:
            logging.info("      Writing file: '{0}'".
                         format(table["output-file"]))
            html_file.write(".. raw:: html\n\n\t")
            html_file.write(ET.tostring(dashboard))
            html_file.write("\n\t<p><br><br></p>\n")
    except KeyError:
        logging.warning("The output file is not defined.")
        return
