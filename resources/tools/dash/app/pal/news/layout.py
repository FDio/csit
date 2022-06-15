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
from .tables import table_failed


class Layout:
    """The layout of the dash app and the callbacks.
    """

    # The default job displayed when the page is loaded first time.
    DEFAULT_JOB = "csit-vpp-perf-mrr-daily-master-2n-icx"

    def __init__(self, app: Flask, html_layout_file: str, data_spec_file: str,
        tooltip_file: str) -> None:
        """Initialization:
        - save the input parameters,
        - read and pre-process the data,
        - prepare data fro the control panel,
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
        ).read_stats(days=10)  # To be sure

        df_tst_info = pd.concat([data_mrr, data_ndrpdr], ignore_index=True)

        # Prepare information for the control panel:
        jobs = sorted(list(df_tst_info["job"].unique()))
        job_info = {
            "job": list(),
            "dut": list(),
            "ttype": list(),
            "cadence": list(),
            "tbed": list()
        }
        for job in jobs:
            lst_job = job.split("-")
            job_info["job"].append(job)
            job_info["dut"].append(lst_job[1])
            job_info["ttype"].append(lst_job[3])
            job_info["cadence"].append(lst_job[4])
            job_info["tbed"].append("-".join(lst_job[-2:]))
        self.df_job_info = pd.DataFrame.from_dict(job_info)

        self._default = self._set_job_params(self.DEFAULT_JOB)

        # Pre-process the data:
        tst_info = {
            "job": list(),
            "build": list(),
            "start": list(),
            "dut_type": list(),
            "dut_version": list(),
            "hosts": list(),
            "lst_failed": list()
        }
        for job in jobs:
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
                    lst_tst = tst.split(".")
                    suite = lst_tst[-2].replace("2n1l-", "").\
                        replace("1n1l-", "").replace("2n-", "")
                    l_failed.append(f"{suite.split('-')[0]}-{lst_tst[-1]}")
            except KeyError:
                l_failed = list()
            tst_info["lst_failed"].append(sorted(l_failed))

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

        self._default_tab_failed = table_failed(self.data, self._default["job"])

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

    def _get_duts(self) -> list:
        """Get the list of DUTs from the pre-processed information about jobs.

        :returns: Alphabeticaly sorted list of DUTs.
        :rtype: list
        """
        return sorted(list(self.df_job_info["dut"].unique()))

    def _get_ttypes(self, dut: str) -> list:
        """Get the list of test types from the pre-processed information about
        jobs.

        :param dut: The DUT for which the list of test types will be populated.
        :type dut: str
        :returns: Alphabeticaly sorted list of test types.
        :rtype: list
        """
        return sorted(list(self.df_job_info.loc[(
            self.df_job_info["dut"] == dut
        )]["ttype"].unique()))

    def _get_cadences(self, dut: str, ttype: str) -> list:
        """Get the list of cadences from the pre-processed information about
        jobs.

        :param dut: The DUT for which the list of cadences will be populated.
        :param ttype: The test type for which the list of cadences will be
            populated.
        :type dut: str
        :type ttype: str
        :returns: Alphabeticaly sorted list of cadences.
        :rtype: list
        """
        return sorted(list(self.df_job_info.loc[(
            (self.df_job_info["dut"] == dut) &
            (self.df_job_info["ttype"] == ttype)
        )]["cadence"].unique()))

    def _get_test_beds(self, dut: str, ttype: str, cadence: str) -> list:
        """Get the list of test beds from the pre-processed information about
        jobs.

        :param dut: The DUT for which the list of test beds will be populated.
        :param ttype: The test type for which the list of test beds will be
            populated.
        :param cadence: The cadence for which the list of test beds will be
            populated.
        :type dut: str
        :type ttype: str
        :type cadence: str
        :returns: Alphabeticaly sorted list of test beds.
        :rtype: list
        """
        return sorted(list(self.df_job_info.loc[(
            (self.df_job_info["dut"] == dut) &
            (self.df_job_info["ttype"] == ttype) &
            (self.df_job_info["cadence"] == cadence)
        )]["tbed"].unique()))

    def _get_job(self, dut, ttype, cadence, testbed):
        """Get the name of a job defined by dut, ttype, cadence, test bed.
        Input information comes from the control panel.

        :param dut: The DUT for which the job name will be created.
        :param ttype: The test type for which the job name will be created.
        :param cadence: The cadence for which the job name will be created.
        :param testbed: The test bed for which the job name will be created.
        :type dut: str
        :type ttype: str
        :type cadence: str
        :type testbed: str
        :returns: Job name.
        :rtype: str
        """
        return self.df_job_info.loc[(
            (self.df_job_info["dut"] == dut) &
            (self.df_job_info["ttype"] == ttype) &
            (self.df_job_info["cadence"] == cadence) &
            (self.df_job_info["tbed"] == testbed)
        )]["job"].item()

    @staticmethod
    def _generate_options(opts: list) -> list:
        """Return list of options for radio items in control panel. The items in
        the list are dictionaries with keys "label" and "value".

        :params opts: List of options (str) to be used for the generated list.
        :type opts: list
        :returns: List of options (dict).
        :rtype: list
        """
        return [{"label": i, "value": i} for i in opts]

    def _set_job_params(self, job: str) -> dict:
        """Create a dictionary with all options and values for (and from) the
        given job.

        :params job: The name of job for and from which the dictionary will be
            created.
        :type job: str
        :returns: Dictionary with all options and values for (and from) the
            given job.
        :rtype: dict
        """

        lst_job = job.split("-")
        return {
            "job": job,
            "dut": lst_job[1],
            "ttype": lst_job[3],
            "cadence": lst_job[4],
            "tbed": "-".join(lst_job[-2:]),
            "duts": self._generate_options(self._get_duts()),
            "ttypes": self._generate_options(self._get_ttypes(lst_job[1])),
            "cadences": self._generate_options(self._get_cadences(
                lst_job[1], lst_job[3])),
            "tbeds": self._generate_options(self._get_test_beds(
                lst_job[1], lst_job[3], lst_job[4]))
        }

    def _show_tooltip(self, id: str, title: str,
            clipboard_id: str=None) -> list:
        """Generate list of elements to display a text (e.g. a title) with a
        tooltip and optionaly with Copy&Paste icon and the clipboard
        functionality enabled.

        :param id: Tooltip ID.
        :param title: A text for which the tooltip will be displayed.
        :param clipboard_id: If defined, a Copy&Paste icon is displayed and the
            clipboard functionality is enabled.
        :type id: str
        :type title: str
        :type clipboard_id: str
        :returns: List of elements to display a text with a tooltip and
            optionaly with Copy&Paste icon.
        :rtype: list
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
        """Top level method which generated the web page.

        It generates:
        - Store for user input data,
        - Navigation bar,
        - Main area with control panel and ploting area.

        If no HTML layout is provided, an error message is displayed instead.

        :returns: The HTML div with teh whole page.
        :rtype: html.Div
        """

        if self.html_layout:
            return html.Div(
                id="div-main",
                children=[
                    dcc.Store(id="control-panel"),
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
        :rtype: dbc.col
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
        :rtype: dbc.col
        """

        return dbc.Col(
            id="col-plotting-area",
            children=[
                dbc.Row(  # Failed tests
                    id="row-table-failed",
                    class_name="g-0 p-2",
                    children=self._default_tab_failed
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
                                    children=self._show_tooltip(
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
                                    children=self._show_tooltip(
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
                                    children=self._show_tooltip(
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
                                    children=self._show_tooltip(
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
                ),
            ]
        )

    class ControlPanel:
        """
        """

        def __init__(self, panel: dict, default: dict) -> None:
            """
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
            return self._panel[key]

        def values(self) -> list:
            return list(self._panel.values())

    def callbacks(self, app):

        @app.callback(
            Output("control-panel", "data"),  # Store
            Output("row-table-failed", "children"),
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
        )
        def _update_ctrl_panel(cp_data: dict, dut:str, ttype: str, cadence:str,
                tbed: str) -> tuple:
            """
            """

            ctrl_panel = self.ControlPanel(cp_data, self.default)

            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]
            if trigger_id == "ri-duts":
                ttype_opts = self._generate_options(self._get_ttypes(dut))
                ttype_val = ttype_opts[0]["value"]
                cad_opts = self._generate_options(
                    self._get_cadences(dut, ttype_val))
                cad_val = cad_opts[0]["value"]
                tbed_opts = self._generate_options(
                    self._get_test_beds(dut, ttype_val, cad_val))
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
                cad_opts = self._generate_options(
                    self._get_cadences(ctrl_panel.get("ri-duts-value"), ttype))
                cad_val = cad_opts[0]["value"]
                tbed_opts = self._generate_options(
                    self._get_test_beds(ctrl_panel.get("ri-duts-value"),
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
                tbed_opts = self._generate_options(
                    self._get_test_beds(ctrl_panel.get("ri-duts-value"),
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

            job = self._get_job(
                ctrl_panel.get("ri-duts-value"),
                ctrl_panel.get("ri-ttypes-value"),
                ctrl_panel.get("ri-cadences-value"),
                ctrl_panel.get("dd-tbeds-value")
            )
            ctrl_panel.set({"al-job-children": job})
            tab_failed = table_failed(self.data, job)

            ret_val = [
                ctrl_panel.panel,
                tab_failed
            ]
            ret_val.extend(ctrl_panel.values())
            return ret_val
