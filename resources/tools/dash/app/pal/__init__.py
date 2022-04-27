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

        # Import Dash applications.
        from .stats.stats import init_stats
        app = init_stats(app)

        # from .trending.trending import init_trending
        # app = init_trending(app)

    return app

app = init_app()
