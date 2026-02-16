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
Hands-free releasing
====================

Automation of the CSIT release flow so that a single action drives a fully
automated pipeline.

Implementation of a hands-free release pipeline based on the existing CSIT
codebase and CI automation (GitHub Actions), such that releases are:
- Triggered by a human who defines the parameters of hands-free release process
- Fully automated from triggering to publishing artefacts
- Producing machine- and human-readable, structured and shareable outputs
  (artefacts, logs, reports, release notes)

The hands-free release pipeline must be usable in all environments which use
GitHub Actions and CSIT test framework.
"""


import logging

from time import sleep

from hfr.app_configuration import AppConfiguration
from hfr.intf_gha import Gha
from hfr.intf_tb import Testbeds
from hfr.run_configuration import RunConfiguration
from hfr.run_management import RunManagement
from hfr.oper_data import OperData


def main():
    """Hands-free releasing.
    """

    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level="DEBUG"
    )

    logging.info("Starting HFR...")

    # Read the app configuration.
    app_conf = AppConfiguration()
    try:
        app_conf.read_conf()
    except RuntimeError as err:
        logging.error(err)
        logging.critical("Exit.")
        return

    # Set the logging.
    logging.getLogger().setLevel(app_conf.logging_level)

    # Read the jobs configuration.
    runs = RunConfiguration(app_conf.run_config_file)
    try:
        runs.read_conf()
    except RuntimeError as err:
        logging.error(err)
        logging.critical("Exit.")
        return

    # Get the testbeds, their properties and initial status.
    tbs = None
    try:
        tbs =  Testbeds(app_conf=app_conf)
    except RuntimeError as err:
        logging.error(err)
        logging.critical("Exit.")
        return

    # Initialize interface to GHA.
    gha = Gha(app_conf=app_conf)

    # Initialize operational data.
    try:
        oper = OperData(app_conf=app_conf, runs=runs)
    except RuntimeError as err:
        logging.error(err)
        logging.critical("Exit.")
        return

    # Manage the runs.
    run_manager = RunManagement(app_conf=app_conf, oper=oper, gha=gha, tbs=tbs)

    if app_conf.logging_level == "DEBUG":
        iteration = 1

    while True:

        if app_conf.logging_level == "DEBUG":
            logging.debug(f"Iteration: {iteration}")
            iteration += 1

        try:
            if not run_manager.manage():
                break
        except RuntimeError as err:
            logging.error(err)
            logging.critical("Exit.")
            return

        sleep(app_conf.sleep_interval)

    logging.info("Run management finished.")


if __name__ == "__main__":
    main()
