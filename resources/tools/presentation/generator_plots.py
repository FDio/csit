# Copyright (c) 2021 Cisco and/or its affiliates.
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

import hdrh.histogram
import hdrh.codec
import pandas as pd
import plotly.offline as ploff
import plotly.graph_objs as plgo

from collections import OrderedDict
from copy import deepcopy
from math import log

from plotly.exceptions import PlotlyError

from pal_utils import mean, stdev


COLORS = (
    u"#1A1110",
    u"#DA2647",
    u"#214FC6",
    u"#01786F",
    u"#BD8260",
    u"#FFD12A",
    u"#A6E7FF",
    u"#738276",
    u"#C95A49",
    u"#FC5A8D",
    u"#CEC8EF",
    u"#391285",
    u"#6F2DA8",
    u"#FF878D",
    u"#45A27D",
    u"#FFD0B9",
    u"#FD5240",
    u"#DB91EF",
    u"#44D7A8",
    u"#4F86F7",
    u"#84DE02",
    u"#FFCFF1",
    u"#614051"
)

REGEX_NIC = re.compile(r'(\d*ge\dp\d\D*\d*[a-z]*)-')

# This value depends on latency stream rate (9001 pps) and duration (5s).
# Keep it slightly higher to ensure rounding errors to not remove tick mark.
PERCENTILE_MAX = 99.999501


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
        u"plot_tsa_name": plot_tsa_name,
        u"plot_http_server_perf_box": plot_http_server_perf_box,
        u"plot_nf_heatmap": plot_nf_heatmap,
        u"plot_hdrh_lat_by_percentile": plot_hdrh_lat_by_percentile,
        u"plot_hdrh_lat_by_percentile_x_log": plot_hdrh_lat_by_percentile_x_log,
        u"plot_mrr_box_name": plot_mrr_box_name,
        u"plot_ndrpdr_box_name": plot_ndrpdr_box_name
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


def plot_hdrh_lat_by_percentile(plot, input_data):
    """Generate the plot(s) with algorithm: plot_hdrh_lat_by_percentile
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
    if plot.get(u"include", None):
        data = input_data.filter_tests_by_name(
            plot,
            params=[u"name", u"latency", u"parent", u"tags", u"type"]
        )[0][0]
    elif plot.get(u"filter", None):
        data = input_data.filter_data(
            plot,
            params=[u"name", u"latency", u"parent", u"tags", u"type"],
            continue_on_error=True
        )[0][0]
    else:
        job = list(plot[u"data"].keys())[0]
        build = str(plot[u"data"][job][0])
        data = input_data.tests(job, build)

    if data is None or len(data) == 0:
        logging.error(u"No data.")
        return

    desc = {
        u"LAT0": u"No-load.",
        u"PDR10": u"Low-load, 10% PDR.",
        u"PDR50": u"Mid-load, 50% PDR.",
        u"PDR90": u"High-load, 90% PDR.",
        u"PDR": u"Full-load, 100% PDR.",
        u"NDR10": u"Low-load, 10% NDR.",
        u"NDR50": u"Mid-load, 50% NDR.",
        u"NDR90": u"High-load, 90% NDR.",
        u"NDR": u"Full-load, 100% NDR."
    }

    graphs = [
        u"LAT0",
        u"PDR10",
        u"PDR50",
        u"PDR90"
    ]

    file_links = plot.get(u"output-file-links", None)
    target_links = plot.get(u"target-links", None)

    for test in data:
        try:
            if test[u"type"] not in (u"NDRPDR",):
                logging.warning(f"Invalid test type: {test[u'type']}")
                continue
            name = re.sub(REGEX_NIC, u"", test[u"parent"].
                          replace(u'-ndrpdr', u'').replace(u'2n1l-', u''))
            try:
                nic = re.search(REGEX_NIC, test[u"parent"]).group(1)
            except (IndexError, AttributeError, KeyError, ValueError):
                nic = u""
            name_link = f"{nic}-{test[u'name']}".replace(u'-ndrpdr', u'')

            logging.info(f"    Generating the graph: {name_link}")

            fig = plgo.Figure()
            layout = deepcopy(plot[u"layout"])

            for color, graph in enumerate(graphs):
                for idx, direction in enumerate((u"direction1", u"direction2")):
                    previous_x = 0.0
                    xaxis = list()
                    yaxis = list()
                    hovertext = list()
                    try:
                        decoded = hdrh.histogram.HdrHistogram.decode(
                            test[u"latency"][graph][direction][u"hdrh"]
                        )
                    except hdrh.codec.HdrLengthException:
                        logging.warning(
                            f"No data for direction {(u'W-E', u'E-W')[idx % 2]}"
                        )
                        continue

                    for item in decoded.get_recorded_iterator():
                        percentile = item.percentile_level_iterated_to
                        xaxis.append(previous_x)
                        yaxis.append(item.value_iterated_to)
                        hovertext.append(
                            f"<b>{desc[graph]}</b><br>"
                            f"Direction: {(u'W-E', u'E-W')[idx % 2]}<br>"
                            f"Percentile: {previous_x:.5f}-{percentile:.5f}%<br>"
                            f"Latency: {item.value_iterated_to}uSec"
                        )
                        xaxis.append(percentile)
                        yaxis.append(item.value_iterated_to)
                        hovertext.append(
                            f"<b>{desc[graph]}</b><br>"
                            f"Direction: {(u'W-E', u'E-W')[idx % 2]}<br>"
                            f"Percentile: {previous_x:.5f}-{percentile:.5f}%<br>"
                            f"Latency: {item.value_iterated_to}uSec"
                        )
                        previous_x = percentile
                    fig.add_trace(
                        plgo.Scatter(
                            x=xaxis,
                            y=yaxis,
                            name=desc[graph],
                            mode=u"lines",
                            legendgroup=desc[graph],
                            showlegend=bool(idx),
                            line=dict(
                                color=COLORS[color],
                                dash=u"solid",
                                width=1 if idx % 2 else 2
                            ),
                            hovertext=hovertext,
                            hoverinfo=u"text"
                        )
                    )

            layout[u"title"][u"text"] = f"<b>Latency:</b> {name}"
            fig.update_layout(layout)

            # Create plot
            file_name = f"{plot[u'output-file']}-{name_link}.html"
            logging.info(f"    Writing file {file_name}")

            try:
                # Export Plot
                ploff.plot(fig, show_link=False, auto_open=False,
                           filename=file_name)
                # Add link to the file:
                if file_links and target_links:
                    with open(file_links, u"a") as file_handler:
                        file_handler.write(
                            f"- `{name_link} "
                            f"<{target_links}/{file_name.split(u'/')[-1]}>`_\n"
                        )
            except FileNotFoundError as err:
                logging.error(
                    f"Not possible to write the link to the file "
                    f"{file_links}\n{err}"
                )
            except PlotlyError as err:
                logging.error(f"   Finished with error: {repr(err)}")

        except hdrh.codec.HdrLengthException as err:
            logging.warning(repr(err))
            continue

        except (ValueError, KeyError) as err:
            logging.warning(repr(err))
            continue


def plot_hdrh_lat_by_percentile_x_log(plot, input_data):
    """Generate the plot(s) with algorithm: plot_hdrh_lat_by_percentile_x_log
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
    if plot.get(u"include", None):
        data = input_data.filter_tests_by_name(
            plot,
            params=[u"name", u"latency", u"parent", u"tags", u"type"]
        )[0][0]
    elif plot.get(u"filter", None):
        data = input_data.filter_data(
            plot,
            params=[u"name", u"latency", u"parent", u"tags", u"type"],
            continue_on_error=True
        )[0][0]
    else:
        job = list(plot[u"data"].keys())[0]
        build = str(plot[u"data"][job][0])
        data = input_data.tests(job, build)

    if data is None or len(data) == 0:
        logging.error(u"No data.")
        return

    desc = {
        u"LAT0": u"No-load.",
        u"PDR10": u"Low-load, 10% PDR.",
        u"PDR50": u"Mid-load, 50% PDR.",
        u"PDR90": u"High-load, 90% PDR.",
        u"PDR": u"Full-load, 100% PDR.",
        u"NDR10": u"Low-load, 10% NDR.",
        u"NDR50": u"Mid-load, 50% NDR.",
        u"NDR90": u"High-load, 90% NDR.",
        u"NDR": u"Full-load, 100% NDR."
    }

    graphs = [
        u"LAT0",
        u"PDR10",
        u"PDR50",
        u"PDR90"
    ]

    file_links = plot.get(u"output-file-links", None)
    target_links = plot.get(u"target-links", None)

    for test in data:
        try:
            if test[u"type"] not in (u"NDRPDR",):
                logging.warning(f"Invalid test type: {test[u'type']}")
                continue
            name = re.sub(REGEX_NIC, u"", test[u"parent"].
                          replace(u'-ndrpdr', u'').replace(u'2n1l-', u''))
            try:
                nic = re.search(REGEX_NIC, test[u"parent"]).group(1)
            except (IndexError, AttributeError, KeyError, ValueError):
                nic = u""
            name_link = f"{nic}-{test[u'name']}".replace(u'-ndrpdr', u'')

            logging.info(f"    Generating the graph: {name_link}")

            fig = plgo.Figure()
            layout = deepcopy(plot[u"layout"])

            for color, graph in enumerate(graphs):
                for idx, direction in enumerate((u"direction1", u"direction2")):
                    previous_x = 0.0
                    prev_perc = 0.0
                    xaxis = list()
                    yaxis = list()
                    hovertext = list()
                    try:
                        decoded = hdrh.histogram.HdrHistogram.decode(
                            test[u"latency"][graph][direction][u"hdrh"]
                        )
                    except hdrh.codec.HdrLengthException:
                        logging.warning(
                            f"No data for direction {(u'W-E', u'E-W')[idx % 2]}"
                        )
                        continue

                    for item in decoded.get_recorded_iterator():
                        # The real value is "percentile".
                        # For 100%, we cut that down to "x_perc" to avoid
                        # infinity.
                        percentile = item.percentile_level_iterated_to
                        x_perc = min(percentile, PERCENTILE_MAX)
                        xaxis.append(previous_x)
                        yaxis.append(item.value_iterated_to)
                        hovertext.append(
                            f"<b>{desc[graph]}</b><br>"
                            f"Direction: {(u'W-E', u'E-W')[idx % 2]}<br>"
                            f"Percentile: {prev_perc:.5f}-{percentile:.5f}%<br>"
                            f"Latency: {item.value_iterated_to}uSec"
                        )
                        next_x = 100.0 / (100.0 - x_perc)
                        xaxis.append(next_x)
                        yaxis.append(item.value_iterated_to)
                        hovertext.append(
                            f"<b>{desc[graph]}</b><br>"
                            f"Direction: {(u'W-E', u'E-W')[idx % 2]}<br>"
                            f"Percentile: {prev_perc:.5f}-{percentile:.5f}%<br>"
                            f"Latency: {item.value_iterated_to}uSec"
                        )
                        previous_x = next_x
                        prev_perc = percentile
                    fig.add_trace(
                        plgo.Scatter(
                            x=xaxis,
                            y=yaxis,
                            name=desc[graph],
                            mode=u"lines",
                            legendgroup=desc[graph],
                            showlegend=not(bool(idx)),
                            line=dict(
                                color=COLORS[color],
                                dash=u"solid",
                                width=1 if idx % 2 else 2
                            ),
                            hovertext=hovertext,
                            hoverinfo=u"text"
                        )
                    )

            layout[u"title"][u"text"] = f"<b>Latency:</b> {name}"
            x_max = log(100.0 / (100.0 - PERCENTILE_MAX), 10)
            layout[u"xaxis"][u"range"] = [0, x_max]
            fig.update_layout(layout)

            # Create plot
            file_name = f"{plot[u'output-file']}-{name_link}.html"
            logging.info(f"    Writing file {file_name}")

            try:
                # Export Plot
                ploff.plot(fig, show_link=False, auto_open=False,
                           filename=file_name)
                # Add link to the file:
                if file_links and target_links:
                    with open(file_links, u"a") as file_handler:
                        file_handler.write(
                            f"- `{name_link} "
                            f"<{target_links}/{file_name.split(u'/')[-1]}>`_\n"
                        )
            except FileNotFoundError as err:
                logging.error(
                    f"Not possible to write the link to the file "
                    f"{file_links}\n{err}"
                )
            except PlotlyError as err:
                logging.error(f"   Finished with error: {repr(err)}")

        except hdrh.codec.HdrLengthException as err:
            logging.warning(repr(err))
            continue

        except (ValueError, KeyError) as err:
            logging.warning(repr(err))
            continue


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

    for core in plot.get(u"core", tuple()):
        # Prepare the data for the plot
        y_vals = OrderedDict()
        loss = dict()
        for item in plot.get(u"include", tuple()):
            reg_ex = re.compile(str(item.format(core=core)).lower())
            for job in data:
                for build in job:
                    for test_id, test in build.iteritems():
                        if not re.match(reg_ex, str(test_id).lower()):
                            continue
                        if y_vals.get(test[u"parent"], None) is None:
                            y_vals[test[u"parent"]] = list()
                            loss[test[u"parent"]] = list()
                        try:
                            y_vals[test[u"parent"]].append(
                                test[u"result"][u"time"]
                            )
                            loss[test[u"parent"]].append(
                                test[u"result"][u"loss"]
                            )
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
            tst_name = re.sub(
                REGEX_NIC, u"",
                col.lower().replace(u'-reconf', u'').replace(u'2n1l-', u'').
                replace(u'2n-', u'').replace(u'-testpmd', u'')
            )
            traces.append(plgo.Box(
                x=[str(i + 1) + u'.'] * len(df_y[col]),
                y=df_y[col],
                name=(
                    f"{i + 1}. "
                    f"({nr_of_samples[i]:02d} "
                    f"run{u's' if nr_of_samples[i] > 1 else u''}, "
                    f"packets lost average: {mean(loss[col]):.1f}) "
                    f"{u'-'.join(tst_name.split(u'-')[2:])}"
                ),
                hoverinfo=u"y+name"
            ))
        try:
            # Create plot
            layout = deepcopy(plot[u"layout"])
            layout[u"title"] = f"<b>Time Lost:</b> {layout[u'title']}"
            layout[u"yaxis"][u"title"] = u"<b>Effective Blocked Time [s]</b>"
            layout[u"legend"][u"font"][u"size"] = 14
            layout[u"yaxis"].pop(u"range")
            plpl = plgo.Figure(data=traces, layout=layout)

            # Export Plot
            file_name = f"{plot[u'output-file'].format(core=core)}.html"
            logging.info(f"    Writing file {file_name}")
            ploff.plot(
                plpl,
                show_link=False,
                auto_open=False,
                filename=file_name
            )
        except PlotlyError as err:
            logging.error(
                f"   Finished with error: {repr(err)}".replace(u"\n", u" ")
            )


def plot_perf_box_name(plot, input_data):
    """Generate the plot(s) with algorithm: plot_perf_box_name
    specified in the specification file.

    Use only for soak and hoststack tests.

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
        plot,
        params=[u"throughput", u"gbps", u"result", u"parent", u"tags", u"type"])
    if data is None:
        logging.error(u"No data.")
        return

    # Prepare the data for the plot
    y_vals = OrderedDict()
    test_type = u""

    for item in plot.get(u"include", tuple()):
        reg_ex = re.compile(str(item).lower())
        for job in data:
            for build in job:
                for test_id, test in build.iteritems():
                    if not re.match(reg_ex, str(test_id).lower()):
                        continue
                    if y_vals.get(test[u"parent"], None) is None:
                        y_vals[test[u"parent"]] = list()
                    try:
                        if test[u"type"] in (u"SOAK",):
                            y_vals[test[u"parent"]]. \
                                append(test[u"throughput"][u"LOWER"])
                            test_type = u"SOAK"

                        elif test[u"type"] in (u"HOSTSTACK",):
                            if u"LDPRELOAD" in test[u"tags"]:
                                y_vals[test[u"parent"]].append(
                                    float(
                                        test[u"result"][u"bits_per_second"]
                                    ) / 1e3
                                )
                            elif u"VPPECHO" in test[u"tags"]:
                                y_vals[test[u"parent"]].append(
                                    (float(
                                        test[u"result"][u"client"][u"tx_data"]
                                    ) * 8 / 1e3) /
                                    ((float(
                                        test[u"result"][u"client"][u"time"]
                                    ) +
                                      float(
                                          test[u"result"][u"server"][u"time"])
                                      ) / 2)
                                )
                            test_type = u"HOSTSTACK"

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
        kwargs = dict(
            x=[str(i + 1) + u'.'] * len(df_y[col]),
            y=[y / 1e6 if y else None for y in df_y[col]],
            name=(
                f"{i + 1}. "
                f"({nr_of_samples[i]:02d} "
                f"run{u's' if nr_of_samples[i] > 1 else u''}) "
                f"{tst_name}"
            ),
            hoverinfo=u"y+name"
        )
        if test_type in (u"SOAK", ):
            kwargs[u"boxpoints"] = u"all"

        traces.append(plgo.Box(**kwargs))

        try:
            val_max = max(df_y[col])
            if val_max:
                y_max.append(int(val_max / 1e6) + 2)
        except (ValueError, TypeError) as err:
            logging.error(repr(err))
            continue

    try:
        # Create plot
        layout = deepcopy(plot[u"layout"])
        if layout.get(u"title", None):
            if test_type in (u"HOSTSTACK", ):
                layout[u"title"] = f"<b>Bandwidth:</b> {layout[u'title']}"
            else:
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


def plot_ndrpdr_box_name(plot, input_data):
    """Generate the plot(s) with algorithm: plot_ndrpdr_box_name
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
        plot,
        params=[u"throughput", u"gbps", u"result", u"parent", u"tags", u"type"]
    )
    if data is None:
        logging.error(u"No data.")
        return

    if u"-gbps" in plot.get(u"title", u"").lower():
        value = u"gbps"
        multiplier = 1e6
    else:
        value = u"throughput"
        multiplier = 1.0

    test_type = u""

    for ttype in plot.get(u"test-type", (u"ndr", u"pdr")):
        for core in plot.get(u"core", tuple()):
            # Prepare the data for the plot
            data_x = list()
            data_y = OrderedDict()
            data_y_max = list()
            idx = 1
            for item in plot.get(u"include", tuple()):
                reg_ex = re.compile(str(item.format(core=core)).lower())
                for job in data:
                    for build in job:
                        for test_id, test in build.iteritems():
                            if not re.match(reg_ex, str(test_id).lower()):
                                continue
                            if data_y.get(test[u"parent"], None) is None:
                                data_y[test[u"parent"]] = list()
                                test_type = test[u"type"]
                                data_x.append(idx)
                                idx += 1
                            try:
                                data_y[test[u"parent"]].append(
                                    test[value][ttype.upper()][u"LOWER"] *
                                    multiplier
                                )
                            except (KeyError, TypeError):
                                pass

            # Add plot traces
            traces = list()
            for idx, (key, vals) in enumerate(data_y.items()):
                name = re.sub(
                    REGEX_NIC, u'', key.lower().replace(u'-ndrpdr', u'').
                    replace(u'2n1l-', u'')
                )
                traces.append(
                    plgo.Box(
                        x=[data_x[idx], ] * len(data_x),
                        y=[y / 1e6 if y else None for y in vals],
                        name=(
                            f"{idx+1}."
                            f"({len(vals):02d} "
                            f"run"
                            f"{u's' if len(vals) > 1 else u''}) "
                            f"{name}"
                        ),
                        hoverinfo=u"y+name"
                    )
                )
                data_y_max.append(max(vals))

            try:
                # Create plot
                layout = deepcopy(plot[u"layout"])
                if layout.get(u"title", None):
                    layout[u"title"] = \
                        layout[u'title'].format(core=core, test_type=ttype)
                    if test_type in (u"CPS", ):
                        layout[u"title"] = f"<b>CPS:</b> {layout[u'title']}"
                    else:
                        layout[u"title"] = \
                            f"<b>Throughput:</b> {layout[u'title']}"
                if data_y_max:
                    layout[u"yaxis"][u"range"] = [0, max(data_y_max) / 1e6 + 1]
                plpl = plgo.Figure(data=traces, layout=layout)

                # Export Plot
                file_name = (
                    f"{plot[u'output-file'].format(core=core, test_type=ttype)}"
                    f".html"
                )
                logging.info(f"    Writing file {file_name}")
                ploff.plot(
                    plpl,
                    show_link=False,
                    auto_open=False,
                    filename=file_name
                )
            except PlotlyError as err:
                logging.error(
                    f"   Finished with error: {repr(err)}".replace(u"\n", u" ")
                )


def plot_mrr_box_name(plot, input_data):
    """Generate the plot(s) with algorithm: plot_mrr_box_name
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
        plot,
        params=[u"result", u"parent", u"tags", u"type"]
    )
    if data is None:
        logging.error(u"No data.")
        return

    for core in plot.get(u"core", tuple()):
        # Prepare the data for the plot
        data_x = list()
        data_names = list()
        data_y = list()
        data_y_max = list()
        idx = 1
        for item in plot.get(u"include", tuple()):
            reg_ex = re.compile(str(item.format(core=core)).lower())
            for job in data:
                for build in job:
                    for test_id, test in build.iteritems():
                        if not re.match(reg_ex, str(test_id).lower()):
                            continue
                        try:
                            data_x.append(idx)
                            name = re.sub(
                                REGEX_NIC, u'', test[u'parent'].lower().
                                replace(u'-mrr', u'').replace(u'2n1l-', u'')
                            )
                            data_y.append(test[u"result"][u"samples"])
                            data_names.append(
                                f"{idx}."
                                f"({len(data_y[-1]):02d} "
                                f"run{u's' if len(data_y[-1]) > 1 else u''}) "
                                f"{name}"
                            )
                            data_y_max.append(max(data_y[-1]))
                            idx += 1
                        except (KeyError, TypeError):
                            pass

        # Add plot traces
        traces = list()
        for idx in range(len(data_x)):
            traces.append(
                plgo.Box(
                    x=[data_x[idx], ] * len(data_y[idx]),
                    y=data_y[idx],
                    name=data_names[idx],
                    hoverinfo=u"y+name"
                )
            )

        try:
            # Create plot
            layout = deepcopy(plot[u"layout"])
            if layout.get(u"title", None):
                layout[u"title"] = (
                    f"<b>Throughput:</b> {layout[u'title'].format(core=core)}"
                )
            if data_y_max:
                layout[u"yaxis"][u"range"] = [0, max(data_y_max) + 1]
            plpl = plgo.Figure(data=traces, layout=layout)

            # Export Plot
            file_name = f"{plot[u'output-file'].format(core=core)}.html"
            logging.info(f"    Writing file {file_name}")
            ploff.plot(
                plpl,
                show_link=False,
                auto_open=False,
                filename=file_name
            )
        except PlotlyError as err:
            logging.error(
                f"   Finished with error: {repr(err)}".replace(u"\n", u" ")
            )


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
        plot,
        params=[u"throughput", u"gbps", u"parent", u"tags", u"type"]
    )
    if data is None:
        logging.error(u"No data.")
        return

    plot_title = plot_title.lower()

    if u"-gbps" in plot_title:
        value = u"gbps"
        h_unit = u"Gbps"
        multiplier = 1e6
    else:
        value = u"throughput"
        h_unit = u"Mpps"
        multiplier = 1.0

    for ttype in plot.get(u"test-type", (u"ndr", u"pdr")):
        y_vals = OrderedDict()
        for item in plot.get(u"include", tuple()):
            reg_ex = re.compile(str(item).lower())
            for job in data:
                for build in job:
                    for test_id, test in build.iteritems():
                        if re.match(reg_ex, str(test_id).lower()):
                            if y_vals.get(test[u"parent"], None) is None:
                                y_vals[test[u"parent"]] = {
                                    u"1": list(),
                                    u"2": list(),
                                    u"4": list()
                                }
                            try:
                                if test[u"type"] not in (u"NDRPDR", u"CPS"):
                                    continue

                                if u"1C" in test[u"tags"]:
                                    y_vals[test[u"parent"]][u"1"].append(
                                        test[value][ttype.upper()][u"LOWER"] *
                                        multiplier
                                    )
                                elif u"2C" in test[u"tags"]:
                                    y_vals[test[u"parent"]][u"2"].append(
                                        test[value][ttype.upper()][u"LOWER"] *
                                        multiplier
                                    )
                                elif u"4C" in test[u"tags"]:
                                    y_vals[test[u"parent"]][u"4"].append(
                                        test[value][ttype.upper()][u"LOWER"] *
                                        multiplier
                                    )
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
                    ideal = avg_val / (int(key) * 1e6)
                    if test_name not in y_1c_max or ideal > y_1c_max[test_name]:
                        y_1c_max[test_name] = ideal

        vals = OrderedDict()
        y_max = list()
        nic_limit = 0
        lnk_limit = 0
        pci_limit = 0
        for test_name, test_vals in y_vals.items():
            try:
                if test_vals[u"1"][1]:
                    name = re.sub(
                        REGEX_NIC,
                        u"",
                        test_name.replace(u'-ndrpdr', u'').
                            replace(u'2n1l-', u'')
                    )
                    vals[name] = OrderedDict()
                    y_val_1 = test_vals[u"1"][0] / 1e6
                    y_val_2 = test_vals[u"2"][0] / 1e6 if test_vals[u"2"][0] \
                        else None
                    y_val_4 = test_vals[u"4"][0] / 1e6 if test_vals[u"4"][0] \
                        else None

                    vals[name][u"val"] = [y_val_1, y_val_2, y_val_4]
                    vals[name][u"rel"] = [1.0, None, None]
                    vals[name][u"ideal"] = [
                        y_1c_max[test_name],
                        y_1c_max[test_name] * 2,
                        y_1c_max[test_name] * 4
                    ]
                    vals[name][u"diff"] = [
                        (y_val_1 - y_1c_max[test_name]) * 100 / y_val_1,
                        None,
                        None
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
            elif u"cx556a" in test_name:
                limit = plot[u"limits"][u"nic"][u"cx556a"]
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

            if u"cx556a" in test_name:
                limit = plot[u"limits"][u"pci"][u"pci-g3-x8"]
            else:
                limit = plot[u"limits"][u"pci"][u"pci-g3-x16"]
            if limit > pci_limit:
                pci_limit = limit

        traces = list()
        annotations = list()
        x_vals = [1, 2, 4]

        # Limits:
        if u"-gbps" not in plot_title and u"-cps-" not in plot_title:
            nic_limit /= 1e6
            lnk_limit /= 1e6
            pci_limit /= 1e6
            min_limit = min((nic_limit, lnk_limit, pci_limit))
            if nic_limit == min_limit:
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
            elif lnk_limit == min_limit:
                traces.append(plgo.Scatter(
                    x=x_vals,
                    y=[lnk_limit, ] * len(x_vals),
                    name=f"Link: {lnk_limit:.2f}Mpps",
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
                    y=lnk_limit,
                    xref=u"x",
                    yref=u"y",
                    xanchor=u"left",
                    yanchor=u"bottom",
                    text=f"Link: {lnk_limit:.2f}Mpps",
                    font=dict(
                        size=14,
                        color=COLORS[-1],
                    ),
                    align=u"left",
                    showarrow=False
                ))
                y_max.append(lnk_limit)
            elif pci_limit == min_limit:
                traces.append(plgo.Scatter(
                    x=x_vals,
                    y=[pci_limit, ] * len(x_vals),
                    name=f"PCIe: {pci_limit:.2f}Mpps",
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
                    y=pci_limit,
                    xref=u"x",
                    yref=u"y",
                    xanchor=u"left",
                    yanchor=u"bottom",
                    text=f"PCIe: {pci_limit:.2f}Mpps",
                    font=dict(
                        size=14,
                        color=COLORS[-1],
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
                            f"Mean: {val[u'val'][idx]:.2f}{h_unit}<br>"
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
            file_name = f"{plot[u'output-file'].format(test_type=ttype)}.html"
            logging.info(f"    Writing file {file_name}")
            layout = deepcopy(plot[u"layout"])
            if layout.get(u"title", None):
                layout[u"title"] = (
                    f"<b>Speedup Multi-core:</b> "
                    f"{layout[u'title'].format(test_type=ttype)}"
                )
            layout[u"yaxis"][u"range"] = [0, int(max(y_max) * 1.1)]
            layout[u"annotations"].extend(annotations)
            plpl = plgo.Figure(data=traces, layout=layout)

            # Export Plot
            ploff.plot(
                plpl,
                show_link=False,
                auto_open=False,
                filename=file_name
            )
        except PlotlyError as err:
            logging.error(
                f"   Finished with error: {repr(err)}".replace(u"\n", u" ")
            )


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
            name_lst = name.split(u'-')
            name = u""
            split_name = True
            for segment in name_lst:
                if (len(name) + len(segment) + 1) > 50 and split_name:
                    name += u"<br>    "
                    split_name = False
                name += segment + u'-'
            name = name[:-1]

        traces.append(plgo.Box(x=[str(i + 1) + u'.'] * len(df_y[col]),
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

    def sort_by_int(value):
        """Makes possible to sort a list of strings which represent integers.

        :param value: Integer as a string.
        :type value: str
        :returns: Integer representation of input parameter 'value'.
        :rtype: int
        """
        return int(value)

    regex_cn = re.compile(r'^(\d*)R(\d*)C$')
    regex_test_name = re.compile(r'^.*-(\d+ch|\d+pl)-'
                                 r'(\d+mif|\d+vh)-'
                                 r'(\d+vm\d+t|\d+dcr\d+t|\d+dcr\d+c).*$')
    vals = dict()

    # Transform the data
    logging.info(
        f"    Creating the data set for the {plot.get(u'type', u'')} "
        f"{plot.get(u'title', u'')}."
    )
    in_data = input_data.filter_tests_by_name(
        plot,
        continue_on_error=True,
        params=[u"throughput", u"result", u"name", u"tags", u"type"]
    )
    if in_data is None or in_data.empty:
        logging.error(u"No data.")
        return

    for ttype in plot.get(u"test-type", (u"ndr", u"pdr")):
        for core in plot.get(u"core", tuple()):
            for item in plot.get(u"include", tuple()):
                reg_ex = re.compile(str(item.format(core=core)).lower())
                for job in in_data:
                    for build in job:
                        for test_id, test in build.iteritems():
                            if not re.match(reg_ex, str(test_id).lower()):
                                continue
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
                                if ttype == u"mrr":
                                    result = test[u"result"][u"receive-rate"]
                                elif ttype == u"pdr":
                                    result = \
                                        test[u"throughput"][u"PDR"][u"LOWER"]
                                elif ttype == u"ndr":
                                    result = \
                                        test[u"throughput"][u"NDR"][u"LOWER"]
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
                        vals[key_c][key_n][u"nr"] = \
                            len(vals[key_c][key_n][u"vals"])
                        vals[key_c][key_n][u"mean"] = \
                            round(mean(vals[key_c][key_n][u"vals"]) / 1e6, 1)
                        vals[key_c][key_n][u"stdev"] = \
                            round(stdev(vals[key_c][key_n][u"vals"]) / 1e6, 1)
            txt_nodes = list(set(txt_nodes))

            txt_chains = sorted(txt_chains, key=sort_by_int)
            txt_nodes = sorted(txt_nodes, key=sort_by_int)

            chains = [i + 1 for i in range(len(txt_chains))]
            nodes = [i + 1 for i in range(len(txt_nodes))]

            data = [list() for _ in range(len(chains))]
            for chain in chains:
                for node in nodes:
                    try:
                        val = vals[txt_chains[chain - 1]] \
                            [txt_nodes[node - 1]][u"mean"]
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
                            name=vals[txt_chains[chain]][txt_nodes[node]]
                            [u"name"],
                            nr=vals[txt_chains[chain]][txt_nodes[node]][u"nr"],
                            val=data[chain][node],
                            stdev=vals[txt_chains[chain]][txt_nodes[node]]
                            [u"stdev"]
                        ))
                hovertext.append(hover_line)

            traces = [
                plgo.Heatmap(
                    x=nodes,
                    y=chains,
                    z=data,
                    colorbar=dict(
                        title=plot.get(u"z-axis", u"{test_type}").
                        format(test_type=ttype.upper()),
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
                logging.error(
                    f"Finished with error: No layout defined\n{repr(err)}"
                )
                return

            layout[u"annotations"] = annotations
            layout[u'updatemenus'] = updatemenus
            if layout.get(u"title", None):
                layout[u"title"] = layout[u'title'].replace(u"test_type", ttype)

            try:
                # Create plot
                plpl = plgo.Figure(data=traces, layout=layout)

                # Export Plot
                file_name = (
                    f"{plot[u'output-file'].format(core=core, test_type=ttype)}"
                    f".html"
                )
                logging.info(f"    Writing file {file_name}")
                ploff.plot(
                    plpl,
                    show_link=False,
                    auto_open=False,
                    filename=file_name
                )
            except PlotlyError as err:
                logging.error(
                    f"   Finished with error: {repr(err)}".replace(u"\n", u" ")
                )
