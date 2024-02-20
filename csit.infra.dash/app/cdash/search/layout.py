# Copyright (c) 2023 Cisco and/or its affiliates.
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
from copy import deepcopy

from ..utils.constants import Constants as C
from ..utils.control_panel import ControlPanel
from ..utils.trigger import Trigger
from ..utils.telemetry_data import TelemetryData
from ..utils.utils import show_tooltip, label, sync_checklists, gen_new_url, \
    generate_options, get_list_group_items, graph_hdrh_latency, navbar_trending, filter_table_data
from ..utils.url_processing import url_decode
from .tables import search_table
#from .graphs import graph_trending, select_trending_data, graph_tm_trending


# Control panel partameters and their default values.
CP_PARAMS = {
    "dd-datatype-val": str(),
    "dd-dut-opt": list(),
    "dd-dut-dis": C.STYLE_DONT_DISPLAY,
    "dd-dut-val": str(),
    "dd-release-opt": list(),
    "dd-release-dis": C.STYLE_DONT_DISPLAY,
    "dd-release-val": str(),
    "dd-search-dis": C.STYLE_DONT_DISPLAY,
    "dd-search-val": str()
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

        # Get structure of tests:
        self._duts = dict()
        for data_type, pd in self._data.items():
            if pd.empty:
                continue
            self._duts[data_type] = dict()
            if data_type in ("iterative", "coverage", ):
                cols = ["dut_type", "release", ]
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
                            class_name="w-50",
                            id="offcanvas-metadata",
                            title="Test Details",
                            placement="end",
                            is_open=False,
                            children=[]
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
                            dbc.InputGroupText("Data Type"),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "datatype"},
                                placeholder="Select a Data Type...",
                                options=sorted(
                                    [
                                        {"label": k, "value": k} \
                                            for k in self._duts.keys()
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
                            dbc.InputGroupText("DUT"),
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
                            dbc.InputGroupText("Release"),
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
        """Add column with plots. It is placed on the right side.

        :returns: Column with plots.
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
                            children=[
                                C.PLACEHOLDER
                            ]
                        )
                    ]
                )
            ],
            width=9
        )

    @staticmethod
    def _get_plotting_area(table: pd.DataFrame, url: str=str()) -> list:
        """Generate the plotting area with all its content.

        :param table: Search table to be displayed.
        :type table: pandas.DataFrame
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

        columns = [{"name": i, "id": i, "selectable": True} \
                   for i in table.columns]

        return [
            dbc.Row(
                children=[
                    dbc.Col(
                        children=dash_table.DataTable(
                            id={"type": "table", "index": "search"},
                            columns=columns,
                            data=table.to_dict("records"),
                            merge_duplicate_headers=True,
                            editable=False,
                            filter_action="custom",
                            filter_query="",
                            sort_action="native",
                            sort_mode="multi",
                            row_selectable=False,
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
                            dcc.Download(id="download-iterative-data")
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
            Output({"type": "ctrl-row", "index": "search"}, "style"),
            Output({"type": "ctrl-dd", "index": "search"}, "value"),

            State("store", "data"),
            State("store-table-data", "data"),
            State("store-filtered-table-data", "data"),
            State({"type": "table", "index": ALL}, "data"),

            Input("url", "href"),
            Input({"type": "table", "index": ALL}, "filter_query"),
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
                    "selection": dict(),
                    "url": str()
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
                        "dd-datatype-val": trigger.value,
                        "dd-dut-opt": options,
                        "dd-dut-dis": disabled,
                        "dd-dut-val": str(),
                        "dd-release-opt": list(),
                        "dd-release-dis": C.STYLE_DONT_DISPLAY,
                        "dd-release-val": str(),
                        "dd-search-dis": C.STYLE_DONT_DISPLAY,
                        "dd-search-val": str()
                    })
                elif trigger.idx == "dut":
                    try:
                        data_type = ctrl_panel.get("dd-datatype-val")
                        dut = self._duts[data_type][trigger.value]
                        if data_type != "trending":
                            options = generate_options(dut)
                        disabled = C.STYLE_DISPLAY
                    except KeyError:
                        options = list()
                        disabled = C.STYLE_DONT_DISPLAY
                    if data_type == "trending":
                        ctrl_panel.set({
                            "dd-dut-val": trigger.value,
                            "dd-release-opt": list(),
                            "dd-release-dis": C.STYLE_DONT_DISPLAY,
                            "dd-release-val": str(),
                            "dd-search-dis": disabled,
                            "dd-search-val": str()
                        })
                    else:
                        ctrl_panel.set({
                            "dd-dut-val": trigger.value,
                            "dd-release-opt": options,
                            "dd-release-dis": disabled,
                            "dd-release-val": str(),
                            "dd-search-dis": C.STYLE_DONT_DISPLAY,
                            "dd-search-val": str()
                        })
                elif trigger.idx == "release":
                    ctrl_panel.set({
                        "dd-release-val": trigger.value,
                        "dd-search-dis": C.STYLE_DISPLAY,
                        "dd-search-val": str()
                    })
                elif trigger.idx == "search":
                    ctrl_panel.set({"dd-search-val": trigger.value})
                    selection = {
                        "datatype": ctrl_panel.get("dd-datatype-val"),
                        "dut": ctrl_panel.get("dd-dut-val"),
                        "release": ctrl_panel.get("dd-release-val"),
                        "regexp":  ctrl_panel.get("dd-search-val"),
                    }
                    on_draw = True
            elif trigger.type == "table" and trigger.idx == "search":
                logging.info(trigger)
                filtered_data = filter_table_data(
                    store_table_data,
                    trigger.value
                )
                table_data = [filtered_data, ]

            if on_draw:
                table = search_table(data=self._data, selection=selection)
                plotting_area = Layout._get_plotting_area(table)
                store_table_data = table.to_dict("records")
                filtered_data = store_table_data
                if table_data:
                    table_data = [store_table_data, ]
            else:
                plotting_area = no_update  # or C.PLACEHOLDER

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
            Output("offcanvas-metadata", "is_open"),
            Output("offcanvas-metadata", "children"),
            Input({"type": "table", "index": ALL}, "active_cell"),
            prevent_initial_call=True
        )
        def show_test_data(*_):
            """
            """
            trigger = Trigger(callback_context.triggered)
            if not trigger.value:
                raise PreventUpdate

            return True, str(trigger)

        @app.callback(
            Output("offcanvas-documentation", "is_open"),
            Input("btn-documentation", "n_clicks"),
            State("offcanvas-documentation", "is_open")
        )
        def toggle_offcanvas_documentation(n_clicks, is_open):
            if n_clicks:
                return not is_open
            return is_open
