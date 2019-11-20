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

"""Algorithms to generate plots.
"""


import re
import logging

from collections import OrderedDict
from copy import deepcopy

import pandas as pd
import plotly.offline as ploff
import plotly.graph_objs as plgo

from plotly.exceptions import PlotlyError

from pal_utils import mean, stdev


COLORS = ["SkyBlue", u"Olive", u"Purple", u"Coral", u"Indigo", u"Pink",
          u"Chocolate", u"Brown", u"Magenta", u"Cyan", u"Orange", u"Black",
          u"Violet", u"Blue", u"Yellow", u"BurlyWood", u"CadetBlue", u"Crimson",
          u"DarkBlue", u"DarkCyan", u"DarkGreen", u"Green", u"GoldenRod",
          u"LightGreen", u"LightSeaGreen", u"LightSkyBlue", u"Maroon",
          u"MediumSeaGreen", u"SeaGreen", u"LightSlateGrey"]

REGEX_NIC = re.compile(r'\d*ge\dp\d\D*\d*-')


def generate_plots(spec, data):
    """Generate all plots specified in the specification file.

    :param spec: Specification read from the specification file.
    :param data: Data to process.
    :type spec: Specification
    :type data: InputData
    """

    generator = {
        u"plot_nf_reconf_box_name": plot_nf_reconf_box_name,
        u"plot_perf_box_name": plot_perf_box_name,
        u"plot_lat_err_bars_name": plot_lat_err_bars_name,
        u"plot_tsa_name": plot_tsa_name,
        u"plot_http_server_perf_box": plot_http_server_perf_box,
        u"plot_nf_heatmap": plot_nf_heatmap
    }

    logging.info(u"Generating the plots ...")
    for index, plot in enumerate(spec.plots):
        try:
            logging.info(f"  Plot nr {index + 1}: {plot.get(u'title', u'')}")
            plot[u"limits"] = spec.configuration[u"limits"]
            generator[plot[u"algorithm"]](plot, data)
            logging.info(u"  Done.")
        except NameError as err:
            logging.error(
                f"Probably algorithm {plot[u'algorithm']} is not defined: "
                f"{repr(err)}"
            )
    logging.info(u"Done.")


def plot_nf_reconf_box_name(plot, input_data):
    """Generate the plot(s) with algorithm: plot_nf_reconf_box_name
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

    # Transform the data
    logging.info(
        f"    Creating the data set for the {plot.get(u'type', u'')} "
        f"{plot.get(u'title', u'')}."
    )
    data = input_data.filter_tests_by_name(
        plot, params=[u"result", u"parent", u"tags", u"type"]
    )
    if data is None:
        logging.error(u"No data.")
        return

    # Prepare the data for the plot
    y_vals = OrderedDict()
    loss = dict()
    for job in data:
        for build in job:
            for test in build:
                if y_vals.get(test[u"parent"], None) is None:
                    y_vals[test[u"parent"]] = list()
                    loss[test[u"parent"]] = list()
                try:
                    y_vals[test[u"parent"]].append(test[u"result"][u"time"])
                    loss[test[u"parent"]].append(test[u"result"][u"loss"])
                except (KeyError, TypeError):
                    y_vals[test[u"parent"]].append(None)

    # Add None to the lists with missing data
    max_len = 0
    nr_of_samples = list()
    for val in y_vals.values():
        if len(val) > max_len:
            max_len = len(val)
        nr_of_samples.append(len(val))
    for val in y_vals.values():
        if len(val) < max_len:
            val.extend([None for _ in range(max_len - len(val))])

    # Add plot traces
    traces = list()
    df_y = pd.DataFrame(y_vals)
    df_y.head()
    for i, col in enumerate(df_y.columns):
        tst_name = re.sub(REGEX_NIC, u"",
                          col.lower().replace(u'-ndrpdr', u'').
                          replace(u'2n1l-', u''))

        traces.append(plgo.Box(
            x=[str(i + 1) + u'.'] * len(df_y[col]),
            y=[y if y else None for y in df_y[col]],
            name=(
                f"{i + 1}. "
                f"({nr_of_samples[i]:02d} "
                f"run{u's' if nr_of_samples[i] > 1 else u''}, "
                f"packets lost average: {mean(loss[col]):.1f}) "
                f"{u'-'.join(tst_name.split(u'-')[3:-2])}"
            ),
            hoverinfo=u"y+name"
        ))
    try:
        # Create plot
        layout = deepcopy(plot[u"layout"])
        layout[u"title"] = f"<b>Time Lost:</b> {layout[u'title']}"
        layout[u"yaxis"][u"title"] = u"<b>Implied Time Lost [s]</b>"
        layout[u"legend"][u"font"][u"size"] = 14
        layout[u"yaxis"].pop(u"range")
        plpl = plgo.Figure(data=traces, layout=layout)

        # Export Plot
        file_type = plot.get(u"output-file-type", u".html")
        logging.info(f"    Writing file {plot[u'output-file']}{file_type}.")
        ploff.plot(
            plpl,
            show_link=False,
            auto_open=False,
            filename=f"{plot[u'output-file']}{file_type}"
        )
    except PlotlyError as err:
        logging.error(
            f"   Finished with error: {repr(err)}".replace(u"\n", u" ")
        )
        return


def plot_perf_box_name(plot, input_data):
    """Generate the plot(s) with algorithm: plot_perf_box_name
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

    # Transform the data
    logging.info(
        f"    Creating data set for the {plot.get(u'type', u'')} "
        f"{plot.get(u'title', u'')}."
    )
    data = input_data.filter_tests_by_name(
        plot, params=[u"throughput", u"parent", u"tags", u"type"])
    if data is None:
        logging.error(u"No data.")
        return

    # Prepare the data for the plot
    y_vals = OrderedDict()
    for job in data:
        for build in job:
            for test in build:
                if y_vals.get(test[u"parent"], None) is None:
                    y_vals[test[u"parent"]] = list()
                try:
                    if (test[u"type"] in (u"NDRPDR", ) and
                            u"-pdr" in plot.get(u"title", u"").lower()):
                        y_vals[test[u"parent"]].\
                            append(test[u"throughput"][u"PDR"][u"LOWER"])
                    elif (test[u"type"] in (u"NDRPDR", ) and
                          u"-ndr" in plot.get(u"title", u"").lower()):
                        y_vals[test[u"parent"]]. \
                            append(test[u"throughput"][u"NDR"][u"LOWER"])
                    elif test[u"type"] in (u"SOAK", ):
                        y_vals[test[u"parent"]].\
                            append(test[u"throughput"][u"LOWER"])
                    else:
                        continue
                except (KeyError, TypeError):
                    y_vals[test[u"parent"]].append(None)

    # Add None to the lists with missing data
    max_len = 0
    nr_of_samples = list()
    for val in y_vals.values():
        if len(val) > max_len:
            max_len = len(val)
        nr_of_samples.append(len(val))
    for val in y_vals.values():
        if len(val) < max_len:
            val.extend([None for _ in range(max_len - len(val))])

    # Add plot traces
    traces = list()
    df_y = pd.DataFrame(y_vals)
    df_y.head()
    y_max = list()
    for i, col in enumerate(df_y.columns):
        tst_name = re.sub(REGEX_NIC, u"",
                          col.lower().replace(u'-ndrpdr', u'').
                          replace(u'2n1l-', u''))
        traces.append(
            plgo.Box(
                x=[str(i + 1) + u'.'] * len(df_y[col]),
                y=[y / 1000000 if y else None for y in df_y[col]],
                name=(
                    f"{i + 1}. "
                    f"({nr_of_samples[i]:02d} "
                    f"run{u's' if nr_of_samples[i] > 1 else u''}) "
                    f"{tst_name}"
                ),
                hoverinfo=u"y+name"
            )
        )
        try:
            val_max = max(df_y[col])
            if val_max:
                y_max.append(int(val_max / 1000000) + 2)
        except (ValueError, TypeError) as err:
            logging.error(repr(err))
            continue

    try:
        # Create plot
        layout = deepcopy(plot[u"layout"])
        if layout.get(u"title", None):
            layout[u"title"] = f"<b>Throughput:</b> {layout[u'title']}"
        if y_max:
            layout[u"yaxis"][u"range"] = [0, max(y_max)]
        plpl = plgo.Figure(data=traces, layout=layout)

        # Export Plot
        logging.info(f"    Writing file {plot[u'output-file']}.html.")
        ploff.plot(
            plpl,
            show_link=False,
            auto_open=False,
            filename=f"{plot[u'output-file']}.html"
        )
    except PlotlyError as err:
        logging.error(
            f"   Finished with error: {repr(err)}".replace(u"\n", u" ")
        )
        return


def plot_lat_err_bars_name(plot, input_data):
    """Generate the plot(s) with algorithm: plot_lat_err_bars_name
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

    # Transform the data
    plot_title = plot.get(u"title", u"")
    logging.info(
        f"    Creating data set for the {plot.get(u'type', u'')} {plot_title}."
    )
    data = input_data.filter_tests_by_name(
        plot, params=[u"latency", u"parent", u"tags", u"type"])
    if data is None:
        logging.error(u"No data.")
        return

    # Prepare the data for the plot
    y_tmp_vals = OrderedDict()
    for job in data:
        for build in job:
            for test in build:
                try:
                    logging.debug(f"test[u'latency']: {test[u'latency']}\n")
                except ValueError as err:
                    logging.warning(repr(err))
                if y_tmp_vals.get(test[u"parent"], None) is None:
                    y_tmp_vals[test[u"parent"]] = [
                        list(),  # direction1, min
                        list(),  # direction1, avg
                        list(),  # direction1, max
                        list(),  # direction2, min
                        list(),  # direction2, avg
                        list()   # direction2, max
                    ]
                try:
                    if test[u"type"] not in (u"NDRPDR", ):
                        logging.warning(f"Invalid test type: {test[u'type']}")
                        continue
                    if u"-pdr" in plot_title.lower():
                        ttype = u"PDR"
                    elif u"-ndr" in plot_title.lower():
                        ttype = u"NDR"
                    else:
                        logging.warning(
                            f"Invalid test type: {test[u'type']}"
                        )
                        continue
                    y_tmp_vals[test[u"parent"]][0].append(
                        test[u"latency"][ttype][u"direction1"][u"min"])
                    y_tmp_vals[test[u"parent"]][1].append(
                        test[u"latency"][ttype][u"direction1"][u"avg"])
                    y_tmp_vals[test[u"parent"]][2].append(
                        test[u"latency"][ttype][u"direction1"][u"max"])
                    y_tmp_vals[test[u"parent"]][3].append(
                        test[u"latency"][ttype][u"direction2"][u"min"])
                    y_tmp_vals[test[u"parent"]][4].append(
                        test[u"latency"][ttype][u"direction2"][u"avg"])
                    y_tmp_vals[test[u"parent"]][5].append(
                        test[u"latency"][ttype][u"direction2"][u"max"])
                except (KeyError, TypeError) as err:
                    logging.warning(repr(err))

    x_vals = list()
    y_vals = list()
    y_mins = list()
    y_maxs = list()
    nr_of_samples = list()
    for key, val in y_tmp_vals.items():
        name = re.sub(REGEX_NIC, u"", key.replace(u'-ndrpdr', u'').
                      replace(u'2n1l-', u''))
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

    traces = list()
    annotations = list()

    for idx, _ in enumerate(x_vals):
        if not bool(int(idx % 2)):
            direction = u"West-East"
        else:
            direction = u"East-West"
        hovertext = (
            f"No. of Runs: {nr_of_samples[idx]}<br>"
            f"Test: {x_vals[idx]}<br>"
            f"Direction: {direction}<br>"
        )
        if isinstance(y_maxs[idx], float):
            hovertext += f"Max: {y_maxs[idx]:.2f}uSec<br>"
        if isinstance(y_vals[idx], float):
            hovertext += f"Mean: {y_vals[idx]:.2f}uSec<br>"
        if isinstance(y_mins[idx], float):
            hovertext += f"Min: {y_mins[idx]:.2f}uSec"

        if isinstance(y_maxs[idx], float) and isinstance(y_vals[idx], float):
            array = [y_maxs[idx] - y_vals[idx], ]
        else:
            array = [None, ]
        if isinstance(y_mins[idx], float) and isinstance(y_vals[idx], float):
            arrayminus = [y_vals[idx] - y_mins[idx], ]
        else:
            arrayminus = [None, ]
        traces.append(plgo.Scatter(
            x=[idx, ],
            y=[y_vals[idx], ],
            name=x_vals[idx],
            legendgroup=x_vals[idx],
            showlegend=bool(int(idx % 2)),
            mode=u"markers",
            error_y=dict(
                type=u"data",
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
            hoverinfo=u"text",
        ))
        annotations.append(dict(
            x=idx,
            y=0,
            xref=u"x",
            yref=u"y",
            xanchor=u"center",
            yanchor=u"top",
            text=u"E-W" if bool(int(idx % 2)) else u"W-E",
            font=dict(
                size=16,
            ),
            align=u"center",
            showarrow=False
        ))

    try:
        # Create plot
        file_type = plot.get(u"output-file-type", u".html")
        logging.info(f"    Writing file {plot[u'output-file']}{file_type}.")
        layout = deepcopy(plot[u"layout"])
        if layout.get(u"title", None):
            layout[u"title"] = f"<b>Latency:</b> {layout[u'title']}"
        layout[u"annotations"] = annotations
        plpl = plgo.Figure(data=traces, layout=layout)

        # Export Plot
        ploff.plot(
            plpl,
            show_link=False, auto_open=False,
            filename=f"{plot[u'output-file']}{file_type}"
        )
    except PlotlyError as err:
        logging.error(
            f"   Finished with error: {repr(err)}".replace(u"\n", u" ")
        )
        return


def plot_tsa_name(plot, input_data):
    """Generate the plot(s) with algorithm:
    plot_tsa_name
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

    # Transform the data
    plot_title = plot.get(u"title", u"")
    logging.info(
        f"    Creating data set for the {plot.get(u'type', u'')} {plot_title}."
    )
    data = input_data.filter_tests_by_name(
        plot, params=[u"throughput", u"parent", u"tags", u"type"])
    if data is None:
        logging.error(u"No data.")
        return

    y_vals = OrderedDict()
    for job in data:
        for build in job:
            for test in build:
                if y_vals.get(test[u"parent"], None) is None:
                    y_vals[test[u"parent"]] = {
                        u"1": list(),
                        u"2": list(),
                        u"4": list()
                    }
                try:
                    if test[u"type"] not in (u"NDRPDR",):
                        continue

                    if u"-pdr" in plot_title.lower():
                        ttype = u"PDR"
                    elif u"-ndr" in plot_title.lower():
                        ttype = u"NDR"
                    else:
                        continue

                    if u"1C" in test[u"tags"]:
                        y_vals[test[u"parent"]][u"1"]. \
                            append(test[u"throughput"][ttype][u"LOWER"])
                    elif u"2C" in test[u"tags"]:
                        y_vals[test[u"parent"]][u"2"]. \
                            append(test[u"throughput"][ttype][u"LOWER"])
                    elif u"4C" in test[u"tags"]:
                        y_vals[test[u"parent"]][u"4"]. \
                            append(test[u"throughput"][ttype][u"LOWER"])
                except (KeyError, TypeError):
                    pass

    if not y_vals:
        logging.warning(f"No data for the plot {plot.get(u'title', u'')}")
        return

    y_1c_max = dict()
    for test_name, test_vals in y_vals.items():
        for key, test_val in test_vals.items():
            if test_val:
                avg_val = sum(test_val) / len(test_val)
                y_vals[test_name][key] = [avg_val, len(test_val)]
                ideal = avg_val / (int(key) * 1000000.0)
                if test_name not in y_1c_max or ideal > y_1c_max[test_name]:
                    y_1c_max[test_name] = ideal

    vals = OrderedDict()
    y_max = list()
    nic_limit = 0
    lnk_limit = 0
    pci_limit = plot[u"limits"][u"pci"][u"pci-g3-x8"]
    for test_name, test_vals in y_vals.items():
        try:
            if test_vals[u"1"][1]:
                name = re.sub(
                    REGEX_NIC,
                    u"",
                    test_name.replace(u'-ndrpdr', u'').replace(u'2n1l-', u'')
                )
                vals[name] = OrderedDict()
                y_val_1 = test_vals[u"1"][0] / 1000000.0
                y_val_2 = test_vals[u"2"][0] / 1000000.0 if test_vals[u"2"][0] \
                    else None
                y_val_4 = test_vals[u"4"][0] / 1000000.0 if test_vals[u"4"][0] \
                    else None

                vals[name][u"val"] = [y_val_1, y_val_2, y_val_4]
                vals[name][u"rel"] = [1.0, None, None]
                vals[name][u"ideal"] = [
                    y_1c_max[test_name],
                    y_1c_max[test_name] * 2,
                    y_1c_max[test_name] * 4
                ]
                vals[name][u"diff"] = [
                    (y_val_1 - y_1c_max[test_name]) * 100 / y_val_1, None, None
                ]
                vals[name][u"count"] = [
                    test_vals[u"1"][1],
                    test_vals[u"2"][1],
                    test_vals[u"4"][1]
                ]

                try:
                    val_max = max(vals[name][u"val"])
                except ValueError as err:
                    logging.error(repr(err))
                    continue
                if val_max:
                    y_max.append(val_max)

                if y_val_2:
                    vals[name][u"rel"][1] = round(y_val_2 / y_val_1, 2)
                    vals[name][u"diff"][1] = \
                        (y_val_2 - vals[name][u"ideal"][1]) * 100 / y_val_2
                if y_val_4:
                    vals[name][u"rel"][2] = round(y_val_4 / y_val_1, 2)
                    vals[name][u"diff"][2] = \
                        (y_val_4 - vals[name][u"ideal"][2]) * 100 / y_val_4
        except IndexError as err:
            logging.warning(f"No data for {test_name}")
            logging.warning(repr(err))

        # Limits:
        if u"x520" in test_name:
            limit = plot[u"limits"][u"nic"][u"x520"]
        elif u"x710" in test_name:
            limit = plot[u"limits"][u"nic"][u"x710"]
        elif u"xxv710" in test_name:
            limit = plot[u"limits"][u"nic"][u"xxv710"]
        elif u"xl710" in test_name:
            limit = plot[u"limits"][u"nic"][u"xl710"]
        elif u"x553" in test_name:
            limit = plot[u"limits"][u"nic"][u"x553"]
        else:
            limit = 0
        if limit > nic_limit:
            nic_limit = limit

        mul = 2 if u"ge2p" in test_name else 1
        if u"10ge" in test_name:
            limit = plot[u"limits"][u"link"][u"10ge"] * mul
        elif u"25ge" in test_name:
            limit = plot[u"limits"][u"link"][u"25ge"] * mul
        elif u"40ge" in test_name:
            limit = plot[u"limits"][u"link"][u"40ge"] * mul
        elif u"100ge" in test_name:
            limit = plot[u"limits"][u"link"][u"100ge"] * mul
        else:
            limit = 0
        if limit > lnk_limit:
            lnk_limit = limit

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
    traces.append(plgo.Scatter(
        x=x_vals,
        y=[nic_limit, ] * len(x_vals),
        name=f"NIC: {nic_limit:.2f}Mpps",
        showlegend=False,
        mode=u"lines",
        line=dict(
            dash=u"dot",
            color=COLORS[-1],
            width=1),
        hoverinfo=u"none"
    ))
    annotations.append(dict(
        x=1,
        y=nic_limit,
        xref=u"x",
        yref=u"y",
        xanchor=u"left",
        yanchor=u"bottom",
        text=f"NIC: {nic_limit:.2f}Mpps",
        font=dict(
            size=14,
            color=COLORS[-1],
        ),
        align=u"left",
        showarrow=False
    ))
    y_max.append(nic_limit)

    lnk_limit /= 1000000.0
    if lnk_limit < threshold:
        traces.append(plgo.Scatter(
            x=x_vals,
            y=[lnk_limit, ] * len(x_vals),
            name=f"Link: {lnk_limit:.2f}Mpps",
            showlegend=False,
            mode=u"lines",
            line=dict(
                dash=u"dot",
                color=COLORS[-2],
                width=1),
            hoverinfo=u"none"
        ))
        annotations.append(dict(
            x=1,
            y=lnk_limit,
            xref=u"x",
            yref=u"y",
            xanchor=u"left",
            yanchor=u"bottom",
            text=f"Link: {lnk_limit:.2f}Mpps",
            font=dict(
                size=14,
                color=COLORS[-2],
            ),
            align=u"left",
            showarrow=False
        ))
        y_max.append(lnk_limit)

    pci_limit /= 1000000.0
    if (pci_limit < threshold and
            (pci_limit < lnk_limit * 0.95 or lnk_limit > lnk_limit * 1.05)):
        traces.append(plgo.Scatter(
            x=x_vals,
            y=[pci_limit, ] * len(x_vals),
            name=f"PCIe: {pci_limit:.2f}Mpps",
            showlegend=False,
            mode=u"lines",
            line=dict(
                dash=u"dot",
                color=COLORS[-3],
                width=1),
            hoverinfo=u"none"
        ))
        annotations.append(dict(
            x=1,
            y=pci_limit,
            xref=u"x",
            yref=u"y",
            xanchor=u"left",
            yanchor=u"bottom",
            text=f"PCIe: {pci_limit:.2f}Mpps",
            font=dict(
                size=14,
                color=COLORS[-3],
            ),
            align=u"left",
            showarrow=False
        ))
        y_max.append(pci_limit)

    # Perfect and measured:
    cidx = 0
    for name, val in vals.items():
        hovertext = list()
        try:
            for idx in range(len(val[u"val"])):
                htext = ""
                if isinstance(val[u"val"][idx], float):
                    htext += (
                        f"No. of Runs: {val[u'count'][idx]}<br>"
                        f"Mean: {val[u'val'][idx]:.2f}Mpps<br>"
                    )
                if isinstance(val[u"diff"][idx], float):
                    htext += f"Diff: {round(val[u'diff'][idx]):.0f}%<br>"
                if isinstance(val[u"rel"][idx], float):
                    htext += f"Speedup: {val[u'rel'][idx]:.2f}"
                hovertext.append(htext)
            traces.append(
                plgo.Scatter(
                    x=x_vals,
                    y=val[u"val"],
                    name=name,
                    legendgroup=name,
                    mode=u"lines+markers",
                    line=dict(
                        color=COLORS[cidx],
                        width=2),
                    marker=dict(
                        symbol=u"circle",
                        size=10
                    ),
                    text=hovertext,
                    hoverinfo=u"text+name"
                )
            )
            traces.append(
                plgo.Scatter(
                    x=x_vals,
                    y=val[u"ideal"],
                    name=f"{name} perfect",
                    legendgroup=name,
                    showlegend=False,
                    mode=u"lines",
                    line=dict(
                        color=COLORS[cidx],
                        width=2,
                        dash=u"dash"),
                    text=[f"Perfect: {y:.2f}Mpps" for y in val[u"ideal"]],
                    hoverinfo=u"text"
                )
            )
            cidx += 1
        except (IndexError, ValueError, KeyError) as err:
            logging.warning(f"No data for {name}\n{repr(err)}")

    try:
        # Create plot
        file_type = plot.get(u"output-file-type", u".html")
        logging.info(f"    Writing file {plot[u'output-file']}{file_type}.")
        layout = deepcopy(plot[u"layout"])
        if layout.get(u"title", None):
            layout[u"title"] = f"<b>Speedup Multi-core:</b> {layout[u'title']}"
        layout[u"yaxis"][u"range"] = [0, int(max(y_max) * 1.1)]
        layout[u"annotations"].extend(annotations)
        plpl = plgo.Figure(data=traces, layout=layout)

        # Export Plot
        ploff.plot(
            plpl,
            show_link=False,
            auto_open=False,
            filename=f"{plot[u'output-file']}{file_type}"
        )
    except PlotlyError as err:
        logging.error(
            f"   Finished with error: {repr(err)}".replace(u"\n", u" ")
        )
        return


def plot_http_server_perf_box(plot, input_data):
    """Generate the plot(s) with algorithm: plot_http_server_perf_box
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

    # Transform the data
    logging.info(
        f"    Creating the data set for the {plot.get(u'type', u'')} "
        f"{plot.get(u'title', u'')}."
    )
    data = input_data.filter_data(plot)
    if data is None:
        logging.error(u"No data.")
        return

    # Prepare the data for the plot
    y_vals = dict()
    for job in data:
        for build in job:
            for test in build:
                if y_vals.get(test[u"name"], None) is None:
                    y_vals[test[u"name"]] = list()
                try:
                    y_vals[test[u"name"]].append(test[u"result"])
                except (KeyError, TypeError):
                    y_vals[test[u"name"]].append(None)

    # Add None to the lists with missing data
    max_len = 0
    nr_of_samples = list()
    for val in y_vals.values():
        if len(val) > max_len:
            max_len = len(val)
        nr_of_samples.append(len(val))
    for val in y_vals.values():
        if len(val) < max_len:
            val.extend([None for _ in range(max_len - len(val))])

    # Add plot traces
    traces = list()
    df_y = pd.DataFrame(y_vals)
    df_y.head()
    for i, col in enumerate(df_y.columns):
        name = \
            f"{i + 1}. " \
            f"({nr_of_samples[i]:02d} " \
            f"run{u's' if nr_of_samples[i] > 1 else u''}) " \
            f"{col.lower().replace(u'-ndrpdr', u'')}"
        if len(name) > 50:
            name_lst = name.split('-')
            name = u""
            split_name = True
            for segment in name_lst:
                if (len(name) + len(segment) + 1) > 50 and split_name:
                    name += u"<br>    "
                    split_name = False
                name += segment + '-'
            name = name[:-1]

        traces.append(plgo.Box(x=[str(i + 1) + '.'] * len(df_y[col]),
                               y=df_y[col],
                               name=name,
                               **plot[u"traces"]))
    try:
        # Create plot
        plpl = plgo.Figure(data=traces, layout=plot[u"layout"])

        # Export Plot
        logging.info(
            f"    Writing file {plot[u'output-file']}"
            f"{plot[u'output-file-type']}."
        )
        ploff.plot(
            plpl,
            show_link=False,
            auto_open=False,
            filename=f"{plot[u'output-file']}{plot[u'output-file-type']}"
        )
    except PlotlyError as err:
        logging.error(
            f"   Finished with error: {repr(err)}".replace(u"\n", u" ")
        )
        return


def plot_nf_heatmap(plot, input_data):
    """Generate the plot(s) with algorithm: plot_nf_heatmap
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

    regex_cn = re.compile(r'^(\d*)R(\d*)C$')
    regex_test_name = re.compile(r'^.*-(\d+ch|\d+pl)-'
                                 r'(\d+mif|\d+vh)-'
                                 r'(\d+vm\d+t|\d+dcr\d+t).*$')
    vals = dict()

    # Transform the data
    logging.info(
        f"    Creating the data set for the {plot.get(u'type', u'')} "
        f"{plot.get(u'title', u'')}."
    )
    data = input_data.filter_data(plot, continue_on_error=True)
    if data is None or data.empty:
        logging.error(u"No data.")
        return

    for job in data:
        for build in job:
            for test in build:
                for tag in test[u"tags"]:
                    groups = re.search(regex_cn, tag)
                    if groups:
                        chain = str(groups.group(1))
                        node = str(groups.group(2))
                        break
                else:
                    continue
                groups = re.search(regex_test_name, test[u"name"])
                if groups and len(groups.groups()) == 3:
                    hover_name = (
                        f"{str(groups.group(1))}-"
                        f"{str(groups.group(2))}-"
                        f"{str(groups.group(3))}"
                    )
                else:
                    hover_name = u""
                if vals.get(chain, None) is None:
                    vals[chain] = dict()
                if vals[chain].get(node, None) is None:
                    vals[chain][node] = dict(
                        name=hover_name,
                        vals=list(),
                        nr=None,
                        mean=None,
                        stdev=None
                    )
                try:
                    if plot[u"include-tests"] == u"MRR":
                        result = test[u"result"][u"receive-rate"]
                    elif plot[u"include-tests"] == u"PDR":
                        result = test[u"throughput"][u"PDR"][u"LOWER"]
                    elif plot[u"include-tests"] == u"NDR":
                        result = test[u"throughput"][u"NDR"][u"LOWER"]
                    else:
                        result = None
                except TypeError:
                    result = None

                if result:
                    vals[chain][node][u"vals"].append(result)

    if not vals:
        logging.error(u"No data.")
        return

    txt_chains = list()
    txt_nodes = list()
    for key_c in vals:
        txt_chains.append(key_c)
        for key_n in vals[key_c].keys():
            txt_nodes.append(key_n)
            if vals[key_c][key_n][u"vals"]:
                vals[key_c][key_n][u"nr"] = len(vals[key_c][key_n][u"vals"])
                vals[key_c][key_n][u"mean"] = \
                    round(mean(vals[key_c][key_n][u"vals"]) / 1000000, 1)
                vals[key_c][key_n][u"stdev"] = \
                    round(stdev(vals[key_c][key_n][u"vals"]) / 1000000, 1)
    txt_nodes = list(set(txt_nodes))

    def sort_by_int(value):
        """Makes possible to sort a list of strings which represent integers.

        :param value: Integer as a string.
        :type value: str
        :returns: Integer representation of input parameter 'value'.
        :rtype: int
        """
        return int(value)

    txt_chains = sorted(txt_chains, key=sort_by_int)
    txt_nodes = sorted(txt_nodes, key=sort_by_int)

    chains = [i + 1 for i in range(len(txt_chains))]
    nodes = [i + 1 for i in range(len(txt_nodes))]

    data = [list() for _ in range(len(chains))]
    for chain in chains:
        for node in nodes:
            try:
                val = vals[txt_chains[chain - 1]][txt_nodes[node - 1]]["mean"]
            except (KeyError, IndexError):
                val = None
            data[chain - 1].append(val)

    # Color scales:
    my_green = [[0.0, u"rgb(235, 249, 242)"],
                [1.0, u"rgb(45, 134, 89)"]]

    my_blue = [[0.0, u"rgb(236, 242, 248)"],
               [1.0, u"rgb(57, 115, 172)"]]

    my_grey = [[0.0, u"rgb(230, 230, 230)"],
               [1.0, u"rgb(102, 102, 102)"]]

    hovertext = list()
    annotations = list()

    text = (u"Test: {name}<br>"
            u"Runs: {nr}<br>"
            u"Thput: {val}<br>"
            u"StDev: {stdev}")

    for chain, _ in enumerate(txt_chains):
        hover_line = list()
        for node, _ in enumerate(txt_nodes):
            if data[chain][node] is not None:
                annotations.append(
                    dict(
                        x=node+1,
                        y=chain+1,
                        xref=u"x",
                        yref=u"y",
                        xanchor=u"center",
                        yanchor=u"middle",
                        text=str(data[chain][node]),
                        font=dict(
                            size=14,
                        ),
                        align=u"center",
                        showarrow=False
                    )
                )
                hover_line.append(text.format(
                    name=vals[txt_chains[chain]][txt_nodes[node]][u"name"],
                    nr=vals[txt_chains[chain]][txt_nodes[node]][u"nr"],
                    val=data[chain][node],
                    stdev=vals[txt_chains[chain]][txt_nodes[node]][u"stdev"]))
        hovertext.append(hover_line)

    traces = [
        plgo.Heatmap(
            x=nodes,
            y=chains,
            z=data,
            colorbar=dict(
                title=plot.get(u"z-axis", u""),
                titleside=u"right",
                titlefont=dict(
                    size=16
                ),
                tickfont=dict(
                    size=16,
                ),
                tickformat=u".1f",
                yanchor=u"bottom",
                y=-0.02,
                len=0.925,
            ),
            showscale=True,
            colorscale=my_green,
            text=hovertext,
            hoverinfo=u"text"
        )
    ]

    for idx, item in enumerate(txt_nodes):
        # X-axis, numbers:
        annotations.append(
            dict(
                x=idx+1,
                y=0.05,
                xref=u"x",
                yref=u"y",
                xanchor=u"center",
                yanchor=u"top",
                text=item,
                font=dict(
                    size=16,
                ),
                align=u"center",
                showarrow=False
            )
        )
    for idx, item in enumerate(txt_chains):
        # Y-axis, numbers:
        annotations.append(
            dict(
                x=0.35,
                y=idx+1,
                xref=u"x",
                yref=u"y",
                xanchor=u"right",
                yanchor=u"middle",
                text=item,
                font=dict(
                    size=16,
                ),
                align=u"center",
                showarrow=False
            )
        )
    # X-axis, title:
    annotations.append(
        dict(
            x=0.55,
            y=-0.15,
            xref=u"paper",
            yref=u"y",
            xanchor=u"center",
            yanchor=u"bottom",
            text=plot.get(u"x-axis", u""),
            font=dict(
                size=16,
            ),
            align=u"center",
            showarrow=False
        )
    )
    # Y-axis, title:
    annotations.append(
        dict(
            x=-0.1,
            y=0.5,
            xref=u"x",
            yref=u"paper",
            xanchor=u"center",
            yanchor=u"middle",
            text=plot.get(u"y-axis", u""),
            font=dict(
                size=16,
            ),
            align=u"center",
            textangle=270,
            showarrow=False
        )
    )
    updatemenus = list([
        dict(
            x=1.0,
            y=0.0,
            xanchor=u"right",
            yanchor=u"bottom",
            direction=u"up",
            buttons=list([
                dict(
                    args=[
                        {
                            u"colorscale": [my_green, ],
                            u"reversescale": False
                        }
                    ],
                    label=u"Green",
                    method=u"update"
                ),
                dict(
                    args=[
                        {
                            u"colorscale": [my_blue, ],
                            u"reversescale": False
                        }
                    ],
                    label=u"Blue",
                    method=u"update"
                ),
                dict(
                    args=[
                        {
                            u"colorscale": [my_grey, ],
                            u"reversescale": False
                        }
                    ],
                    label=u"Grey",
                    method=u"update"
                )
            ])
        )
    ])

    try:
        layout = deepcopy(plot[u"layout"])
    except KeyError as err:
        logging.error(f"Finished with error: No layout defined\n{repr(err)}")
        return

    layout[u"annotations"] = annotations
    layout[u'updatemenus'] = updatemenus

    try:
        # Create plot
        plpl = plgo.Figure(data=traces, layout=layout)

        # Export Plot
        logging.info(
            f"    Writing file {plot[u'output-file']}"
            f"{plot[u'output-file-type']}."
        )
        ploff.plot(
            plpl,
            show_link=False,
            auto_open=False,
            filename=f"{plot[u'output-file']}{plot[u'output-file-type']}"
        )
    except PlotlyError as err:
        logging.error(
            f"   Finished with error: {repr(err)}".replace(u"\n", u" ")
        )
        return
