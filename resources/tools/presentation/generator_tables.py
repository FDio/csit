# Copyright (c) 2022 Cisco and/or its affiliates.
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
import math
import re

from collections import OrderedDict
from xml.etree import ElementTree as ET
from datetime import datetime as dt
from datetime import timedelta
from copy import deepcopy

import plotly.graph_objects as go
import plotly.offline as ploff
import pandas as pd
import prettytable

from numpy import nan, isnan
from yaml import load, FullLoader, YAMLError

from pal_utils import mean, stdev, classify_anomalies, \
    convert_csv_to_pretty_txt, relative_change_stdev, relative_change


REGEX_NIC = re.compile(r'(\d*ge\dp\d\D*\d*[a-z]*)')

NORM_FREQ = 2.0  # [GHz]


def generate_tables(spec, data):
    """Generate all tables specified in the specification file.

    :param spec: Specification read from the specification file.
    :param data: Data to process.
    :type spec: Specification
    :type data: InputData
    """

    generator = {
        "table_merged_details": table_merged_details,
        "table_soak_vs_ndr": table_soak_vs_ndr,
        "table_perf_trending_dash": table_perf_trending_dash,
        "table_perf_trending_dash_html": table_perf_trending_dash_html,
        "table_last_failed_tests": table_last_failed_tests,
        "table_failed_tests": table_failed_tests,
        "table_failed_tests_html": table_failed_tests_html,
        "table_oper_data_html": table_oper_data_html,
        "table_comparison": table_comparison,
        "table_weekly_comparison": table_weekly_comparison,
        "table_job_spec_duration": table_job_spec_duration
    }

    logging.info(u"Generating the tables ...")

    norm_factor = dict()
    for key, val in spec.environment.get("frequency", dict()).items():
        norm_factor[key] = NORM_FREQ / val

    for table in spec.tables:
        try:
            if table["algorithm"] == "table_weekly_comparison":
                table["testbeds"] = spec.environment.get("testbeds", None)
            if table["algorithm"] == "table_comparison":
                table["norm_factor"] = norm_factor
            generator[table["algorithm"]](table, data)
        except NameError as err:
            logging.error(
                f"Probably algorithm {table['algorithm']} is not defined: "
                f"{repr(err)}"
            )
    logging.info("Done.")


def table_job_spec_duration(table, input_data):
    """Generate the table(s) with algorithm: table_job_spec_duration
    specified in the specification file.

    :param table: Table to generate.
    :param input_data: Data to process.
    :type table: pandas.Series
    :type input_data: InputData
    """

    _ = input_data

    logging.info(f"  Generating the table {table.get(u'title', u'')} ...")

    jb_type = table.get(u"jb-type", None)

    tbl_lst = list()
    if jb_type == u"iterative":
        for line in table.get(u"lines", tuple()):
            tbl_itm = {
                u"name": line.get(u"job-spec", u""),
                u"data": list()
            }
            for job, builds in line.get(u"data-set", dict()).items():
                for build_nr in builds:
                    try:
                        minutes = input_data.metadata(
                            job, str(build_nr)
                        )[u"elapsedtime"] // 60000
                    except (KeyError, IndexError, ValueError, AttributeError):
                        continue
                    tbl_itm[u"data"].append(minutes)
            tbl_itm[u"mean"] = mean(tbl_itm[u"data"])
            tbl_itm[u"stdev"] = stdev(tbl_itm[u"data"])
            tbl_lst.append(tbl_itm)
    elif jb_type == u"coverage":
        job = table.get(u"data", None)
        if not job:
            return
        for line in table.get(u"lines", tuple()):
            try:
                tbl_itm = {
                    u"name": line.get(u"job-spec", u""),
                    u"mean": input_data.metadata(
                        list(job.keys())[0], str(line[u"build"])
                    )[u"elapsedtime"] // 60000,
                    u"stdev": float(u"nan")
                }
                tbl_itm[u"data"] = [tbl_itm[u"mean"], ]
            except (KeyError, IndexError, ValueError, AttributeError):
                continue
            tbl_lst.append(tbl_itm)
    else:
        logging.warning(f"Wrong type of job-spec: {jb_type}. Skipping.")
        return

    for line in tbl_lst:
        line[u"mean"] = \
            f"{int(line[u'mean'] // 60):02d}:{int(line[u'mean'] % 60):02d}"
        if math.isnan(line[u"stdev"]):
            line[u"stdev"] = u""
        else:
            line[u"stdev"] = \
                f"{int(line[u'stdev'] //60):02d}:{int(line[u'stdev'] % 60):02d}"

    if not tbl_lst:
        return

    rows = list()
    for itm in tbl_lst:
        rows.append([
            itm[u"name"],
            f"{len(itm[u'data'])}",
            f"{itm[u'mean']} +- {itm[u'stdev']}"
            if itm[u"stdev"] != u"" else f"{itm[u'mean']}"
        ])

    txt_table = prettytable.PrettyTable(
        [u"Job Specification", u"Nr of Runs", u"Duration [HH:MM]"]
    )
    for row in rows:
        txt_table.add_row(row)
    txt_table.align = u"r"
    txt_table.align[u"Job Specification"] = u"l"

    file_name = f"{table.get(u'output-file', u'')}.txt"
    with open(file_name, u"wt", encoding='utf-8') as txt_file:
        txt_file.write(str(txt_table))


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
        params=[u"name", u"parent", u"telemetry-show-run", u"type"],
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

        if tst_data.get(u"telemetry-show-run", None) is None or \
                isinstance(tst_data[u"telemetry-show-run"], str):
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

        for dut_data in tst_data[u"telemetry-show-run"].values():
            trow = ET.SubElement(
                tbl, u"tr", attrib=dict(bgcolor=colors[u"header"])
            )
            tcol = ET.SubElement(
                trow, u"td", attrib=dict(align=u"left", colspan=u"6")
            )
            if dut_data.get(u"runtime", None) is None:
                tcol.text = u"No Data"
                continue

            runtime = dict()
            for item in dut_data[u"runtime"].get(u"data", tuple()):
                tid = int(item[u"labels"][u"thread_id"])
                if runtime.get(tid, None) is None:
                    runtime[tid] = dict()
                gnode = item[u"labels"][u"graph_node"]
                if runtime[tid].get(gnode, None) is None:
                    runtime[tid][gnode] = dict()
                try:
                    runtime[tid][gnode][item[u"name"]] = float(item[u"value"])
                except ValueError:
                    runtime[tid][gnode][item[u"name"]] = item[u"value"]

            threads = dict({idx: list() for idx in range(len(runtime))})
            for idx, run_data in runtime.items():
                for gnode, gdata in run_data.items():
                    threads[idx].append([
                        gnode,
                        int(gdata[u"calls"]),
                        int(gdata[u"vectors"]),
                        int(gdata[u"suspends"]),
                        float(gdata[u"clocks"]),
                        float(gdata[u"vectors"] / gdata[u"calls"]) \
                            if gdata[u"calls"] else 0.0
                    ])

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

            for thread_nr, thread in threads.items():
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
            if data[test][u"status"] != u"PASS" or \
                    data[test][u"parent"] not in suite_name:
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
                                col_data = col_data.split(u"\n", 1)[1]
                            except IndexError:
                                pass
                        col_data = col_data.replace(u'\n', u' |br| ').\
                            replace(u'\r', u'').replace(u'"', u"'")
                        col_data = f" |prein| {col_data} |preout| "
                    elif column[u"data"].split(u" ")[1] in (u"conf-history", ):
                        col_data = col_data.replace(u'\n', u' |br| ')
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
        replace(u"-ndrpdr", u"").\
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
    :param src: Source data to be placed into the target structure.
    :param include_tests: Which results will be included (MRR, NDR, PDR).
    :type target: list
    :type src: dict
    :type include_tests: str
    """
    try:
        if include_tests == u"MRR":
            target[u"mean"] = src[u"result"][u"receive-rate"]
            target[u"stdev"] = src[u"result"][u"receive-stdev"]
        elif include_tests == u"PDR":
            target[u"data"].append(src[u"throughput"][u"PDR"][u"LOWER"])
        elif include_tests == u"NDR":
            target[u"data"].append(src[u"throughput"][u"NDR"][u"LOWER"])
        elif u"latency" in include_tests:
            keys = include_tests.split(u"-")
            if len(keys) == 4:
                lat = src[keys[0]][keys[1]][keys[2]][keys[3]]
                target[u"data"].append(
                    float(u"nan") if lat == -1 else lat * 1e6
                )
        elif include_tests == u"hoststack":
            try:
                target[u"data"].append(
                    float(src[u"result"][u"bits_per_second"])
                )
            except KeyError:
                target[u"data"].append(
                    (float(src[u"result"][u"client"][u"tx_data"]) * 8) /
                    ((float(src[u"result"][u"client"][u"time"]) +
                      float(src[u"result"][u"server"][u"time"])) / 2)
                )
        elif include_tests == u"vsap":
            try:
                target[u"data"].append(src[u"result"][u"cps"])
            except KeyError:
                target[u"data"].append(src[u"result"][u"rps"])
    except (KeyError, TypeError):
        pass


def _tpc_generate_html_table(header, data, out_file_name, legend=u"",
                             footnote=u"", sort_data=True, title=u"",
                             generate_rst=True):
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
    :param title: The table (and file) title.
    :param generate_rst: If True, wrapping rst file is generated.
    :type header: list
    :type data: list of lists
    :type out_file_name: str
    :type legend: str
    :type footnote: str
    :type sort_data: bool
    :type title: str
    :type generate_rst: bool
    """

    try:
        idx = header.index(u"Test Case")
    except ValueError:
        idx = 0
    params = {
        u"align-hdr": (
            [u"left", u"right"],
            [u"left", u"left", u"right"],
            [u"left", u"left", u"left", u"right"]
        ),
        u"align-itm": (
            [u"left", u"right"],
            [u"left", u"left", u"right"],
            [u"left", u"left", u"left", u"right"]
        ),
        u"width": ([15, 9], [4, 24, 10], [4, 4, 32, 10])
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
        align=params[u"align-hdr"][idx],
        font=dict(
            family=u"Courier New",
            size=12
        )
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
                        align=params[u"align-itm"][idx],
                        font=dict(
                            family=u"Courier New",
                            size=12
                        )
                    )
                )
            )

        buttons = list()
        menu_items = [f"<b>{itm}</b> (ascending)" for itm in header]
        menu_items.extend([f"<b>{itm}</b> (descending)" for itm in header])
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
                    y=1.002,
                    yanchor=u"bottom",
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
                    align=params[u"align-itm"][idx],
                    font=dict(
                        family=u"Courier New",
                        size=12
                    )
                )
            )
        )

    ploff.plot(
        fig,
        show_link=False,
        auto_open=False,
        filename=f"{out_file_name}_in.html"
    )

    if not generate_rst:
        return

    file_name = out_file_name.split(u"/")[-1]
    if u"vpp" in out_file_name:
        path = u"_tmp/src/vpp_performance_tests/comparisons/"
    else:
        path = u"_tmp/src/dpdk_performance_tests/comparisons/"
    logging.info(f"    Writing the HTML file to {path}{file_name}.rst")
    with open(f"{path}{file_name}.rst", u"wt") as rst_file:
        rst_file.write(
            u"\n"
            u".. |br| raw:: html\n\n    <br />\n\n\n"
            u".. |prein| raw:: html\n\n    <pre>\n\n\n"
            u".. |preout| raw:: html\n\n    </pre>\n\n"
        )
        if title:
            rst_file.write(f"{title}\n")
            rst_file.write(f"{u'`' * len(title)}\n\n")
        rst_file.write(
            u".. raw:: html\n\n"
            f'    <iframe frameborder="0" scrolling="no" '
            f'width="1600" height="1200" '
            f'src="../..{out_file_name.replace(u"_build", u"")}_in.html">'
            f'</iframe>\n\n'
        )

        if legend:
            try:
                itm_lst = legend[1:-2].split(u"\n")
                rst_file.write(
                    f"{itm_lst[0]}\n\n- " + u'\n- '.join(itm_lst[1:]) + u"\n\n"
                )
            except IndexError as err:
                logging.error(f"Legend cannot be written to html file\n{err}")
        if footnote:
            try:
                itm_lst = footnote[1:].split(u"\n")
                rst_file.write(
                    f"{itm_lst[0]}\n\n- " + u'\n- '.join(itm_lst[1:]) + u"\n\n"
                )
            except IndexError as err:
                logging.error(f"Footnote cannot be written to html file\n{err}")


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
            u"values."
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
            item.append(round(data_c_mean / 1e6, 2))
            item.append(round(data_c_stdev / 1e6, 2))
        else:
            data_c_mean = None
            data_c_stdev = None
            item.extend([None, None])
        if data_r_mean is not None and data_c_mean is not None:
            delta, d_stdev = relative_change_stdev(
                data_r_mean, data_c_mean, data_r_stdev, data_c_stdev)
            try:
                item.append(round(delta, 2))
            except ValueError:
                item.append(delta)
            try:
                item.append(round(d_stdev, 2))
            except ValueError:
                item.append(d_stdev)
            tbl_lst.append(item)

    # Sort the table according to the relative change
    tbl_lst.sort(key=lambda rel: rel[-1], reverse=True)

    # Generate csv tables:
    csv_file_name = f"{table[u'output-file']}.csv"
    with open(csv_file_name, u"wt") as file_handler:
        file_handler.write(header_str)
        for test in tbl_lst:
            file_handler.write(u";".join([str(item) for item in test]) + u"\n")

    convert_csv_to_pretty_txt(
        csv_file_name, f"{table[u'output-file']}.txt", delimiter=u";"
    )
    with open(f"{table[u'output-file']}.txt", u'a') as file_handler:
        file_handler.write(legend)

    # Generate html table:
    _tpc_generate_html_table(
        header,
        tbl_lst,
        table[u'output-file'],
        legend=legend,
        title=table.get(u"title", u"")
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
        u"Runs [#]",
        u"Long-Term Change [%]",
        u"Regressions [#]",
        u"Progressions [#]"
    ]
    header_str = u",".join(header) + u"\n"

    incl_tests = table.get(u"include-tests", u"MRR")

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
                    if incl_tests == u"MRR":
                        tbl_dict[tst_name][u"data"][str(build)] = \
                            tst_data[u"result"][u"receive-rate"]
                    elif incl_tests == u"NDR":
                        tbl_dict[tst_name][u"data"][str(build)] = \
                            tst_data[u"throughput"][u"NDR"][u"LOWER"]
                    elif incl_tests == u"PDR":
                        tbl_dict[tst_name][u"data"][str(build)] = \
                            tst_data[u"throughput"][u"PDR"][u"LOWER"]
                except (TypeError, KeyError):
                    pass  # No data in output.xml for this test

    tbl_lst = list()
    for tst_name in tbl_dict:
        data_t = tbl_dict[tst_name][u"data"]
        if len(data_t) < 2:
            continue

        try:
            classification_lst, avgs, _ = classify_anomalies(data_t)
        except ValueError as err:
            logging.info(f"{err} Skipping")
            return

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

        nr_of_last_avgs = 0;
        for x in reversed(avgs):
            if x == last_avg:
                nr_of_last_avgs += 1
            else:
                break

        if isnan(last_avg) or isnan(avg_week_ago) or avg_week_ago == 0.0:
            rel_change_last = nan
        else:
            rel_change_last = round(
                ((last_avg - avg_week_ago) / avg_week_ago) * 1e2, 2)

        if isnan(max_long_avg) or isnan(last_avg) or max_long_avg == 0.0:
            rel_change_long = nan
        else:
            rel_change_long = round(
                ((last_avg - max_long_avg) / max_long_avg) * 1e2, 2)

        if classification_lst:
            if isnan(rel_change_last) and isnan(rel_change_long):
                continue
            if isnan(last_avg) or isnan(rel_change_last) or \
                    isnan(rel_change_long):
                continue
            tbl_lst.append(
                [tbl_dict[tst_name][u"name"],
                 round(last_avg / 1e6, 2),
                 nr_of_last_avgs,
                 rel_change_long,
                 classification_lst[-win_size+1:].count(u"regression"),
                 classification_lst[-win_size+1:].count(u"progression")])

    tbl_lst.sort(key=lambda rel: rel[0])
    tbl_lst.sort(key=lambda rel: rel[2])
    tbl_lst.sort(key=lambda rel: rel[3])
    tbl_lst.sort(key=lambda rel: rel[5], reverse=True)
    tbl_lst.sort(key=lambda rel: rel[4], reverse=True)

    file_name = f"{table[u'output-file']}{table[u'output-file-ext']}"

    logging.info(f"    Writing file: {file_name}")
    with open(file_name, u"wt") as file_handler:
        file_handler.write(header_str)
        for test in tbl_lst:
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
    elif u"ena" in test_name:
        nic = u"nitro50g"
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
         testbed in (u"3n-hsw", u"3n-tsh", u"2n-dnv", u"3n-dnv", u"2n-tx2")):
        cores = u"1t1c"
    elif u"2t2c" in test_name or \
         (u"-2c-" in test_name and
          testbed in (u"3n-hsw", u"3n-tsh", u"2n-dnv", u"3n-dnv", u"2n-tx2")):
        cores = u"2t2c"
    elif u"4t4c" in test_name or \
         (u"-4c-" in test_name and
          testbed in (u"3n-hsw", u"3n-tsh", u"2n-dnv", u"3n-dnv", u"2n-tx2")):
        cores = u"4t4c"
    elif u"2t1c" in test_name or \
         (u"-1c-" in test_name and
          testbed in
          (u"2n-icx", u"3n-icx", u"2n-skx", u"3n-skx", u"2n-clx", u"2n-zn2",
           u"2n-aws", u"3n-aws")):
        cores = u"2t1c"
    elif u"4t2c" in test_name or \
         (u"-2c-" in test_name and
          testbed in
          (u"2n-icx", u"3n-icx", u"2n-skx", u"3n-skx", u"2n-clx", u"2n-zn2",
           u"2n-aws", u"3n-aws")):
        cores = u"4t2c"
    elif u"8t4c" in test_name or \
         (u"-4c-" in test_name and
          testbed in
          (u"2n-icx", u"3n-icx", u"2n-skx", u"3n-skx", u"2n-clx", u"2n-zn2",
           u"2n-aws", u"3n-aws")):
        cores = u"8t4c"
    else:
        cores = u""

    if u"testpmd" in test_name:
        driver = u"testpmd"
    elif u"l3fwd" in test_name:
        driver = u"l3fwd"
    elif u"avf" in test_name:
        driver = u"avf"
    elif u"af-xdp" in test_name or u"af_xdp" in test_name:
        driver = u"af_xdp"
    elif u"rdma" in test_name:
        driver = u"rdma"
    elif u"dnv" in testbed or u"tsh" in testbed:
        driver = u"ixgbe"
    elif u"ena" in test_name:
        driver = u"ena"
    else:
        driver = u"dpdk"

    if u"macip-iacl1s" in test_name:
        bsf = u"features-macip-iacl1"
    elif u"macip-iacl10s" in test_name:
        bsf = u"features-macip-iacl10"
    elif u"macip-iacl50s" in test_name:
        bsf = u"features-macip-iacl50"
    elif u"iacl1s" in test_name:
        bsf = u"features-iacl1"
    elif u"iacl10s" in test_name:
        bsf = u"features-iacl10"
    elif u"iacl50s" in test_name:
        bsf = u"features-iacl50"
    elif u"oacl1s" in test_name:
        bsf = u"features-oacl1"
    elif u"oacl10s" in test_name:
        bsf = u"features-oacl10"
    elif u"oacl50s" in test_name:
        bsf = u"features-oacl50"
    elif u"nat44det" in test_name:
        bsf = u"nat44det-bidir"
    elif u"nat44ed" in test_name and u"udir" in test_name:
        bsf = u"nat44ed-udir"
    elif u"-cps" in test_name and u"ethip4udp" in test_name:
        bsf = u"udp-cps"
    elif u"-cps" in test_name and u"ethip4tcp" in test_name:
        bsf = u"tcp-cps"
    elif u"-pps" in test_name and u"ethip4udp" in test_name:
        bsf = u"udp-pps"
    elif u"-pps" in test_name and u"ethip4tcp" in test_name:
        bsf = u"tcp-pps"
    elif u"-tput" in test_name and u"ethip4udp" in test_name:
        bsf = u"udp-tput"
    elif u"-tput" in test_name and u"ethip4tcp" in test_name:
        bsf = u"tcp-tput"
    elif u"udpsrcscale" in test_name:
        bsf = u"features-udp"
    elif u"iacl" in test_name:
        bsf = u"features"
    elif u"policer" in test_name:
        bsf = u"features"
    elif u"adl" in test_name:
        bsf = u"features"
    elif u"cop" in test_name:
        bsf = u"features"
    elif u"nat" in test_name:
        bsf = u"features"
    elif u"macip" in test_name:
        bsf = u"features"
    elif u"scale" in test_name:
        bsf = u"scale"
    elif u"base" in test_name:
        bsf = u"base"
    else:
        bsf = u"base"

    if u"114b" in test_name and u"vhost" in test_name:
        domain = u"vts"
    elif u"nat44" in test_name or u"-pps" in test_name or u"-cps" in test_name:
        domain = u"nat44"
        if u"nat44det" in test_name:
            domain += u"-det-bidir"
        else:
            domain += u"-ed"
        if u"udir" in test_name:
            domain += u"-unidir"
        elif u"-ethip4udp-" in test_name:
            domain += u"-udp"
        elif u"-ethip4tcp-" in test_name:
            domain += u"-tcp"
        if u"-cps" in test_name:
            domain += u"-cps"
        elif u"-pps" in test_name:
            domain += u"-pps"
        elif u"-tput" in test_name:
            domain += u"-tput"
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
        elif u"spe" in test_name:
            bsf += u"-spe"
    elif u"ethip4vxlan" in test_name:
        domain = u"ip4_tunnels"
    elif u"ethip4udpgeneve" in test_name:
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
            f"{table.get(u'title', u'')}. Skipping."
        )
        return

    test_type = table.get(u"test-type", u"MRR")
    if test_type not in (u"MRR", u"NDR", u"PDR"):
        logging.error(
            f"Test type {table.get(u'test-type', u'MRR')} is not defined. "
            f"Skipping."
        )
        return

    if test_type in (u"NDR", u"PDR"):
        lnk_dir = u"../ndrpdr_trending/"
        lnk_sufix = f"-{test_type.lower()}"
    else:
        lnk_dir = u"../trending/"
        lnk_sufix = u""

    logging.info(f"  Generating the table {table.get(u'title', u'')} ...")

    try:
        with open(table[u"input-file"], u'rt') as csv_file:
            csv_lst = list(csv.reader(csv_file, delimiter=u',', quotechar=u'"'))
    except FileNotFoundError as err:
        logging.warning(f"{err}")
        return
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
            if c_idx == 0 and table.get(u"add-links", True):
                ref = ET.SubElement(
                    tdata,
                    u"a",
                    attrib=dict(
                        href=f"{lnk_dir}"
                        f"{_generate_url(table.get(u'testbed', ''), item)}"
                        f"{lnk_sufix}"
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
                duration = \
                    input_data.metadata(job, build).get(u"elapsedtime", u"")
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
                msg = tst_data[u'msg'].replace(u"\n", u"")
                msg = re.sub(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
                             'xxx.xxx.xxx.xxx', msg)
                msg = msg.split(u'Also teardown failed')[0]
                failed_tests.append(f"{nic}-{tst_data[u'name']}###{msg}")
            tbl_list.append(passed)
            tbl_list.append(failed)
            tbl_list.append(duration)
            tbl_list.extend(failed_tests)

    file_name = f"{table[u'output-file']}{table[u'output-file-ext']}"
    logging.info(f"    Writing file: {file_name}")
    with open(file_name, u"wt") as file_handler:
        for test in tbl_list:
            file_handler.write(f"{test}\n")


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

    test_type = u"MRR"
    if u"NDRPDR" in table.get(u"filter", list()):
        test_type = u"NDRPDR"

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
            tbl_lst.append([
                tst_data[u"name"],
                fails_nr,
                fails_last_date,
                fails_last_vpp,
                f"{u'mrr-daily' if test_type == u'MRR' else u'ndrpdr-weekly'}"
                f"-build-{fails_last_csit}"
            ])

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
            f"{table.get(u'title', u'')}. Skipping."
        )
        return

    test_type = table.get(u"test-type", u"MRR")
    if test_type not in (u"MRR", u"NDR", u"PDR", u"NDRPDR"):
        logging.error(
            f"Test type {table.get(u'test-type', u'MRR')} is not defined. "
            f"Skipping."
        )
        return

    if test_type in (u"NDRPDR", u"NDR", u"PDR"):
        lnk_dir = u"../ndrpdr_trending/"
        lnk_sufix = u"-pdr"
    else:
        lnk_dir = u"../trending/"
        lnk_sufix = u""

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
            if c_idx == 0 and table.get(u"add-links", True):
                ref = ET.SubElement(
                    tdata,
                    u"a",
                    attrib=dict(
                        href=f"{lnk_dir}"
                        f"{_generate_url(table.get(u'testbed', ''), item)}"
                        f"{lnk_sufix}"
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
    logging.info(f"  Generating the table {table.get('title', '')} ...")

    # Transform the data
    logging.info(
        f"    Creating the data set for the {table.get('type', '')} "
        f"{table.get('title', '')}."
    )

    columns = table.get("columns", None)
    if not columns:
        logging.error(
            f"No columns specified for {table.get('title', '')}. Skipping."
        )
        return

    cols = list()
    for idx, col in enumerate(columns):
        if col.get("data-set", None) is None:
            logging.warning(f"No data for column {col.get('title', '')}")
            continue
        tag = col.get("tag", None)
        data = input_data.filter_data(
            table,
            params=[
                "throughput",
                "result",
                "latency",
                "name",
                "parent",
                "tags"
            ],
            data=col["data-set"],
            continue_on_error=True
        )
        col_data = {
            "title": col.get("title", f"Column{idx}"),
            "data": dict()
        }
        for builds in data.values:
            for build in builds:
                for tst_name, tst_data in build.items():
                    if tag and tag not in tst_data["tags"]:
                        continue
                    tst_name_mod = \
                        _tpc_modify_test_name(tst_name, ignore_nic=True).\
                        replace("2n1l-", "")
                    if col_data["data"].get(tst_name_mod, None) is None:
                        name = tst_data['name'].rsplit('-', 1)[0]
                        if "across testbeds" in table["title"].lower() or \
                                "across topologies" in table["title"].lower():
                            name = _tpc_modify_displayed_test_name(name)
                        col_data["data"][tst_name_mod] = {
                            "name": name,
                            "replace": True,
                            "data": list(),
                            "mean": None,
                            "stdev": None
                        }
                    _tpc_insert_data(
                        target=col_data["data"][tst_name_mod],
                        src=tst_data,
                        include_tests=table["include-tests"]
                    )

        replacement = col.get("data-replacement", None)
        if replacement:
            rpl_data = input_data.filter_data(
                table,
                params=[
                    "throughput",
                    "result",
                    "latency",
                    "name",
                    "parent",
                    "tags"
                ],
                data=replacement,
                continue_on_error=True
            )
            for builds in rpl_data.values:
                for build in builds:
                    for tst_name, tst_data in build.items():
                        if tag and tag not in tst_data["tags"]:
                            continue
                        tst_name_mod = \
                            _tpc_modify_test_name(tst_name, ignore_nic=True).\
                            replace("2n1l-", "")
                        if col_data["data"].get(tst_name_mod, None) is None:
                            name = tst_data['name'].rsplit('-', 1)[0]
                            if "across testbeds" in table["title"].lower() \
                                    or "across topologies" in \
                                    table["title"].lower():
                                name = _tpc_modify_displayed_test_name(name)
                            col_data["data"][tst_name_mod] = {
                                "name": name,
                                "replace": False,
                                "data": list(),
                                "mean": None,
                                "stdev": None
                            }
                        if col_data["data"][tst_name_mod]["replace"]:
                            col_data["data"][tst_name_mod]["replace"] = False
                            col_data["data"][tst_name_mod]["data"] = list()
                        _tpc_insert_data(
                            target=col_data["data"][tst_name_mod],
                            src=tst_data,
                            include_tests=table["include-tests"]
                        )

        if table["include-tests"] in ("NDR", "PDR", "hoststack", "vsap") \
                or "latency" in table["include-tests"]:
            for tst_name, tst_data in col_data["data"].items():
                if tst_data["data"]:
                    tst_data["mean"] = mean(tst_data["data"])
                    tst_data["stdev"] = stdev(tst_data["data"])

        cols.append(col_data)

    tbl_dict = dict()
    for col in cols:
        for tst_name, tst_data in col["data"].items():
            if tbl_dict.get(tst_name, None) is None:
                tbl_dict[tst_name] = {
                    "name": tst_data["name"]
                }
            tbl_dict[tst_name][col["title"]] = {
                "mean": tst_data["mean"],
                "stdev": tst_data["stdev"]
            }

    if not tbl_dict:
        logging.warning(f"No data for table {table.get('title', '')}!")
        return

    tbl_lst = list()
    for tst_data in tbl_dict.values():
        row = [tst_data[u"name"], ]
        for col in cols:
            row.append(tst_data.get(col[u"title"], None))
        tbl_lst.append(row)

    comparisons = table.get("comparisons", None)
    rcas = list()
    if comparisons and isinstance(comparisons, list):
        for idx, comp in enumerate(comparisons):
            try:
                col_ref = int(comp["reference"])
                col_cmp = int(comp["compare"])
            except KeyError:
                logging.warning("Comparison: No references defined! Skipping.")
                comparisons.pop(idx)
                continue
            if not (0 < col_ref <= len(cols) and 0 < col_cmp <= len(cols) or
                    col_ref == col_cmp):
                logging.warning(f"Wrong values of reference={col_ref} "
                                f"and/or compare={col_cmp}. Skipping.")
                comparisons.pop(idx)
                continue
            rca_file_name = comp.get("rca-file", None)
            if rca_file_name:
                try:
                    with open(rca_file_name, "r") as file_handler:
                        rcas.append(
                            {
                                "title": f"RCA{idx + 1}",
                                "data": load(file_handler, Loader=FullLoader)
                            }
                        )
                except (YAMLError, IOError) as err:
                    logging.warning(
                        f"The RCA file {rca_file_name} does not exist or "
                        f"it is corrupted!"
                    )
                    logging.debug(repr(err))
                    rcas.append(None)
            else:
                rcas.append(None)
    else:
        comparisons = None

    tbl_cmp_lst = list()
    if comparisons:
        for row in tbl_lst:
            new_row = deepcopy(row)
            for comp in comparisons:
                ref_itm = row[int(comp["reference"])]
                if ref_itm is None and \
                        comp.get("reference-alt", None) is not None:
                    ref_itm = row[int(comp["reference-alt"])]
                cmp_itm = row[int(comp[u"compare"])]
                if ref_itm is not None and cmp_itm is not None and \
                        ref_itm["mean"] is not None and \
                        cmp_itm["mean"] is not None and \
                        ref_itm["stdev"] is not None and \
                        cmp_itm["stdev"] is not None:
                    norm_factor_ref = table["norm_factor"].get(
                        comp.get("norm-ref", ""),
                        1.0
                    )
                    norm_factor_cmp = table["norm_factor"].get(
                        comp.get("norm-cmp", ""),
                        1.0
                    )
                    try:
                        delta, d_stdev = relative_change_stdev(
                            ref_itm["mean"] * norm_factor_ref,
                            cmp_itm["mean"] * norm_factor_cmp,
                            ref_itm["stdev"] * norm_factor_ref,
                            cmp_itm["stdev"] * norm_factor_cmp
                        )
                    except ZeroDivisionError:
                        break
                    if delta is None or math.isnan(delta):
                        break
                    new_row.append({
                        "mean": delta * 1e6,
                        "stdev": d_stdev * 1e6
                    })
                else:
                    break
            else:
                tbl_cmp_lst.append(new_row)

    try:
        tbl_cmp_lst.sort(key=lambda rel: rel[0], reverse=False)
        tbl_cmp_lst.sort(key=lambda rel: rel[-1]['mean'], reverse=True)
    except TypeError as err:
        logging.warning(f"Empty data element in table\n{tbl_cmp_lst}\n{err}")

    tbl_for_csv = list()
    for line in tbl_cmp_lst:
        row = [line[0], ]
        for idx, itm in enumerate(line[1:]):
            if itm is None or not isinstance(itm, dict) or\
                    itm.get('mean', None) is None or \
                    itm.get('stdev', None) is None:
                row.append("NT")
                row.append("NT")
            else:
                row.append(round(float(itm['mean']) / 1e6, 3))
                row.append(round(float(itm['stdev']) / 1e6, 3))
        for rca in rcas:
            if rca is None:
                continue
            rca_nr = rca["data"].get(row[0], "-")
            row.append(f"[{rca_nr}]" if rca_nr != "-" else "-")
        tbl_for_csv.append(row)

    header_csv = ["Test Case", ]
    for col in cols:
        header_csv.append(f"Avg({col['title']})")
        header_csv.append(f"Stdev({col['title']})")
    for comp in comparisons:
        header_csv.append(
            f"Avg({comp.get('title', '')})"
        )
        header_csv.append(
            f"Stdev({comp.get('title', '')})"
        )
    for rca in rcas:
        if rca:
            header_csv.append(rca["title"])

    legend_lst = table.get("legend", None)
    if legend_lst is None:
        legend = ""
    else:
        legend = "\n" + "\n".join(legend_lst) + "\n"

    footnote = ""
    if rcas and any(rcas):
        footnote += "\nRoot Cause Analysis:\n"
        for rca in rcas:
            if rca:
                footnote += f"{rca['data'].get('footnote', '')}\n"

    csv_file_name = f"{table['output-file']}-csv.csv"
    with open(csv_file_name, "wt", encoding='utf-8') as file_handler:
        file_handler.write(
            ",".join([f'"{itm}"' for itm in header_csv]) + "\n"
        )
        for test in tbl_for_csv:
            file_handler.write(
                ",".join([f'"{item}"' for item in test]) + "\n"
            )
        if legend_lst:
            for item in legend_lst:
                file_handler.write(f'"{item}"\n')
        if footnote:
            for itm in footnote.split("\n"):
                file_handler.write(f'"{itm}"\n')

    tbl_tmp = list()
    max_lens = [0, ] * len(tbl_cmp_lst[0])
    for line in tbl_cmp_lst:
        row = [line[0], ]
        for idx, itm in enumerate(line[1:]):
            if itm is None or not isinstance(itm, dict) or \
                    itm.get('mean', None) is None or \
                    itm.get('stdev', None) is None:
                new_itm = "NT"
            else:
                if idx < len(cols):
                    new_itm = (
                        f"{round(float(itm['mean']) / 1e6, 2)} "
                        f"\u00B1{round(float(itm['stdev']) / 1e6, 2)}".
                        replace("nan", "NaN")
                    )
                else:
                    new_itm = (
                        f"{round(float(itm['mean']) / 1e6, 2):+} "
                        f"\u00B1{round(float(itm['stdev']) / 1e6, 2)}".
                        replace("nan", "NaN")
                    )
            if len(new_itm.rsplit(" ", 1)[-1]) > max_lens[idx]:
                max_lens[idx] = len(new_itm.rsplit(" ", 1)[-1])
            row.append(new_itm)

        tbl_tmp.append(row)

    header = ["Test Case", ]
    header.extend([col["title"] for col in cols])
    header.extend([comp.get("title", "") for comp in comparisons])

    tbl_final = list()
    for line in tbl_tmp:
        row = [line[0], ]
        for idx, itm in enumerate(line[1:]):
            if itm in ("NT", "NaN"):
                row.append(itm)
                continue
            itm_lst = itm.rsplit("\u00B1", 1)
            itm_lst[-1] = \
                f"{' ' * (max_lens[idx] - len(itm_lst[-1]))}{itm_lst[-1]}"
            itm_str = "\u00B1".join(itm_lst)

            if idx >= len(cols):
                # Diffs
                rca = rcas[idx - len(cols)]
                if rca:
                    # Add rcas to diffs
                    rca_nr = rca["data"].get(row[0], None)
                    if rca_nr:
                        hdr_len = len(header[idx + 1]) - 1
                        if hdr_len < 19:
                            hdr_len = 19
                        rca_nr = f"[{rca_nr}]"
                        itm_str = (
                            f"{' ' * (4 - len(rca_nr))}{rca_nr}"
                            f"{' ' * (hdr_len - 4 - len(itm_str))}"
                            f"{itm_str}"
                        )
            row.append(itm_str)
        tbl_final.append(row)

    # Generate csv tables:
    csv_file_name = f"{table['output-file']}.csv"
    logging.info(f"    Writing the file {csv_file_name}")
    with open(csv_file_name, "wt", encoding='utf-8') as file_handler:
        file_handler.write(";".join(header) + "\n")
        for test in tbl_final:
            file_handler.write(";".join([str(item) for item in test]) + "\n")

    # Generate txt table:
    txt_file_name = f"{table['output-file']}.txt"
    logging.info(f"    Writing the file {txt_file_name}")
    convert_csv_to_pretty_txt(csv_file_name, txt_file_name, delimiter=";")

    with open(txt_file_name, 'a', encoding='utf-8') as file_handler:
        file_handler.write(legend)
        file_handler.write(footnote)

    # Generate html table:
    _tpc_generate_html_table(
        header,
        tbl_final,
        table['output-file'],
        legend=legend,
        footnote=footnote,
        sort_data=False,
        title=table.get("title", "")
    )


def table_weekly_comparison(table, in_data):
    """Generate the table(s) with algorithm: table_weekly_comparison
    specified in the specification file.

    :param table: Table to generate.
    :param in_data: Data to process.
    :type table: pandas.Series
    :type in_data: InputData
    """
    logging.info(f"  Generating the table {table.get(u'title', u'')} ...")

    # Transform the data
    logging.info(
        f"    Creating the data set for the {table.get(u'type', u'')} "
        f"{table.get(u'title', u'')}."
    )

    incl_tests = table.get(u"include-tests", None)
    if incl_tests not in (u"NDR", u"PDR"):
        logging.error(f"Wrong tests to include specified ({incl_tests}).")
        return

    nr_cols = table.get(u"nr-of-data-columns", None)
    if not nr_cols or nr_cols < 2:
        logging.error(
            f"No columns specified for {table.get(u'title', u'')}. Skipping."
        )
        return

    data = in_data.filter_data(
        table,
        params=[u"throughput", u"result", u"name", u"parent", u"tags"],
        continue_on_error=True
    )

    header = [
        [u"VPP Version", ],
        [u"Start Timestamp", ],
        [u"CSIT Build", ],
        [u"CSIT Testbed", ]
    ]
    tbl_dict = dict()
    idx = 0
    tb_tbl = table.get(u"testbeds", None)
    for job_name, job_data in data.items():
        for build_nr, build in job_data.items():
            if idx >= nr_cols:
                break
            if build.empty:
                continue

            tb_ip = in_data.metadata(job_name, build_nr).get(u"testbed", u"")
            if tb_ip and tb_tbl:
                testbed = tb_tbl.get(tb_ip, u"")
            else:
                testbed = u""
            header[2].insert(1, build_nr)
            header[3].insert(1, testbed)
            header[1].insert(
                1, in_data.metadata(job_name, build_nr).get(u"generated", u"")
            )
            logging.info(
                in_data.metadata(job_name, build_nr).get(u"version", u"ERROR"))
            header[0].insert(
                1, in_data.metadata(job_name, build_nr).get("version", build_nr)
            )

            for tst_name, tst_data in build.items():
                tst_name_mod = \
                    _tpc_modify_test_name(tst_name).replace(u"2n1l-", u"")
                if not tbl_dict.get(tst_name_mod, None):
                    tbl_dict[tst_name_mod] = dict(
                        name=tst_data[u'name'].rsplit(u'-', 1)[0],
                    )
                try:
                    tbl_dict[tst_name_mod][-idx - 1] = \
                        tst_data[u"throughput"][incl_tests][u"LOWER"]
                except (TypeError, IndexError, KeyError, ValueError):
                    pass
            idx += 1

    if idx < nr_cols:
        logging.error(u"Not enough data to build the table! Skipping")
        return

    cmp_dict = dict()
    for idx, cmp in enumerate(table.get(u"comparisons", list())):
        idx_ref = cmp.get(u"reference", None)
        idx_cmp = cmp.get(u"compare", None)
        if idx_ref is None or idx_cmp is None:
            continue
        header[0].append(
            f"Diff({header[0][idx_ref - idx].split(u'~')[-1]} vs "
            f"{header[0][idx_cmp - idx].split(u'~')[-1]})"
        )
        header[1].append(u"")
        header[2].append(u"")
        header[3].append(u"")
        for tst_name, tst_data in tbl_dict.items():
            if not cmp_dict.get(tst_name, None):
                cmp_dict[tst_name] = list()
            ref_data = tst_data.get(idx_ref, None)
            cmp_data = tst_data.get(idx_cmp, None)
            if ref_data is None or cmp_data is None:
                cmp_dict[tst_name].append(float(u'nan'))
            else:
                cmp_dict[tst_name].append(relative_change(ref_data, cmp_data))

    tbl_lst_none = list()
    tbl_lst = list()
    for tst_name, tst_data in tbl_dict.items():
        itm_lst = [tst_data[u"name"], ]
        for idx in range(nr_cols):
            item = tst_data.get(-idx - 1, None)
            if item is None:
                itm_lst.insert(1, None)
            else:
                itm_lst.insert(1, round(item / 1e6, 1))
        itm_lst.extend(
            [
                None if itm is None else round(itm, 1)
                for itm in cmp_dict[tst_name]
            ]
        )
        if str(itm_lst[-1]) == u"nan" or itm_lst[-1] is None:
            tbl_lst_none.append(itm_lst)
        else:
            tbl_lst.append(itm_lst)

    tbl_lst_none.sort(key=lambda rel: rel[0], reverse=False)
    tbl_lst.sort(key=lambda rel: rel[0], reverse=False)
    tbl_lst.sort(key=lambda rel: rel[-1], reverse=False)
    tbl_lst.extend(tbl_lst_none)

    # Generate csv table:
    csv_file_name = f"{table[u'output-file']}.csv"
    logging.info(f"    Writing the file {csv_file_name}")
    with open(csv_file_name, u"wt", encoding='utf-8') as file_handler:
        for hdr in header:
            file_handler.write(u",".join(hdr) + u"\n")
        for test in tbl_lst:
            file_handler.write(u",".join(
                [
                    str(item).replace(u"None", u"-").replace(u"nan", u"-").
                    replace(u"null", u"-") for item in test
                ]
            ) + u"\n")

    txt_file_name = f"{table[u'output-file']}.txt"
    logging.info(f"    Writing the file {txt_file_name}")
    try:
        convert_csv_to_pretty_txt(csv_file_name, txt_file_name, delimiter=u",")
    except Exception as err:
        logging.error(repr(err))
        for hdr in header:
            logging.info(",".join(hdr))
        for test in tbl_lst:
            logging.info(",".join(
                [
                    str(item).replace(u"None", u"-").replace(u"nan", u"-").
                    replace(u"null", u"-") for item in test
                ]
            ))

    # Reorganize header in txt table
    txt_table = list()
    try:
        with open(txt_file_name, u"rt", encoding='utf-8') as file_handler:
            for line in list(file_handler):
                txt_table.append(line)
        txt_table.insert(5, txt_table.pop(2))
        with open(txt_file_name, u"wt", encoding='utf-8') as file_handler:
            file_handler.writelines(txt_table)
    except FileNotFoundError as err:
        logging.error(repr(err))
    except IndexError:
        pass

    # Generate html table:
    hdr_html = [
        u"<br>".join(row) for row in zip(*header)
    ]
    _tpc_generate_html_table(
        hdr_html,
        tbl_lst,
        table[u'output-file'],
        sort_data=True,
        title=table.get(u"title", u""),
        generate_rst=False
    )
