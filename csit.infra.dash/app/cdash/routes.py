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
    return render_template(
        C.MAIN_HTML_LAYOUT_FILE,
        title=C.TITLE,
        brand=C.BRAND,
        description=C.DESCRIPTION,
        copyright=C.COPYRIGHT,
        trending_title=C.TREND_TITLE,
        trending_display="d-block" if C.START_TRENDING else "d-none",
        report_title=C.REPORT_TITLE,
        report_display="d-block" if C.START_REPORT else "d-none",
        comp_title=C.COMP_TITLE,
        comp_display="d-block" if C.START_COMPARISONS else "d-none",
        stats_title=C.STATS_TITLE,
        stats_display="d-block" if C.START_STATISTICS else "d-none",
        news_title=C.NEWS_TITLE,
        news_display="d-block" if C.START_FAILURES else "d-none",
        cov_title=C.COVERAGE_TITLE,
        cov_display="d-block" if C.START_COVERAGE else "d-none",
        search_title=C.SEARCH_TITLE,
        search_display="d-block" if C.START_SEARCH else "d-none",
        doc_display="d-block" if C.START_DOC else "d-none"
    )
