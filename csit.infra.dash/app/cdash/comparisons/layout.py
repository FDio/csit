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
from dash import dcc, html, dash_table, callback_context, no_update, ALL
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from dash.dash_table.Format import Format, Scheme
from ast import literal_eval
from yaml import load, FullLoader, YAMLError
from copy import deepcopy

from ..utils.constants import Constants as C
from ..utils.control_panel import ControlPanel
from ..utils.trigger import Trigger
from ..utils.url_processing import url_decode
from ..utils.utils import generate_options, gen_new_url, navbar_report, \
    filter_table_data, sort_table_data, show_iterative_graph_data, \
    show_tooltip, get_topo_arch
from .tables import comparison_table
from ..report.graphs import graph_iterative


# Control panel partameters and their default values.
CP_PARAMS = {
    "dut-val": str(),
    "dutver-opt": list(),
    "dutver-dis": True,
    "dutver-val": str(),
    "infra-opt": list(),
    "infra-dis": True,
    "infra-val": str(),
    "core-opt": list(),
    "core-val": list(),
    "frmsize-opt": list(),
    "frmsize-val": list(),
    "ttype-opt": list(),
    "ttype-val": list(),
    "cmp-par-opt": list(),
    "cmp-par-dis": True,
    "cmp-par-val": str(),
    "cmp-val-opt": list(),
    "cmp-val-dis": True,
    "cmp-val-val": str(),
    "normalize-val": list(),
    "outliers-val": list()
}

# List of comparable parameters.
CMP_PARAMS = {
    "dutver": "Release and Version",
    "infra": "Infrastructure",
    "frmsize": "Frame Size",
    "core": "Number of Cores",
    "ttype": "Measurement"
}


class Layout:
    """The layout of the dash app and the callbacks.
    """

    def __init__(
            self,
            app: Flask,
            data_iterative: pd.DataFrame,
            html_layout_file: str,
            graph_layout_file: str,
            tooltip_file: str
        ) -> None:
        """Initialization:
        - save the input parameters,
        - prepare data for the control panel,
        - read HTML layout file,
        - read graph layout file,
        - read tooltips from the tooltip file.

        :param app: Flask application running the dash application.
        :param data_iterative: Iterative data to be used in comparison tables.
        :param html_layout_file: Path and name of the file specifying the HTML
            layout of the dash application.
        :param tooltip_file: Path and name of the yaml file specifying the
            tooltips.
        :param graph_layout_file: Path and name of the file with layout of
            plot.ly graphs.
        :type app: Flask
        :type data_iterative: pandas.DataFrame
        :type html_layout_file: str
        :type graph_layout_file: str
        :type tooltip_file: str
        """

        # Inputs
        self._app = app
        self._data = data_iterative
        self._html_layout_file = html_layout_file
        self._graph_layout_file = graph_layout_file
        self._tooltip_file = tooltip_file

        # Get structure of tests:
        tbs = dict()
        cols = [
            "job", "test_id", "test_type", "dut_type", "dut_version", "tg_type",
            "release", "passed"
        ]
        for _, row in self._data[cols].drop_duplicates().iterrows():
            lst_job = row["job"].split("-")
            dut = lst_job[1]
            dver = f"{row['release']}-{row['dut_version']}"
            tbed = get_topo_arch(lst_job)
            lst_test_id = row["test_id"].split(".")

            suite = lst_test_id[-2].replace("2n1l-", "").replace("1n1l-", "").\
                replace("2n-", "")
            test = lst_test_id[-1]
            nic = suite.split("-")[0]
            for driver in C.DRIVERS:
                if driver in test:
                    drv = driver.replace("-", "_")
                    test = test.replace(f"{driver}-", "")
                    break
            else:
                drv = "dpdk"
            infra = "-".join((tbed, nic, drv))
            lst_test = test.split("-")
            fsize = lst_test[0]
            core = lst_test[1] if lst_test[1] else "8C"

            if tbs.get(dut, None) is None:
                tbs[dut] = dict()
            if tbs[dut].get(dver, None) is None:
                tbs[dut][dver] = dict()
            if tbs[dut][dver].get(infra, None) is None:
                tbs[dut][dver][infra] = dict()
                tbs[dut][dver][infra]["core"] = list()
                tbs[dut][dver][infra]["fsize"] = list()
                tbs[dut][dver][infra]["ttype"] = list()
            if core.upper() not in tbs[dut][dver][infra]["core"]:
                tbs[dut][dver][infra]["core"].append(core.upper())
            if fsize.upper() not in tbs[dut][dver][infra]["fsize"]:
                tbs[dut][dver][infra]["fsize"].append(fsize.upper())
            if row["test_type"] == "mrr":
                if "MRR" not in tbs[dut][dver][infra]["ttype"]:
                    tbs[dut][dver][infra]["ttype"].append("MRR")
            elif row["test_type"] == "ndrpdr":
                if "NDR" not in tbs[dut][dver][infra]["ttype"]:
                    tbs[dut][dver][infra]["ttype"].extend(
                        ("NDR", "PDR", "Latency")
                    )
            elif row["test_type"] == "hoststack" and \
                    row["tg_type"] in ("iperf", "vpp"):
                if "BPS" not in tbs[dut][dver][infra]["ttype"]:
                    tbs[dut][dver][infra]["ttype"].append("BPS")
            elif row["test_type"] == "hoststack" and row["tg_type"] == "ab":
                if "CPS" not in tbs[dut][dver][infra]["ttype"]:
                    tbs[dut][dver][infra]["ttype"].extend(("CPS", "RPS", ))
            elif row["test_type"] == "soak":
                if "SOAK" not in tbs[dut][dver][infra]["ttype"]:
                    tbs[dut][dver][infra]["ttype"].append("SOAK")
        self._tbs = tbs

        # Read from files:
        self._html_layout = str()
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

        if self.html_layout and self._tbs:
            return html.Div(
                id="div-main",
                className="small",
                children=[
                    dbc.Row(
                        id="row-navbar",
                        class_name="g-0",
                        children=[navbar_report((False, True, False, False)), ]
                    ),
                    dbc.Row(
                        id="row-main",
                        class_name="g-0",
                        children=[
                            dcc.Store(id="store-control-panel"),
                            dcc.Store(id="store-selected"),
                            dcc.Store(id="store-table-data"),
                            dcc.Store(id="store-filtered-table-data"),
                            dcc.Location(id="url", refresh=False),
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
                            src=C.URL_DOC_REL_NOTES,
                            width="100%",
                            height="100%"
                        )
                    )
                ]
            )
        else:
            return html.Div(
                id="div-main-error",
                children=[
                    dbc.Alert(
                        [
                            "An Error Occured"
                        ],
                        color="danger"
                    )
                ]
            )

    def _add_ctrl_col(self) -> dbc.Col:
        """Add column with controls. It is placed on the left side.

        :returns: Column with the control panel.
        :rtype: dbc.Col
        """
        return dbc.Col([
            html.Div(
                children=self._add_ctrl_panel(),
                className="sticky-top"
            )
        ])

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

    def _add_ctrl_panel(self) -> list:
        """Add control panel.

        :returns: Control panel.
        :rtype: list
        """

        reference = [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                show_tooltip(self._tooltips, "help-dut", "DUT")
                            ),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "dut"},
                                placeholder="Select a Device under Test...",
                                options=sorted(
                                    [
                                        {"label": k, "value": k} \
                                            for k in self._tbs.keys()
                                    ],
                                    key=lambda d: d["label"]
                                )
                            )
                        ],
                        size="sm"
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-csit-dut",
                                "CSIT and DUT Version"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "dutver"},
                                placeholder="Select a CSIT and DUT Version...")
                        ],
                        size="sm"
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-infra",
                                "Infra"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "infra"},
                                placeholder=\
                                    "Select a Physical Test Bed Topology..."
                            )
                        ],
                        size="sm"
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-framesize",
                                "Frame Size"
                            )),
                            dbc.Checklist(
                                id={"type": "ctrl-cl", "index": "frmsize"},
                                inline=True,
                                class_name="ms-2"
                            )
                        ],
                        style={"align-items": "center"},
                        size="sm"
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-cores",
                                "Number of Cores"
                            )),
                            dbc.Checklist(
                                id={"type": "ctrl-cl", "index": "core"},
                                inline=True,
                                class_name="ms-2"
                            )
                        ],
                        style={"align-items": "center"},
                        size="sm"
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-measurement",
                                "Measurement"
                            )),
                            dbc.Checklist(
                                id={"type": "ctrl-cl", "index": "ttype"},
                                inline=True,
                                class_name="ms-2"
                            )
                        ],
                        style={"align-items": "center"},
                        size="sm"
                    )
                ]
            )
        ]

        compare = [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-cmp-parameter",
                                "Parameter"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "cmpprm"},
                                placeholder="Select a Parameter..."
                            )
                        ],
                        size="sm"
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-cmp-value",
                                "Value"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "cmpval"},
                                placeholder="Select a Value..."
                            )
                        ],
                        size="sm"
                    )
                ]
            )
        ]

        processing = [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        children = [
                            dbc.Checklist(
                                id="normalize",
                                options=[{
                                    "value": "normalize",
                                    "label": "Normalize to 2GHz CPU frequency"
                                }],
                                value=[],
                                inline=True,
                                class_name="ms-2"
                            ),
                            dbc.Checklist(
                                id="outliers",
                                options=[{
                                    "value": "outliers",
                                    "label": "Remove Extreme Outliers"
                                }],
                                value=[],
                                inline=True,
                                class_name="ms-2"
                            )
                        ],
                        style={"align-items": "center"},
                        size="sm"
                    )
                ]
            )
        ]

        return [
            dbc.Row(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5("Reference Value")
                        ),
                        dbc.CardBody(
                            children=reference,
                            class_name="g-0 p-0"
                        )
                    ],
                    color="secondary",
                    outline=True
                ),
                class_name="g-0 p-1"
            ),
            dbc.Row(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5("Compared Value")
                        ),
                        dbc.CardBody(
                            children=compare,
                            class_name="g-0 p-0"
                        )
                    ],
                    color="secondary",
                    outline=True
                ),
                class_name="g-0 p-1"
            ),
            dbc.Row(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5("Data Manipulations")
                        ),
                        dbc.CardBody(
                            children=processing,
                            class_name="g-0 p-0"
                        )
                    ],
                    color="secondary",
                    outline=True
                ),
                class_name="g-0 p-1"
            )
        ]

    @staticmethod
    def _get_plotting_area(
            title: str,
            table: pd.DataFrame,
            url: str
        ) -> list:
        """Generate the plotting area with all its content.

        :param title: The title of the comparison table.
        :param table: Comparison table to be displayed.
        :param url: URL to be displayed in the modal window.
        :type title: str
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
                        "No data for comparison.",
                        color="danger"
                    ),
                    class_name="g-0 p-1",
                ),
                class_name="g-0 p-0"
            )

        cols = list()
        for idx, col in enumerate(table.columns):
            if idx == 0:
                cols.append({
                    "name": ["", col],
                    "id": col,
                    "deletable": False,
                    "selectable": False,
                    "type": "text"
                })
            else:
                l_col = col.rsplit(" ", 2)
                cols.append({
                    "name": [l_col[0], " ".join(l_col[-2:])],
                    "id": col,
                    "deletable": False,
                    "selectable": False,
                    "type": "numeric",
                    "format": Format(precision=2, scheme=Scheme.fixed)
                })

        return [
            dbc.Row(
                children=html.H5(title),
                class_name="g-0 p-1"
            ),
            dbc.Row(
                children=[
                    dbc.Col(
                        children=dash_table.DataTable(
                            id={"type": "table", "index": "comparison"},
                            columns=cols,
                            data=table.to_dict("records"),
                            merge_duplicate_headers=True,
                            editable=False,
                            filter_action="custom",
                            filter_query="",
                            sort_action="custom",
                            sort_mode="multi",
                            selected_columns=[],
                            selected_rows=[],
                            page_action="none",
                            style_cell={"textAlign": "right"},
                            style_cell_conditional=[{
                                "if": {"column_id": "Test Name"},
                                "textAlign": "left"
                            }]
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
                                children="Download Table",
                                class_name="me-1",
                                color="info",
                                style={
                                    "text-transform": "none",
                                    "padding": "0rem 1rem"
                                }
                            ),
                            dcc.Download(id="download-iterative-data"),
                            dbc.Button(
                                id="plot-btn-download-raw",
                                children="Download Raw Data",
                                class_name="me-1",
                                color="info",
                                style={
                                    "text-transform": "none",
                                    "padding": "0rem 1rem"
                                }
                            ),
                            dcc.Download(id="download-raw-data")
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
            [
                Output("store-control-panel", "data"),
                Output("store-selected", "data"),
                Output("store-table-data", "data"),
                Output("store-filtered-table-data", "data"),
                Output("plotting-area", "children"),
                Output({"type": "table", "index": ALL}, "data"),
                Output({"type": "ctrl-dd", "index": "dut"}, "value"),
                Output({"type": "ctrl-dd", "index": "dutver"}, "options"),
                Output({"type": "ctrl-dd", "index": "dutver"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "dutver"}, "value"),
                Output({"type": "ctrl-dd", "index": "infra"}, "options"),
                Output({"type": "ctrl-dd", "index": "infra"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "infra"}, "value"),
                Output({"type": "ctrl-cl", "index": "core"}, "options"),
                Output({"type": "ctrl-cl", "index": "core"}, "value"),
                Output({"type": "ctrl-cl", "index": "frmsize"}, "options"),
                Output({"type": "ctrl-cl", "index": "frmsize"}, "value"),
                Output({"type": "ctrl-cl", "index": "ttype"}, "options"),
                Output({"type": "ctrl-cl", "index": "ttype"}, "value"),
                Output({"type": "ctrl-dd", "index": "cmpprm"}, "options"),
                Output({"type": "ctrl-dd", "index": "cmpprm"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "cmpprm"}, "value"),
                Output({"type": "ctrl-dd", "index": "cmpval"}, "options"),
                Output({"type": "ctrl-dd", "index": "cmpval"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "cmpval"}, "value"),
                Output("normalize", "value"),
                Output("outliers", "value")
            ],
            [
                State("store-control-panel", "data"),
                State("store-selected", "data"),
                State("store-table-data", "data"),
                State("store-filtered-table-data", "data"),
                State({"type": "table", "index": ALL}, "data")
            ],
            [
                Input("url", "href"),
                Input("normalize", "value"),
                Input("outliers", "value"),
                Input({"type": "table", "index": ALL}, "filter_query"),
                Input({"type": "table", "index": ALL}, "sort_by"),
                Input({"type": "ctrl-dd", "index": ALL}, "value"),
                Input({"type": "ctrl-cl", "index": ALL}, "value"),
                Input({"type": "ctrl-btn", "index": ALL}, "n_clicks")
            ]
        )
        def _update_application(
                control_panel: dict,
                selected: dict,
                store_table_data: list,
                filtered_data: list,
                table_data: list,
                href: str,
                normalize: list,
                outliers: bool,
                *_
            ) -> tuple:
            """Update the application when the event is detected.
            """

            ctrl_panel = ControlPanel(CP_PARAMS, control_panel)

            if selected is None:
                selected = {
                    "reference": {
                        "set": False,
                    },
                    "compare": {
                        "set": False,
                    }
                }

            # Parse the url:
            parsed_url = url_decode(href)
            if parsed_url:
                url_params = parsed_url["params"]
            else:
                url_params = None

            on_draw = False
            plotting_area = no_update

            trigger = Trigger(callback_context.triggered)
            if trigger.type == "url" and url_params:
                process_url = False
                try:
                    selected = literal_eval(url_params["selected"][0])
                    r_sel = selected["reference"]["selection"]
                    c_sel = selected["compare"]
                    normalize = literal_eval(url_params["norm"][0])
                    try:  # Necessary for backward compatibility
                        outliers = literal_eval(url_params["outliers"][0])
                    except (KeyError, IndexError, AttributeError):
                        outliers = list()
                    process_url = bool(
                        (selected["reference"]["set"] == True) and
                        (c_sel["set"] == True)
                    )
                except (KeyError, IndexError, AttributeError):
                    pass
                if process_url:
                    ctrl_panel.set({
                        "dut-val": r_sel["dut"],
                        "dutver-opt": generate_options(
                            self._tbs[r_sel["dut"]].keys()
                        ),
                        "dutver-dis": False,
                        "dutver-val": r_sel["dutver"],
                        "infra-opt": generate_options(
                            self._tbs[r_sel["dut"]][r_sel["dutver"]].keys()
                        ),
                        "infra-dis": False,
                        "infra-val": r_sel["infra"],
                        "core-opt": generate_options(
                            self._tbs[r_sel["dut"]][r_sel["dutver"]]\
                                [r_sel["infra"]]["core"]
                        ),
                        "core-val": r_sel["core"],
                        "frmsize-opt": generate_options(
                            self._tbs[r_sel["dut"]][r_sel["dutver"]]\
                                [r_sel["infra"]]["fsize"]
                        ),
                        "frmsize-val": r_sel["frmsize"],
                        "ttype-opt": generate_options(
                            self._tbs[r_sel["dut"]][r_sel["dutver"]]\
                                [r_sel["infra"]]["ttype"]
                        ),
                        "ttype-val": r_sel["ttype"],
                        "normalize-val": normalize,
                        "outliers-val": outliers
                    })
                    opts = list()
                    for itm, label in CMP_PARAMS.items():
                        if len(ctrl_panel.get(f"{itm}-opt")) > 1:
                            opts.append({"label": label, "value": itm})
                    ctrl_panel.set({
                        "cmp-par-opt": opts,
                        "cmp-par-dis": False,
                        "cmp-par-val": c_sel["parameter"]
                    })
                    opts = list()
                    for itm in ctrl_panel.get(f"{c_sel['parameter']}-opt"):
                        set_val = ctrl_panel.get(f"{c_sel['parameter']}-val")
                        if isinstance(set_val, list):
                            if itm["value"] not in set_val:
                                opts.append(itm)
                        else:
                            if itm["value"] != set_val:
                                opts.append(itm)
                    ctrl_panel.set({
                        "cmp-val-opt": opts,
                        "cmp-val-dis": False,
                        "cmp-val-val": c_sel["value"]
                    })
                    on_draw = True
            elif trigger.type == "normalize":
                ctrl_panel.set({"normalize-val": normalize})
                on_draw = True
            elif trigger.type == "outliers":
                ctrl_panel.set({"outliers-val": outliers})
                on_draw = True
            elif trigger.type == "ctrl-dd":
                if trigger.idx == "dut":
                    try:
                        opts = generate_options(self._tbs[trigger.value].keys())
                        disabled = False
                    except KeyError:
                        opts = list()
                        disabled = True
                    ctrl_panel.set({
                        "dut-val": trigger.value,
                        "dutver-opt": opts,
                        "dutver-dis": disabled,
                        "dutver-val": str(),
                        "infra-opt": list(),
                        "infra-dis": True,
                        "infra-val": str(),
                        "core-opt": list(),
                        "core-val": list(),
                        "frmsize-opt": list(),
                        "frmsize-val": list(),
                        "ttype-opt": list(),
                        "ttype-val": list(),
                        "cmp-par-opt": list(),
                        "cmp-par-dis": True,
                        "cmp-par-val": str(),
                        "cmp-val-opt": list(),
                        "cmp-val-dis": True,
                        "cmp-val-val": str()
                    })
                elif trigger.idx == "dutver":
                    try:
                        dut = ctrl_panel.get("dut-val")
                        dver = self._tbs[dut][trigger.value]
                        opts = generate_options(dver.keys())
                        disabled = False
                    except KeyError:
                        opts = list()
                        disabled = True
                    ctrl_panel.set({
                        "dutver-val": trigger.value,
                        "infra-opt": opts,
                        "infra-dis": disabled,
                        "infra-val": str(),
                        "core-opt": list(),
                        "core-val": list(),
                        "frmsize-opt": list(),
                        "frmsize-val": list(),
                        "ttype-opt": list(),
                        "ttype-val": list(),
                        "cmp-par-opt": list(),
                        "cmp-par-dis": True,
                        "cmp-par-val": str(),
                        "cmp-val-opt": list(),
                        "cmp-val-dis": True,
                        "cmp-val-val": str()
                    })
                elif trigger.idx == "infra":
                    dut = ctrl_panel.get("dut-val")
                    dver = ctrl_panel.get("dutver-val")
                    if all((dut, dver, trigger.value, )):
                        driver = self._tbs[dut][dver][trigger.value]
                        ctrl_panel.set({
                            "infra-val": trigger.value,
                            "core-opt": generate_options(driver["core"]),
                            "core-val": list(),
                            "frmsize-opt": generate_options(driver["fsize"]),
                            "frmsize-val": list(),
                            "ttype-opt": generate_options(driver["ttype"]),
                            "ttype-val": list(),
                            "cmp-par-opt": list(),
                            "cmp-par-dis": True,
                            "cmp-par-val": str(),
                            "cmp-val-opt": list(),
                            "cmp-val-dis": True,
                            "cmp-val-val": str()
                        })
                elif trigger.idx == "cmpprm":
                    value = trigger.value
                    opts = list()
                    for itm in ctrl_panel.get(f"{value}-opt"):
                        set_val = ctrl_panel.get(f"{value}-val")
                        if isinstance(set_val, list):
                            if itm["value"] == "Latency":
                                continue
                            if itm["value"] not in set_val:
                                opts.append(itm)
                        else:
                            if itm["value"] != set_val:
                                opts.append(itm)
                    ctrl_panel.set({
                        "cmp-par-val": value,
                        "cmp-val-opt": opts,
                        "cmp-val-dis": False,
                        "cmp-val-val": str()
                    })
                elif trigger.idx == "cmpval":
                    ctrl_panel.set({"cmp-val-val": trigger.value})
                    selected["reference"] = {
                        "set": True,
                        "selection": {
                            "dut": ctrl_panel.get("dut-val"),
                            "dutver": ctrl_panel.get("dutver-val"),
                            "infra": ctrl_panel.get("infra-val"),
                            "core": ctrl_panel.get("core-val"),
                            "frmsize": ctrl_panel.get("frmsize-val"),
                            "ttype": ctrl_panel.get("ttype-val")
                        }
                    }
                    selected["compare"] = {
                        "set": True,
                        "parameter": ctrl_panel.get("cmp-par-val"),
                        "value": trigger.value
                    }
                    on_draw = True
            elif trigger.type == "ctrl-cl":
                ctrl_panel.set({f"{trigger.idx}-val": trigger.value})
                if all((ctrl_panel.get("core-val"),
                        ctrl_panel.get("frmsize-val"),
                        ctrl_panel.get("ttype-val"), )):
                    if "Latency" in ctrl_panel.get("ttype-val"):
                        ctrl_panel.set({"ttype-val": ["Latency", ]})
                    opts = list()
                    for itm, label in CMP_PARAMS.items():
                        if "Latency" in ctrl_panel.get("ttype-val") and \
                                itm == "ttype":
                            continue
                        if len(ctrl_panel.get(f"{itm}-opt")) > 1:
                            if isinstance(ctrl_panel.get(f"{itm}-val"), list):
                                if len(ctrl_panel.get(f"{itm}-opt")) == \
                                        len(ctrl_panel.get(f"{itm}-val")):
                                    continue
                            opts.append({"label": label, "value": itm})
                    ctrl_panel.set({
                        "cmp-par-opt": opts,
                        "cmp-par-dis": False,
                        "cmp-par-val": str(),
                        "cmp-val-opt": list(),
                        "cmp-val-dis": True,
                        "cmp-val-val": str()
                    })
                else:
                    ctrl_panel.set({
                        "cmp-par-opt": list(),
                        "cmp-par-dis": True,
                        "cmp-par-val": str(),
                        "cmp-val-opt": list(),
                        "cmp-val-dis": True,
                        "cmp-val-val": str()
                    })
            elif trigger.type == "table" and trigger.idx == "comparison":
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

            if all((on_draw, selected["reference"]["set"],
                    selected["compare"]["set"], )):
                title, table = comparison_table(
                    data=self._data,
                    selected=selected,
                    normalize=normalize,
                    format="html",
                    remove_outliers=outliers
                )
                plotting_area = self._get_plotting_area(
                    title=title,
                    table=table,
                    url=gen_new_url(
                        parsed_url,
                        params={
                            "selected": selected,
                            "norm": normalize,
                            "outliers": outliers
                        }
                    )
                )
                store_table_data = table.to_dict("records")
                filtered_data = store_table_data
                if table_data:
                    table_data = [store_table_data, ]

            ret_val = [
                ctrl_panel.panel,
                selected,
                store_table_data,
                filtered_data,
                plotting_area,
                table_data
            ]
            ret_val.extend(ctrl_panel.values)
            return ret_val

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
            Output("download-iterative-data", "data"),
            State("store-table-data", "data"),
            State("store-filtered-table-data", "data"),
            Input("plot-btn-download", "n_clicks"),
            prevent_initial_call=True
        )
        def _download_comparison_data(
                table_data: list,
                filtered_table_data: list,
                _: int
            ) -> dict:
            """Download the data.

            :param table_data: Original unfiltered table data.
            :param filtered_table_data: Filtered table data.
            :type table_data: list
            :type filtered_table_data: list
            :returns: dict of data frame content (base64 encoded) and meta data
                used by the Download component.
            :rtype: dict
            """

            if not table_data:
                raise PreventUpdate

            if filtered_table_data:
                table = pd.DataFrame.from_records(filtered_table_data)
            else:
                table = pd.DataFrame.from_records(table_data)

            return dcc.send_data_frame(table.to_csv, C.COMP_DOWNLOAD_FILE_NAME)

        @app.callback(
            Output("download-raw-data", "data"),
            State("store-selected", "data"),
            Input("plot-btn-download-raw", "n_clicks"),
            prevent_initial_call=True
        )
        def _download_raw_comparison_data(selected: dict, _: int) -> dict:
            """Download the data.

            :param selected: Selected tests.
            :type selected: dict
            :returns: dict of data frame content (base64 encoded) and meta data
                used by the Download component.
            :rtype: dict
            """

            if not selected:
                raise PreventUpdate

            _, table = comparison_table(
                    data=self._data,
                    selected=selected,
                    normalize=False,
                    remove_outliers=False,
                    raw_data=True
                )

            return dcc.send_data_frame(
                table.dropna(how="all", axis=1).to_csv,
                f"raw_{C.COMP_DOWNLOAD_FILE_NAME}"
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

        @app.callback(
            Output("offcanvas-details", "is_open"),
            Output("offcanvas-details", "children"),
            State("store-selected", "data"),
            State("store-filtered-table-data", "data"),
            State("normalize", "value"),
            State("outliers", "value"),
            Input({"type": "table", "index": ALL}, "active_cell"),
            prevent_initial_call=True
        )
        def show_test_data(cp_sel, table, normalize, outliers, *_):
            """Show offcanvas with graphs and tables based on selected test(s).
            """

            trigger = Trigger(callback_context.triggered)
            if not all((trigger.value, cp_sel["reference"]["set"], \
                        cp_sel["compare"]["set"])):
                raise PreventUpdate

            try:
                test_name = pd.DataFrame.from_records(table).\
                    iloc[[trigger.value["row"]]]["Test Name"].iloc[0]
                dut = cp_sel["reference"]["selection"]["dut"]
                rls, dutver = cp_sel["reference"]["selection"]["dutver"].\
                    split("-", 1)
                phy = cp_sel["reference"]["selection"]["infra"]
                framesize, core, test_id = test_name.split("-", 2)
                test, ttype = test_id.rsplit("-", 1)
                ttype = "pdr" if ttype == "latency" else ttype
                l_phy = phy.split("-")
                tb = "-".join(l_phy[:2])
                nic = l_phy[2]
                stype = "ndrpdr" if ttype in ("ndr", "pdr") else ttype
            except(KeyError, IndexError, AttributeError, ValueError):
                raise PreventUpdate

            df = pd.DataFrame(self._data.loc[(
                    (self._data["dut_type"] == dut) &
                    (self._data["dut_version"] == dutver) &
                    (self._data["release"] == rls)
                )])
            df = df[df.job.str.endswith(tb)]
            df = df[df.test_id.str.contains(
                f"{nic}.*{test}-{stype}", regex=True
            )]
            if df.empty:
                raise PreventUpdate

            l_test_id = df["test_id"].iloc[0].split(".")
            area = ".".join(l_test_id[3:-2])

            r_sel = {
                "id": f"{test}-{ttype}",
                "rls": rls,
                "dut": dut,
                "dutver": dutver,
                "phy": phy,
                "area": area,
                "test": test,
                "framesize": framesize,
                "core": core,
                "testtype": ttype
            }

            c_sel = deepcopy(r_sel)
            param = cp_sel["compare"]["parameter"]
            val = cp_sel["compare"]["value"].lower()
            if param == "dutver":
                c_sel["rls"], c_sel["dutver"] = val.split("-", 1)
            elif param == "ttype":
                c_sel["id"] = f"{test}-{val}"
                c_sel["testtype"] = val
            elif param == "infra":
                c_sel["phy"] = val
            else:
                c_sel[param] = val

            r_sel["id"] = "-".join(
                (r_sel["phy"], r_sel["framesize"], r_sel["core"], r_sel["id"])
            )
            c_sel["id"] = "-".join(
                (c_sel["phy"], c_sel["framesize"], c_sel["core"], c_sel["id"])
            )
            selected = [r_sel, c_sel]

            indexes = ("tput", "bandwidth", "lat")
            graphs = graph_iterative(
                self._data,
                selected,
                self._graph_layout,
                bool(normalize),
                bool(outliers)
            )
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
                dbc.Row(
                    class_name="g-0 p-0",
                    children=dbc.Alert(test, color="info"),
                ),
                dbc.Row(class_name="g-0 p-0", children=cols)
            ]

            return True, ret_val

        @app.callback(
            Output("metadata-tput-lat", "children"),
            Output("metadata-hdrh-graph", "children"),
            Output("offcanvas-metadata", "is_open"),
            Input({"type": "graph-iter", "index": ALL}, "clickData"),
            prevent_initial_call=True
        )
        def _show_metadata_from_graph(iter_data: dict) -> tuple:
            """Generates the data for the offcanvas displayed when a particular
            point in a graph is clicked on.
            """

            trigger = Trigger(callback_context.triggered)
            if not trigger.value:
                raise PreventUpdate

            if trigger.type == "graph-iter":
                return show_iterative_graph_data(
                    trigger, iter_data, self._graph_layout)
            else:
                raise PreventUpdate
