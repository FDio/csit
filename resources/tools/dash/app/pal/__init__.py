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
from flask_assets import Environment


# Maximal value of TIME_PERIOD for Trending in days.
# Do not change without a good reason.
MAX_TIME_PERIOD = 180

# It defines the time period for Trending in days from now back to the past from
# which data is read to dataframes.
# TIME_PERIOD = None means all data (max MAX_TIME_PERIOD days) is read.
# TIME_PERIOD = MAX_TIME_PERIOD is the default value
TIME_PERIOD = MAX_TIME_PERIOD  # [days]

# List of releases used for iterative data processing.
# The releases MUST be in the order from the current (newest) to the last
# (oldest).
RELEASES=["csit2206", "csit2202", ]

def init_app():
    """Construct core Flask application with embedded Dash app.
    """

    logging.basicConfig(
        format=u"%(asctime)s: %(levelname)s: %(message)s",
        datefmt=u"%Y/%m/%d %H:%M:%S",
        level=logging.INFO
    )

    logging.info("Application started.")

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(u"config.Config")

    with app.app_context():
        # Import parts of our core Flask app.
        from . import routes

        assets = Environment()
        assets.init_app(app)

        if TIME_PERIOD is None or TIME_PERIOD > MAX_TIME_PERIOD:
            time_period = MAX_TIME_PERIOD
        else:
            time_period = TIME_PERIOD

        # Import Dash applications.
        from .news.news import init_news
        app = init_news(app)

        from .stats.stats import init_stats
        app = init_stats(app, time_period=time_period)

        from .trending.trending import init_trending
        app = init_trending(app, time_period=time_period)

        from .report.report import init_report
        app = init_report(app, releases=RELEASES)

    return app


app = init_app()
