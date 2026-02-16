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


"""Run management.
"""


import logging

from datetime import datetime, timedelta, timezone

from hfr.app_configuration import AppConfiguration
from hfr.intf_gha import Gha
from hfr.intf_tb import Testbed, Testbeds
from hfr.oper_data import OperData, Run


class RunManagement:
    """Run Management.
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
            "running": self._running,
            "cancelled": self._cancelled,
            "finished": self._finished
        }

        logging.info("Run management started successfully.")

    @staticmethod
    def _generate_id() -> str:
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
                if str(run.data.gha_data.get("id", str())) == tb.run_id:
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
            run.data.gha_retries = 0
            return data.get("status", None), data.get("conclusion", None), data
        else:
            run.data.gha_retries += 1
            return None, None, None

    def _to_cancel(self, run: Run) -> bool:
        """Cancel the run.
        """
        ret_val = self._gha.cancel_run(run)
        return ret_val[0]

    @staticmethod
    def _print_run(run: Run, prev_state: str=str()):
        """Print the 
        """
        if run.data.hfr_id:
            id = f"{run.conf.name}-{run.data.hfr_id}"
        else:
            id = run.conf.name
        logging.debug(f"{id}: {prev_state} -> {run.data.hfr_status}")

    @staticmethod
    def _get_time_diff(run: Run) -> timedelta:
        """Get time diff between the time when the run started and UTC now.
        Write it to run data as [H]H:mm:ss and return timedelta object for
        further processing.
        """
        if not run.data.gha_data:
            return timedelta(minutes=0)
        r_date = run.data.gha_data.get("run_started_at", None)
        if r_date:
            dt_obj = datetime.fromisoformat(
                r_date.replace("Z","+00:00") if r_date.endswith("Z") else r_date
            )
            diff = datetime.now(timezone.utc) - dt_obj
            total_seconds = int(diff.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            run.data.hfr_duration = f"{hours}:{minutes:02}:{seconds:02}"
            return diff
        else:
            return timedelta(minutes=0)

    # States

    def _queued(self, run: Run):
        """HFR run state: queued.

        The run is in HFR queue to be started immediately when there is an
        available testbed for it.

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

        run.data.hfr_id = self._generate_id()

        # Pre-reserve the testbed. Keep in mind that another testbed can be used
        # by this run, this is just to mark that one testbed (of this topo-arch)
        # will be used.
        free_tb.status = "pre-reserved"
        free_tb.pre_reserved_by = run.data.hfr_id
        run.tb = free_tb  # Could be replaced later.

        # Set the parameters of a run - ID.
        run.conf.inputs["my_run_id"] = run.data.hfr_id

        # Start the run
        started = self._to_start(run)
        if started:
            run.data.hfr_status = "started"

    def _started(self, run: Run):
        """HFR run state: started in GHA but not running.

        The run is queued in GHA waiting for an executor.

        Possible transitions:
        1. started -> started
           - If the run is not running on GHA executor or it is waiting for
             a testbed.
        2. started -> running
           - The run is running on GHA executor and it is running on a testbed.
        3. started -> finished
           - If the run finished.
        4. started -> canceled
           - If the run was canceled either by GHA, HFR or manually.

        :param run: The run to be manipulated.
        :type run: Run
        """

        status, conclusion, data = self._run_status(run)

        if data:
            run.data.gha_data = data

        if run.data.gha_retries == self._app_conf.max_gha_retries:
            run.data.hfr_status = "finished"
            return

        if status == "in_progress":
            t_diff = RunManagement._get_time_diff(run)
            # Check the TBs. If the run is on a testbed, change state to
            # "running", otherwise keep the state as it is.
            my_tb = self._get_my_tb(run)
            if my_tb:
                if my_tb.name != run.tb.name:
                    # It is not the same testbed as pre-reserved.
                    if run.tb.status == "pre-reserved" \
                            and run.tb.pre_reserved_by == run.data.hfr_id:
                        run.tb.status = "available"
                    run.tb = my_tb
                run.data.hfr_status = "running"
            elif t_diff > self._app_conf.max_waiting_time:
                # Check the time diff and cancel the run if waiting too long.
                self._to_cancel(run)
            # else: The run remains in the state "waiting".
        elif status == "completed":
            if conclusion == "cancelled":
                run.data.hfr_status = "cancelled"
            else:
                run.data.hfr_status = "finished"
        # else: The run remains in the state "started".

    def _running(self, run: Run):
        """HFR run state: running on a testbed.

        The run is running on a testbed.

        Possible transitions:
        1. running -> running
           - If the run still runs on the testbed (no change in TB nor
             GHA status)
        2. running -> canceled
           - If the run was canceled either by GHA, HFR or manually.
        3. running -> finished
           - If the run finished.

        :param run: The run to be manipulated.
        :type run: Run
        """

        status, conclusion, data = self._run_status(run)

        if data:
            run.data.gha_data = data

        if run.data.gha_retries == self._app_conf.max_gha_retries:
            run.data.hfr_status = "finished"
            return

        RunManagement._get_time_diff(run)

        if status == "completed":
            if conclusion == "cancelled":
                run.data.hfr_status = "cancelled"
            else:
                run.data.hfr_status = "finished"
        # else: The run remains in the state "running".

    def _cancelled(self, run: Run):
        """HFR run state: canceled (by GHA, HFR or manually).

        The run has been canceled either by GHA, HFR or manually.

        If "re-run" is enabled and the max count is not reached, change the
        status to "queued" and incerase the counter of runs. Otherwise change
        the status to "finished".

        :param run: The run to be manipulated.
        :type run: Run
        """

        if not self._app_conf.re_run_canceled or \
                run.data.nr_of_runs == self._app_conf.nr_of_re_runs:
            # No (more) re-runs, finish the run.
            run.data.hfr_status = "finished"
        else:
            # Clean the operational data of this particular run and queue it
            # again.
            if run.tb.status == "pre-reserved" \
                    and run.tb.pre_reserved_by == run.data.hfr_id:
                run.tb.status = "available"
            run.tb = None
            run.data.hfr_status = "queued"
            run.data.hfr_id = str()
            run.data.hfr_duration = 0
            run.data.gha_data = dict()
            run.data.nr_of_runs += 1

    def _finished(self, run: Run):
        """HFR run state: finished.

        The run finished, clean everything.

        :param run: The run to be manipulated.
        :type run: Run
        """

        if run.tb.status == "pre-reserved" \
                and run.tb.pre_reserved_by == run.data.hfr_id:
            run.tb.status = "available"

        # Increase the counter of runs of this particular run.
        run.data.nr_of_runs += 1

        # Increase the counter of done runs.
        self._runs_done += 1

    def manage(self) -> bool:
        """Manage the runs.
        """

        # Update the status of testbeds
        self._tbs.check_testbeds()

        # Get the status of runs and manage them.
        self._runs_done = 0
        for run in self._oper.data:
            old_status = run.data.hfr_status
            try:
                self._states_map[run.data.hfr_status](run)
            except KeyError:
                raise RuntimeError(
                    f"The run status '{run.data.hfr_status}' is invalid."
                )
            RunManagement._print_run(run, old_status)

        # Write the operational data to the JSON file.
        self._oper.to_json_file()

        # Write a subset of operational data to the CSV file.
        self._oper.to_csv_file()

        # Write the current state of testbeds to the CSV file.
        self._tbs.to_tb_csv_file()

        # If True, the HFR did all its work and can exit.
        return self._runs_done != self._runs_count
