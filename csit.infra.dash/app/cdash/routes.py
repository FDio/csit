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

"""Routes for parent Flask app.
"""

from flask import current_app as app
from flask import render_template

from .utils.constants import Constants as C


@app.route(C.APPLICATIN_ROOT)
def home():
    """Landing page.
    """
    return render_template(
        C.MAIN_HTML_LAYOUT_FILE,
        title=C.TITLE,
        description=C.DESCRIPTION,
        trending_title=C.TREND_TITLE,
        report_title=C.REPORT_TITLE,
        stats_title=C.STATS_TITLE,
        news_title=C.NEWS_TITLE
    )
