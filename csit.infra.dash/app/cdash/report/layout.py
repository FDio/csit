# Copyright (c) 2022 Cisco and/or its affiliates.
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
from copy import deepcopy
from ast import literal_eval

from ..utils.constants import Constants as C
from ..utils.utils import show_tooltip, label, sync_checklists, list_tests, \
    gen_new_url, generate_options
from ..utils.url_processing import url_decode
from ..data.data import Data
from .graphs import graph_iterative, table_comparison, get_short_version, \
    select_iterative_data


class Layout:
    """The layout of the dash app and the callbacks.
    """

    def __init__(self, app: Flask, releases: list, html_layout_file: str,
        graph_layout_file: str, data_spec_file: str, tooltip_file: str) -> None:
        """Initialization:
        - save the input parameters,
        - read and pre-process the data,
        - prepare data for the control panel,
        - read HTML layout file,
        - read tooltips from the tooltip file.

        :param app: Flask application running the dash application.
        :param releases: Lis of releases to be displayed.
        :param html_layout_file: Path and name of the file specifying the HTML
            layout of the dash application.
        :param graph_layout_file: Path and name of the file with layout of
            plot.ly graphs.
        :param data_spec_file: Path and name of the file specifying the data to
            be read from parquets for this application.
        :param tooltip_file: Path and name of the yaml file specifying the
            tooltips.
        :type app: Flask
        :type releases: list
        :type html_layout_file: str
        :type graph_layout_file: str
        :type data_spec_file: str
        :type tooltip_file: str
        """

        # Inputs
        self._app = app
        self.releases = releases
        self._html_layout_file = html_layout_file
        self._graph_layout_file = graph_layout_file
        self._data_spec_file = data_spec_file
        self._tooltip_file = tooltip_file

        # Read the data:
        self._data = pd.DataFrame()
        for rls in releases:
            data_mrr = Data(self._data_spec_file, True).\
                read_iterative_mrr(release=rls.replace("csit", "rls"))
            data_mrr["release"] = rls
            data_ndrpdr = Data(self._data_spec_file, True).\
                read_iterative_ndrpdr(release=rls.replace("csit", "rls"))
            data_ndrpdr["release"] = rls
            self._data = pd.concat(
                [self._data, data_mrr, data_ndrpdr], ignore_index=True)

        # Get structure of tests:
        tbs = dict()
        cols = ["job", "test_id", "test_type", "dut_version", "release"]
        for _, row in self._data[cols].drop_duplicates().iterrows():
            rls = row["release"]
            ttype = row["test_type"]
            lst_job = row["job"].split("-")
            dut = lst_job[1]
            d_ver = get_short_version(row["dut_version"], dut)
            tbed = "-".join(lst_job[-2:])
            lst_test_id = row["test_id"].split(".")
            if dut == "dpdk":
                area = "dpdk"
            else:
                area = "-".join(lst_test_id[3:-2])
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
            if tbs[rls][dut][d_ver].get(infra, None) is None:
                tbs[rls][dut][d_ver][infra] = dict()
            if tbs[rls][dut][d_ver][infra].get(area, None) is None:
                tbs[rls][dut][d_ver][infra][area] = dict()
            if tbs[rls][dut][d_ver][infra][area].get(test, None) is None:
                tbs[rls][dut][d_ver][infra][area][test] = dict()
                tbs[rls][dut][d_ver][infra][area][test]["core"] = list()
                tbs[rls][dut][d_ver][infra][area][test]["frame-size"] = list()
                tbs[rls][dut][d_ver][infra][area][test]["test-type"] = list()
            if core.upper() not in \
                    tbs[rls][dut][d_ver][infra][area][test]["core"]:
                tbs[rls][dut][d_ver][infra][area][test]["core"].append(
                    core.upper())
            if framesize.upper() not in \
                        tbs[rls][dut][d_ver][infra][area][test]["frame-size"]:
                tbs[rls][dut][d_ver][infra][area][test]["frame-size"].append(
                    framesize.upper())
            if ttype == "mrr":
                if "MRR" not in \
                        tbs[rls][dut][d_ver][infra][area][test]["test-type"]:
                    tbs[rls][dut][d_ver][infra][area][test]["test-type"].append(
                        "MRR")
            elif ttype == "ndrpdr":
                if "NDR" not in \
                        tbs[rls][dut][d_ver][infra][area][test]["test-type"]:
                    tbs[rls][dut][d_ver][infra][area][test]["test-type"].extend(
                        ("NDR", "PDR", ))
        self._spec_tbs = tbs

        # Read from files:
        self._html_layout = ""
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
        if self._app is not None and hasattr(self, 'callbacks'):
            self.callbacks(self._app)

    @property
    def html_layout(self):
        return self._html_layout

    @property
    def spec_tbs(self):
        return self._spec_tbs

    @property
    def data(self):
        return self._data

    @property
    def layout(self):
        return self._graph_layout

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

        if self.html_layout and self.spec_tbs:
            return html.Div(
                id="div-main",
                className="small",
                children=[
                    dbc.Row(
                        id="row-navbar",
                        class_name="g-0",
                        children=[
                            self._add_navbar(),
                        ]
                    ),
                    dcc.Loading(
                        dbc.Offcanvas(
                            class_name="w-50",
                            id="offcanvas-metadata",
                            title="Throughput And Latency",
                            placement="end",
                            is_open=False,
                            children=[
                                dbc.Row(id="metadata-tput-lat"),
                                dbc.Row(id="metadata-hdrh-graph"),
                            ]
                        )
                    ),
                    dbc.Row(
                        id="row-main",
                        class_name="g-0",
                        children=[
                            dcc.Store(id="selected-tests"),
                            dcc.Store(id="control-panel"),
                            dcc.Location(id="url", refresh=False),
                            self._add_ctrl_col(),
                            self._add_plotting_col(),
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
                            "An Error Occured",
                        ],
                        color="danger",
                    ),
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
                        C.REPORT_TITLE,
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
            fluid=True,
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
        """Add column with plots and tables. It is placed on the right side.

        :returns: Column with tables.
        :rtype: dbc.Col
        """
        return dbc.Col(
            id="col-plotting-area",
            children=[
                dcc.Loading(
                    children=[
                        dbc.Row(  # Graphs
                            class_name="g-0 p-2",
                            children=[
                                dbc.Col(
                                    dbc.Row(  # Throughput
                                        id="row-graph-tput",
                                        class_name="g-0 p-2",
                                        children=[C.PLACEHOLDER, ]
                                    ),
                                    width=6
                                ),
                                dbc.Col(
                                    dbc.Row(  # Latency
                                        id="row-graph-lat",
                                        class_name="g-0 p-2",
                                        children=[C.PLACEHOLDER, ]
                                    ),
                                    width=6
                                )
                            ]
                        ),
                        dbc.Row(  # Tables
                            id="row-table",
                            class_name="g-0 p-2",
                            children=[C.PLACEHOLDER, ]
                        ),
                        dbc.Row(  # Download
                            id="row-btn-download",
                            class_name="g-0 p-2",
                            children=[C.PLACEHOLDER, ]
                        )
                    ]
                )
            ],
            width=9
        )

    def _add_ctrl_panel(self) -> dbc.Row:
        """Add control panel.

        :returns: Control panel.
        :rtype: dbc.Row
        """
        return [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                children=show_tooltip(self._tooltips,
                                    "help-release", "CSIT Release")
                            ),
                            dbc.Select(
                                id="dd-ctrl-rls",
                                placeholder=("Select a Release..."),
                                options=sorted(
                                    [
                                        {"label": k, "value": k} \
                                            for k in self.spec_tbs.keys()
                                    ],
                                    key=lambda d: d["label"]
                                )
                            )
                        ],
                        size="sm",
                    ),
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                children=show_tooltip(self._tooltips,
                                    "help-dut", "DUT")
                            ),
                            dbc.Select(
                                id="dd-ctrl-dut",
                                placeholder=(
                                    "Select a Device under Test..."
                                )
                            )
                        ],
                        size="sm",
                    ),
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                children=show_tooltip(self._tooltips,
                                    "help-dut-ver", "DUT Version")
                            ),
                            dbc.Select(
                                id="dd-ctrl-dutver",
                                placeholder=(
                                    "Select a Version of "
                                    "Device under Test..."
                                )
                            )
                        ],
                        size="sm",
                    ),
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                children=show_tooltip(self._tooltips,
                                    "help-infra", "Infra")
                            ),
                            dbc.Select(
                                id="dd-ctrl-phy",
                                placeholder=(
                                    "Select a Physical Test Bed "
                                    "Topology..."
                                )
                            )
                        ],
                        size="sm",
                    ),
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                children=show_tooltip(self._tooltips,
                                    "help-area", "Area")
                            ),
                            dbc.Select(
                                id="dd-ctrl-area",
                                placeholder="Select an Area...",
                                disabled=True,
                            ),
                        ],
                        size="sm",
                    ),
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                children=show_tooltip(self._tooltips,
                                    "help-test", "Test")
                            ),
                            dbc.Select(
                                id="dd-ctrl-test",
                                placeholder="Select a Test...",
                                disabled=True,
                            ),
                        ],
                        size="sm",
                    ),
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.Label(
                        children=show_tooltip(self._tooltips,
                            "help-framesize", "Frame Size"),
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                id="cl-ctrl-framesize-all",
                                options=C.CL_ALL_DISABLED,
                                inline=True,
                                switch=False
                            ),
                        ],
                        width=3
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                id="cl-ctrl-framesize",
                                inline=True,
                                switch=False
                            )
                        ]
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.Label(
                        children=show_tooltip(self._tooltips,
                            "help-cores", "Number of Cores"),
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                id="cl-ctrl-core-all",
                                options=C.CL_ALL_DISABLED,
                                inline=False,
                                switch=False
                            )
                        ],
                        width=3
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                id="cl-ctrl-core",
                                inline=True,
                                switch=False
                            )
                        ]
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.Label(
                        children=show_tooltip(self._tooltips,
                            "help-ttype", "Test Type"),
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                id="cl-ctrl-testtype-all",
                                options=C.CL_ALL_DISABLED,
                                inline=True,
                                switch=False
                            ),
                        ],
                        width=3
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                id="cl-ctrl-testtype",
                                inline=True,
                                switch=False
                            )
                        ]
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.Label(
                        children=show_tooltip(self._tooltips,
                            "help-normalize", "Normalize"),
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                id="cl-ctrl-normalize",
                                options=[{
                                    "value": "normalize",
                                    "label": (
                                        "Normalize results to CPU "
                                        "frequency 2GHz"
                                    )
                                }],
                                value=[],
                                inline=True,
                                switch=False
                            ),
                        ]
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.ButtonGroup(
                        [
                            dbc.Button(
                                id="btn-ctrl-add",
                                children="Add Selected",
                                color="info"
                            )
                        ]
                    )
                ]
            ),
            dbc.Row(
                id="row-card-sel-tests",
                class_name="g-0 p-1",
                style=C.STYLE_DISABLED,
                children=[
                    dbc.Label("Selected tests"),
                    dbc.Checklist(
                        class_name="overflow-auto",
                        id="cl-selected",
                        options=[],
                        inline=False,
                        style={"max-height": "20em"},
                    )
                ],
            ),
            dbc.Row(
                id="row-btns-sel-tests",
                class_name="g-0 p-1",
                style=C.STYLE_DISABLED,
                children=[
                    dbc.ButtonGroup(
                        children=[
                            dbc.Button(
                                id="btn-sel-remove",
                                children="Remove Selected",
                                class_name="w-100",
                                color="info",
                                disabled=False
                            ),
                            dbc.Button(
                                id="btn-sel-remove-all",
                                children="Remove All",
                                class_name="w-100",
                                color="info",
                                disabled=False
                            ),
                        ]
                    )
                ]
            ),
        ]

    class ControlPanel:
        """A class representing the control panel.
        """

        def __init__(self, panel: dict) -> None:
            """Initialisation of the control pannel by default values. If
            particular values are provided (parameter "panel") they are set
            afterwards.

            :param panel: Custom values to be set to the control panel.
            :param default: Default values to be set to the control panel.
            :type panel: dict
            :type defaults: dict
            """

            # Defines also the order of keys
            self._defaults = {
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
                "cl-normalize-val": list(),
                "cl-selected-opt": list()
            }

            self._panel = deepcopy(self._defaults)
            if panel:
                for key in self._defaults:
                    self._panel[key] = panel[key]

        @property
        def defaults(self) -> dict:
            return self._defaults

        @property
        def panel(self) -> dict:
            return self._panel

        def set(self, kwargs: dict) -> None:
            """Set the values of the Control panel.

            :param kwargs: key - value pairs to be set.
            :type kwargs: dict
            :raises KeyError: If the key in kwargs is not present in the Control
                panel.
            """
            for key, val in kwargs.items():
                if key in self._panel:
                    self._panel[key] = val
                else:
                    raise KeyError(f"The key {key} is not defined.")

        def get(self, key: str) -> any:
            """Returns the value of a key from the Control panel.

            :param key: The key which value should be returned.
            :type key: str
            :returns: The value of the key.
            :rtype: any
            :raises KeyError: If the key in kwargs is not present in the Control
                panel.
            """
            return self._panel[key]

        def values(self) -> tuple:
            """Returns the values from the Control panel as a list.

            :returns: The values from the Control panel.
            :rtype: list
            """
            return tuple(self._panel.values())

    def callbacks(self, app):
        """Callbacks for the whole application.

        :param app: The application.
        :type app: Flask
        """

        def _generate_plotting_area(figs: tuple, table: pd.DataFrame,
                url: str) -> tuple:
            """Generate the plotting area with all its content.

            :param figs: Figures to be placed in the plotting area.
            :param table: A table to be placed in the plotting area bellow the
                figures.
            :param utl: The URL to be placed in the plotting area bellow the
                tables.
            :type figs: tuple of plotly.graph_objects.Figure
            :type table: pandas.DataFrame
            :type url: str
            :returns: tuple of elements to be shown in the plotting area.
            :rtype: tuple
                (dcc.Graph, dcc.Graph, dbc.Table, list(dbc.Col, dbc.Col))
            """

            (fig_tput, fig_lat) = figs

            row_fig_tput = C.PLACEHOLDER
            row_fig_lat = C.PLACEHOLDER
            row_table = C.PLACEHOLDER
            row_btn_dwnld = C.PLACEHOLDER

            if fig_tput:
                row_fig_tput = [
                    dcc.Graph(
                        id={"type": "graph", "index": "tput"},
                        figure=fig_tput
                    )
                ]
                row_btn_dwnld = [
                    dbc.Col(  # Download
                        width=2,
                        children=[
                            dcc.Loading(children=[
                                dbc.Button(
                                    id="btn-download-data",
                                    children=show_tooltip(self._tooltips,
                                        "help-download", "Download Data"),
                                    class_name="me-1",
                                    color="info"
                                ),
                                dcc.Download(id="download-data")
                            ]),
                        ]
                    ),
                    dbc.Col(  # Show URL
                        width=10,
                        children=[
                            dbc.InputGroup(
                                class_name="me-1",
                                children=[
                                    dbc.InputGroupText(
                                        style=C.URL_STYLE,
                                        children=show_tooltip(self._tooltips,
                                            "help-url", "URL", "input-url")
                                    ),
                                    dbc.Input(
                                        id="input-url",
                                        readonly=True,
                                        type="url",
                                        style=C.URL_STYLE,
                                        value=url
                                    )
                                ]
                            )
                        ]
                    )
                ]
            if fig_lat:
                row_fig_lat = [
                    dcc.Graph(
                        id={"type": "graph", "index": "lat"},
                        figure=fig_lat
                    )
                ]
            if not table.empty:
                row_table = [
                    dbc.Table.from_dataframe(
                        table,
                        id={"type": "table", "index": "compare"},
                        striped=True,
                        bordered=True,
                        hover=True
                    )
                ]

            return row_fig_tput, row_fig_lat, row_table, row_btn_dwnld

        @app.callback(
            Output("control-panel", "data"),  # Store
            Output("selected-tests", "data"),  # Store
            Output("row-graph-tput", "children"),
            Output("row-graph-lat", "children"),
            Output("row-table", "children"),
            Output("row-btn-download", "children"),
            Output("row-card-sel-tests", "style"),
            Output("row-btns-sel-tests", "style"),
            Output("dd-ctrl-rls", "value"),
            Output("dd-ctrl-dut", "options"),
            Output("dd-ctrl-dut", "disabled"),
            Output("dd-ctrl-dut", "value"),
            Output("dd-ctrl-dutver", "options"),
            Output("dd-ctrl-dutver", "disabled"),
            Output("dd-ctrl-dutver", "value"),
            Output("dd-ctrl-phy", "options"),
            Output("dd-ctrl-phy", "disabled"),
            Output("dd-ctrl-phy", "value"),
            Output("dd-ctrl-area", "options"),
            Output("dd-ctrl-area", "disabled"),
            Output("dd-ctrl-area", "value"),
            Output("dd-ctrl-test", "options"),
            Output("dd-ctrl-test", "disabled"),
            Output("dd-ctrl-test", "value"),
            Output("cl-ctrl-core", "options"),
            Output("cl-ctrl-core", "value"),
            Output("cl-ctrl-core-all", "value"),
            Output("cl-ctrl-core-all", "options"),
            Output("cl-ctrl-framesize", "options"),
            Output("cl-ctrl-framesize", "value"),
            Output("cl-ctrl-framesize-all", "value"),
            Output("cl-ctrl-framesize-all", "options"),
            Output("cl-ctrl-testtype", "options"),
            Output("cl-ctrl-testtype", "value"),
            Output("cl-ctrl-testtype-all", "value"),
            Output("cl-ctrl-testtype-all", "options"),
            Output("btn-ctrl-add", "disabled"),
            Output("cl-ctrl-normalize", "value"),
            Output("cl-selected", "options"),  # User selection
            State("control-panel", "data"),  # Store
            State("selected-tests", "data"),  # Store
            State("cl-selected", "value"),  # User selection
            Input("dd-ctrl-rls", "value"),
            Input("dd-ctrl-dut", "value"),
            Input("dd-ctrl-dutver", "value"),
            Input("dd-ctrl-phy", "value"),
            Input("dd-ctrl-area", "value"),
            Input("dd-ctrl-test", "value"),
            Input("cl-ctrl-core", "value"),
            Input("cl-ctrl-core-all", "value"),
            Input("cl-ctrl-framesize", "value"),
            Input("cl-ctrl-framesize-all", "value"),
            Input("cl-ctrl-testtype", "value"),
            Input("cl-ctrl-testtype-all", "value"),
            Input("cl-ctrl-normalize", "value"),
            Input("btn-ctrl-add", "n_clicks"),
            Input("btn-sel-remove", "n_clicks"),
            Input("btn-sel-remove-all", "n_clicks"),
            Input("url", "href")
        )
        def _update_ctrl_panel(cp_data: dict, store_sel: list, list_sel: list,
            dd_rls: str, dd_dut: str, dd_dutver: str, dd_phy: str, dd_area: str,
            dd_test: str, cl_core: list, cl_core_all: list, cl_framesize: list,
            cl_framesize_all: list, cl_testtype: list, cl_testtype_all: list,
            cl_normalize: list, btn_add: int, btn_remove: int,
            btn_remove_all: int, href: str) -> tuple:
            """Update the application when the event is detected.

            :param cp_data: Current status of the control panel stored in
                browser.
            :param store_sel: List of tests selected by user stored in the
                browser.
            :param list_sel: List of tests selected by the user shown in the
                checklist.
            :param dd_rls: Input - Releases.
            :param dd_dut: Input - DUTs.
            :param dd_dutver: Input - Version of DUT.
            :param dd_phy: Input - topo- arch-nic-driver.
            :param dd_area: Input - Tested area.
            :param dd_test: Input - Test.
            :param cl_core: Input - Number of cores.
            :param cl_core_all: Input - All numbers of cores.
            :param cl_framesize: Input - Frame sizes.
            :param cl_framesize_all: Input - All frame sizes.
            :param cl_testtype: Input - Test type (NDR, PDR, MRR).
            :param cl_testtype_all: Input - All test types.
            :param cl_normalize: Input - Normalize the results.
            :param btn_add: Input - Button "Add Selected" tests.
            :param btn_remove: Input - Button "Remove selected" tests.
            :param btn_remove_all: Input - Button "Remove All" tests.
            :param href: Input - The URL provided by the browser.
            :type cp_data: dict
            :type store_sel: list
            :type list_sel: list
            :type dd_rls: str
            :type dd_dut: str
            :type dd_dutver: str
            :type dd_phy: str
            :type dd_area: str
            :type dd_test: str
            :type cl_core: list
            :type cl_core_all: list
            :type cl_framesize: list
            :type cl_framesize_all: list
            :type cl_testtype: list
            :type cl_testtype_all: list
            :type cl_normalize: list
            :type btn_add: int
            :type btn_remove: int
            :type btn_remove_all: int
            :type href: str
            :returns: New values for web page elements.
            :rtype: tuple
            """

            ctrl_panel = self.ControlPanel(cp_data)
            norm = cl_normalize

            # Parse the url:
            parsed_url = url_decode(href)
            if parsed_url:
                url_params = parsed_url["params"]
            else:
                url_params = None

            row_fig_tput = no_update
            row_fig_lat = no_update
            row_table = no_update
            row_btn_dwnld = no_update
            row_card_sel_tests = no_update
            row_btns_sel_tests = no_update

            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

            if trigger_id == "dd-ctrl-rls":
                try:
                    options = generate_options(self.spec_tbs[dd_rls].keys())
                    disabled = False
                except KeyError:
                    options = list()
                    disabled = True
                ctrl_panel.set({
                    "dd-rls-val": dd_rls,
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
                    "cl-tsttype-all-opt": C.CL_ALL_DISABLED
                })
            elif trigger_id == "dd-ctrl-dut":
                try:
                    rls = ctrl_panel.get("dd-rls-val")
                    dut = self.spec_tbs[rls][dd_dut]
                    options = generate_options(dut.keys())
                    disabled = False
                except KeyError:
                    options = list()
                    disabled = True
                ctrl_panel.set({
                    "dd-dut-val": dd_dut,
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
                    "cl-tsttype-all-opt": C.CL_ALL_DISABLED
                })
            elif trigger_id == "dd-ctrl-dutver":
                try:
                    rls = ctrl_panel.get("dd-rls-val")
                    dut = ctrl_panel.get("dd-dut-val")
                    dutver = self.spec_tbs[rls][dut][dd_dutver]
                    options = generate_options(dutver.keys())
                    disabled = False
                except KeyError:
                    options = list()
                    disabled = True
                ctrl_panel.set({
                    "dd-dutver-val": dd_dutver,
                    "dd-phy-val": str(),
                    "dd-phy-opt": options,
                    "dd-phy-dis": disabled,
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
                    "cl-tsttype-all-opt": C.CL_ALL_DISABLED
                })
            elif trigger_id == "dd-ctrl-phy":
                try:
                    rls = ctrl_panel.get("dd-rls-val")
                    dut = ctrl_panel.get("dd-dut-val")
                    dutver = ctrl_panel.get("dd-dutver-val")
                    phy = self.spec_tbs[rls][dut][dutver][dd_phy]
                    options = [{"label": label(v), "value": v} \
                        for v in sorted(phy.keys())]
                    disabled = False
                except KeyError:
                    options = list()
                    disabled = True
                ctrl_panel.set({
                    "dd-phy-val": dd_phy,
                    "dd-area-val": str(),
                    "dd-area-opt": options,
                    "dd-area-dis": disabled,
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
                    "cl-tsttype-all-opt": C.CL_ALL_DISABLED
                })
            elif trigger_id == "dd-ctrl-area":
                try:
                    rls = ctrl_panel.get("dd-rls-val")
                    dut = ctrl_panel.get("dd-dut-val")
                    dutver = ctrl_panel.get("dd-dutver-val")
                    phy = ctrl_panel.get("dd-phy-val")
                    area = self.spec_tbs[rls][dut][dutver][phy][dd_area]
                    options = generate_options(area.keys())
                    disabled = False
                except KeyError:
                    options = list()
                    disabled = True
                ctrl_panel.set({
                    "dd-area-val": dd_area,
                    "dd-test-val": str(),
                    "dd-test-opt": options,
                    "dd-test-dis": disabled,
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
                    "cl-tsttype-all-opt": C.CL_ALL_DISABLED
                })
            elif trigger_id == "dd-ctrl-test":
                rls = ctrl_panel.get("dd-rls-val")
                dut = ctrl_panel.get("dd-dut-val")
                dutver = ctrl_panel.get("dd-dutver-val")
                phy = ctrl_panel.get("dd-phy-val")
                area = ctrl_panel.get("dd-area-val")
                if all((rls, dut, dutver, phy, area, dd_test, )):
                    test = self.spec_tbs[rls][dut][dutver][phy][area][dd_test]
                    ctrl_panel.set({
                        "dd-test-val": dd_test,
                        "cl-core-opt": generate_options(test["core"]),
                        "cl-core-val": list(),
                        "cl-core-all-val": list(),
                        "cl-core-all-opt": C.CL_ALL_ENABLED,
                        "cl-frmsize-opt": \
                            generate_options(test["frame-size"]),
                        "cl-frmsize-val": list(),
                        "cl-frmsize-all-val": list(),
                        "cl-frmsize-all-opt": C.CL_ALL_ENABLED,
                        "cl-tsttype-opt": \
                            generate_options(test["test-type"]),
                        "cl-tsttype-val": list(),
                        "cl-tsttype-all-val": list(),
                        "cl-tsttype-all-opt": C.CL_ALL_ENABLED,
                    })
            elif trigger_id == "cl-ctrl-core":
                val_sel, val_all = sync_checklists(
                    options=ctrl_panel.get("cl-core-opt"),
                    sel=cl_core,
                    all=list(),
                    id=""
                )
                ctrl_panel.set({
                    "cl-core-val": val_sel,
                    "cl-core-all-val": val_all,
                })
            elif trigger_id == "cl-ctrl-core-all":
                val_sel, val_all = sync_checklists(
                    options = ctrl_panel.get("cl-core-opt"),
                    sel=list(),
                    all=cl_core_all,
                    id="all"
                )
                ctrl_panel.set({
                    "cl-core-val": val_sel,
                    "cl-core-all-val": val_all,
                })
            elif trigger_id == "cl-ctrl-framesize":
                val_sel, val_all = sync_checklists(
                    options = ctrl_panel.get("cl-frmsize-opt"),
                    sel=cl_framesize,
                    all=list(),
                    id=""
                )
                ctrl_panel.set({
                    "cl-frmsize-val": val_sel,
                    "cl-frmsize-all-val": val_all,
                })
            elif trigger_id == "cl-ctrl-framesize-all":
                val_sel, val_all = sync_checklists(
                    options = ctrl_panel.get("cl-frmsize-opt"),
                    sel=list(),
                    all=cl_framesize_all,
                    id="all"
                )
                ctrl_panel.set({
                    "cl-frmsize-val": val_sel,
                    "cl-frmsize-all-val": val_all,
                })
            elif trigger_id == "cl-ctrl-testtype":
                val_sel, val_all = sync_checklists(
                    options = ctrl_panel.get("cl-tsttype-opt"),
                    sel=cl_testtype,
                    all=list(),
                    id=""
                )
                ctrl_panel.set({
                    "cl-tsttype-val": val_sel,
                    "cl-tsttype-all-val": val_all,
                })
            elif trigger_id == "cl-ctrl-testtype-all":
                val_sel, val_all = sync_checklists(
                    options = ctrl_panel.get("cl-tsttype-opt"),
                    sel=list(),
                    all=cl_testtype_all,
                    id="all"
                )
                ctrl_panel.set({
                    "cl-tsttype-val": val_sel,
                    "cl-tsttype-all-val": val_all,
                })
            elif trigger_id == "btn-ctrl-add":
                _ = btn_add
                rls = ctrl_panel.get("dd-rls-val")
                dut = ctrl_panel.get("dd-dut-val")
                dutver = ctrl_panel.get("dd-dutver-val")
                phy = ctrl_panel.get("dd-phy-val")
                area = ctrl_panel.get("dd-area-val")
                test = ctrl_panel.get("dd-test-val")
                cores = ctrl_panel.get("cl-core-val")
                framesizes = ctrl_panel.get("cl-frmsize-val")
                testtypes = ctrl_panel.get("cl-tsttype-val")
                # Add selected test to the list of tests in store:
                if all((rls, dut, dutver, phy, area, test, cores, framesizes,
                        testtypes)):
                    if store_sel is None:
                        store_sel = list()
                    for core in cores:
                        for framesize in framesizes:
                            for ttype in testtypes:
                                if dut == "trex":
                                    core = str()
                                tid = "-".join((rls, dut, dutver,
                                    phy.replace('af_xdp', 'af-xdp'), area,
                                    framesize.lower(), core.lower(), test,
                                    ttype.lower()))
                                if tid not in [itm["id"] for itm in store_sel]:
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
                    row_card_sel_tests = C.STYLE_ENABLED
                    row_btns_sel_tests = C.STYLE_ENABLED
                    if C.CLEAR_ALL_INPUTS:
                        ctrl_panel.set(ctrl_panel.defaults)
                    ctrl_panel.set({
                        "cl-selected-opt": list_tests(store_sel)
                    })
            elif trigger_id == "btn-sel-remove-all":
                _ = btn_remove_all
                row_fig_tput = C.PLACEHOLDER
                row_fig_lat = C.PLACEHOLDER
                row_table = C.PLACEHOLDER
                row_btn_dwnld = C.PLACEHOLDER
                row_card_sel_tests = C.STYLE_DISABLED
                row_btns_sel_tests = C.STYLE_DISABLED
                store_sel = list()
                ctrl_panel.set({"cl-selected-opt": list()})
            elif trigger_id == "btn-sel-remove":
                _ = btn_remove
                if list_sel:
                    new_store_sel = list()
                    for item in store_sel:
                        if item["id"] not in list_sel:
                            new_store_sel.append(item)
                    store_sel = new_store_sel
            elif trigger_id == "url":
                if url_params:
                    try:
                        store_sel = literal_eval(url_params["store_sel"][0])
                        norm = literal_eval(url_params["norm"][0])
                    except (KeyError, IndexError):
                        pass
                    if store_sel:
                        row_card_sel_tests = C.STYLE_ENABLED
                        row_btns_sel_tests = C.STYLE_ENABLED
                        last_test = store_sel[-1]
                        test = self.spec_tbs[last_test["rls"]]\
                            [last_test["dut"]][last_test["dutver"]]\
                                [last_test["phy"]][last_test["area"]]\
                                    [last_test["test"]]
                        ctrl_panel.set({
                            "dd-rls-val": last_test["rls"],
                            "dd-dut-val": last_test["dut"],
                            "dd-dut-opt": generate_options(
                                self.spec_tbs[last_test["rls"]].keys()),
                            "dd-dut-dis": False,
                            "dd-dutver-val": last_test["dutver"],
                            "dd-dutver-opt": generate_options(
                                self.spec_tbs[last_test["rls"]]\
                                    [last_test["dut"]].keys()),
                            "dd-dutver-dis": False,
                            "dd-phy-val": last_test["phy"],
                            "dd-phy-opt": generate_options(
                                self.spec_tbs[last_test["rls"]]\
                                    [last_test["dut"]]\
                                        [last_test["dutver"]].keys()),
                            "dd-phy-dis": False,
                            "dd-area-val": last_test["area"],
                            "dd-area-opt": [
                                {"label": label(v), "value": v} for v in \
                                    sorted(self.spec_tbs[last_test["rls"]]\
                                        [last_test["dut"]][last_test["dutver"]]\
                                            [last_test["phy"]].keys())
                            ],
                            "dd-area-dis": False,
                            "dd-test-val": last_test["test"],
                            "dd-test-opt": generate_options(
                                self.spec_tbs[last_test["rls"]]\
                                    [last_test["dut"]][last_test["dutver"]]\
                                        [last_test["phy"]]\
                                            [last_test["area"]].keys()),
                            "dd-test-dis": False,
                            "cl-core-opt": generate_options(test["core"]),
                            "cl-core-val": [last_test["core"].upper(), ],
                            "cl-core-all-val": list(),
                            "cl-core-all-opt": C.CL_ALL_ENABLED,
                            "cl-frmsize-opt": generate_options(
                                test["frame-size"]),
                            "cl-frmsize-val": \
                                [last_test["framesize"].upper(), ],
                            "cl-frmsize-all-val": list(),
                            "cl-frmsize-all-opt": C.CL_ALL_ENABLED,
                            "cl-tsttype-opt": generate_options(
                                test["test-type"]),
                            "cl-tsttype-val": \
                                [last_test["testtype"].upper(), ],
                            "cl-tsttype-all-val": list(),
                            "cl-tsttype-all-opt": C.CL_ALL_ENABLED
                        })

            if trigger_id in ("btn-ctrl-add", "url", "btn-sel-remove",
                    "cl-ctrl-normalize"):
                if store_sel:
                    row_fig_tput, row_fig_lat, row_table, row_btn_dwnld = \
                        _generate_plotting_area(
                            graph_iterative(
                                self.data, store_sel, self.layout, bool(norm)
                            ),
                            table_comparison(
                                self.data, store_sel, bool(norm)
                            ),
                            gen_new_url(
                                parsed_url,
                                {"store_sel": store_sel, "norm": norm}
                            )
                        )
                    ctrl_panel.set({
                        "cl-selected-opt": list_tests(store_sel)
                    })
                else:
                    row_fig_tput = C.PLACEHOLDER
                    row_fig_lat = C.PLACEHOLDER
                    row_table = C.PLACEHOLDER
                    row_btn_dwnld = C.PLACEHOLDER
                    row_card_sel_tests = C.STYLE_DISABLED
                    row_btns_sel_tests = C.STYLE_DISABLED
                    store_sel = list()
                    ctrl_panel.set({"cl-selected-opt": list()})

            if ctrl_panel.get("cl-core-val") and \
                    ctrl_panel.get("cl-frmsize-val") and \
                    ctrl_panel.get("cl-tsttype-val"):
                disabled = False
            else:
                disabled = True
            ctrl_panel.set({
                "btn-add-dis": disabled,
                "cl-normalize-val": norm
            })

            ret_val = [
                ctrl_panel.panel, store_sel,
                row_fig_tput, row_fig_lat, row_table, row_btn_dwnld,
                row_card_sel_tests, row_btns_sel_tests
            ]
            ret_val.extend(ctrl_panel.values())
            return ret_val

        @app.callback(
            Output("download-data", "data"),
            State("selected-tests", "data"),
            Input("btn-download-data", "n_clicks"),
            prevent_initial_call=True
        )
        def _download_data(store_sel, n_clicks):
            """Download the data

            :param store_sel: List of tests selected by user stored in the
                browser.
            :param n_clicks: Number of clicks on the button "Download".
            :type store_sel: list
            :type n_clicks: int
            :returns: dict of data frame content (base64 encoded) and meta data
                used by the Download component.
            :rtype: dict
            """

            if not n_clicks:
                raise PreventUpdate

            if not store_sel:
                raise PreventUpdate

            df = pd.DataFrame()
            for itm in store_sel:
                sel_data = select_iterative_data(self.data, itm)
                if sel_data is None:
                    continue
                df = pd.concat([df, sel_data], ignore_index=True)

            return dcc.send_data_frame(df.to_csv, C.REPORT_DOWNLOAD_FILE_NAME)
