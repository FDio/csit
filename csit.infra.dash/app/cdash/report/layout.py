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
from dash import html
from dash import callback_context, no_update, ALL
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from yaml import load, FullLoader, YAMLError
from ast import literal_eval

from ..utils.constants import Constants as C
from ..utils.control_panel import ControlPanel
from ..utils.trigger import Trigger
from ..utils.utils import show_tooltip, label, sync_checklists, gen_new_url, \
    generate_options, get_list_group_items, navbar_report, \
    show_iterative_graph_data
from ..utils.url_processing import url_decode
from .graphs import graph_iterative, select_iterative_data


# Control panel partameters and their default values.
CP_PARAMS = {
    "dd-rls-val": str(),
    "dd-dut-opt": list(),
    "dd-dut-dis": True,
    "dd-dut-val": str(),
    "dd-dutver-opt": list(),
    "dd-dutver-dis": True,
    "dd-dutver-val": str(),
    "dd-phy-opt": list(),
    "dd-phy-dis": True,
    "dd-phy-val": str(),
    "dd-area-opt": list(),
    "dd-area-dis": True,
    "dd-area-val": str(),
    "dd-test-opt": list(),
    "dd-test-dis": True,
    "dd-test-val": str(),
    "cl-core-opt": list(),
    "cl-core-val": list(),
    "cl-core-all-val": list(),
    "cl-core-all-opt": C.CL_ALL_DISABLED,
    "cl-frmsize-opt": list(),
    "cl-frmsize-val": list(),
    "cl-frmsize-all-val": list(),
    "cl-frmsize-all-opt": C.CL_ALL_DISABLED,
    "cl-tsttype-opt": list(),
    "cl-tsttype-val": list(),
    "cl-tsttype-all-val": list(),
    "cl-tsttype-all-opt": C.CL_ALL_DISABLED,
    "btn-add-dis": True,
    "cl-normalize-val": list()
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
        - read and pre-process the data,
        - prepare data for the control panel,
        - read HTML layout file,
        - read tooltips from the tooltip file.

        :param app: Flask application running the dash application.
        :param html_layout_file: Path and name of the file specifying the HTML
            layout of the dash application.
        :param graph_layout_file: Path and name of the file with layout of
            plot.ly graphs.
        :param tooltip_file: Path and name of the yaml file specifying the
            tooltips.
        :type app: Flask
        :type html_layout_file: str
        :type graph_layout_file: str
        :type tooltip_file: str
        """

        # Inputs
        self._app = app
        self._html_layout_file = html_layout_file
        self._graph_layout_file = graph_layout_file
        self._tooltip_file = tooltip_file
        self._data = data_iterative

        # Get structure of tests:
        tbs = dict()
        cols = [
            "job", "test_id", "test_type", "dut_version", "tg_type", "release"
        ]
        for _, row in self._data[cols].drop_duplicates().iterrows():
            rls = row["release"]
            lst_job = row["job"].split("-")
            dut = lst_job[1]
            d_ver = row["dut_version"]
            tbed = "-".join(lst_job[-2:])
            lst_test_id = row["test_id"].split(".")
            if dut == "dpdk":
                area = "dpdk"
            else:
                area = ".".join(lst_test_id[3:-2])
            suite = lst_test_id[-2].replace("2n1l-", "").replace("1n1l-", "").\
                replace("2n-", "")
            test = lst_test_id[-1]
            nic = suite.split("-")[0]
            for drv in C.DRIVERS:
                if drv in test:
                    driver = drv.replace("-", "_")
                    test = test.replace(f"{drv}-", "")
                    break
            else:
                driver = "dpdk"
            infra = "-".join((tbed, nic, driver))
            lst_test = test.split("-")
            framesize = lst_test[0]
            core = lst_test[1] if lst_test[1] else "8C"
            test = "-".join(lst_test[2: -1])

            if tbs.get(rls, None) is None:
                tbs[rls] = dict()
            if tbs[rls].get(dut, None) is None:
                tbs[rls][dut] = dict()
            if tbs[rls][dut].get(d_ver, None) is None:
                tbs[rls][dut][d_ver] = dict()
            if tbs[rls][dut][d_ver].get(area, None) is None:
                tbs[rls][dut][d_ver][area] = dict()
            if tbs[rls][dut][d_ver][area].get(test, None) is None:
                tbs[rls][dut][d_ver][area][test] = dict()
            if tbs[rls][dut][d_ver][area][test].get(infra, None) is None:
                tbs[rls][dut][d_ver][area][test][infra] = {
                    "core": list(),
                    "frame-size": list(),
                    "test-type": list()
                }
            tst_params = tbs[rls][dut][d_ver][area][test][infra]
            if core.upper() not in tst_params["core"]:
                tst_params["core"].append(core.upper())
            if framesize.upper() not in tst_params["frame-size"]:
                tst_params["frame-size"].append(framesize.upper())
            if row["test_type"] == "ndrpdr":
                if "NDR" not in tst_params["test-type"]:
                    tst_params["test-type"].extend(("NDR", "PDR", ))
            elif row["test_type"] == "hoststack" and \
                    row["tg_type"] in ("iperf", "vpp"):
                if "BPS" not in tst_params["test-type"]:
                    tst_params["test-type"].append("BPS")
            elif row["test_type"] == "hoststack" and row["tg_type"] == "ab":
                if "CPS" not in tst_params["test-type"]:
                    tst_params["test-type"].extend(("CPS", "RPS"))
            else:  # MRR, SOAK
                if row["test_type"].upper() not in tst_params["test-type"]:
                    tst_params["test-type"].append(row["test_type"].upper())
        self._spec_tbs = tbs

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

        if self.html_layout and self._spec_tbs:
            return html.Div(
                id="div-main",
                className="small",
                children=[
                    dbc.Row(
                        id="row-navbar",
                        class_name="g-0",
                        children=[navbar_report((True, False, False, False)), ]
                    ),
                    dbc.Row(
                        id="row-main",
                        class_name="g-0",
                        children=[
                            dcc.Store(id="store-selected-tests"),
                            dcc.Store(id="store-control-panel"),
                            dcc.Location(id="url", refresh=False),
                            self._add_ctrl_col(),
                            self._add_plotting_col()
                        ]
                    ),
                    dbc.Spinner(
                        dbc.Offcanvas(
                            class_name="w-50",
                            id="offcanvas-metadata",
                            title="Throughput And Latency",
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
        test_selection = [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-release",
                                "CSIT Release"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "rls"},
                                placeholder="Select a Release...",
                                options=sorted(
                                    [
                                        {"label": k, "value": k} \
                                            for k in self._spec_tbs.keys()
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
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-dut-ver",
                                "DUT Version"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "dutver"},
                                placeholder=\
                                    "Select a Version of Device under Test..."
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
                                "help-area",
                                "Area"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "area"},
                                placeholder="Select an Area..."
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
                                "help-test",
                                "Test"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "test"},
                                placeholder="Select a Test..."
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
                                "help-infra",
                                "Infra"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "phy"},
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
                            dbc.InputGroupText(
                                children=show_tooltip(
                                    self._tooltips,
                                    "help-framesize",
                                    "Frame Size"
                                )
                            ),
                            dbc.Col(
                                children=[
                                    dbc.Checklist(
                                        id={
                                            "type": "ctrl-cl",
                                            "index": "frmsize-all"
                                        },
                                        options=C.CL_ALL_DISABLED,
                                        inline=True,
                                        class_name="ms-2"
                                    )
                                ],
                                width=2
                            ),
                            dbc.Col(
                                children=[
                                    dbc.Checklist(
                                        id={
                                            "type": "ctrl-cl",
                                            "index": "frmsize"
                                        },
                                        inline=True
                                    )
                                ]
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
                            dbc.InputGroupText(
                                children=show_tooltip(
                                    self._tooltips,
                                    "help-cores",
                                    "Number of Cores"
                                )
                            ),
                            dbc.Col(
                                children=[
                                    dbc.Checklist(
                                        id={
                                            "type": "ctrl-cl",
                                            "index": "core-all"
                                        },
                                        options=C.CL_ALL_DISABLED,
                                        inline=True,
                                        class_name="ms-2"
                                    )
                                ],
                                width=2
                            ),
                            dbc.Col(
                                children=[
                                    dbc.Checklist(
                                        id={
                                            "type": "ctrl-cl",
                                            "index": "core"
                                        },
                                        inline=True
                                    )
                                ]
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
                            dbc.InputGroupText(
                                children=show_tooltip(
                                    self._tooltips,
                                    "help-ttype",
                                    "Test Type"
                                )
                            ),
                            dbc.Col(
                                children=[
                                    dbc.Checklist(
                                        id={
                                            "type": "ctrl-cl",
                                            "index": "tsttype-all"
                                        },
                                        options=C.CL_ALL_DISABLED,
                                        inline=True,
                                        class_name="ms-2"
                                    )
                                ],
                                width=2
                            ),
                            dbc.Col(
                                children=[
                                    dbc.Checklist(
                                        id={
                                            "type": "ctrl-cl",
                                            "index": "tsttype"
                                        },
                                        inline=True
                                    )
                                ]
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
                    dbc.Button(
                        id={"type": "ctrl-btn", "index": "add-test"},
                        children="Add Selected",
                        color="info",
                        class_name="p-1"
                    )
                ]
            )
        ]
        processing = [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.Checklist(
                        id="normalize",
                        options=[{
                            "value": "normalize",
                            "label": "Normalize to 2GHz CPU frequency"
                        }],
                        value=[],
                        inline=True,
                        class_name="ms-2"
                    )
                ]
            )
        ]
        test_list = [
            dbc.Row(
                id="row-card-sel-tests",
                class_name="g-0 p-1",
                children=[
                    dbc.ListGroup(
                        class_name="overflow-auto p-0",
                        id="lg-selected",
                        children=[],
                        style={"max-height": "20em"},
                        flush=True
                    )
                ]
            ),
            dbc.Stack(
                id="row-btns-sel-tests",
                class_name="g-0 p-1",
                gap=2,
                children=[
                    dbc.ButtonGroup(children=[
                        dbc.Button(
                            id={"type": "ctrl-btn", "index": "rm-test"},
                            children="Remove Selected",
                            class_name="w-100 p-1",
                            color="info",
                            disabled=False
                        ),
                        dbc.Button(
                            id={"type": "ctrl-btn", "index": "rm-test-all"},
                            children="Remove All",
                            class_name="w-100 p-1",
                            color="info",
                            disabled=False
                        )
                    ]),
                    dbc.ButtonGroup(children=[
                        dbc.Button(
                            id="plot-btn-url",
                            children="Show URL",
                            class_name="w-100 p-1",
                            color="info",
                            disabled=False
                        ),
                        dbc.Button(
                            id="plot-btn-download",
                            children="Download Data",
                            class_name="w-100 p-1",
                            color="info",
                            disabled=False
                        )
                    ])
                ]
            )
        ]

        return [
            dbc.Row(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5("Test Selection")
                        ),
                        dbc.CardBody(
                            children=test_selection,
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
            ),
            dbc.Row(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5("Selected Tests")
                        ),
                        dbc.CardBody(
                            children=test_list,
                            class_name="g-0 p-0"
                        )
                    ],
                    color="secondary",
                    outline=True
                ),
                id = "row-selected-tests",
                class_name="g-0 p-1",
                style=C.STYLE_DISABLED,
            )
        ]

    def _get_plotting_area(
            self,
            tests: list,
            normalize: bool,
            url: str
        ) -> list:
        """Generate the plotting area with all its content.

        :param tests: List of tests to be displayed in the graphs.
        :param normalize: If true, the values in graphs are normalized.
        :param url: URL to be displayed in the modal window.
        :type tests: list
        :type normalize: bool
        :type url: str
        :returns: List of rows with elements to be displayed in the plotting
            area.
        :rtype: list
        """
        if not tests:
            return C.PLACEHOLDER

        graphs = \
            graph_iterative(self._data, tests, self._graph_layout, normalize)

        if not graphs[0]:
            return C.PLACEHOLDER
        
        tab_items = [
            dbc.Tab(
                children=dcc.Graph(
                    id={"type": "graph", "index": "tput"},
                    figure=graphs[0]
                ),
                label="Throughput",
                tab_id="tab-tput"
            )
        ]

        if graphs[1]:
            tab_items.append(
                dbc.Tab(
                    children=dcc.Graph(
                        id={"type": "graph", "index": "bandwidth"},
                        figure=graphs[1]
                    ),
                    label="Bandwidth",
                    tab_id="tab-bandwidth"
                )
            )

        if graphs[2]:
            tab_items.append(
                dbc.Tab(
                    children=dcc.Graph(
                        id={"type": "graph", "index": "lat"},
                        figure=graphs[2]
                    ),
                    label="Latency",
                    tab_id="tab-lat"
                )
            )

        return [
            dbc.Row(
                dbc.Tabs(
                    children=tab_items,
                    id="tabs",
                    active_tab="tab-tput",
                ),
                class_name="g-0 p-0"
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
            dcc.Download(id="download-iterative-data")
        ]

    def callbacks(self, app):
        """Callbacks for the whole application.

        :param app: The application.
        :type app: Flask
        """

        @app.callback(
            [
                Output("store-control-panel", "data"),
                Output("store-selected-tests", "data"),
                Output("plotting-area", "children"),
                Output("row-selected-tests", "style"),
                Output("lg-selected", "children"),

                Output({"type": "ctrl-dd", "index": "rls"}, "value"),
                Output({"type": "ctrl-dd", "index": "dut"}, "options"),
                Output({"type": "ctrl-dd", "index": "dut"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "dut"}, "value"),
                Output({"type": "ctrl-dd", "index": "dutver"}, "options"),
                Output({"type": "ctrl-dd", "index": "dutver"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "dutver"}, "value"),
                Output({"type": "ctrl-dd", "index": "phy"}, "options"),
                Output({"type": "ctrl-dd", "index": "phy"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "phy"}, "value"),
                Output({"type": "ctrl-dd", "index": "area"}, "options"),
                Output({"type": "ctrl-dd", "index": "area"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "area"}, "value"),
                Output({"type": "ctrl-dd", "index": "test"}, "options"),
                Output({"type": "ctrl-dd", "index": "test"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "test"}, "value"),
                Output({"type": "ctrl-cl", "index": "core"}, "options"),
                Output({"type": "ctrl-cl", "index": "core"}, "value"),
                Output({"type": "ctrl-cl", "index": "core-all"}, "value"),
                Output({"type": "ctrl-cl", "index": "core-all"}, "options"),
                Output({"type": "ctrl-cl", "index": "frmsize"}, "options"),
                Output({"type": "ctrl-cl", "index": "frmsize"}, "value"),
                Output({"type": "ctrl-cl", "index": "frmsize-all"}, "value"),
                Output({"type": "ctrl-cl", "index": "frmsize-all"}, "options"),
                Output({"type": "ctrl-cl", "index": "tsttype"}, "options"),
                Output({"type": "ctrl-cl", "index": "tsttype"}, "value"),
                Output({"type": "ctrl-cl", "index": "tsttype-all"}, "value"),
                Output({"type": "ctrl-cl", "index": "tsttype-all"}, "options"),
                Output({"type": "ctrl-btn", "index": "add-test"}, "disabled"),
                Output("normalize", "value")
            ],
            [
                State("store-control-panel", "data"),
                State("store-selected-tests", "data"),
                State({"type": "sel-cl", "index": ALL}, "value")
            ],
            [
                Input("url", "href"),
                Input("normalize", "value"),

                Input({"type": "ctrl-dd", "index": ALL}, "value"),
                Input({"type": "ctrl-cl", "index": ALL}, "value"),
                Input({"type": "ctrl-btn", "index": ALL}, "n_clicks")
            ]
        )
        def _update_application(
                control_panel: dict,
                store_sel: list,
                lst_sel: list,
                href: str,
                normalize: list,
                *_
            ) -> tuple:
            """Update the application when the event is detected.
            """

            ctrl_panel = ControlPanel(CP_PARAMS, control_panel)
            on_draw = False

            # Parse the url:
            parsed_url = url_decode(href)
            if parsed_url:
                url_params = parsed_url["params"]
            else:
                url_params = None

            plotting_area = no_update
            row_sel_tests = no_update
            lg_selected = no_update

            trigger = Trigger(callback_context.triggered)

            if trigger.type == "url" and url_params:
                try:
                    store_sel = literal_eval(url_params["store_sel"][0])
                    normalize = literal_eval(url_params["norm"][0])
                except (KeyError, IndexError, AttributeError):
                    pass
                if store_sel:
                    row_sel_tests = C.STYLE_ENABLED
                    last_test = store_sel[-1]
                    test = self._spec_tbs[last_test["rls"]][last_test["dut"]]\
                        [last_test["dutver"]][last_test["area"]]\
                            [last_test["test"]][last_test["phy"]]
                    ctrl_panel.set({
                        "dd-rls-val": last_test["rls"],
                        "dd-dut-val": last_test["dut"],
                        "dd-dut-opt": generate_options(
                            self._spec_tbs[last_test["rls"]].keys()
                        ),
                        "dd-dut-dis": False,
                        "dd-dutver-val": last_test["dutver"],
                        "dd-dutver-opt": generate_options(
                            self._spec_tbs[last_test["rls"]]\
                                [last_test["dut"]].keys()
                        ),
                        "dd-dutver-dis": False,
                        "dd-area-val": last_test["area"],
                        "dd-area-opt": [
                            {"label": label(v), "value": v} for v in \
                                sorted(self._spec_tbs[last_test["rls"]]\
                                    [last_test["dut"]]\
                                        [last_test["dutver"]].keys())
                        ],
                        "dd-area-dis": False,
                        "dd-test-val": last_test["test"],
                        "dd-test-opt": generate_options(
                            self._spec_tbs[last_test["rls"]][last_test["dut"]]\
                                [last_test["dutver"]][last_test["area"]].keys()
                        ),
                        "dd-test-dis": False,
                        "dd-phy-val": last_test["phy"],
                        "dd-phy-opt": generate_options(
                            self._spec_tbs[last_test["rls"]][last_test["dut"]]\
                                [last_test["dutver"]][last_test["area"]]\
                                    [last_test["test"]].keys()
                        ),
                        "dd-phy-dis": False,
                        "cl-core-opt": generate_options(test["core"]),
                        "cl-core-val": [last_test["core"].upper(), ],
                        "cl-core-all-val": list(),
                        "cl-core-all-opt": C.CL_ALL_ENABLED,
                        "cl-frmsize-opt": generate_options(test["frame-size"]),
                        "cl-frmsize-val": [last_test["framesize"].upper(), ],
                        "cl-frmsize-all-val": list(),
                        "cl-frmsize-all-opt": C.CL_ALL_ENABLED,
                        "cl-tsttype-opt": generate_options(test["test-type"]),
                        "cl-tsttype-val": [last_test["testtype"].upper(), ],
                        "cl-tsttype-all-val": list(),
                        "cl-tsttype-all-opt": C.CL_ALL_ENABLED,
                        "cl-normalize-val": normalize,
                        "btn-add-dis": False
                    })
                    on_draw = True
            elif trigger.type == "normalize":
                ctrl_panel.set({"cl-normalize-val": normalize})
                on_draw = True
            elif trigger.type == "ctrl-dd":
                if trigger.idx == "rls":
                    try:
                        options = generate_options(
                            self._spec_tbs[trigger.value].keys()
                        )
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "dd-rls-val": trigger.value,
                        "dd-dut-val": str(),
                        "dd-dut-opt": options,
                        "dd-dut-dis": disabled,
                        "dd-dutver-val": str(),
                        "dd-dutver-opt": list(),
                        "dd-dutver-dis": True,
                        "dd-phy-val": str(),
                        "dd-phy-opt": list(),
                        "dd-phy-dis": True,
                        "dd-area-val": str(),
                        "dd-area-opt": list(),
                        "dd-area-dis": True,
                        "dd-test-val": str(),
                        "dd-test-opt": list(),
                        "dd-test-dis": True,
                        "cl-core-opt": list(),
                        "cl-core-val": list(),
                        "cl-core-all-val": list(),
                        "cl-core-all-opt": C.CL_ALL_DISABLED,
                        "cl-frmsize-opt": list(),
                        "cl-frmsize-val": list(),
                        "cl-frmsize-all-val": list(),
                        "cl-frmsize-all-opt": C.CL_ALL_DISABLED,
                        "cl-tsttype-opt": list(),
                        "cl-tsttype-val": list(),
                        "cl-tsttype-all-val": list(),
                        "cl-tsttype-all-opt": C.CL_ALL_DISABLED,
                        "btn-add-dis": True
                    })
                elif trigger.idx == "dut":
                    try:
                        rls = ctrl_panel.get("dd-rls-val")
                        dut = self._spec_tbs[rls][trigger.value]
                        options = generate_options(dut.keys())
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "dd-dut-val": trigger.value,
                        "dd-dutver-val": str(),
                        "dd-dutver-opt": options,
                        "dd-dutver-dis": disabled,
                        "dd-phy-val": str(),
                        "dd-phy-opt": list(),
                        "dd-phy-dis": True,
                        "dd-area-val": str(),
                        "dd-area-opt": list(),
                        "dd-area-dis": True,
                        "dd-test-val": str(),
                        "dd-test-opt": list(),
                        "dd-test-dis": True,
                        "cl-core-opt": list(),
                        "cl-core-val": list(),
                        "cl-core-all-val": list(),
                        "cl-core-all-opt": C.CL_ALL_DISABLED,
                        "cl-frmsize-opt": list(),
                        "cl-frmsize-val": list(),
                        "cl-frmsize-all-val": list(),
                        "cl-frmsize-all-opt": C.CL_ALL_DISABLED,
                        "cl-tsttype-opt": list(),
                        "cl-tsttype-val": list(),
                        "cl-tsttype-all-val": list(),
                        "cl-tsttype-all-opt": C.CL_ALL_DISABLED,
                        "btn-add-dis": True
                    })
                elif trigger.idx == "dutver":
                    try:
                        rls = ctrl_panel.get("dd-rls-val")
                        dut = ctrl_panel.get("dd-dut-val")
                        dutver = self._spec_tbs[rls][dut][trigger.value]
                        options = [{"label": label(v), "value": v} \
                            for v in sorted(dutver.keys())]
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "dd-dutver-val": trigger.value,
                        "dd-area-val": str(),
                        "dd-area-opt": options,
                        "dd-area-dis": disabled,
                        "dd-test-val": str(),
                        "dd-test-opt": list(),
                        "dd-test-dis": True,
                        "dd-phy-val": str(),
                        "dd-phy-opt": list(),
                        "dd-phy-dis": True,
                        "cl-core-opt": list(),
                        "cl-core-val": list(),
                        "cl-core-all-val": list(),
                        "cl-core-all-opt": C.CL_ALL_DISABLED,
                        "cl-frmsize-opt": list(),
                        "cl-frmsize-val": list(),
                        "cl-frmsize-all-val": list(),
                        "cl-frmsize-all-opt": C.CL_ALL_DISABLED,
                        "cl-tsttype-opt": list(),
                        "cl-tsttype-val": list(),
                        "cl-tsttype-all-val": list(),
                        "cl-tsttype-all-opt": C.CL_ALL_DISABLED,
                        "btn-add-dis": True
                    })
                elif trigger.idx == "area":
                    try:
                        rls = ctrl_panel.get("dd-rls-val")
                        dut = ctrl_panel.get("dd-dut-val")
                        dutver = ctrl_panel.get("dd-dutver-val")
                        area = self._spec_tbs[rls][dut][dutver][trigger.value]
                        options = generate_options(area.keys())
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "dd-area-val": trigger.value,
                        "dd-test-val": str(),
                        "dd-test-opt": options,
                        "dd-test-dis": disabled,
                        "dd-phy-val": str(),
                        "dd-phy-opt": list(),
                        "dd-phy-dis": True,
                        "cl-core-opt": list(),
                        "cl-core-val": list(),
                        "cl-core-all-val": list(),
                        "cl-core-all-opt": C.CL_ALL_DISABLED,
                        "cl-frmsize-opt": list(),
                        "cl-frmsize-val": list(),
                        "cl-frmsize-all-val": list(),
                        "cl-frmsize-all-opt": C.CL_ALL_DISABLED,
                        "cl-tsttype-opt": list(),
                        "cl-tsttype-val": list(),
                        "cl-tsttype-all-val": list(),
                        "cl-tsttype-all-opt": C.CL_ALL_DISABLED,
                        "btn-add-dis": True
                    })
                elif trigger.idx == "test":
                    try:
                        rls = ctrl_panel.get("dd-rls-val")
                        dut = ctrl_panel.get("dd-dut-val")
                        dutver = ctrl_panel.get("dd-dutver-val")
                        area = ctrl_panel.get("dd-area-val")
                        test = self._spec_tbs[rls][dut][dutver][area]\
                            [trigger.value]
                        options = generate_options(test.keys())
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "dd-test-val": trigger.value,
                        "dd-phy-val": str(),
                        "dd-phy-opt": options,
                        "dd-phy-dis": disabled,
                        "cl-core-opt": list(),
                        "cl-core-val": list(),
                        "cl-core-all-val": list(),
                        "cl-core-all-opt": C.CL_ALL_DISABLED,
                        "cl-frmsize-opt": list(),
                        "cl-frmsize-val": list(),
                        "cl-frmsize-all-val": list(),
                        "cl-frmsize-all-opt": C.CL_ALL_DISABLED,
                        "cl-tsttype-opt": list(),
                        "cl-tsttype-val": list(),
                        "cl-tsttype-all-val": list(),
                        "cl-tsttype-all-opt": C.CL_ALL_DISABLED,
                        "btn-add-dis": True
                    })
                elif trigger.idx == "phy":
                    rls = ctrl_panel.get("dd-rls-val")
                    dut = ctrl_panel.get("dd-dut-val")
                    dutver = ctrl_panel.get("dd-dutver-val")
                    area = ctrl_panel.get("dd-area-val")
                    test = ctrl_panel.get("dd-test-val")
                    if all((rls, dut, dutver, area, test, trigger.value, )):
                        phy = self._spec_tbs[rls][dut][dutver][area][test]\
                            [trigger.value]
                        ctrl_panel.set({
                            "dd-phy-val": trigger.value,
                            "cl-core-opt": generate_options(phy["core"]),
                            "cl-core-val": list(),
                            "cl-core-all-val": list(),
                            "cl-core-all-opt": C.CL_ALL_ENABLED,
                            "cl-frmsize-opt": \
                                generate_options(phy["frame-size"]),
                            "cl-frmsize-val": list(),
                            "cl-frmsize-all-val": list(),
                            "cl-frmsize-all-opt": C.CL_ALL_ENABLED,
                            "cl-tsttype-opt": \
                                generate_options(phy["test-type"]),
                            "cl-tsttype-val": list(),
                            "cl-tsttype-all-val": list(),
                            "cl-tsttype-all-opt": C.CL_ALL_ENABLED,
                            "btn-add-dis": True
                        })
            elif trigger.type == "ctrl-cl":
                param = trigger.idx.split("-")[0]
                if "-all" in trigger.idx:
                    c_sel, c_all, c_id = list(), trigger.value, "all"
                else:
                    c_sel, c_all, c_id = trigger.value, list(), str()
                val_sel, val_all = sync_checklists(
                    options=ctrl_panel.get(f"cl-{param}-opt"),
                    sel=c_sel,
                    all=c_all,
                    id=c_id
                )
                ctrl_panel.set({
                    f"cl-{param}-val": val_sel,
                    f"cl-{param}-all-val": val_all,
                })
                if all((ctrl_panel.get("cl-core-val"),
                        ctrl_panel.get("cl-frmsize-val"),
                        ctrl_panel.get("cl-tsttype-val"), )):
                    ctrl_panel.set({"btn-add-dis": False})
                else:
                    ctrl_panel.set({"btn-add-dis": True})
            elif trigger.type == "ctrl-btn":
                on_draw = True
                if trigger.idx == "add-test":
                    rls = ctrl_panel.get("dd-rls-val")
                    dut = ctrl_panel.get("dd-dut-val")
                    dutver = ctrl_panel.get("dd-dutver-val")
                    phy = ctrl_panel.get("dd-phy-val")
                    area = ctrl_panel.get("dd-area-val")
                    test = ctrl_panel.get("dd-test-val")
                    # Add selected test to the list of tests in store:
                    if store_sel is None:
                        store_sel = list()
                    for core in ctrl_panel.get("cl-core-val"):
                        for framesize in ctrl_panel.get("cl-frmsize-val"):
                            for ttype in ctrl_panel.get("cl-tsttype-val"):
                                if dut == "trex":
                                    core = str()
                                tid = "-".join((
                                    rls,
                                    dut,
                                    dutver,
                                    phy.replace("af_xdp", "af-xdp"),
                                    area,
                                    framesize.lower(),
                                    core.lower(),
                                    test,
                                    ttype.lower()
                                ))
                                if tid not in [i["id"] for i in store_sel]:
                                    store_sel.append({
                                        "id": tid,
                                        "rls": rls,
                                        "dut": dut,
                                        "dutver": dutver,
                                        "phy": phy,
                                        "area": area,
                                        "test": test,
                                        "framesize": framesize.lower(),
                                        "core": core.lower(),
                                        "testtype": ttype.lower()
                                    })
                    store_sel = sorted(store_sel, key=lambda d: d["id"])
                    if C.CLEAR_ALL_INPUTS:
                        ctrl_panel.set(ctrl_panel.defaults)
                elif trigger.idx == "rm-test" and lst_sel:
                    new_store_sel = list()
                    for idx, item in enumerate(store_sel):
                        if not lst_sel[idx]:
                            new_store_sel.append(item)
                    store_sel = new_store_sel
                elif trigger.idx == "rm-test-all":
                    store_sel = list()

            if on_draw:
                if store_sel:
                    lg_selected = get_list_group_items(
                        store_sel, "sel-cl", add_index=True
                    )
                    plotting_area = self._get_plotting_area(
                        store_sel,
                        bool(normalize),
                        gen_new_url(
                            parsed_url,
                            {"store_sel": store_sel, "norm": normalize}
                        )
                    )
                    row_sel_tests = C.STYLE_ENABLED
                else:
                    plotting_area = C.PLACEHOLDER
                    row_sel_tests = C.STYLE_DISABLED
                    store_sel = list()

            ret_val = [
                ctrl_panel.panel,
                store_sel,
                plotting_area,
                row_sel_tests,
                lg_selected
            ]
            ret_val.extend(ctrl_panel.values)
            return ret_val

        @app.callback(
            Output("plot-mod-url", "is_open"),
            Output("plot-btn-url", "n_clicks"),
            Input("plot-btn-url", "n_clicks"),
            State("plot-mod-url", "is_open")
        )
        def toggle_plot_mod_url(n, is_open):
            """Toggle the modal window with url.
            """
            if n:
                return not is_open, 0
            return is_open, 0

        @app.callback(
            Output("download-iterative-data", "data"),
            State("store-selected-tests", "data"),
            Input("plot-btn-download", "n_clicks"),
            prevent_initial_call=True
        )
        def _download_iterative_data(store_sel, _):
            """Download the data

            :param store_sel: List of tests selected by user stored in the
                browser.
            :type store_sel: list
            :returns: dict of data frame content (base64 encoded) and meta data
                used by the Download component.
            :rtype: dict
            """

            if not store_sel:
                raise PreventUpdate

            df = pd.DataFrame()
            for itm in store_sel:
                sel_data = select_iterative_data(self._data, itm)
                if sel_data is None:
                    continue
                df = pd.concat([df, sel_data], ignore_index=True)

            return dcc.send_data_frame(df.to_csv, C.REPORT_DOWNLOAD_FILE_NAME)

        @app.callback(
            Output("metadata-tput-lat", "children"),
            Output("metadata-hdrh-graph", "children"),
            Output("offcanvas-metadata", "is_open"),
            Input({"type": "graph", "index": ALL}, "clickData"),
            prevent_initial_call=True
        )
        def _show_metadata_from_graphs(graph_data: dict) -> tuple:
            """Generates the data for the offcanvas displayed when a particular
            point in a graph is clicked on.

            :param graph_data: The data from the clicked point in the graph.
            :type graph_data: dict
            :returns: The data to be displayed on the offcanvas and the
                information to show the offcanvas.
            :rtype: tuple(list, list, bool)
            """

            trigger = Trigger(callback_context.triggered)
            if not trigger.value:
                raise PreventUpdate

            return show_iterative_graph_data(
                    trigger, graph_data, self._graph_layout)

        @app.callback(
            Output("offcanvas-documentation", "is_open"),
            Input("btn-documentation", "n_clicks"),
            State("offcanvas-documentation", "is_open")
        )
        def toggle_offcanvas_documentation(n_clicks, is_open):
            if n_clicks:
                return not is_open
            return is_open
