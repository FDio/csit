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

"""Algorithms to generate plots.
"""


import logging
import pandas as pd
import plotly.offline as ploff
import plotly.graph_objs as plgo

from plotly.exceptions import PlotlyError
from math import log10, floor
from collections import OrderedDict

from utils import mean


COLORS = ["SkyBlue", "Olive", "Purple", "Coral", "Indigo", "Pink",
          "Chocolate", "Brown", "Magenta", "Cyan", "Orange", "Black",
          "Violet", "Blue", "Yellow", "BurlyWood", "CadetBlue", "Crimson",
          "DarkBlue", "DarkCyan", "DarkGreen", "Green", "GoldenRod",
          "LightGreen", "LightSeaGreen", "LightSkyBlue", "Maroon",
          "MediumSeaGreen", "SeaGreen", "LightSlateGrey"]


def generate_plots(spec, data):
    """Generate all plots specified in the specification file.

    :param spec: Specification read from the specification file.
    :param data: Data to process.
    :type spec: Specification
    :type data: InputData
    """

    logging.info("Generating the plots ...")
    for index, plot in enumerate(spec.plots):
        try:
            logging.info("  Plot nr {0}:".format(index + 1))
            plot["limits"] = spec.configuration["limits"]
            eval(plot["algorithm"])(plot, data)
        except NameError as err:
            logging.error("Probably algorithm '{alg}' is not defined: {err}".
                          format(alg=plot["algorithm"], err=repr(err)))
    logging.info("Done.")


def plot_performance_box(plot, input_data):
    """Generate the plot(s) with algorithm: plot_performance_box
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the plot {0} ...".
                 format(plot.get("title", "")))

    # Transform the data
    plot_title = plot.get("title", "")
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(plot.get("type", ""), plot_title))
    data = input_data.filter_data(plot)
    if data is None:
        logging.error("No data.")
        return

    # Prepare the data for the plot
    y_vals = dict()
    y_tags = dict()
    for job in data:
        for build in job:
            for test in build:
                if y_vals.get(test["parent"], None) is None:
                    y_vals[test["parent"]] = list()
                    y_tags[test["parent"]] = test.get("tags", None)
                try:
                    if test["type"] in ("NDRPDR", ):
                        if "-pdr" in plot_title.lower():
                            y_vals[test["parent"]].\
                                append(test["throughput"]["PDR"]["LOWER"])
                        elif "-ndr" in plot_title.lower():
                            y_vals[test["parent"]]. \
                                append(test["throughput"]["NDR"]["LOWER"])
                        else:
                            continue
                    else:
                        continue
                except (KeyError, TypeError):
                    y_vals[test["parent"]].append(None)

    # Sort the tests
    order = plot.get("sort", None)
    if order and y_tags:
        y_sorted = OrderedDict()
        for tag in order:
            for suite, tags in y_tags.items():
                if tag in tags:
                    y_sorted[suite] = y_vals.pop(suite)
                    y_tags.pop(suite)
        # The rest comes unsorted at the end
        for suite in y_tags.keys():
            y_sorted[suite] = y_vals[suite]
    else:
        y_sorted = y_vals

    # Add None to the lists with missing data
    max_len = 0
    for val in y_sorted.values():
        if len(val) > max_len:
            max_len = len(val)
    for key, val in y_sorted.items():
        if len(val) < max_len:
            val.extend([None for _ in range(max_len - len(val))])

    # Add plot traces
    traces = list()
    df = pd.DataFrame(y_sorted)
    df.head()
    y_max = list()
    for i, col in enumerate(df.columns):
        name = "{0}. {1}".format(i + 1, col.lower().replace('-ndrpdrdisc', '').
                                 replace('-ndrpdr', ''))
        traces.append(plgo.Box(x=[str(i + 1) + '.'] * len(df[col]),
                               y=[y / 1000000 for y in df[col]],
                               name=name,
                               **plot["traces"]))
        val_max = max(df[col])
        y_max.append(int(val_max / 1000000) + 1)

    try:
        # Create plot
        if plot["layout"].get("title", None):
            plot["layout"]["title"] = "<b>Packet Throughput:</b>{0}". \
                format(plot["layout"]["title"])
        plot["layout"]["yaxis"]["range"] = [0, max(y_max)]
        plpl = plgo.Figure(data=traces, layout=plot["layout"])

        # Export Plot
        logging.info("    Writing file '{0}{1}'.".
                     format(plot["output-file"], plot["output-file-type"]))
        ploff.plot(plpl,
                   show_link=False, auto_open=False,
                   filename='{0}{1}'.format(plot["output-file"],
                                            plot["output-file-type"]))
    except PlotlyError as err:
        logging.error("   Finished with error: {}".
                      format(str(err).replace("\n", " ")))
        return

    logging.info("  Done.")


def plot_error_bars_latency(plot, input_data):
    """Generate the plot(s) with algorithm: plot_latency_box
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the plot {0} ...".
                 format(plot.get("title", "")))

    # Transform the data
    plot_title = plot.get("title", "")
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(plot.get("type", ""), plot_title))
    data = input_data.filter_data(plot)
    if data is None:
        logging.error("No data.")
        return

    # Prepare the data for the plot
    y_tmp_vals = dict()
    y_tags = dict()
    for job in data:
        for build in job:
            for test in build:
                if y_tmp_vals.get(test["parent"], None) is None:
                    y_tmp_vals[test["parent"]] = [
                        list(),  # direction1, min
                        list(),  # direction1, avg
                        list(),  # direction1, max
                        list(),  # direction2, min
                        list(),  # direction2, avg
                        list()   # direction2, max
                    ]
                    y_tags[test["parent"]] = test["tags"]
                try:
                    if test["type"] in ("NDRPDR", ):
                        if "-pdr" in plot_title.lower():
                            ttype = "PDR"
                        elif "-ndr" in plot_title.lower():
                            ttype = "NDR"
                        else:
                            continue
                        y_tmp_vals[test["parent"]][0].append(
                            test["latency"][ttype]["direction1"]["min"])
                        y_tmp_vals[test["parent"]][1].append(
                            test["latency"][ttype]["direction1"]["avg"])
                        y_tmp_vals[test["parent"]][2].append(
                            test["latency"][ttype]["direction1"]["max"])
                        y_tmp_vals[test["parent"]][3].append(
                            test["latency"][ttype]["direction2"]["min"])
                        y_tmp_vals[test["parent"]][4].append(
                            test["latency"][ttype]["direction2"]["avg"])
                        y_tmp_vals[test["parent"]][5].append(
                            test["latency"][ttype]["direction2"]["max"])
                    else:
                        continue
                except (KeyError, TypeError):
                    pass

    logging.info("y_tmp_vals: {0}\n".format(y_tmp_vals))

    # Sort the tests
    order = plot.get("sort", None)
    if order and y_tags:
        y_sorted = OrderedDict()
        for tag in order:
            for suite, tags in y_tags.items():
                if tag in tags:
                    y_sorted[suite] = y_tmp_vals.pop(suite)
                    y_tags.pop(suite)
        # The rest comes unsorted at the end
        for suite in y_tags.keys():
            y_sorted[suite] = y_tmp_vals[suite]
    else:
        y_sorted = y_tmp_vals

    logging.info("y_sorted: {0}\n".format(y_sorted))

    x_vals = list()
    y_vals = list()
    y_mins = list()
    y_maxs = list()
    for key, val in y_sorted.items():
        key = "-".join(key.split("-")[1:-1])
        x_vals.append(key)  # dir 1
        y_vals.append(mean(val[1]))
        y_mins.append(mean(val[0]))
        y_maxs.append(mean(val[2]))
        x_vals.append(key)  # dir 2
        y_vals.append(mean(val[4]))
        y_mins.append(mean(val[3]))
        y_maxs.append(mean(val[5]))

    logging.info("x_vals: {0}\n".format(x_vals))
    logging.info("y_vals: {0}\n".format(y_vals))
    logging.info("y_mins: {0}\n".format(y_mins))
    logging.info("y_maxs: {0}\n".format(y_maxs))

    traces = list()

    for idx in range(len(x_vals)):
        if not bool(int(idx % 2)):
            direction = "TGint1-SUT1-SUT2-TGint2"
        else:
            direction = "TGint2-SUT2-SUT1-TGint1"
        hovertext = ("Test: {test}<br>"
                     "Direction: {dir}<br>"
                     "Max: {max}uSec<br>"
                     "Avg: {avg}uSec<br>"
                     "Min: {min}uSec".format(test=x_vals[idx],
                                             dir=direction,
                                             max=y_maxs[idx],
                                             avg=y_vals[idx],
                                             min=y_mins[idx]))
        traces.append(plgo.Scatter(
            x=[idx, ],
            y=[y_vals[idx], ],
            name=x_vals[idx],
            legendgroup=x_vals[idx],
            showlegend=bool(int(idx % 2)),
            mode="markers",
            error_y=dict(
                type='data',
                symmetric=False,
                array=[y_maxs[idx] - y_vals[idx], ],
                arrayminus=[y_vals[idx] - y_mins[idx], ],
                color=COLORS[int(idx / 2)]
            ),
            marker = dict(
                size=10,
                color=COLORS[int(idx / 2)],
            ),
            text=hovertext,
            hoverinfo="text",
        ))

    try:
        # Create plot
        logging.info("    Writing file '{0}{1}'.".
                     format(plot["output-file"], plot["output-file-type"]))
        layout = plot["layout"]
        if layout.get("title", None):
            layout["title"] = "<b>Packet Latency:</b> {0}".\
                format(layout["title"])
        # layout["yaxis"]["range"] = [0, max(y_max)]
        plpl = plgo.Figure(data=traces, layout=layout)

        # Export Plot
        ploff.plot(plpl,
                   show_link=False, auto_open=False,
                   filename='{0}{1}'.format(plot["output-file"],
                                            plot["output-file-type"]))
    except PlotlyError as err:
        logging.error("   Finished with error: {}".
                      format(str(err).replace("\n", " ")))
        return

    logging.info("  Done.")


def plot_latency_box(plot, input_data):
    """Generate the plot(s) with algorithm: plot_latency_box
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the plot {0} ...".
                 format(plot.get("title", "")))

    # Transform the data
    plot_title = plot.get("title", "")
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(plot.get("type", ""), plot_title))
    data = input_data.filter_data(plot)
    if data is None:
        logging.error("No data.")
        return

    # Prepare the data for the plot
    y_tmp_vals = dict()
    y_tags = dict()
    for job in data:
        for build in job:
            for test in build:
                if y_tmp_vals.get(test["parent"], None) is None:
                    y_tmp_vals[test["parent"]] = [
                        list(),  # direction1, min
                        list(),  # direction1, avg
                        list(),  # direction1, max
                        list(),  # direction2, min
                        list(),  # direction2, avg
                        list()   # direction2, max
                    ]
                    y_tags[test["parent"]] = test["tags"]
                try:
                    if test["type"] in ("NDRPDR", ):
                        if "-pdr" in plot_title.lower():
                            ttype = "PDR"
                        elif "-ndr" in plot_title.lower():
                            ttype = "NDR"
                        else:
                            continue
                        y_tmp_vals[test["parent"]][0].append(
                            test["latency"][ttype]["direction1"]["min"])
                        y_tmp_vals[test["parent"]][1].append(
                            test["latency"][ttype]["direction1"]["avg"])
                        y_tmp_vals[test["parent"]][2].append(
                            test["latency"][ttype]["direction1"]["max"])
                        y_tmp_vals[test["parent"]][3].append(
                            test["latency"][ttype]["direction2"]["min"])
                        y_tmp_vals[test["parent"]][4].append(
                            test["latency"][ttype]["direction2"]["avg"])
                        y_tmp_vals[test["parent"]][5].append(
                            test["latency"][ttype]["direction2"]["max"])
                    else:
                        continue
                except (KeyError, TypeError):
                    pass

    logging.info("y_tmp_vals: {0}\n".format(y_tmp_vals))

    # Sort the tests
    order = plot.get("sort", None)
    if order and y_tags:
        y_sorted = OrderedDict()
        for tag in order:
            for suite, tags in y_tags.items():
                if tag in tags:
                    y_sorted[suite] = y_tmp_vals.pop(suite)
                    y_tags.pop(suite)
        # The rest comes unsorted at the end
        for suite in y_tags.keys():
            y_sorted[suite] = y_tmp_vals[suite]
    else:
        y_sorted = y_tmp_vals

    y_vals = OrderedDict()
    for key, values in y_sorted.items():
        y_vals[key] = list()
        for val in values:
            if val:
                average = mean(val)
            else:
                average = None
            y_vals[key].append(average)
            y_vals[key].append(average)  # Twice for plot.ly

    logging.info("y_vals: {0}\n".format(y_vals))

    try:
        df = pd.DataFrame(y_vals)
        df.head()
    except ValueError as err:
        logging.error("   Finished with error: {}".
                      format(str(err).replace("\n", " ")))
        return

    x_axis = ["TGint1-to-SUT1-to-SUT2-to-TGint2", ] * 6
    x_axis.extend(["TGint2-to-SUT2-to-SUT1-to-TGint1", ] * 6)

    # Add plot traces
    traces = list()
    for col in df.columns:
        name = "{0}".format(col.lower().replace('-ndrpdrdisc', '').
                            replace('-ndrpdr', ''))
        traces.append(plgo.Box(x=x_axis,
                               y=df[col],
                               name=name))
    try:
        # Create plot
        logging.info("    Writing file '{0}{1}'.".
                     format(plot["output-file"], plot["output-file-type"]))
        if plot["layout"].get("title", None):
            plot["layout"]["title"] = "<b>Packet Latency:</b> {0}". \
                format(plot["layout"]["title"])
        plpl = plgo.Figure(data=traces, layout=plot["layout"])

        # Export Plot
        ploff.plot(plpl,
                   show_link=False, auto_open=False,
                   filename='{0}{1}'.format(plot["output-file"],
                                            plot["output-file-type"]))
    except PlotlyError as err:
        logging.error("   Finished with error: {}".
                      format(str(err).replace("\n", " ")))
        return

    logging.info("  Done.")


def plot_throughput_speedup_analysis(plot, input_data):
    """Generate the plot(s) with algorithm: plot_throughput_speedup_analysis
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the plot {0} ...".
                 format(plot.get("title", "")))

    # Transform the data
    plot_title = plot.get("title", "")
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(plot.get("type", ""), plot_title))
    data = input_data.filter_data(plot)
    if data is None:
        logging.error("No data.")
        return

    throughput = dict()
    for job in data:
        for build in job:
            for test in build:
                if throughput.get(test["parent"], None) is None:
                    throughput[test["parent"]] = {"1": list(),
                                                  "2": list(),
                                                  "4": list()}
                try:
                    if test["type"] in ("NDRPDR", ):
                        if "-pdr" in plot_title.lower():
                            ttype = "PDR"
                        elif "-ndr" in plot_title.lower():
                            ttype = "NDR"
                        else:
                            continue
                        if "1C" in test["tags"]:
                            throughput[test["parent"]]["1"].\
                                append(test["throughput"][ttype]["LOWER"])
                        elif "2C" in test["tags"]:
                            throughput[test["parent"]]["2"]. \
                                append(test["throughput"][ttype]["LOWER"])
                        elif "4C" in test["tags"]:
                            throughput[test["parent"]]["4"]. \
                                append(test["throughput"][ttype]["LOWER"])
                except (KeyError, TypeError):
                    pass

    if not throughput:
        logging.warning("No data for the plot '{}'".
                        format(plot.get("title", "")))
        return

    for test_name, test_vals in throughput.items():
        for key, test_val in test_vals.items():
            if test_val:
                throughput[test_name][key] = sum(test_val) / len(test_val)

    names = ['1 core', '2 cores', '4 cores']
    x_vals = list()
    y_vals_1 = list()
    y_vals_2 = list()
    y_vals_4 = list()

    for test_name, test_vals in throughput.items():
        if test_vals["1"]:
            x_vals.append("-".join(test_name.split('-')[1:-1]))
            y_vals_1.append(1)
            if test_vals["2"]:
                y_vals_2.append(
                    round(float(test_vals["2"]) / float(test_vals["1"]), 2))
            else:
                y_vals_2.append(None)
            if test_vals["4"]:
                y_vals_4.append(
                    round(float(test_vals["4"]) / float(test_vals["1"]), 2))
            else:
                y_vals_4.append(None)

    y_vals = [y_vals_1, y_vals_2, y_vals_4]

    y_vals_zipped = zip(names, y_vals)
    traces = list()
    for val in y_vals_zipped:
        traces.append(plgo.Bar(x=x_vals,
                               y=val[1],
                               name=val[0]))

    try:
        # Create plot
        logging.info("    Writing file '{0}{1}'.".
                     format(plot["output-file"], plot["output-file-type"]))
        plpl = plgo.Figure(data=traces, layout=plot["layout"])

        # Export Plot
        ploff.plot(plpl,
                   show_link=False, auto_open=False,
                   filename='{0}{1}'.format(plot["output-file"],
                                            plot["output-file-type"]))
    except PlotlyError as err:
        logging.error("   Finished with error: {}".
                      format(str(err).replace("\n", " ")))
        return

    logging.info("  Done.")


def plot_line_throughput_speedup_analysis(plot, input_data):
    """Generate the plot(s) with algorithm:
    plot_line_throughput_speedup_analysis
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the plot {0} ...".
                 format(plot.get("title", "")))

    # Transform the data
    plot_title = plot.get("title", "")
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(plot.get("type", ""), plot_title))
    data = input_data.filter_data(plot)
    if data is None:
        logging.error("No data.")
        return

    y_vals = dict()
    y_tags = dict()
    for job in data:
        for build in job:
            for test in build:
                if y_vals.get(test["parent"], None) is None:
                    y_vals[test["parent"]] = {"1": list(),
                                              "2": list(),
                                              "4": list()}
                    y_tags[test["parent"]] = test.get("tags", None)
                try:
                    if test["type"] in ("NDRPDR", ):
                        if "-pdr" in plot_title.lower():
                            ttype = "PDR"
                        elif "-ndr" in plot_title.lower():
                            ttype = "NDR"
                        else:
                            continue
                        if "1C" in test["tags"]:
                            y_vals[test["parent"]]["1"].\
                                append(test["throughput"][ttype]["LOWER"])
                        elif "2C" in test["tags"]:
                            y_vals[test["parent"]]["2"]. \
                                append(test["throughput"][ttype]["LOWER"])
                        elif "4C" in test["tags"]:
                            y_vals[test["parent"]]["4"]. \
                                append(test["throughput"][ttype]["LOWER"])
                except (KeyError, TypeError):
                    pass

    if not y_vals:
        logging.warning("No data for the plot '{}'".
                        format(plot.get("title", "")))
        return

    y_1c_max = dict()
    for test_name, test_vals in y_vals.items():
        for key, test_val in test_vals.items():
            if test_val:
                y_vals[test_name][key] = sum(test_val) / len(test_val)
                if key == "1":
                    y_1c_max[test_name] = max(test_val) / 1000000.0

    vals = dict()
    y_max = list()
    nic_limit = 0
    link_limit = 0
    pci_limit = plot["limits"]["pci"]["pci-g3-x8"]
    for test_name, test_vals in y_vals.items():
        if test_vals["1"]:
            name = "-".join(test_name.split('-')[1:-1])

            vals[name] = dict()
            y_val_1 = test_vals["1"] / 1000000.0
            y_val_2 = test_vals["2"] / 1000000.0 if test_vals["2"] else None
            y_val_4 = test_vals["4"] / 1000000.0 if test_vals["4"] else None

            vals[name]["val"] = [y_val_1, y_val_2, y_val_4]
            vals[name]["rel"] = [1.0, None, None]
            vals[name]["ideal"] = [y_1c_max[test_name],
                                   y_1c_max[test_name] * 2,
                                   y_1c_max[test_name] * 4]
            vals[name]["diff"] = [0.0,  None, None]

            val_max = max(max(vals[name]["val"], vals[name]["ideal"]))
            y_max.append(10**floor(log10(val_max)) * (int(val_max/10) + 1))

            if y_val_2:
                vals[name]["rel"][1] = round(y_val_2 / y_val_1, 2)
                vals[name]["diff"][1] = \
                    (y_val_2 - vals[name]["ideal"][1]) * 100 / y_val_2
            if y_val_4:
                vals[name]["rel"][2] = round(y_val_4 / y_val_1, 2)
                vals[name]["diff"][2] = \
                    (y_val_4 - vals[name]["ideal"][2]) * 100 / y_val_4

        # Limits:
        if "x520" in test_name:
            limit = plot["limits"]["nic"]["x520"]
        elif "x710" in test_name:
            limit = plot["limits"]["nic"]["x710"]
        elif "xxv710" in test_name:
            limit = plot["limits"]["nic"]["xxv710"]
        elif "xl710" in test_name:
            limit = plot["limits"]["nic"]["xl710"]
        else:
            limit = 0
        if limit > nic_limit:
            nic_limit = limit

        mul = 2 if "ge2p" in test_name else 1
        if "10ge" in test_name:
            limit = plot["limits"]["link"]["10ge"] * mul
        elif "25ge" in test_name:
            limit = plot["limits"]["link"]["25ge"] * mul
        elif "40ge" in test_name:
            limit = plot["limits"]["link"]["40ge"] * mul
        elif "100ge" in test_name:
            limit = plot["limits"]["link"]["100ge"] * mul
        else:
            limit = 0
        if limit > link_limit:
            link_limit = limit

    # Sort the tests
    order = plot.get("sort", None)
    if order and y_tags:
        y_sorted = OrderedDict()
        for tag in order:
            for test, tags in y_tags.items():
                if tag in tags:
                    name = "-".join(test.split('-')[1:-1])
                    y_sorted[name] = vals.pop(name)
                    y_tags.pop(test)
        # The rest comes unsorted at the end
        for test in vals.keys():
            y_sorted[test] = vals[test]
    else:
        y_sorted = vals

    traces = list()
    x_vals = [1, 2, 4]

    # Limits:
    nic_limit /= 1000000.0
    link_limit /= 1000000.0
    pci_limit /= 1000000.0

    y_max.append(10 ** floor(log10(nic_limit)) * (int(nic_limit / 10) + 1))
    y_max.append(10 ** floor(log10(link_limit)) * (int(link_limit / 10) + 1))
    y_max.append(10 ** floor(log10(pci_limit)) * (int(pci_limit / 10) + 1))

    traces.append(plgo.Scatter(x=x_vals,
                               y=[nic_limit, ] * len(x_vals),
                               showlegend=False,
                               mode="lines",
                               line=dict(
                                   color="Grey",
                                   width=2),
                               text="NIC Limit: {0:.2f}Mpps".format(nic_limit),
                               hoverinfo="text"
                               ))
    traces.append(plgo.Scatter(x=x_vals,
                               y=[link_limit, ] * len(x_vals),
                               showlegend=False,
                               mode="lines",
                               line=dict(
                                   color="Grey",
                                   width=2),
                               text="Link Limit: {0:.2f}Mpps".
                               format(link_limit),
                               hoverinfo="text"
                               ))
    traces.append(plgo.Scatter(x=x_vals,
                               y=[pci_limit, ] * len(x_vals),
                               showlegend=False,
                               mode="lines",
                               line=dict(
                                   color="Grey",
                                   width=2),
                               text="PCIe Limit: {0:.2f}Mpps".format(pci_limit),
                               hoverinfo="text"
                               ))
    # Perfect and measured:
    cidx = 0
    for name, val in y_sorted.iteritems():
        hovertext=list()
        for idx in range(len(val["val"])):
            hovertext.append("value: {0:.2f}Mpps<br>"
                             "diff: {1:.0f}%<br>"
                             "speedup: {2:.2f}".
                             format(val["val"][idx],
                                    round(val["diff"][idx]),
                                    val["rel"][idx]))
        traces.append(plgo.Scatter(x=x_vals,
                                   y=val["val"],
                                   name=name,
                                   legendgroup=name,
                                   mode="lines+markers",
                                   line=dict(
                                       color=COLORS[cidx],
                                       width=2),
                                   text=hovertext,
                                   hoverinfo="text+name"
                                   ))
        traces.append(plgo.Scatter(x=x_vals,
                                   y=val["ideal"],
                                   name="{0} perfect".format(name),
                                   legendgroup=name,
                                   showlegend=False,
                                   mode="lines+markers",
                                   line=dict(
                                       color=COLORS[cidx],
                                       width=2,
                                       dash="dash"),
                                   text=["perfect: {0:.2f}Mpps".format(y)
                                         for y in val["ideal"]],
                                   hoverinfo="text"
                                   ))
        cidx += 1

    try:
        # Create plot
        logging.info("    Writing file '{0}{1}'.".
                     format(plot["output-file"], plot["output-file-type"]))
        layout = plot["layout"]
        if layout.get("title", None):
            layout["title"] = "<b>Speedup Multi-core:</b> {0}".\
                format(layout["title"])
        layout["yaxis"]["range"] = [0, max(y_max)]
        plpl = plgo.Figure(data=traces, layout=layout)

        # Export Plot
        ploff.plot(plpl,
                   show_link=False, auto_open=False,
                   filename='{0}{1}'.format(plot["output-file"],
                                            plot["output-file-type"]))
    except PlotlyError as err:
        logging.error("   Finished with error: {}".
                      format(str(err).replace("\n", " ")))
        return

    logging.info("  Done.")


def plot_http_server_performance_box(plot, input_data):
    """Generate the plot(s) with algorithm: plot_http_server_performance_box
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the plot {0} ...".
                 format(plot.get("title", "")))

    # Transform the data
    logging.info("    Creating the data set for the {0} '{1}'.".
                 format(plot.get("type", ""), plot.get("title", "")))
    data = input_data.filter_data(plot)
    if data is None:
        logging.error("No data.")
        return

    # Prepare the data for the plot
    y_vals = dict()
    for job in data:
        for build in job:
            for test in build:
                if y_vals.get(test["name"], None) is None:
                    y_vals[test["name"]] = list()
                try:
                    y_vals[test["name"]].append(test["result"])
                except (KeyError, TypeError):
                    y_vals[test["name"]].append(None)

    # Add None to the lists with missing data
    max_len = 0
    for val in y_vals.values():
        if len(val) > max_len:
            max_len = len(val)
    for key, val in y_vals.items():
        if len(val) < max_len:
            val.extend([None for _ in range(max_len - len(val))])

    # Add plot traces
    traces = list()
    df = pd.DataFrame(y_vals)
    df.head()
    for i, col in enumerate(df.columns):
        name = "{0}. {1}".format(i + 1, col.lower().replace('-cps', '').
                                 replace('-rps', ''))
        traces.append(plgo.Box(x=[str(i + 1) + '.'] * len(df[col]),
                               y=df[col],
                               name=name,
                               **plot["traces"]))
    try:
        # Create plot
        plpl = plgo.Figure(data=traces, layout=plot["layout"])

        # Export Plot
        logging.info("    Writing file '{0}{1}'.".
                     format(plot["output-file"], plot["output-file-type"]))
        ploff.plot(plpl,
                   show_link=False, auto_open=False,
                   filename='{0}{1}'.format(plot["output-file"],
                                            plot["output-file-type"]))
    except PlotlyError as err:
        logging.error("   Finished with error: {}".
                      format(str(err).replace("\n", " ")))
        return

    logging.info("  Done.")
