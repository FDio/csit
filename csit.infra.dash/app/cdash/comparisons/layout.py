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
from dash import html
from dash import callback_context, no_update, ALL
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from yaml import load, FullLoader, YAMLError
from ast import literal_eval

from ..utils.constants import Constants as C
from ..utils.control_panel import ControlPanel
from ..utils.trigger import Trigger
from ..utils.url_processing import url_decode
from ..utils.utils import show_tooltip, generate_options, gen_new_url
from .tables import comparison_table


# Control panel partameters and their default values.
CP_PARAMS = {
    "dd-dut-val": str(),
    "dd-rls-opt": list(),
    "dd-rls-dis": True,
    "dd-rls-val": str(),
    "dd-dutver-opt": list(),
    "dd-dutver-dis": True,
    "dd-dutver-val": str(),
    "dd-tbed-opt": list(),
    "dd-tbed-dis": True,
    "dd-tbed-val": str(),
    "dd-nic-opt": list(),
    "dd-nic-dis": True,
    "dd-nic-val": str(),
    "dd-driver-opt": list(),
    "dd-driver-dis": True,
    "dd-driver-val": str(),
    "cl-core-opt": list(),
    "cl-core-val": list(),
    "cl-frmsize-opt": list(),
    "cl-frmsize-val": list(),
    "cl-ttype-opt": list(),
    "cl-ttype-val": list(),
    "cl-normalize-val": list(),
    "btn-ref-dis": True,
    "btn-cmp-dis": True
}


class Layout:
    """The layout of the dash app and the callbacks.
    """

    def __init__(
            self,
            app: Flask,
            data_iterative: pd.DataFrame,
            html_layout_file: str,
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
        :param tooltip_file: Path and name of the yaml file specifying the
            tooltips.
        :type app: Flask
        :type html_layout_file: str

        :type tooltip_file: str
        """

        # Inputs
        self._app = app
        self._html_layout_file = html_layout_file
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
            dver = row["dut_version"]
            if dut == "vpp":
                dver = dver.split("~")[0]            
            tbed = "-".join(lst_job[-2:])
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
            lst_test = test.split("-")
            fsize = lst_test[0]
            core = lst_test[1] if lst_test[1] else "8C"

            if tbs.get(dut, None) is None:
                tbs[dut] = dict()
            if tbs[dut].get(rls, None) is None:
                tbs[dut][rls] = dict()
            if tbs[dut][rls].get(dver, None) is None:
                tbs[dut][rls][dver] = dict()
            if tbs[dut][rls][dver].get(tbed, None) is None:
                tbs[dut][rls][dver][tbed] = dict()
            if tbs[dut][rls][dver][tbed].get(nic, None) is None:
                tbs[dut][rls][dver][tbed][nic] = dict()
            if tbs[dut][rls][dver][tbed][nic].get(drv, None) is None:
                tbs[dut][rls][dver][tbed][nic][drv] = dict()
                tbs[dut][rls][dver][tbed][nic][drv]["core"] = list()
                tbs[dut][rls][dver][tbed][nic][drv]["fsize"] = list()
                tbs[dut][rls][dver][tbed][nic][drv]["ttype"] = list()
            if core.upper() not in tbs[dut][rls][dver][tbed][nic][drv]["core"]:
                tbs[dut][rls][dver][tbed][nic][drv]["core"].append(core.upper())
            if fsize.upper() not in \
                    tbs[dut][rls][dver][tbed][nic][drv]["fsize"]:
                tbs[dut][rls][dver][tbed][nic][drv]["fsize"].append(
                    fsize.upper()
                )
            if row["test_type"] == "mrr":
                if "MRR" not in tbs[dut][rls][dver][tbed][nic][drv]["ttype"]:
                    tbs[dut][rls][dver][tbed][nic][drv]["ttype"].append("MRR")
            elif row["test_type"] == "ndrpdr":
                if "NDR" not in tbs[dut][rls][dver][tbed][nic][drv]["ttype"]:
                    tbs[dut][rls][dver][tbed][nic][drv]["ttype"].extend(
                        ("NDR", "PDR", )
                    )
            elif row["test_type"] == "hoststack" and \
                    row["tg_type"] in ("iperf", "vpp"):
                if "BPS" not in tbs[dut][rls][dver][tbed][nic][drv]["ttype"]:
                    tbs[dut][rls][dver][tbed][nic][drv]["ttype"].append("BPS")
            elif row["test_type"] == "hoststack" and row["tg_type"] == "ab":
                if "CPS" not in tbs[dut][rls][dver][tbed][nic][drv]["ttype"]:
                    tbs[dut][rls][dver][tbed][nic][drv]["ttype"].extend(
                        ("CPS", "RPS", )
                    )
        self._tbs = tbs

        # Read from files:
        self._html_layout = str()
        self._tooltips = dict()

        try:
            with open(self._html_layout_file, "r") as file_read:
                self._html_layout = file_read.read()
        except IOError as err:
            raise RuntimeError(
                f"Not possible to open the file {self._html_layout_file}\n{err}"
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
                        children=[
                            self._add_navbar()
                        ]
                    ),
                    dbc.Row(
                        id="row-main",
                        class_name="g-0",
                        children=[
                            dcc.Store(id="store-control-panel"),
                            dcc.Store(id="store-selected"),
                            dcc.Location(id="url", refresh=False),
                            self._add_ctrl_col(),
                            self._add_plotting_col()
                        ]
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

    def _add_navbar(self):
        """Add nav element with navigation panel. It is placed on the top.

        :returns: Navigation bar.
        :rtype: dbc.NavbarSimple
        """
        return dbc.NavbarSimple(
            id="navbarsimple-main",
            children=[
                dbc.NavItem(
                    dbc.NavLink(
                        C.COMP_TITLE,
                        disabled=True,
                        external_link=True,
                        href="#"
                    )
                )
            ],
            brand=C.BRAND,
            brand_href="/",
            brand_external_link=True,
            class_name="p-2",
            fluid=True
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
        return [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                children=show_tooltip(
                                    self._tooltips,
                                    "help-dut",
                                    "DUT"
                                )
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
                            dbc.InputGroupText(
                                children=show_tooltip(
                                    self._tooltips,
                                    "help-release",
                                    "CSIT Release"
                                )
                            ),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "rls"},
                                placeholder="Select a CSIT Release...",
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
                                    "help-dut-ver",
                                    "Tested DUT Version"
                                )
                            ),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "dutver"},
                                placeholder="Select a Version of DUT...")
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
                                    "help-tbed",
                                    "Test Bed"
                                )
                            ),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "tbed"},
                                placeholder="Select a Test Bed..."
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
                                    "help-nic",
                                    "NIC"
                                )
                            ),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "nic"},
                                placeholder="Select a NIC..."
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
                                    "help-driver",
                                    "Driver"
                                )
                            ),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "driver"},
                                placeholder="Select a Driver..."
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
                            dbc.InputGroupText(
                                children=show_tooltip(
                                    self._tooltips,
                                    "help-cores",
                                    "Number of Cores"
                                )
                            ),
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
                            dbc.InputGroupText(
                                children=show_tooltip(
                                    self._tooltips,
                                    "help-ttype",
                                    "Test Type"
                                )
                            ),
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
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                children=show_tooltip(
                                    self._tooltips,
                                    "help-normalize",
                                    "Normalization"
                                )
                            ),
                            dbc.Checklist(
                                id="normalize",
                                options=[{
                                    "value": "normalize",
                                    "label": "Normalize to CPU frequency 2GHz"
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
            ),
            dbc.Row(
                # id="row-btns-sel-tests",
                class_name="g-0 p-1",
                # style=C.STYLE_DISABLED,
                children=[
                    dbc.ButtonGroup(
                        children=[
                            dbc.Button(
                                id={"type": "ctrl-btn", "index": "reference"},
                                children="Set Reference",
                                class_name="w-100",
                                color="info",
                                disabled=True
                            ),
                            dbc.Button(
                                id={"type": "ctrl-btn", "index": "compare"},
                                children="Set Compare",
                                class_name="w-100",
                                color="info",
                                disabled=True
                            )
                        ]
                    )
                ]
            )
        ]

    def _get_plotting_area(
            self,
            selected: dict,
            url: str,
            normalize: bool
        ) -> list:
        """Generate the plotting area with all its content.

        :param selected: Selected parameters of tests.
        :param normalize: If true, the values in tables are normalized.
        :param url: URL to be displayed in the modal window.
        :type selected: dict
        :type normalize: bool
        :type url: str
        :returns: List of rows with elements to be displayed in the plotting
            area.
        :rtype: list
        """

        table = comparison_table(self._data, selected, normalize)

        if not table:
            return C.PLACEHOLDER

        row_items = [
            dbc.Col(
                children=table,
                class_name="g-0 p-1",
            )
        ]

        return [
            dbc.Row(
                children=row_items,
                class_name="g-0 p-0",
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
                Output("plotting-area", "children"),
                Output({"type": "ctrl-dd", "index": "dut"}, "value"),
                Output({"type": "ctrl-dd", "index": "rls"}, "options"),
                Output({"type": "ctrl-dd", "index": "rls"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "rls"}, "value"),
                Output({"type": "ctrl-dd", "index": "dutver"}, "options"),
                Output({"type": "ctrl-dd", "index": "dutver"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "dutver"}, "value"),
                Output({"type": "ctrl-dd", "index": "tbed"}, "options"),
                Output({"type": "ctrl-dd", "index": "tbed"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "tbed"}, "value"),
                Output({"type": "ctrl-dd", "index": "nic"}, "options"),
                Output({"type": "ctrl-dd", "index": "nic"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "nic"}, "value"),
                Output({"type": "ctrl-dd", "index": "driver"}, "options"),
                Output({"type": "ctrl-dd", "index": "driver"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "driver"}, "value"),
                Output({"type": "ctrl-cl", "index": "core"}, "options"),
                Output({"type": "ctrl-cl", "index": "core"}, "value"),
                Output({"type": "ctrl-cl", "index": "frmsize"}, "options"),
                Output({"type": "ctrl-cl", "index": "frmsize"}, "value"),
                Output({"type": "ctrl-cl", "index": "ttype"}, "options"),
                Output({"type": "ctrl-cl", "index": "ttype"}, "value"),
                Output("normalize", "value"),
                Output({"type": "ctrl-btn", "index": "reference"}, "disabled"),
                Output({"type": "ctrl-btn", "index": "compare"}, "disabled")
            ],
            [
                State("store-control-panel", "data"),
                State("store-selected", "data")
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
                selected: dict,
                href: str,
                normalize: list,
                *_
            ) -> tuple:
            """Update the application when the event is detected.
            """
            
            ctrl_panel = ControlPanel(CP_PARAMS, control_panel)

            if selected is None:
                selected = {
                    "reference": {
                        "set": False
                    },
                    "compare": {
                        "set": False
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
                pass
            elif trigger.type == "normalize":
                ctrl_panel.set({"cl-normalize-val": normalize})
                on_draw = True
            elif trigger.type == "ctrl-dd":
                if trigger.idx == "dut":
                    try:
                        options = generate_options(
                            self._tbs[trigger.value].keys()
                        )
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "dd-dut-val": trigger.value,
                        "dd-rls-opt": options,
                        "dd-rls-dis": disabled,
                        "dd-rls-val": str(),
                        "dd-dutver-opt": list(),
                        "dd-dutver-dis": True,
                        "dd-dutver-val": str(),
                        "dd-tbed-opt": list(),
                        "dd-tbed-dis": True,
                        "dd-tbed-val": str(),
                        "dd-nic-opt": list(),
                        "dd-nic-dis": True,
                        "dd-nic-val": str(),
                        "dd-driver-opt": list(),
                        "dd-driver-dis": True,
                        "dd-driver-val": str(),
                        "cl-core-opt": list(),
                        "cl-core-val": list(),
                        "cl-frmsize-opt": list(),
                        "cl-frmsize-val": list(),
                        "cl-ttype-opt": list(),
                        "cl-ttype-val": list(),
                        "btn-ref-dis": True,
                        "btn-cmp-dis": True
                    })
                elif trigger.idx == "rls":
                    try:
                        dut = ctrl_panel.get("dd-dut-val")
                        rls = self._tbs[dut][trigger.value]
                        options = generate_options(rls.keys())
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "dd-rls-val": trigger.value,
                        "dd-dutver-opt": options,
                        "dd-dutver-dis": disabled,
                        "dd-dutver-val": str(),
                        "dd-tbed-opt": list(),
                        "dd-tbed-dis": True,
                        "dd-tbed-val": str(),
                        "dd-nic-opt": list(),
                        "dd-nic-dis": True,
                        "dd-nic-val": str(),
                        "dd-driver-opt": list(),
                        "dd-driver-dis": True,
                        "dd-driver-val": str(),
                        "cl-core-opt": list(),
                        "cl-core-val": list(),
                        "cl-frmsize-opt": list(),
                        "cl-frmsize-val": list(),
                        "cl-ttype-opt": list(),
                        "cl-ttype-val": list(),
                        "btn-ref-dis": True,
                        "btn-cmp-dis": True
                    })
                elif trigger.idx == "dutver":
                    try:
                        dut = ctrl_panel.get("dd-dut-val")
                        rls = ctrl_panel.get("dd-rls-val")
                        dver = self._tbs[dut][rls][trigger.value]
                        options = generate_options(dver.keys())
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "dd-dutver-val": trigger.value,
                        "dd-tbed-opt": options,
                        "dd-tbed-dis": disabled,
                        "dd-tbed-val": str(),
                        "dd-nic-opt": list(),
                        "dd-nic-dis": True,
                        "dd-nic-val": str(),
                        "dd-driver-opt": list(),
                        "dd-driver-dis": True,
                        "dd-driver-val": str(),
                        "cl-core-opt": list(),
                        "cl-core-val": list(),
                        "cl-frmsize-opt": list(),
                        "cl-frmsize-val": list(),
                        "cl-ttype-opt": list(),
                        "cl-ttype-val": list(),
                        "btn-ref-dis": True,
                        "btn-cmp-dis": True
                    })
                elif trigger.idx == "tbed":
                    try:
                        dut = ctrl_panel.get("dd-dut-val")
                        rls = ctrl_panel.get("dd-rls-val")
                        dver = ctrl_panel.get("dd-dutver-val")
                        tbed = self._tbs[dut][rls][dver][trigger.value]
                        options = generate_options(tbed.keys())
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "dd-tbed-val": trigger.value,
                        "dd-nic-opt": options,
                        "dd-nic-dis": disabled,
                        "dd-nic-val": str(),
                        "dd-driver-opt": list(),
                        "dd-driver-dis": True,
                        "dd-driver-val": str(),
                        "cl-core-opt": list(),
                        "cl-core-val": list(),
                        "cl-frmsize-opt": list(),
                        "cl-frmsize-val": list(),
                        "cl-ttype-opt": list(),
                        "cl-ttype-val": list(),
                        "btn-ref-dis": True,
                        "btn-cmp-dis": True
                    })
                elif trigger.idx == "nic":
                    try:
                        dut = ctrl_panel.get("dd-dut-val")
                        rls = ctrl_panel.get("dd-rls-val")
                        dver = ctrl_panel.get("dd-dutver-val")
                        tbed = ctrl_panel.get("dd-tbed-val")
                        nic = self._tbs[dut][rls][dver][tbed][trigger.value]
                        options = generate_options(nic.keys())
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "dd-nic-val": trigger.value,
                        "dd-driver-opt": options,
                        "dd-driver-dis": disabled,
                        "dd-driver-val": str(),
                        "cl-core-opt": list(),
                        "cl-core-val": list(),
                        "cl-frmsize-opt": list(),
                        "cl-frmsize-val": list(),
                        "cl-ttype-opt": list(),
                        "cl-ttype-val": list(),
                        "btn-ref-dis": True,
                        "btn-cmp-dis": True
                    })
                elif trigger.idx == "driver":
                    dut = ctrl_panel.get("dd-dut-val")
                    rls = ctrl_panel.get("dd-rls-val")
                    dver = ctrl_panel.get("dd-dutver-val")
                    tbed = ctrl_panel.get("dd-tbed-val")
                    nic = ctrl_panel.get("dd-nic-val")
                    if all((dut, rls, dver, tbed, nic, trigger.value, )):
                        driver = \
                            self._tbs[dut][rls][dver][tbed][nic][trigger.value]
                        ctrl_panel.set({
                            "dd-driver-val": trigger.value,
                            "cl-core-opt": generate_options(driver["core"]),
                            "cl-core-val": list(),
                            "cl-frmsize-opt": generate_options(driver["fsize"]),
                            "cl-frmsize-val": list(),
                            "cl-ttype-opt": generate_options(driver["ttype"]),
                            "cl-ttype-val": list(),
                            "btn-ref-dis": True,
                            "btn-cmp-dis": True
                        })
            elif trigger.type == "ctrl-cl":
                ctrl_panel.set({f"cl-{trigger.idx}-val": trigger.value})
                if all((ctrl_panel.get("cl-core-val"),
                        ctrl_panel.get("cl-frmsize-val"),
                        ctrl_panel.get("cl-ttype-val"), )):
                    ctrl_panel.set({
                        "btn-ref-dis": False,
                        "btn-cmp-dis": False
                    })
                else:
                    ctrl_panel.set({
                        "btn-ref-dis": True,
                        "btn-cmp-dis": True
                    })
            elif trigger.type == "ctrl-btn":
                on_draw = True
                selected[trigger.idx] = {
                    "set": True,
                    "dut": ctrl_panel.get("dd-dut-val"),
                    "rls": ctrl_panel.get("dd-rls-val"),
                    "dutver": ctrl_panel.get("dd-dutver-val"),
                    "tbed": ctrl_panel.get("dd-tbed-val"),
                    "nic": ctrl_panel.get("dd-nic-val"),
                    "driver": ctrl_panel.get("dd-driver-val"),
                    "core": ctrl_panel.get("cl-core-val"),
                    "frmsize": ctrl_panel.get("cl-frmsize-val"),
                    "ttype": ctrl_panel.get("cl-ttype-val")
                }

            if all((on_draw, selected["reference"]["set"],
                    selected["compare"]["set"], )):
                plotting_area = self._get_plotting_area(
                    selected=selected,
                    normalize=bool(normalize),
                    url=gen_new_url(
                        parsed_url,
                        {"selected": selected, "norm": normalize}
                    )
                )

            ret_val = [
                ctrl_panel.panel,
                selected,
                plotting_area
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
            State("store-selected-tests", "data"),
            Input("plot-btn-download", "n_clicks"),
            prevent_initial_call=True
        )
        def _download_trending_data(store_sel, _):
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

            # TODO: Implement

            # for itm in store_sel:
            #     sel_data = select_iterative_data(self._data, itm)
            #     if sel_data is None:
            #         continue
            #     df = pd.concat([df, sel_data], ignore_index=True)

            return dcc.send_data_frame(df.to_csv, C.REPORT_DOWNLOAD_FILE_NAME)
