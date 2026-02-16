"""This module defines constants and their values used in the whole application.
"""


class Constants:
    """Constants and their values used in the whole application.
    """

    # Logging.
    LOGGING_LEVEL = ("NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    DEFAULT_LOG_LEVEL = "INFO"

    # GitHub.
    DEFAULT_GITHUB_URL = "https://api.github.com"
    DEFAULT_GITHUB_ACCOUNT = "repos"
    DEFAULT_GITHUB_REPO = "fdio/csit"
    DEFAULT_GITHUB_PAT = str()

    # Application configuration file.
    DEFAULT_PATH_CONFIG = "hfr/app_conf.yaml"

    # Interval between runs of job management in seconds.
    DEFAULT_SLEEP_INTERVAL = 30
    MIN_SLEEP_INTERVAL = 5
    MAX_SLEEP_INTERVAL = 3600

    # The means of job queuing during the processing of job configuration file.
    QUEUING  = ("sequential", "mixed", "random")

    # Priorities of runs
    MIN_PRIO = 9
    MAX_PRIO = 1

    # Number of repetitions of a run (used with (mainly) iterative jobs, when
    # the same run is run several times).
    MIN_REPEAT = 1
    MAX_REPEAT = 20
