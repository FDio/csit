"""
Interface to testbeds
=====================

Structure
---------

[
    Testbed(
        name=str,
        node=str,
        tg=dict,
        status=str,
        job=str,
        run_id=str
    ),

    ...
]

Testbed
- name - The name of the testbed as it is defined in its topology file.
- node - node-arch identificator, e.g.: 2n-spr.
- tg - All information about the tb's traffic generator as it is defined in the
  topology file. This information is used to communicate with the testbed.
- status - The status of the testbed:
  - available,
  - pre-reserved (by HFR),
  - reserved,
  - unreachable.
- job - the job name (only for status == reserved, otherwise None).
- run_id - The ID of a run (only for status == reserved, otherwise None).

"""


import logging

from dataclasses import dataclass
from glob import glob
from yaml import load, FullLoader, YAMLError

from hfr.ssh import exec_cmd


@dataclass
class Testbed:
    """Information about a testbed.
    """
    name: str = None
    node: str = None
    tg: dict = None
    status: str = None
    job: str = None
    run_id: str = None


class Testbeds:
    """Information about all testbeds.
    """

    CMD_LS = "ls /tmp/reservation_dir/"
    CMD_RM = "rm -rf /tmp/reservation_dir/"

    def __init__(self, app_conf):
        """Initialization.
        """
        
        self._app_conf = app_conf
        self._path = self._app_conf.path_to_tbs

        self._tbs = self._get_testbeds()

    def _check_tb(self, tg):
        """Check the status of a single testbed.

        :param tg: Traffic generator node of the testbed.
        :type tg: dict
        :returns: status of the testbed, job which is running on it and the run
            ID.
        :rtype: tuple(str, str, str)
        """

        job = None
        run_id = None
        logging.getLogger().setLevel("ERROR")
        try:
            ret_code, stdout, _ = exec_cmd(
                tg,
                cmd=Testbeds.CMD_LS,
                timeout=60,
                disconnect=True
            )
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
        finally:
            logging.getLogger().setLevel(self._app_conf.logging_level)

        return status, job, run_id

    def _get_testbeds(self):
        """Read the information about testbeds from their topology files and get
        their current status.

        :returns: List of testbeds.
        :rtype: list
        """
        logging.info("Getting initial information about testbeds:")
        
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

        logging.info("Done.")

        return tbs

    def check_testbeds(self, node=None):
        """Get the current status of the testbed(s).

        :param node: The node, not the particular testbed, you are interested
            in.
        :type node: str
        :returns: Status of the testbed, job which is running on it and the run
            ID.
        :rtype: tuple(str, str, str)
        """
        for tb in self._tbs:
            if node and node != tb.node:
                continue
            # Get info from a testbed
            tb.status, tb.job, tb.run_id = self._check_tb(tb.tg)
            logging.info(f"Checking {tb.name} - {tb.status}")

    def check_testbed(self, tb):
        """Get the current status of the testbed.

        :param tb: The particular testbed, you are interested in.
        :type tb: str
        :returns: Status of the testbed, job which is running on it and the run
            ID.
        :rtype: tuple(str, str, str)
        """
        tb.status, tb.job, tb.run_id = self._check_tb(tb.tg)

    def get_free_tb(self, node):
        """Get a free testbed of the defined node.

        :param node: The node, not the particular testbed, you are interested
            in.
        :type node: str
        :returns: A free testbed, if there is no free testbed, returns None.
        :rtype: Testbed
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
        else:
            return None

    def unreserve_tb(self, node):
        """Unreserve the testbed.

        :param tg: Traffic generator node of the testbed.
        :type tg: dict
        """

        status = False
        logging.getLogger().setLevel("ERROR")
        try:
            ret_code, _, _ = exec_cmd(
                node,
                cmd=Testbeds.CMD_RM,
                timeout=60,
                disconnect=True
            )
            if ret_code == 0:
                status = True
        except (TimeoutError, OSError) as err:
            logging.error(err)
        finally:
            logging.getLogger().setLevel(self._app_conf.logging_level)

        return status

    @property
    def testbeds(self):
        """Return the list of all testbeds.
        :rtype: list
        """
        return self._tbs
