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

import pandas as pd
import dash_bootstrap_components as dbc

from flask import Flask
from dash import dcc
from dash import html
from dash import callback_context
from dash import Input, Output, State

from ..utils.constants import Constants as C
from ..utils.utils import gen_new_url, navbar_trending
from ..utils.anomalies import classify_anomalies
from ..utils.url_processing import url_decode
from .tables import table_summary


class Layout:
    """The layout of the dash app and the callbacks.
    """

    def __init__(
            self,
            app: Flask,
            data_stats: pd.DataFrame,
            data_trending: pd.DataFrame,
            html_layout_file: str
        ) -> None:
        """Initialization:
        - save the input parameters,
        - read and pre-process the data,
        - prepare data for the control panel,
        - read HTML layout file,
        - read tooltips from the tooltip file.

        :param app: Flask application running the dash application.
        :param data_stats: Pandas dataframe with staistical data.
        :param data_trending: Pandas dataframe with trending data.
        :param html_layout_file: Path and name of the file specifying the HTML
            layout of the dash application.
        :type app: Flask
        :type data_stats: pandas.DataFrame
        :type data_trending: pandas.DataFrame
        :type html_layout_file: str
        """

        # Inputs
        self._app = app
        self._html_layout_file = html_layout_file

        # Prepare information for the control panel:
        self._jobs = sorted(list(data_trending["job"].unique()))
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
        for job in self._jobs:
            # Create lists of failed tests:
            df_job = data_trending.loc[(data_trending["job"] == job)]
            last_build = str(max(pd.to_numeric(df_job["build"].unique())))
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
                tst_data = df_job.loc[(
                    (df_job["test_id"] == test) &
                    (df_job["passed"] == True)
                )].sort_values(by="start_time", ignore_index=True)
                if "-ndrpdr" in test:
                    tst_data = tst_data.dropna(
                        subset=["result_pdr_lower_rate_value", ]
                    )
                    if tst_data.empty:
                        continue
                    x_axis = tst_data["start_time"].tolist()
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
                    x_axis = tst_data["start_time"].tolist()
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

        try:
            with open(self._html_layout_file, "r") as file_read:
                self._html_layout = file_read.read()
        except IOError as err:
            raise RuntimeError(
                f"Not possible to open the file {self._html_layout_file}\n{err}"
            )

        self._default_period = C.NEWS_SHORT
        self._default_active = (False, True, False)

        # Callbacks:
        if self._app is not None and hasattr(self, 'callbacks'):
            self.callbacks(self._app)

    @property
    def html_layout(self) -> dict:
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

        if self.html_layout:
            return html.Div(
                id="div-main",
                className="small",
                children=[
                    dcc.Location(id="url", refresh=False),
                    dbc.Row(
                        id="row-navbar",
                        class_name="g-0",
                        children=[navbar_trending((False, True, False, False))]
                    ),
                    dbc.Row(
                        id="row-main",
                        class_name="g-0",
                        children=[
                            self._add_ctrl_col(),
                            self._add_plotting_col()
                        ]
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
                dbc.NavItem(dbc.NavLink(
                    C.TREND_TITLE,
                    external_link=True,
                    href="/trending"
                )),
                dbc.NavItem(dbc.NavLink(
                    C.NEWS_TITLE,
                    active=True,
                    external_link=True,
                    href="/news"
                )),
                dbc.NavItem(dbc.NavLink(
                    C.STATS_TITLE,
                    external_link=True,
                    href="/stats"
                )),
                dbc.NavItem(dbc.NavLink(
                    "Documentation",
                    id="btn-documentation",
                ))
            ],
            brand=C.BRAND,
            brand_href="/",
            brand_external_link=True,
            class_name="p-2",
            fluid=True
        )

    def _add_ctrl_col(self) -> dbc.Col:
        """Add column with control panel. It is placed on the left side.

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
        """Add column with tables. It is placed on the right side.

        :returns: Column with tables.
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
                    dbc.ButtonGroup(
                        id="bg-time-period",
                        children=[
                            dbc.Button(
                                id="period-last",
                                children="Last Run",
                                className="me-1",
                                outline=True,
                                color="info"
                            ),
                            dbc.Button(
                                id="period-short",
                                children=f"Last {C.NEWS_SHORT} Runs",
                                className="me-1",
                                outline=True,
                                active=True,
                                color="info"
                            ),
                            dbc.Button(
                                id="period-long",
                                children="All Runs",
                                className="me-1",
                                outline=True,
                                color="info"
                            )
                        ]
                    )
                ]
            )
        ]

    def _get_plotting_area(
            self,
            period: int,
            url: str
        ) -> list:
        """Generate the plotting area with all its content.

        :param period: The time period for summary tables.
        :param url: URL to be displayed in the modal window.
        :type period: int
        :type url: str
        :returns: The content of the plotting area.
        :rtype: list
        """
        return [
            dbc.Row(
                id="row-table",
                class_name="g-0 p-1",
                children=table_summary(self._data, self._jobs, period)
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
                            )
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
            Output("plotting-area", "children"),
            Output("period-last", "active"),
            Output("period-short", "active"),
            Output("period-long", "active"),
            Input("url", "href"),
            Input("period-last", "n_clicks"),
            Input("period-short", "n_clicks"),
            Input("period-long", "n_clicks")
        )
        def _update_application(href: str, *_) -> tuple:
            """Update the application when the event is detected.

            :returns: New values for web page elements.
            :rtype: tuple
            """

            periods = {
                "period-last": C.NEWS_LAST,
                "period-short": C.NEWS_SHORT,
                "period-long": C.NEWS_LONG
            }
            actives = {
                "period-last": (True, False, False),
                "period-short": (False, True, False),
                "period-long": (False, False, True)
            }

            # Parse the url:
            parsed_url = url_decode(href)
            if parsed_url:
                url_params = parsed_url["params"]
            else:
                url_params = None

            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]
            if trigger_id == "url" and url_params:
                trigger_id = url_params.get("period", list())[0]

            ret_val = [
                self._get_plotting_area(
                    periods.get(trigger_id, self._default_period),
                    gen_new_url(parsed_url, {"period": trigger_id})
                )
            ]
            ret_val.extend(actives.get(trigger_id, self._default_active))
            return ret_val

        @app.callback(
            Output("plot-mod-url", "is_open"),
            [Input("plot-btn-url", "n_clicks")],
            [State("plot-mod-url", "is_open")],
        )
        def toggle_plot_mod_url(n, is_open):
            """Toggle the modal window with url.
            """
            if n:
                return not is_open
            return is_open

        @app.callback(
            Output("offcanvas-documentation", "is_open"),
            Input("btn-documentation", "n_clicks"),
            State("offcanvas-documentation", "is_open")
        )
        def toggle_offcanvas_documentation(n_clicks, is_open):
            if n_clicks:
                return not is_open
            return is_open
