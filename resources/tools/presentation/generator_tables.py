# Copyright (c) 2020 Cisco and/or its affiliates.
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
from copy import deepcopy

import plotly.graph_objects as go
import plotly.offline as ploff
import pandas as pd

from numpy import nan, isnan
from yaml import load, FullLoader, YAMLError

from pal_utils import mean, stdev, classify_anomalies, \
    convert_csv_to_pretty_txt, relative_change_stdev


REGEX_NIC = re.compile(r'(\d*ge\dp\d\D*\d*[a-z]*)')


def generate_tables(spec, data):
    """Generate all tables specified in the specification file.

    :param spec: Specification read from the specification file.
    :param data: Data to process.
    :type spec: Specification
    :type data: InputData
    """

    generator = {
        u"table_merged_details": table_merged_details,
        u"table_perf_comparison": table_perf_comparison,
        u"table_perf_comparison_nic": table_perf_comparison_nic,
        u"table_nics_comparison": table_nics_comparison,
        u"table_soak_vs_ndr": table_soak_vs_ndr,
        u"table_perf_trending_dash": table_perf_trending_dash,
        u"table_perf_trending_dash_html": table_perf_trending_dash_html,
        u"table_last_failed_tests": table_last_failed_tests,
        u"table_failed_tests": table_failed_tests,
        u"table_failed_tests_html": table_failed_tests_html,
        u"table_oper_data_html": table_oper_data_html,
        u"table_comparison": table_comparison
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


def table_oper_data_html(table, input_data):
    """Generate the table(s) with algorithm: html_table_oper_data
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
    data = input_data.filter_data(
        table,
        params=[u"name", u"parent", u"show-run", u"type"],
        continue_on_error=True
    )
    if data.empty:
        return
    data = input_data.merge_data(data)

    sort_tests = table.get(u"sort", None)
    if sort_tests:
        args = dict(
            inplace=True,
            ascending=(sort_tests == u"ascending")
        )
        data.sort_index(**args)

    suites = input_data.filter_data(
        table,
        continue_on_error=True,
        data_set=u"suites"
    )
    if suites.empty:
        return
    suites = input_data.merge_data(suites)

    def _generate_html_table(tst_data):
        """Generate an HTML table with operational data for the given test.

        :param tst_data: Test data to be used to generate the table.
        :type tst_data: pandas.Series
        :returns: HTML table with operational data.
        :rtype: str
        """

        colors = {
            u"header": u"#7eade7",
            u"empty": u"#ffffff",
            u"body": (u"#e9f1fb", u"#d4e4f7")
        }

        tbl = ET.Element(u"table", attrib=dict(width=u"100%", border=u"0"))

        trow = ET.SubElement(tbl, u"tr", attrib=dict(bgcolor=colors[u"header"]))
        thead = ET.SubElement(
            trow, u"th", attrib=dict(align=u"left", colspan=u"6")
        )
        thead.text = tst_data[u"name"]

        trow = ET.SubElement(tbl, u"tr", attrib=dict(bgcolor=colors[u"empty"]))
        thead = ET.SubElement(
            trow, u"th", attrib=dict(align=u"left", colspan=u"6")
        )
        thead.text = u"\t"

        if tst_data.get(u"show-run", u"No Data") == u"No Data":
            trow = ET.SubElement(
                tbl, u"tr", attrib=dict(bgcolor=colors[u"header"])
            )
            tcol = ET.SubElement(
                trow, u"td", attrib=dict(align=u"left", colspan=u"6")
            )
            tcol.text = u"No Data"

            trow = ET.SubElement(
                tbl, u"tr", attrib=dict(bgcolor=colors[u"empty"])
            )
            thead = ET.SubElement(
                trow, u"th", attrib=dict(align=u"left", colspan=u"6")
            )
            font = ET.SubElement(
                thead, u"font", attrib=dict(size=u"12px", color=u"#ffffff")
            )
            font.text = u"."
            return str(ET.tostring(tbl, encoding=u"unicode"))

        tbl_hdr = (
            u"Name",
            u"Nr of Vectors",
            u"Nr of Packets",
            u"Suspends",
            u"Cycles per Packet",
            u"Average Vector Size"
        )

        for dut_data in tst_data[u"show-run"].values():
            trow = ET.SubElement(
                tbl, u"tr", attrib=dict(bgcolor=colors[u"header"])
            )
            tcol = ET.SubElement(
                trow, u"td", attrib=dict(align=u"left", colspan=u"6")
            )
            if dut_data.get(u"threads", None) is None:
                tcol.text = u"No Data"
                continue

            bold = ET.SubElement(tcol, u"b")
            bold.text = (
                f"Host IP: {dut_data.get(u'host', '')}, "
                f"Socket: {dut_data.get(u'socket', '')}"
            )
            trow = ET.SubElement(
                tbl, u"tr", attrib=dict(bgcolor=colors[u"empty"])
            )
            thead = ET.SubElement(
                trow, u"th", attrib=dict(align=u"left", colspan=u"6")
            )
            thead.text = u"\t"

            for thread_nr, thread in dut_data[u"threads"].items():
                trow = ET.SubElement(
                    tbl, u"tr", attrib=dict(bgcolor=colors[u"header"])
                )
                tcol = ET.SubElement(
                    trow, u"td", attrib=dict(align=u"left", colspan=u"6")
                )
                bold = ET.SubElement(tcol, u"b")
                bold.text = u"main" if thread_nr == 0 else f"worker_{thread_nr}"
                trow = ET.SubElement(
                    tbl, u"tr", attrib=dict(bgcolor=colors[u"header"])
                )
                for idx, col in enumerate(tbl_hdr):
                    tcol = ET.SubElement(
                        trow, u"td",
                        attrib=dict(align=u"right" if idx else u"left")
                    )
                    font = ET.SubElement(
                        tcol, u"font", attrib=dict(size=u"2")
                    )
                    bold = ET.SubElement(font, u"b")
                    bold.text = col
                for row_nr, row in enumerate(thread):
                    trow = ET.SubElement(
                        tbl, u"tr",
                        attrib=dict(bgcolor=colors[u"body"][row_nr % 2])
                    )
                    for idx, col in enumerate(row):
                        tcol = ET.SubElement(
                            trow, u"td",
                            attrib=dict(align=u"right" if idx else u"left")
                        )
                        font = ET.SubElement(
                            tcol, u"font", attrib=dict(size=u"2")
                        )
                        if isinstance(col, float):
                            font.text = f"{col:.2f}"
                        else:
                            font.text = str(col)
                trow = ET.SubElement(
                    tbl, u"tr", attrib=dict(bgcolor=colors[u"empty"])
                )
                thead = ET.SubElement(
                    trow, u"th", attrib=dict(align=u"left", colspan=u"6")
                )
                thead.text = u"\t"

        trow = ET.SubElement(tbl, u"tr", attrib=dict(bgcolor=colors[u"empty"]))
        thead = ET.SubElement(
            trow, u"th", attrib=dict(align=u"left", colspan=u"6")
        )
        font = ET.SubElement(
            thead, u"font", attrib=dict(size=u"12px", color=u"#ffffff")
        )
        font.text = u"."

        return str(ET.tostring(tbl, encoding=u"unicode"))

    for suite in suites.values:
        html_table = str()
        for test_data in data.values:
            if test_data[u"parent"] not in suite[u"name"]:
                continue
            html_table += _generate_html_table(test_data)
        if not html_table:
            continue
        try:
            file_name = f"{table[u'output-file']}{suite[u'name']}.rst"
            with open(f"{file_name}", u'w') as html_file:
                logging.info(f"    Writing file: {file_name}")
                html_file.write(u".. raw:: html\n\n\t")
                html_file.write(html_table)
                html_file.write(u"\n\t<p><br><br></p>\n")
        except KeyError:
            logging.warning(u"The output file is not defined.")
            return
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

    sort_tests = table.get(u"sort", None)
    if sort_tests:
        args = dict(
            inplace=True,
            ascending=(sort_tests == u"ascending")
        )
        data.sort_index(**args)

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
                    # Do not include tests with "Test Failed" in test message
                    if u"Test Failed" in col_data:
                        continue
                    col_data = col_data.replace(
                        u"No Data", u"Not Captured     "
                    )
                    if column[u"data"].split(u" ")[1] in (u"name", ):
                        if len(col_data) > 30:
                            col_data_lst = col_data.split(u"-")
                            half = int(len(col_data_lst) / 2)
                            col_data = f"{u'-'.join(col_data_lst[:half])}" \
                                       f"- |br| " \
                                       f"{u'-'.join(col_data_lst[half:])}"
                        col_data = f" |prein| {col_data} |preout| "
                    elif column[u"data"].split(u" ")[1] in (u"msg", ):
                        # Temporary solution: remove NDR results from message:
                        if bool(table.get(u'remove-ndr', False)):
                            try:
                                col_data = col_data.split(u" |br| ", 1)[1]
                            except IndexError:
                                pass
                        col_data = f" |prein| {col_data} |preout| "
                    elif column[u"data"].split(u" ")[1] in \
                            (u"conf-history", u"show-run"):
                        col_data = col_data.replace(u" |br| ", u"", 1)
                        col_data = f" |prein| {col_data[:-5]} |preout| "
                    row_lst.append(f'"{col_data}"')
                except KeyError:
                    row_lst.append(u'"Not captured"')
            if len(row_lst) == len(table[u"columns"]):
                table_lst.append(row_lst)

        # Write the data to file
        if table_lst:
            separator = u"" if table[u'output-file'].endswith(u"/") else u"_"
            file_name = f"{table[u'output-file']}{separator}{suite_name}.csv"
            logging.info(f"      Writing file: {file_name}")
            with open(file_name, u"wt") as file_handler:
                file_handler.write(u",".join(header) + u"\n")
                for item in table_lst:
                    file_handler.write(u",".join(item) + u"\n")

    logging.info(u"  Done.")


def _tpc_modify_test_name(test_name, ignore_nic=False):
    """Modify a test name by replacing its parts.

    :param test_name: Test name to be modified.
    :param ignore_nic: If True, NIC is removed from TC name.
    :type test_name: str
    :type ignore_nic: bool
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

    if ignore_nic:
        return re.sub(REGEX_NIC, u"", test_name_mod)
    return test_name_mod


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
            target.append(
                (
                    src[u"result"][u"receive-rate"],
                    src[u"result"][u"receive-stdev"]
                )
            )
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
    tbl_see.sort(key=lambda rel: rel[-2], reverse=False)
    tbl_delta.sort(key=lambda rel: rel[0], reverse=False)
    tbl_delta.sort(key=lambda rel: rel[-2], reverse=True)

    # Put the tables together:
    table = list()
    # We do not want "New in CSIT":
    # table.extend(tbl_new)
    table.extend(tbl_see)
    table.extend(tbl_delta)

    return table


def _tpc_generate_html_table(header, data, out_file_name, legend=u"",
                             footnote=u"", sort_data=True):
    """Generate html table from input data with simple sorting possibility.

    :param header: Table header.
    :param data: Input data to be included in the table. It is a list of lists.
        Inner lists are rows in the table. All inner lists must be of the same
        length. The length of these lists must be the same as the length of the
        header.
    :param out_file_name: The name (relative or full path) where the
        generated html table is written.
    :param legend: The legend to display below the table.
    :param footnote: The footnote to display below the table (and legend).
    :param sort_data: If True the data sorting is enabled.
    :type header: list
    :type data: list of lists
    :type out_file_name: str
    :type legend: str
    :type footnote: str
    :type sort_data: bool
    """

    try:
        idx = header.index(u"Test Case")
    except ValueError:
        idx = 0
    params = {
        u"align-hdr": (
            [u"left", u"center"],
            [u"left", u"left", u"center"],
            [u"left", u"left", u"left", u"center"]
        ),
        u"align-itm": (
            [u"left", u"right"],
            [u"left", u"left", u"right"],
            [u"left", u"left", u"left", u"right"]
        ),
        u"width": ([28, 9], [4, 24, 10], [4, 4, 32, 10])
    }

    df_data = pd.DataFrame(data, columns=header)

    if sort_data:
        df_sorted = [df_data.sort_values(
            by=[key, header[idx]], ascending=[True, True]
            if key != header[idx] else [False, True]) for key in header]
        df_sorted_rev = [df_data.sort_values(
            by=[key, header[idx]], ascending=[False, True]
            if key != header[idx] else [True, True]) for key in header]
        df_sorted.extend(df_sorted_rev)
    else:
        df_sorted = df_data

    fill_color = [[u"#d4e4f7" if idx % 2 else u"#e9f1fb"
                   for idx in range(len(df_data))]]
    table_header = dict(
        values=[f"<b>{item.replace(u',', u',<br>')}</b>" for item in header],
        fill_color=u"#7eade7",
        align=params[u"align-hdr"][idx]
    )

    fig = go.Figure()

    if sort_data:
        for table in df_sorted:
            columns = [table.get(col) for col in header]
            fig.add_trace(
                go.Table(
                    columnwidth=params[u"width"][idx],
                    header=table_header,
                    cells=dict(
                        values=columns,
                        fill_color=fill_color,
                        align=params[u"align-itm"][idx]
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
                    x=0.0,
                    xanchor=u"left",
                    y=1.045,
                    yanchor=u"top",
                    active=len(menu_items) - 1,
                    buttons=list(buttons)
                )
            ],
        )
    else:
        fig.add_trace(
            go.Table(
                columnwidth=params[u"width"][idx],
                header=table_header,
                cells=dict(
                    values=[df_sorted.get(col) for col in header],
                    fill_color=fill_color,
                    align=params[u"align-itm"][idx]
                )
            )
        )

    ploff.plot(
        fig,
        show_link=False,
        auto_open=False,
        filename=f"{out_file_name}_in.html"
    )

    file_name = out_file_name.split(u"/")[-1]
    if u"vpp" in out_file_name:
        path = u"_tmp/src/vpp_performance_tests/comparisons/"
    else:
        path = u"_tmp/src/dpdk_performance_tests/comparisons/"
    with open(f"{path}{file_name}.rst", u"wt") as rst_file:
        rst_file.write(
            u"\n"
            u".. |br| raw:: html\n\n    <br />\n\n\n"
            u".. |prein| raw:: html\n\n    <pre>\n\n\n"
            u".. |preout| raw:: html\n\n    </pre>\n\n"
        )
        rst_file.write(
            u".. raw:: html\n\n"
            f'    <iframe frameborder="0" scrolling="no" '
            f'width="1600" height="1200" '
            f'src="../..{out_file_name.replace(u"_build", u"")}_in.html">'
            f'</iframe>\n\n'
        )
        if legend:
            rst_file.write(legend[1:].replace(u"\n", u" |br| "))
        if footnote:
            rst_file.write(footnote.replace(u"\n", u" |br| ")[1:])


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
        header = [u"Test Case", ]
        legend = u"\nLegend:\n"

        rca_data = None
        rca = table.get(u"rca", None)
        if rca:
            try:
                with open(rca.get(u"data-file", u""), u"r") as rca_file:
                    rca_data = load(rca_file, Loader=FullLoader)
                header.insert(0, rca.get(u"title", u"RCA"))
                legend += (
                    u"RCA: Reference to the Root Cause Analysis, see below.\n"
                )
            except (YAMLError, IOError) as err:
                logging.warning(repr(err))

        history = table.get(u"history", list())
        for item in history:
            header.extend(
                [
                    f"{item[u'title']} Avg({table[u'include-tests']})",
                    f"{item[u'title']} Stdev({table[u'include-tests']})"
                ]
            )
            legend += (
                f"{item[u'title']} Avg({table[u'include-tests']}): "
                f"Mean value of {table[u'include-tests']} [Mpps] computed from "
                f"a series of runs of the listed tests executed against "
                f"{item[u'title']}.\n"
                f"{item[u'title']} Stdev({table[u'include-tests']}): "
                f"Standard deviation value of {table[u'include-tests']} [Mpps] "
                f"computed from a series of runs of the listed tests executed "
                f"against {item[u'title']}.\n"
            )
        header.extend(
            [
                f"{table[u'reference'][u'title']} "
                f"Avg({table[u'include-tests']})",
                f"{table[u'reference'][u'title']} "
                f"Stdev({table[u'include-tests']})",
                f"{table[u'compare'][u'title']} "
                f"Avg({table[u'include-tests']})",
                f"{table[u'compare'][u'title']} "
                f"Stdev({table[u'include-tests']})",
                f"Diff({table[u'reference'][u'title']},"
                f"{table[u'compare'][u'title']})",
                u"Stdev(Diff)"
            ]
        )
        header_str = u";".join(header) + u"\n"
        legend += (
            f"{table[u'reference'][u'title']} "
            f"Avg({table[u'include-tests']}): "
            f"Mean value of {table[u'include-tests']} [Mpps] computed from a "
            f"series of runs of the listed tests executed against "
            f"{table[u'reference'][u'title']}.\n"
            f"{table[u'reference'][u'title']} "
            f"Stdev({table[u'include-tests']}): "
            f"Standard deviation value of {table[u'include-tests']} [Mpps] "
            f"computed from a series of runs of the listed tests executed "
            f"against {table[u'reference'][u'title']}.\n"
            f"{table[u'compare'][u'title']} "
            f"Avg({table[u'include-tests']}): "
            f"Mean value of {table[u'include-tests']} [Mpps] computed from a "
            f"series of runs of the listed tests executed against "
            f"{table[u'compare'][u'title']}.\n"
            f"{table[u'compare'][u'title']} "
            f"Stdev({table[u'include-tests']}): "
            f"Standard deviation value of {table[u'include-tests']} [Mpps] "
            f"computed from a series of runs of the listed tests executed "
            f"against {table[u'compare'][u'title']}.\n"
            f"Diff({table[u'reference'][u'title']},"
            f"{table[u'compare'][u'title']}): "
            f"Percentage change calculated for mean values.\n"
            u"Stdev(Diff): "
            u"Standard deviation of percentage change calculated for mean "
            u"values.\n"
            u"NT: Not Tested\n"
        )
    except (AttributeError, KeyError) as err:
        logging.error(f"The model is invalid, missing parameter: {repr(err)}")
        return

    # Prepare data to the table:
    tbl_dict = dict()
    for job, builds in table[u"reference"][u"data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].items():
                tst_name_mod = _tpc_modify_test_name(tst_name)
                if (u"across topologies" in table[u"title"].lower() or
                        (u" 3n-" in table[u"title"].lower() and
                         u" 2n-" in table[u"title"].lower())):
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

    replacement = table[u"reference"].get(u"data-replacement", None)
    if replacement:
        create_new_list = True
        rpl_data = input_data.filter_data(
            table, data=replacement, continue_on_error=True)
        for job, builds in replacement.items():
            for build in builds:
                for tst_name, tst_data in rpl_data[job][str(build)].items():
                    tst_name_mod = _tpc_modify_test_name(tst_name)
                    if (u"across topologies" in table[u"title"].lower() or
                            (u" 3n-" in table[u"title"].lower() and
                             u" 2n-" in table[u"title"].lower())):
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
                        tbl_dict[tst_name_mod][u"ref-data"] = list()

                    _tpc_insert_data(
                        target=tbl_dict[tst_name_mod][u"ref-data"],
                        src=tst_data,
                        include_tests=table[u"include-tests"]
                    )

    for job, builds in table[u"compare"][u"data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].items():
                tst_name_mod = _tpc_modify_test_name(tst_name)
                if (u"across topologies" in table[u"title"].lower() or
                        (u" 3n-" in table[u"title"].lower() and
                         u" 2n-" in table[u"title"].lower())):
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
                    if (u"across topologies" in table[u"title"].lower() or
                            (u" 3n-" in table[u"title"].lower() and
                             u" 2n-" in table[u"title"].lower())):
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
                    if (u"across topologies" in table[u"title"].lower() or
                            (u" 3n-" in table[u"title"].lower() and
                             u" 2n-" in table[u"title"].lower())):
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
                            res = (tst_data[u"result"][u"receive-rate"],
                                   tst_data[u"result"][u"receive-stdev"])
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
    for tst_name in tbl_dict:
        item = [tbl_dict[tst_name][u"name"], ]
        if history:
            if tbl_dict[tst_name].get(u"history", None) is not None:
                for hist_data in tbl_dict[tst_name][u"history"].values():
                    if hist_data:
                        if table[u"include-tests"] == u"MRR":
                            item.append(round(hist_data[0][0] / 1e6, 1))
                            item.append(round(hist_data[0][1] / 1e6, 1))
                        else:
                            item.append(round(mean(hist_data) / 1e6, 1))
                            item.append(round(stdev(hist_data) / 1e6, 1))
                    else:
                        item.extend([u"NT", u"NT"])
            else:
                item.extend([u"NT", u"NT"])
        data_r = tbl_dict[tst_name][u"ref-data"]
        if data_r:
            if table[u"include-tests"] == u"MRR":
                data_r_mean = data_r[0][0]
                data_r_stdev = data_r[0][1]
            else:
                data_r_mean = mean(data_r)
                data_r_stdev = stdev(data_r)
            item.append(round(data_r_mean / 1e6, 1))
            item.append(round(data_r_stdev / 1e6, 1))
        else:
            data_r_mean = None
            data_r_stdev = None
            item.extend([u"NT", u"NT"])
        data_c = tbl_dict[tst_name][u"cmp-data"]
        if data_c:
            if table[u"include-tests"] == u"MRR":
                data_c_mean = data_c[0][0]
                data_c_stdev = data_c[0][1]
            else:
                data_c_mean = mean(data_c)
                data_c_stdev = stdev(data_c)
            item.append(round(data_c_mean / 1e6, 1))
            item.append(round(data_c_stdev / 1e6, 1))
        else:
            data_c_mean = None
            data_c_stdev = None
            item.extend([u"NT", u"NT"])
        if item[-2] == u"NT":
            pass
        elif item[-4] == u"NT":
            item.append(u"New in CSIT-2001")
            item.append(u"New in CSIT-2001")
        elif data_r_mean is not None and data_c_mean is not None:
            delta, d_stdev = relative_change_stdev(
                data_r_mean, data_c_mean, data_r_stdev, data_c_stdev
            )
            try:
                item.append(round(delta))
            except ValueError:
                item.append(delta)
            try:
                item.append(round(d_stdev))
            except ValueError:
                item.append(d_stdev)
        if rca_data:
            rca_nr = rca_data.get(item[0], u"-")
            item.insert(0, f"[{rca_nr}]" if rca_nr != u"-" else u"-")
        if (len(item) == len(header)) and (item[-4] != u"NT"):
            tbl_lst.append(item)

    tbl_lst = _tpc_sort_table(tbl_lst)

    # Generate csv tables:
    csv_file = f"{table[u'output-file']}.csv"
    with open(csv_file, u"wt") as file_handler:
        file_handler.write(header_str)
        for test in tbl_lst:
            file_handler.write(u";".join([str(item) for item in test]) + u"\n")

    txt_file_name = f"{table[u'output-file']}.txt"
    convert_csv_to_pretty_txt(csv_file, txt_file_name, delimiter=u";")

    footnote = u""
    with open(txt_file_name, u'a') as txt_file:
        txt_file.write(legend)
        if rca_data:
            footnote = rca_data.get(u"footnote", u"")
            if footnote:
                txt_file.write(footnote)
        txt_file.write(u":END")

    # Generate html table:
    _tpc_generate_html_table(
        header,
        tbl_lst,
        table[u'output-file'],
        legend=legend,
        footnote=footnote
    )


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
        header = [u"Test Case", ]
        legend = u"\nLegend:\n"

        rca_data = None
        rca = table.get(u"rca", None)
        if rca:
            try:
                with open(rca.get(u"data-file", ""), u"r") as rca_file:
                    rca_data = load(rca_file, Loader=FullLoader)
                header.insert(0, rca.get(u"title", "RCA"))
                legend += (
                    u"RCA: Reference to the Root Cause Analysis, see below.\n"
                )
            except (YAMLError, IOError) as err:
                logging.warning(repr(err))

        history = table.get(u"history", list())
        for item in history:
            header.extend(
                [
                    f"{item[u'title']} Avg({table[u'include-tests']})",
                    f"{item[u'title']} Stdev({table[u'include-tests']})"
                ]
            )
            legend += (
                f"{item[u'title']} Avg({table[u'include-tests']}): "
                f"Mean value of {table[u'include-tests']} [Mpps] computed from "
                f"a series of runs of the listed tests executed against "
                f"{item[u'title']}.\n"
                f"{item[u'title']} Stdev({table[u'include-tests']}): "
                f"Standard deviation value of {table[u'include-tests']} [Mpps] "
                f"computed from a series of runs of the listed tests executed "
                f"against {item[u'title']}.\n"
            )
        header.extend(
            [
                f"{table[u'reference'][u'title']} "
                f"Avg({table[u'include-tests']})",
                f"{table[u'reference'][u'title']} "
                f"Stdev({table[u'include-tests']})",
                f"{table[u'compare'][u'title']} "
                f"Avg({table[u'include-tests']})",
                f"{table[u'compare'][u'title']} "
                f"Stdev({table[u'include-tests']})",
                f"Diff({table[u'reference'][u'title']},"
                f"{table[u'compare'][u'title']})",
                u"Stdev(Diff)"
            ]
        )
        header_str = u";".join(header) + u"\n"
        legend += (
            f"{table[u'reference'][u'title']} "
            f"Avg({table[u'include-tests']}): "
            f"Mean value of {table[u'include-tests']} [Mpps] computed from a "
            f"series of runs of the listed tests executed against "
            f"{table[u'reference'][u'title']}.\n"
            f"{table[u'reference'][u'title']} "
            f"Stdev({table[u'include-tests']}): "
            f"Standard deviation value of {table[u'include-tests']} [Mpps] "
            f"computed from a series of runs of the listed tests executed "
            f"against {table[u'reference'][u'title']}.\n"
            f"{table[u'compare'][u'title']} "
            f"Avg({table[u'include-tests']}): "
            f"Mean value of {table[u'include-tests']} [Mpps] computed from a "
            f"series of runs of the listed tests executed against "
            f"{table[u'compare'][u'title']}.\n"
            f"{table[u'compare'][u'title']} "
            f"Stdev({table[u'include-tests']}): "
            f"Standard deviation value of {table[u'include-tests']} [Mpps] "
            f"computed from a series of runs of the listed tests executed "
            f"against {table[u'compare'][u'title']}.\n"
            f"Diff({table[u'reference'][u'title']},"
            f"{table[u'compare'][u'title']}): "
            f"Percentage change calculated for mean values.\n"
            u"Stdev(Diff): "
            u"Standard deviation of percentage change calculated for mean "
            u"values.\n"
            u"NT: Not Tested\n"
        )
    except (AttributeError, KeyError) as err:
        logging.error(f"The model is invalid, missing parameter: {repr(err)}")
        return

    # Prepare data to the table:
    tbl_dict = dict()
    for job, builds in table[u"reference"][u"data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].items():
                if table[u"reference"][u"nic"] not in tst_data[u"tags"]:
                    continue
                tst_name_mod = _tpc_modify_test_name(tst_name)
                if (u"across topologies" in table[u"title"].lower() or
                        (u" 3n-" in table[u"title"].lower() and
                         u" 2n-" in table[u"title"].lower())):
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

    replacement = table[u"reference"].get(u"data-replacement", None)
    if replacement:
        create_new_list = True
        rpl_data = input_data.filter_data(
            table, data=replacement, continue_on_error=True)
        for job, builds in replacement.items():
            for build in builds:
                for tst_name, tst_data in rpl_data[job][str(build)].items():
                    if table[u"reference"][u"nic"] not in tst_data[u"tags"]:
                        continue
                    tst_name_mod = _tpc_modify_test_name(tst_name)
                    if (u"across topologies" in table[u"title"].lower() or
                            (u" 3n-" in table[u"title"].lower() and
                             u" 2n-" in table[u"title"].lower())):
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
                        tbl_dict[tst_name_mod][u"ref-data"] = list()

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
                if (u"across topologies" in table[u"title"].lower() or
                        (u" 3n-" in table[u"title"].lower() and
                         u" 2n-" in table[u"title"].lower())):
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
                    if (u"across topologies" in table[u"title"].lower() or
                            (u" 3n-" in table[u"title"].lower() and
                             u" 2n-" in table[u"title"].lower())):
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
                    if (u"across topologies" in table[u"title"].lower() or
                            (u" 3n-" in table[u"title"].lower() and
                             u" 2n-" in table[u"title"].lower())):
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
                            res = (tst_data[u"result"][u"receive-rate"],
                                   tst_data[u"result"][u"receive-stdev"])
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
    for tst_name in tbl_dict:
        item = [tbl_dict[tst_name][u"name"], ]
        if history:
            if tbl_dict[tst_name].get(u"history", None) is not None:
                for hist_data in tbl_dict[tst_name][u"history"].values():
                    if hist_data:
                        if table[u"include-tests"] == u"MRR":
                            item.append(round(hist_data[0][0] / 1e6, 1))
                            item.append(round(hist_data[0][1] / 1e6, 1))
                        else:
                            item.append(round(mean(hist_data) / 1e6, 1))
                            item.append(round(stdev(hist_data) / 1e6, 1))
                    else:
                        item.extend([u"NT", u"NT"])
            else:
                item.extend([u"NT", u"NT"])
        data_r = tbl_dict[tst_name][u"ref-data"]
        if data_r:
            if table[u"include-tests"] == u"MRR":
                data_r_mean = data_r[0][0]
                data_r_stdev = data_r[0][1]
            else:
                data_r_mean = mean(data_r)
                data_r_stdev = stdev(data_r)
            item.append(round(data_r_mean / 1e6, 1))
            item.append(round(data_r_stdev / 1e6, 1))
        else:
            data_r_mean = None
            data_r_stdev = None
            item.extend([u"NT", u"NT"])
        data_c = tbl_dict[tst_name][u"cmp-data"]
        if data_c:
            if table[u"include-tests"] == u"MRR":
                data_c_mean = data_c[0][0]
                data_c_stdev = data_c[0][1]
            else:
                data_c_mean = mean(data_c)
                data_c_stdev = stdev(data_c)
            item.append(round(data_c_mean / 1e6, 1))
            item.append(round(data_c_stdev / 1e6, 1))
        else:
            data_c_mean = None
            data_c_stdev = None
            item.extend([u"NT", u"NT"])
        if item[-2] == u"NT":
            pass
        elif item[-4] == u"NT":
            item.append(u"New in CSIT-2001")
            item.append(u"New in CSIT-2001")
        elif data_r_mean is not None and data_c_mean is not None:
            delta, d_stdev = relative_change_stdev(
                data_r_mean, data_c_mean, data_r_stdev, data_c_stdev
            )
            try:
                item.append(round(delta))
            except ValueError:
                item.append(delta)
            try:
                item.append(round(d_stdev))
            except ValueError:
                item.append(d_stdev)
        if rca_data:
            rca_nr = rca_data.get(item[0], u"-")
            item.insert(0, f"[{rca_nr}]" if rca_nr != u"-" else u"-")
        if (len(item) == len(header)) and (item[-4] != u"NT"):
            tbl_lst.append(item)

    tbl_lst = _tpc_sort_table(tbl_lst)

    # Generate csv tables:
    csv_file = f"{table[u'output-file']}.csv"
    with open(csv_file, u"wt") as file_handler:
        file_handler.write(header_str)
        for test in tbl_lst:
            file_handler.write(u";".join([str(item) for item in test]) + u"\n")

    txt_file_name = f"{table[u'output-file']}.txt"
    convert_csv_to_pretty_txt(csv_file, txt_file_name, delimiter=u";")

    footnote = u""
    with open(txt_file_name, u'a') as txt_file:
        txt_file.write(legend)
        if rca_data:
            footnote = rca_data.get(u"footnote", u"")
            if footnote:
                txt_file.write(footnote)
        txt_file.write(u":END")

    # Generate html table:
    _tpc_generate_html_table(
        header,
        tbl_lst,
        table[u'output-file'],
        legend=legend,
        footnote=footnote
    )


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
        header = [
            u"Test Case",
            f"{table[u'reference'][u'title']} "
            f"Avg({table[u'include-tests']})",
            f"{table[u'reference'][u'title']} "
            f"Stdev({table[u'include-tests']})",
            f"{table[u'compare'][u'title']} "
            f"Avg({table[u'include-tests']})",
            f"{table[u'compare'][u'title']} "
            f"Stdev({table[u'include-tests']})",
            f"Diff({table[u'reference'][u'title']},"
            f"{table[u'compare'][u'title']})",
            u"Stdev(Diff)"
        ]
        legend = (
            u"\nLegend:\n"
            f"{table[u'reference'][u'title']} "
            f"Avg({table[u'include-tests']}): "
            f"Mean value of {table[u'include-tests']} [Mpps] computed from a "
            f"series of runs of the listed tests executed using "
            f"{table[u'reference'][u'title']} NIC.\n"
            f"{table[u'reference'][u'title']} "
            f"Stdev({table[u'include-tests']}): "
            f"Standard deviation value of {table[u'include-tests']} [Mpps] "
            f"computed from a series of runs of the listed tests executed "
            f"using {table[u'reference'][u'title']} NIC.\n"
            f"{table[u'compare'][u'title']} "
            f"Avg({table[u'include-tests']}): "
            f"Mean value of {table[u'include-tests']} [Mpps] computed from a "
            f"series of runs of the listed tests executed using "
            f"{table[u'compare'][u'title']} NIC.\n"
            f"{table[u'compare'][u'title']} "
            f"Stdev({table[u'include-tests']}): "
            f"Standard deviation value of {table[u'include-tests']} [Mpps] "
            f"computed from a series of runs of the listed tests executed "
            f"using {table[u'compare'][u'title']} NIC.\n"
            f"Diff({table[u'reference'][u'title']},"
            f"{table[u'compare'][u'title']}): "
            f"Percentage change calculated for mean values.\n"
            u"Stdev(Diff): "
            u"Standard deviation of percentage change calculated for mean "
            u"values.\n"
            u":END"
        )

    except (AttributeError, KeyError) as err:
        logging.error(f"The model is invalid, missing parameter: {repr(err)}")
        return

    # Prepare data to the table:
    tbl_dict = dict()
    for job, builds in table[u"data"].items():
        for build in builds:
            for tst_name, tst_data in data[job][str(build)].items():
                tst_name_mod = _tpc_modify_test_name(tst_name, ignore_nic=True)
                if tbl_dict.get(tst_name_mod, None) is None:
                    name = u"-".join(tst_data[u"name"].split(u"-")[:-1])
                    tbl_dict[tst_name_mod] = {
                        u"name": name,
                        u"ref-data": list(),
                        u"cmp-data": list()
                    }
                try:
                    if table[u"include-tests"] == u"MRR":
                        result = (tst_data[u"result"][u"receive-rate"],
                                  tst_data[u"result"][u"receive-stdev"])
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
        data_r = tbl_dict[tst_name][u"ref-data"]
        if data_r:
            if table[u"include-tests"] == u"MRR":
                data_r_mean = data_r[0][0]
                data_r_stdev = data_r[0][1]
            else:
                data_r_mean = mean(data_r)
                data_r_stdev = stdev(data_r)
            item.append(round(data_r_mean / 1e6, 1))
            item.append(round(data_r_stdev / 1e6, 1))
        else:
            data_r_mean = None
            data_r_stdev = None
            item.extend([None, None])
        data_c = tbl_dict[tst_name][u"cmp-data"]
        if data_c:
            if table[u"include-tests"] == u"MRR":
                data_c_mean = data_c[0][0]
                data_c_stdev = data_c[0][1]
            else:
                data_c_mean = mean(data_c)
                data_c_stdev = stdev(data_c)
            item.append(round(data_c_mean / 1e6, 1))
            item.append(round(data_c_stdev / 1e6, 1))
        else:
            data_c_mean = None
            data_c_stdev = None
            item.extend([None, None])
        if data_r_mean is not None and data_c_mean is not None:
            delta, d_stdev = relative_change_stdev(
                data_r_mean, data_c_mean, data_r_stdev, data_c_stdev
            )
            try:
                item.append(round(delta))
            except ValueError:
                item.append(delta)
            try:
                item.append(round(d_stdev))
            except ValueError:
                item.append(d_stdev)
            tbl_lst.append(item)

    # Sort the table according to the relative change
    tbl_lst.sort(key=lambda rel: rel[-1], reverse=True)

    # Generate csv tables:
    with open(f"{table[u'output-file']}.csv", u"wt") as file_handler:
        file_handler.write(u";".join(header) + u"\n")
        for test in tbl_lst:
            file_handler.write(u";".join([str(item) for item in test]) + u"\n")

    convert_csv_to_pretty_txt(f"{table[u'output-file']}.csv",
                              f"{table[u'output-file']}.txt",
                              delimiter=u";")

    with open(table[u'output-file'], u'a') as txt_file:
        txt_file.write(legend)

    # Generate html table:
    _tpc_generate_html_table(
        header,
        tbl_lst,
        table[u'output-file'],
        legend=legend
    )


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
            u"Test Case",
            f"Avg({table[u'reference'][u'title']})",
            f"Stdev({table[u'reference'][u'title']})",
            f"Avg({table[u'compare'][u'title']})",
            f"Stdev{table[u'compare'][u'title']})",
            u"Diff",
            u"Stdev(Diff)"
        ]
        header_str = u";".join(header) + u"\n"
        legend = (
            u"\nLegend:\n"
            f"Avg({table[u'reference'][u'title']}): "
            f"Mean value of {table[u'reference'][u'title']} [Mpps] computed "
            f"from a series of runs of the listed tests.\n"
            f"Stdev({table[u'reference'][u'title']}): "
            f"Standard deviation value of {table[u'reference'][u'title']} "
            f"[Mpps] computed from a series of runs of the listed tests.\n"
            f"Avg({table[u'compare'][u'title']}): "
            f"Mean value of {table[u'compare'][u'title']} [Mpps] computed from "
            f"a series of runs of the listed tests.\n"
            f"Stdev({table[u'compare'][u'title']}): "
            f"Standard deviation value of {table[u'compare'][u'title']} [Mpps] "
            f"computed from a series of runs of the listed tests.\n"
            f"Diff({table[u'reference'][u'title']},"
            f"{table[u'compare'][u'title']}): "
            f"Percentage change calculated for mean values.\n"
            u"Stdev(Diff): "
            u"Standard deviation of percentage change calculated for mean "
            u"values.\n"
            u":END"
        )
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
                        result = (tst_data[u"result"][u"receive-rate"],
                                  tst_data[u"result"][u"receive-stdev"])
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
            if table[u"include-tests"] == u"MRR":
                data_r_mean = data_r[0][0]
                data_r_stdev = data_r[0][1]
            else:
                data_r_mean = mean(data_r)
                data_r_stdev = stdev(data_r)
            item.append(round(data_r_mean / 1e6, 1))
            item.append(round(data_r_stdev / 1e6, 1))
        else:
            data_r_mean = None
            data_r_stdev = None
            item.extend([None, None])
        data_c = tbl_dict[tst_name][u"cmp-data"]
        if data_c:
            if table[u"include-tests"] == u"MRR":
                data_c_mean = data_c[0][0]
                data_c_stdev = data_c[0][1]
            else:
                data_c_mean = mean(data_c)
                data_c_stdev = stdev(data_c)
            item.append(round(data_c_mean / 1e6, 1))
            item.append(round(data_c_stdev / 1e6, 1))
        else:
            data_c_mean = None
            data_c_stdev = None
            item.extend([None, None])
        if data_r_mean is not None and data_c_mean is not None:
            delta, d_stdev = relative_change_stdev(
                data_r_mean, data_c_mean, data_r_stdev, data_c_stdev)
            try:
                item.append(round(delta))
            except ValueError:
                item.append(delta)
            try:
                item.append(round(d_stdev))
            except ValueError:
                item.append(d_stdev)
            tbl_lst.append(item)

    # Sort the table according to the relative change
    tbl_lst.sort(key=lambda rel: rel[-1], reverse=True)

    # Generate csv tables:
    csv_file = f"{table[u'output-file']}.csv"
    with open(csv_file, u"wt") as file_handler:
        file_handler.write(header_str)
        for test in tbl_lst:
            file_handler.write(u";".join([str(item) for item in test]) + u"\n")

    convert_csv_to_pretty_txt(
        csv_file, f"{table[u'output-file']}.txt", delimiter=u";"
    )
    with open(f"{table[u'output-file']}.txt", u'a') as txt_file:
        txt_file.write(legend)

    # Generate html table:
    _tpc_generate_html_table(
        header,
        tbl_lst,
        table[u'output-file'],
        legend=legend
    )


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
    with open(file_name, u"wt") as file_handler:
        file_handler.write(header_str)
        for test in tbl_sorted:
            file_handler.write(u",".join([str(item) for item in test]) + u'\n')

    logging.info(f"    Writing file: {table[u'output-file']}.txt")
    convert_csv_to_pretty_txt(file_name, f"{table[u'output-file']}.txt")


def _generate_url(testbed, test_name):
    """Generate URL to a trending plot from the name of the test case.

    :param testbed: The testbed used for testing.
    :param test_name: The name of the test case.
    :type testbed: str
    :type test_name: str
    :returns: The URL to the plot with the trending data for the given test
        case.
    :rtype str
    """

    if u"x520" in test_name:
        nic = u"x520"
    elif u"x710" in test_name:
        nic = u"x710"
    elif u"xl710" in test_name:
        nic = u"xl710"
    elif u"xxv710" in test_name:
        nic = u"xxv710"
    elif u"vic1227" in test_name:
        nic = u"vic1227"
    elif u"vic1385" in test_name:
        nic = u"vic1385"
    elif u"x553" in test_name:
        nic = u"x553"
    elif u"cx556" in test_name or u"cx556a" in test_name:
        nic = u"cx556a"
    else:
        nic = u""

    if u"64b" in test_name:
        frame_size = u"64b"
    elif u"78b" in test_name:
        frame_size = u"78b"
    elif u"imix" in test_name:
        frame_size = u"imix"
    elif u"9000b" in test_name:
        frame_size = u"9000b"
    elif u"1518b" in test_name:
        frame_size = u"1518b"
    elif u"114b" in test_name:
        frame_size = u"114b"
    else:
        frame_size = u""

    if u"1t1c" in test_name or \
        (u"-1c-" in test_name and
         testbed in (u"3n-hsw", u"3n-tsh", u"2n-dnv", u"3n-dnv")):
        cores = u"1t1c"
    elif u"2t2c" in test_name or \
         (u"-2c-" in test_name and
          testbed in (u"3n-hsw", u"3n-tsh", u"2n-dnv", u"3n-dnv")):
        cores = u"2t2c"
    elif u"4t4c" in test_name or \
         (u"-4c-" in test_name and
          testbed in (u"3n-hsw", u"3n-tsh", u"2n-dnv", u"3n-dnv")):
        cores = u"4t4c"
    elif u"2t1c" in test_name or \
         (u"-1c-" in test_name and
          testbed in (u"2n-skx", u"3n-skx", u"2n-clx")):
        cores = u"2t1c"
    elif u"4t2c" in test_name or \
         (u"-2c-" in test_name and
          testbed in (u"2n-skx", u"3n-skx", u"2n-clx")):
        cores = u"4t2c"
    elif u"8t4c" in test_name or \
         (u"-4c-" in test_name and
          testbed in (u"2n-skx", u"3n-skx", u"2n-clx")):
        cores = u"8t4c"
    else:
        cores = u""

    if u"testpmd" in test_name:
        driver = u"testpmd"
    elif u"l3fwd" in test_name:
        driver = u"l3fwd"
    elif u"avf" in test_name:
        driver = u"avf"
    elif u"rdma" in test_name:
        driver = u"rdma"
    elif u"dnv" in testbed or u"tsh" in testbed:
        driver = u"ixgbe"
    else:
        driver = u"dpdk"

    if u"acl" in test_name or \
            u"macip" in test_name or \
            u"nat" in test_name or \
            u"policer" in test_name or \
            u"cop" in test_name:
        bsf = u"features"
    elif u"scale" in test_name:
        bsf = u"scale"
    elif u"base" in test_name:
        bsf = u"base"
    else:
        bsf = u"base"

    if u"114b" in test_name and u"vhost" in test_name:
        domain = u"vts"
    elif u"testpmd" in test_name or u"l3fwd" in test_name:
        domain = u"dpdk"
    elif u"memif" in test_name:
        domain = u"container_memif"
    elif u"srv6" in test_name:
        domain = u"srv6"
    elif u"vhost" in test_name:
        domain = u"vhost"
        if u"vppl2xc" in test_name:
            driver += u"-vpp"
        else:
            driver += u"-testpmd"
        if u"lbvpplacp" in test_name:
            bsf += u"-link-bonding"
    elif u"ch" in test_name and u"vh" in test_name and u"vm" in test_name:
        domain = u"nf_service_density_vnfc"
    elif u"ch" in test_name and u"mif" in test_name and u"dcr" in test_name:
        domain = u"nf_service_density_cnfc"
    elif u"pl" in test_name and u"mif" in test_name and u"dcr" in test_name:
        domain = u"nf_service_density_cnfp"
    elif u"ipsec" in test_name:
        domain = u"ipsec"
        if u"sw" in test_name:
            bsf += u"-sw"
        elif u"hw" in test_name:
            bsf += u"-hw"
    elif u"ethip4vxlan" in test_name:
        domain = u"ip4_tunnels"
    elif u"ip4base" in test_name or u"ip4scale" in test_name:
        domain = u"ip4"
    elif u"ip6base" in test_name or u"ip6scale" in test_name:
        domain = u"ip6"
    elif u"l2xcbase" in test_name or \
            u"l2xcscale" in test_name or \
            u"l2bdbasemaclrn" in test_name or \
            u"l2bdscale" in test_name or \
            u"l2patch" in test_name:
        domain = u"l2"
    else:
        domain = u""

    file_name = u"-".join((domain, testbed, nic)) + u".html#"
    anchor_name = u"-".join((frame_size, cores, bsf, driver))

    return file_name + anchor_name


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
                        href=f"../trending/"
                             f"{_generate_url(table.get(u'testbed', ''), item)}"
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
    with open(file_name, u"wt") as file_handler:
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
    with open(file_name, u"wt") as file_handler:
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
                        href=f"../trending/"
                             f"{_generate_url(table.get(u'testbed', ''), item)}"
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


def table_comparison(table, input_data):
    """Generate the table(s) with algorithm: table_comparison
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

    columns = table.get(u"columns", None)
    if not columns:
        logging.error(
            f"No columns specified for {table.get(u'title', u'')}. Skipping."
        )
        return

    cols = list()
    for idx, col in enumerate(columns):
        if col.get(u"data-set", None) is None:
            logging.warning(f"No data for column {col.get(u'title', u'')}")
            continue
        data = input_data.filter_data(
            table,
            params=[u"throughput", u"result", u"name", u"parent", u"tags"],
            data=col[u"data-set"],
            continue_on_error=True
        )
        col_data = {
            u"title": col.get(u"title", f"Column{idx}"),
            u"data": dict()
        }
        for builds in data.values:
            for build in builds:
                for tst_name, tst_data in build.items():
                    tst_name_mod = \
                        _tpc_modify_test_name(tst_name).replace(u"2n1l-", u"")
                    if col_data[u"data"].get(tst_name_mod, None) is None:
                        name = f"{tst_data[u'name'].rsplit(u'-', 1)[0]}"
                        if u"across testbeds" in table[u"title"].lower() or \
                                u"across topologies" in table[u"title"].lower():
                            name = _tpc_modify_displayed_test_name(name)
                        col_data[u"data"][tst_name_mod] = {
                            u"name": name,
                            u"replace": True,
                            u"data": list(),
                            u"mean": None,
                            u"stdev": None
                        }
                    _tpc_insert_data(
                        target=col_data[u"data"][tst_name_mod][u"data"],
                        src=tst_data,
                        include_tests=table[u"include-tests"]
                    )

        replacement = col.get(u"data-replacement", None)
        if replacement:
            rpl_data = input_data.filter_data(
                table,
                params=[u"throughput", u"result", u"name", u"parent", u"tags"],
                data=replacement,
                continue_on_error=True
            )
            for job, builds in rpl_data.items():
                for build in builds:
                    for tst_name, tst_data in build.items():
                        tst_name_mod = \
                            _tpc_modify_test_name(tst_name).\
                            replace(u"2n1l-", u"")
                        if col_data[u"data"].get(tst_name_mod, None) is None:
                            name = f"{tst_data[u'name'].rsplit(u'-', 1)[0]}"
                            if u"across testbeds" in table[u"title"].lower() \
                                    or u"across topologies" in \
                                    table[u"title"].lower():
                                name = _tpc_modify_displayed_test_name(name)
                            col_data[u"data"][tst_name_mod] = {
                                u"name": name,
                                u"replace": False,
                                u"data": list(),
                                u"mean": None,
                                u"stdev": None
                            }
                        if col_data[u"data"][tst_name_mod][u"replace"]:
                            col_data[u"data"][tst_name_mod][u"replace"] = False
                            col_data[u"data"][tst_name_mod][u"data"] = list()
                        _tpc_insert_data(
                            target=col_data[u"data"][tst_name_mod][u"data"],
                            src=tst_data,
                            include_tests=table[u"include-tests"]
                        )

        if table[u"include-tests"] in (u"NDR", u"PDR"):
            for tst_name, tst_data in col_data[u"data"].items():
                if tst_data[u"data"]:
                    tst_data[u"mean"] = mean(tst_data[u"data"])
                    tst_data[u"stdev"] = stdev(tst_data[u"data"])
        elif table[u"include-tests"] in (u"MRR", ):
            for tst_name, tst_data in col_data[u"data"].items():
                if tst_data[u"data"]:
                    tst_data[u"mean"] = tst_data[u"data"][0]
                    tst_data[u"stdev"] = tst_data[u"data"][0]

        cols.append(col_data)

    tbl_dict = dict()
    for col in cols:
        for tst_name, tst_data in col[u"data"].items():
            if tbl_dict.get(tst_name, None) is None:
                tbl_dict[tst_name] = {
                    "name": tst_data[u"name"]
                }
            tbl_dict[tst_name][col[u"title"]] = {
                u"mean": tst_data[u"mean"],
                u"stdev": tst_data[u"stdev"]
            }

    tbl_lst=list()
    for tst_data in tbl_dict.values():
        row = [tst_data[u"name"], ]
        for col in cols:
            row.append(tst_data.get(col[u"title"], None))
        tbl_lst.append(row)

    comparisons = table.get(u"comparisons", None)
    if comparisons and isinstance(comparisons, list):
        for idx, comp in enumerate(comparisons):
            try:
                col_ref = int(comp[u"reference"])
                col_cmp = int(comp[u"compare"])
            except KeyError:
                logging.warning(u"Comparison: No references defined! Skipping.")
                comparisons.pop(idx)
                continue
            if not (0 < col_ref <= len(cols) and
                    0 < col_cmp <= len(cols)) or \
                    col_ref == col_cmp:
                logging.warning(f"Wrong values of reference={col_ref} "
                                f"and/or compare={col_cmp}. Skipping.")
                comparisons.pop(idx)
                continue

    tbl_cmp_lst = list()
    if comparisons:
        for row in tbl_lst:
            new_row = deepcopy(row)
            add_to_tbl = False
            for comp in comparisons:
                ref_itm = row[int(comp[u"reference"])]
                if ref_itm is None and \
                        comp.get(u"reference-alt", None) is not None:
                    ref_itm = row[int(comp[u"reference-alt"])]
                cmp_itm = row[int(comp[u"compare"])]
                if ref_itm is not None and cmp_itm is not None and \
                        ref_itm[u"mean"] is not None and \
                        cmp_itm[u"mean"] is not None and \
                        ref_itm[u"stdev"] is not None and \
                        cmp_itm[u"stdev"] is not None:
                    delta, d_stdev = relative_change_stdev(
                        ref_itm[u"mean"], cmp_itm[u"mean"],
                        ref_itm[u"stdev"], cmp_itm[u"stdev"]
                    )
                    new_row.append(
                        {
                            u"mean": delta * 1e6,
                            u"stdev": d_stdev * 1e6
                        }
                    )
                    add_to_tbl = True
                else:
                    new_row.append(None)
            if add_to_tbl:
                tbl_cmp_lst.append(new_row)

    tbl_cmp_lst.sort(key=lambda rel: rel[0], reverse=False)
    tbl_cmp_lst.sort(key=lambda rel: rel[-1][u'mean'], reverse=True)

    rcas = list()
    rca_in = table.get(u"rca", None)
    if rca_in and isinstance(rca_in, list):
        for idx, itm in enumerate(rca_in):
            try:
                with open(itm.get(u"data", u""), u"r") as rca_file:
                    rcas.append(
                        {
                            u"title": itm.get(u"title", f"RCA{idx}"),
                            u"data": load(rca_file, Loader=FullLoader)
                        }
                    )
            except (YAMLError, IOError) as err:
                logging.warning(
                    f"The RCA file {itm.get(u'data', u'')} does not exist or "
                    f"it is corrupted!"
                )
                logging.debug(repr(err))

    tbl_for_csv = list()
    for line in tbl_cmp_lst:
        row = [line[0], ]
        for idx, itm in enumerate(line[1:]):
            if itm is None:
                row.append(u"NT")
                row.append(u"NT")
            else:
                row.append(round(float(itm[u'mean']) / 1e6, 3))
                row.append(round(float(itm[u'stdev']) / 1e6, 3))
        for rca in rcas:
            rca_nr = rca[u"data"].get(row[0], u"-")
            row.append(f"[{rca_nr}]" if rca_nr != u"-" else u"-")
        tbl_for_csv.append(row)

    header_csv = [u"Test Case", ]
    for col in cols:
        header_csv.append(f"Avg({col[u'title']})")
        header_csv.append(f"Stdev({col[u'title']})")
    for comp in comparisons:
        header_csv.append(
            f"Avg({cols[comp[u'reference'] - 1][u'title']},"
            f"{cols[comp[u'compare'] - 1][u'title']})"
        )
        header_csv.append(
            f"Stdev({cols[comp[u'reference'] - 1][u'title']},"
            f"{cols[comp[u'compare'] - 1][u'title']})"
        )
    header_csv.extend([rca[u"title"] for rca in rcas])

    legend_lst = table.get(u"legend", None)
    if legend_lst is None:
        legend = u""
    else:
        legend = u"\n" + u"\n".join(legend_lst) + u"\n"

    footnote = u""
    for rca in rcas:
        footnote += f"\n{rca[u'title']}:\n"
        footnote += rca[u"data"].get(u"footnote", u"")

    csv_file = f"{table[u'output-file']}-csv.csv"
    with open(csv_file, u"wt", encoding='utf-8') as file_handler:
        file_handler.write(u";".join(header_csv) + u"\n")
        for test in tbl_for_csv:
            file_handler.write(u";".join([str(item) for item in test]) + u"\n")
        if legend_lst:
            for item in legend_lst:
                file_handler.write(f"{item}\n")
        if footnote:
            file_handler.write(footnote)

    tbl_final = list()
    for line in tbl_cmp_lst:
        row = [line[0], ]
        for idx, itm in enumerate(line[1:]):
            if itm is None:
                row.append(u"NT")
            else:
                if idx < len(cols):
                    row.append(
                        f"{round(float(itm[u'mean']) / 1e6, 1)} "
                        f"\u00B1{round(float(itm[u'stdev']) / 1e6, 1)}".
                        replace(u"nan", u"NaN")
                    )
                else:
                    row.append(
                        f"{round(float(itm[u'mean']) / 1e6, 1):+} "
                        f"\u00B1{round(float(itm[u'stdev']) / 1e6, 1)}".
                        replace(u"nan", u"NaN")
                    )
        for rca in rcas:
            rca_nr = rca[u"data"].get(row[0], u"-")
            row.append(f"[{rca_nr}]" if rca_nr != u"-" else u"-")
        tbl_final.append(row)

    header = [u"Test Case", ]
    header.extend([col[u"title"] for col in cols])
    header.extend([comp.get(u"title", u"") for comp in comparisons])
    header.extend([rca[u"title"] for rca in rcas])

    # Generate csv tables:
    csv_file = f"{table[u'output-file']}.csv"
    with open(csv_file, u"wt", encoding='utf-8') as file_handler:
        file_handler.write(u";".join(header) + u"\n")
        for test in tbl_final:
            file_handler.write(u";".join([str(item) for item in test]) + u"\n")

    # Generate txt table:
    txt_file_name = f"{table[u'output-file']}.txt"
    convert_csv_to_pretty_txt(csv_file, txt_file_name, delimiter=u";")

    with open(txt_file_name, u'a', encoding='utf-8') as txt_file:
        txt_file.write(legend)
        if footnote:
            txt_file.write(footnote)
        txt_file.write(u":END")

    # Generate html table:
    _tpc_generate_html_table(
        header,
        tbl_final,
        table[u'output-file'],
        legend=legend,
        footnote=footnote,
        sort_data=False
    )
