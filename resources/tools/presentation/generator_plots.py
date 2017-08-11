# Copyright (c) 2017 Cisco and/or its affiliates.
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
    index = 0
    for plot in spec.plots:
        index += 1
        try:
            logging.info("  Plot nr {0}:".format(index))
            eval(plot["algorithm"])(plot, data)
        except NameError:
            logging.error("The algorithm '{0}' is not defined.".
                          format(plot["algorithm"]))
    logging.info("Done.")


def plot_performance_box(plot, input_data):
    """Generate the plot(s) with algorithm: table_detailed_test_results
    specified in the specification file.

    :param plot: Plot to generate.
    :param input_data: Data to process.
    :type plot: pandas.Series
    :type input_data: InputData
    """

    logging.info("  Generating the plot {0} ...".
                 format(plot.get("title", "")))

    # Transform the data
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
                    y_vals[test["parent"]].append(test["throughput"]["value"])
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
        name = "{0}. {1}".format(i + 1, col.lower().replace('-ndrpdrdisc', ''))
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
        name = "{0}. {1}".format(i + 1, col.lower().replace('-ndrpdrdisc', ''))
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
