# Copyright (c) 2020 Cisco and/or its affiliates.
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

import re
import logging
import csv

from collections import OrderedDict
from datetime import datetime
from copy import deepcopy

import prettytable
import plotly.offline as ploff
import plotly.graph_objs as plgo
import plotly.exceptions as plerr

from pal_utils import archive_input_data, execute_command, classify_anomalies


# Command to build the html format of the report
HTML_BUILDER = u'sphinx-build -v -c conf_cpta -a ' \
               u'-b html -E ' \
               u'-t html ' \
               u'-D version="{date}" ' \
               u'{working_dir} ' \
               u'{build_dir}/'

# .css file for the html format of the report
THEME_OVERRIDES = u"""/* override table width restrictions */
.wy-nav-content {
    max-width: 1200px !important;
}
.rst-content blockquote {
    margin-left: 0px;
    line-height: 18px;
    margin-bottom: 0px;
}
.wy-menu-vertical a {
    display: inline-block;
    line-height: 18px;
    padding: 0 2em;
    display: block;
    position: relative;
    font-size: 90%;
    color: #d9d9d9
}
.wy-menu-vertical li.current a {
    color: gray;
    border-right: solid 1px #c9c9c9;
    padding: 0 3em;
}
.wy-menu-vertical li.toctree-l2.current > a {
    background: #c9c9c9;
    padding: 0 3em;
}
.wy-menu-vertical li.toctree-l2.current li.toctree-l3 > a {
    display: block;
    background: #c9c9c9;
    padding: 0 4em;
}
.wy-menu-vertical li.toctree-l3.current li.toctree-l4 > a {
    display: block;
    background: #bdbdbd;
    padding: 0 5em;
}
.wy-menu-vertical li.on a, .wy-menu-vertical li.current > a {
    color: #404040;
    padding: 0 2em;
    font-weight: bold;
    position: relative;
    background: #fcfcfc;
    border: none;
        border-top-width: medium;
        border-bottom-width: medium;
        border-top-style: none;
        border-bottom-style: none;
        border-top-color: currentcolor;
        border-bottom-color: currentcolor;
    padding-left: 2em -4px;
}
"""

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


def generate_cpta(spec, data):
    """Generate all formats and versions of the Continuous Performance Trending
    and Analysis.

    :param spec: Specification read from the specification file.
    :param data: Full data set.
    :type spec: Specification
    :type data: InputData
    """

    logging.info(u"Generating the Continuous Performance Trending and Analysis "
                 u"...")

    ret_code = _generate_all_charts(spec, data)

    cmd = HTML_BUILDER.format(
        date=datetime.utcnow().strftime(u'%Y-%m-%d %H:%M UTC'),
        working_dir=spec.environment[u'paths'][u'DIR[WORKING,SRC]'],
        build_dir=spec.environment[u'paths'][u'DIR[BUILD,HTML]'])
    execute_command(cmd)

    with open(spec.environment[u'paths'][u'DIR[CSS_PATCH_FILE]'], u'w') as \
            css_file:
        css_file.write(THEME_OVERRIDES)

    with open(spec.environment[u'paths'][u'DIR[CSS_PATCH_FILE2]'], u'w') as \
            css_file:
        css_file.write(THEME_OVERRIDES)

    if spec.configuration.get(u"archive-inputs", True):
        archive_input_data(spec)

    logging.info(u"Done.")

    return ret_code


def _generate_trending_traces(in_data, job_name, build_info,
                              name=u"", color=u"", incl_tests=u"MRR"):
    """Generate the trending traces:
     - samples,
     - outliers, regress, progress
     - average of normal samples (trending line)

    :param in_data: Full data set.
    :param job_name: The name of job which generated the data.
    :param build_info: Information about the builds.
    :param name: Name of the plot
    :param color: Name of the color for the plot.
    :param incl_tests: Included tests, accepted values: mrr, ndr, pdr
    :type in_data: OrderedDict
    :type job_name: str
    :type build_info: dict
    :type name: str
    :type color: str
    :type incl_tests: str
    :returns: Generated traces (list) and the evaluated result.
    :rtype: tuple(traces, result)
    """

    if incl_tests not in (u"mrr", u"ndr", u"pdr"):
        return list(), None

    data_x = list(in_data.keys())
    data_y_pps = list()
    data_y_mpps = list()
    data_y_stdev = list()
    for item in in_data.values():
        data_y_pps.append(float(item[u"receive-rate"]))
        data_y_stdev.append(float(item[u"receive-stdev"]) / 1e6)
        data_y_mpps.append(float(item[u"receive-rate"]) / 1e6)

    hover_text = list()
    xaxis = list()
    for index, key in enumerate(data_x):
        str_key = str(key)
        date = build_info[job_name][str_key][0]
        hover_str = (u"date: {date}<br>"
                     u"{property} [Mpps]: {value:.3f}<br>"
                     u"<stdev>"
                     u"{sut}-ref: {build}<br>"
                     u"csit-ref: {test}-{period}-build-{build_nr}<br>"
                     u"testbed: {testbed}")
        if incl_tests == u"mrr":
            hover_str = hover_str.replace(
                u"<stdev>", f"stdev [Mpps]: {data_y_stdev[index]:.3f}<br>"
            )
        else:
            hover_str = hover_str.replace(u"<stdev>", u"")
        if u"-cps" in name:
            hover_str = hover_str.replace(u"[Mpps]", u"[Mcps]")
        if u"dpdk" in job_name:
            hover_text.append(hover_str.format(
                date=date,
                property=u"average" if incl_tests == u"mrr" else u"throughput",
                value=data_y_mpps[index],
                sut=u"dpdk",
                build=build_info[job_name][str_key][1].rsplit(u'~', 1)[0],
                test=incl_tests,
                period=u"weekly",
                build_nr=str_key,
                testbed=build_info[job_name][str_key][2]))
        elif u"vpp" in job_name:
            hover_str = hover_str.format(
                date=date,
                property=u"average" if incl_tests == u"mrr" else u"throughput",
                value=data_y_mpps[index],
                sut=u"vpp",
                build=build_info[job_name][str_key][1].rsplit(u'~', 1)[0],
                test=incl_tests,
                period=u"daily" if incl_tests == u"mrr" else u"weekly",
                build_nr=str_key,
                testbed=build_info[job_name][str_key][2])
            if u"-cps" in name:
                hover_str = hover_str.replace(u"throughput", u"connection rate")
            hover_text.append(hover_str)

        xaxis.append(datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]),
                              int(date[9:11]), int(date[12:])))

    data_pd = OrderedDict()
    for key, value in zip(xaxis, data_y_pps):
        data_pd[key] = value

    anomaly_classification, avgs_pps, stdevs_pps = classify_anomalies(data_pd)
    avgs_mpps = [avg_pps / 1e6 for avg_pps in avgs_pps]
    stdevs_mpps = [stdev_pps / 1e6 for stdev_pps in stdevs_pps]

    anomalies = OrderedDict()
    anomalies_colors = list()
    anomalies_avgs = list()
    anomaly_color = {
        u"regression": 0.0,
        u"normal": 0.5,
        u"progression": 1.0
    }
    if anomaly_classification:
        for index, (key, value) in enumerate(data_pd.items()):
            if anomaly_classification[index] in (u"regression", u"progression"):
                anomalies[key] = value / 1e6
                anomalies_colors.append(
                    anomaly_color[anomaly_classification[index]])
                anomalies_avgs.append(avgs_mpps[index])
        anomalies_colors.extend([0.0, 0.5, 1.0])

    # Create traces

    trace_samples = plgo.Scatter(
        x=xaxis,
        y=data_y_mpps,
        mode=u"markers",
        line={
            u"width": 1
        },
        showlegend=True,
        legendgroup=name,
        name=f"{name}",
        marker={
            u"size": 5,
            u"color": color,
            u"symbol": u"circle",
        },
        text=hover_text,
        hoverinfo=u"text+name"
    )
    traces = [trace_samples, ]

    trend_hover_text = list()
    for idx in range(len(data_x)):
        trend_hover_str = (
            f"trend [Mpps]: {avgs_mpps[idx]:.3f}<br>"
            f"stdev [Mpps]: {stdevs_mpps[idx]:.3f}"
        )
        trend_hover_text.append(trend_hover_str)

    trace_trend = plgo.Scatter(
        x=xaxis,
        y=avgs_mpps,
        mode=u"lines",
        line={
            u"shape": u"linear",
            u"width": 1,
            u"color": color,
        },
        showlegend=False,
        legendgroup=name,
        name=f"{name}",
        text=trend_hover_text,
        hoverinfo=u"text+name"
    )
    traces.append(trace_trend)

    trace_anomalies = plgo.Scatter(
        x=list(anomalies.keys()),
        y=anomalies_avgs,
        mode=u"markers",
        hoverinfo=u"none",
        showlegend=False,
        legendgroup=name,
        name=f"{name}-anomalies",
        marker={
            u"size": 15,
            u"symbol": u"circle-open",
            u"color": anomalies_colors,
            u"colorscale": [
                [0.00, u"red"],
                [0.33, u"red"],
                [0.33, u"white"],
                [0.66, u"white"],
                [0.66, u"green"],
                [1.00, u"green"]
            ],
            u"showscale": True,
            u"line": {
                u"width": 2
            },
            u"colorbar": {
                u"y": 0.5,
                u"len": 0.8,
                u"title": u"Circles Marking Data Classification",
                u"titleside": u"right",
                u"titlefont": {
                    u"size": 14
                },
                u"tickmode": u"array",
                u"tickvals": [0.167, 0.500, 0.833],
                u"ticktext": [u"Regression", u"Normal", u"Progression"],
                u"ticks": u"",
                u"ticklen": 0,
                u"tickangle": -90,
                u"thickness": 10
            }
        }
    )
    traces.append(trace_anomalies)

    if anomaly_classification:
        return traces, anomaly_classification[-1]

    return traces, None


def _generate_all_charts(spec, input_data):
    """Generate all charts specified in the specification file.

    :param spec: Specification.
    :param input_data: Full data set.
    :type spec: Specification
    :type input_data: InputData
    """

    def _generate_chart(graph):
        """Generates the chart.

        :param graph: The graph to be generated
        :type graph: dict
        :returns: Dictionary with the job name, csv table with results and
            list of tests classification results.
        :rtype: dict
        """

        logging.info(f"  Generating the chart {graph.get(u'title', u'')} ...")

        job_name = list(graph[u"data"].keys())[0]

        # Transform the data
        logging.info(
            f"    Creating the data set for the {graph.get(u'type', u'')} "
            f"{graph.get(u'title', u'')}."
        )

        data = input_data.filter_tests_by_name(
            graph,
            params=[u"type", u"result", u"throughput", u"tags"],
            continue_on_error=True
        )

        if data is None or data.empty:
            logging.error(u"No data.")
            return dict()

        return_lst = list()

        for ttype in graph.get(u"test-type", (u"mrr", )):
            for core in graph.get(u"core", tuple()):
                csv_tbl = list()
                res = dict()
                chart_data = dict()
                chart_tags = dict()
                for item in graph.get(u"include", tuple()):
                    reg_ex = re.compile(str(item.format(core=core)).lower())
                    for job, job_data in data.items():
                        if job != job_name:
                            continue
                        for index, bld in job_data.items():
                            for test_id, test in bld.items():
                                if not re.match(reg_ex, str(test_id).lower()):
                                    continue
                                if chart_data.get(test_id, None) is None:
                                    chart_data[test_id] = OrderedDict()
                                try:
                                    if ttype == u"mrr":
                                        rate = test[u"result"][u"receive-rate"]
                                        stdev = \
                                            test[u"result"][u"receive-stdev"]
                                    elif ttype == u"ndr":
                                        rate = \
                                            test["throughput"][u"NDR"][u"LOWER"]
                                        stdev = float(u"nan")
                                    elif ttype == u"pdr":
                                        rate = \
                                            test["throughput"][u"PDR"][u"LOWER"]
                                        stdev = float(u"nan")
                                    else:
                                        continue
                                    chart_data[test_id][int(index)] = {
                                        u"receive-rate": rate,
                                        u"receive-stdev": stdev
                                    }
                                    chart_tags[test_id] = \
                                        test.get(u"tags", None)
                                except (KeyError, TypeError):
                                    pass

                # Add items to the csv table:
                for tst_name, tst_data in chart_data.items():
                    tst_lst = list()
                    for bld in builds_dict[job_name]:
                        itm = tst_data.get(int(bld), dict())
                        # CSIT-1180: Itm will be list, compute stats.
                        try:
                            tst_lst.append(str(itm.get(u"receive-rate", u"")))
                        except AttributeError:
                            tst_lst.append(u"")
                    csv_tbl.append(f"{tst_name}," + u",".join(tst_lst) + u'\n')

                # Generate traces:
                traces = list()
                index = 0
                groups = graph.get(u"groups", None)
                visibility = list()

                if groups:
                    for group in groups:
                        visible = list()
                        for tag in group:
                            for tst_name, test_data in chart_data.items():
                                if not test_data:
                                    logging.warning(
                                        f"No data for the test {tst_name}"
                                    )
                                    continue
                                if tag not in chart_tags[tst_name]:
                                    continue
                                try:
                                    trace, rslt = _generate_trending_traces(
                                        test_data,
                                        job_name=job_name,
                                        build_info=build_info,
                                        name=u'-'.join(tst_name.split(u'.')[-1].
                                                       split(u'-')[2:-1]),
                                        color=COLORS[index],
                                        incl_tests=ttype
                                    )
                                except IndexError:
                                    logging.error(f"Out of colors: index: "
                                                  f"{index}, test: {tst_name}")
                                    index += 1
                                    continue
                                traces.extend(trace)
                                visible.extend(
                                    [True for _ in range(len(trace))]
                                )
                                res[tst_name] = rslt
                                index += 1
                                break
                        visibility.append(visible)
                else:
                    for tst_name, test_data in chart_data.items():
                        if not test_data:
                            logging.warning(f"No data for the test {tst_name}")
                            continue
                        try:
                            trace, rslt = _generate_trending_traces(
                                test_data,
                                job_name=job_name,
                                build_info=build_info,
                                name=u'-'.join(
                                    tst_name.split(u'.')[-1].split(u'-')[2:-1]),
                                color=COLORS[index],
                                incl_tests=ttype
                            )
                        except IndexError:
                            logging.error(
                                f"Out of colors: index: "
                                f"{index}, test: {tst_name}"
                            )
                            index += 1
                            continue
                        traces.extend(trace)
                        res[tst_name] = rslt
                        index += 1

                if traces:
                    # Generate the chart:
                    try:
                        layout = deepcopy(graph[u"layout"])
                    except KeyError as err:
                        logging.error(u"Finished with error: No layout defined")
                        logging.error(repr(err))
                        return dict()
                    if groups:
                        show = list()
                        for i in range(len(visibility)):
                            visible = list()
                            for vis_idx, _ in enumerate(visibility):
                                for _ in range(len(visibility[vis_idx])):
                                    visible.append(i == vis_idx)
                            show.append(visible)

                        buttons = list()
                        buttons.append(dict(
                            label=u"All",
                            method=u"update",
                            args=[{u"visible":
                                       [True for _ in range(len(show[0]))]}, ]
                        ))
                        for i in range(len(groups)):
                            try:
                                label = graph[u"group-names"][i]
                            except (IndexError, KeyError):
                                label = f"Group {i + 1}"
                            buttons.append(dict(
                                label=label,
                                method=u"update",
                                args=[{u"visible": show[i]}, ]
                            ))

                        layout[u"updatemenus"] = list([
                            dict(
                                active=0,
                                type=u"dropdown",
                                direction=u"down",
                                xanchor=u"left",
                                yanchor=u"bottom",
                                x=-0.12,
                                y=1.0,
                                buttons=buttons
                            )
                        ])

                    name_file = (
                        f"{spec.cpta[u'output-file']}/"
                        f"{graph[u'output-file-name']}.html"
                    )
                    name_file = name_file.format(core=core, test_type=ttype)

                    logging.info(f"    Writing the file {name_file}")
                    plpl = plgo.Figure(data=traces, layout=layout)
                    try:
                        ploff.plot(
                            plpl,
                            show_link=False,
                            auto_open=False,
                            filename=name_file
                        )
                    except plerr.PlotlyEmptyDataError:
                        logging.warning(u"No data for the plot. Skipped.")

                return_lst.append(
                    {
                        u"job_name": job_name,
                        u"csv_table": csv_tbl,
                        u"results": res
                    }
                )

        return return_lst

    builds_dict = dict()
    for job in spec.input[u"builds"].keys():
        if builds_dict.get(job, None) is None:
            builds_dict[job] = list()
        for build in spec.input[u"builds"][job]:
            status = build[u"status"]
            if status not in (u"failed", u"not found", u"removed", None):
                builds_dict[job].append(str(build[u"build"]))

    # Create "build ID": "date" dict:
    build_info = dict()
    tb_tbl = spec.environment.get(u"testbeds", None)
    for job_name, job_data in builds_dict.items():
        if build_info.get(job_name, None) is None:
            build_info[job_name] = OrderedDict()
        for build in job_data:
            testbed = u""
            tb_ip = input_data.metadata(job_name, build).get(u"testbed", u"")
            if tb_ip and tb_tbl:
                testbed = tb_tbl.get(tb_ip, u"")
            build_info[job_name][build] = (
                input_data.metadata(job_name, build).get(u"generated", u""),
                input_data.metadata(job_name, build).get(u"version", u""),
                testbed
            )

    anomaly_classifications = dict()

    # Create the table header:
    csv_tables = dict()
    for job_name in builds_dict:
        if csv_tables.get(job_name, None) is None:
            csv_tables[job_name] = list()
        header = f"Build Number:,{u','.join(builds_dict[job_name])}\n"
        csv_tables[job_name].append(header)
        build_dates = [x[0] for x in build_info[job_name].values()]
        header = f"Build Date:,{u','.join(build_dates)}\n"
        csv_tables[job_name].append(header)
        versions = [x[1] for x in build_info[job_name].values()]
        header = f"Version:,{u','.join(versions)}\n"
        csv_tables[job_name].append(header)

    for chart in spec.cpta[u"plots"]:
        results = _generate_chart(chart)
        if not results:
            continue

        for result in results:
            csv_tables[result[u"job_name"]].extend(result[u"csv_table"])

            if anomaly_classifications.get(result[u"job_name"], None) is None:
                anomaly_classifications[result[u"job_name"]] = dict()
            anomaly_classifications[result[u"job_name"]].\
                update(result[u"results"])

    # Write the tables:
    for job_name, csv_table in csv_tables.items():
        file_name = f"{spec.cpta[u'output-file']}/{job_name}-trending"
        with open(f"{file_name}.csv", u"wt") as file_handler:
            file_handler.writelines(csv_table)

        txt_table = None
        with open(f"{file_name}.csv", u"rt") as csv_file:
            csv_content = csv.reader(csv_file, delimiter=u',', quotechar=u'"')
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
                    # PrettyTable raises Exception
                    except Exception as err:
                        logging.warning(
                            f"Error occurred while generating TXT table:\n{err}"
                        )
                line_nr += 1
            txt_table.align[u"Build Number:"] = u"l"
        with open(f"{file_name}.txt", u"wt") as txt_file:
            txt_file.write(str(txt_table))

    # Evaluate result:
    if anomaly_classifications:
        result = u"PASS"
        for job_name, job_data in anomaly_classifications.items():
            file_name = \
                f"{spec.cpta[u'output-file']}/regressions-{job_name}.txt"
            with open(file_name, u'w') as txt_file:
                for test_name, classification in job_data.items():
                    if classification == u"regression":
                        txt_file.write(test_name + u'\n')
                    if classification in (u"regression", u"outlier"):
                        result = u"FAIL"
            file_name = \
                f"{spec.cpta[u'output-file']}/progressions-{job_name}.txt"
            with open(file_name, u'w') as txt_file:
                for test_name, classification in job_data.items():
                    if classification == u"progression":
                        txt_file.write(test_name + u'\n')
    else:
        result = u"FAIL"

    logging.info(f"Partial results: {anomaly_classifications}")
    logging.info(f"Result: {result}")

    return result
