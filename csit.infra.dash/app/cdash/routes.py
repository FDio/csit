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

"""Routes for parent Flask app.
"""

from flask import current_app as app
from flask import render_template

from .utils.constants import Constants as C


@app.route(C.APPLICATIN_ROOT)
def home():
    """Landing page.
    """

    menu_itms = list()
    if C.START_TRENDING:
        menu_itms.append({"path": "/trending/", "title": C.TREND_TITLE})
    if C.START_REPORT:
        menu_itms.append({"path": "/report/", "title": C.REPORT_TITLE})
    if C.START_COMPARISONS:
        menu_itms.append({"path": "/comparisons/", "title": C.COMP_TITLE})
    if C.START_COVERAGE:
        menu_itms.append({"path": "/coverage/", "title": C.COVERAGE_TITLE})
    if C.START_STATISTICS:
        menu_itms.append({"path": "/stats/", "title": C.STATS_TITLE})
    if C.START_FAILURES:
        menu_itms.append({"path": "/news/", "title": C.NEWS_TITLE})
    if C.START_SEARCH:
        menu_itms.append({"path": "/search/", "title": C.SEARCH_TITLE})
    if C.START_DOC:
        menu_itms.append({"path": "/cdocs/", "title": C.DOC_TITLE})

    return render_template(
        C.MAIN_HTML_LAYOUT_FILE,
        title=C.TITLE,
        brand=C.BRAND,
        description=C.DESCRIPTION,
        menu_itms=menu_itms
    )
