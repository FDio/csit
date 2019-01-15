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
from collections import OrderedDict
from copy import deepcopy

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
            logging.info("  Plot nr {0}: {1}".format(index + 1,
                                                     plot.get("title", "")))
            plot["limits"] = spec.configuration["limits"]
            eval(plot["algorithm"])(plot, data)
            logging.info("  Done.")
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
        y_tags_l = {s: [t.lower() for t in ts] for s, ts in y_tags.items()}
        for tag in order:
            logging.debug(tag)
            for suite, tags in y_tags_l.items():
                if "not " in tag:
                    tag = tag.split(" ")[-1]
                    if tag.lower() in tags:
                        continue
                else:
                    if tag.lower() not in tags:
                        continue
                try:
                    y_sorted[suite] = y_vals.pop(suite)
                    y_tags_l.pop(suite)
                    logging.debug(suite)
                except KeyError as err:
                    logging.error("Not found: {0}".format(repr(err)))
                finally:
                    break
    else:
        y_sorted = y_vals

    # Add None to the lists with missing data
    max_len = 0
    nr_of_samples = list()
    for val in y_sorted.values():
        if len(val) > max_len:
            max_len = len(val)
        nr_of_samples.append(len(val))
    for key, val in y_sorted.items():
        if len(val) < max_len:
            val.extend([None for _ in range(max_len - len(val))])

    # Add plot traces
    traces = list()
    df = pd.DataFrame(y_sorted)
    df.head()
    y_max = list()
    for i, col in enumerate(df.columns):
        name = "{nr}. ({samples:02d} run{plural}) {name}".\
            format(nr=(i + 1),
                   samples=nr_of_samples[i],
                   plural='s' if nr_of_samples[i] > 1 else '',
                   name=col.lower().replace('-ndrpdr', ''))
        if len(name) > 50:
            name_lst = name.split('-')
            name = ""
            split_name = True
            for segment in name_lst:
                if (len(name) + len(segment) + 1) > 50 and split_name:
                    name += "<br>    "
                    split_name = False
                name += segment + '-'
            name = name[:-1]

        logging.debug(name)
        traces.append(plgo.Box(x=[str(i + 1) + '.'] * len(df[col]),
                               y=[y / 1000000 if y else None for y in df[col]],
                               name=name,
                               **plot["traces"]))
        try:
            val_max = max(df[col])
        except ValueError as err:
            logging.error(repr(err))
            continue
        if val_max:
            y_max.append(int(val_max / 1000000) + 1)

    try:
        # Create plot
        layout = deepcopy(plot["layout"])
        if layout.get("title", None):
            layout["title"] = "<b>Packet Throughput:</b> {0}". \
                format(layout["title"])
        if y_max:
            layout["yaxis"]["range"] = [0, max(y_max)]
        plpl = plgo.Figure(data=traces, layout=layout)

        # Export Plot
        logging.info("    Writing file '{0}{1}'.".
                     format(plot["output-file"], plot["output-file-type"]))
        ploff.plot(plpl, show_link=False, auto_open=False,
                   filename='{0}{1}'.format(plot["output-file"],
                                            plot["output-file-type"]))
    except PlotlyError as err:
        logging.error("   Finished with error: {}".
                      format(repr(err).replace("\n", " ")))
        return


def plot_latency_error_bars(plot, input_data):
    """Generate the plot(s) with algorithm: plot_latency_error_bars
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

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
                try:
                    logging.debug("test['latency']: {0}\n".
                                 format(test["latency"]))
                except ValueError as err:
                    logging.warning(repr(err))
                if y_tmp_vals.get(test["parent"], None) is None:
                    y_tmp_vals[test["parent"]] = [
                        list(),  # direction1, min
                        list(),  # direction1, avg
                        list(),  # direction1, max
                        list(),  # direction2, min
                        list(),  # direction2, avg
                        list()   # direction2, max
                    ]
                    y_tags[test["parent"]] = test.get("tags", None)
                try:
                    if test["type"] in ("NDRPDR", ):
                        if "-pdr" in plot_title.lower():
                            ttype = "PDR"
                        elif "-ndr" in plot_title.lower():
                            ttype = "NDR"
                        else:
                            logging.warning("Invalid test type: {0}".
                                            format(test["type"]))
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
                        logging.warning("Invalid test type: {0}".
                                        format(test["type"]))
                        continue
                except (KeyError, TypeError) as err:
                    logging.warning(repr(err))
    logging.debug("y_tmp_vals: {0}\n".format(y_tmp_vals))

    # Sort the tests
    order = plot.get("sort", None)
    if order and y_tags:
        y_sorted = OrderedDict()
        y_tags_l = {s: [t.lower() for t in ts] for s, ts in y_tags.items()}
        for tag in order:
            logging.debug(tag)
            for suite, tags in y_tags_l.items():
                if "not " in tag:
                    tag = tag.split(" ")[-1]
                    if tag.lower() in tags:
                        continue
                else:
                    if tag.lower() not in tags:
                        continue
                try:
                    y_sorted[suite] = y_tmp_vals.pop(suite)
                    y_tags_l.pop(suite)
                    logging.debug(suite)
                except KeyError as err:
                    logging.error("Not found: {0}".format(repr(err)))
                finally:
                    break
    else:
        y_sorted = y_tmp_vals

    logging.debug("y_sorted: {0}\n".format(y_sorted))
    x_vals = list()
    y_vals = list()
    y_mins = list()
    y_maxs = list()
    nr_of_samples = list()
    for key, val in y_sorted.items():
        name = "-".join(key.split("-")[1:-1])
        if len(name) > 50:
            name_lst = name.split('-')
            name = ""
            split_name = True
            for segment in name_lst:
                if (len(name) + len(segment) + 1) > 50 and split_name:
                    name += "<br>"
                    split_name = False
                name += segment + '-'
            name = name[:-1]
        x_vals.append(name)  # dir 1
        y_vals.append(mean(val[1]) if val[1] else None)
        y_mins.append(mean(val[0]) if val[0] else None)
        y_maxs.append(mean(val[2]) if val[2] else None)
        nr_of_samples.append(len(val[1]) if val[1] else 0)
        x_vals.append(name)  # dir 2
        y_vals.append(mean(val[4]) if val[4] else None)
        y_mins.append(mean(val[3]) if val[3] else None)
        y_maxs.append(mean(val[5]) if val[5] else None)
        nr_of_samples.append(len(val[3]) if val[3] else 0)

    logging.debug("x_vals :{0}\n".format(x_vals))
    logging.debug("y_vals :{0}\n".format(y_vals))
    logging.debug("y_mins :{0}\n".format(y_mins))
    logging.debug("y_maxs :{0}\n".format(y_maxs))
    logging.debug("nr_of_samples :{0}\n".format(nr_of_samples))
    traces = list()
    annotations = list()

    for idx in range(len(x_vals)):
        if not bool(int(idx % 2)):
            direction = "West-East"
        else:
            direction = "East-West"
        hovertext = ("No. of Runs: {nr}<br>"
                     "Test: {test}<br>"
                     "Direction: {dir}<br>".format(test=x_vals[idx],
                                                   dir=direction,
                                                   nr=nr_of_samples[idx]))
        if isinstance(y_maxs[idx], float):
            hovertext += "Max: {max:.2f}uSec<br>".format(max=y_maxs[idx])
        if isinstance(y_vals[idx], float):
            hovertext += "Mean: {avg:.2f}uSec<br>".format(avg=y_vals[idx])
        if isinstance(y_mins[idx], float):
            hovertext += "Min: {min:.2f}uSec".format(min=y_mins[idx])

        if isinstance(y_maxs[idx], float) and isinstance(y_vals[idx], float):
            array = [y_maxs[idx] - y_vals[idx], ]
        else:
            array = [None, ]
        if isinstance(y_mins[idx], float) and isinstance(y_vals[idx], float):
            arrayminus = [y_vals[idx] - y_mins[idx], ]
        else:
            arrayminus = [None, ]
        logging.debug("y_vals[{1}] :{0}\n".format(y_vals[idx], idx))
        logging.debug("array :{0}\n".format(array))
        logging.debug("arrayminus :{0}\n".format(arrayminus))
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
                array=array,
                arrayminus=arrayminus,
                color=COLORS[int(idx / 2)]
            ),
            marker=dict(
                size=10,
                color=COLORS[int(idx / 2)],
            ),
            text=hovertext,
            hoverinfo="text",
        ))
        annotations.append(dict(
            x=idx,
            y=0,
            xref="x",
            yref="y",
            xanchor="center",
            yanchor="top",
            text="E-W" if bool(int(idx % 2)) else "W-E",
            font=dict(
                size=16,
            ),
            align="center",
            showarrow=False
        ))

    try:
        # Create plot
        logging.info("    Writing file '{0}{1}'.".
                     format(plot["output-file"], plot["output-file-type"]))
        layout = deepcopy(plot["layout"])
        if layout.get("title", None):
            layout["title"] = "<b>Packet Latency:</b> {0}".\
                format(layout["title"])
        layout["annotations"] = annotations
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


def plot_throughput_speedup_analysis(plot, input_data):
    """Generate the plot(s) with algorithm:
    plot_throughput_speedup_analysis
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

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
                    if test["type"] in ("NDRPDR",):
                        if "-pdr" in plot_title.lower():
                            ttype = "PDR"
                        elif "-ndr" in plot_title.lower():
                            ttype = "NDR"
                        else:
                            continue
                        if "1C" in test["tags"]:
                            y_vals[test["parent"]]["1"]. \
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
                avg_val = sum(test_val) / len(test_val)
                y_vals[test_name][key] = (avg_val, len(test_val))
                ideal = avg_val / (int(key) * 1000000.0)
                if test_name not in y_1c_max or ideal > y_1c_max[test_name]:
                    y_1c_max[test_name] = ideal

    vals = dict()
    y_max = list()
    nic_limit = 0
    lnk_limit = 0
    pci_limit = plot["limits"]["pci"]["pci-g3-x8"]
    for test_name, test_vals in y_vals.items():
        try:
            if test_vals["1"][1]:
                name = "-".join(test_name.split('-')[1:-1])
                if len(name) > 50:
                    name_lst = name.split('-')
                    name = ""
                    split_name = True
                    for segment in name_lst:
                        if (len(name) + len(segment) + 1) > 50 and split_name:
                            name += "<br>"
                            split_name = False
                        name += segment + '-'
                    name = name[:-1]

                vals[name] = dict()
                y_val_1 = test_vals["1"][0] / 1000000.0
                y_val_2 = test_vals["2"][0] / 1000000.0 if test_vals["2"][0] \
                    else None
                y_val_4 = test_vals["4"][0] / 1000000.0 if test_vals["4"][0] \
                    else None

                vals[name]["val"] = [y_val_1, y_val_2, y_val_4]
                vals[name]["rel"] = [1.0, None, None]
                vals[name]["ideal"] = [y_1c_max[test_name],
                                       y_1c_max[test_name] * 2,
                                       y_1c_max[test_name] * 4]
                vals[name]["diff"] = [(y_val_1 - y_1c_max[test_name]) * 100 /
                                      y_val_1, None, None]
                vals[name]["count"] = [test_vals["1"][1],
                                       test_vals["2"][1],
                                       test_vals["4"][1]]

                try:
                    val_max = max(max(vals[name]["val"], vals[name]["ideal"]))
                except ValueError as err:
                    logging.error(err)
                    continue
                if val_max:
                    y_max.append(int((val_max / 10) + 1) * 10)

                if y_val_2:
                    vals[name]["rel"][1] = round(y_val_2 / y_val_1, 2)
                    vals[name]["diff"][1] = \
                        (y_val_2 - vals[name]["ideal"][1]) * 100 / y_val_2
                if y_val_4:
                    vals[name]["rel"][2] = round(y_val_4 / y_val_1, 2)
                    vals[name]["diff"][2] = \
                        (y_val_4 - vals[name]["ideal"][2]) * 100 / y_val_4
        except IndexError as err:
            logging.warning("No data for '{0}'".format(test_name))
            logging.warning(repr(err))

        # Limits:
        if "x520" in test_name:
            limit = plot["limits"]["nic"]["x520"]
        elif "x710" in test_name:
            limit = plot["limits"]["nic"]["x710"]
        elif "xxv710" in test_name:
            limit = plot["limits"]["nic"]["xxv710"]
        elif "xl710" in test_name:
            limit = plot["limits"]["nic"]["xl710"]
        elif "x553" in test_name:
            limit = plot["limits"]["nic"]["x553"]
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
        if limit > lnk_limit:
            lnk_limit = limit

    # Sort the tests
    order = plot.get("sort", None)
    if order and y_tags:
        y_sorted = OrderedDict()
        y_tags_l = {s: [t.lower() for t in ts] for s, ts in y_tags.items()}
        for tag in order:
            for test, tags in y_tags_l.items():
                if tag.lower() in tags:
                    name = "-".join(test.split('-')[1:-1])
                    try:
                        y_sorted[name] = vals.pop(name)
                        y_tags_l.pop(test)
                    except KeyError as err:
                        logging.error("Not found: {0}".format(err))
                    finally:
                        break
    else:
        y_sorted = vals

    traces = list()
    annotations = list()
    x_vals = [1, 2, 4]

    # Limits:
    try:
        threshold = 1.1 * max(y_max)  # 10%
    except ValueError as err:
        logging.error(err)
        return
    nic_limit /= 1000000.0
    if nic_limit < threshold:
        traces.append(plgo.Scatter(
            x=x_vals,
            y=[nic_limit, ] * len(x_vals),
            name="NIC: {0:.2f}Mpps".format(nic_limit),
            showlegend=False,
            mode="lines",
            line=dict(
                dash="dot",
                color=COLORS[-1],
                width=1),
            hoverinfo="none"
        ))
        annotations.append(dict(
            x=1,
            y=nic_limit,
            xref="x",
            yref="y",
            xanchor="left",
            yanchor="bottom",
            text="NIC: {0:.2f}Mpps".format(nic_limit),
            font=dict(
                size=14,
                color=COLORS[-1],
            ),
            align="left",
            showarrow=False
        ))
        y_max.append(int((nic_limit / 10) + 1) * 10)

    lnk_limit /= 1000000.0
    if lnk_limit < threshold:
        traces.append(plgo.Scatter(
            x=x_vals,
            y=[lnk_limit, ] * len(x_vals),
            name="Link: {0:.2f}Mpps".format(lnk_limit),
            showlegend=False,
            mode="lines",
            line=dict(
                dash="dot",
                color=COLORS[-2],
                width=1),
            hoverinfo="none"
        ))
        annotations.append(dict(
            x=1,
            y=lnk_limit,
            xref="x",
            yref="y",
            xanchor="left",
            yanchor="bottom",
            text="Link: {0:.2f}Mpps".format(lnk_limit),
            font=dict(
                size=14,
                color=COLORS[-2],
            ),
            align="left",
            showarrow=False
        ))
        y_max.append(int((lnk_limit / 10) + 1) * 10)

    pci_limit /= 1000000.0
    if pci_limit < threshold:
        traces.append(plgo.Scatter(
            x=x_vals,
            y=[pci_limit, ] * len(x_vals),
            name="PCIe: {0:.2f}Mpps".format(pci_limit),
            showlegend=False,
            mode="lines",
            line=dict(
                dash="dot",
                color=COLORS[-3],
                width=1),
            hoverinfo="none"
        ))
        annotations.append(dict(
            x=1,
            y=pci_limit,
            xref="x",
            yref="y",
            xanchor="left",
            yanchor="bottom",
            text="PCIe: {0:.2f}Mpps".format(pci_limit),
            font=dict(
                size=14,
                color=COLORS[-3],
            ),
            align="left",
            showarrow=False
        ))
        y_max.append(int((pci_limit / 10) + 1) * 10)

    # Perfect and measured:
    cidx = 0
    for name, val in y_sorted.iteritems():
        hovertext = list()
        try:
            for idx in range(len(val["val"])):
                htext = ""
                if isinstance(val["val"][idx], float):
                    htext += "No. of Runs: {1}<br>" \
                             "Mean: {0:.2f}Mpps<br>".format(val["val"][idx],
                                                            val["count"][idx])
                if isinstance(val["diff"][idx], float):
                    htext += "Diff: {0:.0f}%<br>".format(round(val["diff"][idx]))
                if isinstance(val["rel"][idx], float):
                    htext += "Speedup: {0:.2f}".format(val["rel"][idx])
                hovertext.append(htext)
            traces.append(plgo.Scatter(x=x_vals,
                                       y=val["val"],
                                       name=name,
                                       legendgroup=name,
                                       mode="lines+markers",
                                       line=dict(
                                           color=COLORS[cidx],
                                           width=2),
                                       marker=dict(
                                           symbol="circle",
                                           size=10
                                       ),
                                       text=hovertext,
                                       hoverinfo="text+name"
                                       ))
            traces.append(plgo.Scatter(x=x_vals,
                                       y=val["ideal"],
                                       name="{0} perfect".format(name),
                                       legendgroup=name,
                                       showlegend=False,
                                       mode="lines",
                                       line=dict(
                                           color=COLORS[cidx],
                                           width=2,
                                           dash="dash"),
                                       text=["Perfect: {0:.2f}Mpps".format(y)
                                             for y in val["ideal"]],
                                       hoverinfo="text"
                                       ))
            cidx += 1
        except (IndexError, ValueError, KeyError) as err:
            logging.warning("No data for '{0}'".format(name))
            logging.warning(repr(err))

    try:
        # Create plot
        logging.info("    Writing file '{0}{1}'.".
                     format(plot["output-file"], plot["output-file-type"]))
        layout = deepcopy(plot["layout"])
        if layout.get("title", None):
            layout["title"] = "<b>Speedup Multi-core:</b> {0}". \
                format(layout["title"])
        layout["annotations"].extend(annotations)
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


def plot_http_server_performance_box(plot, input_data):
    """Generate the plot(s) with algorithm: plot_http_server_performance_box
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

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
    nr_of_samples = list()
    for val in y_vals.values():
        if len(val) > max_len:
            max_len = len(val)
        nr_of_samples.append(len(val))
    for key, val in y_vals.items():
        if len(val) < max_len:
            val.extend([None for _ in range(max_len - len(val))])

    # Add plot traces
    traces = list()
    df = pd.DataFrame(y_vals)
    df.head()
    for i, col in enumerate(df.columns):
        name = "{nr}. ({samples:02d} run{plural}) {name}".\
            format(nr=(i + 1),
                   samples=nr_of_samples[i],
                   plural='s' if nr_of_samples[i] > 1 else '',
                   name=col.lower().replace('-ndrpdr', ''))
        if len(name) > 50:
            name_lst = name.split('-')
            name = ""
            split_name = True
            for segment in name_lst:
                if (len(name) + len(segment) + 1) > 50 and split_name:
                    name += "<br>    "
                    split_name = False
                name += segment + '-'
            name = name[:-1]

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
        ploff.plot(plpl, show_link=False, auto_open=False,
                   filename='{0}{1}'.format(plot["output-file"],
                                            plot["output-file-type"]))
    except PlotlyError as err:
        logging.error("   Finished with error: {}".
                      format(str(err).replace("\n", " ")))
        return


def plot_service_density_heatmap(plot, input_data):
    """Generate the plot(s) with algorithm: plot_service_density_heatmap
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

    # Example data in Mpps
    txt_chains = ['1', '2', '4', '6']
    txt_nodes = ['1', '2', '4', '6']
    chains = [1, 2, 3, 4]
    nodes = [1, 2, 3, 4]
    data = [
        [10.3, 8.16, 6.51, 3.94],  # 1c1n, 1c2n, 1c4n, 1c6n
        [9.11, 7.27, 6.23, 4.15],  # 2c1n, 2c2n, 2c4n, 2c6n
        [8.22, 6.18, 5.03, None],  # 4c1n, 4c2n, 4c4n, 4c6n
        [7.01, 5.39, None, None]   # 6c1n, 6c2n, 6c4n, 6c6n
    ]

    hovertext = list()
    annotations = list()

    text = ("No. of Network Functions in a Chain: {nodes}<br>"
            "No. of Chains of Network Functions: {chains}<br>"
            "Packet Throughput: {val}")

    for c in range(len(txt_chains)):
        hover_line = list()
        for n in range(len(txt_nodes)):
            val = "{0}Mpps".format(data[c][n]) if data[c][n] else "Not measured"
            hover_line.append(text.format(nodes=txt_nodes[n],
                                          chains=txt_chains[c],
                                          val=val))
            if data[c][n]:
                annotations.append(dict(
                    x=n+1,
                    y=c+1,
                    xref="x",
                    yref="y",
                    xanchor="center",
                    yanchor="middle",
                    text="{val}".format(val=val),
                    font=dict(
                        size=14,
                    ),
                    align="center",
                    showarrow=False
                ))
        hovertext.append(hover_line)

    traces = [
        plgo.Heatmap(x=nodes,
                     y=chains,
                     z=data,
                     colorbar={
                         "title": "Packet Throughput [Mpps]",
                         "titleside": "right",
                         "titlefont": {
                            "size": 14
                         }
                     },
                     colorscale="Reds",
                     text=hovertext,
                     hoverinfo="text")
    ]

    for idx, item in enumerate(txt_nodes):
        annotations.append(dict(
            x=idx+1,
            y=0.4,
            xref="x",
            yref="y",
            xanchor="center",
            yanchor="top",
            text=item,
            font=dict(
                size=16,
            ),
            align="center",
            showarrow=False
        ))
    for idx, item in enumerate(txt_chains):
        annotations.append(dict(
            x=0.4,
            y=idx+1,
            xref="x",
            yref="y",
            xanchor="right",
            yanchor="middle",
            text=item,
            font=dict(
                size=16,
            ),
            align="center",
            showarrow=False
        ))

    updatemenus = list([
        dict(
            buttons=list([
                dict(
                    args=[{"colorscale": "Reds"}],
                    label="Red",
                    method="update"
                ),
                dict(
                    args=[{"colorscale": "Blues"}],
                    label="Blue",
                    method="update"
                ),
                dict(
                    args=[{"colorscale": "Greys"}],
                    label="Grey",
                    method="update"
                ),
                dict(
                    args=[{"colorscale": "Greens"}],
                    label="Green",
                    method="update"
                ),
                dict(
                    args=[{"colorscale": "RdBu"}],
                    label="RedBlue",
                    method="update"
                ),
                dict(
                    args=[{"colorscale": "Picnic"}],
                    label="Picnic",
                    method="update"
                ),
                dict(
                    args=[{"colorscale": "Rainbow"}],
                    label="Rainbow",
                    method="update"
                ),
                dict(
                    args=[{"colorscale": "Portland"}],
                    label="Portland",
                    method="update"
                ),
                dict(
                    args=[{"colorscale": "Jet"}],
                    label="Jet",
                    method="update"
                ),
                dict(
                    args=[{"colorscale": "Hot"}],
                    label="Hot",
                    method="update"
                ),
                dict(
                    args=[{"colorscale": "Blackbody"}],
                    label="Blackbody",
                    method="update"
                ),
                dict(
                    args=[{"colorscale": "Earth"}],
                    label="Earth",
                    method="update"
                ),
                dict(
                    args=[{"colorscale": "Electric"}],
                    label="Electric",
                    method="update"
                ),
                dict(
                    args=[{"colorscale": "Viridis"}],
                    label="Viridis",
                    method="update"
                ),
                dict(
                    args=[{"colorscale": "Cividis"}],
                    label="Cividis",
                    method="update"
                ),
            ])
        )
    ])

    try:
        layout = deepcopy(plot["layout"])
    except KeyError as err:
        logging.error("Finished with error: No layout defined")
        logging.error(repr(err))
        return

    if layout.get("title", None):
            layout["title"] = "<b>Packet Throughput:</b> {0}". \
                format(layout["title"])
    layout["annotations"] = annotations
    layout['updatemenus'] = updatemenus

    try:
        # Create plot
        plpl = plgo.Figure(data=traces, layout=layout)

        # Export Plot
        logging.info("    Writing file '{0}{1}'.".
                     format(plot["output-file"], plot["output-file-type"]))
        ploff.plot(plpl, show_link=False, auto_open=False,
                   filename='{0}{1}'.format(plot["output-file"],
                                            plot["output-file-type"]))
    except PlotlyError as err:
        logging.error("   Finished with error: {}".
                      format(str(err).replace("\n", " ")))
        return
