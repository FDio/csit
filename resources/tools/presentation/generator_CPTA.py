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

import logging

import plotly.offline as ploff
import plotly.graph_objs as plgo
import numpy as np
import pandas as pd

from collections import OrderedDict

from utils import find_outliers


import subprocess

import datetime

from os import makedirs, environ
from os.path import isdir
from shutil import copy, Error, make_archive

from utils import get_files
from errors import PresentationError


def generate_cpta(spec, data):
    """Generate all formats and versions of the Continuous Performance Trending
    and Analysis.

    :param spec: Specification read from the specification file.
    :type spec: Specification
    """

    logging.info("Generating the Continuous Performance Trending and Analysis "
                 "...")

    _generate_all_charts(spec, data)

    logging.info("Done.")


def _select_data(in_data, period, fill_missing=False, use_first=False):
    """

    :param in_data:
    :param period:
    :param fill_missing:
    :param use_first:
    :return:
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
    """

    :param in_data:
    :param trimmed_data:
    :param window:
    :return:
    """

    if len(in_data) > 2:
        win_size = in_data.size if in_data.size < window else window
        results = [0.0, ] * win_size
        median = in_data.rolling(window=win_size).median()
        stdev_t = trimmed_data.rolling(window=win_size, min_periods=2).std()
        m_vals = median.values
        s_vals = stdev_t.values
        d_vals = in_data.values
        for day in range(win_size, in_data.size):
            if np.isnan(m_vals[day - 1]) or np.isnan(s_vals[day - 1]):
                results.append(0.0)
            elif d_vals[day] < (m_vals[day - 1] - 3 * s_vals[day - 1]):
                results.append(0.33)
            elif (m_vals[day - 1] - 3 * s_vals[day - 1]) <= d_vals[day] <= \
                    (m_vals[day - 1] + 3 * s_vals[day - 1]):
                results.append(0.66)
            else:
                results.append(1.0)
    else:
        results = [0.0, ]
        median = np.median(in_data)
        stdev = np.std(in_data)
        if in_data.values[-1] < (median - 3 * stdev):
            results.append(0.33)
        elif (median - 3 * stdev) <= in_data.values[-1] <= (
                median + 3 * stdev):
            results.append(0.66)
        else:
            results.append(1.0)
    return results


def _generate_trending_traces(in_data, period, moving_win_size=10,
                              fill_missing=True, use_first=False,
                              show_moving_median=True, name="", color=""):
    """

    :param in_data:
    :param period:
    :param moving_win_size:
    :param fill_missing:
    :param use_first:
    :param show_moving_median:
    :param name:
    :param color:
    :return:
    """

    if period > 1:
        in_data = _select_data(in_data, period,
                               fill_missing=fill_missing,
                               use_first=use_first)

    data_x = [key for key in in_data.keys()]
    data_y = [val for val in in_data.values()]
    data_pd = pd.Series(data_y, index=data_x)

    t_data, outliers = find_outliers(data_pd)

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
        name="{name}".format(name=name),
        marker={
            "size": 5,
            "color": color,
            "symbol": "circle",
        },
    )
    traces = [trace_samples, ]

    trace_anomalies = plgo.Scatter(
        x=anomalies.keys(),
        y=anomalies.values,
        mode='markers',
        hoverinfo="none",
        showlegend=False,
        name="{name}: outliers".format(name=name),
        marker={
            "size": 15,
            "symbol": "circle-open",
            "color": anomalies_res,
            "colorscale": color_scale,
            "showscale": True,

            "colorbar": {
                "y": 0.5,
                "len": 0.8,
                "title": "Evaluation result",
                "titleside": 'right',
                "titlefont": {
                    "size": 14
                },
                "tickmode": 'array',
                "tickvals": [0.125, 0.375, 0.625, 0.875],
                "ticktext": ["Outlier", "Regress", "Normal", "Progress"],
                "ticks": 'outside',
                "ticklen": 0,
                "tickangle": -90,
                "thickness": 10
            }
        }
    )
    traces.append(trace_anomalies)

    if show_moving_median:
        data_mean_y = pd.Series(data_y).rolling(
            window=moving_win_size).median()
        trace_median = plgo.Scatter(
            x=data_x,
            y=data_mean_y,
            mode='lines',
            line={
                "shape": "spline",
                "width": 1,
                "color": color,
            },
            name='{name}: Trending line'.format(name=name,
                                                size=moving_win_size)
        )
        traces.append(trace_median)

    return traces, results[-5]


def _generate_chart(traces, layout, file_name):
    """

    :param traces:
    :param layout:
    :param file_name:
    :return:
    """

    # Create plot
    plpl = plgo.Figure(data=traces, layout=layout)
    ploff.plot(plpl, show_link=False, auto_open=False, filename=file_name)


def _generate_all_charts(spec, data):
    """

    :param spec:
    :param data:
    :return:
    """
    pass

    for chart in spec.cpta["plots"]:
        print(chart["title"])


# def plot_cpta_line(plot, input_data):
#     """Generate the plot(s) with algorithm: plot_cpta_line
#     specified in the specification file.
#
#     :param plot: Plot to generate.
#     :param input_data: Data to process.
#     :type plot: pandas.Series
#     :type input_data: InputData
#     """

# logging.info("  Generating the plot {0} ...".
#              format(plot.get("title", "")))
#
# colors = ["SkyBlue", "Olive", "Purple", "Coral", "Indigo", "Pink",
#           "Chocolate", "Brown", "Magenta", "Cyan", "Orange", "Black",
#           "Violet", "Blue", "Yellow"]
# results = list()
# traces = list()
#
# trace, result = _generate_trending_traces(L2XC, period=1, moving_win_size=10,
#                                          fill_missing=True, use_first=False,
#                                          name="l2xc", color=colors[0])
# traces.extend(trace)
# results.append(result)
#
# trace, result = _generate_trending_traces(IP4, period=1, moving_win_size=10,
#                                          fill_missing=True, use_first=False,
#                                          name="ip4", color=colors[1])
# traces.extend(trace)
# results.append(result)
#
# trace, result = _generate_trending_traces(IP6, period=1, moving_win_size=10,
#                                          fill_missing=True, use_first=False,
#                                          name="ip6", color=colors[2])
# traces.extend(trace)
# results.append(result)
#
# _generate_trending_plot(traces, LAYOUT, "trending_daily.html")
#
# results = list()
# traces = list()
#
# trace, result = _generate_trending_traces(L2XC, period=7, moving_win_size=5,
#                                          fill_missing=True, use_first=False,
#                                          name="l2xc", color=colors[3])
# traces.extend(trace)
# results.append(result)
#
# trace, result = _generate_trending_traces(IP4, period=7, moving_win_size=5,
#                                          fill_missing=True, use_first=False,
#                                          name="ip4", color=colors[4])
# traces.extend(trace)
# results.append(result)
#
# trace, result = _generate_trending_traces(IP6, period=7, moving_win_size=5,
#                                          fill_missing=True, use_first=False,
#                                          name="ip6", color=colors[5])
# traces.extend(trace)
# results.append(result)
#
# _generate_trending_plot(traces, LAYOUT, "trending_weekly.html")
#
# results = list()
# traces = list()
#
# trace, result = _generate_trending_traces(L2XC, period=30, moving_win_size=3,
#                                          fill_missing=True, use_first=False,
#                                          name="l2xc", color=colors[6])
# traces.extend(trace)
# results.append(result)
#
# trace, result = _generate_trending_traces(IP4, period=30, moving_win_size=3,
#                                          fill_missing=True, use_first=False,
#                                          name="ip4", color=colors[7])
# traces.extend(trace)
# results.append(result)
#
# trace, result = _generate_trending_traces(IP6, period=30, moving_win_size=3,
#                                          fill_missing=True, use_first=False,
#                                          name="ip6", color=colors[8])
# traces.extend(trace)
# results.append(result)
#
# _generate_trending_plot(traces, LAYOUT, "trending_monthly.html")
#
# logging.info("  Done.")
