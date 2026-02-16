"""
Hands-free releasing
====================

"""


import logging

from time import sleep

from hfr.app_configuration import AppConfiguration
from hfr.job_configuration import JobConfiguration
from hfr.job_management import JobManagement
from hfr.oper_data import OperData
from hfr.intf_gha import Gha
from hfr.intf_tb import Testbeds



def main():
    """Hands-free releasing
    """

    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level="DEBUG"
    )

    logging.info("Starting HFR...")

    # Read the app configuration
    app_conf = AppConfiguration()
    try:
        app_conf.read_conf()
    except RuntimeError as err:
        logging.error(err)
        logging.critical("Exit.")
        return

    # Set the logging
    logging.getLogger().setLevel(app_conf.logging_level)

    # Read the jobs configuration
    jobs = JobConfiguration(app_conf.job_config_file)
    try:
        jobs.read_conf()
    except RuntimeError as err:
        logging.error(err)
        logging.critical("Exit.")
        return
    
    # logging.info(jobs.runs)

    # Get the testbeds, their properties and initial status
    tbs = None
    try:
        tbs =  Testbeds(app_conf=app_conf)
    except RuntimeError as err:
        logging.error(err)
        logging.critical("Exit.")
        return
    
    # logging.info(tbs.testbeds)

    # Initialize interface to GHA
    gha = Gha(app_conf=app_conf)

    # Initialize operational data
    try:
        oper = OperData(
            app_conf=app_conf,
            jobs = jobs
        )
    except RuntimeError as err:
        logging.error(err)
        logging.critical("Exit.")
        return
    
    # logging.info(oper.data)

    # status, data = gha.get_run_status(oper.data[0])

    # status, data = gha.start_run(oper.data[0])
    # logging.info(status)
    # logging.info(data)



    # tbs.check_testbeds("2n-spr")

    # free_tb = tbs.get_free_tb("2n-icx")
    # free_tb = tbs.get_free_tb("2n-icx")

    # Manage the jobs
    job_manager = JobManagement(oper=oper, tbs=tbs)

    while True:
        try:
            if not job_manager.manage():
                break
        except RuntimeError as err:
            logging.error(err)
            logging.critical("Exit.")
            return

        sleep(app_conf.sleep_interval)


if __name__ == "__main__":
    main()
