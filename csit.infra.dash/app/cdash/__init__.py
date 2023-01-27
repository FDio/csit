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
            debug=True
        ).read_all_data(releases=C.RELEASES, days=time_period)

        # Import Dash applications.
        from .news.news import init_news
        app = init_news(
            app,
            data_stats=data["statistics"],
            data_mrr=data["trending-mrr"],
            data_ndrpdr=data["trending-ndrpdr"]
        )

        from .stats.stats import init_stats
        app = init_stats(
            app,
            data_stats=data["statistics"],
            data_mrr=data["trending-mrr"],
            data_ndrpdr=data["trending-ndrpdr"]
        )

        from .trending.trending import init_trending
        app = init_trending(
            app,
            data_mrr=data["trending-mrr"],
            data_ndrpdr=data["trending-ndrpdr"]
        )

        from .report.report import init_report
        app = init_report(
            app,
            data_iterative=data["iterative"]
        )

    return app


app = init_app()
