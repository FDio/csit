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

"""Initialize Flask app.
"""

import logging

from flask import Flask
from flask_assets import Environment, Bundle

from .utils.constants import Constants as C


def init_app():
    """Construct core Flask application with embedded Dash app.
    """
    logging.basicConfig(
        format=C.LOG_FORMAT,
        datefmt=C.LOG_DATE_FORMAT,
        level=C.LOG_LEVEL
    )

    logging.info("Application started.")

    app = Flask(__name__, instance_relative_config=False)
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

        # Set the time period for Trending
        if C.TIME_PERIOD is None or C.TIME_PERIOD > C.MAX_TIME_PERIOD:
            time_period = C.MAX_TIME_PERIOD
        else:
            time_period = C.TIME_PERIOD

        # Import Dash applications.
        # from .news.news import init_news
        # app = init_news(app)

        # from .stats.stats import init_stats
        # app = init_stats(app, time_period=time_period)

        # from .trending.trending import init_trending
        # app = init_trending(app, time_period=time_period)

        from .report.report import init_report
        app = init_report(app, releases=C.RELEASES)

    return app


app = init_app()
