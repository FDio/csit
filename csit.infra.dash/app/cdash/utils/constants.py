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

"""Constants used in CDash.

"Constant" means a value that keeps its value since initialization. The value
does not need to be hard coded here, but can be read from environment variables.
"""

import logging

from dash import html


class Constants:
    """Constants used in CDash.
    """

    ############################################################################
    # General, application wide constants.

    # Logging settings.
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s: %(levelname)s: %(message)s"
    LOG_DATE_FORMAT = "%Y/%m/%d %H:%M:%S"

    # The application title.
    TITLE = "FD.io CSIT"
    BRAND = "CSIT-Dash"

    # The application description.
    DESCRIPTION = "Performance Dashboard"

    # External stylesheets.
    EXTERNAL_STYLESHEETS = ["/static/dist/css/bootstrap.css", ]

    # Path and name of the file specifying the HTML layout of the dash
    # application.
    MAIN_HTML_LAYOUT_FILE = "base_layout.jinja2"

    # Path and name of the file specifying the HTML layout of the dash
    # application.
    HTML_LAYOUT_FILE = "cdash/templates/dash_layout.jinja2"

    # Application root.
    APPLICATIN_ROOT = "/"

    # Data to be downloaded from the parquets specification file.
    DATA_SPEC_FILE = "cdash/data/data.yaml"

    # The file with tooltips.
    TOOLTIP_FILE = "cdash/utils/tooltips.yaml"

    # Maximal value of TIME_PERIOD for data read from the parquets in days.
    # Do not change without a good reason.
    MAX_TIME_PERIOD = 180

    # It defines the time period for data read from the parquets in days from
    # now back to the past.
    # TIME_PERIOD = None - means all data (max MAX_TIME_PERIOD days) is read.
    # TIME_PERIOD = MAX_TIME_PERIOD - is the default value
    TIME_PERIOD = MAX_TIME_PERIOD  # [days]

    # List of releases used for iterative data processing.
    # The releases MUST be in the order from the current (newest) to the last
    # (oldest).
    RELEASES = ["rls2210", "rls2206", "rls2202", ]

    ############################################################################
    # General, application wide, layout affecting constants.

    # If True, clear all inputs in control panel when button "ADD SELECTED" is
    # pressed.
    CLEAR_ALL_INPUTS = False

    # The element is disabled.
    STYLE_DISABLED = {"display": "none"}

    # The element is enabled and visible.
    STYLE_ENABLED = {"display": "inherit"}

    # Checklist "All" is disabled.
    CL_ALL_DISABLED = [
        {
            "label": "All",
            "value": "all",
            "disabled": True
        }
    ]

    # Checklist "All" is enabled, visible and unchecked.
    CL_ALL_ENABLED = [
        {
            "label": "All",
            "value": "all",
            "disabled": False
        }
    ]

    # Placeholder for any element in the layout.
    PLACEHOLDER = html.Nobr("")

    # List of drivers used in CSIT.
    DRIVERS = ("avf", "af-xdp", "rdma", "dpdk")

    # Labels for input elements (dropdowns, ...).
    LABELS = {
        "dpdk": "DPDK",
        "container_memif": "LXC/DRC Container Memif",
        "crypto": "IPSec IPv4 Routing",
        "ip4": "IPv4 Routing",
        "ip6": "IPv6 Routing",
        "ip4_tunnels": "IPv4 Tunnels",
        "l2": "L2 Ethernet Switching",
        "srv6": "SRv6 Routing",
        "vm_vhost": "VMs vhost-user",
        "nfv_density-dcr_memif-chain_ipsec": "CNF Service Chains Routing IPSec",
        "nfv_density-vm_vhost-chain_dot1qip4vxlan":"VNF Service Chains Tunnels",
        "nfv_density-vm_vhost-chain": "VNF Service Chains Routing",
        "nfv_density-dcr_memif-pipeline": "CNF Service Pipelines Routing",
        "nfv_density-dcr_memif-chain": "CNF Service Chains Routing",
    }

    # URL style.
    URL_STYLE = {
        "background-color": "#d2ebf5",
        "border-color": "#bce1f1",
        "color": "#135d7c"
    }

    ############################################################################
    # General, normalization constants.

    NORM_FREQUENCY = 2.0  # [GHz]
    FREQUENCY = {  # [GHz]
        "2n-aws": 1.000,
        "2n-dnv": 2.000,
        "2n-clx": 2.300,
        "2n-icx": 2.600,
        "2n-skx": 2.500,
        "2n-tx2": 2.500,
        "2n-zn2": 2.900,
        "3n-alt": 3.000,
        "3n-aws": 1.000,
        "3n-dnv": 2.000,
        "3n-icx": 2.600,
        "3n-skx": 2.500,
        "3n-tsh": 2.200,
        "3n-snr": 2.200
    }

    ############################################################################
    # General, plots constants.

    PLOT_COLORS = (
        "#1A1110", "#DA2647", "#214FC6", "#01786F", "#BD8260", "#FFD12A",
        "#A6E7FF", "#738276", "#C95A49", "#FC5A8D", "#CEC8EF", "#391285",
        "#6F2DA8", "#FF878D", "#45A27D", "#FFD0B9", "#FD5240", "#DB91EF",
        "#44D7A8", "#4F86F7", "#84DE02", "#FFCFF1", "#614051"
    )

    # Trending, anomalies.
    ANOMALY_COLOR = {
        "regression": 0.0,
        "normal": 0.5,
        "progression": 1.0
    }

    COLORSCALE_TPUT = [
        [0.00, "red"],
        [0.33, "red"],
        [0.33, "white"],
        [0.66, "white"],
        [0.66, "green"],
        [1.00, "green"]
    ]

    TICK_TEXT_TPUT = ["Regression", "Normal", "Progression"]

    COLORSCALE_LAT = [
        [0.00, "green"],
        [0.33, "green"],
        [0.33, "white"],
        [0.66, "white"],
        [0.66, "red"],
        [1.00, "red"]
    ]

    TICK_TEXT_LAT = ["Progression", "Normal", "Regression"]

    # Access to the results.
    VALUE = {
        "mrr": "result_receive_rate_rate_avg",
        "ndr": "result_ndr_lower_rate_value",
        "pdr": "result_pdr_lower_rate_value",
        "pdr-lat": "result_latency_forward_pdr_50_avg"
    }

    VALUE_ITER = {
        "mrr": "result_receive_rate_rate_values",
        "ndr": "result_ndr_lower_rate_value",
        "pdr": "result_pdr_lower_rate_value",
        "pdr-lat": "result_latency_forward_pdr_50_avg"
    }

    UNIT = {
        "mrr": "result_receive_rate_rate_unit",
        "ndr": "result_ndr_lower_rate_unit",
        "pdr": "result_pdr_lower_rate_unit",
        "pdr-lat": "result_latency_forward_pdr_50_unit"
    }

    # Latencies.
    LAT_HDRH = (  # Do not change the order
        "result_latency_forward_pdr_0_hdrh",
        "result_latency_reverse_pdr_0_hdrh",
        "result_latency_forward_pdr_10_hdrh",
        "result_latency_reverse_pdr_10_hdrh",
        "result_latency_forward_pdr_50_hdrh",
        "result_latency_reverse_pdr_50_hdrh",
        "result_latency_forward_pdr_90_hdrh",
        "result_latency_reverse_pdr_90_hdrh",
    )

    # This value depends on latency stream rate (9001 pps) and duration (5s).
    # Keep it slightly higher to ensure rounding errors to not remove tick mark.
    PERCENTILE_MAX = 99.999501

    GRAPH_LAT_HDRH_DESC = {
        "result_latency_forward_pdr_0_hdrh": "No-load.",
        "result_latency_reverse_pdr_0_hdrh": "No-load.",
        "result_latency_forward_pdr_10_hdrh": "Low-load, 10% PDR.",
        "result_latency_reverse_pdr_10_hdrh": "Low-load, 10% PDR.",
        "result_latency_forward_pdr_50_hdrh": "Mid-load, 50% PDR.",
        "result_latency_reverse_pdr_50_hdrh": "Mid-load, 50% PDR.",
        "result_latency_forward_pdr_90_hdrh": "High-load, 90% PDR.",
        "result_latency_reverse_pdr_90_hdrh": "High-load, 90% PDR."
    }

    ############################################################################
    # News.

    # The title.
    NEWS_TITLE = "Failures and Anomalies"

    # The pathname prefix for the application.
    NEWS_ROUTES_PATHNAME_PREFIX = "/news/"

    # Time period for regressions and progressions.
    NEWS_TIME_PERIOD = TIME_PERIOD  # [days]

    # Time periods for summary tables.
    NEWS_LAST = 1  # [days]
    NEWS_SHORT = 7  # [days]
    NEWS_LONG = NEWS_TIME_PERIOD  # [days]

    ############################################################################
    # Report.

    # The title.
    REPORT_TITLE = "Per Release Performance"

    # The pathname prefix for the application.
    REPORT_ROUTES_PATHNAME_PREFIX = "/report/"

    # Layout of plot.ly graphs.
    REPORT_GRAPH_LAYOUT_FILE = "cdash/report/layout.yaml"

    # Default name of downloaded file with selected data.
    REPORT_DOWNLOAD_FILE_NAME = "iterative_data.csv"

    ############################################################################
    # Statistics.

    # The title.
    STATS_TITLE = "Test Job Statistics"

    # The pathname prefix for the application.
    STATS_ROUTES_PATHNAME_PREFIX = "/stats/"

    # Layout of plot.ly graphs.
    STATS_GRAPH_LAYOUT_FILE = "cdash/stats/layout.yaml"

    # The default job displayed when the page is loaded first time.
    STATS_DEFAULT_JOB = "csit-vpp-perf-mrr-daily-master-2n-icx"

    # Default name of downloaded file with selected data.
    STATS_DOWNLOAD_FILE_NAME = "stats.csv"

    ############################################################################
    # Trending.

    # The title.
    TREND_TITLE = "Performance Trending"

    # The pathname prefix for the application.
    TREND_ROUTES_PATHNAME_PREFIX = "/trending/"

    # Layout of plot.ly graphs.
    TREND_GRAPH_LAYOUT_FILE = "cdash/trending/layout.yaml"

    # Default name of downloaded file with selected data.
    TREND_DOWNLOAD_FILE_NAME = "trending_data.csv"
