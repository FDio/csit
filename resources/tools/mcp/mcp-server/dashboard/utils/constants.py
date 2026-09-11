"""Constants used.

"Constant" means a value that keeps its value since initialization. The value
does not need to be hard coded here, but can be read from environment variables.
"""

import os
import logging


def get_str_from_env(env_var_name: str, default_value: str) -> str:
    """Return a CSIT-prefixed environment string or a default value.

    Environment variables are looked up as ``CSIT_<env_var_name>``.

    If environment variable exists, but is empty (and default is not),
    empty string is returned.

    :param env_var_name: Base name of the environment variable to read.
    :param default_value: Value to return if the env var does not exist.
    :type env_var_name: str
    :type default_value: str
    :returns: The value read, or default value.
    :rtype: str
    """
    prefix = "CSIT_"
    env_str = os.environ.get(prefix + env_var_name, None)
    if env_str is not None:
        return env_str
    return default_value


def get_int_from_env(env_var_name: str, default_value: int) -> int:
    """Return a CSIT-prefixed environment integer or a default value.

    Environment variables are looked up as ``CSIT_<env_var_name>``.

    String value is read, default is returned also if conversion fails.

    :param env_var_name: Base name of the environment variable to read.
    :param default_value: Value to return if read or conversion fails.
    :type env_var_name: str
    :type default_value: int
    :returns: The value read, or default value.
    :rtype: int
    """
    try:
        return int(get_str_from_env(env_var_name, str()))
    except ValueError:
        return default_value


def get_bool_from_env(env_var_name: str, default_value: bool) -> bool:
    """Return a CSIT-prefixed environment boolean or a default value.

    Environment variables are looked up as ``CSIT_<env_var_name>``.

    :param env_var_name: Base name of the environment variable to read.
    :param default_value: Value to return if read or conversion fails.
    :type env_var_name: str
    :type default_value: bool
    :returns: The value read, or default value.
    :rtype: bool
    """
    env_str = get_str_from_env(env_var_name, str()).lower()
    if env_str in ("true", "yes", "y", "1"):
        return True
    elif env_str in ("false", "no", "n", "0"):
        return False
    else:
        return default_value


class Constants:
    """Constants used in MCP.
    """

    ############################################################################
    # General, application wide constants.

    # AWS specific settings.
    AWS_ENDPOINT_URL = get_str_from_env("AWS_ENDPOINT_URL", "")

    # Data loading mode.
    # Options:
    # 1. s3 - read FD.io CSIT parquet data from S3-compatible storage.
    # 2. fixture - read small local JSON fixture data.
    DATA_MODE = get_str_from_env("DATA_MODE", "s3")

    # Optional scheduled data refresh interval.
    # 0 disables scheduled refreshes.
    REFRESH_INTERVAL_SECONDS = get_int_from_env("REFRESH_INTERVAL_SECONDS", 0)

    # Comma-separated CORS allowlist for the FastAPI wrapper.
    # "*" preserves trusted-local development behavior.
    CORS_ALLOW_ORIGINS = get_str_from_env("CORS_ALLOW_ORIGINS", "*")

    # Select applications to start.
    START_TRENDING = get_bool_from_env("START_TRENDING", True)
    START_REPORT = get_bool_from_env("START_REPORT", True)
    START_COMPARISONS = get_bool_from_env("START_COMPARISONS", True)
    START_COVERAGE = get_bool_from_env("START_COVERAGE", True)
    START_STATISTICS = get_bool_from_env("START_STATISTICS", True)
    START_FAILURES = get_bool_from_env("START_FAILURES", True)
    START_SEARCH = get_bool_from_env("START_SEARCH", True)
    START_DOC = get_bool_from_env("START_DOC", True)

    # Logging settings.
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s: %(levelname)s: %(message)s"
    LOG_DATE_FORMAT = "%Y/%m/%d %H:%M:%S"

    # CICD type.
    # Options:
    # 1. csit - for CICD used by CSIT in LFN environment
    # 2. external - otherwise
    CICD_TYPE = get_str_from_env("CICD_TYPE", "csit")

    # URL to CICD.
    URL_CICD = get_str_from_env(
        "URL_CICD", "https://github.com/FDio/csit/actions/workflows/"
    )

    # URL to logs.
    URL_LOGS = get_str_from_env(
        "URL_LOGS", "https://logs.fd.io/vex-yul-rot-jenkins-1/"
    )

    # URL to the documentation.
    URL_DOC = get_str_from_env("URL_DOC", "https://csit.fd.io/cdocs/")
    URL_DOC_TRENDING = URL_DOC + "methodology/trending/analysis/"
    URL_DOC_REL_NOTES = URL_DOC + "release_notes/current/"

    # Application root.
    MOUNT_PREFIX = ""
    MCP_PATH = "/mcp"

    # Data to be downloaded from the parquets specification file.
    DATA_SPEC_FILE = "./dashboard/data/data.yaml"

    # Path to schemas to use when reading data from the parquet.
    PATH_TO_SCHEMAS = "./dashboard/data/_metadata/"

    # Max pool size for boto3
    MAX_POOL_SIZE = get_int_from_env("MAX_POOL_SIZE", 30)

    # Maximal value of TIME_PERIOD for data read from the parquets in days.
    # Do not change without a good reason.
    MAX_TIME_PERIOD = 200

    # It defines the time period for data read from the parquets in days from
    # now back to the past.
    # TIME_PERIOD = None - means all data (max MAX_TIME_PERIOD days) is read.
    # TIME_PERIOD = MAX_TIME_PERIOD - is the default value
    TIME_PERIOD = get_int_from_env("TIME_PERIOD", MAX_TIME_PERIOD)  # [days]

    ############################################################################
    # General, application wide, layout affecting constants.

    # List of drivers used in CSIT.
    DRIVERS = ("avf", "af-xdp", "rdma", "dpdk", "mlx5", "octeon")
    DRVS_NOT_IN_NAME = ("dpdk", "octeon")

    # Labels for input elements (dropdowns, ...).
    LABELS = {
        "dpdk": "DPDK",
        "container_memif": "LXC/DRC Container Memif",
        "crypto": "IPSec IPv4 Routing",
        "gso": "GSO",
        "ip4": "IPv4 Routing",
        "ip4_tunnels": "IPv4 Tunnels",
        "ip6": "IPv6 Routing",
        "ip6_tunnels": "IPv6 Tunnels",
        "l2": "L2 Ethernet Switching",
        "lb": "Load Balancer",
        "srv6": "SRv6 Routing",
        "vm_vhost": "VMs vhost-user",
        "nfv_density.dcr_memif.chain_ipsec": "CNF Service Chains Routing IPSec",
        "nfv_density.vm_vhost.chain_dot1qip4vxlan":"VNF Service Chains Tunnels",
        "nfv_density.vm_vhost.chain": "VNF Service Chains Routing",
        "nfv_density.dcr_memif.pipeline": "CNF Service Pipelines Routing",
        "nfv_density.dcr_memif.chain": "CNF Service Chains Routing",
        "hoststack": "Hoststack",
        "flow": "Flow",
        "l2bd": "L2 Bridge Domain",
        "crypto.ethip4": "IPSec IPv4 Routing",
        "crypto.ethip6": "IPSec IPv6 Routing",
        "interfaces": "Interfaces",
        "ip4_tunnels.lisp": "IPv4 Tunnels LISP",
        "ip6_tunnels.lisp": "IPv6 Tunnels LISP",
        "l2patch": "L2 Patch",
        "l2xc": "L2 Cross Connect",
        "vm_vhost.ethip4": "VMs vhost-user IPv4 Routing",
        "vm_vhost.ethip6": "VMs vhost-user IPv6 Routing"
    }

    ############################################################################
    # General, normalization constants.

    NORM_FREQUENCY = 2.0  # [GHz]
    FREQUENCY = {  # [GHz]
        "1n-aws": 3.400,
        "2n-aws": 3.400,
        "2n-c6in": 3.500,
        "2n-c7gn": 3.500,
        "2n-c8gn": 3.500,
        "2n-grc": 3.300,
        "2n-icx": 2.600,
        "2n-spr": 2.800,
        "2n-emr": 2.300,
        "2n-gnr": 2.400,
        "2n-zn2": 2.900,
        "3n-alt": 3.000,
        "3n-icx": 2.600,
        "3n-icxd": 2.000,
        "3n-oct": 2.500,
        "3n-snr": 2.200,
        "3n-srf": 2.200,
        "3n-emr": 2.300,
        "3n-gnr": 2.400,
        "3na-spr": 2.800,
        "3nb-spr": 2.800
    }

    # Access to the results.
    VALUE = {
        "mrr": "result_receive_rate_rate_avg",
        "ndr": "result_ndr_lower_rate_value",
        "pdr": "result_pdr_lower_rate_value",
        "mrr-bandwidth": "result_receive_rate_bandwidth_avg",
        "ndr-bandwidth": "result_ndr_lower_bandwidth_value",
        "pdr-bandwidth": "result_pdr_lower_bandwidth_value",
        "latency": "result_latency_forward_pdr_50_avg",
        "hoststack-cps": "result_rate_value",
        "hoststack-rps": "result_rate_value",
        "hoststack-cps-bandwidth": "result_bandwidth_value",
        "hoststack-rps-bandwidth": "result_bandwidth_value",
        "hoststack-bps": "result_bandwidth_value",
        "hoststack-latency": "result_latency_value",
        "soak": "result_critical_rate_lower_rate_value",
        "soak-bandwidth": "result_critical_rate_lower_bandwidth_value"
    }

    VALUE_ITER = {
        "mrr": "result_receive_rate_rate_avg",
        "ndr": "result_ndr_lower_rate_value",
        "pdr": "result_pdr_lower_rate_value",
        "mrr-bandwidth": "result_receive_rate_bandwidth_avg",
        "ndr-bandwidth": "result_ndr_lower_bandwidth_value",
        "pdr-bandwidth": "result_pdr_lower_bandwidth_value",
        "latency": "result_latency_forward_pdr_50_avg",
        "hoststack-cps": "result_rate_value",
        "hoststack-rps": "result_rate_value",
        "hoststack-cps-bandwidth": "result_bandwidth_value",
        "hoststack-rps-bandwidth": "result_bandwidth_value",
        "hoststack-bps": "result_bandwidth_value",
        "hoststack-latency": "result_latency_value",
        "soak": "result_critical_rate_lower_rate_value",
        "soak-bandwidth": "result_critical_rate_lower_bandwidth_value"
    }

    UNIT = {
        "mrr": "result_receive_rate_rate_unit",
        "ndr": "result_ndr_lower_rate_unit",
        "pdr": "result_pdr_lower_rate_unit",
        "mrr-bandwidth": "result_receive_rate_bandwidth_unit",
        "ndr-bandwidth": "result_ndr_lower_bandwidth_unit",
        "pdr-bandwidth": "result_pdr_lower_bandwidth_unit",
        "latency": "result_latency_forward_pdr_50_unit",
        "hoststack-cps": "result_rate_unit",
        "hoststack-rps": "result_rate_unit",
        "hoststack-cps-bandwidth": "result_bandwidth_unit",
        "hoststack-rps-bandwidth": "result_bandwidth_unit",
        "hoststack-bps": "result_bandwidth_unit",
        "hoststack-latency": "result_latency_unit",
        "soak": "result_critical_rate_lower_rate_unit",
        "soak-bandwidth": "result_critical_rate_lower_bandwidth_unit"
    }

    TESTS_WITH_BANDWIDTH = (
        "ndr",
        "pdr",
        "mrr",
        "hoststack-cps",
        "hoststack-rps",
        "soak"
    )
    TESTS_WITH_LATENCY = (
        "pdr",
        "hoststack-cps",
        "hoststack-rps"
    )

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

    # Operators used to filter data in comparison tables.
    OPERATORS = (
        ("contains ", ),
        ("lt ", "<"),
        ("gt ", ">"),
        ("eq ", "="),
        ("ge ", ">="),
        ("le ", "<="),
        ("ne ", "!="),
        ("datestartswith ", )
    )

    ############################################################################
    # News.

    # The title.
    NEWS_TITLE = "Failures and Anomalies"

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

    ############################################################################
    # Comparisons.

    # The title.
    COMP_TITLE = "Per Release Performance Comparisons"

    # This parameter specifies the method to use for estimating the percentile.
    # Possible values:
    # - inverted_cdf
    # - averaged_inverted_cdf
    # - closest_observation
    # - interpolated_inverted_cdf
    # - hazen
    # - weibull
    # - linear (default)
    # - median_unbiased
    # - normal_unbiased
    COMP_PERCENTILE_METHOD = "linear"

    # Extreme or mild outlier?
    OUTLIER_EXTREME = 3
    OUTLIER_MILD = 1.5
    COMP_OUTLIER_TYPE = OUTLIER_EXTREME

    ############################################################################
    # Statistics.

    # The title.
    STATS_TITLE = "Test Job Statistics"

    ############################################################################
    # Trending.

    # The title.
    TREND_TITLE = "Performance Trending"

    ############################################################################
    # Coverage data.

    # The title.
    COVERAGE_TITLE = "Per Release Coverage Data"
