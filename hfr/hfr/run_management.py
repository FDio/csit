"""Run management
"""


import logging

from datetime import datetime, timezone

from hfr.app_configuration import AppConfiguration
from hfr.intf_gha import Gha
from hfr.intf_tb import Testbed, Testbeds
from hfr.oper_data import OperData, Run


class RunManagement:
    """Run Management
    """

    def __init__(self, app_conf: AppConfiguration, oper: OperData, gha: Gha,
                 tbs: Testbeds):
        """Initialization.
        """

        self._app_conf = app_conf
        self._oper = oper
        self._gha = gha
        self._tbs = tbs

        self._runs_count = len(self._oper.data)
        self._runs_done = 0

        self._states_map = {
            "queued": self._queued,
            "started": self._started,
            "waiting": self._waiting,
            "running": self._running,
            "cancelled": self._cancelled,
            "finished": self._finished
        }

        logging.info("Run management started successfully.")

    @staticmethod
    def _generate_id():
        """Based on the timestamp.

        :returns: Last ten digits of the timestamp as a string.
        :rtype: str
        """
        id = str(int(datetime.now(timezone.utc).timestamp() * 1e6))
        return id[-10:]

    def _get_free_tb(self, node: str) -> Testbed:
        """Get a free testbed of given node-arch. It searches in the previously
            populated list of testbeds, it does not checks the testbeds. It is
            done so to save time. The first available is returned. If there is
            no available testbed, returns None.

        :param node: The node-arch (e.g. 2n-emr) of the testbed.
        :type node: str
        :returns: An available testbed or None.
        :rtype: Testbed
        """
        for tb in self._tbs.testbeds:
            if node == tb.node and tb.status == "available":
                return tb
        else:
            return None

    def _get_my_tb(self, run: Run) -> Testbed:
        """Get the testbed where the "run" is running.
        """
        for tb in self._tbs.testbeds:
            if run.node == tb.node and tb.status == "reserved":
                if run.data.gha_data.get("id", str()) == tb.run_id:
                    return tb
        else:
            return None

    def _to_start(self, run: Run) -> bool:
        """Start the run.
        """
        ret_val = self._gha.start_run(run)
        return ret_val[0]

    def _run_status(self, run: Run) -> tuple:
        """Return the run status, conclusion, and the run operational data.
        """
        status, data = self._gha.get_run_status(run)
        if status:  
            return data.get("status", None), data.get("conclusion", None), data
        else:
            return None, None, None

    def _to_cancel(self, run: Run) -> bool:
        """Cancel the run.
        """
        ret_val = self._gha.cancel_run(run)
        return ret_val[0]

    @staticmethod
    def _print_run(run: Run):
        # Only for the development. To be removed
        id = f"{run.node}-{run.data.hfr_id}" if run.data.hfr_id else run.node
        logging.info(f"{id}: {run.data.hfr_status}")

    # States

    def _queued(self, run: Run):
        """HFR run state: queued.

        Possible transitions:
        1. queued -> queued
           - if there is no accessible testbed
        2. queued -> started
           - if there is an accessible testbed
        
        Procedure:
        1. Find testbed
        2. If testbed, start run, otherwise return
        3. change status to "started"

        :param run: The run to be manipulated.
        :type run: Run
        """

        # Find an available testbed
        free_tb = self._get_free_tb(run.node)
        if not free_tb:
            return

        # Pre-reserve the testbed. Keep in mind that another testbed can be used
        # by this run, this is just to mark that one testbed (of this topo-arch)
        # will be used.
        free_tb.status = "pre-reserved"
        run.tb = free_tb  # Could be replaced later.
        # Set the parameters of a run - ID.
        run.data.hfr_id = self._generate_id()
        run.conf.inputs["my_run_id"] = run.data.hfr_id
        # Start the run
        started = self._to_start(run)
        if started:
            run.data.hfr_status = "started"

    def _started(self, run: Run):
        """HFR run state: started in GHA but not running.

        Possible transitions:
        1. started -> started
           - If the run is not running in GHA.
        2. started -> waiting
           - The run is running in GHA but it is waiting for a testbed. 
        3. started -> finished
           - If the run finished.
        4. started -> canceled
           - If the run was canceled either by GHA, HFR or manually.

        :param run: The run to be manipulated.
        :type run: Run
        """

        status, conclusion, run.data.gha_data = self._run_status(run)
        if status == "in_progress":
            run.data.hfr_status = "waiting"  # for a testbed
        elif status == "completed":
            if conclusion == "cancelled":
                run.data.hfr_status = "cancelled"
            else:
                run.data.hfr_status = "finished"
        # else: The run remains in the state "started".

    def _waiting(self, run: Run):
        """HFR run state: waiting for a testbed.
        
        Possible transitions:
        1. waiting -> waiting
           - Still waiting for a testbed.
        2. waiting -> running
           - Running on a testbed.
        3. waiting -> finished
           - If the run finished.
        4. waiting -> canceled
           - If the run was canceled either by GHA or HFR.

        :param run: The run to be manipulated.
        :type run: Run
        """

        status, conclusion, run.data.gha_data = self._run_status(run)
        if status == "in_progress":
            # Check the TBs. If the run is on a testbed, change state to
            # "running", otherwise keep the state as it is.
            my_tb = self._get_my_tb(run)
            if my_tb:
                run.tb.status = "available"
                run.tb = my_tb
                run.data.hfr_status = "running"
        elif status == "completed":
            if conclusion == "cancelled":
                run.data.hfr_status = "cancelled"
            else:
                run.data.hfr_status = "finished"
        # else: The run remains in the state "waiting".

    def _running(self, run: Run):
        """HFR run state: running on a testbed.

        Possible transitions:
        1. running -> running
           - If the run still runs on the testbed (no change in TB nor
             GHA status)
        2. running -> canceled
           - If the run was canceled either by GHA or HFR.
        3. running -> finished
           - If the run finished.

        :param run: The run to be manipulated.
        :type run: Run
        """

        status, conclusion, run.data.gha_data = self._run_status(run)
        if status == "completed":
            if conclusion == "cancelled":
                run.data.hfr_status = "cancelled"
            else:
                run.data.hfr_status = "finished"
        # else: The run remains in the state "running".
        
    def _cancelled(self, run: Run):
        """HFR run state: canceled (by GHA, HFR or manually).
        
        If "re-run" is enabled and the max count is not reached, change the
        status to"queued" and incerase the counter of runs. Otherwise change the
        status to "finished".

        :param run: The run to be manipulated.
        :type run: Run
        """

        if not self._app_conf.re_run_canceled or \
                run.data.nr_of_runs == self._app_conf.nr_of_re_runs:
            run.data.hfr_status = "finished"
        else:
            run.data.hfr_status = "queued"
            run.data.hfr_id = str()
            run.data.gha_data = dict()
            run.data.nr_of_runs += 1
            if run.tb.status == "pre-reserved":
                run.tb.status = "available"
            run.tb = None

    def _finished(self, run: Run):
        """HFR run state: finished.

        If the run is done, continue with the next one for the same node-arch.

        :param run: The run to be manipulated.
        :type run: Run
        """

        if run.tb.status == "pre-reserved":
            run.tb.status = "available"

        self._runs_done += 1

    def manage(self) -> bool:
        """Manage the runs.
        """

        # Update the status of testbeds
        self._tbs.check_testbeds()

        self._runs_done = 0
        for run in self._oper.data:
            RunManagement._print_run(run)
            try:
                self._states_map[run.data.hfr_status](run)
            except KeyError:
                raise RuntimeError(
                    f"The run status '{run.data.hfr_status}' is invalid."
                )

        # Write the operational data
        self._oper.to_json_file()

        # Write a subset of operational data to csv file.
        self._oper.to_csv_file()

        # If True, the HFR did all its work and can exit.
        return self._runs_done != self._runs_count
