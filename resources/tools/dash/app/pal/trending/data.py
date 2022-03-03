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

"""Prepare data for Plotly Dash.
"""

import pandas as pd


def read_data():
    """Create Pandas DataFrame from local CSV.

    Only for DEMO
    """

    return pd.read_csv(
        u"https://s3-docs.fd.io/csit/master/trending/_static/vpp/"
        u"csit-vpp-perf-mrr-weekly-master-2n-aws-trending.csv"
    )
