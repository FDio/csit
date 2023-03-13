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
from ..utils.utils import show_tooltip


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
            "job", "test_id", "test_type", "dut_version", "tg_type"  #, "release"
        ]
        for _, row in self._data[cols].drop_duplicates().iterrows():
            # rls = row["release"]
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
            if tbs[dut].get(dver, None) is None:
                tbs[dut][dver] = dict()
            if tbs[dut][dver].get(tbed, None) is None:
                tbs[dut][dver][tbed] = dict()
            if tbs[dut][dver][tbed].get(nic, None) is None:
                tbs[dut][dver][tbed][nic] = dict()
            if tbs[dut][dver][tbed][nic].get(drv, None) is None:
                tbs[dut][dver][tbed][nic][drv] = dict()
                tbs[dut][dver][tbed][nic][drv]["core"] = list()
                tbs[dut][dver][tbed][nic][drv]["fsize"] = list()
                tbs[dut][dver][tbed][nic][drv]["ttype"] = list()
            if core.upper() not in tbs[dut][dver][tbed][nic][drv]["core"]:
                tbs[dut][dver][tbed][nic][drv]["core"].append(core.upper())
            if fsize.upper() not in tbs[dut][dver][tbed][nic][drv]["fsize"]:
                tbs[dut][dver][tbed][nic][drv]["fsize"].append(fsize.upper())
            if row["test_type"] == "mrr":
                if "MRR" not in tbs[dut][dver][tbed][nic][drv]["ttype"]:
                    tbs[dut][dver][tbed][nic][drv]["ttype"].append("MRR")
            elif row["test_type"] == "ndrpdr":
                if "NDR" not in tbs[dut][dver][tbed][nic][drv]["ttype"]:
                    tbs[dut][dver][tbed][nic][drv]["ttype"].extend(
                        ("NDR", "PDR", )
                    )
            elif row["test_type"] == "hoststack" and \
                    row["tg_type"] in ("iperf", "vpp"):
                if "BPS" not in tbs[dut][dver][tbed][nic][drv]["ttype"]:
                    tbs[dut][dver][tbed][nic][drv]["ttype"].append("BPS")
            elif row["test_type"] == "hoststack" and row["tg_type"] == "ab":
                if "CPS" not in tbs[dut][dver][tbed][nic][drv]["ttype"]:
                    tbs[dut][dver][tbed][nic][drv]["ttype"].extend(
                        ("CPS", "RPS", )
                    )
        self._spec_tbs = tbs

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

        if self.html_layout and self._spec_tbs:
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
                            dbc.InputGroupText(
                                children=show_tooltip(
                                    self._tooltips,
                                    "help-dut-ver",
                                    "DUT Version"
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
                                    "help-testbed",
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
                                id={
                                    "type": "ctrl-cl",
                                    "index": "frmsize"
                                },
                                inline=True
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
                                id={
                                    "type": "ctrl-cl",
                                    "index": "core"
                                },
                                inline=True
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
                                id={
                                    "type": "ctrl-cl",
                                    "index": "ttype"
                                },
                                inline=True
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
                                    "label": (
                                        "Normalize to CPU frequency "
                                        "2GHz"
                                    )
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

    def callbacks(self, app):
        """Callbacks for the whole application.

        :param app: The application.
        :type app: Flask
        """
        pass