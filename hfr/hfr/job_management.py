"""

"""


import logging

from datetime import datetime, timezone

from hfr.constants import Constants as C
from hfr.intf_tb import Testbeds
from hfr.oper_data import OperData, Run

class JobManagement:
    """
    Docstring for JobManagement
    """

    def __init__(self, oper: OperData, tbs: Testbeds):
        """
        """
        self._oper = oper
        self._tbs = tbs

        self._runs_count = len(self._oper.data)
        self._runs_done = 0

        logging.info("Job management started successfully.")

    @staticmethod
    def _generate_id():
        """Based on timestamp.

        :returns: Last ten digits of the timestamp.
        :rtype: str
        """
        id = str(int(datetime.now(timezone.utc).timestamp() * 1e6))
        return id[-10:]

    def _to_start(self, run: Run) -> bool:
        """
        """
        ret_val = False
        return ret_val

    def _is_running(self, run: Run) -> bool:
        """
        """
        ret_val = False
        return ret_val

    def manage(self) -> bool:
        """
        """

        logging.info("I am still alive!")

        self._runs_done = 0
        for run in self._oper.data:
            # If the run is done, continue with the next one.
            if run.data.hfr_status in C.HFR_RUN_DONE:
                self._runs_done += 1
                continue

            if run.data.hfr_status == "queued":
                # Possible transitions:
                # 1. queued -> queued
                #    - if there is no accessible testbed
                # 2. queued -> started
                #    - if there is an accessible testbed
                #
                # Procedure:
                # 1. Find testbed
                # 2. If testbed, start run, otherwise continue
                # 3. change status to "started"

                # Find an available testbed
                pass

                # Set the parameters of a run - ID, ...

                # Start the run
                status = self._to_start(run)

                # Check the status
                pass

            elif run.data.hfr_status == "started":
                # Possible transitions:
                # 1. started -> started
                #    - If the run does not have its testbed.
                # 2. started -> running
                #    - If the run has its testbed.
                #
                # Procedure:
                # 1. Check if the run is on the testbed.
                # 2. If on the testbed, change the ststus to "running".
                # 3. Otherwise continue

                # Check the run in GHA
                status = self._is_running(run)

                # Check the TB
                # tb_status = 

                # Evaluate and set the parametres of the run
                pass

            elif run.data.hfr_status == "running":
                # Possible transitions:
                # 1. running -> running
                #    - If the run still runs on the testbed (no change in TB nor
                #      GHA status)
                # 2. running -> canceled
                #    - If the run was canceled either by GHA or HFR.
                # 3. running -> finished
                #    - If the run finished.
                #
                # Procedure:
                # 1. Check the ru ststus in GHA.
                # 2. If running, continue.
                # 3. If canceled, change the status to canceled.
                # 4. If finished, change the status to finished.
                # 5. If canceled or finished, check the stsus of the testbed, if
                #    neccessary un-reserve the testbed.

                # Check the GHA
                pass

                # Check the TB ???
                pass

                # Evaluate and set the parameters of the run
                pass

            else:
                raise RuntimeError(
                    f"The run status '{run.data.hfr_status}' is invalid."
                )

        # Write the operational data
        self._oper.to_json_file()

        return self._runs_done == self._runs_count
