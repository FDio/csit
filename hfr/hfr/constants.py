# Copyright (c) 2026 Cisco and/or its affiliates.
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

    GITHUB_REQUEST_TIMEOUT = 10 # seconds

    # Application configuration file.
    DEFAULT_PATH_CONFIG = "hfr/app_conf.yaml"

    # Interval between runs of job management in seconds.
    DEFAULT_SLEEP_INTERVAL = 30
    MIN_SLEEP_INTERVAL = 5
    MAX_SLEEP_INTERVAL = 3600

    # Run again the canceled runs?
    DEFAULT_RE_RUN_CANCELED = False
    DEFAULT_NR_OF_RE_RUNS = 3

    # Number of retries if the GHA does not provide data about a run
    # (e.g.: response = 404).
    DEFAULT_MAX_GHA_RETRIES = 3

    # Max waiting time for a testbed.
    DEFAULT_MAX_WAITING_TIME = 600  # minutes

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
        "running",  # on a testbed
        "finished", # correctly (not important how many tests passed or failed)
        "canceled"  # by GHA (e.g. timeout) or HFR
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

    # URL to logs for the robotframework.
    DEFAULT_RUN_LOG_URL = "https://logs.fd.io/vex-yul-rot-jenkins-1"
