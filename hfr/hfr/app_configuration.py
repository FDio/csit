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


"""
Application configuration
=========================

The application configuration is read from two sources:
1. environment
2. configuration file.

All listed parameters are mandatory if it is not marked "optional".

1. Environment
   - GITHUB_URL (optional)
   - GITHUB_ACCOUNT (optional)
   - GITHUB_REPO (optional)
   - GITHUB_PAT
   - PATH_CONFIG (optional)

2. Configuration file
   - logging_level
   - sleep_interval
   - re_run_canceled (optional) - run again cancelled runs
   - nr_of_re_runs (optional) - number of re-runs of cancelled runs
   - max_waiting_time (optional) - max time while a run waits for a testbed
   - run_config - path to the run configuration file
   - oper_data - path to the operational data
   - csv_data - a path to the csv file to save selected parameters
   - testbed_data - a path to the csv file to save the current state of testbeds
   - run_log_url (optional) - base URL to run logs
   - keep_old_oper_data (optional)
   - dir_testbeds - path to the testbeds specifications

Structure of application configuration data after processing
------------------------------------------------------------

{
    "github": {
        "url": str,
        "account": str,
        "repo": str,
        "pat": str
    },
    "app": {
        "path_config": str,
        "logging_level": str,
        "sleep_interval": int,
        "re_run_canceled": bool,
        "nr_of_re_runs": int,
        "max_waiting_time": int,
        "run_config": str,
        "oper_data": str,
        "testbed_data": str,
        "run_log_url": str,
        "keep_old_oper_data": bool,
        "dir_testbeds": str
    }
}

"""


import logging
import os

from datetime import timedelta
from yaml import load, FullLoader, YAMLError

from hfr.constants import Constants as C


class AppConfiguration:
    """Read, validate and provide the application configuration.
    """

    def __init__(self):
        """Initialization.
        """
        self._conf = {
            "github": dict(),
            "app": dict()
        }

    def _validate_conf(self, conf_source: str):
        """Validate the read configuration.

        :param conf_source: The source of configuration, either environment or
            configuration file. The valid values are:
            - env
            - file
        :type conf_source: str
        :raises RuntimeError: if a parameter is missing or it is invalid.
        """

        valid = True

        # Validate parameters read from the environment.
        if conf_source == "env":
            for key, val in self._conf["github"].items():
                if not val:
                    valid = False
                    logging.error(
                        f"The value of 'GITHUB_{key.upper()}' must be defined "
                        f"in the environment."
                    )
            if not self._conf["app"]["path_config"]:
                valid = False
                logging.error(
                    "The value of 'PATH_CONFIG' must be defined in the "
                    "environment."
                )
        # Validate parameters read from the configuration file.
        elif conf_source == "file":
            # Logging level.
            log_level = \
                self._conf["app"].get("logging_level", C.DEFAULT_LOG_LEVEL)
            if log_level not in C.LOGGING_LEVEL:
                logging.warning(
                    f"The logging level '{log_level}' is incorrect, will be set"
                    f" to '{C.DEFAULT_LOG_LEVEL}'."
                )
                self._conf["app"]["logging_level"] = C.DEFAULT_LOG_LEVEL
            # Sleep interval.
            sleep_interval = \
                self._conf["app"].get("sleep_interval",C.DEFAULT_SLEEP_INTERVAL)
            try:
                sleep_interval = int(sleep_interval)
                if sleep_interval < C.MIN_SLEEP_INTERVAL or \
                        sleep_interval > C.MAX_SLEEP_INTERVAL:
                    logging.warning(
                        f"The sleep interval '{sleep_interval}' is out of the "
                        f"range from {C.MIN_SLEEP_INTERVAL} to "
                        f"{C.MAX_SLEEP_INTERVAL}, will be set to "
                        f"{C.DEFAULT_SLEEP_INTERVAL}"
                    )
                    sleep_interval = C.DEFAULT_SLEEP_INTERVAL
                self._conf["app"]["sleep_interval"] = sleep_interval
            except ValueError:
                logging.warning(
                    f"The 'sleep_interval = {sleep_interval}' is incorrect, "
                    f"will be set to {C.DEFAULT_SLEEP_INTERVAL}"
                )
                self._conf["app"]["sleep_interval"] = C.DEFAULT_SLEEP_INTERVAL
            # Testbeds topologies.
            if not self._conf["app"].get("dir_testbeds", None):
                valid = False
                logging.error(
                    "The path to testbeds configuration must be defined."
                )
            # Run configuration file.
            if not self._conf["app"].get("run_config", None):
                valid = False
                logging.error("The path to run configuration must be defined.")
            # Operational data file.
            if not self._conf["app"].get("oper_data", None):
                valid = False
                logging.error(
                    "The path to file with operational data must be defined."
                )
            # CSV data file.
            if not self._conf["app"].get("csv_data", None):
                valid = False
                logging.error("The path to file with CSV data must be defined.")
            # CSV testbed file.
            if not self._conf["app"].get("testbed_data", None):
                valid = False
                logging.error(
                    "The path to file with CSV testbed data must be defined."
                )
            # Base URL to run logs.
            if not self._conf["app"].get("run_log_url", None):
                self._conf["app"]["run_log_url"] = C.DEFAULT_RUN_LOG_URL
            # Re-runs.
            if not self._conf["app"].get("re_run_canceled", None):
                self._conf["app"]["re_run_canceled"] = C.DEFAULT_RE_RUN_CANCELED
            if not self._conf["app"].get("nr_of_re_runs", None):
                self._conf["app"]["nr_of_re_runs"] = C.DEFAULT_NR_OF_RE_RUNS
            # GHA re-tries.
            if not self._conf["app"].get("max_gha_retries", None):
                self._conf["app"]["max_gha_retries"] = C.DEFAULT_MAX_GHA_RETRIES
            # Max waiting time for a testbed.
            diff = self._conf["app"].get("max_waiting_time", None)
            if diff:
                self._conf["app"]["max_waiting_time"] = timedelta(minutes=diff)
            else:
                self._conf["app"]["max_waiting_time"] = \
                    timedelta(minutes=C.DEFAULT_MAX_WAITING_TIME)

        # There is no other way.
        else:
            raise RuntimeError(
                f"The configuration method '{conf_source}' is not supported."
            )

        # Conclusion.
        if not valid:
            raise RuntimeError("The application configuration is not valid.")

    def read_conf(self):
        """Read the configuration from envoronment at first and then from
        specified configuration file.
        """

        logging.info("Reading the application configuration...")

        # Read the configuration from the environment.
        self._conf["github"] = {
            "url": os.getenv("GITHUB_URL", C.DEFAULT_GITHUB_URL),
            "account": os.getenv("GITHUB_ACCOUNT", C.DEFAULT_GITHUB_ACCOUNT),
            "repo": os.getenv("GITHUB_REPO", C.DEFAULT_GITHUB_REPO),
            "pat": os.getenv("GITHUB_PAT", C.DEFAULT_GITHUB_PAT)
        }
        self._conf["app"]["path_config"] = \
            os.getenv("PATH_CONFIG", C.DEFAULT_PATH_CONFIG)

        self._validate_conf(conf_source="env")

        # Read the configuration from the configuration file.
        try:
            with open(self._conf["app"]["path_config"], "r") as file_read:
                self._conf["app"].update(load(file_read, Loader=FullLoader))
        except IOError as err:
            raise RuntimeError(
                f"Not possible to open the file "
                f"{self._conf['app']['path_config']}\n {err}"
            )
        except YAMLError as err:
            raise RuntimeError(
                f"An error occurred while parsing the application "
                f"configuration file {self._conf['app']['path_config']}\n{err}"
            )

        self._validate_conf(conf_source="file")

        logging.debug(
            f"HFR configuration read from the environment and from the "
            f"configuration file '{self._conf['app']['path_config']}':\n"
            f"{self._conf}"
        )
        logging.info("Done.")

    @property
    def conf(self) -> dict:
        """Application configuration.
        :rtype: dict
        """
        return self._conf

    @property
    def logging_level(self) -> str:
        """Logging level.
        :rtype: str
        """
        return self._conf["app"]["logging_level"]

    @property
    def sleep_interval(self) -> int:
        """Interval between runs of the run management in seconds.
        :rtype: int
        """
        return self._conf["app"]["sleep_interval"]

    @property
    def github(self) -> dict:
        """GitHub parameters.
        :rtype: dict
        """
        return self._conf["github"]

    @property
    def run_config_file(self) -> str:
        """Path to the run configuration file.
        :rtype: str
        """
        return self._conf["app"]["run_config"]

    @property
    def path_to_tbs(self) -> str:
        """Path to the testbeds configuration files.
        :rtype: str
        """
        return self._conf["app"]["dir_testbeds"]

    @property
    def path_to_oper(self) ->str:
        """Path to the operational data.
        :rtype: str
        """
        return self._conf["app"]["oper_data"]

    @property
    def path_to_csv(self) -> str:
        """Path to the csv data.
        :rtype: str
        """
        return self._conf["app"]["csv_data"]

    @property
    def path_to_tb_csv(self) -> str:
        """Path to the csv testbed data.
        :rtype: str
        """
        return self._conf["app"]["testbed_data"]

    @property
    def log_url(self) -> str:
        """Base URL to run logs.
        :rtype: str
        """
        return self._conf["app"]["run_log_url"]

    @property
    def keep_old_oper_data(self) -> bool:
        """Keep the file with old operational data and use it.
        :rtype: bool
        """
        return self._conf["app"].get("keep_old_oper_data", False)

    @property
    def re_run_canceled(self) -> bool:
        """If True re-run the canceled runs.
        :rtype: bool
        """
        return self._conf["app"]["re_run_canceled"]

    @property
    def nr_of_re_runs(self) -> int:
        """Number of re-runs of the canceled runs.
        :rtype: str
        """
        return self._conf["app"]["nr_of_re_runs"]

    @property
    def max_waiting_time(self) -> timedelta:
        """Max waiting time for a testbed.
        :rtype: str
        """
        return self._conf["app"]["max_waiting_time"]

    @property
    def max_gha_retries(self) -> int:
        """Number of retries if the GHA does not provide data about a run.
        :rtype: str
        """
        return self._conf["app"]["max_gha_retries"]
