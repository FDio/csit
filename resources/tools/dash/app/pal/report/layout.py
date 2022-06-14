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
from yaml import load, FullLoader, YAMLError
from copy import deepcopy
from ast import literal_eval

from ..data.data import Data
from ..data.url_processing import url_decode, url_encode
from .graphs import graph_iterative, table_comparison, get_short_version


class Layout:
    """
    """

    # If True, clear all inputs in control panel when button "ADD SELECTED" is
    # pressed.
    CLEAR_ALL_INPUTS = False

    STYLE_DISABLED = {"display": "none"}
    STYLE_ENABLED = {"display": "inherit"}

    CL_ALL_DISABLED = [{
        "label": "All",
        "value": "all",
        "disabled": True
    }]
    CL_ALL_ENABLED = [{
        "label": "All",
        "value": "all",
        "disabled": False
    }]

    PLACEHOLDER = html.Nobr("")

    DRIVERS = ("avf", "af-xdp", "rdma", "dpdk")

    LABELS = {
        "dpdk": "DPDK",
        "container_memif": "LXC/DRC Container Memif",
        "crypto": "IPSec IPv4 Routing",
        "ip4": "IPv4 Routing",
        "ip6": "IPv6 Routing",
        "ip4_tunnels": "IPv4 Tunnels",
        "l2": "L2 Ethernet Switching",
        "srv6": "SRv6 Routing",
        "vm_vhost": "VMs vhost-user",
        "nfv_density-dcr_memif-chain_ipsec": "CNF Service Chains Routing IPSec",
        "nfv_density-vm_vhost-chain_dot1qip4vxlan":"VNF Service Chains Tunnels",
        "nfv_density-vm_vhost-chain": "VNF Service Chains Routing",
        "nfv_density-dcr_memif-pipeline": "CNF Service Pipelines Routing",
        "nfv_density-dcr_memif-chain": "CNF Service Chains Routing",
    }

    URL_STYLE = {
        "background-color": "#d2ebf5",
        "border-color": "#bce1f1",
        "color": "#135d7c"
    }

    def __init__(self, app: Flask, releases: list, html_layout_file: str,
        graph_layout_file: str, data_spec_file: str, tooltip_file: str) -> None:
        """
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
            for drv in self.DRIVERS:
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

    def label(self, key: str) -> str:
        return self.LABELS.get(key, key)

    def _show_tooltip(self, id: str, title: str,
            clipboard_id: str=None) -> list:
        """
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
                children=self._tooltips.get(id, str()),
                target=id,
                placement="auto"
            )
        ]

    def add_content(self):
        """
        """
        if self.html_layout and self.spec_tbs:
            return html.Div(
                id="div-main",
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
        """
        return dbc.NavbarSimple(
            id="navbarsimple-main",
            children=[
                dbc.NavItem(
                    dbc.NavLink(
                        "Iterative Test Runs",
                        disabled=True,
                        external_link=True,
                        href="#"
                    )
                )
            ],
            brand="Dashboard",
            brand_href="/",
            brand_external_link=True,
            class_name="p-2",
            fluid=True,
        )

    def _add_ctrl_col(self) -> dbc.Col:
        """Add column with controls. It is placed on the left side.
        """
        return dbc.Col(
            id="col-controls",
            children=[
                self._add_ctrl_panel(),
            ],
        )

    def _add_plotting_col(self) -> dbc.Col:
        """Add column with plots and tables. It is placed on the right side.
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
                                        children=[
                                            self.PLACEHOLDER
                                        ]
                                    ),
                                    width=6
                                ),
                                dbc.Col(
                                    dbc.Row(  # Latency
                                        id="row-graph-lat",
                                        class_name="g-0 p-2",
                                        children=[
                                            self.PLACEHOLDER
                                        ]
                                    ),
                                    width=6
                                )
                            ]
                        ),
                        dbc.Row(  # Tables
                            id="row-table",
                            class_name="g-0 p-2",
                            children=[
                                self.PLACEHOLDER
                            ]
                        ),
                        dbc.Row(  # Download
                            id="row-btn-download",
                            class_name="g-0 p-2",
                            children=[
                                self.PLACEHOLDER
                            ]
                        )
                    ]
                )
            ],
            width=9
        )

    def _add_ctrl_panel(self) -> dbc.Row:
        """
        """
        return dbc.Row(
            id="row-ctrl-panel",
            class_name="g-0 p-2",
            children=[
                dbc.Row(
                    class_name="g-0",
                    children=[
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText(
                                    children=self._show_tooltip(
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
                            class_name="mb-3",
                            size="sm",
                        ),
                    ]
                ),
                dbc.Row(
                    class_name="g-0",
                    children=[
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText(
                                    children=self._show_tooltip(
                                        "help-dut", "DUT")
                                ),
                                dbc.Select(
                                    id="dd-ctrl-dut",
                                    placeholder=(
                                        "Select a Device under Test..."
                                    )
                                )
                            ],
                            class_name="mb-3",
                            size="sm",
                        ),
                    ]
                ),
                dbc.Row(
                    class_name="g-0",
                    children=[
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText(
                                    children=self._show_tooltip(
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
                            class_name="mb-3",
                            size="sm",
                        ),
                    ]
                ),
                dbc.Row(
                    class_name="g-0",
                    children=[
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText(
                                    children=self._show_tooltip(
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
                            class_name="mb-3",
                            size="sm",
                        ),
                    ]
                ),
                dbc.Row(
                    class_name="g-0",
                    children=[
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText(
                                    children=self._show_tooltip(
                                        "help-area", "Area")
                                ),
                                dbc.Select(
                                    id="dd-ctrl-area",
                                    placeholder="Select an Area...",
                                    disabled=True,
                                ),
                            ],
                            class_name="mb-3",
                            size="sm",
                        ),
                    ]
                ),
                dbc.Row(
                    class_name="g-0",
                    children=[
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText(
                                    children=self._show_tooltip(
                                        "help-test", "Test")
                                ),
                                dbc.Select(
                                    id="dd-ctrl-test",
                                    placeholder="Select a Test...",
                                    disabled=True,
                                ),
                            ],
                            class_name="mb-3",
                            size="sm",
                        ),
                    ]
                ),
                dbc.Row(
                    id="row-ctrl-framesize",
                    class_name="gy-1",
                    children=[
                        dbc.Label(
                            children=self._show_tooltip(
                                "help-framesize", "Frame Size"),
                            class_name="p-0"
                        ),
                        dbc.Col(
                            children=[
                                dbc.Checklist(
                                    id="cl-ctrl-framesize-all",
                                    options=self.CL_ALL_DISABLED,
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
                    id="row-ctrl-core",
                    class_name="gy-1",
                    children=[
                        dbc.Label(
                            children=self._show_tooltip(
                                "help-cores", "Number of Cores"),
                            class_name="p-0"
                        ),
                        dbc.Col(
                            children=[
                                dbc.Checklist(
                                    id="cl-ctrl-core-all",
                                    options=self.CL_ALL_DISABLED,
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
                    id="row-ctrl-testtype",
                    class_name="gy-1",
                    children=[
                        dbc.Label(
                            children=self._show_tooltip(
                                "help-ttype", "Test Type"),
                            class_name="p-0"
                        ),
                        dbc.Col(
                            children=[
                                dbc.Checklist(
                                    id="cl-ctrl-testtype-all",
                                    options=self.CL_ALL_DISABLED,
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
                    class_name="gy-1 p-0",
                    children=[
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    id="btn-ctrl-add",
                                    children="Add Selected",
                                    class_name="me-1",
                                    color="info"
                                )
                            ],
                            size="md",
                        )
                    ]
                ),
                dbc.Row(
                    id="row-card-sel-tests",
                    class_name="gy-1",
                    style=self.STYLE_DISABLED,
                    children=[
                        dbc.Label(
                            "Selected tests",
                            class_name="p-0"
                        ),
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
                    style=self.STYLE_DISABLED,
                    children=[
                        dbc.ButtonGroup(
                            class_name="gy-2",
                            children=[
                                dbc.Button(
                                    id="btn-sel-remove",
                                    children="Remove Selected",
                                    class_name="w-100 me-1",
                                    color="info",
                                    disabled=False
                                ),
                                dbc.Button(
                                    id="btn-sel-remove-all",
                                    children="Remove All",
                                    class_name="w-100 me-1",
                                    color="info",
                                    disabled=False
                                ),
                            ],
                            size="md",
                        )
                    ]
                ),
            ]
        )

    class ControlPanel:
        def __init__(self, panel: dict) -> None:

            CL_ALL_DISABLED = [{
                "label": "All",
                "value": "all",
                "disabled": True
            }]

            # Defines also the order of keys
            self._defaults = {
                "dd-rls-value": str(),
                "dd-dut-options": list(),
                "dd-dut-disabled": True,
                "dd-dut-value": str(),
                "dd-dutver-options": list(),
                "dd-dutver-disabled": True,
                "dd-dutver-value": str(),
                "dd-phy-options": list(),
                "dd-phy-disabled": True,
                "dd-phy-value": str(),
                "dd-area-options": list(),
                "dd-area-disabled": True,
                "dd-area-value": str(),
                "dd-test-options": list(),
                "dd-test-disabled": True,
                "dd-test-value": str(),
                "cl-core-options": list(),
                "cl-core-value": list(),
                "cl-core-all-value": list(),
                "cl-core-all-options": CL_ALL_DISABLED,
                "cl-framesize-options": list(),
                "cl-framesize-value": list(),
                "cl-framesize-all-value": list(),
                "cl-framesize-all-options": CL_ALL_DISABLED,
                "cl-testtype-options": list(),
                "cl-testtype-value": list(),
                "cl-testtype-all-value": list(),
                "cl-testtype-all-options": CL_ALL_DISABLED,
                "btn-add-disabled": True,
                "cl-selected-options": list()
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
            for key, val in kwargs.items():
                if key in self._panel:
                    self._panel[key] = val
                else:
                    raise KeyError(f"The key {key} is not defined.")

        def get(self, key: str) -> any:
            return self._panel[key]

        def values(self) -> tuple:
            return tuple(self._panel.values())

    @staticmethod
    def _sync_checklists(opt: list, sel: list, all: list, id: str) -> tuple:
        """
        """
        options = {v["value"] for v in opt}
        if id =="all":
            sel = list(options) if all else list()
        else:
            all = ["all", ] if set(sel) == options else list()
        return sel, all

    @staticmethod
    def _list_tests(selection: dict) -> list:
        """Display selected tests with checkboxes
        """
        if selection:
            return [{"label": v["id"], "value": v["id"]} for v in selection]
        else:
            return list()

    def callbacks(self, app):

        def _generate_plotting_area(figs: tuple, table: pd.DataFrame,
                url: str) -> tuple:
            """
            """

            (fig_tput, fig_lat) = figs

            row_fig_tput = self.PLACEHOLDER
            row_fig_lat = self.PLACEHOLDER
            row_table = self.PLACEHOLDER
            row_btn_dwnld = self.PLACEHOLDER

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
                                    children=self._show_tooltip(
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
                                        style=self.URL_STYLE,
                                        children=self._show_tooltip(
                                            "help-url", "URL", "input-url")
                                    ),
                                    dbc.Input(
                                        id="input-url",
                                        readonly=True,
                                        type="url",
                                        style=self.URL_STYLE,
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
            Input("btn-ctrl-add", "n_clicks"),
            Input("btn-sel-remove", "n_clicks"),
            Input("btn-sel-remove-all", "n_clicks"),
            Input("url", "href")
        )
        def _update_ctrl_panel(cp_data: dict, store_sel: list, list_sel: list,
            dd_rls: str, dd_dut: str, dd_dutver: str, dd_phy: str, dd_area: str,
            dd_test: str, cl_core: list, cl_core_all: list, cl_framesize: list,
            cl_framesize_all: list, cl_testtype: list, cl_testtype_all: list,
            btn_add: int, btn_remove: int, btn_remove_all: int,
            href: str) -> tuple:
            """
            """

            def _gen_new_url(parsed_url: dict, store_sel: list) -> str:

                if parsed_url:
                    new_url = url_encode({
                        "scheme": parsed_url["scheme"],
                        "netloc": parsed_url["netloc"],
                        "path": parsed_url["path"],
                        "params": {
                            "store_sel": store_sel,
                        }
                    })
                else:
                    new_url = str()
                return new_url


            ctrl_panel = self.ControlPanel(cp_data)

            # Parse the url:
            parsed_url = url_decode(href)

            row_fig_tput = no_update
            row_fig_lat = no_update
            row_table = no_update
            row_btn_dwnld = no_update
            row_card_sel_tests = no_update
            row_btns_sel_tests = no_update

            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

            if trigger_id == "dd-ctrl-rls":
                try:
                    rls = self.spec_tbs[dd_rls]
                    options = sorted(
                        [{"label": v, "value": v} for v in rls.keys()],
                        key=lambda d: d["label"]
                    )
                    disabled = False
                except KeyError:
                    options = list()
                    disabled = True
                ctrl_panel.set({
                    "dd-rls-value": dd_rls,
                    "dd-dut-value": str(),
                    "dd-dut-options": options,
                    "dd-dut-disabled": disabled,
                    "dd-dutver-value": str(),
                    "dd-dutver-options": list(),
                    "dd-dutver-disabled": True,
                    "dd-phy-value": str(),
                    "dd-phy-options": list(),
                    "dd-phy-disabled": True,
                    "dd-area-value": str(),
                    "dd-area-options": list(),
                    "dd-area-disabled": True,
                    "dd-test-value": str(),
                    "dd-test-options": list(),
                    "dd-test-disabled": True,
                    "cl-core-options": list(),
                    "cl-core-value": list(),
                    "cl-core-all-value": list(),
                    "cl-core-all-options": self.CL_ALL_DISABLED,
                    "cl-framesize-options": list(),
                    "cl-framesize-value": list(),
                    "cl-framesize-all-value": list(),
                    "cl-framesize-all-options": self.CL_ALL_DISABLED,
                    "cl-testtype-options": list(),
                    "cl-testtype-value": list(),
                    "cl-testtype-all-value": list(),
                    "cl-testtype-all-options": self.CL_ALL_DISABLED
                })
            elif trigger_id == "dd-ctrl-dut":
                try:
                    rls = ctrl_panel.get("dd-rls-value")
                    dut = self.spec_tbs[rls][dd_dut]
                    options = sorted(
                        [{"label": v, "value": v} for v in dut.keys()],
                        key=lambda d: d["label"]
                    )
                    disabled = False
                except KeyError:
                    options = list()
                    disabled = True
                ctrl_panel.set({
                    "dd-dut-value": dd_dut,
                    "dd-dutver-value": str(),
                    "dd-dutver-options": options,
                    "dd-dutver-disabled": disabled,
                    "dd-phy-value": str(),
                    "dd-phy-options": list(),
                    "dd-phy-disabled": True,
                    "dd-area-value": str(),
                    "dd-area-options": list(),
                    "dd-area-disabled": True,
                    "dd-test-value": str(),
                    "dd-test-options": list(),
                    "dd-test-disabled": True,
                    "cl-core-options": list(),
                    "cl-core-value": list(),
                    "cl-core-all-value": list(),
                    "cl-core-all-options": self.CL_ALL_DISABLED,
                    "cl-framesize-options": list(),
                    "cl-framesize-value": list(),
                    "cl-framesize-all-value": list(),
                    "cl-framesize-all-options": self.CL_ALL_DISABLED,
                    "cl-testtype-options": list(),
                    "cl-testtype-value": list(),
                    "cl-testtype-all-value": list(),
                    "cl-testtype-all-options": self.CL_ALL_DISABLED
                })
            elif trigger_id == "dd-ctrl-dutver":
                try:
                    rls = ctrl_panel.get("dd-rls-value")
                    dut = ctrl_panel.get("dd-dut-value")
                    dutver = self.spec_tbs[rls][dut][dd_dutver]
                    options = sorted(
                        [{"label": v, "value": v} for v in dutver.keys()],
                        key=lambda d: d["label"]
                    )
                    disabled = False
                except KeyError:
                    options = list()
                    disabled = True
                ctrl_panel.set({
                    "dd-dutver-value": dd_dutver,
                    "dd-phy-value": str(),
                    "dd-phy-options": options,
                    "dd-phy-disabled": disabled,
                    "dd-area-value": str(),
                    "dd-area-options": list(),
                    "dd-area-disabled": True,
                    "dd-test-value": str(),
                    "dd-test-options": list(),
                    "dd-test-disabled": True,
                    "cl-core-options": list(),
                    "cl-core-value": list(),
                    "cl-core-all-value": list(),
                    "cl-core-all-options": self.CL_ALL_DISABLED,
                    "cl-framesize-options": list(),
                    "cl-framesize-value": list(),
                    "cl-framesize-all-value": list(),
                    "cl-framesize-all-options": self.CL_ALL_DISABLED,
                    "cl-testtype-options": list(),
                    "cl-testtype-value": list(),
                    "cl-testtype-all-value": list(),
                    "cl-testtype-all-options": self.CL_ALL_DISABLED
                })
            elif trigger_id == "dd-ctrl-phy":
                try:
                    rls = ctrl_panel.get("dd-rls-value")
                    dut = ctrl_panel.get("dd-dut-value")
                    dutver = ctrl_panel.get("dd-dutver-value")
                    phy = self.spec_tbs[rls][dut][dutver][dd_phy]
                    options = sorted(
                        [{"label": self.label(v), "value": v}
                            for v in phy.keys()],
                        key=lambda d: d["label"]
                    )
                    disabled = False
                except KeyError:
                    options = list()
                    disabled = True
                ctrl_panel.set({
                    "dd-phy-value": dd_phy,
                    "dd-area-value": str(),
                    "dd-area-options": options,
                    "dd-area-disabled": disabled,
                    "dd-test-value": str(),
                    "dd-test-options": list(),
                    "dd-test-disabled": True,
                    "cl-core-options": list(),
                    "cl-core-value": list(),
                    "cl-core-all-value": list(),
                    "cl-core-all-options": self.CL_ALL_DISABLED,
                    "cl-framesize-options": list(),
                    "cl-framesize-value": list(),
                    "cl-framesize-all-value": list(),
                    "cl-framesize-all-options": self.CL_ALL_DISABLED,
                    "cl-testtype-options": list(),
                    "cl-testtype-value": list(),
                    "cl-testtype-all-value": list(),
                    "cl-testtype-all-options": self.CL_ALL_DISABLED
                })
            elif trigger_id == "dd-ctrl-area":
                try:
                    rls = ctrl_panel.get("dd-rls-value")
                    dut = ctrl_panel.get("dd-dut-value")
                    dutver = ctrl_panel.get("dd-dutver-value")
                    phy = ctrl_panel.get("dd-phy-value")
                    area = self.spec_tbs[rls][dut][dutver][phy][dd_area]
                    options = sorted(
                        [{"label": v, "value": v} for v in area.keys()],
                        key=lambda d: d["label"]
                    )
                    disabled = False
                except KeyError:
                    options = list()
                    disabled = True
                ctrl_panel.set({
                    "dd-area-value": dd_area,
                    "dd-test-value": str(),
                    "dd-test-options": options,
                    "dd-test-disabled": disabled,
                    "cl-core-options": list(),
                    "cl-core-value": list(),
                    "cl-core-all-value": list(),
                    "cl-core-all-options": self.CL_ALL_DISABLED,
                    "cl-framesize-options": list(),
                    "cl-framesize-value": list(),
                    "cl-framesize-all-value": list(),
                    "cl-framesize-all-options": self.CL_ALL_DISABLED,
                    "cl-testtype-options": list(),
                    "cl-testtype-value": list(),
                    "cl-testtype-all-value": list(),
                    "cl-testtype-all-options": self.CL_ALL_DISABLED
                })
            elif trigger_id == "dd-ctrl-test":
                rls = ctrl_panel.get("dd-rls-value")
                dut = ctrl_panel.get("dd-dut-value")
                dutver = ctrl_panel.get("dd-dutver-value")
                phy = ctrl_panel.get("dd-phy-value")
                area = ctrl_panel.get("dd-area-value")
                test = self.spec_tbs[rls][dut][dutver][phy][area][dd_test]
                if dut and phy and area and dd_test:
                    ctrl_panel.set({
                        "dd-test-value": dd_test,
                        "cl-core-options": [{"label": v, "value": v}
                            for v in sorted(test["core"])],
                        "cl-core-value": list(),
                        "cl-core-all-value": list(),
                        "cl-core-all-options": self.CL_ALL_ENABLED,
                        "cl-framesize-options": [{"label": v, "value": v}
                            for v in sorted(test["frame-size"])],
                        "cl-framesize-value": list(),
                        "cl-framesize-all-value": list(),
                        "cl-framesize-all-options": self.CL_ALL_ENABLED,
                        "cl-testtype-options": [{"label": v, "value": v}
                            for v in sorted(test["test-type"])],
                        "cl-testtype-value": list(),
                        "cl-testtype-all-value": list(),
                        "cl-testtype-all-options": self.CL_ALL_ENABLED,
                    })
            elif trigger_id == "cl-ctrl-core":
                val_sel, val_all = self._sync_checklists(
                    opt=ctrl_panel.get("cl-core-options"),
                    sel=cl_core,
                    all=list(),
                    id=""
                )
                ctrl_panel.set({
                    "cl-core-value": val_sel,
                    "cl-core-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-core-all":
                val_sel, val_all = self._sync_checklists(
                    opt = ctrl_panel.get("cl-core-options"),
                    sel=list(),
                    all=cl_core_all,
                    id="all"
                )
                ctrl_panel.set({
                    "cl-core-value": val_sel,
                    "cl-core-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-framesize":
                val_sel, val_all = self._sync_checklists(
                    opt = ctrl_panel.get("cl-framesize-options"),
                    sel=cl_framesize,
                    all=list(),
                    id=""
                )
                ctrl_panel.set({
                    "cl-framesize-value": val_sel,
                    "cl-framesize-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-framesize-all":
                val_sel, val_all = self._sync_checklists(
                    opt = ctrl_panel.get("cl-framesize-options"),
                    sel=list(),
                    all=cl_framesize_all,
                    id="all"
                )
                ctrl_panel.set({
                    "cl-framesize-value": val_sel,
                    "cl-framesize-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-testtype":
                val_sel, val_all = self._sync_checklists(
                    opt = ctrl_panel.get("cl-testtype-options"),
                    sel=cl_testtype,
                    all=list(),
                    id=""
                )
                ctrl_panel.set({
                    "cl-testtype-value": val_sel,
                    "cl-testtype-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-testtype-all":
                val_sel, val_all = self._sync_checklists(
                    opt = ctrl_panel.get("cl-testtype-options"),
                    sel=list(),
                    all=cl_testtype_all,
                    id="all"
                )
                ctrl_panel.set({
                    "cl-testtype-value": val_sel,
                    "cl-testtype-all-value": val_all,
                })
            elif trigger_id == "btn-ctrl-add":
                _ = btn_add
                rls = ctrl_panel.get("dd-rls-value")
                dut = ctrl_panel.get("dd-dut-value")
                dutver = ctrl_panel.get("dd-dutver-value")
                phy = ctrl_panel.get("dd-phy-value")
                area = ctrl_panel.get("dd-area-value")
                test = ctrl_panel.get("dd-test-value")
                cores = ctrl_panel.get("cl-core-value")
                framesizes = ctrl_panel.get("cl-framesize-value")
                testtypes = ctrl_panel.get("cl-testtype-value")
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
                    row_card_sel_tests = self.STYLE_ENABLED
                    row_btns_sel_tests = self.STYLE_ENABLED
                    if self.CLEAR_ALL_INPUTS:
                        ctrl_panel.set(ctrl_panel.defaults)
                    ctrl_panel.set({
                        "cl-selected-options": self._list_tests(store_sel)
                    })
                    row_fig_tput, row_fig_lat, row_table, row_btn_dwnld = \
                        _generate_plotting_area(
                            graph_iterative(self.data, store_sel, self.layout),
                            table_comparison(self.data, store_sel),
                            _gen_new_url(parsed_url, store_sel)
                        )
            elif trigger_id == "btn-sel-remove-all":
                _ = btn_remove_all
                row_fig_tput = self.PLACEHOLDER
                row_fig_lat = self.PLACEHOLDER
                row_table = self.PLACEHOLDER
                row_btn_dwnld = self.PLACEHOLDER
                row_card_sel_tests = self.STYLE_DISABLED
                row_btns_sel_tests = self.STYLE_DISABLED
                store_sel = list()
                ctrl_panel.set({"cl-selected-options": list()})
            elif trigger_id == "btn-sel-remove":
                _ = btn_remove
                if list_sel:
                    new_store_sel = list()
                    for item in store_sel:
                        if item["id"] not in list_sel:
                            new_store_sel.append(item)
                    store_sel = new_store_sel
                if store_sel:
                    row_fig_tput, row_fig_lat, row_table, row_btn_dwnld = \
                        _generate_plotting_area(
                            graph_iterative(self.data, store_sel, self.layout),
                            table_comparison(self.data, store_sel),
                            _gen_new_url(parsed_url, store_sel)
                        )
                    ctrl_panel.set({
                        "cl-selected-options": self._list_tests(store_sel)
                    })
                else:
                    row_fig_tput = self.PLACEHOLDER
                    row_fig_lat = self.PLACEHOLDER
                    row_table = self.PLACEHOLDER
                    row_btn_dwnld = self.PLACEHOLDER
                    row_card_sel_tests = self.STYLE_DISABLED
                    row_btns_sel_tests = self.STYLE_DISABLED
                    store_sel = list()
                    ctrl_panel.set({"cl-selected-options": list()})
            elif trigger_id == "url":
                # TODO: Add verification
                url_params = parsed_url["params"]
                if url_params:
                    store_sel = literal_eval(
                        url_params.get("store_sel", list())[0])
                    if store_sel:
                        row_fig_tput, row_fig_lat, row_table, row_btn_dwnld = \
                            _generate_plotting_area(
                                graph_iterative(self.data, store_sel,
                                    self.layout),
                                table_comparison(self.data, store_sel),
                                _gen_new_url(parsed_url, store_sel)
                            )
                        row_card_sel_tests = self.STYLE_ENABLED
                        row_btns_sel_tests = self.STYLE_ENABLED
                        ctrl_panel.set({
                            "cl-selected-options": self._list_tests(store_sel)
                        })
                    else:
                        row_fig_tput = self.PLACEHOLDER
                        row_fig_lat = self.PLACEHOLDER
                        row_table = self.PLACEHOLDER
                        row_btn_dwnld = self.PLACEHOLDER
                        row_card_sel_tests = self.STYLE_DISABLED
                        row_btns_sel_tests = self.STYLE_DISABLED
                        store_sel = list()
                        ctrl_panel.set({"cl-selected-options": list()})

            if ctrl_panel.get("cl-core-value") and \
                    ctrl_panel.get("cl-framesize-value") and \
                    ctrl_panel.get("cl-testtype-value"):
                disabled = False
            else:
                disabled = True
            ctrl_panel.set({"btn-add-disabled": disabled})

            ret_val = [
                ctrl_panel.panel, store_sel,
                row_fig_tput, row_fig_lat, row_table, row_btn_dwnld,
                row_card_sel_tests, row_btns_sel_tests
            ]
            ret_val.extend(ctrl_panel.values())
            return ret_val

        # @app.callback(
        #     Output("download-data", "data"),
        #     State("selected-tests", "data"),
        #     Input("btn-download-data", "n_clicks"),
        #     prevent_initial_call=True
        # )
        # def _download_data(store_sel, n_clicks):
        #     """
        #     """

        #     if not n_clicks:
        #         raise PreventUpdate

        #     if not store_sel:
        #         raise PreventUpdate

        #     df = pd.DataFrame()
        #     for itm in store_sel:
        #         sel_data = select_trending_data(self.data, itm)
        #         if sel_data is None:
        #             continue
        #         df = pd.concat([df, sel_data], ignore_index=True)

        #     return dcc.send_data_frame(df.to_csv, "trending_data.csv")
