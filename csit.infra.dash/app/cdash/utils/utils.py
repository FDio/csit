# Copyright (c) 2024 Cisco and/or its affiliates.
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

"""Functions used by Dash applications.
"""

import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

import hdrh.histogram
import hdrh.codec

from math import sqrt
from dash import dcc, no_update, html
from datetime import datetime

from ..utils.constants import Constants as C
from ..utils.url_processing import url_encode
from ..utils.trigger import Trigger


def get_color(idx: int) -> str:
    """Returns a color from the list defined in Constants.PLOT_COLORS defined by
    its index.

    :param idx: Index of the color.
    :type idx: int
    :returns: Color defined by hex code.
    :trype: str
    """
    return C.PLOT_COLORS[idx % len(C.PLOT_COLORS)]


def show_tooltip(tooltips:dict, id: str, title: str,
        clipboard_id: str=None) -> list:
    """Generate list of elements to display a text (e.g. a title) with a
    tooltip and optionaly with Copy&Paste icon and the clipboard
    functionality enabled.

    :param tooltips: Dictionary with tooltips.
    :param id: Tooltip ID.
    :param title: A text for which the tooltip will be displayed.
    :param clipboard_id: If defined, a Copy&Paste icon is displayed and the
        clipboard functionality is enabled.
    :type tooltips: dict
    :type id: str
    :type title: str
    :type clipboard_id: str
    :returns: List of elements to display a text with a tooltip and
        optionaly with Copy&Paste icon.
    :rtype: list
    """

    return [
        dcc.Clipboard(target_id=clipboard_id, title="Copy URL") \
            if clipboard_id else str(),
        f"{title} ",
        dbc.Badge(
            id=id,
            children="?",
            pill=True,
            color="white",
            text_color="info",
            class_name="border ms-1",
        ),
        dbc.Tooltip(
            children=tooltips.get(id, str()),
            target=id,
            placement="auto"
        )
    ]


def label(key: str) -> str:
    """Returns a label for input elements (dropdowns, ...).

    If the label is not defined, the function returns the provided key.

    :param key: The key to the label defined in Constants.LABELS.
    :type key: str
    :returns: Label.
    :rtype: str
    """
    return C.LABELS.get(key, key)


def sync_checklists(options: list, sel: list, all: list, id: str) -> tuple:
    """Synchronize a checklist with defined "options" with its "All" checklist.

    :param options: List of options for the cheklist.
    :param sel: List of selected options.
    :param all: List of selected option from "All" checklist.
    :param id: ID of a checklist to be used for synchronization.
    :returns: Tuple of lists with otions for both checklists.
    :rtype: tuple of lists
    """
    opts = {v["value"] for v in options}
    if id =="all":
        sel = list(opts) if all else list()
    else:
        all = ["all", ] if set(sel) == opts else list()
    return sel, all


def list_tests(selection: dict) -> list:
    """Transform list of tests to a list of dictionaries usable by checkboxes.

    :param selection: List of tests to be displayed in "Selected tests" window.
    :type selection: list
    :returns: List of dictionaries with "label", "value" pairs for a checkbox.
    :rtype: list
    """
    if selection:
        return [{"label": v["id"], "value": v["id"]} for v in selection]
    else:
        return list()


def get_date(s_date: str) -> datetime:
    """Transform string reprezentation of date to datetime.datetime data type.

    :param s_date: String reprezentation of date.
    :type s_date: str
    :returns: Date as datetime.datetime.
    :rtype: datetime.datetime
    """
    return datetime(int(s_date[0:4]), int(s_date[5:7]), int(s_date[8:10]))


def gen_new_url(url_components: dict, params: dict) -> str:
    """Generate a new URL with encoded parameters.

    :param url_components: Dictionary with URL elements. It should contain
        "scheme", "netloc" and "path".
    :param url_components: URL parameters to be encoded to the URL.
    :type parsed_url: dict
    :type params: dict
    :returns Encoded URL with parameters.
    :rtype: str
    """

    if url_components:
        return url_encode(
            {
                "scheme": url_components.get("scheme", ""),
                "netloc": url_components.get("netloc", ""),
                "path": url_components.get("path", ""),
                "params": params
            }
        )
    else:
        return str()


def get_duts(df: pd.DataFrame) -> list:
    """Get the list of DUTs from the pre-processed information about jobs.

    :param df: DataFrame with information about jobs.
    :type df: pandas.DataFrame
    :returns: Alphabeticaly sorted list of DUTs.
    :rtype: list
    """
    return sorted(list(df["dut"].unique()))


def get_ttypes(df: pd.DataFrame, dut: str) -> list:
    """Get the list of test types from the pre-processed information about
    jobs.

    :param df: DataFrame with information about jobs.
    :param dut: The DUT for which the list of test types will be populated.
    :type df: pandas.DataFrame
    :type dut: str
    :returns: Alphabeticaly sorted list of test types.
    :rtype: list
    """
    return sorted(list(df.loc[(df["dut"] == dut)]["ttype"].unique()))


def get_cadences(df: pd.DataFrame, dut: str, ttype: str) -> list:
    """Get the list of cadences from the pre-processed information about
    jobs.

    :param df: DataFrame with information about jobs.
    :param dut: The DUT for which the list of cadences will be populated.
    :param ttype: The test type for which the list of cadences will be
        populated.
    :type df: pandas.DataFrame
    :type dut: str
    :type ttype: str
    :returns: Alphabeticaly sorted list of cadences.
    :rtype: list
    """
    return sorted(list(df.loc[(
        (df["dut"] == dut) &
        (df["ttype"] == ttype)
    )]["cadence"].unique()))


def get_test_beds(df: pd.DataFrame, dut: str, ttype: str, cadence: str) -> list:
    """Get the list of test beds from the pre-processed information about
    jobs.

    :param df: DataFrame with information about jobs.
    :param dut: The DUT for which the list of test beds will be populated.
    :param ttype: The test type for which the list of test beds will be
        populated.
    :param cadence: The cadence for which the list of test beds will be
        populated.
    :type df: pandas.DataFrame
    :type dut: str
    :type ttype: str
    :type cadence: str
    :returns: Alphabeticaly sorted list of test beds.
    :rtype: list
    """
    return sorted(list(df.loc[(
        (df["dut"] == dut) &
        (df["ttype"] == ttype) &
        (df["cadence"] == cadence)
    )]["tbed"].unique()))


def get_job(df: pd.DataFrame, dut, ttype, cadence, testbed):
    """Get the name of a job defined by dut, ttype, cadence, test bed.
    Input information comes from the control panel.

    :param df: DataFrame with information about jobs.
    :param dut: The DUT for which the job name will be created.
    :param ttype: The test type for which the job name will be created.
    :param cadence: The cadence for which the job name will be created.
    :param testbed: The test bed for which the job name will be created.
    :type df: pandas.DataFrame
    :type dut: str
    :type ttype: str
    :type cadence: str
    :type testbed: str
    :returns: Job name.
    :rtype: str
    """
    return df.loc[(
        (df["dut"] == dut) &
        (df["ttype"] == ttype) &
        (df["cadence"] == cadence) &
        (df["tbed"] == testbed)
    )]["job"].item()


def generate_options(opts: list, sort: bool=True) -> list:
    """Return list of options for radio items in control panel. The items in
    the list are dictionaries with keys "label" and "value".

    :params opts: List of options (str) to be used for the generated list.
    :type opts: list
    :returns: List of options (dict).
    :rtype: list
    """
    if sort:
        opts = sorted(opts)
    return [{"label": i, "value": i} for i in opts]


def set_job_params(df: pd.DataFrame, job: str) -> dict:
    """Create a dictionary with all options and values for (and from) the
    given job.

    :param df: DataFrame with information about jobs.
    :params job: The name of job for and from which the dictionary will be
        created.
    :type df: pandas.DataFrame
    :type job: str
    :returns: Dictionary with all options and values for (and from) the
        given job.
    :rtype: dict
    """

    l_job = job.split("-")
    return {
        "job": job,
        "dut": l_job[1],
        "ttype": l_job[3],
        "cadence": l_job[4],
        "tbed": "-".join(l_job[-2:]),
        "duts": generate_options(get_duts(df)),
        "ttypes": generate_options(get_ttypes(df, l_job[1])),
        "cadences": generate_options(get_cadences(df, l_job[1], l_job[3])),
        "tbeds": generate_options(
            get_test_beds(df, l_job[1], l_job[3], l_job[4]))
    }


def get_list_group_items(
        items: list,
        type: str,
        colorize: bool=True,
        add_index: bool=False
    ) -> list:
    """Generate list of ListGroupItems with checkboxes with selected items.

    :param items: List of items to be displayed in the ListGroup.
    :param type: The type part of an element ID.
    :param colorize: If True, the color of labels is set, otherwise the default
        color is used.
    :param add_index: Add index to the list items.
    :type items: list
    :type type: str
    :type colorize: bool
    :type add_index: bool
    :returns: List of ListGroupItems with checkboxes with selected items.
    :rtype: list
    """

    children = list()
    for i, l in enumerate(items):
        idx = f"{i + 1}. " if add_index else str()
        label = f"{idx}{l['id']}" if isinstance(l, dict) else f"{idx}{l}"
        children.append(
            dbc.ListGroupItem(
                children=[
                    dbc.Checkbox(
                        id={"type": type, "index": i},
                        label=label,
                        value=False,
                        label_class_name="m-0 p-0",
                        label_style={
                            "font-size": ".875em",
                            "color": get_color(i) if colorize else "#55595c"
                        },
                        class_name="info"
                    )
                ],
                class_name="p-0"
            )
        )

    return children


def relative_change_stdev(mean1, mean2, std1, std2):
    """Compute relative standard deviation of change of two values.

    The "1" values are the base for comparison.
    Results are returned as percentage (and percentual points for stdev).
    Linearized theory is used, so results are wrong for relatively large stdev.

    :param mean1: Mean of the first number.
    :param mean2: Mean of the second number.
    :param std1: Standard deviation estimate of the first number.
    :param std2: Standard deviation estimate of the second number.
    :type mean1: float
    :type mean2: float
    :type std1: float
    :type std2: float
    :returns: Relative change and its stdev.
    :rtype: float
    """
    mean1, mean2 = float(mean1), float(mean2)
    quotient = mean2 / mean1
    first = std1 / mean1
    second = std2 / mean2
    std = quotient * sqrt(first * first + second * second)
    return (quotient - 1) * 100, std * 100


def get_hdrh_latencies(row: pd.Series, name: str) -> dict:
    """Get the HDRH latencies from the test data.

    :param row: A row fron the data frame with test data.
    :param name: The test name to be displayed as the graph title.
    :type row: pandas.Series
    :type name: str
    :returns: Dictionary with HDRH latencies.
    :rtype: dict
    """

    latencies = {"name": name}
    for key in C.LAT_HDRH:
        try:
            latencies[key] = row[key]
        except KeyError:
            return None

    return latencies


def graph_hdrh_latency(data: dict, layout: dict) -> go.Figure:
    """Generate HDR Latency histogram graphs.

    :param data: HDRH data.
    :param layout: Layout of plot.ly graph.
    :type data: dict
    :type layout: dict
    :returns: HDR latency Histogram.
    :rtype: plotly.graph_objects.Figure
    """

    fig = None

    traces = list()
    for idx, (lat_name, lat_hdrh) in enumerate(data.items()):
        try:
            decoded = hdrh.histogram.HdrHistogram.decode(lat_hdrh)
        except (hdrh.codec.HdrLengthException, TypeError):
            continue
        previous_x = 0.0
        prev_perc = 0.0
        xaxis = list()
        yaxis = list()
        hovertext = list()
        for item in decoded.get_recorded_iterator():
            # The real value is "percentile".
            # For 100%, we cut that down to "x_perc" to avoid
            # infinity.
            percentile = item.percentile_level_iterated_to
            x_perc = min(percentile, C.PERCENTILE_MAX)
            xaxis.append(previous_x)
            yaxis.append(item.value_iterated_to)
            hovertext.append(
                f"<b>{C.GRAPH_LAT_HDRH_DESC[lat_name]}</b><br>"
                f"Direction: {('W-E', 'E-W')[idx % 2]}<br>"
                f"Percentile: {prev_perc:.5f}-{percentile:.5f}%<br>"
                f"Latency: {item.value_iterated_to}uSec"
            )
            next_x = 100.0 / (100.0 - x_perc)
            xaxis.append(next_x)
            yaxis.append(item.value_iterated_to)
            hovertext.append(
                f"<b>{C.GRAPH_LAT_HDRH_DESC[lat_name]}</b><br>"
                f"Direction: {('W-E', 'E-W')[idx % 2]}<br>"
                f"Percentile: {prev_perc:.5f}-{percentile:.5f}%<br>"
                f"Latency: {item.value_iterated_to}uSec"
            )
            previous_x = next_x
            prev_perc = percentile

        traces.append(
            go.Scatter(
                x=xaxis,
                y=yaxis,
                name=C.GRAPH_LAT_HDRH_DESC[lat_name],
                mode="lines",
                legendgroup=C.GRAPH_LAT_HDRH_DESC[lat_name],
                showlegend=bool(idx % 2),
                line=dict(
                    color=get_color(int(idx/2)),
                    dash="solid",
                    width=1 if idx % 2 else 2
                ),
                hovertext=hovertext,
                hoverinfo="text"
            )
        )
    if traces:
        fig = go.Figure()
        fig.add_traces(traces)
        layout_hdrh = layout.get("plot-hdrh-latency", None)
        if lat_hdrh:
            fig.update_layout(layout_hdrh)

    return fig


def navbar_trending(active: tuple):
    """Add nav element with navigation panel. It is placed on the top.

    :param active: Tuple of boolean values defining the active items in the
        navbar. True == active
    :type active: tuple
    :returns: Navigation bar.
    :rtype: dbc.NavbarSimple
    """
    children = list()
    if C.START_TRENDING:
        children.append(dbc.NavItem(dbc.NavLink(
            C.TREND_TITLE,
            active=active[0],
            external_link=True,
            href="/trending"
        )))
    if C.START_FAILURES:
        children.append(dbc.NavItem(dbc.NavLink(
            C.NEWS_TITLE,
            active=active[1],
            external_link=True,
            href="/news"
        )))
    if C.START_STATISTICS:
        children.append(dbc.NavItem(dbc.NavLink(
            C.STATS_TITLE,
            active=active[2],
            external_link=True,
            href="/stats"
        )))
    if C.START_SEARCH:
        children.append(dbc.NavItem(dbc.NavLink(
            C.SEARCH_TITLE,
            active=active[3],
            external_link=True,
            href="/search"
        )))
    if C.START_DOC:
        children.append(dbc.NavItem(dbc.NavLink(
            "Documentation",
            id="btn-documentation",
        )))
    return dbc.NavbarSimple(
        children=children,
        id="navbarsimple-main",
        brand=C.BRAND,
        brand_href="/",
        brand_external_link=True,
        class_name="p-2",
        fluid=True
    )


def navbar_report(active: tuple):
    """Add nav element with navigation panel. It is placed on the top.

    :param active: Tuple of boolean values defining the active items in the
        navbar. True == active
    :type active: tuple
    :returns: Navigation bar.
    :rtype: dbc.NavbarSimple
    """
    children = list()
    if C.START_REPORT:
        children.append(dbc.NavItem(dbc.NavLink(
            C.REPORT_TITLE,
            active=active[0],
            external_link=True,
            href="/report"
        )))
    if C.START_COMPARISONS:
        children.append(dbc.NavItem(dbc.NavLink(
            "Comparisons",
            active=active[1],
            external_link=True,
            href="/comparisons"
        )))
    if C.START_COVERAGE:
        children.append(dbc.NavItem(dbc.NavLink(
            "Coverage Data",
            active=active[2],
            external_link=True,
            href="/coverage"
        )))
    if C.START_SEARCH:
        children.append(dbc.NavItem(dbc.NavLink(
            C.SEARCH_TITLE,
            active=active[3],
            external_link=True,
            href="/search"
        )))
    if C.START_DOC:
        children.append(dbc.NavItem(dbc.NavLink(
            "Documentation",
            id="btn-documentation",
        )))
    return dbc.NavbarSimple(
        children=children,
        id="navbarsimple-main",
        brand=C.BRAND,
        brand_href="/",
        brand_external_link=True,
        class_name="p-2",
        fluid=True
    )


def filter_table_data(
        store_table_data: list,
        table_filter: str
    ) -> list:
    """Filter table data using user specified filter.

    :param store_table_data: Table data represented as a list of records.
    :param table_filter: User specified filter.
    :type store_table_data: list
    :type table_filter: str
    :returns: A new table created by filtering of table data represented as
        a list of records.
    :rtype: list
    """

    # Checks:
    if not any((table_filter, store_table_data, )):
        return store_table_data

    def _split_filter_part(filter_part: str) -> tuple:
        """Split a part of filter into column name, operator and value.
        A "part of filter" is a sting berween "&&" operator.

        :param filter_part: A part of filter.
        :type filter_part: str
        :returns: Column name, operator, value
        :rtype: tuple[str, str, str|float]
        """
        for operator_type in C.OPERATORS:
            for operator in operator_type:
                if operator in filter_part:
                    name_p, val_p = filter_part.split(operator, 1)
                    name = name_p[name_p.find("{") + 1 : name_p.rfind("}")]
                    val_p = val_p.strip()
                    if (val_p[0] == val_p[-1] and val_p[0] in ("'", '"', '`')):
                        value = val_p[1:-1].replace("\\" + val_p[0], val_p[0])
                    else:
                        try:
                            value = float(val_p)
                        except ValueError:
                            value = val_p

                    return name, operator_type[0].strip(), value
        return (None, None, None)

    df = pd.DataFrame.from_records(store_table_data)
    for filter_part in table_filter.split(" && "):
        col_name, operator, filter_value = _split_filter_part(filter_part)
        if operator == "contains":
            df = df.loc[df[col_name].str.contains(filter_value, regex=True)]
        elif operator in ("eq", "ne", "lt", "le", "gt", "ge"):
            # These operators match pandas series operator method names.
            df = df.loc[getattr(df[col_name], operator)(filter_value)]
        elif operator == "datestartswith":
            # This is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format.
            # Currently not used in comparison tables.
            df = df.loc[df[col_name].str.startswith(filter_value)]

    return df.to_dict("records")


def sort_table_data(
        store_table_data: list,
        sort_by: list
    ) -> list:
    """Sort table data using user specified order.

    :param store_table_data: Table data represented as a list of records.
    :param sort_by: User specified sorting order (multicolumn).
    :type store_table_data: list
    :type sort_by: list
    :returns: A new table created by sorting the table data represented as
        a list of records.
    :rtype: list
    """

    # Checks:
    if not any((sort_by, store_table_data, )):
        return store_table_data

    df = pd.DataFrame.from_records(store_table_data)
    if len(sort_by):
        dff = df.sort_values(
            [col["column_id"] for col in sort_by],
            ascending=[col["direction"] == "asc" for col in sort_by],
            inplace=False
        )
    else:
        # No sort is applied
        dff = df

    return dff.to_dict("records")


def show_trending_graph_data(
        trigger: Trigger,
        data: dict,
        graph_layout: dict
    ) -> tuple:
    """Generates the data for the offcanvas displayed when a particular point in
    a trending graph (daily data) is clicked on.

    :param trigger: The information from trigger when the data point is clicked
        on.
    :param graph: The data from the clicked point in the graph.
    :param graph_layout: The layout of the HDRH latency graph.
    :type trigger: Trigger
    :type graph: dict
    :type graph_layout: dict
    :returns: The data to be displayed on the offcanvas and the information to
        show the offcanvas.
    :rtype: tuple(list, list, bool)
    """

    if trigger.idx == "tput":
        idx = 0
    elif trigger.idx == "bandwidth":
        idx = 1
    elif trigger.idx == "lat":
        idx = len(data) - 1
    else:
        return list(), list(), False
    try:
        data = data[idx]["points"][0]
    except (IndexError, KeyError, ValueError, TypeError):
        return list(), list(), False

    metadata = no_update
    graph = list()

    list_group_items = list()
    for itm in data.get("text", None).split("<br>"):
        if not itm:
            continue
        lst_itm = itm.split(": ")
        if lst_itm[0] == "csit-ref":
            list_group_item = dbc.ListGroupItem([
                dbc.Badge(lst_itm[0]),
                html.A(
                    lst_itm[1],
                    href=f"{C.URL_LOGS}{lst_itm[1]}",
                    target="_blank"
                )
            ])
        else:
            list_group_item = dbc.ListGroupItem([
                dbc.Badge(lst_itm[0]),
                lst_itm[1]
            ])
        list_group_items.append(list_group_item)

    if trigger.idx == "tput":
        title = "Throughput"
    elif trigger.idx == "bandwidth":
        title = "Bandwidth"
    elif trigger.idx == "lat":
        title = "Latency"
        hdrh_data = data.get("customdata", None)
        if hdrh_data:
            graph = [dbc.Card(
                class_name="gy-2 p-0",
                children=[
                    dbc.CardHeader(hdrh_data.pop("name")),
                    dbc.CardBody(
                        dcc.Graph(
                            id="hdrh-latency-graph",
                            figure=graph_hdrh_latency(hdrh_data, graph_layout)
                        )
                    )
                ])
            ]

    metadata = [
        dbc.Card(
            class_name="gy-2 p-0",
            children=[
                dbc.CardHeader(children=[
                    dcc.Clipboard(
                        target_id="tput-lat-metadata",
                        title="Copy",
                        style={"display": "inline-block"}
                    ),
                    title
                ]),
                dbc.CardBody(
                    dbc.ListGroup(list_group_items, flush=True),
                    id="tput-lat-metadata",
                    class_name="p-0",
                )
            ]
        )
    ]

    return metadata, graph, True


def show_iterative_graph_data(
        trigger: Trigger,
        data: dict,
        graph_layout: dict
    ) -> tuple:
    """Generates the data for the offcanvas displayed when a particular point in
    a box graph (iterative data) is clicked on.

    :param trigger: The information from trigger when the data point is clicked
        on.
    :param graph: The data from the clicked point in the graph.
    :param graph_layout: The layout of the HDRH latency graph.
    :type trigger: Trigger
    :type graph: dict
    :type graph_layout: dict
    :returns: The data to be displayed on the offcanvas and the information to
        show the offcanvas.
    :rtype: tuple(list, list, bool)
    """

    if trigger.idx == "tput":
        idx = 0
    elif trigger.idx == "bandwidth":
        idx = 1
    elif trigger.idx == "lat":
        idx = len(data) - 1
    else:
        return list(), list(), False

    try:
        data = data[idx]["points"]
    except (IndexError, KeyError, ValueError, TypeError):
        return list(), list(), False

    def _process_stats(data: list, param: str) -> list:
        """Process statistical data provided by plot.ly box graph.

        :param data: Statistical data provided by plot.ly box graph.
        :param param: Parameter saying if the data come from "tput" or
            "lat" graph.
        :type data: list
        :type param: str
        :returns: Listo of tuples where the first value is the
            statistic's name and the secont one it's value.
        :rtype: list
        """
        if len(data) == 7:
            stats = ("max", "upper fence", "q3", "median", "q1",
                    "lower fence", "min")
        elif len(data) == 9:
            stats = ("outlier", "max", "upper fence", "q3", "median",
                    "q1", "lower fence", "min", "outlier")
        elif len(data) == 1:
            if param == "lat":
                stats = ("average latency at 50% PDR", )
            elif param == "bandwidth":
                stats = ("bandwidth", )
            else:
                stats = ("throughput", )
        else:
            return list()
        unit = " [us]" if param == "lat" else str()
        return [(f"{stat}{unit}", f"{value['y']:,.0f}")
                for stat, value in zip(stats, data)]

    customdata = data[0].get("customdata", dict())
    datapoint = customdata.get("metadata", dict())
    hdrh_data = customdata.get("hdrh", dict())

    list_group_items = list()
    for k, v in datapoint.items():
        if k == "csit-ref":
            if len(data) > 1:
                continue
            list_group_item = dbc.ListGroupItem([
                dbc.Badge(k),
                html.A(v, href=f"{C.URL_LOGS}{v}", target="_blank")
            ])
        else:
            list_group_item = dbc.ListGroupItem([dbc.Badge(k), v])
        list_group_items.append(list_group_item)

    graph = list()
    if trigger.idx == "tput":
        title = "Throughput"
    elif trigger.idx == "bandwidth":
        title = "Bandwidth"
    elif trigger.idx == "lat":
        title = "Latency"
        if len(data) == 1:
            if hdrh_data:
                graph = [dbc.Card(
                    class_name="gy-2 p-0",
                    children=[
                        dbc.CardHeader(hdrh_data.pop("name")),
                        dbc.CardBody(dcc.Graph(
                            id="hdrh-latency-graph",
                            figure=graph_hdrh_latency(hdrh_data, graph_layout)
                        ))
                    ])
                ]

    for k, v in _process_stats(data, trigger.idx):
        list_group_items.append(dbc.ListGroupItem([dbc.Badge(k), v]))

    metadata = [
        dbc.Card(
            class_name="gy-2 p-0",
            children=[
                dbc.CardHeader(children=[
                    dcc.Clipboard(
                        target_id="tput-lat-metadata",
                        title="Copy",
                        style={"display": "inline-block"}
                    ),
                    title
                ]),
                dbc.CardBody(
                    dbc.ListGroup(list_group_items, flush=True),
                    id="tput-lat-metadata",
                    class_name="p-0"
                )
            ]
        )
    ]

    return metadata, graph, True
