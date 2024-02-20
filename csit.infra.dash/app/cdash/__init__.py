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

"""Initialize Flask app.
"""

import logging
import pandas as pd

from flask import Flask
from flask_assets import Environment, Bundle

from .utils.constants import Constants as C
from .data.data import Data


def init_app():
    """Construct core Flask application with embedded Dash app.
    """
    logging.basicConfig(
        format=C.LOG_FORMAT,
        datefmt=C.LOG_DATE_FORMAT,
        level=C.LOG_LEVEL
    )

    app = Flask(__name__, instance_relative_config=False)
    app.logger.info("Application started.")
    app.config.from_object("config.Config")

    with app.app_context():
        # Import parts of our core Flask app.
        from . import routes

        assets = Environment()
        assets.init_app(app)

        # Compile static assets.
        sass_bundle = Bundle(
            "sass/lux.scss",
            filters="libsass",
            output="dist/css/bootstrap.css",
            depends="**/*.scss",
            extra={
                "rel": "stylesheet"
            }
        )
        assets.register("sass_all", sass_bundle)
        sass_bundle.build()

        if C.TIME_PERIOD is None or C.TIME_PERIOD > C.MAX_TIME_PERIOD:
            time_period = C.MAX_TIME_PERIOD
        else:
            time_period = C.TIME_PERIOD

        data = Data(
            data_spec_file=C.DATA_SPEC_FILE,
        ).read_all_data(days=time_period)

        # Import Dash applications.
        logging.info("\n\nStarting the applications:\n" + "-" * 26 + "\n")
        if data["statistics"].empty or data["trending"].empty:
            logging.error(
                f'"{C.NEWS_TITLE}" application not loaded, no data available.'
            )
            logging.error(
                f'"{C.STATS_TITLE}" application not loaded, no data available.'
            )
        else:
            logging.info(C.NEWS_TITLE)
            from .news.news import init_news
            app = init_news(
                app,
                data_stats=data["statistics"],
                data_trending=data["trending"]
            )

            logging.info(C.STATS_TITLE)
            from .stats.stats import init_stats
            app = init_stats(
                app,
                data_stats=data["statistics"],
                data_trending=data["trending"]
            )

        if data["trending"].empty:
            logging.error(
                f'"{C.TREND_TITLE}" application not loaded, no data available.'
            )
        else:
            logging.info(C.TREND_TITLE)
            from .trending.trending import init_trending
            app = init_trending(app, data_trending=data["trending"])

        if data["iterative"].empty:
            logging.error(
                f'"{C.REPORT_TITLE}" application not loaded, no data available.'
            )
            logging.error(
                f'"{C.COMP_TITLE}" application not loaded, no data available.'
            )
        else:
            logging.info(C.REPORT_TITLE)
            from .report.report import init_report
            app = init_report(app, data_iterative=data["iterative"])

            logging.info(C.COMP_TITLE)
            from .comparisons.comparisons import init_comparisons
            app = init_comparisons(app, data_iterative=data["iterative"])

        if data["coverage"].empty:
            logging.error((
                f'"{C.COVERAGE_TITLE}" application not loaded, '
                'no data available.'
            ))
        else:
            logging.info(C.COVERAGE_TITLE)
            from .coverage.coverage import init_coverage
            app = init_coverage(app, data_coverage=data["coverage"])

        if all((data["trending"].empty, data["iterative"].empty,
                data["coverage"].empty)):
            logging.error((
                f'"{C.SEARCH_TITLE}" application not loaded, '
                'no data available.'
            ))
        else:
            logging.info(C.SEARCH_TITLE)
            from .search.search import init_search
            app = init_search(app, data)

    return app


app = init_app()
