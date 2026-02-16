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

    HFR_RUN_STATUS = (
        "queued",   # in the list of runs to run (oper data)
        "started",  # by HFR but no GHA run started
        "waiting",  # for a testbed
        "running",  # on a testbed
        "finished", # correctly (not important how many tests passed or failed)
        "canceled"  # by GHA (e.g. timeout) or HFR
    )
    HFR_RUN_DONE = (
        "finished",
        "canceled"
    )
    HFR_RUN_INITIAL_STATUS = "queued"

    # GitHub Actions statuses and conclusions.
    GHA_STATUSES = (
        "queued",      # The run is waiting for a runner to become available.
        "in_progress", # The run is currently executing.
        "completed",   # The run has finished executing all jobs and steps.
        "waiting",     # The run is paused, often for environment protection
                       # rules like manual approvals.
        "requested",   # Internal state indicating the run has been initiated.
        "pending"      # The run is in a preliminary state before it can be
                       # queued.
    )
    GHA_CONCLUSIONS = (
        "success",         # All jobs completed successfully.
        "failure",         # At least one job or a required step failed.
        "cancelled",       # The run was manually stopped or terminated by a
                           # concurrency rule.
        "skipped",         # The run or its jobs were not executed due to
                           # conditional logic.
        "timed_out",       # The run exceeded its maximum allowed execution
                           # time.
        "action_required", # The run finished but needs a manual external action
                           # to proceed.
        "neutral",         # The run completed with a result that is neither a
                           # success nor failure (treated as success for
                           # dependent checks).
        "stale",           # Marked by GitHub if a run loses connection or takes
                           # too long to report back.
        "startup_failure"  # The run failed during the initial setup phase
                           # before any jobs could start. 
    )
