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
from dash import callback_context
from dash import Input, Output, State
from yaml import load, FullLoader, YAMLError
from copy import deepcopy

from ..data.data import Data
from ..utils.constants import Constants as C
from ..utils.utils import classify_anomalies, show_tooltip, gen_new_url, \
    get_ttypes, get_cadences, get_test_beds, get_job, generate_options, \
    set_job_params
from ..utils.url_processing import url_decode
from ..data.data import Data
from .tables import table_news, table_summary


class Layout:
    """The layout of the dash app and the callbacks.
    """

    def __init__(self, app: Flask, html_layout_file: str, data_spec_file: str,
        tooltip_file: str) -> None:
        """Initialization:
        - save the input parameters,
        - read and pre-process the data,
        - prepare data for the control panel,
        - read HTML layout file,
        - read tooltips from the tooltip file.

        :param app: Flask application running the dash application.
        :param html_layout_file: Path and name of the file specifying the HTML
            layout of the dash application.
        :param data_spec_file: Path and name of the file specifying the data to
            be read from parquets for this application.
        :param tooltip_file: Path and name of the yaml file specifying the
            tooltips.
        :type app: Flask
        :type html_layout_file: str
        :type data_spec_file: str
        :type tooltip_file: str
        """

        # Inputs
        self._app = app
        self._html_layout_file = html_layout_file
        self._data_spec_file = data_spec_file
        self._tooltip_file = tooltip_file

        # Read the data:
        data_stats, data_mrr, data_ndrpdr = Data(
            data_spec_file=self._data_spec_file,
            debug=True
        ).read_stats(days=C.NEWS_TIME_PERIOD)

        df_tst_info = pd.concat([data_mrr, data_ndrpdr], ignore_index=True)

        # Prepare information for the control panel:
        self._jobs = sorted(list(df_tst_info["job"].unique()))
        d_job_info = {
            "job": list(),
            "dut": list(),
            "ttype": list(),
            "cadence": list(),
            "tbed": list()
        }
        for job in self._jobs:
            lst_job = job.split("-")
            d_job_info["job"].append(job)
            d_job_info["dut"].append(lst_job[1])
            d_job_info["ttype"].append(lst_job[3])
            d_job_info["cadence"].append(lst_job[4])
            d_job_info["tbed"].append("-".join(lst_job[-2:]))
        self.job_info = pd.DataFrame.from_dict(d_job_info)

        self._default = set_job_params(self.job_info, C.NEWS_DEFAULT_JOB)

        # Pre-process the data:

        def _create_test_name(test: str) -> str:
            lst_tst = test.split(".")
            suite = lst_tst[-2].replace("2n1l-", "").replace("1n1l-", "").\
                replace("2n-", "")
            return f"{suite.split('-')[0]}-{lst_tst[-1]}"

        def _get_rindex(array: list, itm: any) -> int:
            return len(array) - 1 - array[::-1].index(itm)

        tst_info = {
            "job": list(),
            "build": list(),
            "start": list(),
            "dut_type": list(),
            "dut_version": list(),
            "hosts": list(),
            "failed": list(),
            "regressions": list(),
            "progressions": list()
        }
        logging.debug("Processing jobs ...")
        for job in self._jobs:
            logging.debug(f"+ {job}")
            # Create lists of failed tests:
            df_job = df_tst_info.loc[(df_tst_info["job"] == job)]
            last_build = max(df_job["build"].unique())
            df_build = df_job.loc[(df_job["build"] == last_build)]
            tst_info["job"].append(job)
            tst_info["build"].append(last_build)
            tst_info["start"].append(data_stats.loc[
                (data_stats["job"] == job) &
                (data_stats["build"] == last_build)
            ]["start_time"].iloc[-1].strftime('%Y-%m-%d %H:%M'))
            tst_info["dut_type"].append(df_build["dut_type"].iloc[-1])
            tst_info["dut_version"].append(df_build["dut_version"].iloc[-1])
            tst_info["hosts"].append(df_build["hosts"].iloc[-1])
            failed_tests = df_build.loc[(df_build["passed"] == False)]\
                ["test_id"].to_list()
            l_failed = list()
            try:
                for tst in failed_tests:
                    l_failed.append(_create_test_name(tst))
            except KeyError:
                l_failed = list()
            tst_info["failed"].append(sorted(l_failed))

            # Create lists of regressions and progressions:
            l_reg = list()
            l_prog = list()

            tests = df_job["test_id"].unique()
            for test in tests:
                tst_data = df_job.loc[df_job["test_id"] == test].sort_values(
                    by="start_time", ignore_index=True)
                x_axis = tst_data["start_time"].tolist()
                if "-ndrpdr" in test:
                    tst_data = tst_data.dropna(
                        subset=["result_pdr_lower_rate_value", ]
                    )
                    if tst_data.empty:
                        continue
                    try:
                        anomalies, _, _ = classify_anomalies({
                            k: v for k, v in zip(
                                x_axis,
                                tst_data["result_ndr_lower_rate_value"].tolist()
                            )
                        })
                    except ValueError:
                        continue
                    if "progression" in anomalies:
                        l_prog.append((
                            _create_test_name(test).replace("-ndrpdr", "-ndr"),
                            x_axis[_get_rindex(anomalies, "progression")]
                        ))
                    if "regression" in anomalies:
                        l_reg.append((
                            _create_test_name(test).replace("-ndrpdr", "-ndr"),
                            x_axis[_get_rindex(anomalies, "regression")]
                        ))
                    try:
                        anomalies, _, _ = classify_anomalies({
                            k: v for k, v in zip(
                                x_axis,
                                tst_data["result_pdr_lower_rate_value"].tolist()
                            )
                        })
                    except ValueError:
                        continue
                    if "progression" in anomalies:
                        l_prog.append((
                            _create_test_name(test).replace("-ndrpdr", "-pdr"),
                            x_axis[_get_rindex(anomalies, "progression")]
                        ))
                    if "regression" in anomalies:
                        l_reg.append((
                            _create_test_name(test).replace("-ndrpdr", "-pdr"),
                            x_axis[_get_rindex(anomalies, "regression")]
                        ))
                else:  # mrr
                    tst_data = tst_data.dropna(
                        subset=["result_receive_rate_rate_avg", ]
                    )
                    if tst_data.empty:
                        continue
                    try:
                        anomalies, _, _ = classify_anomalies({
                            k: v for k, v in zip(
                                x_axis,
                                tst_data["result_receive_rate_rate_avg"].\
                                    tolist()
                            )
                        })
                    except ValueError:
                        continue
                    if "progression" in anomalies:
                        l_prog.append((
                            _create_test_name(test),
                            x_axis[_get_rindex(anomalies, "progression")]
                        ))
                    if "regression" in anomalies:
                        l_reg.append((
                            _create_test_name(test),
                            x_axis[_get_rindex(anomalies, "regression")]
                        ))

            tst_info["regressions"].append(
                sorted(l_reg, key=lambda k: k[1], reverse=True))
            tst_info["progressions"].append(
                sorted(l_prog, key=lambda k: k[1], reverse=True))

        self._data = pd.DataFrame.from_dict(tst_info)

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

        self._default_tab_failed = \
            table_news(self.data, self._default["job"], C.NEWS_TIME_PERIOD)

        # Callbacks:
        if self._app is not None and hasattr(self, 'callbacks'):
            self.callbacks(self._app)

    @property
    def html_layout(self) -> dict:
        return self._html_layout

    @property
    def data(self) -> pd.DataFrame:
        return self._data

    @property
    def default(self) -> dict:
        return self._default

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

        if self.html_layout:
            return html.Div(
                id="div-main",
                children=[
                    dcc.Store(id="control-panel"),
                    dcc.Location(id="url", refresh=False),
                    dbc.Row(
                        id="row-navbar",
                        class_name="g-0",
                        children=[
                            self._add_navbar(),
                        ]
                    ),
                    dbc.Row(
                        id="row-main",
                        class_name="g-0",
                        children=[
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
                        "Continuous Performance News",
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
        """Add column with control panel. It is placed on the left side.

        :returns: Column with the control panel.
        :rtype: dbc.Col
        """

        return dbc.Col(
            id="col-controls",
            children=[
                self._add_ctrl_panel(),
            ],
        )

    def _add_plotting_col(self) -> dbc.Col:
        """Add column with tables. It is placed on the right side.

        :returns: Column with tables.
        :rtype: dbc.Col
        """

        return dbc.Col(
            id="col-plotting-area",
            children=[
                dbc.Row(  # Failed tests
                    id="row-table-failed",
                    class_name="g-0 p-2",
                    children=self._default_tab_failed
                ),
                dbc.Row(
                    class_name="g-0 p-2",
                    align="center",
                    justify="start",
                    children=[
                        dbc.InputGroup(
                            class_name="me-1",
                            children=[
                                dbc.InputGroupText(
                                    style=C.URL_STYLE,
                                    children=show_tooltip(
                                        self._tooltips,
                                        "help-url", "URL",
                                        "input-url"
                                    )
                                ),
                                dbc.Input(
                                    id="input-url",
                                    readonly=True,
                                    type="url",
                                    style=C.URL_STYLE,
                                    value=""
                                )
                            ]
                        )
                    ]
                )
            ],
            width=9,
        )

    def _add_ctrl_panel(self) -> dbc.Row:
        """Add control panel.

        :returns: Control panel.
        :rtype: dbc.Row
        """
        return dbc.Row(
            id="row-ctrl-panel",
            class_name="g-0",
            children=[
                dbc.Row(
                    class_name="g-0 p-2",
                    children=[
                        dbc.Row(
                            class_name="gy-1",
                            children=[
                                dbc.Label(
                                    class_name="p-0",
                                    children=show_tooltip(self._tooltips,
                                        "help-dut", "Device under Test")
                                ),
                                dbc.Row(
                                    dbc.RadioItems(
                                        id="ri-duts",
                                        inline=True,
                                        value=self.default["dut"],
                                        options=self.default["duts"]
                                    )
                                )
                            ]
                        ),
                        dbc.Row(
                            class_name="gy-1",
                            children=[
                                dbc.Label(
                                    class_name="p-0",
                                    children=show_tooltip(self._tooltips,
                                        "help-ttype", "Test Type"),
                                ),
                                dbc.RadioItems(
                                    id="ri-ttypes",
                                    inline=True,
                                    value=self.default["ttype"],
                                    options=self.default["ttypes"]
                                )
                            ]
                        ),
                        dbc.Row(
                            class_name="gy-1",
                            children=[
                                dbc.Label(
                                    class_name="p-0",
                                    children=show_tooltip(self._tooltips,
                                        "help-cadence", "Cadence"),
                                ),
                                dbc.RadioItems(
                                    id="ri-cadences",
                                    inline=True,
                                    value=self.default["cadence"],
                                    options=self.default["cadences"]
                                )
                            ]
                        ),
                        dbc.Row(
                            class_name="gy-1",
                            children=[
                                dbc.Label(
                                    class_name="p-0",
                                    children=show_tooltip(self._tooltips,
                                        "help-tbed", "Test Bed"),
                                ),
                                dbc.Select(
                                    id="dd-tbeds",
                                    placeholder="Select a test bed...",
                                    value=self.default["tbed"],
                                    options=self.default["tbeds"]
                                )
                            ]
                        ),
                        dbc.Row(
                            class_name="gy-1 p-0",
                            children=[
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button(
                                            id="btn-summary",
                                            children=(
                                                f"Show Summary from the last "
                                                f"{C.NEWS_SUMMARY_PERIOD} Days"
                                            ),
                                            class_name="me-1",
                                            color="info"
                                        )
                                    ],
                                    size="md",
                                )
                            ]
                        ),
                        dbc.Row(
                            class_name="gy-1",
                            children=[
                                dbc.Alert(
                                    id="al-job",
                                    color="info",
                                    children=self.default["job"]
                                )
                            ]
                        )
                    ]
                )
            ]
        )

    class ControlPanel:
        """A class representing the control panel.
        """

        def __init__(self, panel: dict, default: dict) -> None:
            """Initialisation of the control pannel by default values. If
            particular values are provided (parameter "panel") they are set
            afterwards.

            :param panel: Custom values to be set to the control panel.
            :param default: Default values to be set to the control panel.
            :type panel: dict
            :type defaults: dict
            """

            self._defaults = {
                "ri-ttypes-options": default["ttypes"],
                "ri-cadences-options": default["cadences"],
                "dd-tbeds-options": default["tbeds"],
                "ri-duts-value": default["dut"],
                "ri-ttypes-value": default["ttype"],
                "ri-cadences-value": default["cadence"],
                "dd-tbeds-value": default["tbed"],
                "al-job-children": default["job"]
            }
            self._panel = deepcopy(self._defaults)
            if panel:
                for key in self._defaults:
                    self._panel[key] = panel[key]

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

        @property
        def defaults(self) -> dict:
            return self._defaults

        @property
        def panel(self) -> dict:
            return self._panel

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

        def values(self) -> list:
            """Returns the values from the Control panel as a list.

            :returns: The values from the Control panel.
            :rtype: list
            """
            return list(self._panel.values())

    def callbacks(self, app):
        """Callbacks for the whole application.

        :param app: The application.
        :type app: Flask
        """

        @app.callback(
            Output("control-panel", "data"),  # Store
            Output("row-table-failed", "children"),
            Output("input-url", "value"),
            Output("ri-ttypes", "options"),
            Output("ri-cadences", "options"),
            Output("dd-tbeds", "options"),
            Output("ri-duts", "value"),
            Output("ri-ttypes", "value"),
            Output("ri-cadences", "value"),
            Output("dd-tbeds", "value"),
            Output("al-job", "children"),
            State("control-panel", "data"),  # Store
            Input("ri-duts", "value"),
            Input("ri-ttypes", "value"),
            Input("ri-cadences", "value"),
            Input("dd-tbeds", "value"),
            Input("url", "href"),
            Input("btn-summary", "n_clicks")
        )
        def _update_application(cp_data: dict, dut: str, ttype: str,
                cadence:str, tbed: str, href: str, btn_all: int) -> tuple:
            """Update the application when the event is detected.

            :param cp_data: Current status of the control panel stored in
                browser.
            :param dut: Input - DUT name.
            :param ttype: Input - Test type.
            :param cadence: Input - The cadence of the job.
            :param tbed: Input - The test bed.
            :param href: Input - The URL provided by the browser.
            :type cp_data: dict
            :type dut: str
            :type ttype: str
            :type cadence: str
            :type tbed: str
            :type href: str
            :returns: New values for web page elements.
            :rtype: tuple
            """

            ctrl_panel = self.ControlPanel(cp_data, self.default)

            # Parse the url:
            parsed_url = url_decode(href)
            if parsed_url:
                url_params = parsed_url["params"]
            else:
                url_params = None

            show_summary = False

            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]
            if trigger_id == "ri-duts":
                ttype_opts = generate_options(get_ttypes(self.job_info, dut))
                ttype_val = ttype_opts[0]["value"]
                cad_opts = generate_options(
                    get_cadences(self.job_info, dut, ttype_val))
                cad_val = cad_opts[0]["value"]
                tbed_opts = generate_options(get_test_beds(
                    self.job_info, dut, ttype_val, cad_val))
                tbed_val = tbed_opts[0]["value"]
                ctrl_panel.set({
                    "ri-duts-value": dut,
                    "ri-ttypes-options": ttype_opts,
                    "ri-ttypes-value": ttype_val,
                    "ri-cadences-options": cad_opts,
                    "ri-cadences-value": cad_val,
                    "dd-tbeds-options": tbed_opts,
                    "dd-tbeds-value": tbed_val
                })
            elif trigger_id == "ri-ttypes":
                cad_opts = generate_options(get_cadences(
                    self.job_info, ctrl_panel.get("ri-duts-value"), ttype))
                cad_val = cad_opts[0]["value"]
                tbed_opts = generate_options(get_test_beds(
                    self.job_info, ctrl_panel.get("ri-duts-value"),
                    ttype, cad_val))
                tbed_val = tbed_opts[0]["value"]
                ctrl_panel.set({
                    "ri-ttypes-value": ttype,
                    "ri-cadences-options": cad_opts,
                    "ri-cadences-value": cad_val,
                    "dd-tbeds-options": tbed_opts,
                    "dd-tbeds-value": tbed_val
                })
            elif trigger_id == "ri-cadences":
                tbed_opts = generate_options(get_test_beds(
                    self.job_info, ctrl_panel.get("ri-duts-value"),
                    ctrl_panel.get("ri-ttypes-value"), cadence))
                tbed_val = tbed_opts[0]["value"]
                ctrl_panel.set({
                    "ri-cadences-value": cadence,
                    "dd-tbeds-options": tbed_opts,
                    "dd-tbeds-value": tbed_val
                })
            elif trigger_id == "dd-tbeds":
                ctrl_panel.set({
                    "dd-tbeds-value": tbed
                })
            elif trigger_id == "url":
                # TODO: Add verification
                if url_params:
                    new_job = url_params.get("job", list())[0]
                    if new_job and new_job != "all":
                        job_params = set_job_params(self.job_info, new_job)
                        ctrl_panel = self.ControlPanel(None, job_params)
                    if new_job and new_job == "all":
                        show_summary = True
                else:
                    ctrl_panel = self.ControlPanel(cp_data, self.default)
            elif trigger_id == "btn-summary":
                show_summary = True

            if show_summary:
                ctrl_panel.set({
                    "al-job-children": \
                        f"Summary from the last {C.NEWS_SUMMARY_PERIOD} Days"
                })
                job = "all"
                tables = table_summary(self.data, self._jobs)
            else:
                job = get_job(
                    self.job_info,
                    ctrl_panel.get("ri-duts-value"),
                    ctrl_panel.get("ri-ttypes-value"),
                    ctrl_panel.get("ri-cadences-value"),
                    ctrl_panel.get("dd-tbeds-value")
                )
                ctrl_panel.set({"al-job-children": job})
                tables = table_news(self.data, job, C.NEWS_TIME_PERIOD)

            ret_val = [
                ctrl_panel.panel,
                tables,
                gen_new_url(parsed_url, {"job": job})
            ]
            ret_val.extend(ctrl_panel.values())
            return ret_val
