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

from collections import OrderedDict
from xml.etree import ElementTree as ET
from datetime import datetime as dt
from datetime import timedelta

import plotly.graph_objects as go
import plotly.offline as ploff
import pandas as pd

from numpy import nan, isnan

from pal_utils import mean, stdev, relative_change, classify_anomalies, \
    convert_csv_to_pretty_txt, relative_change_stdev


REGEX_NIC = re.compile(r'\d*ge\dp\d\D*\d*')


def generate_tables(spec, data):
    """Generate all tables specified in the specification file.

    :param spec: Specification read from the specification file.
    :param data: Data to process.
    :type spec: Specification
    :type data: InputData
    """

    generator = {
        u"table_details": table_details,
        u"table_merged_details": table_merged_details,
        u"table_perf_comparison": table_perf_comparison,
        u"table_perf_comparison_nic": table_perf_comparison_nic,
        u"table_nics_comparison": table_nics_comparison,
        u"table_soak_vs_ndr": table_soak_vs_ndr,
        u"table_perf_trending_dash": table_perf_trending_dash,
        u"table_perf_trending_dash_html": table_perf_trending_dash_html,
        u"table_last_failed_tests": table_last_failed_tests,
        u"table_failed_tests": table_failed_tests,
        u"table_failed_tests_html": table_failed_tests_html
    }

    logging.info(u"Generating the tables ...")
    for table in spec.tables:
        try:
            generator[table[u"algorithm"]](table, data)
        except NameError as err:
            logging.error(
                f"Probably algorithm {table[u'algorithm']} is not defined: "
                f"{repr(err)}"
            )
    logging.info(u"Done.")


def table_details(table, input_data):
    """Generate the table(s) with algorithm: table_detailed_test_results
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info(f"  Generating the table {table.get(u'title', u'')} ...")

    # Transform the data
    logging.info(
        f"    Creating the data set for the {table.get(u'type', u'')} "
        f"{table.get(u'title', u'')}."
    )
    data = input_data.filter_data(table)

    # Prepare the header of the tables
    header = list()
    for column in table[u"columns"]:
        header.append(
            u'"{0}"'.format(str(column[u"title"]).replace(u'"', u'""'))
        )

    # Generate the data for the table according to the model in the table
    # specification
    job = list(table[u"data"].keys())[0]
    build = str(table[u"data"][job][0])
    try:
        suites = input_data.suites(job, build)
    except KeyError:
        logging.error(
            u"    No data available. The table will not be generated."
        )
        return

    for suite in suites.values:
        # Generate data
        suite_name = suite[u"name"]
        table_lst = list()
        for test in data[job][build].keys():
            if data[job][build][test][u"parent"] not in suite_name:
                continue
            row_lst = list()
            for column in table[u"columns"]:
                try:
                    col_data = str(data[job][build][test][column[
                        u"data"].split(" ")[1]]).replace(u'"', u'""')
                    if column[u"data"].split(u" ")[1] in \
                        (u"conf-history", u"show-run"):
                        col_data = col_data.replace(u" |br| ", u"", )
                        col_data = f" |prein| {col_data[:-5]} |preout| "
                    row_lst.append(f'"{col_data}"')
                except KeyError:
                    row_lst.append(u"No data")
            table_lst.append(row_lst)

        # Write the data to file
        if table_lst:
            file_name = (
                f"{table[u'output-file']}_{suite_name}"
                f"{table[u'output-file-ext']}"
            )
            logging.info(f"      Writing file: {file_name}")
            with open(file_name, u"w") as file_handler:
                file_handler.write(u",".join(header) + u"\n")
                for item in table_lst:
                    file_handler.write(u",".join(item) + u"\n")

    logging.info(u"  Done.")


def table_merged_details(table, input_data):
    """Generate the table(s) with algorithm: table_merged_details
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info(f"  Generating the table {table.get(u'title', u'')} ...")
    # Transform the data
    logging.info(
        f"    Creating the data set for the {table.get(u'type', u'')} "
        f"{table.get(u'title', u'')}."
    )
    data = input_data.filter_data(table, continue_on_error=True)
    data = input_data.merge_data(data)
    data.sort_index(inplace=True)

    logging.info(
        f"    Creating the data set for the {table.get(u'type', u'')} "
        f"{table.get(u'title', u'')}."
    )
    suites = input_data.filter_data(
        table, continue_on_error=True, data_set=u"suites")
    suites = input_data.merge_data(suites)

    # Prepare the header of the tables
    header = list()
    for column in table[u"columns"]:
        header.append(
            u'"{0}"'.format(str(column[u"title"]).replace(u'"', u'""'))
        )

    for suite in suites.values:
        # Generate data
        suite_name = suite[u"name"]
        table_lst = list()
        for test in data.keys():
            if data[test][u"parent"] not in suite_name:
                continue
            row_lst = list()
            for column in table[u"columns"]:
                try:
                    col_data = str(data[test][column[
                        u"data"].split(u" ")[1]]).replace(u'"', u'""')
                    col_data = col_data.replace(
                        u"No Data", u"Not Captured     "
                    )
                    if column[u"data"].split(u" ")[1] in \
                        (u"conf-history", u"show-run"):
                        col_data = col_data.replace(u" |br| ", u"", 1)
                        col_data = f" |prein| {col_data[:-5]} |preout| "
                    row_lst.append(f'"{col_data}"')
                except KeyError:
                    row_lst.append(u'"Not captured"')
            table_lst.append(row_lst)

        # Write the data to file
        if table_lst:
            file_name = (
                f"{table[u'output-file']}_{suite_name}"
                f"{table[u'output-file-ext']}"
            )
            logging.info(f"      Writing file: {file_name}")
            with open(file_name, u"w") as file_handler:
                file_handler.write(u",".join(header) + u"\n")
                for item in table_lst:
                    file_handler.write(u",".join(item) + u"\n")

    logging.info(u"  Done.")


def _tpc_modify_test_name(test_name):
    """Modify a test name by replacing its parts.

    :param test_name: Test name to be modified.
    :type test_name: str
    :returns: Modified test name.
    :rtype: str
    """
    test_name_mod = test_name.\
        replace(u"-ndrpdrdisc", u""). \
        replace(u"-ndrpdr", u"").\
        replace(u"-pdrdisc", u""). \
        replace(u"-ndrdisc", u"").\
        replace(u"-pdr", u""). \
        replace(u"-ndr", u""). \
        replace(u"1t1c", u"1c").\
        replace(u"2t1c", u"1c"). \
        replace(u"2t2c", u"2c").\
        replace(u"4t2c", u"2c"). \
        replace(u"4t4c", u"4c").\
        replace(u"8t4c", u"4c")

    return re.sub(REGEX_NIC, u"", test_name_mod)


def _tpc_modify_displayed_test_name(test_name):
    """Modify a test name which is displayed in a table by replacing its parts.

    :param test_name: Test name to be modified.
    :type test_name: str
    :returns: Modified test name.
    :rtype: str
    """
    return test_name.\
        replace(u"1t1c", u"1c").\
        replace(u"2t1c", u"1c"). \
        replace(u"2t2c", u"2c").\
        replace(u"4t2c", u"2c"). \
        replace(u"4t4c", u"4c").\
        replace(u"8t4c", u"4c")


def _tpc_insert_data(target, src, include_tests):
    """Insert src data to the target structure.

    :param target: Target structure where the data is placed.
    :param src: Source data to be placed into the target stucture.
    :param include_tests: Which results will be included (MRR, NDR, PDR).
    :type target: list
    :type src: dict
    :type include_tests: str
    """
    try:
        if include_tests == u"MRR":
            target.append(src[u"result"][u"receive-rate"])
        elif include_tests == u"PDR":
            target.append(src[u"throughput"][u"PDR"][u"LOWER"])
        elif include_tests == u"NDR":
            target.append(src[u"throughput"][u"NDR"][u"LOWER"])
    except (KeyError, TypeError):
        pass


def _tpc_sort_table(table):
    """Sort the table this way:

    1. Put "New in CSIT-XXXX" at the first place.
    2. Put "See footnote" at the second place.
    3. Sort the rest by "Delta".

    :param table: Table to sort.
    :type table: list
    :returns: Sorted table.
    :rtype: list
    """


    tbl_new = list()
    tbl_see = list()
    tbl_delta = list()
    for item in table:
        if isinstance(item[-1], str):
            if u"New in CSIT" in item[-1]:
                tbl_new.append(item)
            elif u"See footnote" in item[-1]:
                tbl_see.append(item)
        else:
            tbl_delta.append(item)

    # Sort the tables:
    tbl_new.sort(key=lambda rel: rel[0], reverse=False)
    tbl_see.sort(key=lambda rel: rel[0], reverse=False)
    tbl_see.sort(key=lambda rel: rel[-1], reverse=False)
    tbl_delta.sort(key=lambda rel: rel[-1], reverse=True)

    # Put the tables together:
    table = list()
    table.extend(tbl_new)
    table.extend(tbl_see)
    table.extend(tbl_delta)

    return table


def _tpc_generate_html_table(header, data, output_file_name):
    """Generate html table from input data with simple sorting possibility.

    :param header: Table header.
    :param data: Input data to be included in the table. It is a list of lists.
        Inner lists are rows in the table. All inner lists must be of the same
        length. The length of these lists must be the same as the length of the
        header.
    :param output_file_name: The name (relative or full path) where the
        generated html table is written.
    :type header: list
    :type data: list of lists
    :type output_file_name: str
    """

    df_data = pd.DataFrame(data, columns=header)

    df_sorted = [df_data.sort_values(
        by=[key, header[0]], ascending=[True, True]
        if key != header[0] else [False, True]) for key in header]
    df_sorted_rev = [df_data.sort_values(
        by=[key, header[0]], ascending=[False, True]
        if key != header[0] else [True, True]) for key in header]
    df_sorted.extend(df_sorted_rev)

    fill_color = [[u"#d4e4f7" if idx % 2 else u"#e9f1fb"
                   for idx in range(len(df_data))]]
    table_header = dict(
        values=[f"<b>{item}</b>" for item in header],
        fill_color=u"#7eade7",
        align=[u"left", u"center"]
    )

    fig = go.Figure()

    for table in df_sorted:
        columns = [table.get(col) for col in header]
        fig.add_trace(
            go.Table(
                columnwidth=[30, 10],
                header=table_header,
                cells=dict(
                    values=columns,
                    fill_color=fill_color,
                    align=[u"left", u"right"]
                )
            )
        )

    buttons = list()
    menu_items = [f"<b>{itm}</b> (ascending)" for itm in header]
    menu_items_rev = [f"<b>{itm}</b> (descending)" for itm in header]
    menu_items.extend(menu_items_rev)
    for idx, hdr in enumerate(menu_items):
        visible = [False, ] * len(menu_items)
        visible[idx] = True
        buttons.append(
            dict(
                label=hdr.replace(u" [Mpps]", u""),
                method=u"update",
                args=[{u"visible": visible}],
            )
        )

    fig.update_layout(
        updatemenus=[
            go.layout.Updatemenu(
                type=u"dropdown",
                direction=u"down",
                x=0.03,
                xanchor=u"left",
                y=1.045,
                yanchor=u"top",
                active=len(menu_items) - 1,
                buttons=list(buttons)
            )
        ],
        annotations=[
            go.layout.Annotation(
                text=u"<b>Sort by:</b>",
                x=0,
                xref=u"paper",
                y=1.035,
                yref=u"paper",
                align=u"left",
                showarrow=False
            )
        ]
    )

    ploff.plot(fig, show_link=False, auto_open=False, filename=output_file_name)


def table_perf_comparison(table, input_data):
    """Generate the table(s) with algorithm: table_perf_comparison
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info(f"  Generating the table {table.get(u'title', u'')} ...")

    # Transform the data
    logging.info(
        f"    Creating the data set for the {table.get(u'type', u'')} "
        f"{table.get(u'title', u'')}."
    )
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the tables
    try:
        header = [u"Test case", ]

        if table[u"include-tests"] == u"MRR":
            hdr_param = u"Rec Rate"
        else:
            hdr_param = u"Thput"

        history = table.get(u"history", list())
        for item in history:
            header.extend(
                [
                    f"{item[u'title']} {hdr_param} [Mpps]",
                    f"{item[u'title']} Stdev [Mpps]"
                ]
            )
        header.extend(
            [
                f"{table[u'reference'][u'title']} {hdr_param} [Mpps]",
                f"{table[u'reference'][u'title']} Stdev [Mpps]",
                f"{table[u'compare'][u'title']} {hdr_param} [Mpps]",
                f"{table[u'compare'][u'title']} Stdev [Mpps]",
                u"Delta [%]"
            ]
        )
        header_str = u",".join(header) + u"\n"
    except (AttributeError, KeyError) as err:
        logging.error(f"The model is invalid, missing parameter: {repr(err)}")
        return

    # Prepare data to the table:
    tbl_dict = dict()
    topo = ""
    for job, builds in table[u"reference"][u"data"].items():
        topo = u"2n-skx" if u"2n-skx" in job else u""
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].items():
                tst_name_mod = _tpc_modify_test_name(tst_name)
                if u"across topologies" in table[u"title"].lower():
                    tst_name_mod = tst_name_mod.replace(u"2n1l-", u"")
                if tbl_dict.get(tst_name_mod, None) is None:
                    groups = re.search(REGEX_NIC, tst_data[u"parent"])
                    nic = groups.group(0) if groups else u""
                    name = \
                        f"{nic}-{u'-'.join(tst_data[u'name'].split(u'-')[:-1])}"
                    if u"across testbeds" in table[u"title"].lower() or \
                            u"across topologies" in table[u"title"].lower():
                        name = _tpc_modify_displayed_test_name(name)
                    tbl_dict[tst_name_mod] = {
                        u"name": name,
                        u"ref-data": list(),
                        u"cmp-data": list()
                    }
                _tpc_insert_data(target=tbl_dict[tst_name_mod][u"ref-data"],
                                 src=tst_data,
                                 include_tests=table[u"include-tests"])

    for job, builds in table[u"compare"][u"data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].items():
                tst_name_mod = _tpc_modify_test_name(tst_name)
                if u"across topologies" in table[u"title"].lower():
                    tst_name_mod = tst_name_mod.replace(u"2n1l-", u"")
                if tbl_dict.get(tst_name_mod, None) is None:
                    groups = re.search(REGEX_NIC, tst_data[u"parent"])
                    nic = groups.group(0) if groups else u""
                    name = \
                        f"{nic}-{u'-'.join(tst_data[u'name'].split(u'-')[:-1])}"
                    if u"across testbeds" in table[u"title"].lower() or \
                            u"across topologies" in table[u"title"].lower():
                        name = _tpc_modify_displayed_test_name(name)
                    tbl_dict[tst_name_mod] = {
                        u"name": name,
                        u"ref-data": list(),
                        u"cmp-data": list()
                    }
                _tpc_insert_data(
                    target=tbl_dict[tst_name_mod][u"cmp-data"],
                    src=tst_data,
                    include_tests=table[u"include-tests"]
                )

    replacement = table[u"compare"].get(u"data-replacement", None)
    if replacement:
        create_new_list = True
        rpl_data = input_data.filter_data(
            table, data=replacement, continue_on_error=True)
        for job, builds in replacement.items():
            for build in builds:
                for tst_name, tst_data in rpl_data[job][str(build)].items():
                    tst_name_mod = _tpc_modify_test_name(tst_name)
                    if u"across topologies" in table[u"title"].lower():
                        tst_name_mod = tst_name_mod.replace(u"2n1l-", u"")
                    if tbl_dict.get(tst_name_mod, None) is None:
                        name = \
                            f"{u'-'.join(tst_data[u'name'].split(u'-')[:-1])}"
                        if u"across testbeds" in table[u"title"].lower() or \
                                u"across topologies" in table[u"title"].lower():
                            name = _tpc_modify_displayed_test_name(name)
                        tbl_dict[tst_name_mod] = {
                            u"name": name,
                            u"ref-data": list(),
                            u"cmp-data": list()
                        }
                    if create_new_list:
                        create_new_list = False
                        tbl_dict[tst_name_mod][u"cmp-data"] = list()

                    _tpc_insert_data(
                        target=tbl_dict[tst_name_mod][u"cmp-data"],
                        src=tst_data,
                        include_tests=table[u"include-tests"]
                    )

    for item in history:
        for job, builds in item[u"data"].items():
            for build in builds:
                for tst_name, tst_data in data[job][str(build)].items():
                    tst_name_mod = _tpc_modify_test_name(tst_name)
                    if u"across topologies" in table[u"title"].lower():
                        tst_name_mod = tst_name_mod.replace(u"2n1l-", u"")
                    if tbl_dict.get(tst_name_mod, None) is None:
                        continue
                    if tbl_dict[tst_name_mod].get(u"history", None) is None:
                        tbl_dict[tst_name_mod][u"history"] = OrderedDict()
                    if tbl_dict[tst_name_mod][u"history"].\
                            get(item[u"title"], None) is None:
                        tbl_dict[tst_name_mod][u"history"][item[
                            u"title"]] = list()
                    try:
                        if table[u"include-tests"] == u"MRR":
                            res = tst_data[u"result"][u"receive-rate"]
                        elif table[u"include-tests"] == u"PDR":
                            res = tst_data[u"throughput"][u"PDR"][u"LOWER"]
                        elif table[u"include-tests"] == u"NDR":
                            res = tst_data[u"throughput"][u"NDR"][u"LOWER"]
                        else:
                            continue
                        tbl_dict[tst_name_mod][u"history"][item[u"title"]].\
                            append(res)
                    except (TypeError, KeyError):
                        pass

    tbl_lst = list()
    footnote = False
    for tst_name in tbl_dict:
        item = [tbl_dict[tst_name][u"name"], ]
        if history:
            if tbl_dict[tst_name].get(u"history", None) is not None:
                for hist_data in tbl_dict[tst_name][u"history"].values():
                    if hist_data:
                        item.append(round(mean(hist_data) / 1000000, 2))
                        item.append(round(stdev(hist_data) / 1000000, 2))
                    else:
                        item.extend([u"Not tested", u"Not tested"])
            else:
                item.extend([u"Not tested", u"Not tested"])
        data_t = tbl_dict[tst_name][u"ref-data"]
        if data_t:
            item.append(round(mean(data_t) / 1000000, 2))
            item.append(round(stdev(data_t) / 1000000, 2))
        else:
            item.extend([u"Not tested", u"Not tested"])
        data_t = tbl_dict[tst_name][u"cmp-data"]
        if data_t:
            item.append(round(mean(data_t) / 1000000, 2))
            item.append(round(stdev(data_t) / 1000000, 2))
        else:
            item.extend([u"Not tested", u"Not tested"])
        if item[-2] == u"Not tested":
            pass
        elif item[-4] == u"Not tested":
            item.append(u"New in CSIT-1908")
        elif topo == u"2n-skx" and u"dot1q" in tbl_dict[tst_name][u"name"]:
            item.append(u"See footnote [1]")
            footnote = True
        elif item[-4] != 0:
            item.append(int(relative_change(float(item[-4]), float(item[-2]))))
        if (len(item) == len(header)) and (item[-3] != u"Not tested"):
            tbl_lst.append(item)

    tbl_lst = _tpc_sort_table(tbl_lst)

    # Generate csv tables:
    csv_file = f"{table[u'output-file']}.csv"
    with open(csv_file, u"w") as file_handler:
        file_handler.write(header_str)
        for test in tbl_lst:
            file_handler.write(u",".join([str(item) for item in test]) + u"\n")

    txt_file_name = f"{table[u'output-file']}.txt"
    convert_csv_to_pretty_txt(csv_file, txt_file_name)

    if footnote:
        with open(txt_file_name, u'a') as txt_file:
            txt_file.writelines([
                u"\nFootnotes:\n",
                u"[1] CSIT-1908 changed test methodology of dot1q tests in "
                u"2-node testbeds, dot1q encapsulation is now used on both "
                u"links of SUT.\n",
                u"    Previously dot1q was used only on a single link with the "
                u"other link carrying untagged Ethernet frames. This changes "
                u"results\n",
                u"    in slightly lower throughput in CSIT-1908 for these "
                u"tests. See release notes."
            ])

    # Generate html table:
    _tpc_generate_html_table(header, tbl_lst, f"{table[u'output-file']}.html")


def table_perf_comparison_nic(table, input_data):
    """Generate the table(s) with algorithm: table_perf_comparison
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info(f"  Generating the table {table.get(u'title', u'')} ...")

    # Transform the data
    logging.info(
        f"    Creating the data set for the {table.get(u'type', u'')} "
        f"{table.get(u'title', u'')}."
    )
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the tables
    try:
        header = [u"Test case", ]

        if table[u"include-tests"] == u"MRR":
            hdr_param = u"Rec Rate"
        else:
            hdr_param = u"Thput"

        history = table.get(u"history", list())
        for item in history:
            header.extend(
                [
                    f"{item[u'title']} {hdr_param} [Mpps]",
                    f"{item[u'title']} Stdev [Mpps]"
                ]
            )
        header.extend(
            [
                f"{table[u'reference'][u'title']} {hdr_param} [Mpps]",
                f"{table[u'reference'][u'title']} Stdev [Mpps]",
                f"{table[u'compare'][u'title']} {hdr_param} [Mpps]",
                f"{table[u'compare'][u'title']} Stdev [Mpps]",
                u"Delta [%]"
            ]
        )
        header_str = u",".join(header) + u"\n"
    except (AttributeError, KeyError) as err:
        logging.error(f"The model is invalid, missing parameter: {repr(err)}")
        return

    # Prepare data to the table:
    tbl_dict = dict()
    topo = u""
    for job, builds in table[u"reference"][u"data"].items():
        topo = u"2n-skx" if u"2n-skx" in job else u""
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].items():
                if table[u"reference"][u"nic"] not in tst_data[u"tags"]:
                    continue
                tst_name_mod = _tpc_modify_test_name(tst_name)
                if u"across topologies" in table[u"title"].lower():
                    tst_name_mod = tst_name_mod.replace(u"2n1l-", u"")
                if tbl_dict.get(tst_name_mod, None) is None:
                    name = f"{u'-'.join(tst_data[u'name'].split(u'-')[:-1])}"
                    if u"across testbeds" in table[u"title"].lower() or \
                            u"across topologies" in table[u"title"].lower():
                        name = _tpc_modify_displayed_test_name(name)
                    tbl_dict[tst_name_mod] = {
                        u"name": name,
                        u"ref-data": list(),
                        u"cmp-data": list()
                    }
                _tpc_insert_data(
                    target=tbl_dict[tst_name_mod][u"ref-data"],
                    src=tst_data,
                    include_tests=table[u"include-tests"]
                )

    for job, builds in table[u"compare"][u"data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].items():
                if table[u"compare"][u"nic"] not in tst_data[u"tags"]:
                    continue
                tst_name_mod = _tpc_modify_test_name(tst_name)
                if u"across topologies" in table[u"title"].lower():
                    tst_name_mod = tst_name_mod.replace(u"2n1l-", u"")
                if tbl_dict.get(tst_name_mod, None) is None:
                    name = f"{u'-'.join(tst_data[u'name'].split(u'-')[:-1])}"
                    if u"across testbeds" in table[u"title"].lower() or \
                            u"across topologies" in table[u"title"].lower():
                        name = _tpc_modify_displayed_test_name(name)
                    tbl_dict[tst_name_mod] = {
                        u"name": name,
                        u"ref-data": list(),
                        u"cmp-data": list()
                    }
                _tpc_insert_data(
                    target=tbl_dict[tst_name_mod][u"cmp-data"],
                    src=tst_data,
                    include_tests=table[u"include-tests"]
                )

    replacement = table[u"compare"].get(u"data-replacement", None)
    if replacement:
        create_new_list = True
        rpl_data = input_data.filter_data(
            table, data=replacement, continue_on_error=True)
        for job, builds in replacement.items():
            for build in builds:
                for tst_name, tst_data in rpl_data[job][str(build)].items():
                    if table[u"compare"][u"nic"] not in tst_data[u"tags"]:
                        continue
                    tst_name_mod = _tpc_modify_test_name(tst_name)
                    if u"across topologies" in table[u"title"].lower():
                        tst_name_mod = tst_name_mod.replace(u"2n1l-", u"")
                    if tbl_dict.get(tst_name_mod, None) is None:
                        name = \
                            f"{u'-'.join(tst_data[u'name'].split(u'-')[:-1])}"
                        if u"across testbeds" in table[u"title"].lower() or \
                                u"across topologies" in table[u"title"].lower():
                            name = _tpc_modify_displayed_test_name(name)
                        tbl_dict[tst_name_mod] = {
                            u"name": name,
                            u"ref-data": list(),
                            u"cmp-data": list()
                        }
                    if create_new_list:
                        create_new_list = False
                        tbl_dict[tst_name_mod][u"cmp-data"] = list()

                    _tpc_insert_data(
                        target=tbl_dict[tst_name_mod][u"cmp-data"],
                        src=tst_data,
                        include_tests=table[u"include-tests"]
                    )

    for item in history:
        for job, builds in item[u"data"].items():
            for build in builds:
                for tst_name, tst_data in data[job][str(build)].items():
                    if item[u"nic"] not in tst_data[u"tags"]:
                        continue
                    tst_name_mod = _tpc_modify_test_name(tst_name)
                    if u"across topologies" in table[u"title"].lower():
                        tst_name_mod = tst_name_mod.replace(u"2n1l-", u"")
                    if tbl_dict.get(tst_name_mod, None) is None:
                        continue
                    if tbl_dict[tst_name_mod].get(u"history", None) is None:
                        tbl_dict[tst_name_mod][u"history"] = OrderedDict()
                    if tbl_dict[tst_name_mod][u"history"].\
                            get(item[u"title"], None) is None:
                        tbl_dict[tst_name_mod][u"history"][item[
                            u"title"]] = list()
                    try:
                        if table[u"include-tests"] == u"MRR":
                            res = tst_data[u"result"][u"receive-rate"]
                        elif table[u"include-tests"] == u"PDR":
                            res = tst_data[u"throughput"][u"PDR"][u"LOWER"]
                        elif table[u"include-tests"] == u"NDR":
                            res = tst_data[u"throughput"][u"NDR"][u"LOWER"]
                        else:
                            continue
                        tbl_dict[tst_name_mod][u"history"][item[u"title"]].\
                            append(res)
                    except (TypeError, KeyError):
                        pass

    tbl_lst = list()
    footnote = False
    for tst_name in tbl_dict:
        item = [tbl_dict[tst_name][u"name"], ]
        if history:
            if tbl_dict[tst_name].get(u"history", None) is not None:
                for hist_data in tbl_dict[tst_name][u"history"].values():
                    if hist_data:
                        item.append(round(mean(hist_data) / 1000000, 2))
                        item.append(round(stdev(hist_data) / 1000000, 2))
                    else:
                        item.extend([u"Not tested", u"Not tested"])
            else:
                item.extend([u"Not tested", u"Not tested"])
        data_t = tbl_dict[tst_name][u"ref-data"]
        if data_t:
            item.append(round(mean(data_t) / 1000000, 2))
            item.append(round(stdev(data_t) / 1000000, 2))
        else:
            item.extend([u"Not tested", u"Not tested"])
        data_t = tbl_dict[tst_name][u"cmp-data"]
        if data_t:
            item.append(round(mean(data_t) / 1000000, 2))
            item.append(round(stdev(data_t) / 1000000, 2))
        else:
            item.extend([u"Not tested", u"Not tested"])
        if item[-2] == u"Not tested":
            pass
        elif item[-4] == u"Not tested":
            item.append(u"New in CSIT-1908")
        elif topo == u"2n-skx" and u"dot1q" in tbl_dict[tst_name][u"name"]:
            item.append(u"See footnote [1]")
            footnote = True
        elif item[-4] != 0:
            item.append(int(relative_change(float(item[-4]), float(item[-2]))))
        if (len(item) == len(header)) and (item[-3] != u"Not tested"):
            tbl_lst.append(item)

    tbl_lst = _tpc_sort_table(tbl_lst)

    # Generate csv tables:
    csv_file = f"{table[u'output-file']}.csv"
    with open(csv_file, u"w") as file_handler:
        file_handler.write(header_str)
        for test in tbl_lst:
            file_handler.write(u",".join([str(item) for item in test]) + u"\n")

    txt_file_name = f"{table[u'output-file']}.txt"
    convert_csv_to_pretty_txt(csv_file, txt_file_name)

    if footnote:
        with open(txt_file_name, u'a') as txt_file:
            txt_file.writelines([
                u"\nFootnotes:\n",
                u"[1] CSIT-1908 changed test methodology of dot1q tests in "
                u"2-node testbeds, dot1q encapsulation is now used on both "
                u"links of SUT.\n",
                u"    Previously dot1q was used only on a single link with the "
                u"other link carrying untagged Ethernet frames. This changes "
                u"results\n",
                u"    in slightly lower throughput in CSIT-1908 for these "
                u"tests. See release notes."
            ])

    # Generate html table:
    _tpc_generate_html_table(header, tbl_lst, f"{table[u'output-file']}.html")


def table_nics_comparison(table, input_data):
    """Generate the table(s) with algorithm: table_nics_comparison
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info(f"  Generating the table {table.get(u'title', u'')} ...")

    # Transform the data
    logging.info(
        f"    Creating the data set for the {table.get(u'type', u'')} "
        f"{table.get(u'title', u'')}."
    )
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the tables
    try:
        header = [u"Test case", ]

        if table[u"include-tests"] == u"MRR":
            hdr_param = u"Rec Rate"
        else:
            hdr_param = u"Thput"

        header.extend(
            [
                f"{table[u'reference'][u'title']} {hdr_param} [Mpps]",
                f"{table[u'reference'][u'title']} Stdev [Mpps]",
                f"{table[u'compare'][u'title']} {hdr_param} [Mpps]",
                f"{table[u'compare'][u'title']} Stdev [Mpps]",
                u"Delta [%]"
            ]
        )

    except (AttributeError, KeyError) as err:
        logging.error(f"The model is invalid, missing parameter: {repr(err)}")
        return

    # Prepare data to the table:
    tbl_dict = dict()
    for job, builds in table[u"data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].items():
                tst_name_mod = _tpc_modify_test_name(tst_name)
                if tbl_dict.get(tst_name_mod, None) is None:
                    name = u"-".join(tst_data[u"name"].split(u"-")[:-1])
                    tbl_dict[tst_name_mod] = {
                        u"name": name,
                        u"ref-data": list(),
                        u"cmp-data": list()
                    }
                try:
                    result = None
                    if table[u"include-tests"] == u"MRR":
                        result = tst_data[u"result"][u"receive-rate"]
                    elif table[u"include-tests"] == u"PDR":
                        result = tst_data[u"throughput"][u"PDR"][u"LOWER"]
                    elif table[u"include-tests"] == u"NDR":
                        result = tst_data[u"throughput"][u"NDR"][u"LOWER"]
                    else:
                        continue

                    if result and \
                            table[u"reference"][u"nic"] in tst_data[u"tags"]:
                        tbl_dict[tst_name_mod][u"ref-data"].append(result)
                    elif result and \
                            table[u"compare"][u"nic"] in tst_data[u"tags"]:
                        tbl_dict[tst_name_mod][u"cmp-data"].append(result)
                except (TypeError, KeyError) as err:
                    logging.debug(f"No data for {tst_name}\n{repr(err)}")
                    # No data in output.xml for this test

    tbl_lst = list()
    for tst_name in tbl_dict:
        item = [tbl_dict[tst_name][u"name"], ]
        data_t = tbl_dict[tst_name][u"ref-data"]
        if data_t:
            item.append(round(mean(data_t) / 1000000, 2))
            item.append(round(stdev(data_t) / 1000000, 2))
        else:
            item.extend([None, None])
        data_t = tbl_dict[tst_name][u"cmp-data"]
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
    with open(f"{table[u'output-file']}.csv", u"w") as file_handler:
        file_handler.write(u",".join(header) + u"\n")
        for test in tbl_lst:
            file_handler.write(u",".join([str(item) for item in test]) + u"\n")

    convert_csv_to_pretty_txt(f"{table[u'output-file']}.csv",
                              f"{table[u'output-file']}.txt")

    # Generate html table:
    _tpc_generate_html_table(header, tbl_lst, f"{table[u'output-file']}.html")


def table_soak_vs_ndr(table, input_data):
    """Generate the table(s) with algorithm: table_soak_vs_ndr
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info(f"  Generating the table {table.get(u'title', u'')} ...")

    # Transform the data
    logging.info(
        f"    Creating the data set for the {table.get(u'type', u'')} "
        f"{table.get(u'title', u'')}."
    )
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the table
    try:
        header = [
            u"Test case",
            f"{table[u'reference'][u'title']} Thput [Mpps]",
            f"{table[u'reference'][u'title']} Stdev [Mpps]",
            f"{table[u'compare'][u'title']} Thput [Mpps]",
            f"{table[u'compare'][u'title']} Stdev [Mpps]",
            u"Delta [%]", u"Stdev of delta [%]"
        ]
        header_str = u",".join(header) + u"\n"
    except (AttributeError, KeyError) as err:
        logging.error(f"The model is invalid, missing parameter: {repr(err)}")
        return

    # Create a list of available SOAK test results:
    tbl_dict = dict()
    for job, builds in table[u"compare"][u"data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].items():
                if tst_data[u"type"] == u"SOAK":
                    tst_name_mod = tst_name.replace(u"-soak", u"")
                    if tbl_dict.get(tst_name_mod, None) is None:
                        groups = re.search(REGEX_NIC, tst_data[u"parent"])
                        nic = groups.group(0) if groups else u""
                        name = (
                            f"{nic}-"
                            f"{u'-'.join(tst_data[u'name'].split(u'-')[:-1])}"
                        )
                        tbl_dict[tst_name_mod] = {
                            u"name": name,
                            u"ref-data": list(),
                            u"cmp-data": list()
                        }
                    try:
                        tbl_dict[tst_name_mod][u"cmp-data"].append(
                            tst_data[u"throughput"][u"LOWER"])
                    except (KeyError, TypeError):
                        pass
    tests_lst = tbl_dict.keys()

    # Add corresponding NDR test results:
    for job, builds in table[u"reference"][u"data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].items():
                tst_name_mod = tst_name.replace(u"-ndrpdr", u"").\
                    replace(u"-mrr", u"")
                if tst_name_mod not in tests_lst:
                    continue
                try:
                    if tst_data[u"type"] not in (u"NDRPDR", u"MRR", u"BMRR"):
                        continue
                    if table[u"include-tests"] == u"MRR":
                        result = tst_data[u"result"][u"receive-rate"]
                    elif table[u"include-tests"] == u"PDR":
                        result = \
                            tst_data[u"throughput"][u"PDR"][u"LOWER"]
                    elif table[u"include-tests"] == u"NDR":
                        result = \
                            tst_data[u"throughput"][u"NDR"][u"LOWER"]
                    else:
                        result = None
                    if result is not None:
                        tbl_dict[tst_name_mod][u"ref-data"].append(
                            result)
                except (KeyError, TypeError):
                    continue

    tbl_lst = list()
    for tst_name in tbl_dict:
        item = [tbl_dict[tst_name][u"name"], ]
        data_r = tbl_dict[tst_name][u"ref-data"]
        if data_r:
            data_r_mean = mean(data_r)
            item.append(round(data_r_mean / 1000000, 2))
            data_r_stdev = stdev(data_r)
            item.append(round(data_r_stdev / 1000000, 2))
        else:
            data_r_mean = None
            data_r_stdev = None
            item.extend([None, None])
        data_c = tbl_dict[tst_name][u"cmp-data"]
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
    csv_file = f"{table[u'output-file']}.csv"
    with open(csv_file, u"w") as file_handler:
        file_handler.write(header_str)
        for test in tbl_lst:
            file_handler.write(u",".join([str(item) for item in test]) + u"\n")

    convert_csv_to_pretty_txt(csv_file, f"{table[u'output-file']}.txt")

    # Generate html table:
    _tpc_generate_html_table(header, tbl_lst, f"{table[u'output-file']}.html")


def table_perf_trending_dash(table, input_data):
    """Generate the table(s) with algorithm:
    table_perf_trending_dash
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info(f"  Generating the table {table.get(u'title', u'')} ...")

    # Transform the data
    logging.info(
        f"    Creating the data set for the {table.get(u'type', u'')} "
        f"{table.get(u'title', u'')}."
    )
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the tables
    header = [
        u"Test Case",
        u"Trend [Mpps]",
        u"Short-Term Change [%]",
        u"Long-Term Change [%]",
        u"Regressions [#]",
        u"Progressions [#]"
    ]
    header_str = u",".join(header) + u"\n"

    # Prepare data to the table:
    tbl_dict = dict()
    for job, builds in table[u"data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].items():
                if tst_name.lower() in table.get(u"ignore-list", list()):
                    continue
                if tbl_dict.get(tst_name, None) is None:
                    groups = re.search(REGEX_NIC, tst_data[u"parent"])
                    if not groups:
                        continue
                    nic = groups.group(0)
                    tbl_dict[tst_name] = {
                        u"name": f"{nic}-{tst_data[u'name']}",
                        u"data": OrderedDict()
                    }
                try:
                    tbl_dict[tst_name][u"data"][str(build)] = \
                        tst_data[u"result"][u"receive-rate"]
                except (TypeError, KeyError):
                    pass  # No data in output.xml for this test

    tbl_lst = list()
    for tst_name in tbl_dict:
        data_t = tbl_dict[tst_name][u"data"]
        if len(data_t) < 2:
            continue

        classification_lst, avgs = classify_anomalies(data_t)

        win_size = min(len(data_t), table[u"window"])
        long_win_size = min(len(data_t), table[u"long-trend-window"])

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
            if isnan(last_avg) or isnan(rel_change_last) or \
                    isnan(rel_change_long):
                continue
            tbl_lst.append(
                [tbl_dict[tst_name][u"name"],
                 round(last_avg / 1000000, 2),
                 rel_change_last,
                 rel_change_long,
                 classification_lst[-win_size:].count(u"regression"),
                 classification_lst[-win_size:].count(u"progression")])

    tbl_lst.sort(key=lambda rel: rel[0])

    tbl_sorted = list()
    for nrr in range(table[u"window"], -1, -1):
        tbl_reg = [item for item in tbl_lst if item[4] == nrr]
        for nrp in range(table[u"window"], -1, -1):
            tbl_out = [item for item in tbl_reg if item[5] == nrp]
            tbl_out.sort(key=lambda rel: rel[2])
            tbl_sorted.extend(tbl_out)

    file_name = f"{table[u'output-file']}{table[u'output-file-ext']}"

    logging.info(f"    Writing file: {file_name}")
    with open(file_name, u"w") as file_handler:
        file_handler.write(header_str)
        for test in tbl_sorted:
            file_handler.write(u",".join([str(item) for item in test]) + u'\n')

    logging.info(f"    Writing file: {table[u'output-file']}.txt")
    convert_csv_to_pretty_txt(file_name, f"{table[u'output-file']}.txt")


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
    file_name = u""
    anchor = u".html#"
    feature = u""

    if u"lbdpdk" in test_name or u"lbvpp" in test_name:
        file_name = u"link_bonding"

    elif u"114b" in test_name and u"vhost" in test_name:
        file_name = u"vts"

    elif u"testpmd" in test_name or u"l3fwd" in test_name:
        file_name = u"dpdk"

    elif u"memif" in test_name:
        file_name = u"container_memif"
        feature = u"-base"

    elif u"srv6" in test_name:
        file_name = u"srv6"

    elif u"vhost" in test_name:
        if u"l2xcbase" in test_name or u"l2bdbasemaclrn" in test_name:
            file_name = u"vm_vhost_l2"
            if u"114b" in test_name:
                feature = u""
            elif u"l2xcbase" in test_name and u"x520" in test_name:
                feature = u"-base-l2xc"
            elif u"l2bdbasemaclrn" in test_name and u"x520" in test_name:
                feature = u"-base-l2bd"
            else:
                feature = u"-base"
        elif u"ip4base" in test_name:
            file_name = u"vm_vhost_ip4"
            feature = u"-base"

    elif u"ipsecbasetnlsw" in test_name:
        file_name = u"ipsecsw"
        feature = u"-base-scale"

    elif u"ipsec" in test_name:
        file_name = u"ipsec"
        feature = u"-base-scale"
        if u"hw-" in test_name:
            file_name = u"ipsechw"
        elif u"sw-" in test_name:
            file_name = u"ipsecsw"
        if u"-int-" in test_name:
            feature = u"-base-scale-int"
        elif u"tnl" in test_name:
            feature = u"-base-scale-tnl"

    elif u"ethip4lispip" in test_name or u"ethip4vxlan" in test_name:
        file_name = u"ip4_tunnels"
        feature = u"-base"

    elif u"ip4base" in test_name or u"ip4scale" in test_name:
        file_name = u"ip4"
        if u"xl710" in test_name:
            feature = u"-base-scale-features"
        elif u"iacl" in test_name:
            feature = u"-features-iacl"
        elif u"oacl" in test_name:
            feature = u"-features-oacl"
        elif u"snat" in test_name or u"cop" in test_name:
            feature = u"-features"
        else:
            feature = u"-base-scale"

    elif u"ip6base" in test_name or u"ip6scale" in test_name:
        file_name = u"ip6"
        feature = u"-base-scale"

    elif u"l2xcbase" in test_name or u"l2xcscale" in test_name \
            or u"l2bdbasemaclrn" in test_name or u"l2bdscale" in test_name:
        file_name = u"l2"
        if u"macip" in test_name:
            feature = u"-features-macip"
        elif u"iacl" in test_name:
            feature = u"-features-iacl"
        elif u"oacl" in test_name:
            feature = u"-features-oacl"
        else:
            feature = u"-base-scale"

    if u"x520" in test_name:
        nic = u"x520-"
    elif u"x710" in test_name:
        nic = u"x710-"
    elif u"xl710" in test_name:
        nic = u"xl710-"
    elif u"xxv710" in test_name:
        nic = u"xxv710-"
    elif u"vic1227" in test_name:
        nic = u"vic1227-"
    elif u"vic1385" in test_name:
        nic = u"vic1385-"
    elif u"x553" in test_name:
        nic = u"x553-"
    else:
        nic = u""
    anchor += nic

    if u"64b" in test_name:
        framesize = u"64b"
    elif u"78b" in test_name:
        framesize = u"78b"
    elif u"imix" in test_name:
        framesize = u"imix"
    elif u"9000b" in test_name:
        framesize = u"9000b"
    elif u"1518b" in test_name:
        framesize = u"1518b"
    elif u"114b" in test_name:
        framesize = u"114b"
    else:
        framesize = u""
    anchor += framesize + u"-"

    if u"1t1c" in test_name:
        anchor += u"1t1c"
    elif u"2t2c" in test_name:
        anchor += u"2t2c"
    elif u"4t4c" in test_name:
        anchor += u"4t4c"
    elif u"2t1c" in test_name:
        anchor += u"2t1c"
    elif u"4t2c" in test_name:
        anchor += u"4t2c"
    elif u"8t4c" in test_name:
        anchor += u"8t4c"

    return url + file_name + u"-" + testbed + u"-" + nic + framesize + \
        feature.replace("-int", u"").replace("-tnl", u"") + anchor + feature


def table_perf_trending_dash_html(table, input_data):
    """Generate the table(s) with algorithm:
    table_perf_trending_dash_html specified in the specification
    file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: dict
    :type input_data: InputData
    """

    _ = input_data

    if not table.get(u"testbed", None):
        logging.error(
            f"The testbed is not defined for the table "
            f"{table.get(u'title', u'')}."
        )
        return

    logging.info(f"  Generating the table {table.get(u'title', u'')} ...")

    try:
        with open(table[u"input-file"], u'rt') as csv_file:
            csv_lst = list(csv.reader(csv_file, delimiter=u',', quotechar=u'"'))
    except KeyError:
        logging.warning(u"The input file is not defined.")
        return
    except csv.Error as err:
        logging.warning(
            f"Not possible to process the file {table[u'input-file']}.\n"
            f"{repr(err)}"
        )
        return

    # Table:
    dashboard = ET.Element(u"table", attrib=dict(width=u"100%", border=u'0'))

    # Table header:
    trow = ET.SubElement(dashboard, u"tr", attrib=dict(bgcolor=u"#7eade7"))
    for idx, item in enumerate(csv_lst[0]):
        alignment = u"left" if idx == 0 else u"center"
        thead = ET.SubElement(trow, u"th", attrib=dict(align=alignment))
        thead.text = item

    # Rows:
    colors = {
        u"regression": (
            u"#ffcccc",
            u"#ff9999"
        ),
        u"progression": (
            u"#c6ecc6",
            u"#9fdf9f"
        ),
        u"normal": (
            u"#e9f1fb",
            u"#d4e4f7"
        )
    }
    for r_idx, row in enumerate(csv_lst[1:]):
        if int(row[4]):
            color = u"regression"
        elif int(row[5]):
            color = u"progression"
        else:
            color = u"normal"
        trow = ET.SubElement(
            dashboard, u"tr", attrib=dict(bgcolor=colors[color][r_idx % 2])
        )

        # Columns:
        for c_idx, item in enumerate(row):
            tdata = ET.SubElement(
                trow,
                u"td",
                attrib=dict(align=u"left" if c_idx == 0 else u"center")
            )
            # Name:
            if c_idx == 0:
                ref = ET.SubElement(
                    tdata,
                    u"a",
                    attrib=dict(
                        href=_generate_url(
                            u"../trending/",
                            table.get(u"testbed", None),
                            item
                        )
                    )
                )
                ref.text = item
            else:
                tdata.text = item
    try:
        with open(table[u"output-file"], u'w') as html_file:
            logging.info(f"    Writing file: {table[u'output-file']}")
            html_file.write(u".. raw:: html\n\n\t")
            html_file.write(str(ET.tostring(dashboard, encoding=u"unicode")))
            html_file.write(u"\n\t<p><br><br></p>\n")
    except KeyError:
        logging.warning(u"The output file is not defined.")
        return


def table_last_failed_tests(table, input_data):
    """Generate the table(s) with algorithm: table_last_failed_tests
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info(f"  Generating the table {table.get(u'title', u'')} ...")

    # Transform the data
    logging.info(
        f"    Creating the data set for the {table.get(u'type', u'')} "
        f"{table.get(u'title', u'')}."
    )

    data = input_data.filter_data(table, continue_on_error=True)

    if data is None or data.empty:
        logging.warning(
            f"    No data for the {table.get(u'type', u'')} "
            f"{table.get(u'title', u'')}."
        )
        return

    tbl_list = list()
    for job, builds in table[u"data"].items():
        for build in builds:
            build = str(build)
            try:
                version = input_data.metadata(job, build).get(u"version", u"")
            except KeyError:
                logging.error(f"Data for {job}: {build} is not present.")
                return
            tbl_list.append(build)
            tbl_list.append(version)
            failed_tests = list()
            passed = 0
            failed = 0
            for tst_data in data[job][build].values:
                if tst_data[u"status"] != u"FAIL":
                    passed += 1
                    continue
                failed += 1
                groups = re.search(REGEX_NIC, tst_data[u"parent"])
                if not groups:
                    continue
                nic = groups.group(0)
                failed_tests.append(f"{nic}-{tst_data[u'name']}")
            tbl_list.append(str(passed))
            tbl_list.append(str(failed))
            tbl_list.extend(failed_tests)

    file_name = f"{table[u'output-file']}{table[u'output-file-ext']}"
    logging.info(f"    Writing file: {file_name}")
    with open(file_name, u"w") as file_handler:
        for test in tbl_list:
            file_handler.write(test + u'\n')


def table_failed_tests(table, input_data):
    """Generate the table(s) with algorithm: table_failed_tests
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    logging.info(f"  Generating the table {table.get(u'title', u'')} ...")

    # Transform the data
    logging.info(
        f"    Creating the data set for the {table.get(u'type', u'')} "
        f"{table.get(u'title', u'')}."
    )
    data = input_data.filter_data(table, continue_on_error=True)

    # Prepare the header of the tables
    header = [
        u"Test Case",
        u"Failures [#]",
        u"Last Failure [Time]",
        u"Last Failure [VPP-Build-Id]",
        u"Last Failure [CSIT-Job-Build-Id]"
    ]

    # Generate the data for the table according to the model in the table
    # specification

    now = dt.utcnow()
    timeperiod = timedelta(int(table.get(u"window", 7)))

    tbl_dict = dict()
    for job, builds in table[u"data"].items():
        for build in builds:
            build = str(build)
            for tst_name, tst_data in data[job][build].items():
                if tst_name.lower() in table.get(u"ignore-list", list()):
                    continue
                if tbl_dict.get(tst_name, None) is None:
                    groups = re.search(REGEX_NIC, tst_data[u"parent"])
                    if not groups:
                        continue
                    nic = groups.group(0)
                    tbl_dict[tst_name] = {
                        u"name": f"{nic}-{tst_data[u'name']}",
                        u"data": OrderedDict()
                    }
                try:
                    generated = input_data.metadata(job, build).\
                        get(u"generated", u"")
                    if not generated:
                        continue
                    then = dt.strptime(generated, u"%Y%m%d %H:%M")
                    if (now - then) <= timeperiod:
                        tbl_dict[tst_name][u"data"][build] = (
                            tst_data[u"status"],
                            generated,
                            input_data.metadata(job, build).get(u"version",
                                                                u""),
                            build
                        )
                except (TypeError, KeyError) as err:
                    logging.warning(f"tst_name: {tst_name} - err: {repr(err)}")

    max_fails = 0
    tbl_lst = list()
    for tst_data in tbl_dict.values():
        fails_nr = 0
        fails_last_date = u""
        fails_last_vpp = u""
        fails_last_csit = u""
        for val in tst_data[u"data"].values():
            if val[0] == u"FAIL":
                fails_nr += 1
                fails_last_date = val[1]
                fails_last_vpp = val[2]
                fails_last_csit = val[3]
        if fails_nr:
            max_fails = fails_nr if fails_nr > max_fails else max_fails
            tbl_lst.append(
                [
                    tst_data[u"name"],
                    fails_nr,
                    fails_last_date,
                    fails_last_vpp,
                    f"mrr-daily-build-{fails_last_csit}"
                ]
            )

    tbl_lst.sort(key=lambda rel: rel[2], reverse=True)
    tbl_sorted = list()
    for nrf in range(max_fails, -1, -1):
        tbl_fails = [item for item in tbl_lst if item[1] == nrf]
        tbl_sorted.extend(tbl_fails)

    file_name = f"{table[u'output-file']}{table[u'output-file-ext']}"
    logging.info(f"    Writing file: {file_name}")
    with open(file_name, u"w") as file_handler:
        file_handler.write(u",".join(header) + u"\n")
        for test in tbl_sorted:
            file_handler.write(u",".join([str(item) for item in test]) + u'\n')

    logging.info(f"    Writing file: {table[u'output-file']}.txt")
    convert_csv_to_pretty_txt(file_name, f"{table[u'output-file']}.txt")


def table_failed_tests_html(table, input_data):
    """Generate the table(s) with algorithm: table_failed_tests_html
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    _ = input_data

    if not table.get(u"testbed", None):
        logging.error(
            f"The testbed is not defined for the table "
            f"{table.get(u'title', u'')}."
        )
        return

    logging.info(f"  Generating the table {table.get(u'title', u'')} ...")

    try:
        with open(table[u"input-file"], u'rt') as csv_file:
            csv_lst = list(csv.reader(csv_file, delimiter=u',', quotechar=u'"'))
    except KeyError:
        logging.warning(u"The input file is not defined.")
        return
    except csv.Error as err:
        logging.warning(
            f"Not possible to process the file {table[u'input-file']}.\n"
            f"{repr(err)}"
        )
        return

    # Table:
    failed_tests = ET.Element(u"table", attrib=dict(width=u"100%", border=u'0'))

    # Table header:
    trow = ET.SubElement(failed_tests, u"tr", attrib=dict(bgcolor=u"#7eade7"))
    for idx, item in enumerate(csv_lst[0]):
        alignment = u"left" if idx == 0 else u"center"
        thead = ET.SubElement(trow, u"th", attrib=dict(align=alignment))
        thead.text = item

    # Rows:
    colors = (u"#e9f1fb", u"#d4e4f7")
    for r_idx, row in enumerate(csv_lst[1:]):
        background = colors[r_idx % 2]
        trow = ET.SubElement(
            failed_tests, u"tr", attrib=dict(bgcolor=background)
        )

        # Columns:
        for c_idx, item in enumerate(row):
            tdata = ET.SubElement(
                trow,
                u"td",
                attrib=dict(align=u"left" if c_idx == 0 else u"center")
            )
            # Name:
            if c_idx == 0:
                ref = ET.SubElement(
                    tdata,
                    u"a",
                    attrib=dict(
                        href=_generate_url(
                            u"../trending/",
                            table.get(u"testbed", None),
                            item
                        )
                    )
                )
                ref.text = item
            else:
                tdata.text = item
    try:
        with open(table[u"output-file"], u'w') as html_file:
            logging.info(f"    Writing file: {table[u'output-file']}")
            html_file.write(u".. raw:: html\n\n\t")
            html_file.write(str(ET.tostring(failed_tests, encoding=u"unicode")))
            html_file.write(u"\n\t<p><br><br></p>\n")
    except KeyError:
        logging.warning(u"The output file is not defined.")
        return
