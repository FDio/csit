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


@app.route("/")
def home():
    """Landing page.
    """
    return render_template(
        "index_layout.jinja2",
        title="FD.io CSIT",
        description="Performance Dashboard",
        template="d-flex h-100 text-center text-white bg-dark"
    )
