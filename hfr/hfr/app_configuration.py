"""Application configuration.

The application configuration is read from two sources:
1. environment
2. configuration file.

All listed parameters are mandatory if it is not marked "optional".

1. Environment
   - GITHUB_URL
   - GITHUB_ACCOUNT
   - GITHUB_REPO
   - GITHUB_PAT
   - PATH_CONFIG

2. Configuration file
   - logging_level
   - sleep_interval
   - job_config - path to the job configuration file
   - oper_data - path to the operational data.
   - keep_old_oper_data (optional)
   - dir_testbeds - path to the testbeds specifications

Structure of aplication configuration data:

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
        "job_config": str,
        "oper_data": str,
        "keep_old_oper_data": bool,
        "dir_testbeds": str
    }
}

"""


import logging
import os

from yaml import load, FullLoader, YAMLError

from hfr.constants import Constants as C


class AppConfiguration:
    """Read, validate and provide the application configuration.
    """

    def __init__(self):
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
                self._conf["app"]["sleep_interval"] = sleep_interval
            except ValueError as err:
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
            # Job configuration file.
            if not self._conf["app"].get("job_config", None):
                valid = False
                logging.error("The path to job configuration must be defined.")
            # Operational data file.
            if not self._conf["app"].get("oper_data", None):
                valid = False
                logging.error("The path to job configuration must be defined.")
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
                f"An error occurred while parsing the application configuration"
                f" file {self._conf['app']['path_config']}\n"
                f"{err}"
            )
        
        self._validate_conf(conf_source="file")

        logging.debug(self._conf)

    @property
    def conf(self):
        """Application configuration.
        :rtype: dict
        """
        return self._conf
    
    @property
    def logging_level(self):
        """Logging level
        :rtype: str
        """
        return self._conf["app"]["logging_level"]
    
    @property
    def sleep_interval(self):
        """Interval between runs of job management in seconds.
        :rtype: int
        """
        return self._conf["app"]["sleep_interval"]
    
    @property
    def github(self):
        """GitHub parameters.
        :rtype: dict
        """
        return self._conf["github"]
    
    @property
    def job_config_file(self):
        """Path to the job configuration file.
        :rtype: str
        """
        return self._conf["app"]["job_config"]

    @property
    def path_to_tbs(self):
        """Path to the testbeds configuration files.
        :rtype: str
        """
        return self._conf["app"]["dir_testbeds"]
    
    @property
    def path_to_oper(self):
        """Path to the operational data.
        :rtype: str
        """
        return self._conf["app"]["oper_data"]
    
    @property
    def keep_old_oper_data(self):
        """Keep the file with old operational data and use it.
        :rtype: bool
        """
        return self._conf["app"].get("keep_old_oper_data", False)
