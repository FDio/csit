"""
"""


import logging

from dataclasses import dataclass
from glob import glob
from yaml import load, FullLoader, YAMLError

from hfr.constants import Constants as C
from hfr.ssh import exec_cmd

USE_TBS = True

@dataclass
class Testbed:
    """
    """
    name: str = None
    node: str = None
    tg: str = None
    status: str = None
    job: str = None
    run_id: str = None


class Testbeds:
    """
    """

    CMD_LS = "ls /tmp/reservation_dir/"

    def __init__(self, app_conf):
        """
        """
        
        self._app_conf = app_conf
        self._path = self._app_conf.path_to_tbs

        self._tbs = self._get_testbeds()

    def _check_tb(self, tg):
        """
        """
        job = None
        run_id = None
        try:
            if USE_TBS:
                logging.getLogger().setLevel("ERROR")
                ret_code, stdout, _ = exec_cmd(
                    tg,
                    cmd=Testbeds.CMD_LS,
                    timeout=60,
                    disconnect=True
                )
                logging.getLogger().setLevel(self._app_conf.logging_level)
            else:
            # ---
            # For testing purposes only, to be removed:
                if tg["host"] == "10.30.51.57":
                    ret_code = 0
                    stdout = "csit-vpp-perf-mrr-daily-master-2n-spr-21885288042"
                elif tg["host"] == "10.30.51.77":
                    ret_code = 0
                    stdout = "csit-vpp-perf-mrr-daily-master-3n-icx-21885288042"
                elif tg["host"] == "10.30.51.89":
                    ret_code = 0
                    stdout = "dead"
                elif tg["host"] == "10.30.51.90":
                    raise TimeoutError(
                        "Unable to connect to port 6001 on 10.30.51.90"
                    )
                else:
                    ret_code = 2
                    stdout = ""
            # ---

            if ret_code != 0:
                status = "available"
            else:
                status = "reserved"
                try:
                    job, run_id = stdout.strip().rsplit("-", maxsplit=1)
                except (ValueError, IndexError):
                    pass
        except (TimeoutError, OSError) as err:
            logging.error(err)
            status = "unreachable"

        return status, job, run_id

    def _get_testbeds(self):
        """
        """
        logging.info("Getting initial information about and from testbeds:")
        
        tb_files = sorted(glob(f"{self._path}/*.yaml", recursive=True))        
        if not tb_files:
            raise RuntimeError(
                f"There are no topolopgy files in '{self._path}'."
            )

        tbs = list()
        for file_name in tb_files:
            logging.info(file_name)
            tb_name = file_name.split("/")[-1].replace(".yaml", "")
            tb = Testbed(
                name=tb_name,
                node="-".join(tb_name.split("_")[1:3])
            )

            # Read the YAML file with info about the test bed:
            try:
                with open(file_name, "r") as file_read:
                    tb_info = load(file_read, Loader=FullLoader)
            except IOError as err:
                logging.error(
                    f"Not possible to open the file {file_name}\n{err}"
                )
                continue
            except YAMLError as err:
                logging.error(
                    f"An error occurred while parsing the topology file "
                    f"{file_name}\n{err}"
                )
                continue

            tb.tg = tb_info["nodes"]["TG"]

            # Get info from a testbed
            tb.status, tb.job, tb.run_id = self._check_tb(tb.tg)
            tbs.append(tb)

        return tbs

    def check_testbeds(self, node=None):
        """
        """
        for tb in self._tbs:
            if node and node != tb.node:
                continue
            logging.debug(f"Checking {tb.name} - {tb.status}")
            # Get info from a testbed
            tb.status, tb.job, tb.run_id = self._check_tb(tb.tg)

    def get_free_tb(self, node):
        """
        """
        for tb in self._tbs:
            if node and node != tb.node:
                continue
            logging.debug(f"Checking {tb.name} - {tb.status}")
            if tb.status == "pre-reserved":
                continue
            tb.status, tb.job, tb.run_id = self._check_tb(tb.tg)
            if tb.status == "available":
                tb.status = "pre-reserved"
                return tb

    @property
    def testbeds(self):
        return self._tbs
