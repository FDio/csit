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


"""Plotly Dash HTML layout override.
"""

import logging
import pandas as pd
import dash_bootstrap_components as dbc

from flask import Flask
from dash import dcc
from dash import html, dash_table
from dash import callback_context, no_update, ALL
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from yaml import load, FullLoader, YAMLError
from ast import literal_eval

from ..utils.constants import Constants as C
from ..utils.control_panel import ControlPanel
from ..utils.trigger import Trigger
from ..utils.utils import gen_new_url, generate_options, navbar_trending, \
    filter_table_data, sort_table_data, show_trending_graph_data, \
    show_iterative_graph_data, show_tooltip, get_topo_arch
from ..utils.url_processing import url_decode
from .tables import search_table
from ..coverage.tables import coverage_tables
from ..report.graphs import graph_iterative
from ..trending.graphs import graph_trending


# Control panel partameters and their default values.
CP_PARAMS = {
    "datatype-val": str(),
    "dut-opt": list(),
    "dut-dis": C.STYLE_DONT_DISPLAY,
    "dut-val": str(),
    "release-opt": list(),
    "release-dis": C.STYLE_DONT_DISPLAY,
    "release-val": str(),
    "help-dis": C.STYLE_DONT_DISPLAY,
    "help-val": str(),
    "search-dis": C.STYLE_DONT_DISPLAY,
    "search-val": str()
}


class Layout:
    """The layout of the dash app and the callbacks.
    """

    def __init__(self,
            app: Flask,
            data: dict,
            html_layout_file: str,
            graph_layout_file: str,
            tooltip_file: str
        ) -> None:
        """Initialization:
        - save the input parameters,
        - read and pre-process the data,
        - prepare data for the control panel,
        - read HTML layout file,
        - read graph layout file,
        - read tooltips from the tooltip file.

        :param app: Flask application running the dash application.
        :param data_trending: Pandas dataframe with trending data.
        :param html_layout_file: Path and name of the file specifying the HTML
            layout of the dash application.
        :param graph_layout_file: Path and name of the file with layout of
            plot.ly graphs.
        :param tooltip_file: Path and name of the yaml file specifying the
            tooltips.
        :type app: Flask
        :type data_trending: pandas.DataFrame
        :type html_layout_file: str
        :type graph_layout_file: str
        :type tooltip_file: str
        """

        # Inputs
        self._app = app
        self._html_layout_file = html_layout_file
        self._graph_layout_file = graph_layout_file
        self._tooltip_file = tooltip_file
        # Inputs - Data
        self._data = {
            k: v for k, v in data.items() if not v.empty and k != "statistics"
        }

        for data_type, pd in self._data.items():
            if pd.empty:
                continue
            full_id = list()

            for _, row in pd.iterrows():
                l_id = row["test_id"].split(".")
                suite = l_id[-2].replace("2n1l-", "").replace("1n1l-", "").\
                    replace("2n-", "")
                tb = get_topo_arch(row["job"].split("-"))
                nic = suite.split("-")[0]
                for driver in C.DRIVERS:
                    if driver in suite:
                        drv = driver
                        break
                else:
                    drv = "dpdk"
                test = l_id[-1]

                if data_type in ("iterative", "coverage", ):
                    full_id.append(
                        "_".join((row["release"], row["dut_type"],
                            row["dut_version"], tb, nic, drv, test))
                    )
                else:  # Trending
                    full_id.append(
                        "_".join((row["dut_type"], tb, nic, drv, test))
                    )
            pd["full_id"] = full_id

        # Get structure of tests:
        self._duts = dict()
        for data_type, pd in self._data.items():
            if pd.empty:
                continue
            self._duts[data_type] = dict()
            if data_type in ("iterative", "coverage", ):
                cols = ["job", "dut_type", "dut_version", "release", "test_id"]
                for _, row in pd[cols].drop_duplicates().iterrows():
                    dut = row["dut_type"]
                    if self._duts[data_type].get(dut, None) is None:
                        self._duts[data_type][dut] = list()
                    if row["release"] not in self._duts[data_type][dut]:
                        self._duts[data_type][dut].append(row["release"])
            else:
                for dut in pd["dut_type"].unique():
                    if self._duts[data_type].get(dut, None) is None:
                        self._duts[data_type][dut] = list()

        # Read from files:
        self._html_layout = str()
        self._graph_layout = None
        self._tooltips = dict()

        try:
            with open(self._html_layout_file, "r") as file_read:
                self._html_layout = file_read.read()
        except IOError as err:
            raise RuntimeError(
                f"Not possible to open the file {self._html_layout_file}\n{err}"
            )

        try:
            with open(self._graph_layout_file, "r") as file_read:
                self._graph_layout = load(file_read, Loader=FullLoader)
        except IOError as err:
            raise RuntimeError(
                f"Not possible to open the file {self._graph_layout_file}\n"
                f"{err}"
            )
        except YAMLError as err:
            raise RuntimeError(
                f"An error occurred while parsing the specification file "
                f"{self._graph_layout_file}\n{err}"
            )

        try:
            with open(self._tooltip_file, "r") as file_read:
                self._tooltips = load(file_read, Loader=FullLoader)
        except IOError as err:
            logging.warning(
                f"Not possible to open the file {self._tooltip_file}\n{err}"
            )
        except YAMLError as err:
            logging.warning(
                f"An error occurred while parsing the specification file "
                f"{self._tooltip_file}\n{err}"
            )

        # Callbacks:
        if self._app is not None and hasattr(self, "callbacks"):
            self.callbacks(self._app)

    @property
    def html_layout(self):
        return self._html_layout

    def add_content(self):
        """Top level method which generated the web page.

        It generates:
        - Store for user input data,
        - Navigation bar,
        - Main area with control panel and ploting area.

        If no HTML layout is provided, an error message is displayed instead.

        :returns: The HTML div with the whole page.
        :rtype: html.Div
        """
        if self.html_layout and self._duts:
            return html.Div(
                id="div-main",
                className="small",
                children=[
                    dcc.Store(id="store"),
                    dcc.Store(id="store-table-data"),
                    dcc.Store(id="store-filtered-table-data"),
                    dcc.Location(id="url", refresh=False),
                    dbc.Row(
                        id="row-navbar",
                        class_name="g-0",
                        children=[navbar_trending((False, False, False, True))]
                    ),
                    dbc.Row(
                        id="row-main",
                        class_name="g-0",
                        children=[
                            self._add_ctrl_col(),
                            self._add_plotting_col()
                        ]
                    ),
                    dbc.Spinner(
                        dbc.Offcanvas(
                            class_name="w-75",
                            id="offcanvas-details",
                            title="Test Details",
                            placement="end",
                            is_open=False,
                            children=[]
                        ),
                        delay_show=C.SPINNER_DELAY
                    ),
                    dbc.Spinner(
                        dbc.Offcanvas(
                            class_name="w-50",
                            id="offcanvas-metadata",
                            title="Detailed Information",
                            placement="end",
                            is_open=False,
                            children=[
                                dbc.Row(id="metadata-tput-lat"),
                                dbc.Row(id="metadata-hdrh-graph")
                            ]
                        ),
                        delay_show=C.SPINNER_DELAY
                    ),
                    dbc.Offcanvas(
                        class_name="w-75",
                        id="offcanvas-documentation",
                        title="Documentation",
                        placement="end",
                        is_open=False,
                        children=html.Iframe(
                            src=C.URL_DOC_TRENDING,
                            width="100%",
                            height="100%"
                        )
                    )
                ]
            )
        else:
            return html.Div(
                dbc.Alert("An Error Occured", color="danger"),
                id="div-main-error"
            )

    def _add_ctrl_col(self) -> dbc.Col:
        """Add column with controls. It is placed on the left side.

        :returns: Column with the control panel.
        :rtype: dbc.Col
        """
        return dbc.Col(html.Div(self._add_ctrl_panel(), className="sticky-top"))

    def _add_ctrl_panel(self) -> list:
        """Add control panel.

        :returns: Control panel.
        :rtype: list
        """
        return [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-data-type",
                                "Data Type"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "datatype"},
                                placeholder="Select a Data Type...",
                                options=sorted(
                                    [
                                        {"label": k, "value": k} \
                                            for k in self._data.keys()
                                    ],
                                    key=lambda d: d["label"]
                                )
                            )
                        ],
                        size="sm"
                    )
                ],
                style=C.STYLE_DISPLAY
            ),
            dbc.Row(
                class_name="g-0 p-1",
                id={"type": "ctrl-row", "index": "dut"},
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-dut",
                                "DUT"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "dut"},
                                placeholder="Select a Device under Test..."
                            )
                        ],
                        size="sm"
                    )
                ],
                style=C.STYLE_DONT_DISPLAY
            ),
            dbc.Row(
                class_name="g-0 p-1",
                id={"type": "ctrl-row", "index": "release"},
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-release",
                                "CSIT Release"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "release"},
                                placeholder="Select a Release..."
                            )
                        ],
                        size="sm"
                    )
                ],
                style=C.STYLE_DONT_DISPLAY
            ),
            dbc.Row(
                class_name="g-0 p-1",
                id={"type": "ctrl-row", "index": "help"},
                children=[
                    dbc.Input(
                        id={"type": "ctrl-dd", "index": "help"},
                        readonly=True,
                        debounce=True,
                        size="sm"
                    )
                ],
                style=C.STYLE_DONT_DISPLAY
            ),
            dbc.Row(
                class_name="g-0 p-1",
                id={"type": "ctrl-row", "index": "search"},
                children=[
                    dbc.Input(
                        id={"type": "ctrl-dd", "index": "search"},
                        placeholder="Type a Regular Expression...",
                        debounce=True,
                        size="sm"
                    )
                ],
                style=C.STYLE_DONT_DISPLAY
            )
        ]

    def _add_plotting_col(self) -> dbc.Col:
        """Add column with tables. It is placed on the right side.

        :returns: Column with tables.
        :rtype: dbc.Col
        """
        return dbc.Col(
            id="col-plotting-area",
            children=[
                dbc.Spinner(
                    children=[
                        dbc.Row(
                            id="plotting-area",
                            class_name="g-0 p-0",
                            children=[C.PLACEHOLDER, ]
                        )
                    ]
                )
            ],
            width=9
        )

    @staticmethod
    def _get_plotting_area(table: pd.DataFrame, url: str) -> list:
        """Generate the plotting area with all its content.

        :param table: Search table to be displayed.
        :param url: URL to be displayed in a modal window.
        :type table: pandas.DataFrame
        :type url: str
        :returns: List of rows with elements to be displayed in the plotting
            area.
        :rtype: list
        """

        if table.empty:
            return dbc.Row(
                dbc.Col(
                    children=dbc.Alert(
                        "No data found.",
                        color="danger"
                    ),
                    class_name="g-0 p-1",
                ),
                class_name="g-0 p-0"
            )

        columns = [{"name": col, "id": col} for col in table.columns]

        return [
            dbc.Row(
                children=[
                    dbc.Col(
                        children=dash_table.DataTable(
                            id={"type": "table", "index": "search"},
                            columns=columns,
                            data=table.to_dict("records"),
                            filter_action="custom",
                            sort_action="custom",
                            sort_mode="multi",
                            selected_columns=[],
                            selected_rows=[],
                            page_action="none",
                            style_cell={"textAlign": "left"}
                        ),
                        class_name="g-0 p-1"
                    )
                ],
                class_name="g-0 p-0"
            ),
            dbc.Row(
                [
                    dbc.Col([html.Div(
                        [
                            dbc.Button(
                                id="plot-btn-url",
                                children="Show URL",
                                class_name="me-1",
                                color="info",
                                style={
                                    "text-transform": "none",
                                    "padding": "0rem 1rem"
                                }
                            ),
                            dbc.Modal(
                                [
                                    dbc.ModalHeader(dbc.ModalTitle("URL")),
                                    dbc.ModalBody(url)
                                ],
                                id="plot-mod-url",
                                size="xl",
                                is_open=False,
                                scrollable=True
                            ),
                            dbc.Button(
                                id="plot-btn-download",
                                children="Download Data",
                                class_name="me-1",
                                color="info",
                                style={
                                    "text-transform": "none",
                                    "padding": "0rem 1rem"
                                }
                            ),
                            dcc.Download(id="download-data")
                        ],
                        className=\
                            "d-grid gap-0 d-md-flex justify-content-md-end"
                    )])
                ],
                class_name="g-0 p-0"
            ),
            dbc.Row(
                children=C.PLACEHOLDER,
                class_name="g-0 p-1"
            )
        ]

    def callbacks(self, app):
        """Callbacks for the whole application.

        :param app: The application.
        :type app: Flask
        """

        @app.callback(
            Output("store", "data"),
            Output("store-table-data", "data"),
            Output("store-filtered-table-data", "data"),
            Output("plotting-area", "children"),
            Output({"type": "table", "index": ALL}, "data"),
            Output({"type": "ctrl-dd", "index": "datatype"}, "value"),
            Output({"type": "ctrl-dd", "index": "dut"}, "options"),
            Output({"type": "ctrl-row", "index": "dut"}, "style"),
            Output({"type": "ctrl-dd", "index": "dut"}, "value"),
            Output({"type": "ctrl-dd", "index": "release"}, "options"),
            Output({"type": "ctrl-row", "index": "release"}, "style"),
            Output({"type": "ctrl-dd", "index": "release"}, "value"),
            Output({"type": "ctrl-row", "index": "help"}, "style"),
            Output({"type": "ctrl-dd", "index": "help"}, "value"),
            Output({"type": "ctrl-row", "index": "search"}, "style"),
            Output({"type": "ctrl-dd", "index": "search"}, "value"),
            State("store", "data"),
            State("store-table-data", "data"),
            State("store-filtered-table-data", "data"),
            State({"type": "table", "index": ALL}, "data"),
            Input("url", "href"),
            Input({"type": "table", "index": ALL}, "filter_query"),
            Input({"type": "table", "index": ALL}, "sort_by"),
            Input({"type": "ctrl-dd", "index": ALL}, "value"),
            prevent_initial_call=True
        )
        def _update_application(
                store: dict,
                store_table_data: list,
                filtered_data: list,
                table_data: list,
                href: str,
                *_
            ) -> tuple:
            """Update the application when the event is detected.
            """

            if store is None:
                store = {
                    "control-panel": dict(),
                    "selection": dict()
                }

            ctrl_panel = ControlPanel(
                CP_PARAMS,
                store.get("control-panel", dict())
            )
            selection = store["selection"]

            plotting_area = no_update
            on_draw = False

            # Parse the url:
            parsed_url = url_decode(href)
            if parsed_url:
                url_params = parsed_url["params"]
            else:
                url_params = None

            trigger = Trigger(callback_context.triggered)
            if trigger.type == "url" and url_params:
                try:
                    selection = literal_eval(url_params["selection"][0])
                    if selection:
                        dtype = selection["datatype"]
                        dut = selection["dut"]
                        if dtype == "trending":
                            rls_opts = list()
                            rls_dis = C.STYLE_DONT_DISPLAY
                        else:
                            rls_opts = generate_options(self._duts[dtype][dut])
                            rls_dis = C.STYLE_DISPLAY
                        ctrl_panel.set({
                            "datatype-val": dtype,
                            "dut-opt": \
                                generate_options(self._duts[dtype].keys()),
                            "dut-dis": C.STYLE_DISPLAY,
                            "dut-val": dut,
                            "release-opt": rls_opts,
                            "release-dis": rls_dis,
                            "release-val": selection["release"],
                            "help-dis": C.STYLE_DISPLAY,
                            "help-val": selection["help"],
                            "search-dis": C.STYLE_DISPLAY,
                            "search-val": selection["regexp"]
                        })
                        on_draw = True
                except (KeyError, IndexError, AttributeError, ValueError):
                    pass
            elif trigger.type == "ctrl-dd":
                if trigger.idx == "datatype":
                    try:
                        data_type = self._duts[trigger.value]
                        options = generate_options(data_type.keys())
                        disabled = C.STYLE_DISPLAY
                    except KeyError:
                        options = list()
                        disabled = C.STYLE_DONT_DISPLAY
                    ctrl_panel.set({
                        "datatype-val": trigger.value,
                        "dut-opt": options,
                        "dut-dis": disabled,
                        "dut-val": str(),
                        "release-opt": list(),
                        "release-dis": C.STYLE_DONT_DISPLAY,
                        "release-val": str(),
                        "help-dis": C.STYLE_DONT_DISPLAY,
                        "help-val": str(),
                        "search-dis": C.STYLE_DONT_DISPLAY,
                        "search-val": str()
                    })
                elif trigger.idx == "dut":
                    try:
                        data_type = ctrl_panel.get("datatype-val")
                        dut = self._duts[data_type][trigger.value]
                        if data_type != "trending":
                            options = generate_options(dut)
                        disabled = C.STYLE_DISPLAY
                    except KeyError:
                        options = list()
                        disabled = C.STYLE_DONT_DISPLAY
                    if data_type == "trending":
                        ctrl_panel.set({
                            "dut-val": trigger.value,
                            "release-opt": list(),
                            "release-dis": C.STYLE_DONT_DISPLAY,
                            "release-val": str(),
                            "help-dis": disabled,
                            "help-val": "<topo> <arch> <nic> <driver> " + \
                                "<framesize> <cores> <test>",
                            "search-dis": disabled,
                            "search-val": str()
                        })
                    else:
                        ctrl_panel.set({
                            "dut-val": trigger.value,
                            "release-opt": options,
                            "release-dis": disabled,
                            "release-val": str(),
                            "help-dis": C.STYLE_DONT_DISPLAY,
                            "help-val": str(),
                            "search-dis": C.STYLE_DONT_DISPLAY,
                            "search-val": str()
                        })
                elif trigger.idx == "release":
                    ctrl_panel.set({
                        "release-val": trigger.value,
                        "help-dis": C.STYLE_DISPLAY,
                        "help-val": "<DUT version> <topo> <arch> <nic> " + \
                            "<driver> <framesize> <core> <test>",
                        "search-dis": C.STYLE_DISPLAY,
                        "search-val": str()
                    })
                elif trigger.idx == "search":
                    ctrl_panel.set({"search-val": trigger.value})
                    selection = {
                        "datatype": ctrl_panel.get("datatype-val"),
                        "dut": ctrl_panel.get("dut-val"),
                        "release": ctrl_panel.get("release-val"),
                        "help": ctrl_panel.get("help-val"),
                        "regexp":  ctrl_panel.get("search-val"),
                    }
                    on_draw = True
            elif trigger.type == "table" and trigger.idx == "search":
                if trigger.parameter == "filter_query":
                    filtered_data = filter_table_data(
                        store_table_data,
                        trigger.value
                    )
                elif trigger.parameter == "sort_by":
                    filtered_data = sort_table_data(
                        store_table_data,
                        trigger.value
                    )
                table_data = [filtered_data, ]

            if on_draw:
                table = search_table(data=self._data, selection=selection)
                plotting_area = Layout._get_plotting_area(
                    table,
                    gen_new_url(parsed_url, {"selection": selection})
                )
                store_table_data = table.to_dict("records")
                filtered_data = store_table_data
                if table_data:
                    table_data = [store_table_data, ]
            else:
                plotting_area = no_update

            store["control-panel"] = ctrl_panel.panel
            store["selection"] = selection
            ret_val = [
                store,
                store_table_data,
                filtered_data,
                plotting_area,
                table_data
            ]
            ret_val.extend(ctrl_panel.values)

            return ret_val

        @app.callback(
            Output("offcanvas-details", "is_open"),
            Output("offcanvas-details", "children"),
            State("store", "data"),
            State("store-filtered-table-data", "data"),
            Input({"type": "table", "index": ALL}, "active_cell"),
            prevent_initial_call=True
        )
        def show_test_data(store, table, *_):
            """Show offcanvas with graphs and tables based on selected test(s).
            """

            trigger = Trigger(callback_context.triggered)
            if not trigger.value:
                raise PreventUpdate

            try:
                row = pd.DataFrame.from_records(table).\
                    iloc[[trigger.value["row"]]]
                datatype = store["selection"]["datatype"]
                dut = store["selection"]["dut"]
                rls = store["selection"]["release"]
                tb = row["Test Bed"].iloc[0]
                nic = row["NIC"].iloc[0]
                driver = row["Driver"].iloc[0]
                test_name = row["Test"].iloc[0]
                dutver = str()
            except(KeyError, IndexError, AttributeError, ValueError):
                raise PreventUpdate

            data = self._data[datatype]
            if datatype == "trending":
                df = pd.DataFrame(data.loc[data["dut_type"] == dut])
            else:
                dutver = row["DUT Version"].iloc[0]
                df = pd.DataFrame(data.loc[(
                    (data["dut_type"] == dut) &
                    (data["dut_version"] == dutver) &
                    (data["release"] == rls)
                )])
            tb_1, tb_2 = tb.split("-", maxsplit=1)
            df = df[df.full_id.str.contains(
                f".*{tb_1}.*{tb_2}.*{nic}.*{test_name}",
                regex=True
            )]

            if datatype in ("trending", "iterative"):
                l_test_id = df["test_id"].iloc[0].split(".")
                if dut == "dpdk":
                    area = "dpdk"
                else:
                    area = ".".join(l_test_id[3:-2])
                for drv in C.DRIVERS:
                    if drv in test_name:
                        test = test_name.replace(f"{drv}-", "")
                        break
                else:
                    test = test_name
                l_test = test.split("-")
                testtype = l_test[-1]
                if testtype == "ndrpdr":
                    testtype = ["ndr", "pdr"]
                else:
                    testtype = [testtype, ]
                core = l_test[1] if l_test[1] else "8c"
                test = "-".join(l_test[2: -1])
                test_id = f"{tb}-{nic}-{driver}-{l_test[0]}-{core}-{test}"
                title = dbc.Row(
                    class_name="g-0 p-0",
                    children=dbc.Alert(test_id, color="info"),
                )
                selected = list()
                indexes = ("tput", "bandwidth", "lat")
                if datatype == "trending":
                    for ttype in testtype:
                        selected.append({
                            "id": f"{dut}-{test_id}-{ttype}",
                            "dut": dut,
                            "phy": f"{tb}-{nic}-{driver}",
                            "area": area,
                            "test": test,
                            "framesize": l_test[0],
                            "core": core,
                            "testtype": ttype
                        })
                    graphs = graph_trending(df, selected, self._graph_layout)
                    labels = ("Throughput", "Bandwidth", "Latency")
                    tabs = list()
                    for graph, label, idx in zip(graphs, labels, indexes):
                        if graph:
                            tabs.append(dbc.Tab(
                                children=dcc.Graph(
                                    figure=graph,
                                    id={"type": "graph-trend", "index": idx},
                                ),
                                label=label
                            ))
                    if tabs:
                        ret_val = [
                            title,
                            dbc.Row(dbc.Tabs(tabs), class_name="g-0 p-0")
                        ]
                    else:
                        ret_val = [
                            title,
                            dbc.Row("No data.", class_name="g-0 p-0")
                        ]

                else:  # Iterative
                    for ttype in testtype:
                        selected.append({
                            "id": f"{test_id}-{ttype}",
                            "rls": rls,
                            "dut": dut,
                            "dutver": dutver,
                            "phy": f"{tb}-{nic}-{driver}",
                            "area": area,
                            "test": test,
                            "framesize": l_test[0],
                            "core": core,
                            "testtype": ttype
                        })
                    graphs = graph_iterative(df, selected, self._graph_layout)
                    cols = list()
                    for graph, idx in zip(graphs, indexes):
                        if graph:
                            cols.append(dbc.Col(dcc.Graph(
                                figure=graph,
                                id={"type": "graph-iter", "index": idx},
                            )))
                    if not cols:
                        cols="No data."
                    ret_val = [
                        title,
                        dbc.Row(class_name="g-0 p-0", children=cols)
                    ]

            elif datatype == "coverage":
                ret_val = coverage_tables(
                    data=df,
                    selected={
                        "rls": rls,
                        "dut": dut,
                        "dutver": dutver,
                        "phy": f"{tb}-{nic}-{driver}",
                        "area": ".*",
                    },
                    start_collapsed=False
                )
            else:
                raise PreventUpdate

            return True, ret_val

        @app.callback(
            Output("metadata-tput-lat", "children"),
            Output("metadata-hdrh-graph", "children"),
            Output("offcanvas-metadata", "is_open"),
            Input({"type": "graph-trend", "index": ALL}, "clickData"),
            Input({"type": "graph-iter", "index": ALL}, "clickData"),
            prevent_initial_call=True
        )
        def _show_metadata_from_graph(
                trend_data: dict,
                iter_data: dict
            ) -> tuple:
            """Generates the data for the offcanvas displayed when a particular
            point in a graph is clicked on.
            """

            trigger = Trigger(callback_context.triggered)
            if not trigger.value:
                raise PreventUpdate

            if trigger.type == "graph-trend":
                return show_trending_graph_data(
                    trigger, trend_data, self._graph_layout)
            elif trigger.type == "graph-iter":
                return show_iterative_graph_data(
                    trigger, iter_data, self._graph_layout)
            else:
                raise PreventUpdate

        @app.callback(
            Output("plot-mod-url", "is_open"),
            Input("plot-btn-url", "n_clicks"),
            State("plot-mod-url", "is_open")
        )
        def toggle_plot_mod_url(n, is_open):
            """Toggle the modal window with url.
            """
            if n:
                return not is_open
            return is_open

        @app.callback(
            Output("download-data", "data"),
            State("store-filtered-table-data", "data"),
            Input("plot-btn-download", "n_clicks"),
            prevent_initial_call=True
        )
        def _download_search_data(selection, _):
            """Download the data.

            :param selection: Selected data in table format (records).
            :type selection: dict
            :returns: dict of data frame content (base64 encoded) and meta data
                used by the Download component.
            :rtype: dict
            """

            if not selection:
                raise PreventUpdate

            return dcc.send_data_frame(
                pd.DataFrame.from_records(selection).to_csv,
                C.SEARCH_DOWNLOAD_FILE_NAME
            )

        @app.callback(
            Output("offcanvas-documentation", "is_open"),
            Input("btn-documentation", "n_clicks"),
            State("offcanvas-documentation", "is_open")
        )
        def toggle_offcanvas_documentation(n_clicks, is_open):
            if n_clicks:
                return not is_open
            return is_open
