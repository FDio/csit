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
from copy import deepcopy

from ..utils.constants import Constants as C
from ..utils.control_panel import ControlPanel
from ..utils.trigger import Trigger
from ..utils.telemetry_data import TelemetryData
from ..utils.utils import show_tooltip, label, sync_checklists, gen_new_url, \
    generate_options, get_list_group_items, navbar_trending, \
    show_trending_graph_data
from ..utils.url_processing import url_decode
from .graphs import graph_trending, select_trending_data, graph_tm_trending


# Control panel partameters and their default values.
CP_PARAMS = {
    "dd-dut-val": str(),
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
    "cl-normalize-val": list(),
    "cl-show-trials": list()
}


class Layout:
    """The layout of the dash app and the callbacks.
    """

    def __init__(self,
            app: Flask,
            data_trending: pd.DataFrame,
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
        self._data = data_trending
        self._html_layout_file = html_layout_file
        self._graph_layout_file = graph_layout_file
        self._tooltip_file = tooltip_file

        # Get structure of tests:
        tbs = dict()
        cols = ["job", "test_id", "test_type", "tg_type"]
        for _, row in self._data[cols].drop_duplicates().iterrows():
            lst_job = row["job"].split("-")
            dut = lst_job[1]
            tbed = "-".join(lst_job[-2:])
            lst_test = row["test_id"].split(".")
            if dut == "dpdk":
                area = "dpdk"
            else:
                area = ".".join(lst_test[3:-2])
            suite = lst_test[-2].replace("2n1l-", "").replace("1n1l-", "").\
                replace("2n-", "")
            test = lst_test[-1]
            nic = suite.split("-")[0]
            for drv in C.DRIVERS:
                if drv in test:
                    if drv == "af-xdp":
                        driver = "af_xdp"
                    else:
                        driver = drv
                    test = test.replace(f"{drv}-", "")
                    break
            else:
                driver = "dpdk"
            infra = "-".join((tbed, nic, driver))
            lst_test = test.split("-")
            framesize = lst_test[0]
            core = lst_test[1] if lst_test[1] else "8C"
            test = "-".join(lst_test[2: -1])

            if tbs.get(dut, None) is None:
                tbs[dut] = dict()
            if tbs[dut].get(area, None) is None:
                tbs[dut][area] = dict()
            if tbs[dut][area].get(test, None) is None:
                tbs[dut][area][test] = dict()
            if tbs[dut][area][test].get(infra, None) is None:
                tbs[dut][area][test][infra] = {
                    "core": list(),
                    "frame-size": list(),
                    "test-type": list()
                }
            tst_params = tbs[dut][area][test][infra]
            if core.upper() not in tst_params["core"]:
                tst_params["core"].append(core.upper())
            if framesize.upper() not in tst_params["frame-size"]:
                tst_params["frame-size"].append(framesize.upper())
            if row["test_type"] == "ndrpdr":
                if "NDR" not in tst_params["test-type"]:
                    tst_params["test-type"].extend(("NDR", "PDR"))
            elif row["test_type"] == "hoststack":
                if row["tg_type"] in ("iperf", "vpp"):
                    if "BPS" not in tst_params["test-type"]:
                        tst_params["test-type"].append("BPS")
                elif row["tg_type"] == "ab":
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
                    dcc.Store(id="store"),
                    dcc.Location(id="url", refresh=False),
                    dbc.Row(
                        id="row-navbar",
                        class_name="g-0",
                        children=[navbar_trending((True, False, False, False))]
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
        test_selection = [
            dbc.Row(
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
                                        for k in self._spec_tbs.keys()
                                ],
                                key=lambda d: d["label"]
                            )
                        )
                    ],
                    size="sm"
                ),
                class_name="g-0 p-1"
            ),
            dbc.Row(
                dbc.InputGroup(
                    [
                        dbc.InputGroupText(
                            show_tooltip(self._tooltips, "help-area", "Area")
                        ),
                        dbc.Select(
                            id={"type": "ctrl-dd", "index": "area"},
                            placeholder="Select an Area..."
                        )
                    ],
                    size="sm"
                ),
                class_name="g-0 p-1"
            ),
            dbc.Row(
                dbc.InputGroup(
                    [
                        dbc.InputGroupText(
                            show_tooltip(self._tooltips, "help-test", "Test")
                        ),
                        dbc.Select(
                            id={"type": "ctrl-dd", "index": "test"},
                            placeholder="Select a Test..."
                        )
                    ],
                    size="sm"
                ),
                class_name="g-0 p-1"
            ),
            dbc.Row(
                dbc.InputGroup(
                    [
                        dbc.InputGroupText(
                            show_tooltip(self._tooltips, "help-infra", "Infra")
                        ),
                        dbc.Select(
                            id={"type": "ctrl-dd", "index": "phy"},
                            placeholder="Select a Physical Test Bed Topology..."
                        )
                    ],
                    size="sm"
                ),
                class_name="g-0 p-1"
            ),
            dbc.Row(
                dbc.InputGroup(
                    [
                        dbc.InputGroupText(show_tooltip(
                            self._tooltips,
                            "help-framesize",
                            "Frame Size"
                        )),
                        dbc.Col(
                            dbc.Checklist(
                                id={"type": "ctrl-cl", "index": "frmsize-all"},
                                options=C.CL_ALL_DISABLED,
                                inline=True,
                                class_name="ms-2"
                            ),
                            width=2
                        ),
                        dbc.Col(
                            dbc.Checklist(
                                id={"type": "ctrl-cl", "index": "frmsize"},
                                inline=True
                            )
                        )
                    ],
                    style={"align-items": "center"},
                    size="sm"
                ),
                class_name="g-0 p-1"
            ),
            dbc.Row(
                dbc.InputGroup(
                    [
                        dbc.InputGroupText(show_tooltip(
                            self._tooltips,
                            "help-cores",
                            "Number of Cores"
                        )),
                        dbc.Col(
                            dbc.Checklist(
                                id={"type": "ctrl-cl", "index": "core-all"},
                                options=C.CL_ALL_DISABLED,
                                inline=True,
                                class_name="ms-2"
                            ),
                            width=2
                        ),
                        dbc.Col(
                            dbc.Checklist(
                                id={"type": "ctrl-cl", "index": "core"},
                                inline=True
                            )
                        )
                    ],
                    style={"align-items": "center"},
                    size="sm"
                ),
                class_name="g-0 p-1"
            ),
            dbc.Row(
                dbc.InputGroup(
                    [
                        dbc.InputGroupText(show_tooltip(
                            self._tooltips,
                            "help-ttype",
                            "Test Type"
                        )),
                        dbc.Col(
                            dbc.Checklist(
                                id={"type": "ctrl-cl", "index": "tsttype-all"},
                                options=C.CL_ALL_DISABLED,
                                inline=True,
                                class_name="ms-2"
                            ),
                            width=2
                        ),
                        dbc.Col(
                            dbc.Checklist(
                                id={"type": "ctrl-cl", "index": "tsttype"},
                                inline=True
                            )
                        )
                    ],
                    style={"align-items": "center"},
                    size="sm"
                ),
                class_name="g-0 p-1"
            ),
            dbc.Row(
                dbc.Button(
                    id={"type": "ctrl-btn", "index": "add-test"},
                    children="Add Selected",
                    color="info",
                    class_name="p-1"
                ),
                class_name="g-0 p-1"
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
                    ),
                    dbc.Checklist(
                        id="show-trials",
                        options=[{
                            "value": "trials",
                            "label": "Show MRR Trials"
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
                dbc.ListGroup(
                    class_name="overflow-auto p-0",
                    id="lg-selected",
                    children=[],
                    style={"max-height": "20em"},
                    flush=True
                ),
                class_name="g-0 p-1"
            ),
            dbc.Row(
                dbc.ButtonGroup(
                    children=[
                        dbc.Button(
                            "Remove Selected",
                            id={"type": "ctrl-btn", "index": "rm-test"},
                            class_name="w-100 p-1",
                            color="info",
                            disabled=False
                        ),
                        dbc.Button(
                            "Remove All",
                            id={"type": "ctrl-btn", "index": "rm-test-all"},
                            class_name="w-100 p-1",
                            color="info",
                            disabled=False
                        )
                    ]
                ),
                class_name="g-0 p-1"
            ),
            dbc.Stack(
                [
                    dbc.Button(
                        "Add Telemetry Panel",
                        id={"type": "telemetry-btn", "index": "open"},
                        color="info",
                        class_name="p-1"
                    ),
                    dbc.Button(
                        "Show URL",
                        id="plot-btn-url",
                        color="info",
                        class_name="p-1"
                    ),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("URL")),
                            dbc.ModalBody(id="mod-url")
                        ],
                        id="plot-mod-url",
                        size="xl",
                        is_open=False,
                        scrollable=True
                    )
                ],
                class_name="g-0 p-1",
                gap=2
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


    def _add_plotting_col(self) -> dbc.Col:
        """Add column with plots. It is placed on the right side.

        :returns: Column with plots.
        :rtype: dbc.Col
        """
        return dbc.Col(
            id="col-plotting-area",
            children=[
                dbc.Row(
                    id="plotting-area-trending",
                    class_name="g-0 p-0",
                    children=C.PLACEHOLDER
                ),
                dbc.Row(
                    id="plotting-area-telemetry",
                    class_name="g-0 p-0",
                    children=C.PLACEHOLDER
                )
            ],
            width=9,
            style=C.STYLE_DISABLED,
        )

    @staticmethod
    def _plotting_area_trending(graphs: list) -> dbc.Col:
        """Generate the plotting area with all its content.

        :param graphs: A list of graphs to be displayed in the trending page.
        :type graphs: list
        :returns: A collumn with trending graphs (tput and latency) in tabs.
        :rtype: dbc.Col
        """
        if not graphs:
            return C.PLACEHOLDER

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

        trending = [
            dbc.Row(
                dbc.Tabs(
                    children=tab_items,
                    id="tabs",
                    active_tab="tab-tput",
                ),
                class_name="g-0 p-0"
            ),
            dbc.Row(
                html.Div(
                    [
                        dbc.Button(
                            "Download Data",
                            id="plot-btn-download",
                            class_name="me-1",
                            color="info",
                            style={"padding": "0rem 1rem"}
                        ),
                        dcc.Download(id="download-trending-data")
                    ],
                    className="d-grid gap-0 d-md-flex justify-content-md-end"
                ),
                class_name="g-0 p-0"
            )
        ]

        return dbc.Col(
            children=[
                dbc.Accordion(
                    dbc.AccordionItem(trending, title="Trending"),
                    class_name="g-0 p-1",
                    start_collapsed=False,
                    always_open=True,
                    active_item=["item-0", ]
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(
                            dbc.ModalTitle("Select a Metric"),
                            close_button=False
                        ),
                        dbc.Spinner(
                            dbc.ModalBody(Layout._get_telemetry_step_1()),
                            delay_show=2 * C.SPINNER_DELAY
                        ),
                        dbc.ModalFooter([
                            dbc.Button(
                                "Select",
                                id={"type": "telemetry-btn", "index": "select"},
                                color="success",
                                disabled=True
                            ),
                            dbc.Button(
                                "Cancel",
                                id={"type": "telemetry-btn", "index": "cancel"},
                                color="info",
                                disabled=False
                            ),
                            dbc.Button(
                                "Remove All",
                                id={"type": "telemetry-btn", "index": "rm-all"},
                                color="danger",
                                disabled=False
                            )
                        ])
                    ],
                    id={"type": "plot-mod-telemetry", "index": 0},
                    size="lg",
                    is_open=False,
                    scrollable=False,
                    backdrop="static",
                    keyboard=False
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(
                            dbc.ModalTitle("Select Labels"),
                            close_button=False
                        ),
                        dbc.Spinner(
                            dbc.ModalBody(Layout._get_telemetry_step_2()),
                            delay_show=2 * C.SPINNER_DELAY
                        ),
                        dbc.ModalFooter([
                            dbc.Button(
                                "Back",
                                id={"type": "telemetry-btn", "index": "back"},
                                color="info",
                                disabled=False
                            ),
                            dbc.Button(
                                "Add Telemetry Panel",
                                id={"type": "telemetry-btn", "index": "add"},
                                color="success",
                                disabled=True
                            ),
                            dbc.Button(
                                "Cancel",
                                id={"type": "telemetry-btn", "index": "cancel"},
                                color="info",
                                disabled=False
                            )
                        ])
                    ],
                    id={"type": "plot-mod-telemetry", "index": 1},
                    size="xl",
                    is_open=False,
                    scrollable=False,
                    backdrop="static",
                    keyboard=False
                )
            ]
        )

    @staticmethod
    def _plotting_area_telemetry(graphs: list) -> dbc.Col:
        """Generate the plotting area with telemetry.

        :param graphs: A list of graphs to be displayed in the telemetry page.
        :type graphs: list
        :returns: A collumn with telemetry trending graphs.
        :rtype: dbc.Col
        """
        if not graphs:
            return C.PLACEHOLDER

        def _plural(iterative):
            return "s" if len(iterative) > 1 else str()

        panels = list()
        for idx, graph_set in enumerate(graphs):
            acc_items = list()
            for graph in graph_set[0]:
                graph_name = ", ".join(graph[1])
                acc_items.append(
                    dbc.AccordionItem(
                        dcc.Graph(
                            id={"type": "graph-telemetry", "index": graph_name},
                            figure=graph[0]
                        ),
                        title=(f"Test{_plural(graph[1])}: {graph_name}"),
                        class_name="g-0 p-0"
                    )
                )
            panels.append(
                dbc.AccordionItem(
                    [
                        dbc.Row(
                            dbc.Accordion(
                                children=acc_items,
                                class_name="g-0 p-0",
                                start_collapsed=True,
                                always_open=True,
                                flush=True
                            ),
                            class_name="g-0 p-0"
                        ),
                        dbc.Row(
                            html.Div(
                                [
                                    dbc.Button(
                                        "Remove",
                                        id={
                                            "type": "tm-btn-remove",
                                            "index": idx
                                        },
                                        class_name="me-1",
                                        color="danger",
                                        style={"padding": "0rem 1rem"}
                                    ),
                                    dbc.Button(
                                        "Download Data",
                                        id={
                                            "type": "tm-btn-download",
                                            "index": idx
                                        },
                                        class_name="me-1",
                                        color="info",
                                        style={"padding": "0rem 1rem"}
                                    )
                                ],
                            className=\
                                "d-grid gap-0 d-md-flex justify-content-md-end"
                            ),
                            class_name="g-0 p-0"
                        )
                    ],
                    class_name="g-0 p-0",
                    title=(
                        f"Metric{_plural(graph_set[1])}: ",
                        ", ".join(graph_set[1])
                    )
                )
            )

        return dbc.Col(
            dbc.Accordion(
                panels,
                class_name="g-0 p-1",
                start_collapsed=True,
                always_open=True
            )
        )

    @staticmethod
    def _get_telemetry_step_1() -> list:
        """Return the content of the modal window used in the step 1 of metrics
        selection.

        :returns: A list of dbc rows with 'input' and 'search output'.
        :rtype: list
        """
        return [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.Input(
                        id={"type": "telemetry-search-in", "index": 0},
                        placeholder="Start typing a metric name...",
                        type="text"
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.ListGroup(
                        class_name="overflow-auto p-0",
                        id={"type": "telemetry-search-out", "index": 0},
                        children=[],
                        style={"max-height": "14em"},
                        flush=True
                    )
                ]
            )
        ]

    @staticmethod
    def _get_telemetry_step_2() -> list:
        """Return the content of the modal window used in the step 2 of metrics
        selection.

        :returns: A list of dbc rows with 'container with dynamic dropdowns' and
            'search output'.
        :rtype: list
        """
        return [
            dbc.Row(
                "Add content here.",
                id={"type": "tm-container", "index": 0},
                class_name="g-0 p-1"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Checkbox(
                            id={"type": "cb-all-in-one", "index": 0},
                            label="All Metrics in one Graph"
                        ),
                        width=6
                    ),
                    dbc.Col(
                        dbc.Checkbox(
                            id={"type": "cb-ignore-host", "index": 0},
                            label="Ignore Host"
                        ),
                        width=6
                    )
                ],
                class_name="g-0 p-2"
            ),
            dbc.Row(
                dbc.Textarea(
                    id={"type": "tm-list-metrics", "index": 0},
                    rows=20,
                    size="sm",
                    wrap="off",
                    readonly=True
                ),
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
            Output("plotting-area-trending", "children"),
            Output("plotting-area-telemetry", "children"),
            Output("col-plotting-area", "style"),
            Output("row-selected-tests", "style"),
            Output("lg-selected", "children"),
            Output({"type": "telemetry-search-out", "index": ALL}, "children"),
            Output({"type": "plot-mod-telemetry", "index": ALL}, "is_open"),
            Output({"type": "telemetry-btn", "index": ALL}, "disabled"),
            Output({"type": "tm-container", "index": ALL}, "children"),
            Output({"type": "tm-list-metrics", "index": ALL}, "value"),
            Output({"type": "ctrl-dd", "index": "dut"}, "value"),
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
            Output("normalize", "value"),
            Output("show-trials", "value"),

            State("store", "data"),
            State({"type": "sel-cl", "index": ALL}, "value"),
            State({"type": "cb-all-in-one", "index": ALL}, "value"),
            State({"type": "cb-ignore-host", "index": ALL}, "value"),
            State({"type": "telemetry-search-out", "index": ALL}, "children"),
            State({"type": "plot-mod-telemetry", "index": ALL}, "is_open"),
            State({"type": "telemetry-btn", "index": ALL}, "disabled"),
            State({"type": "tm-container", "index": ALL}, "children"),
            State({"type": "tm-list-metrics", "index": ALL}, "value"),
            State({"type": "tele-cl", "index": ALL}, "value"),

            Input("url", "href"),
            Input({"type": "tm-dd", "index": ALL}, "value"),

            Input("normalize", "value"),
            Input("show-trials", "value"),
            Input({"type": "telemetry-search-in", "index": ALL}, "value"),
            Input({"type": "telemetry-btn", "index": ALL}, "n_clicks"),
            Input({"type": "tm-btn-remove", "index": ALL}, "n_clicks"),
            Input({"type": "ctrl-dd", "index": ALL}, "value"),
            Input({"type": "ctrl-cl", "index": ALL}, "value"),
            Input({"type": "ctrl-btn", "index": ALL}, "n_clicks"),

            prevent_initial_call=True
        )
        def _update_application(
                store: dict,
                lst_sel: list,
                all_in_one: list,
                ignore_host: list,
                search_out: list,
                is_open: list,
                tm_btns_disabled: list,
                tm_dd: list,
                list_metrics: list,
                cl_metrics: list,
                href: str,
                tm_dd_in: list,
                *_
            ) -> tuple:
            """Update the application when the event is detected.
            """

            if store is None:
                store = {
                    "control-panel": dict(),
                    "selected-tests": list(),
                    "trending-graphs": None,
                    "telemetry-data": dict(),
                    "selected-metrics": dict(),
                    "telemetry-panels": list(),
                    "telemetry-all-in-one": list(),
                    "telemetry-ignore-host": list(),
                    "telemetry-graphs": list(),
                    "url": str()
                }

            ctrl_panel = ControlPanel(
                CP_PARAMS,
                store.get("control-panel", dict())
            )
            store_sel = store["selected-tests"]
            tm_data = store["telemetry-data"]
            tm_user = store["selected-metrics"]
            tm_panels = store["telemetry-panels"]
            tm_all_in_one = store["telemetry-all-in-one"]
            tm_ignore_host = store["telemetry-ignore-host"]

            plotting_area_telemetry = no_update
            on_draw = [False, False]  # 0 --> trending, 1 --> telemetry

            # Parse the url:
            parsed_url = url_decode(href)
            if parsed_url:
                url_params = parsed_url["params"]
            else:
                url_params = None

            if tm_user is None:
                # Telemetry user data
                # The data provided by user or result of user action
                tm_user = {
                    # List of unique metrics:
                    "unique_metrics": list(),
                    # List of metrics selected by user:
                    "selected_metrics": list(),
                    # Labels from metrics selected by user (key: label name,
                    # value: list of all possible values):
                    "unique_labels": dict(),
                    # Labels selected by the user (subset of 'unique_labels'):
                    "selected_labels": dict(),
                    # All unique metrics with labels (output from the step 1)
                    # converted from pandas dataframe to dictionary.
                    "unique_metrics_with_labels": dict(),
                    # Metrics with labels selected by the user using dropdowns.
                    "selected_metrics_with_labels": dict()
                }
            tm = TelemetryData(store_sel) if store_sel else TelemetryData()

            trigger = Trigger(callback_context.triggered)
            if trigger.type == "url" and url_params:
                telemetry = None
                try:
                    store_sel = literal_eval(url_params["store_sel"][0])
                    normalize = literal_eval(url_params["norm"][0])
                    telemetry = literal_eval(url_params["telemetry"][0])
                    url_p = url_params.get("all-in-one", ["[[None]]"])
                    tm_all_in_one = literal_eval(url_p[0])
                    url_p = url_params.get("ignore-host", ["[[None]]"])
                    tm_ignore_host = literal_eval(url_p[0])
                    if not isinstance(telemetry, list):
                        telemetry = [telemetry, ]
                except (KeyError, IndexError, AttributeError, ValueError):
                    pass
                if store_sel:
                    last_test = store_sel[-1]
                    test = self._spec_tbs[last_test["dut"]]\
                        [last_test["area"]][last_test["test"]][last_test["phy"]]
                    ctrl_panel.set({
                        "dd-dut-val": last_test["dut"],
                        "dd-area-val": last_test["area"],
                        "dd-area-opt": [
                            {"label": label(v), "value": v} for v in sorted(
                                self._spec_tbs[last_test["dut"]].keys())
                        ],
                        "dd-area-dis": False,
                        "dd-test-val": last_test["test"],
                        "dd-test-opt": generate_options(
                            self._spec_tbs[last_test["dut"]]\
                                [last_test["area"]].keys()
                        ),
                        "dd-test-dis": False,
                        "dd-phy-val": last_test["phy"],
                        "dd-phy-opt": generate_options(
                            self._spec_tbs[last_test["dut"]][last_test["area"]]\
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
                    store["trending-graphs"] = None
                    store["telemetry-graphs"] = list()
                    on_draw[0] = True
                    if telemetry:
                        tm = TelemetryData(store_sel)
                        tm.from_dataframe(self._data)
                        tm_data = tm.to_json()
                        tm.from_json(tm_data)
                        tm_panels = telemetry
                        on_draw[1] = True
            elif trigger.type == "normalize":
                ctrl_panel.set({"cl-normalize-val": trigger.value})
                store["trending-graphs"] = None
                on_draw[0] = True
            elif trigger.type == "show-trials":
                ctrl_panel.set({"cl-show-trials": trigger.value})
                store["trending-graphs"] = None
                on_draw[0] = True
            elif trigger.type == "ctrl-dd":
                if trigger.idx == "dut":
                    try:
                        dut = self._spec_tbs[trigger.value]
                        options = [{"label": label(v), "value": v} \
                            for v in sorted(dut.keys())]
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "dd-dut-val": trigger.value,
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
                if trigger.idx == "area":
                    try:
                        dut = ctrl_panel.get("dd-dut-val")
                        area = self._spec_tbs[dut][trigger.value]
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
                if trigger.idx == "test":
                    try:
                        dut = ctrl_panel.get("dd-dut-val")
                        area = ctrl_panel.get("dd-area-val")
                        test = self._spec_tbs[dut][area][trigger.value]
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
                if trigger.idx == "phy":
                    dut = ctrl_panel.get("dd-dut-val")
                    area = ctrl_panel.get("dd-area-val")
                    test = ctrl_panel.get("dd-test-val")
                    if all((dut, area, test, trigger.value, )):
                        phy = self._spec_tbs[dut][area][test][trigger.value]
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
                tm_panels = list()
                tm_all_in_one = list()
                tm_ignore_host = list()
                store["trending-graphs"] = None
                store["telemetry-graphs"] = list()
                on_draw = [True, True]
                if trigger.idx == "add-test":
                    dut = ctrl_panel.get("dd-dut-val")
                    phy = ctrl_panel.get("dd-phy-val")
                    area = ctrl_panel.get("dd-area-val")
                    test = ctrl_panel.get("dd-test-val")
                    # Add selected test(s) to the list of tests in store:
                    if store_sel is None:
                        store_sel = list()
                    for core in ctrl_panel.get("cl-core-val"):
                        for framesize in ctrl_panel.get("cl-frmsize-val"):
                            for ttype in ctrl_panel.get("cl-tsttype-val"):
                                if dut == "trex":
                                    core = str()
                                tid = "-".join((
                                    dut,
                                    phy.replace('af_xdp', 'af-xdp'),
                                    area,
                                    framesize.lower(),
                                    core.lower(),
                                    test,
                                    ttype.lower()
                                ))
                                if tid not in [i["id"] for i in store_sel]:
                                    store_sel.append({
                                        "id": tid,
                                        "dut": dut,
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
            elif trigger.type == "telemetry-btn":
                if trigger.idx in ("open", "back"):
                    tm.from_dataframe(self._data)
                    tm_data = tm.to_json()
                    tm_user["unique_metrics"] = tm.unique_metrics
                    tm_user["selected_metrics"] = list()
                    tm_user["unique_labels"] = dict()
                    tm_user["selected_labels"] = dict()
                    search_out = (
                        get_list_group_items(tm_user["unique_metrics"],
                            "tele-cl", False),
                    )
                    is_open = (True, False)
                    tm_btns_disabled[1], tm_btns_disabled[5] = False, True
                elif trigger.idx == "select":
                    if any(cl_metrics):
                        tm.from_json(tm_data)
                        if not tm_user["selected_metrics"]:
                            tm_user["selected_metrics"] = \
                                tm_user["unique_metrics"]
                        metrics = [a for a, b in \
                            zip(tm_user["selected_metrics"], cl_metrics) if b]
                        tm_user["selected_metrics"] = metrics
                        tm_user["unique_labels"] = \
                            tm.get_selected_labels(metrics)
                        tm_user["unique_metrics_with_labels"] = \
                            tm.unique_metrics_with_labels
                        list_metrics[0] = tm.str_metrics
                        tm_dd[0] = _get_dd_container(tm_user["unique_labels"])
                        if list_metrics[0]:
                            tm_btns_disabled[1] = True
                            tm_btns_disabled[4] = False
                        is_open = (False, True)
                    else:
                        is_open = (True, False)
                elif trigger.idx == "add":
                    tm.from_json(tm_data)
                    tm_panels.append(tm_user["selected_metrics_with_labels"])
                    tm_all_in_one.append(all_in_one)
                    tm_ignore_host.append(ignore_host)
                    is_open = (False, False)
                    tm_btns_disabled[1], tm_btns_disabled[5] = True, True
                    on_draw = [True, True]
                elif trigger.idx == "cancel":
                    is_open = (False, False)
                    tm_btns_disabled[1], tm_btns_disabled[5] = True, True
                elif trigger.idx == "rm-all":
                    tm_panels = list()
                    tm_all_in_one = list()
                    tm_ignore_host = list()
                    tm_user = None
                    is_open = (False, False)
                    tm_btns_disabled[1], tm_btns_disabled[5] = True, True
                    plotting_area_telemetry = C.PLACEHOLDER
            elif trigger.type == "telemetry-search-in":
                tm.from_metrics(tm_user["unique_metrics"])
                tm_user["selected_metrics"] = \
                    tm.search_unique_metrics(trigger.value)
                search_out = (get_list_group_items(
                    tm_user["selected_metrics"],
                    type="tele-cl",
                    colorize=False
                ), )
                is_open = (True, False)
            elif trigger.type == "tm-dd":
                tm.from_metrics_with_labels(
                    tm_user["unique_metrics_with_labels"]
                )
                selected = dict()
                previous_itm = None
                for itm in tm_dd_in:
                    if itm is None:
                        show_new = True
                    elif isinstance(itm, str):
                        show_new = False
                        selected[itm] = list()
                    elif isinstance(itm, list):
                        if previous_itm is not None:
                            selected[previous_itm] = itm
                        show_new = True
                    previous_itm = itm
                tm_dd[0] = _get_dd_container(
                    tm_user["unique_labels"],
                    selected,
                    show_new
                )
                sel_metrics = tm.filter_selected_metrics_by_labels(selected)
                tm_user["selected_metrics_with_labels"] = sel_metrics.to_dict()
                if not sel_metrics.empty:
                    list_metrics[0] = tm.metrics_to_str(sel_metrics)
                    tm_btns_disabled[5] = False
                else:
                    list_metrics[0] = str()
            elif trigger.type == "tm-btn-remove":
                del tm_panels[trigger.idx]
                del tm_all_in_one[trigger.idx]
                del tm_ignore_host[trigger.idx]
                del store["telemetry-graphs"][trigger.idx]
                tm.from_json(tm_data)
                on_draw = [True, True]

            new_url_params = {
                "store_sel": store_sel,
                "norm": ctrl_panel.get("cl-normalize-val")
            }
            if tm_panels:
                new_url_params["telemetry"] = tm_panels
                new_url_params["all-in-one"] = tm_all_in_one
                new_url_params["ignore-host"] = tm_ignore_host

            if on_draw[0]:  # Trending
                if store_sel:
                    lg_selected = get_list_group_items(store_sel, "sel-cl")
                    if store["trending-graphs"]:
                        graphs = store["trending-graphs"]
                    else:
                        graphs = graph_trending(
                            self._data,
                            store_sel,
                            self._graph_layout,
                            bool(ctrl_panel.get("cl-normalize-val")),
                            bool(ctrl_panel.get("cl-show-trials"))
                        )
                        if graphs and graphs[0]:
                            store["trending-graphs"] = graphs
                    plotting_area_trending = \
                        Layout._plotting_area_trending(graphs)

                    # Telemetry
                    start_idx = len(store["telemetry-graphs"])
                    end_idx = len(tm_panels)
                    if not end_idx:
                        plotting_area_telemetry = C.PLACEHOLDER
                    elif on_draw[1] and (end_idx >= start_idx):
                        if len(tm_all_in_one) != end_idx:
                            tm_all_in_one = [[None], ] * end_idx
                        if len(tm_ignore_host) != end_idx:
                            tm_ignore_host = [[None], ] * end_idx
                        for idx in range(start_idx, end_idx):
                            store["telemetry-graphs"].append(graph_tm_trending(
                                tm.select_tm_trending_data(
                                    tm_panels[idx],
                                    ignore_host=bool(tm_ignore_host[idx][0])
                                ),
                                self._graph_layout,
                                bool(tm_all_in_one[idx][0])
                            ))
                        plotting_area_telemetry = \
                            Layout._plotting_area_telemetry(
                                store["telemetry-graphs"]
                            )
                    col_plotting_area = C.STYLE_ENABLED
                    row_selected_tests = C.STYLE_ENABLED
                else:
                    plotting_area_trending = no_update
                    plotting_area_telemetry = C.PLACEHOLDER
                    col_plotting_area = C.STYLE_DISABLED
                    row_selected_tests = C.STYLE_DISABLED
                    lg_selected = no_update
                    store_sel = list()
                    tm_panels = list()
                    tm_all_in_one = list()
                    tm_ignore_host = list()
                    tm_user = None
            else:
                plotting_area_trending = no_update
                col_plotting_area = no_update
                row_selected_tests = no_update
                lg_selected = no_update

            store["url"] = gen_new_url(parsed_url, new_url_params)
            store["control-panel"] = ctrl_panel.panel
            store["selected-tests"] = store_sel
            store["telemetry-data"] = tm_data
            store["selected-metrics"] = tm_user
            store["telemetry-panels"] = tm_panels
            store["telemetry-all-in-one"] = tm_all_in_one
            store["telemetry-ignore-host"] = tm_ignore_host
            ret_val = [
                store,
                plotting_area_trending,
                plotting_area_telemetry,
                col_plotting_area,
                row_selected_tests,
                lg_selected,
                search_out,
                is_open,
                tm_btns_disabled,
                tm_dd,
                list_metrics
            ]
            ret_val.extend(ctrl_panel.values)
            return ret_val

        @app.callback(
            Output("plot-mod-url", "is_open"),
            Output("mod-url", "children"),
            State("store", "data"),
            State("plot-mod-url", "is_open"),
            Input("plot-btn-url", "n_clicks")
        )
        def toggle_plot_mod_url(store, is_open, n_clicks):
            """Toggle the modal window with url.
            """
            if not store:
                raise PreventUpdate

            if n_clicks:
                return not is_open, store.get("url", str())
            return is_open, store["url"]

        def _get_dd_container(
                all_labels: dict,
                selected_labels: dict=dict(),
                show_new=True
            ) -> list:
            """Generate a container with dropdown selection boxes depenting on
            the input data.

            :param all_labels: A dictionary with unique labels and their
                possible values.
            :param selected_labels: A dictionalry with user selected lables and
                their values.
            :param show_new: If True, a dropdown selection box to add a new
                label is displayed.
            :type all_labels: dict
            :type selected_labels: dict
            :type show_new: bool
            :returns: A list of dbc rows with dropdown selection boxes.
            :rtype: list
            """

            def _row(
                    id: str,
                    lopts: list=list(),
                    lval: str=str(),
                    vopts: list=list(),
                    vvals: list=list()
                ) -> dbc.Row:
                """Generates a dbc row with dropdown boxes.

                :param id: A string added to the dropdown ID.
                :param lopts: A list of options for 'label' dropdown.
                :param lval: Value of 'label' dropdown.
                :param vopts: A list of options for 'value' dropdown.
                :param vvals: A list of values for 'value' dropdown.
                :type id: str
                :type lopts: list
                :type lval: str
                :type vopts: list
                :type vvals: list
                :returns: dbc row with dropdown boxes.
                :rtype: dbc.Row
                """
                children = list()
                if lopts:
                    children.append(
                        dbc.Col(
                            width=6,
                            children=[
                                dcc.Dropdown(
                                    id={
                                        "type": "tm-dd",
                                        "index": f"label-{id}"
                                    },
                                    placeholder="Select a label...",
                                    optionHeight=20,
                                    multi=False,
                                    options=lopts,
                                    value=lval if lval else None
                                )
                            ]
                        )
                    )
                    if vopts:
                        children.append(
                            dbc.Col(
                                width=6,
                                children=[
                                    dcc.Dropdown(
                                        id={
                                            "type": "tm-dd",
                                            "index": f"value-{id}"
                                        },
                                        placeholder="Select a value...",
                                        optionHeight=20,
                                        multi=True,
                                        options=vopts,
                                        value=vvals if vvals else None
                                    )
                                ]
                            )
                        )

                return dbc.Row(class_name="g-0 p-1", children=children)

            container = list()

            # Display rows with items in 'selected_labels'; label on the left,
            # values on the right:
            keys_left = list(all_labels.keys())
            for idx, label in enumerate(selected_labels.keys()):
                container.append(_row(
                    id=idx,
                    lopts=deepcopy(keys_left),
                    lval=label,
                    vopts=all_labels[label],
                    vvals=selected_labels[label]
                ))
                keys_left.remove(label)

            # Display row with dd with labels on the left, right side is empty:
            if show_new and keys_left:
                container.append(_row(id="new", lopts=keys_left))

            return container

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
            
            return show_trending_graph_data(
                    trigger, graph_data, self._graph_layout)

        @app.callback(
            Output("download-trending-data", "data"),
            State("store", "data"),
            Input("plot-btn-download", "n_clicks"),
            Input({"type": "tm-btn-download", "index": ALL}, "n_clicks"),
            prevent_initial_call=True
        )
        def _download_data(store: list, *_) -> dict:
            """Download the data

            :param store_sel: List of tests selected by user stored in the
                browser.
            :type store_sel: list
            :returns: dict of data frame content (base64 encoded) and meta data
                used by the Download component.
            :rtype: dict
            """

            if not store:
                raise PreventUpdate
            if not store["selected-tests"]:
                raise PreventUpdate
            
            df = pd.DataFrame()
            
            trigger = Trigger(callback_context.triggered)
            if not trigger.value:
                raise PreventUpdate
            
            if trigger.type == "plot-btn-download":
                data = list()
                for itm in store["selected-tests"]:
                    sel_data = select_trending_data(self._data, itm)
                    if sel_data is None:
                        continue
                    data.append(sel_data)
                df = pd.concat(data, ignore_index=True, copy=False)
                file_name = C.TREND_DOWNLOAD_FILE_NAME
            elif trigger.type == "tm-btn-download":
                tm = TelemetryData(store["selected-tests"])
                tm.from_json(store["telemetry-data"])
                df = tm.select_tm_trending_data(
                    store["telemetry-panels"][trigger.idx]
                )
                file_name = C.TELEMETRY_DOWNLOAD_FILE_NAME
            else:
                raise PreventUpdate

            return dcc.send_data_frame(df.to_csv, file_name)

        @app.callback(
            Output("offcanvas-documentation", "is_open"),
            Input("btn-documentation", "n_clicks"),
            State("offcanvas-documentation", "is_open")
        )
        def toggle_offcanvas_documentation(n_clicks, is_open):
            if n_clicks:
                return not is_open
            return is_open
