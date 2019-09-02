# Copyright (c) 2019 Cisco and/or its affiliates.
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
import re

from string import replace
from collections import OrderedDict
from numpy import nan, isnan
from xml.etree import ElementTree as ET
from datetime import datetime as dt
from datetime import timedelta

from utils import mean, stdev, relative_change, classify_anomalies, \
    convert_csv_to_pretty_txt, relative_change_stdev


REGEX_NIC = re.compile(r'\d*ge\dp\d\D*\d*')


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
        except NameError as err:
            logging.error("Probably algorithm '{alg}' is not defined: {err}".
                          format(alg=table["algorithm"], err=repr(err)))
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
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(table.get("type", ""), table.get("title", "")))
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
                        if column["data"].split(" ")[1] in ("conf-history",
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
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(table.get("type", ""), table.get("title", "")))
    data = input_data.filter_data(table)
    data = input_data.merge_data(data)
    data.sort_index(inplace=True)

    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(table.get("type", ""), table.get("title", "")))
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
                        col_data = replace(col_data, "No Data",
                                           "Not Captured     ")
                        if column["data"].split(" ")[1] in ("conf-history",
                                                            "show-run"):
                            col_data = replace(col_data, " |br| ", "",
                                               maxreplace=1)
                            col_data = " |prein| {0} |preout| ".\
                                format(col_data[:-5])
                        row_lst.append('"{0}"'.format(col_data))
                    except KeyError:
                        row_lst.append('"Not captured"')
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
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(table.get("type", ""), table.get("title", "")))
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the tables
    try:
        header = ["Test case", ]

        if table["include-tests"] == "MRR":
            hdr_param = "Receive Rate"
        else:
            hdr_param = "Throughput"

        history = table.get("history", None)
        if history:
            for item in history:
                header.extend(
                    ["{0} {1} [Mpps]".format(item["title"], hdr_param),
                     "{0} Stdev [Mpps]".format(item["title"])])
        header.extend(
            ["{0} {1} [Mpps]".format(table["reference"]["title"], hdr_param),
             "{0} Stdev [Mpps]".format(table["reference"]["title"]),
             "{0} {1} [Mpps]".format(table["compare"]["title"], hdr_param),
             "{0} Stdev [Mpps]".format(table["compare"]["title"]),
             "Delta [%]"])
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
                tst_name_mod = tst_name.replace("-ndrpdrdisc", "").\
                    replace("-ndrpdr", "").replace("-pdrdisc", "").\
                    replace("-ndrdisc", "").replace("-pdr", "").\
                    replace("-ndr", "").\
                    replace("1t1c", "1c").replace("2t1c", "1c").\
                    replace("2t2c", "2c").replace("4t2c", "2c").\
                    replace("4t4c", "4c").replace("8t4c", "4c")
                if "across topologies" in table["title"].lower():
                    tst_name_mod = tst_name_mod.replace("2n1l-", "")
                if tbl_dict.get(tst_name_mod, None) is None:
                    groups = re.search(REGEX_NIC, tst_data["parent"])
                    nic = groups.group(0) if groups else ""
                    name = "{0}-{1}".format(nic, "-".join(tst_data["name"].
                                                          split("-")[:-1]))
                    if "across testbeds" in table["title"].lower() or \
                            "across topologies" in table["title"].lower():
                        name = name.\
                            replace("1t1c", "1c").replace("2t1c", "1c").\
                            replace("2t2c", "2c").replace("4t2c", "2c").\
                            replace("4t4c", "4c").replace("8t4c", "4c")
                    tbl_dict[tst_name_mod] = {"name": name,
                                              "ref-data": list(),
                                              "cmp-data": list()}
                try:
                    # TODO: Re-work when NDRPDRDISC tests are not used
                    if table["include-tests"] == "MRR":
                        tbl_dict[tst_name_mod]["ref-data"]. \
                            append(tst_data["result"]["receive-rate"].avg)
                    elif table["include-tests"] == "PDR":
                        if tst_data["type"] == "PDR":
                            tbl_dict[tst_name_mod]["ref-data"]. \
                                append(tst_data["throughput"]["value"])
                        elif tst_data["type"] == "NDRPDR":
                            tbl_dict[tst_name_mod]["ref-data"].append(
                                tst_data["throughput"]["PDR"]["LOWER"])
                    elif table["include-tests"] == "NDR":
                        if tst_data["type"] == "NDR":
                            tbl_dict[tst_name_mod]["ref-data"]. \
                                append(tst_data["throughput"]["value"])
                        elif tst_data["type"] == "NDRPDR":
                            tbl_dict[tst_name_mod]["ref-data"].append(
                                tst_data["throughput"]["NDR"]["LOWER"])
                    else:
                        continue
                except TypeError:
                    pass  # No data in output.xml for this test

    for job, builds in table["compare"]["data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].iteritems():
                tst_name_mod = tst_name.replace("-ndrpdrdisc", ""). \
                    replace("-ndrpdr", "").replace("-pdrdisc", ""). \
                    replace("-ndrdisc", "").replace("-pdr", ""). \
                    replace("-ndr", "").\
                    replace("1t1c", "1c").replace("2t1c", "1c").\
                    replace("2t2c", "2c").replace("4t2c", "2c").\
                    replace("4t4c", "4c").replace("8t4c", "4c")
                if "across topologies" in table["title"].lower():
                    tst_name_mod = tst_name_mod.replace("2n1l-", "")
                try:
                    # TODO: Re-work when NDRPDRDISC tests are not used
                    if table["include-tests"] == "MRR":
                        tbl_dict[tst_name_mod]["cmp-data"]. \
                            append(tst_data["result"]["receive-rate"].avg)
                    elif table["include-tests"] == "PDR":
                        if tst_data["type"] == "PDR":
                            tbl_dict[tst_name_mod]["cmp-data"]. \
                                append(tst_data["throughput"]["value"])
                        elif tst_data["type"] == "NDRPDR":
                            tbl_dict[tst_name_mod]["cmp-data"].append(
                                tst_data["throughput"]["PDR"]["LOWER"])
                    elif table["include-tests"] == "NDR":
                        if tst_data["type"] == "NDR":
                            tbl_dict[tst_name_mod]["cmp-data"]. \
                                append(tst_data["throughput"]["value"])
                        elif tst_data["type"] == "NDRPDR":
                            tbl_dict[tst_name_mod]["cmp-data"].append(
                                tst_data["throughput"]["NDR"]["LOWER"])
                    else:
                        continue
                except KeyError:
                    pass
                except TypeError:
                    tbl_dict.pop(tst_name_mod, None)
    if history:
        for item in history:
            for job, builds in item["data"].items():
                for build in builds:
                    for tst_name, tst_data in data[job][str(build)].iteritems():
                        tst_name_mod = tst_name.replace("-ndrpdrdisc", ""). \
                            replace("-ndrpdr", "").replace("-pdrdisc", ""). \
                            replace("-ndrdisc", "").replace("-pdr", ""). \
                            replace("-ndr", "").\
                            replace("1t1c", "1c").replace("2t1c", "1c").\
                            replace("2t2c", "2c").replace("4t2c", "2c").\
                            replace("4t4c", "4c").replace("8t4c", "4c")
                        if "across topologies" in table["title"].lower():
                            tst_name_mod = tst_name_mod.replace("2n1l-", "")
                        if tbl_dict.get(tst_name_mod, None) is None:
                            continue
                        if tbl_dict[tst_name_mod].get("history", None) is None:
                            tbl_dict[tst_name_mod]["history"] = OrderedDict()
                        if tbl_dict[tst_name_mod]["history"].get(item["title"],
                                                             None) is None:
                            tbl_dict[tst_name_mod]["history"][item["title"]] = \
                                list()
                        try:
                            # TODO: Re-work when NDRPDRDISC tests are not used
                            if table["include-tests"] == "MRR":
                                tbl_dict[tst_name_mod]["history"][item["title"
                                ]].append(tst_data["result"]["receive-rate"].
                                          avg)
                            elif table["include-tests"] == "PDR":
                                if tst_data["type"] == "PDR":
                                    tbl_dict[tst_name_mod]["history"][
                                        item["title"]].\
                                        append(tst_data["throughput"]["value"])
                                elif tst_data["type"] == "NDRPDR":
                                    tbl_dict[tst_name_mod]["history"][item[
                                        "title"]].append(tst_data["throughput"][
                                        "PDR"]["LOWER"])
                            elif table["include-tests"] == "NDR":
                                if tst_data["type"] == "NDR":
                                    tbl_dict[tst_name_mod]["history"][
                                        item["title"]].\
                                        append(tst_data["throughput"]["value"])
                                elif tst_data["type"] == "NDRPDR":
                                    tbl_dict[tst_name_mod]["history"][item[
                                        "title"]].append(tst_data["throughput"][
                                        "NDR"]["LOWER"])
                            else:
                                continue
                        except (TypeError, KeyError):
                            pass

    tbl_lst = list()
    for tst_name in tbl_dict.keys():
        item = [tbl_dict[tst_name]["name"], ]
        if history:
            if tbl_dict[tst_name].get("history", None) is not None:
                for hist_data in tbl_dict[tst_name]["history"].values():
                    if hist_data:
                        item.append(round(mean(hist_data) / 1000000, 2))
                        item.append(round(stdev(hist_data) / 1000000, 2))
                    else:
                        item.extend([None, None])
            else:
                item.extend([None, None])
        data_t = tbl_dict[tst_name]["ref-data"]
        if data_t:
            item.append(round(mean(data_t) / 1000000, 2))
            item.append(round(stdev(data_t) / 1000000, 2))
        else:
            item.extend([None, None])
        data_t = tbl_dict[tst_name]["cmp-data"]
        if data_t:
            item.append(round(mean(data_t) / 1000000, 2))
            item.append(round(stdev(data_t) / 1000000, 2))
        else:
            item.extend([None, None])
        if item[-4] is not None and item[-2] is not None and item[-4] != 0:
            item.append(int(relative_change(float(item[-4]), float(item[-2]))))
        if len(item) == len(header):
            tbl_lst.append(item)

    # Sort the table according to the relative change
    tbl_lst.sort(key=lambda rel: rel[-1], reverse=True)

    # Generate csv tables:
    csv_file = "{0}.csv".format(table["output-file"])
    with open(csv_file, "w") as file_handler:
        file_handler.write(header_str)
        for test in tbl_lst:
            file_handler.write(",".join([str(item) for item in test]) + "\n")

    convert_csv_to_pretty_txt(csv_file, "{0}.txt".format(table["output-file"]))


def table_performance_comparison_nic(table, input_data):
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
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(table.get("type", ""), table.get("title", "")))
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the tables
    try:
        header = ["Test case", ]

        if table["include-tests"] == "MRR":
            hdr_param = "Receive Rate"
        else:
            hdr_param = "Throughput"

        history = table.get("history", None)
        if history:
            for item in history:
                header.extend(
                    ["{0} {1} [Mpps]".format(item["title"], hdr_param),
                     "{0} Stdev [Mpps]".format(item["title"])])
        header.extend(
            ["{0} {1} [Mpps]".format(table["reference"]["title"], hdr_param),
             "{0} Stdev [Mpps]".format(table["reference"]["title"]),
             "{0} {1} [Mpps]".format(table["compare"]["title"], hdr_param),
             "{0} Stdev [Mpps]".format(table["compare"]["title"]),
             "Delta [%]"])
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
                if table["reference"]["nic"] not in tst_data["tags"]:
                    continue
                tst_name_mod = tst_name.replace("-ndrpdrdisc", "").\
                    replace("-ndrpdr", "").replace("-pdrdisc", "").\
                    replace("-ndrdisc", "").replace("-pdr", "").\
                    replace("-ndr", "").\
                    replace("1t1c", "1c").replace("2t1c", "1c").\
                    replace("2t2c", "2c").replace("4t2c", "2c").\
                    replace("4t4c", "4c").replace("8t4c", "4c")
                tst_name_mod = re.sub(REGEX_NIC, "", tst_name_mod)
                if "across topologies" in table["title"].lower():
                    tst_name_mod = tst_name_mod.replace("2n1l-", "")
                if tbl_dict.get(tst_name_mod, None) is None:
                    name = "{0}".format("-".join(tst_data["name"].
                                                 split("-")[:-1]))
                    if "across testbeds" in table["title"].lower() or \
                            "across topologies" in table["title"].lower():
                        name = name.\
                            replace("1t1c", "1c").replace("2t1c", "1c").\
                            replace("2t2c", "2c").replace("4t2c", "2c").\
                            replace("4t4c", "4c").replace("8t4c", "4c")
                    tbl_dict[tst_name_mod] = {"name": name,
                                              "ref-data": list(),
                                              "cmp-data": list()}
                try:
                    # TODO: Re-work when NDRPDRDISC tests are not used
                    if table["include-tests"] == "MRR":
                        tbl_dict[tst_name_mod]["ref-data"]. \
                            append(tst_data["result"]["receive-rate"].avg)
                    elif table["include-tests"] == "PDR":
                        if tst_data["type"] == "PDR":
                            tbl_dict[tst_name_mod]["ref-data"]. \
                                append(tst_data["throughput"]["value"])
                        elif tst_data["type"] == "NDRPDR":
                            tbl_dict[tst_name_mod]["ref-data"].append(
                                tst_data["throughput"]["PDR"]["LOWER"])
                    elif table["include-tests"] == "NDR":
                        if tst_data["type"] == "NDR":
                            tbl_dict[tst_name_mod]["ref-data"]. \
                                append(tst_data["throughput"]["value"])
                        elif tst_data["type"] == "NDRPDR":
                            tbl_dict[tst_name_mod]["ref-data"].append(
                                tst_data["throughput"]["NDR"]["LOWER"])
                    else:
                        continue
                except TypeError:
                    pass  # No data in output.xml for this test

    for job, builds in table["compare"]["data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].iteritems():
                if table["compare"]["nic"] not in tst_data["tags"]:
                    continue
                tst_name_mod = tst_name.replace("-ndrpdrdisc", ""). \
                    replace("-ndrpdr", "").replace("-pdrdisc", ""). \
                    replace("-ndrdisc", "").replace("-pdr", ""). \
                    replace("-ndr", "").\
                    replace("1t1c", "1c").replace("2t1c", "1c").\
                    replace("2t2c", "2c").replace("4t2c", "2c").\
                    replace("4t4c", "4c").replace("8t4c", "4c")
                tst_name_mod = re.sub(REGEX_NIC, "", tst_name_mod)
                if "across topologies" in table["title"].lower():
                    tst_name_mod = tst_name_mod.replace("2n1l-", "")
                try:
                    # TODO: Re-work when NDRPDRDISC tests are not used
                    if table["include-tests"] == "MRR":
                        tbl_dict[tst_name_mod]["cmp-data"]. \
                            append(tst_data["result"]["receive-rate"].avg)
                    elif table["include-tests"] == "PDR":
                        if tst_data["type"] == "PDR":
                            tbl_dict[tst_name_mod]["cmp-data"]. \
                                append(tst_data["throughput"]["value"])
                        elif tst_data["type"] == "NDRPDR":
                            tbl_dict[tst_name_mod]["cmp-data"].append(
                                tst_data["throughput"]["PDR"]["LOWER"])
                    elif table["include-tests"] == "NDR":
                        if tst_data["type"] == "NDR":
                            tbl_dict[tst_name_mod]["cmp-data"]. \
                                append(tst_data["throughput"]["value"])
                        elif tst_data["type"] == "NDRPDR":
                            tbl_dict[tst_name_mod]["cmp-data"].append(
                                tst_data["throughput"]["NDR"]["LOWER"])
                    else:
                        continue
                except (KeyError, TypeError):
                    pass

    if history:
        for item in history:
            for job, builds in item["data"].items():
                for build in builds:
                    for tst_name, tst_data in data[job][str(build)].iteritems():
                        if item["nic"] not in tst_data["tags"]:
                            continue
                        tst_name_mod = tst_name.replace("-ndrpdrdisc", ""). \
                            replace("-ndrpdr", "").replace("-pdrdisc", ""). \
                            replace("-ndrdisc", "").replace("-pdr", ""). \
                            replace("-ndr", "").\
                            replace("1t1c", "1c").replace("2t1c", "1c").\
                            replace("2t2c", "2c").replace("4t2c", "2c").\
                            replace("4t4c", "4c").replace("8t4c", "4c")
                        tst_name_mod = re.sub(REGEX_NIC, "", tst_name_mod)
                        if "across topologies" in table["title"].lower():
                            tst_name_mod = tst_name_mod.replace("2n1l-", "")
                        if tbl_dict.get(tst_name_mod, None) is None:
                            continue
                        if tbl_dict[tst_name_mod].get("history", None) is None:
                            tbl_dict[tst_name_mod]["history"] = OrderedDict()
                        if tbl_dict[tst_name_mod]["history"].get(item["title"],
                                                             None) is None:
                            tbl_dict[tst_name_mod]["history"][item["title"]] = \
                                list()
                        try:
                            # TODO: Re-work when NDRPDRDISC tests are not used
                            if table["include-tests"] == "MRR":
                                tbl_dict[tst_name_mod]["history"][item["title"
                                ]].append(tst_data["result"]["receive-rate"].
                                          avg)
                            elif table["include-tests"] == "PDR":
                                if tst_data["type"] == "PDR":
                                    tbl_dict[tst_name_mod]["history"][
                                        item["title"]].\
                                        append(tst_data["throughput"]["value"])
                                elif tst_data["type"] == "NDRPDR":
                                    tbl_dict[tst_name_mod]["history"][item[
                                        "title"]].append(tst_data["throughput"][
                                        "PDR"]["LOWER"])
                            elif table["include-tests"] == "NDR":
                                if tst_data["type"] == "NDR":
                                    tbl_dict[tst_name_mod]["history"][
                                        item["title"]].\
                                        append(tst_data["throughput"]["value"])
                                elif tst_data["type"] == "NDRPDR":
                                    tbl_dict[tst_name_mod]["history"][item[
                                        "title"]].append(tst_data["throughput"][
                                        "NDR"]["LOWER"])
                            else:
                                continue
                        except (TypeError, KeyError):
                            pass

    tbl_lst = list()
    for tst_name in tbl_dict.keys():
        item = [tbl_dict[tst_name]["name"], ]
        if history:
            if tbl_dict[tst_name].get("history", None) is not None:
                for hist_data in tbl_dict[tst_name]["history"].values():
                    if hist_data:
                        item.append(round(mean(hist_data) / 1000000, 2))
                        item.append(round(stdev(hist_data) / 1000000, 2))
                    else:
                        item.extend([None, None])
            else:
                item.extend([None, None])
        data_t = tbl_dict[tst_name]["ref-data"]
        if data_t:
            item.append(round(mean(data_t) / 1000000, 2))
            item.append(round(stdev(data_t) / 1000000, 2))
        else:
            item.extend([None, None])
        data_t = tbl_dict[tst_name]["cmp-data"]
        if data_t:
            item.append(round(mean(data_t) / 1000000, 2))
            item.append(round(stdev(data_t) / 1000000, 2))
        else:
            item.extend([None, None])
        if item[-4] is not None and item[-2] is not None and item[-4] != 0:
            item.append(int(relative_change(float(item[-4]), float(item[-2]))))
        if len(item) == len(header):
            tbl_lst.append(item)

    # Sort the table according to the relative change
    tbl_lst.sort(key=lambda rel: rel[-1], reverse=True)

    # Generate csv tables:
    csv_file = "{0}.csv".format(table["output-file"])
    with open(csv_file, "w") as file_handler:
        file_handler.write(header_str)
        for test in tbl_lst:
            file_handler.write(",".join([str(item) for item in test]) + "\n")

    convert_csv_to_pretty_txt(csv_file, "{0}.txt".format(table["output-file"]))


def table_nics_comparison(table, input_data):
    """Generate the table(s) with algorithm: table_nics_comparison
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the table {0} ...".
                 format(table.get("title", "")))

    # Transform the data
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(table.get("type", ""), table.get("title", "")))
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the tables
    try:
        header = ["Test case", ]

        if table["include-tests"] == "MRR":
            hdr_param = "Receive Rate"
        else:
            hdr_param = "Throughput"

        header.extend(
            ["{0} {1} [Mpps]".format(table["reference"]["title"], hdr_param),
             "{0} Stdev [Mpps]".format(table["reference"]["title"]),
             "{0} {1} [Mpps]".format(table["compare"]["title"], hdr_param),
             "{0} Stdev [Mpps]".format(table["compare"]["title"]),
             "Delta [%]"])
        header_str = ",".join(header) + "\n"
    except (AttributeError, KeyError) as err:
        logging.error("The model is invalid, missing parameter: {0}".
                      format(err))
        return

    # Prepare data to the table:
    tbl_dict = dict()
    for job, builds in table["data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].iteritems():
                tst_name_mod = tst_name.replace("-ndrpdrdisc", "").\
                    replace("-ndrpdr", "").replace("-pdrdisc", "").\
                    replace("-ndrdisc", "").replace("-pdr", "").\
                    replace("-ndr", "").\
                    replace("1t1c", "1c").replace("2t1c", "1c").\
                    replace("2t2c", "2c").replace("4t2c", "2c").\
                    replace("4t4c", "4c").replace("8t4c", "4c")
                tst_name_mod = re.sub(REGEX_NIC, "", tst_name_mod)
                if tbl_dict.get(tst_name_mod, None) is None:
                    name = "-".join(tst_data["name"].split("-")[:-1])
                    tbl_dict[tst_name_mod] = {"name": name,
                                              "ref-data": list(),
                                              "cmp-data": list()}
                try:
                    if table["include-tests"] == "MRR":
                        result = tst_data["result"]["receive-rate"].avg
                    elif table["include-tests"] == "PDR":
                        result = tst_data["throughput"]["PDR"]["LOWER"]
                    elif table["include-tests"] == "NDR":
                        result = tst_data["throughput"]["NDR"]["LOWER"]
                    else:
                        result = None

                    if result:
                        if table["reference"]["nic"] in tst_data["tags"]:
                            tbl_dict[tst_name_mod]["ref-data"].append(result)
                        elif table["compare"]["nic"] in tst_data["tags"]:
                            tbl_dict[tst_name_mod]["cmp-data"].append(result)
                except (TypeError, KeyError) as err:
                    logging.debug("No data for {0}".format(tst_name))
                    logging.debug(repr(err))
                    # No data in output.xml for this test

    tbl_lst = list()
    for tst_name in tbl_dict.keys():
        item = [tbl_dict[tst_name]["name"], ]
        data_t = tbl_dict[tst_name]["ref-data"]
        if data_t:
            item.append(round(mean(data_t) / 1000000, 2))
            item.append(round(stdev(data_t) / 1000000, 2))
        else:
            item.extend([None, None])
        data_t = tbl_dict[tst_name]["cmp-data"]
        if data_t:
            item.append(round(mean(data_t) / 1000000, 2))
            item.append(round(stdev(data_t) / 1000000, 2))
        else:
            item.extend([None, None])
        if item[-4] is not None and item[-2] is not None and item[-4] != 0:
            item.append(int(relative_change(float(item[-4]), float(item[-2]))))
        if len(item) == len(header):
            tbl_lst.append(item)

    # Sort the table according to the relative change
    tbl_lst.sort(key=lambda rel: rel[-1], reverse=True)

    # Generate csv tables:
    csv_file = "{0}.csv".format(table["output-file"])
    with open(csv_file, "w") as file_handler:
        file_handler.write(header_str)
        for test in tbl_lst:
            file_handler.write(",".join([str(item) for item in test]) + "\n")

    convert_csv_to_pretty_txt(csv_file, "{0}.txt".format(table["output-file"]))


def table_soak_vs_ndr(table, input_data):
    """Generate the table(s) with algorithm: table_soak_vs_ndr
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the table {0} ...".
                 format(table.get("title", "")))

    # Transform the data
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(table.get("type", ""), table.get("title", "")))
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the table
    try:
        header = [
            "Test case",
            "{0} Throughput [Mpps]".format(table["reference"]["title"]),
            "{0} Stdev [Mpps]".format(table["reference"]["title"]),
            "{0} Throughput [Mpps]".format(table["compare"]["title"]),
            "{0} Stdev [Mpps]".format(table["compare"]["title"]),
            "Delta [%]", "Stdev of delta [%]"]
        header_str = ",".join(header) + "\n"
    except (AttributeError, KeyError) as err:
        logging.error("The model is invalid, missing parameter: {0}".
                      format(err))
        return

    # Create a list of available SOAK test results:
    tbl_dict = dict()
    for job, builds in table["compare"]["data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].iteritems():
                if tst_data["type"] == "SOAK":
                    tst_name_mod = tst_name.replace("-soak", "")
                    if tbl_dict.get(tst_name_mod, None) is None:
                        groups = re.search(REGEX_NIC, tst_data["parent"])
                        nic = groups.group(0) if groups else ""
                        name = "{0}-{1}".format(nic, "-".join(tst_data["name"].
                                                              split("-")[:-1]))
                        tbl_dict[tst_name_mod] = {
                            "name": name,
                            "ref-data": list(),
                            "cmp-data": list()
                        }
                    try:
                        tbl_dict[tst_name_mod]["cmp-data"].append(
                            tst_data["throughput"]["LOWER"])
                    except (KeyError, TypeError):
                        pass
    tests_lst = tbl_dict.keys()

    # Add corresponding NDR test results:
    for job, builds in table["reference"]["data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].iteritems():
                tst_name_mod = tst_name.replace("-ndrpdr", "").\
                    replace("-mrr", "")
                if tst_name_mod in tests_lst:
                    try:
                        if tst_data["type"] in ("NDRPDR", "MRR", "BMRR"):
                            if table["include-tests"] == "MRR":
                                result = tst_data["result"]["receive-rate"].avg
                            elif table["include-tests"] == "PDR":
                                result = tst_data["throughput"]["PDR"]["LOWER"]
                            elif table["include-tests"] == "NDR":
                                result = tst_data["throughput"]["NDR"]["LOWER"]
                            else:
                                result = None
                            if result is not None:
                                tbl_dict[tst_name_mod]["ref-data"].append(
                                    result)
                    except (KeyError, TypeError):
                        continue

    tbl_lst = list()
    for tst_name in tbl_dict.keys():
        item = [tbl_dict[tst_name]["name"], ]
        data_r = tbl_dict[tst_name]["ref-data"]
        if data_r:
            data_r_mean = mean(data_r)
            item.append(round(data_r_mean / 1000000, 2))
            data_r_stdev = stdev(data_r)
            item.append(round(data_r_stdev / 1000000, 2))
        else:
            data_r_mean = None
            data_r_stdev = None
            item.extend([None, None])
        data_c = tbl_dict[tst_name]["cmp-data"]
        if data_c:
            data_c_mean = mean(data_c)
            item.append(round(data_c_mean / 1000000, 2))
            data_c_stdev = stdev(data_c)
            item.append(round(data_c_stdev / 1000000, 2))
        else:
            data_c_mean = None
            data_c_stdev = None
            item.extend([None, None])
        if data_r_mean and data_c_mean:
            delta, d_stdev = relative_change_stdev(
                data_r_mean, data_c_mean, data_r_stdev, data_c_stdev)
            item.append(round(delta, 2))
            item.append(round(d_stdev, 2))
            tbl_lst.append(item)

    # Sort the table according to the relative change
    tbl_lst.sort(key=lambda rel: rel[-1], reverse=True)

    # Generate csv tables:
    csv_file = "{0}.csv".format(table["output-file"])
    with open(csv_file, "w") as file_handler:
        file_handler.write(header_str)
        for test in tbl_lst:
            file_handler.write(",".join([str(item) for item in test]) + "\n")

    convert_csv_to_pretty_txt(csv_file, "{0}.txt".format(table["output-file"]))


def table_performance_trending_dashboard(table, input_data):
    """Generate the table(s) with algorithm:
    table_performance_trending_dashboard
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the table {0} ...".
                 format(table.get("title", "")))

    # Transform the data
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(table.get("type", ""), table.get("title", "")))
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the tables
    header = ["Test Case",
              "Trend [Mpps]",
              "Short-Term Change [%]",
              "Long-Term Change [%]",
              "Regressions [#]",
              "Progressions [#]"
              ]
    header_str = ",".join(header) + "\n"

    # Prepare data to the table:
    tbl_dict = dict()
    for job, builds in table["data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].iteritems():
                if tst_name.lower() in table.get("ignore-list", list()):
                    continue
                if tbl_dict.get(tst_name, None) is None:
                    groups = re.search(REGEX_NIC, tst_data["parent"])
                    if not groups:
                        continue
                    nic = groups.group(0)
                    tbl_dict[tst_name] = {
                        "name": "{0}-{1}".format(nic, tst_data["name"]),
                        "data": OrderedDict()}
                try:
                    tbl_dict[tst_name]["data"][str(build)] = \
                        tst_data["result"]["receive-rate"]
                except (TypeError, KeyError):
                    pass  # No data in output.xml for this test

    tbl_lst = list()
    for tst_name in tbl_dict.keys():
        data_t = tbl_dict[tst_name]["data"]
        if len(data_t) < 2:
            continue

        classification_lst, avgs = classify_anomalies(data_t)

        win_size = min(len(data_t), table["window"])
        long_win_size = min(len(data_t), table["long-trend-window"])

        try:
            max_long_avg = max(
                [x for x in avgs[-long_win_size:-win_size]
                 if not isnan(x)])
        except ValueError:
            max_long_avg = nan
        last_avg = avgs[-1]
        avg_week_ago = avgs[max(-win_size, -len(avgs))]

        if isnan(last_avg) or isnan(avg_week_ago) or avg_week_ago == 0.0:
            rel_change_last = nan
        else:
            rel_change_last = round(
                ((last_avg - avg_week_ago) / avg_week_ago) * 100, 2)

        if isnan(max_long_avg) or isnan(last_avg) or max_long_avg == 0.0:
            rel_change_long = nan
        else:
            rel_change_long = round(
                ((last_avg - max_long_avg) / max_long_avg) * 100, 2)

        if classification_lst:
            if isnan(rel_change_last) and isnan(rel_change_long):
                continue
            if (isnan(last_avg) or
                isnan(rel_change_last) or
                isnan(rel_change_long)):
                continue
            tbl_lst.append(
                [tbl_dict[tst_name]["name"],
                 round(last_avg / 1000000, 2),
                 rel_change_last,
                 rel_change_long,
                 classification_lst[-win_size:].count("regression"),
                 classification_lst[-win_size:].count("progression")])

    tbl_lst.sort(key=lambda rel: rel[0])

    tbl_sorted = list()
    for nrr in range(table["window"], -1, -1):
        tbl_reg = [item for item in tbl_lst if item[4] == nrr]
        for nrp in range(table["window"], -1, -1):
            tbl_out = [item for item in tbl_reg if item[5] == nrp]
            tbl_out.sort(key=lambda rel: rel[2])
            tbl_sorted.extend(tbl_out)

    file_name = "{0}{1}".format(table["output-file"], table["output-file-ext"])

    logging.info("    Writing file: '{0}'".format(file_name))
    with open(file_name, "w") as file_handler:
        file_handler.write(header_str)
        for test in tbl_sorted:
            file_handler.write(",".join([str(item) for item in test]) + '\n')

    txt_file_name = "{0}.txt".format(table["output-file"])
    logging.info("    Writing file: '{0}'".format(txt_file_name))
    convert_csv_to_pretty_txt(file_name, txt_file_name)


def _generate_url(base, testbed, test_name):
    """Generate URL to a trending plot from the name of the test case.

    :param base: The base part of URL common to all test cases.
    :param testbed: The testbed used for testing.
    :param test_name: The name of the test case.
    :type base: str
    :type testbed: str
    :type test_name: str
    :returns: The URL to the plot with the trending data for the given test
        case.
    :rtype str
    """

    url = base
    file_name = ""
    anchor = ".html#"
    feature = ""

    if "lbdpdk" in test_name or "lbvpp" in test_name:
        file_name = "link_bonding"

    elif "114b" in test_name and "vhost" in test_name:
        file_name = "vts"

    elif "testpmd" in test_name or "l3fwd" in test_name:
        file_name = "dpdk"

    elif "memif" in test_name:
        file_name = "container_memif"
        feature = "-base"

    elif "srv6" in test_name:
        file_name = "srv6"

    elif "vhost" in test_name:
        if "l2xcbase" in test_name or "l2bdbasemaclrn" in test_name:
            file_name = "vm_vhost_l2"
            if "114b" in test_name:
                feature = ""
            elif "l2xcbase" in test_name and "x520" in test_name:
                feature = "-base-l2xc"
            elif "l2bdbasemaclrn" in test_name and "x520" in test_name:
                feature = "-base-l2bd"
            else:
                feature = "-base"
        elif "ip4base" in test_name:
            file_name = "vm_vhost_ip4"
            feature = "-base"

    elif "ipsecbasetnlsw" in test_name:
        file_name = "ipsecsw"
        feature = "-base-scale"

    elif "ipsec" in test_name:
        file_name = "ipsec"
        feature = "-base-scale"
        if "hw-" in test_name:
            file_name = "ipsechw"
        elif "sw-" in test_name:
            file_name = "ipsecsw"
        if "-int-" in test_name:
            feature = "-base-scale-int"
        elif "tnl" in test_name:
            feature = "-base-scale-tnl"

    elif "ethip4lispip" in test_name or "ethip4vxlan" in test_name:
        file_name = "ip4_tunnels"
        feature = "-base"

    elif "ip4base" in test_name or "ip4scale" in test_name:
        file_name = "ip4"
        if "xl710" in test_name:
            feature = "-base-scale-features"
        elif "iacl" in test_name:
            feature = "-features-iacl"
        elif "oacl" in test_name:
            feature = "-features-oacl"
        elif "snat" in test_name or "cop" in test_name:
            feature = "-features"
        else:
            feature = "-base-scale"

    elif "ip6base" in test_name or "ip6scale" in test_name:
        file_name = "ip6"
        feature = "-base-scale"

    elif "l2xcbase" in test_name or "l2xcscale" in test_name \
            or "l2bdbasemaclrn" in test_name or "l2bdscale" in test_name \
            or "l2dbbasemaclrn" in test_name or "l2dbscale" in test_name:
        file_name = "l2"
        if "macip" in test_name:
            feature = "-features-macip"
        elif "iacl" in test_name:
            feature = "-features-iacl"
        elif "oacl" in test_name:
            feature = "-features-oacl"
        else:
            feature = "-base-scale"

    if "x520" in test_name:
        nic = "x520-"
    elif "x710" in test_name:
        nic = "x710-"
    elif "xl710" in test_name:
        nic = "xl710-"
    elif "xxv710" in test_name:
        nic = "xxv710-"
    elif "vic1227" in test_name:
        nic = "vic1227-"
    elif "vic1385" in test_name:
        nic = "vic1385-"
    elif "x553" in test_name:
        nic = "x553-"
    else:
        nic = ""
    anchor += nic

    if "64b" in test_name:
        framesize = "64b"
    elif "78b" in test_name:
        framesize = "78b"
    elif "imix" in test_name:
        framesize = "imix"
    elif "9000b" in test_name:
        framesize = "9000b"
    elif "1518b" in test_name:
        framesize = "1518b"
    elif "114b" in test_name:
        framesize = "114b"
    else:
        framesize = ""
    anchor += framesize + '-'

    if "1t1c" in test_name:
        anchor += "1t1c"
    elif "2t2c" in test_name:
        anchor += "2t2c"
    elif "4t4c" in test_name:
        anchor += "4t4c"
    elif "2t1c" in test_name:
        anchor += "2t1c"
    elif "4t2c" in test_name:
        anchor += "4t2c"
    elif "8t4c" in test_name:
        anchor += "8t4c"

    return url + file_name + '-' + testbed + '-' + nic + framesize + \
        feature.replace("-int", "").replace("-tnl", "") + anchor + feature


def table_performance_trending_dashboard_html(table, input_data):
    """Generate the table(s) with algorithm:
    table_performance_trending_dashboard_html specified in the specification
    file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: dict
    :type input_data: InputData
    """

    testbed = table.get("testbed", None)
    if testbed is None:
        logging.error("The testbed is not defined for the table '{0}'.".
                      format(table.get("title", "")))
        return

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
    colors = {"regression": ("#ffcccc", "#ff9999"),
              "progression": ("#c6ecc6", "#9fdf9f"),
              "normal": ("#e9f1fb", "#d4e4f7")}
    for r_idx, row in enumerate(csv_lst[1:]):
        if int(row[4]):
            color = "regression"
        elif int(row[5]):
            color = "progression"
        else:
            color = "normal"
        background = colors[color][r_idx % 2]
        tr = ET.SubElement(dashboard, "tr", attrib=dict(bgcolor=background))

        # Columns:
        for c_idx, item in enumerate(row):
            alignment = "left" if c_idx == 0 else "center"
            td = ET.SubElement(tr, "td", attrib=dict(align=alignment))
            # Name:
            if c_idx == 0:
                url = _generate_url("../trending/", testbed, item)
                ref = ET.SubElement(td, "a", attrib=dict(href=url))
                ref.text = item
            else:
                td.text = item
    try:
        with open(table["output-file"], 'w') as html_file:
            logging.info("    Writing file: '{0}'".format(table["output-file"]))
            html_file.write(".. raw:: html\n\n\t")
            html_file.write(ET.tostring(dashboard))
            html_file.write("\n\t<p><br><br></p>\n")
    except KeyError:
        logging.warning("The output file is not defined.")
        return


def table_last_failed_tests(table, input_data):
    """Generate the table(s) with algorithm: table_last_failed_tests
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the table {0} ...".
                 format(table.get("title", "")))

    # Transform the data
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(table.get("type", ""), table.get("title", "")))
    data = input_data.filter_data(table, continue_on_error=True)

    if data is None or data.empty:
        logging.warn("    No data for the {0} '{1}'.".
                     format(table.get("type", ""), table.get("title", "")))
        return

    tbl_list = list()
    for job, builds in table["data"].items():
        for build in builds:
            build = str(build)
            try:
                version = input_data.metadata(job, build).get("version", "")
            except KeyError:
                logging.error("Data for {job}: {build} is not present.".
                              format(job=job, build=build))
                return
            tbl_list.append(build)
            tbl_list.append(version)
            for tst_name, tst_data in data[job][build].iteritems():
                if tst_data["status"] != "FAIL":
                    continue
                groups = re.search(REGEX_NIC, tst_data["parent"])
                if not groups:
                    continue
                nic = groups.group(0)
                tbl_list.append("{0}-{1}".format(nic, tst_data["name"]))

    file_name = "{0}{1}".format(table["output-file"], table["output-file-ext"])
    logging.info("    Writing file: '{0}'".format(file_name))
    with open(file_name, "w") as file_handler:
        for test in tbl_list:
            file_handler.write(test + '\n')


def table_failed_tests(table, input_data):
    """Generate the table(s) with algorithm: table_failed_tests
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the table {0} ...".
                 format(table.get("title", "")))

    # Transform the data
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(table.get("type", ""), table.get("title", "")))
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the tables
    header = ["Test Case",
              "Failures [#]",
              "Last Failure [Time]",
              "Last Failure [VPP-Build-Id]",
              "Last Failure [CSIT-Job-Build-Id]"]

    # Generate the data for the table according to the model in the table
    # specification

    now = dt.utcnow()
    timeperiod = timedelta(int(table.get("window", 7)))

    tbl_dict = dict()
    for job, builds in table["data"].items():
        for build in builds:
            build = str(build)
            for tst_name, tst_data in data[job][build].iteritems():
                if tst_name.lower() in table.get("ignore-list", list()):
                    continue
                if tbl_dict.get(tst_name, None) is None:
                    groups = re.search(REGEX_NIC, tst_data["parent"])
                    if not groups:
                        continue
                    nic = groups.group(0)
                    tbl_dict[tst_name] = {
                        "name": "{0}-{1}".format(nic, tst_data["name"]),
                        "data": OrderedDict()}
                try:
                    generated = input_data.metadata(job, build).\
                        get("generated", "")
                    if not generated:
                        continue
                    then = dt.strptime(generated, "%Y%m%d %H:%M")
                    if (now - then) <= timeperiod:
                        tbl_dict[tst_name]["data"][build] = (
                            tst_data["status"],
                            generated,
                            input_data.metadata(job, build).get("version", ""),
                            build)
                except (TypeError, KeyError) as err:
                    logging.warning("tst_name: {} - err: {}".
                                    format(tst_name, repr(err)))

    max_fails = 0
    tbl_lst = list()
    for tst_data in tbl_dict.values():
        fails_nr = 0
        for val in tst_data["data"].values():
            if val[0] == "FAIL":
                fails_nr += 1
                fails_last_date = val[1]
                fails_last_vpp = val[2]
                fails_last_csit = val[3]
        if fails_nr:
            max_fails = fails_nr if fails_nr > max_fails else max_fails
            tbl_lst.append([tst_data["name"],
                            fails_nr,
                            fails_last_date,
                            fails_last_vpp,
                            "mrr-daily-build-{0}".format(fails_last_csit)])

    tbl_lst.sort(key=lambda rel: rel[2], reverse=True)
    tbl_sorted = list()
    for nrf in range(max_fails, -1, -1):
        tbl_fails = [item for item in tbl_lst if item[1] == nrf]
        tbl_sorted.extend(tbl_fails)
    file_name = "{0}{1}".format(table["output-file"], table["output-file-ext"])

    logging.info("    Writing file: '{0}'".format(file_name))
    with open(file_name, "w") as file_handler:
        file_handler.write(",".join(header) + "\n")
        for test in tbl_sorted:
            file_handler.write(",".join([str(item) for item in test]) + '\n')

    txt_file_name = "{0}.txt".format(table["output-file"])
    logging.info("    Writing file: '{0}'".format(txt_file_name))
    convert_csv_to_pretty_txt(file_name, txt_file_name)


def table_failed_tests_html(table, input_data):
    """Generate the table(s) with algorithm: table_failed_tests_html
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    testbed = table.get("testbed", None)
    if testbed is None:
        logging.error("The testbed is not defined for the table '{0}'.".
                      format(table.get("title", "")))
        return

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
    failed_tests = ET.Element("table", attrib=dict(width="100%", border='0'))

    # Table header:
    tr = ET.SubElement(failed_tests, "tr", attrib=dict(bgcolor="#7eade7"))
    for idx, item in enumerate(csv_lst[0]):
        alignment = "left" if idx == 0 else "center"
        th = ET.SubElement(tr, "th", attrib=dict(align=alignment))
        th.text = item

    # Rows:
    colors = ("#e9f1fb", "#d4e4f7")
    for r_idx, row in enumerate(csv_lst[1:]):
        background = colors[r_idx % 2]
        tr = ET.SubElement(failed_tests, "tr", attrib=dict(bgcolor=background))

        # Columns:
        for c_idx, item in enumerate(row):
            alignment = "left" if c_idx == 0 else "center"
            td = ET.SubElement(tr, "td", attrib=dict(align=alignment))
            # Name:
            if c_idx == 0:
                url = _generate_url("../trending/", testbed, item)
                ref = ET.SubElement(td, "a", attrib=dict(href=url))
                ref.text = item
            else:
                td.text = item
    try:
        with open(table["output-file"], 'w') as html_file:
            logging.info("    Writing file: '{0}'".format(table["output-file"]))
            html_file.write(".. raw:: html\n\n\t")
            html_file.write(ET.tostring(failed_tests))
            html_file.write("\n\t<p><br><br></p>\n")
    except KeyError:
        logging.warning("The output file is not defined.")
        return
