"""
"""


import logging
import os

from dataclasses import dataclass, asdict
from json import dump, load

from hfr.app_configuration import AppConfiguration
from hfr.job_configuration import JobConfiguration
from hfr.job_configuration import Run


@dataclass
class RunData:
    """
    """
    status: str  # queued, started, running, finished
    run_id: str  # generated and set by HFR
    gha_data: dict  # oper data from GHA


@dataclass
class OperItm:
    """
    """
    node: str
    run: Run
    data: RunData


class OperData:
    """
    """

    RUN_DATA_DEFAULTS = dict(
        status = "queued",
        run_id = str(),
        gha_data = dict()
    )

    def __init__(self, app_conf: AppConfiguration, jobs: JobConfiguration):
        """
        """
        self._app_conf = app_conf
        self._jobs = jobs

        if self._app_conf.keep_old_oper_data:
            self._data = self._from_json_file()
            if not self._data:
                self._initialize()
        else:
            self._initialize()

        self.to_json_file()

    def _from_json_file(self):
        """
        """

        # Read JSON file
        try:
            with(open(self._app_conf.path_to_oper, "rt") as fr):
                j_data = load(fr)
        except IOError as err:
            raise RuntimeError(
                f"Not possible to read from the file "
                f"'{self._app_conf.path_to_oper}'\n {err}"
            )

        # Deserialize
        return [
            OperItm(
                node=itm["node"],
                run=Run(**itm["run"]),
                data=RunData(**itm["data"]))
            for itm in j_data
        ]

    def to_json_file(self):
        """
        """
        # Serialize:
        s_data = [asdict(itm) for itm in self._data]

        # Write JSON file:
        try:
            directory = self._app_conf.path_to_oper.rsplit("/", maxsplit=1)[0]
            if not os.path.exists(directory):
                os.makedirs(directory)
            with(open(self._app_conf.path_to_oper, "wt") as fw):
                dump(s_data, fw)
        except IOError as err:
            raise RuntimeError(
                f"Not possible to write to the file "
                f"'{self._app_conf.path_to_oper}'\n {err}"
            )

    def _initialize(self):
        """
        """
        self._data = list()
        self._add_jobs()

    def _add_jobs(self):
        """
        """
        for node, runs in self._jobs.runs.items():
            for run in runs:
                self._data.append(OperItm(
                    node=node,
                    run=run,
                    data=RunData(**OperData.RUN_DATA_DEFAULTS)
                ))

    @property
    def data(self):
        return self._data
