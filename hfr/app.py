"""
Hands-free releasing
====================

"""


import logging

from time import sleep

from hfr.app_configuration import AppConfiguration
from hfr.run_configuration import RunConfiguration
from hfr.run_management import RunManagement
from hfr.oper_data import OperData
from hfr.intf_gha import Gha
from hfr.intf_tb import Testbeds


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

    iteration = 1  # Only for the demo
    while True:
        logging.info(f"Iteration: {iteration}")  # Only for the demo
        try:
            if not run_manager.manage():
                break
        except RuntimeError as err:
            logging.error(err)
            logging.critical("Exit.")
            return

        sleep(2)  # Only for the demo
        iteration += 1  # Only for the demo
        # sleep(app_conf.sleep_interval)


if __name__ == "__main__":
    main()
