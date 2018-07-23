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

from utils import mean


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
    for job in data:
        for build in job:
            for test in build:
                if y_vals.get(test["parent"], None) is None:
                    y_vals[test["parent"]] = list()
                try:
                    # TODO: Remove when definitely no NDRPDRDISC tests are used:
                    if test["type"] in ("NDR", "PDR"):
                        y_vals[test["parent"]].\
                            append(test["throughput"]["value"])
                    elif test["type"] in ("NDRPDR", ):
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
        name = "{0}. {1}".format(i + 1, col.lower().replace('-ndrpdrdisc', '').
                                 replace('-ndrpdr', ''))
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
                try:
                    # TODO: Remove when definitely no NDRPDRDISC tests are used:
                    if test["type"] in ("NDR", "PDR"):
                        y_tmp_vals[test["parent"]][0].append(
                            test["latency"]["direction1"]["50"]["min"])
                        y_tmp_vals[test["parent"]][1].append(
                            test["latency"]["direction1"]["50"]["avg"])
                        y_tmp_vals[test["parent"]][2].append(
                            test["latency"]["direction1"]["50"]["max"])
                        y_tmp_vals[test["parent"]][3].append(
                            test["latency"]["direction2"]["50"]["min"])
                        y_tmp_vals[test["parent"]][4].append(
                            test["latency"]["direction2"]["50"]["avg"])
                        y_tmp_vals[test["parent"]][5].append(
                            test["latency"]["direction2"]["50"]["max"])
                    elif test["type"] in ("NDRPDR", ):
                        if "-pdr" in plot_title.lower():
                            y_tmp_vals[test["parent"]][0].append(
                                test["latency"]["PDR"]["direction1"]["min"])
                            y_tmp_vals[test["parent"]][1].append(
                                test["latency"]["PDR"]["direction1"]["avg"])
                            y_tmp_vals[test["parent"]][2].append(
                                test["latency"]["PDR"]["direction1"]["max"])
                            y_tmp_vals[test["parent"]][3].append(
                                test["latency"]["PDR"]["direction2"]["min"])
                            y_tmp_vals[test["parent"]][4].append(
                                test["latency"]["PDR"]["direction2"]["avg"])
                            y_tmp_vals[test["parent"]][5].append(
                                test["latency"]["PDR"]["direction2"]["max"])
                        elif "-ndr" in plot_title.lower():
                            y_tmp_vals[test["parent"]][0].append(
                                test["latency"]["NDR"]["direction1"]["min"])
                            y_tmp_vals[test["parent"]][1].append(
                                test["latency"]["NDR"]["direction1"]["avg"])
                            y_tmp_vals[test["parent"]][2].append(
                                test["latency"]["NDR"]["direction1"]["max"])
                            y_tmp_vals[test["parent"]][3].append(
                                test["latency"]["NDR"]["direction2"]["min"])
                            y_tmp_vals[test["parent"]][4].append(
                                test["latency"]["NDR"]["direction2"]["avg"])
                            y_tmp_vals[test["parent"]][5].append(
                                test["latency"]["NDR"]["direction2"]["max"])
                        else:
                            continue
                    else:
                        continue
                except (KeyError, TypeError):
                    pass

    y_vals = dict()
    for key, values in y_tmp_vals.items():
        y_vals[key] = list()
        for val in values:
            if val:
                average = mean(val)
            else:
                average = None
            y_vals[key].append(average)
            y_vals[key].append(average)  # Twice for plot.ly

    # Add plot traces
    traces = list()
    try:
        df = pd.DataFrame(y_vals)
        df.head()
    except ValueError as err:
        logging.error("   Finished with error: {}".
                      format(str(err).replace("\n", " ")))
        return

    for i, col in enumerate(df.columns):
        name = "{0}. {1}".format(i + 1, col.lower().replace('-ndrpdrdisc', '').
                                 replace('-ndrpdr', ''))
        traces.append(plgo.Box(x=['TGint1-to-SUT1-to-SUT2-to-TGint2',
                                  'TGint1-to-SUT1-to-SUT2-to-TGint2',
                                  'TGint1-to-SUT1-to-SUT2-to-TGint2',
                                  'TGint1-to-SUT1-to-SUT2-to-TGint2',
                                  'TGint1-to-SUT1-to-SUT2-to-TGint2',
                                  'TGint1-to-SUT1-to-SUT2-to-TGint2',
                                  'TGint2-to-SUT2-to-SUT1-to-TGint1',
                                  'TGint2-to-SUT2-to-SUT1-to-TGint1',
                                  'TGint2-to-SUT2-to-SUT1-to-TGint1',
                                  'TGint2-to-SUT2-to-SUT1-to-TGint1',
                                  'TGint2-to-SUT2-to-SUT1-to-TGint1',
                                  'TGint2-to-SUT2-to-SUT1-to-TGint1'],
                               y=df[col],
                               name=name,
                               **plot["traces"]))

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
                    # TODO: Remove when definitely no NDRPDRDISC tests are used:
                    if test["type"] in ("NDR", "PDR"):
                        if "1T1C" in test["tags"]:
                            throughput[test["parent"]]["1"].\
                                append(test["throughput"]["value"])
                        elif "2T2C" in test["tags"]:
                            throughput[test["parent"]]["2"]. \
                                append(test["throughput"]["value"])
                        elif "4T4C" in test["tags"]:
                            throughput[test["parent"]]["4"]. \
                                append(test["throughput"]["value"])
                    elif test["type"] in ("NDRPDR", ):
                        if "-pdr" in plot_title.lower():
                            if "1T1C" in test["tags"]:
                                throughput[test["parent"]]["1"].\
                                    append(test["throughput"]["PDR"]["LOWER"])
                            elif "2T2C" in test["tags"]:
                                throughput[test["parent"]]["2"]. \
                                    append(test["throughput"]["PDR"]["LOWER"])
                            elif "4T4C" in test["tags"]:
                                throughput[test["parent"]]["4"]. \
                                    append(test["throughput"]["PDR"]["LOWER"])
                        elif "-ndr" in plot_title.lower():
                            if "1T1C" in test["tags"]:
                                throughput[test["parent"]]["1"].\
                                    append(test["throughput"]["NDR"]["LOWER"])
                            elif "2T2C" in test["tags"]:
                                throughput[test["parent"]]["2"]. \
                                    append(test["throughput"]["NDR"]["LOWER"])
                            elif "4T4C" in test["tags"]:
                                throughput[test["parent"]]["4"]. \
                                    append(test["throughput"]["NDR"]["LOWER"])
                        else:
                            continue
                    else:
                        continue
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
