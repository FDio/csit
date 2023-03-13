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
from ..utils.utils import generate_options, gen_new_url  #, show_tooltip
from .tables import comparison_table


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
    "sort-by-val": str(),
    "sort-order-val": int()
}

# List of comparable parameters.
CMP_PARAMS = {
    "dutver": "Release and Version",
    "infra": "Infrastructure",
    "frmsize": "Frame Size",
    "core": "Number of Cores",
    "ttype": "Test Type"
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
            "job", "test_id", "test_type", "dut_type", "dut_version", "tg_type",
            "release", "passed"
        ]
        for _, row in self._data[cols].drop_duplicates().iterrows():
            lst_job = row["job"].split("-")
            dut = lst_job[1]
            dver = f"{row['release']}-{row['dut_version']}"
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
                    tbs[dut][dver][infra]["ttype"].extend(("NDR", "PDR", ))
            elif row["test_type"] == "hoststack" and \
                    row["tg_type"] in ("iperf", "vpp"):
                if "BPS" not in tbs[dut][dver][infra]["ttype"]:
                    tbs[dut][dver][infra]["ttype"].append("BPS")
            elif row["test_type"] == "hoststack" and row["tg_type"] == "ab":
                if "CPS" not in tbs[dut][dver][infra]["ttype"]:
                    tbs[dut][dver][infra]["ttype"].extend(("CPS", "RPS", ))
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

        reference = [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                "DUT"
                                # children=show_tooltip(
                                #     self._tooltips,
                                #     "help-dut",
                                #     "DUT"
                                # )
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
                                "Release and Version"
                                # children=show_tooltip(
                                #     self._tooltips,
                                #     "help-dut-ver",
                                #     "Release and Version"
                                # )
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
                                "Infra"
                                # children=show_tooltip(
                                #     self._tooltips,
                                #     "help-infra",
                                #     "Infra"
                                # )
                            ),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "infra"},
                                placeholder="Select an Infrastructure..."
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
                                "Frame Size"
                                # children=show_tooltip(
                                #     self._tooltips,
                                #     "help-framesize",
                                #     "Frame Size"
                                # )
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
                                "Number of Cores"
                                # children=show_tooltip(
                                #     self._tooltips,
                                #     "help-cores",
                                #     "Number of Cores"
                                # )
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
                                "Test Type"
                                # children=show_tooltip(
                                #     self._tooltips,
                                #     "help-ttype",
                                #     "Test Type"
                                # )
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
        ]

        compare = [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                "Parameter"
                                # children=show_tooltip(
                                #     self._tooltips,
                                #     "help-cmpprm",
                                #     "Parameter to Compare"
                                # )
                            ),
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
                            dbc.InputGroupText(
                                "Value"
                                # children=show_tooltip(
                                #     self._tooltips,
                                #     "help-cmpval",
                                #     "Value to Compare"
                                # )
                            ),
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

        normalize = [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
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
                        style={"align-items": "center"},
                        size="sm"
                    )
                ]
            )
        ]

        sort = [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Sort by"),
                            dbc.Select(
                                id="sort-by",
                                placeholder="Select..."
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
                        dbc.RadioItems(
                            id="sort-order",
                            options=[
                                {"value": 0, "label": "Descending"},
                                {"value": 1, "label": "Ascending"}
                            ],
                            value=0,
                            inline=True,
                            class_name="ms-2"
                        ),
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
                            html.H5("Normalization")
                        ),
                        dbc.CardBody(
                            children=normalize,
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
                            html.H5("Sort")
                        ),
                        dbc.CardBody(
                            children=sort,
                            class_name="g-0 p-0"
                        )
                    ],
                    color="secondary",
                    outline=True
                ),
                id="row-sort",
                class_name="g-0 p-1",
                style=C.STYLE_DISABLED
            )
        ]

    def _get_plotting_area(
            self,
            selected: dict,
            url: str,
            normalize: bool,
            sort_by: str,
            sort_order: int,
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

        title, df = comparison_table(
            self._data, selected, normalize, sort_by, sort_order
        )

        if df.empty:
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

        row_items = [
            dbc.Col(
                children=dbc.Table.from_dataframe(
                    df,
                    bordered=True,
                    striped=True,
                    hover=True,
                    size="sm",
                    color="info"
                ),
                class_name="g-0 p-1",
            )
        ]

        return [
            dbc.Row(
                children=html.H5(title),
                class_name="g-0 p-1"
            ),
            dbc.Row(
                children=row_items,
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
            ),
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
                Output("row-sort", "style"),
                Output("sort-by", "options"),
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
                Output("sort-by", "value"),
                Output("sort-order", "value")
            ],
            [
                State("store-control-panel", "data"),
                State("store-selected", "data")
            ],
            [
                Input("url", "href"),
                Input("normalize", "value"),
                Input("sort-by", "value"),
                Input("sort-order", "value"),
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
                sort_by: str,
                sort_order: int,
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

            if not sort_by:
                sort_by = "Diff mean"
            if sort_order is None:
                sort_order = 0

            # Parse the url:
            parsed_url = url_decode(href)
            if parsed_url:
                url_params = parsed_url["params"]
            else:
                url_params = None

            on_draw = False
            plotting_area = no_update
            row_sort = no_update
            sort_by_opts = no_update

            trigger = Trigger(callback_context.triggered)
            if trigger.type == "url" and url_params:
                process_url = False
                try:
                    selected = literal_eval(url_params["selected"][0])
                    r_sel = selected["reference"]["selection"]
                    c_sel = selected["compare"]
                    normalize = literal_eval(url_params["norm"][0])
                    sort = literal_eval(url_params["sort"][0])
                    sort_by = sort["by"]
                    sort_order = sort["order"]
                    process_url = bool(
                        (selected["reference"]["set"] == True) and
                        (c_sel["set"] == True)
                    )
                except (KeyError, IndexError):
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
                        "sort-by-val": sort_by,
                        "sort-order-val": sort_order
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
            elif trigger.type == "sort-by":
                ctrl_panel.set({"sort-by-val": sort_by})
                on_draw = True
            elif trigger.type == "sort-order":
                ctrl_panel.set({"sort-order-val": sort_order})
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
                        "dut-val": trigger.value,
                        "dutver-opt": options,
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
                        options = generate_options(dver.keys())
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "dutver-val": trigger.value,
                        "infra-opt": options,
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
                    opts = list()
                    for itm, label in CMP_PARAMS.items():
                        if len(ctrl_panel.get(f"{itm}-opt")) > 1:
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

            if all((on_draw, selected["reference"]["set"],
                    selected["compare"]["set"], )):
                plotting_area = self._get_plotting_area(
                    selected=selected,
                    normalize=bool(normalize),
                    sort_by=sort_by,
                    sort_order=sort_order,
                    url=gen_new_url(
                        parsed_url,
                        params={
                            "selected": selected,
                            "norm": normalize,
                            "sort": {"by": sort_by, "order": sort_order}
                        }
                    )
                )

                row_sort = C.STYLE_ENABLED
                value = selected["reference"]["selection"]\
                    [selected["compare"]["parameter"]]
                r_name = "|".join(value) if isinstance(value, list) else value
                sort_by_opts = [
                    "Test Name",
                    f"{r_name} mean",
                    f"{r_name} stdev",
                    f"{selected['compare']['value']} mean",
                    f"{selected['compare']['value']} stdev",
                    "Diff mean",
                    "Diff stdev"
                ]
            else:
                row_sort = C.STYLE_DISABLED

            ret_val = [
                ctrl_panel.panel,
                selected,
                plotting_area,
                row_sort,
                sort_by_opts
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
            State("store-selected", "data"),
            State("normalize", "value"),
            Input("plot-btn-download", "n_clicks"),
            prevent_initial_call=True
        )
        def _download_trending_data(selected: dict, normalize: list, _: int):
            """Download the data

            :param selected: List of tests selected by user stored in the
                browser.
            :param normalize: If set, the data is normalized to 2GHz CPU
                frequency.
            :type selected: list
            :type normalize: list
            :returns: dict of data frame content (base64 encoded) and meta data
                used by the Download component.
            :rtype: dict
            """

            if not selected:
                raise PreventUpdate

            _, table = comparison_table(
                self._data, selected, normalize, output="csv"
            )

            return dcc.send_data_frame(table.to_csv, C.COMP_DOWNLOAD_FILE_NAME)
