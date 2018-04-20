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

"""Generation of Continuous Performance Trending and Analysis.
"""

import datetime
import logging
import csv
import prettytable
import plotly.offline as ploff
import plotly.graph_objs as plgo
import plotly.exceptions as plerr
import numpy as np
import pandas as pd

from collections import OrderedDict
from utils import split_outliers, archive_input_data, execute_command


# Command to build the html format of the report
HTML_BUILDER = 'sphinx-build -v -c conf_cpta -a ' \
               '-b html -E ' \
               '-t html ' \
               '-D version="Generated on {date}" ' \
               '{working_dir} ' \
               '{build_dir}/'

# .css file for the html format of the report
THEME_OVERRIDES = """/* override table width restrictions */
.wy-nav-content {
    max-width: 1200px !important;
}
"""

COLORS = ["SkyBlue", "Olive", "Purple", "Coral", "Indigo", "Pink",
          "Chocolate", "Brown", "Magenta", "Cyan", "Orange", "Black",
          "Violet", "Blue", "Yellow"]


def generate_cpta(spec, data):
    """Generate all formats and versions of the Continuous Performance Trending
    and Analysis.

    :param spec: Specification read from the specification file.
    :param data: Full data set.
    :type spec: Specification
    :type data: InputData
    """

    logging.info("Generating the Continuous Performance Trending and Analysis "
                 "...")

    ret_code = _generate_all_charts(spec, data)

    cmd = HTML_BUILDER.format(
        date=datetime.date.today().strftime('%d-%b-%Y'),
        working_dir=spec.environment["paths"]["DIR[WORKING,SRC]"],
        build_dir=spec.environment["paths"]["DIR[BUILD,HTML]"])
    execute_command(cmd)

    with open(spec.environment["paths"]["DIR[CSS_PATCH_FILE]"], "w") as \
            css_file:
        css_file.write(THEME_OVERRIDES)

    with open(spec.environment["paths"]["DIR[CSS_PATCH_FILE2]"], "w") as \
            css_file:
        css_file.write(THEME_OVERRIDES)

    archive_input_data(spec)

    logging.info("Done.")

    return ret_code


def _select_data(in_data, period, fill_missing=False, use_first=False):
    """Select the data from the full data set. The selection is done by picking
    the samples depending on the period: period = 1: All, period = 2: every
    second sample, period = 3: every third sample ...

    :param in_data: Full set of data.
    :param period: Sampling period.
    :param fill_missing: If the chosen sample is missing in the full set, its
    nearest neighbour is used.
    :param use_first: Use the first sample even though it is not chosen.
    :type in_data: OrderedDict
    :type period: int
    :type fill_missing: bool
    :type use_first: bool
    :returns: Reduced data.
    :rtype: OrderedDict
    """

    first_idx = min(in_data.keys())
    last_idx = max(in_data.keys())

    idx = last_idx
    data_dict = dict()
    if use_first:
        data_dict[first_idx] = in_data[first_idx]
    while idx >= first_idx:
        data = in_data.get(idx, None)
        if data is None:
            if fill_missing:
                threshold = int(round(idx - period / 2)) + 1 - period % 2
                idx_low = first_idx if threshold < first_idx else threshold
                threshold = int(round(idx + period / 2))
                idx_high = last_idx if threshold > last_idx else threshold

                flag_l = True
                flag_h = True
                idx_lst = list()
                inc = 1
                while flag_l or flag_h:
                    if idx + inc > idx_high:
                        flag_h = False
                    else:
                        idx_lst.append(idx + inc)
                    if idx - inc < idx_low:
                        flag_l = False
                    else:
                        idx_lst.append(idx - inc)
                    inc += 1

                for i in idx_lst:
                    if i in in_data.keys():
                        data_dict[i] = in_data[i]
                        break
        else:
            data_dict[idx] = data
        idx -= period

    return OrderedDict(sorted(data_dict.items(), key=lambda t: t[0]))


def _evaluate_results(in_data, trimmed_data, window=10):
    """Evaluates if the sample value is regress, normal or progress compared to
    previous data within the window.
    We use the intervals defined as:
    - regress: less than median - 3 * stdev
    - normal: between median - 3 * stdev and median + 3 * stdev
    - progress: more than median + 3 * stdev

    :param in_data: Full data set.
    :param trimmed_data: Full data set without the outliers.
    :param window: Window size used to calculate moving median and moving stdev.
    :type in_data: pandas.Series
    :type trimmed_data: pandas.Series
    :type window: int
    :returns: Evaluated results.
    :rtype: list
    """

    if len(in_data) > 2:
        win_size = in_data.size if in_data.size < window else window
        results = [0.66, ]
        median = in_data.rolling(window=win_size, min_periods=2).median()
        stdev_t = trimmed_data.rolling(window=win_size, min_periods=2).std()

        first = True
        for build_nr, value in in_data.iteritems():
            if first:
                first = False
                continue
            if np.isnan(trimmed_data[build_nr]) \
                    or np.isnan(median[build_nr]) \
                    or np.isnan(stdev_t[build_nr]) \
                    or np.isnan(value):
                results.append(0.0)
            elif value < (median[build_nr] - 3 * stdev_t[build_nr]):
                results.append(0.33)
            elif value > (median[build_nr] + 3 * stdev_t[build_nr]):
                results.append(1.0)
            else:
                results.append(0.66)
    else:
        results = [0.0, ]
        try:
            median = np.median(in_data)
            stdev = np.std(in_data)
            if in_data.values[-1] < (median - 3 * stdev):
                results.append(0.33)
            elif (median - 3 * stdev) <= in_data.values[-1] <= (
                    median + 3 * stdev):
                results.append(0.66)
            else:
                results.append(1.0)
        except TypeError:
            results.append(None)
    return results


def _generate_trending_traces(in_data, build_info, period, moving_win_size=10,
                              fill_missing=True, use_first=False,
                              show_moving_median=True, name="", color=""):
    """Generate the trending traces:
     - samples,
     - moving median (trending plot)
     - outliers, regress, progress

    :param in_data: Full data set.
    :param build_info: Information about the builds.
    :param period: Sampling period.
    :param moving_win_size: Window size.
    :param fill_missing: If the chosen sample is missing in the full set, its
    nearest neighbour is used.
    :param use_first: Use the first sample even though it is not chosen.
    :param show_moving_median: Show moving median (trending plot).
    :param name: Name of the plot
    :param color: Name of the color for the plot.
    :type in_data: OrderedDict
    :type build_info: dict
    :type period: int
    :type moving_win_size: int
    :type fill_missing: bool
    :type use_first: bool
    :type show_moving_median: bool
    :type name: str
    :type color: str
    :returns: Generated traces (list) and the evaluated result (float).
    :rtype: tuple(traces, result)
    """

    if period > 1:
        in_data = _select_data(in_data, period,
                               fill_missing=fill_missing,
                               use_first=use_first)

    data_x = [key for key in in_data.keys()]
    data_y = [val for val in in_data.values()]

    hover_text = list()
    for idx in data_x:
        hover_text.append("vpp-build: {0}".
                          format(build_info[str(idx)][1].split("~")[-1]))

    data_pd = pd.Series(data_y, index=data_x)

    t_data, outliers = split_outliers(data_pd, outlier_const=1.5,
                                      window=moving_win_size)
    results = _evaluate_results(data_pd, t_data, window=moving_win_size)

    anomalies = pd.Series()
    anomalies_res = list()
    for idx, item in enumerate(in_data.items()):
        item_pd = pd.Series([item[1], ], index=[item[0], ])
        if item[0] in outliers.keys():
            anomalies = anomalies.append(item_pd)
            anomalies_res.append(0.0)
        elif results[idx] in (0.33, 1.0):
            anomalies = anomalies.append(item_pd)
            anomalies_res.append(results[idx])
    anomalies_res.extend([0.0, 0.33, 0.66, 1.0])

    # Create traces
    color_scale = [[0.00, "grey"],
                   [0.25, "grey"],
                   [0.25, "red"],
                   [0.50, "red"],
                   [0.50, "white"],
                   [0.75, "white"],
                   [0.75, "green"],
                   [1.00, "green"]]

    trace_samples = plgo.Scatter(
        x=data_x,
        y=data_y,
        mode='markers',
        line={
            "width": 1
        },
        name="{name}-thput".format(name=name),
        marker={
            "size": 5,
            "color": color,
            "symbol": "circle",
        },
        text=hover_text,
        hoverinfo="x+y+text+name"
    )
    traces = [trace_samples, ]

    trace_anomalies = plgo.Scatter(
        x=anomalies.keys(),
        y=anomalies.values,
        mode='markers',
        hoverinfo="none",
        showlegend=True,
        legendgroup=name,
        name="{name}: outliers".format(name=name),
        marker={
            "size": 15,
            "symbol": "circle-open",
            "color": anomalies_res,
            "colorscale": color_scale,
            "showscale": True,
            "line": {
                "width": 2
            },
            "colorbar": {
                "y": 0.5,
                "len": 0.8,
                "title": "Circles Marking Data Classification",
                "titleside": 'right',
                "titlefont": {
                    "size": 14
                },
                "tickmode": 'array',
                "tickvals": [0.125, 0.375, 0.625, 0.875],
                "ticktext": ["Outlier", "Regression", "Normal", "Progression"],
                "ticks": "",
                "ticklen": 0,
                "tickangle": -90,
                "thickness": 10
            }
        }
    )
    traces.append(trace_anomalies)

    if show_moving_median:
        data_mean_y = pd.Series(data_y).rolling(
            window=moving_win_size, min_periods=2).median()
        trace_median = plgo.Scatter(
            x=data_x,
            y=data_mean_y,
            mode='lines',
            line={
                "shape": "spline",
                "width": 1,
                "color": color,
            },
            name='{name}-trend'.format(name=name)
        )
        traces.append(trace_median)

    return traces, results[-1]


def _generate_chart(traces, layout, file_name):
    """Generates the whole chart using pre-generated traces.

    :param traces: Traces for the chart.
    :param layout: Layout of the chart.
    :param file_name: File name for the generated chart.
    :type traces: list
    :type layout: dict
    :type file_name: str
    """

    # Create plot
    logging.info("    Writing the file '{0}' ...".format(file_name))
    plpl = plgo.Figure(data=traces, layout=layout)
    try:
        ploff.plot(plpl, show_link=False, auto_open=False, filename=file_name)
    except plerr.PlotlyEmptyDataError:
        logging.warning(" No data for the plot. Skipped.")


def _generate_all_charts(spec, input_data):
    """Generate all charts specified in the specification file.

    :param spec: Specification.
    :param input_data: Full data set.
    :type spec: Specification
    :type input_data: InputData
    """

    job_name = spec.cpta["data"].keys()[0]

    builds_lst = list()
    for build in spec.input["builds"][job_name]:
        status = build["status"]
        if status != "failed" and status != "not found":
            builds_lst.append(str(build["build"]))

    # Get "build ID": "date" dict:
    build_info = OrderedDict()
    for build in builds_lst:
        try:
            build_info[build] = (
                input_data.metadata(job_name, build)["generated"][:14],
                input_data.metadata(job_name, build)["version"]
            )
        except KeyError:
            build_info[build] = ("", "")
        logging.info("{}: {}, {}".format(build,
                                         build_info[build][0],
                                         build_info[build][1]))

    # Create the header:
    csv_table = list()
    header = "Build Number:," + ",".join(builds_lst) + '\n'
    csv_table.append(header)
    build_dates = [x[0] for x in build_info.values()]
    header = "Build Date:," + ",".join(build_dates) + '\n'
    csv_table.append(header)
    vpp_versions = [x[1] for x in build_info.values()]
    header = "VPP Version:," + ",".join(vpp_versions) + '\n'
    csv_table.append(header)

    results = list()
    for chart in spec.cpta["plots"]:
        logging.info("  Generating the chart '{0}' ...".
                     format(chart.get("title", "")))

        # Transform the data
        data = input_data.filter_data(chart, continue_on_error=True)
        if data is None:
            logging.error("No data.")
            return

        chart_data = dict()
        for job in data:
            for idx, build in job.items():
                for test_name, test in build.items():
                    if chart_data.get(test_name, None) is None:
                        chart_data[test_name] = OrderedDict()
                    try:
                        chart_data[test_name][int(idx)] = \
                            test["result"]["throughput"]
                    except (KeyError, TypeError):
                        pass

        # Add items to the csv table:
        for tst_name, tst_data in chart_data.items():
            tst_lst = list()
            for build in builds_lst:
                item = tst_data.get(int(build), '')
                tst_lst.append(str(item) if item else '')
            csv_table.append("{0},".format(tst_name) + ",".join(tst_lst) + '\n')

        for period in chart["periods"]:
            # Generate traces:
            traces = list()
            win_size = 14 if period == 1 else 5 if period < 20 else 3
            idx = 0
            for test_name, test_data in chart_data.items():
                if not test_data:
                    logging.warning("No data for the test '{0}'".
                                    format(test_name))
                    continue
                test_name = test_name.split('.')[-1]
                trace, result = _generate_trending_traces(
                    test_data,
                    build_info=build_info,
                    period=period,
                    moving_win_size=win_size,
                    fill_missing=True,
                    use_first=False,
                    name='-'.join(test_name.split('-')[3:-1]),
                    color=COLORS[idx])
                traces.extend(trace)
                results.append(result)
                idx += 1

            # Generate the chart:
            chart["layout"]["xaxis"]["title"] = \
                chart["layout"]["xaxis"]["title"].format(job=job_name)
            _generate_chart(traces,
                            chart["layout"],
                            file_name="{0}-{1}-{2}{3}".format(
                                spec.cpta["output-file"],
                                chart["output-file-name"],
                                period,
                                spec.cpta["output-file-type"]))

        logging.info("  Done.")

    # Write the tables:
    file_name = spec.cpta["output-file"] + "-trending"
    with open("{0}.csv".format(file_name), 'w') as file_handler:
        file_handler.writelines(csv_table)

    txt_table = None
    with open("{0}.csv".format(file_name), 'rb') as csv_file:
        csv_content = csv.reader(csv_file, delimiter=',', quotechar='"')
        line_nr = 0
        for row in csv_content:
            if txt_table is None:
                txt_table = prettytable.PrettyTable(row)
            else:
                if line_nr > 1:
                    for idx, item in enumerate(row):
                        try:
                            row[idx] = str(round(float(item) / 1000000, 2))
                        except ValueError:
                            pass
                try:
                    txt_table.add_row(row)
                except Exception as err:
                    logging.warning("Error occurred while generating TXT table:"
                                    "\n{0}".format(err))
            line_nr += 1
        txt_table.align["Build Number:"] = "l"
    with open("{0}.txt".format(file_name), "w") as txt_file:
        txt_file.write(str(txt_table))

    # Evaluate result:
    result = "PASS"
    for item in results:
        if item is None:
            result = "FAIL"
            break
        if item == 0.66 and result == "PASS":
            result = "PASS"
        elif item == 0.33 or item == 0.0:
            result = "FAIL"

    logging.info("Partial results: {0}".format(results))
    logging.info("Result: {0}".format(result))

    return result
