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

import multiprocessing
import os
import logging
import csv
import prettytable
import plotly.offline as ploff
import plotly.graph_objs as plgo
import plotly.exceptions as plerr

from collections import OrderedDict
from datetime import datetime

from utils import archive_input_data, execute_command, \
    classify_anomalies, Worker


# Command to build the html format of the report
HTML_BUILDER = 'sphinx-build -v -c conf_cpta -a ' \
               '-b html -E ' \
               '-t html ' \
               '-D version="{date}" ' \
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
        date=datetime.utcnow().strftime('%m/%d/%Y %H:%M UTC'),
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


def _generate_trending_traces(in_data, job_name, build_info,
                              show_trend_line=True, name="", color=""):
    """Generate the trending traces:
     - samples,
     - outliers, regress, progress
     - average of normal samples (trending line)

    :param in_data: Full data set.
    :param job_name: The name of job which generated the data.
    :param build_info: Information about the builds.
    :param show_trend_line: Show moving median (trending plot).
    :param name: Name of the plot
    :param color: Name of the color for the plot.
    :type in_data: OrderedDict
    :type job_name: str
    :type build_info: dict
    :type show_trend_line: bool
    :type name: str
    :type color: str
    :returns: Generated traces (list) and the evaluated result.
    :rtype: tuple(traces, result)
    """

    data_x = list(in_data.keys())
    data_y = list(in_data.values())

    hover_text = list()
    xaxis = list()
    for idx in data_x:
        date = build_info[job_name][str(idx)][0]
        hover_str = ("date: {0}<br>"
                     "value: {1:,}<br>"
                     "{2}-ref: {3}<br>"
                     "csit-ref: mrr-{4}-build-{5}")
        if "dpdk" in job_name:
            hover_text.append(hover_str.format(
                date,
                int(in_data[idx].avg),
                "dpdk",
                build_info[job_name][str(idx)][1].
                rsplit('~', 1)[0],
                "weekly",
                idx))
        elif "vpp" in job_name:
            hover_text.append(hover_str.format(
                date,
                int(in_data[idx].avg),
                "vpp",
                build_info[job_name][str(idx)][1].
                rsplit('~', 1)[0],
                "daily",
                idx))

        xaxis.append(datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]),
                              int(date[9:11]), int(date[12:])))

    data_pd = OrderedDict()
    for key, value in zip(xaxis, data_y):
        data_pd[key] = value

    anomaly_classification, avgs = classify_anomalies(data_pd)

    anomalies = OrderedDict()
    anomalies_colors = list()
    anomalies_avgs = list()
    anomaly_color = {
        "regression": 0.0,
        "normal": 0.5,
        "progression": 1.0
    }
    if anomaly_classification:
        for idx, (key, value) in enumerate(data_pd.iteritems()):
            if anomaly_classification[idx] in \
                    ("outlier", "regression", "progression"):
                anomalies[key] = value
                anomalies_colors.append(
                    anomaly_color[anomaly_classification[idx]])
                anomalies_avgs.append(avgs[idx])
        anomalies_colors.extend([0.0, 0.5, 1.0])

    # Create traces

    trace_samples = plgo.Scatter(
        x=xaxis,
        y=[y.avg for y in data_y],
        mode='markers',
        line={
            "width": 1
        },
        showlegend=True,
        legendgroup=name,
        name="{name}".format(name=name),
        marker={
            "size": 5,
            "color": color,
            "symbol": "circle",
        },
        text=hover_text,
        hoverinfo="text"
    )
    traces = [trace_samples, ]

    if show_trend_line:
        trace_trend = plgo.Scatter(
            x=xaxis,
            y=avgs,
            mode='lines',
            line={
                "shape": "linear",
                "width": 1,
                "color": color,
            },
            showlegend=False,
            legendgroup=name,
            name='{name}'.format(name=name),
            text=["trend: {0:,}".format(int(avg)) for avg in avgs],
            hoverinfo="text+name"
        )
        traces.append(trace_trend)

    trace_anomalies = plgo.Scatter(
        x=anomalies.keys(),
        y=anomalies_avgs,
        mode='markers',
        hoverinfo="none",
        showlegend=False,
        legendgroup=name,
        name="{name}-anomalies".format(name=name),
        marker={
            "size": 15,
            "symbol": "circle-open",
            "color": anomalies_colors,
            "colorscale": [[0.00, "red"],
                           [0.33, "red"],
                           [0.33, "white"],
                           [0.66, "white"],
                           [0.66, "green"],
                           [1.00, "green"]],
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
                "tickvals": [0.167, 0.500, 0.833],
                "ticktext": ["Regression", "Normal", "Progression"],
                "ticks": "",
                "ticklen": 0,
                "tickangle": -90,
                "thickness": 10
            }
        }
    )
    traces.append(trace_anomalies)

    if anomaly_classification:
        return traces, anomaly_classification[-1]
    else:
        return traces, None


def _generate_all_charts(spec, input_data):
    """Generate all charts specified in the specification file.

    :param spec: Specification.
    :param input_data: Full data set.
    :type spec: Specification
    :type input_data: InputData
    """

    def _generate_chart(_, data_q, graph):
        """Generates the chart.
        """

        logs = list()

        logging.info("  Generating the chart '{0}' ...".
                     format(graph.get("title", "")))
        logs.append(("INFO", "  Generating the chart '{0}' ...".
                     format(graph.get("title", ""))))

        job_name = graph["data"].keys()[0]

        csv_tbl = list()
        res = list()

        # Transform the data
        logs.append(("INFO", "    Creating the data set for the {0} '{1}'.".
                     format(graph.get("type", ""), graph.get("title", ""))))
        data = input_data.filter_data(graph, continue_on_error=True)
        if data is None:
            logging.error("No data.")
            return

        chart_data = dict()
        for job, job_data in data.iteritems():
            if job != job_name:
                continue
            for index, bld in job_data.items():
                for test_name, test in bld.items():
                    if chart_data.get(test_name, None) is None:
                        chart_data[test_name] = OrderedDict()
                    try:
                        chart_data[test_name][int(index)] = test["result"]
                    except (KeyError, TypeError):
                        pass

        # Add items to the csv table:
        for tst_name, tst_data in chart_data.items():
            tst_lst = list()
            for bld in builds_dict[job_name]:
                itm = tst_data.get(int(bld), '')
                if not isinstance(itm, str):
                    itm = itm.avg
                tst_lst.append(str(itm))
            csv_tbl.append("{0},".format(tst_name) + ",".join(tst_lst) + '\n')
        # Generate traces:
        traces = list()
        index = 0
        for test_name, test_data in chart_data.items():
            if not test_data:
                logs.append(("WARNING", "No data for the test '{0}'".
                             format(test_name)))
                continue
            test_name = test_name.split('.')[-1]
            trace, rslt = _generate_trending_traces(
                test_data,
                job_name=job_name,
                build_info=build_info,
                name='-'.join(test_name.split('-')[2:-1]),
                color=COLORS[index])
            traces.extend(trace)
            res.append(rslt)
            index += 1

        if traces:
            # Generate the chart:
            graph["layout"]["xaxis"]["title"] = \
                graph["layout"]["xaxis"]["title"].format(job=job_name)
            name_file = "{0}-{1}{2}".format(spec.cpta["output-file"],
                                            graph["output-file-name"],
                                            spec.cpta["output-file-type"])

            logs.append(("INFO", "    Writing the file '{0}' ...".
                         format(name_file)))
            plpl = plgo.Figure(data=traces, layout=graph["layout"])
            try:
                ploff.plot(plpl, show_link=False, auto_open=False,
                           filename=name_file)
            except plerr.PlotlyEmptyDataError:
                logs.append(("WARNING", "No data for the plot. Skipped."))

        data_out = {
            "job_name": job_name,
            "csv_table": csv_tbl,
            "results": res,
            "logs": logs
        }
        data_q.put(data_out)

    builds_dict = dict()
    for job in spec.input["builds"].keys():
        if builds_dict.get(job, None) is None:
            builds_dict[job] = list()
        for build in spec.input["builds"][job]:
            status = build["status"]
            if status != "failed" and status != "not found":
                builds_dict[job].append(str(build["build"]))

    # Create "build ID": "date" dict:
    build_info = dict()
    for job_name, job_data in builds_dict.items():
        if build_info.get(job_name, None) is None:
            build_info[job_name] = OrderedDict()
        for build in job_data:
            build_info[job_name][build] = (
                input_data.metadata(job_name, build).get("generated", ""),
                input_data.metadata(job_name, build).get("version", "")
            )

    work_queue = multiprocessing.JoinableQueue()
    manager = multiprocessing.Manager()
    data_queue = manager.Queue()
    cpus = multiprocessing.cpu_count()

    workers = list()
    for cpu in range(cpus):
        worker = Worker(work_queue,
                        data_queue,
                        _generate_chart)
        worker.daemon = True
        worker.start()
        workers.append(worker)
        os.system("taskset -p -c {0} {1} > /dev/null 2>&1".
                  format(cpu, worker.pid))

    for chart in spec.cpta["plots"]:
        work_queue.put((chart, ))
    work_queue.join()

    anomaly_classifications = list()

    # Create the header:
    csv_tables = dict()
    for job_name in builds_dict.keys():
        if csv_tables.get(job_name, None) is None:
            csv_tables[job_name] = list()
        header = "Build Number:," + ",".join(builds_dict[job_name]) + '\n'
        csv_tables[job_name].append(header)
        build_dates = [x[0] for x in build_info[job_name].values()]
        header = "Build Date:," + ",".join(build_dates) + '\n'
        csv_tables[job_name].append(header)
        versions = [x[1] for x in build_info[job_name].values()]
        header = "Version:," + ",".join(versions) + '\n'
        csv_tables[job_name].append(header)

    while not data_queue.empty():
        result = data_queue.get()

        anomaly_classifications.extend(result["results"])
        csv_tables[result["job_name"]].extend(result["csv_table"])

        for item in result["logs"]:
            if item[0] == "INFO":
                logging.info(item[1])
            elif item[0] == "ERROR":
                logging.error(item[1])
            elif item[0] == "DEBUG":
                logging.debug(item[1])
            elif item[0] == "CRITICAL":
                logging.critical(item[1])
            elif item[0] == "WARNING":
                logging.warning(item[1])

    del data_queue

    # Terminate all workers
    for worker in workers:
        worker.terminate()
        worker.join()

    # Write the tables:
    for job_name, csv_table in csv_tables.items():
        file_name = spec.cpta["output-file"] + "-" + job_name + "-trending"
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
                        logging.warning("Error occurred while generating TXT "
                                        "table:\n{0}".format(err))
                line_nr += 1
            txt_table.align["Build Number:"] = "l"
        with open("{0}.txt".format(file_name), "w") as txt_file:
            txt_file.write(str(txt_table))

    # Evaluate result:
    if anomaly_classifications:
        result = "PASS"
        for classification in anomaly_classifications:
            if classification == "regression" or classification == "outlier":
                result = "FAIL"
                break
    else:
        result = "FAIL"

    logging.info("Partial results: {0}".format(anomaly_classifications))
    logging.info("Result: {0}".format(result))

    return result
