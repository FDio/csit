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

"""Compile static assets."""
from flask import current_app as app
from flask_assets import Bundle


def compile_static_assets(assets):
    """Compile stylesheets if in development mode.

    :param assets: Flask-Assets Environment.
    :type assets: Environment
    :returns: Compiled stylesheets.
    :rtype: Environment
    """
    assets.auto_build = True
    assets.debug = False
    less_bundle = Bundle(
        "less/*.less",
        filters="less,cssmin",
        output="dist/css/styles.css",
        extra={"rel": "stylesheet/less"},
    )
    assets.register("less_all", less_bundle)
    if app.config["FLASK_ENV"] == "development":
        less_bundle.build()
    return assets
