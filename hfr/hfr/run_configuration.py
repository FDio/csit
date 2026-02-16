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
Run configuration
=================

The runs and their runs are defined in a YAML configuraton file, e.g.:

workflows:
  workflow_name_1:
    runs:
      - inputs:
          job_type: "iterative"
          dut: "vpp"
          node: "2n-icx"
          branch: "rls2602"
          suite_gen_params: "#2n-icx-vpp-iterative"
        params:
          prio: 1
          repeat: 10
      - inputs:
          job_type: "coverage"
          dut: "vpp"
          node: "2n-icx"
          branch: "rls2602"
          suite_gen_params:
            - "#2n-icx-vpp-cov-ip4-00"
            - "#2n-icx-vpp-cov-ip4-01"
            - "#2n-icx-vpp-cov-ip4-02"
            - "#2n-icx-vpp-cov-ip4-10"
            - "#2n-icx-vpp-cov-ip4-11"
            - "#2n-icx-vpp-cov-ip4tun-00"
            - "#2n-icx-vpp-cov-ip6-00"
            - "#2n-icx-vpp-cov-ip6-10"
            - "#2n-icx-vpp-cov-l2-00"
            - "#2n-icx-vpp-cov-l2-01"
            - "#2n-icx-vpp-cov-l2-10"
            - "#2n-icx-vpp-cov-l2-11"
            - "#2n-icx-vpp-cov-memif-00"
            - "#2n-icx-vpp-cov-memif-10"
            - "#2n-icx-vpp-cov-vhost-00"
            - "#2n-icx-vpp-cov-vhost-10"
        params:
          prio: 5
          repeat: 1
    parameters:
      # Use only parameters specified in 'inputs'
      name: "csit-{dut}-perf-report-{job_type}-{branch}-{node}"
      ref: "master"
      needed_params:  # Only for validation, but neccessary for report runs
        - "job_type"
        - "dut"
        - "node"
        - "branch"
        - "suite_gen_params"
parameters:
  queuing: "mixed"  #"sequential" or "mixed" or "random"

Top-level
---------

- workflows - defines workflows
- parameters - defines the way how the runs specified in this configuration file
  will be processed.

Workflows
.........

Each workflow has its runs and parameters.

runs:
- inputs - The variables and their values which are then passed to the workflow
  run. All inputs required by the workflow must be listed here. They are passed
  to the workflow whne it is started without any processing.
- params:
  - prio - priority of the run: 1 - highest priority, 9 - lowest priority.
  - repeat - how many times the run is run. Typicaly it is 1 for coverage jobs
    and 10 for iterative jobs. The valit value is for 1 to 20.

parameters:
- name - the name of a run as it is set in GHA workflow yaml file.
- ref - The branch with the workflow, usually "master".
- needed_params - the list of pararameters which must be present in 'inputs'
  section of each run in the workflow. Thie list is uosed to validate the run's
  definitions.

Parameters
..........

Parameters in this section sayhow the runs will be processed:
- queuing: one of "sequential", "mixed" or "random". This parameter says how the
  runs will be queued depending on their priority:
  - sequential - Runs are only sorted by priority, e.g. if there are 10 mrr and
    10 ndrpdr runs with the same priority we get list of 10 mrr runs followed
    by 10 ndrpdr runs.
  - mixed - Runs are sorted by priority and then the runs with the same priority
    are mixed, e.g. if there are 10 mrr and 10 ndrpdr runs with the same
    priority we get list: [mrr, ndrpdr, mrr, ndrpdr, ..., ndrpdr].
  - random - Runs with the same priority are queued randomly.

Run configuration after processing
----------------------------------

{
    "node_1": [
        Run(
            workflow=str,
            inputs={
                "job_type": str,
                "dut": str,
                "node": str,
                "branch": str,
                "suite_gen_params": str
            },
            "name": str,
            "ref": str
        ),
        Run(...),
        ...
    ],
    "node_2": list,
    ...
}

The runs are groupped by the node and sorted by the priority and the parameter
'queuing'.

"""

import logging

from copy import deepcopy
from dataclasses import dataclass
from itertools import zip_longest
from yaml import load, FullLoader, YAMLError

from hfr.constants import Constants as C


@dataclass
class RunConf:
    """A single run of a workflow.
    """
    workflow: str
    inputs: dict
    name: str
    ref: str


class RunConfiguration:
    """Run configuration.
    """

    RUN_DEFAULTS = dict(
        workflow = str(),
        inputs = dict(),
        name = str(),
        ref = str()
    )

    def __init__(self, config_file: str):

        self._conf_file = config_file

        self._raw_conf = dict()
        self._runs = dict()
        self._params = dict()

    def _validate_conf(self):
        """Validation of the run configuration.
        :raises RuntimeError: if a mandatory parameter is missing or if
            a parameter value is invalid.
        """
        if not self._raw_conf:
            raise RuntimeError(
                f"The run configuration file '{self._conf_file}' is empty."
            )
        wfs = self._raw_conf.get("workflows", None)
        if not wfs:
            raise RuntimeError(
                f"The run configuration file '{self._conf_file}' does not "
                f"include any workflows."
            )
        if not isinstance(wfs, dict):
            raise RuntimeError(
                f"The workflows in the configuration file "
                f"'{self._conf_file}' must be defined as a dictionary."
            )

        params = self._raw_conf.get("parameters", None)
        if not params:
            raise RuntimeError(
                f"The run configuration file '{self._conf_file}' does not "
                f"include any parameters."
            )
        if not isinstance(params, dict):
            raise RuntimeError(
                f"The parameters in the run configuration file "
                f"'{self._conf_file}' must be defined as a dictionary."
            )
        queuing = params.get("queuing", None)
        if not queuing:
            valid = False
            logging.error(
                f"The parameter 'queuing' must be defined in 'parameters'."
            )
        elif queuing not in C.QUEUING:
            valid = False
            logging.error(
                f"The parameter 'queuing' "
                f"must be one of {C.QUEUING}, not '{queuing}'."
            )

        valid = True
        for wf_name, wf_data in wfs.items():
            if not isinstance(wf_data, dict):
                valid = False
                logging.error(f"The workflow '{wf_name}' must be a dictionary.")
                continue
            runs = wf_data.get("runs", None)
            if not runs:
                valid = False
                logging.error(
                    f"There are no runs defined for the workflow '{wf_name}'."
                )
            if not valid:
                continue

            if not isinstance(runs, list):
                valid = False
                logging.error(
                    f"The runs for workflow '{wf_name}' must be defined "
                    f"as a list."
                )
            if not valid:
                continue

            params = wf_data.get("parameters", dict())
            needed_params = params.get("needed_params", None)
            if needed_params and not isinstance(needed_params, list):
                valid = False
                logging.error(
                    f"The parameter 'needed_params' for the workflow "
                    f"'{wf_name}' must be defined as a list."
                )
                continue

            if not params.get("name", None):
                valid = False
                logging.error(
                    f"The parameter 'name' for the workflow "
                    f"'{wf_name}' must be defined as a string."
                )
                continue

            if not params.get("ref", None):
                valid = False
                logging.error(
                    f"The parameter 'ref' for the workflow "
                    f"'{wf_name}' must be defined as a string."
                )
                continue

            for idx, run in enumerate(runs):
                params = run.get("params", None)
                if not params:
                    valid = False
                    logging.error(
                        f"The 'params' must be defined for run nr {idx} of the "
                        f"workflow {wf_name}."
                    )
                elif not isinstance(params, dict):
                    valid = False
                    logging.error(
                        f"The 'params' must be defined as a dictionary for run "
                        f"nr {idx} of the workflow {wf_name}."
                    )
                if valid:
                    prio = params.get("prio", None)
                    if not prio:
                        valid = False
                        logging.error(
                            f"The parameter 'prio' must be defined for the run "
                            f"nr {idx} of the workflow '{wf_name}'."
                        )
                    elif not isinstance(prio, int):
                        valid = False
                        logging.error(
                            f"The parameter 'prio' must be integer for the run "
                            f"nr {idx} of the workflow '{wf_name}'."
                        )
                    elif prio > C.MIN_PRIO or prio < C.MAX_PRIO:
                        valid = False
                        logging.error(
                            f"The parameter 'prio' must be from the range "
                            f"{C.MIN_PRIO} to {C.MAX_PRIO} for the run nr "
                            f"{idx} of the workflow '{wf_name}', not {prio}."
                        )
                    repeat = params.get("repeat", None)
                    if not repeat:
                        valid = False
                        logging.error(
                            f"The parameter 'repeat' must be defined for the "
                            f"run nr {idx} of the workflow '{wf_name}'."
                        )
                    elif not isinstance(repeat, int):
                        valid = False
                        logging.error(
                            f"The parameter 'repeat' must be integer for the "
                            f"run nr {idx} of the workflow '{wf_name}'."
                        )
                    elif repeat < C.MIN_REPEAT or repeat > C.MAX_REPEAT:
                        valid = False
                        logging.error(
                            f"The parameter 'repeat' must be from the range "
                            f"{C.MIN_REPEAT} to {C.MAX_REPEAT} for the run nr "
                            f"{idx} of the workflow '{wf_name}', not {repeat}."
                        )
                inputs = run.get("inputs", None)
                if not inputs:
                    continue
                if not isinstance(inputs, dict):
                    valid = False
                    logging.error(
                        f"The 'inputs' for the run nr {idx} of the workflow "
                        f"{wf_name} must be a dictionary."
                    )
                    continue
                if needed_params:
                    in_params = list(inputs.keys())
                    for np in needed_params:
                        if np not in in_params:
                            valid = False
                            logging.error(
                                f"The input '{np}' must be defined for the run "
                                f"nr {idx} of the workflow '{wf_name}'."
                            )

        if not valid:
            raise RuntimeError("The run configuration is not valid.")

    @staticmethod
    def _pre_queuing(in_q: dict) -> dict:
        """The runs are expanded to the pre-defined structure and sorted by
        priority.
        """
        tmp_q = dict()
        for itm in in_q:
            inputs = itm.get("inputs", dict())
            node = inputs.get("node", "other")
            prio = itm["params"]["prio"]
            repeat = itm["params"]["repeat"]
            run = RunConf(**RunConfiguration.RUN_DEFAULTS)
            run.workflow = itm["workflow"]
            run.inputs = inputs
            run.name = itm["name"]
            run.ref = itm["ref"]

            if tmp_q.get(node, None) is None:
                tmp_q[node] = dict()
            if tmp_q[node].get(prio, None) is None:
                tmp_q[node][prio] = list()
            tmp_q[node][prio].append([run for _ in range(repeat)])

        out_q = dict()
        # Sort by priority:
        for key, val in tmp_q.items():
            out_q[key] = dict(sorted(val.items()))

        return out_q

    @staticmethod
    def _queuing_sequential(in_q: dict) -> dict:
        """Runs are only sorted by priority, e.g. if there are 10 mrr and 10
        ndrpdr runs with the same priority we get list of 10 mrr runs followed
        by 10 ndrpdr runs.
        """
        tmp_q = RunConfiguration._pre_queuing(in_q)

        out_q = dict()
        for node, prios in tmp_q.items():
            if out_q.get(node, None) is None:
                out_q[node] = list()
            for _, runs in prios.items():
                for run in runs:
                    out_q[node].extend(run)
        return out_q

    @staticmethod
    def _queuing_mixed(in_q: dict) -> dict:
        """Runs are sorted by priority and then the runs with the same priority
        are mixed, e.g. if there are 10 mrr and 10 ndrpdr runs with the same
        priority we get list: [mrr, ndrpdr, mrr, ndrpdr, ..., ndrpdr].
        """
        tmp_q = RunConfiguration._pre_queuing(in_q)

        out_q = dict()
        for node, prios in tmp_q.items():
            if out_q.get(node, None) is None:
                out_q[node] = list()
            for _, runs in prios.items():
                zipped = zip_longest(*runs, fillvalue=None)
                out_q[node].extend(
                    [itm for subl in zipped for itm in subl if itm is not None]
                )
        return out_q

    @staticmethod
    def _queuing_random(in_q: dict) -> dict:
        """Runs with the same priority are queued randomly.
        """
        _ = in_q
        raise NotImplementedError("The random queuing is not implemeted yet.")

    def _process_conf(self) -> dict:
        """Process the configuration.

        :returns: Runs for each node sorted in the specified way:
          - sequential - runs are only sorted by priority, e.g. if there are 10
            mrr and 10 ndrpdr runs with the same priority we get list of 10 mrr
            runs followed by 10 ndrpdr runs.
          - mixed - runs are sorted by priority and then the runs with the same
            priority are mixed, e.g. if there are 10 mrr and 10 ndrpdr runs with
            the same priority we get list: [mrr, ndrpdr, mrr, ndrpdr, ...,
            ndrpdr].
          - random - runs are sorted by priority and then the runs with the same
            priority are randomized.
        :rtype: dict
        """
        # Pre-processing:
        # 'suite_gen_params' can be:
        # - string - it defines only one run (e.g. iterative jobs), or
        # - list - it defines len(list) runs with the equal other parameters
        #   (e.g. coverage jobs)

        self._params = self._raw_conf["parameters"]

        ppconf = list()
        for wf_name, wf_data in self._raw_conf["workflows"].items():
            name_tmpl = wf_data["parameters"].get("name", str())
            ref = wf_data["parameters"].get("ref", str())
            for run in wf_data["runs"]:
                name = name_tmpl.format(**run["inputs"]).replace("rls", "")
                if run.get("inputs", None) and \
                        run["inputs"].get("suite_gen_params", None) and \
                        isinstance(run["inputs"]["suite_gen_params"], list):
                    for itm in run["inputs"]["suite_gen_params"]:
                        new_run = deepcopy(run)
                        new_run["inputs"]["suite_gen_params"] = itm
                        new_run["workflow"] = wf_name
                        new_run["name"] = name
                        new_run["ref"] = ref
                        ppconf.append(new_run)
                else:
                    run["workflow"] = wf_name
                    run["name"] = name
                    run["ref"] = ref
                    ppconf.append(run)

        # Processing:
        if self._params["queuing"] == "sequential":
            self._runs = RunConfiguration._queuing_sequential(ppconf)
        elif self._params["queuing"] == "mixed":
            self._runs = RunConfiguration._queuing_mixed(ppconf)
        elif self._params["queuing"] == "random":
            self._runs = RunConfiguration._queuing_random(ppconf)

    def read_conf(self):
        """Read the run configuration from the configuration file.

        :raises RuntimeError: If the configuraton is invalid.
        """

        logging.info("Reading the run configuration...")

        # Read the configuration from the configuration file...
        try:
            with open(self._conf_file, "r") as file_read:
                self._raw_conf = load(file_read, Loader=FullLoader)
        except IOError as err:
            raise RuntimeError(
                f"Not possible to open the file '{self._conf_file}'\n {err}"
            )
        except YAMLError as err:
            raise RuntimeError(
                f"An error occurred while parsing the application "
                f"configuration file '{self._conf_file}'\n {err}"
            )

        # ...validate it...
        self._validate_conf()

        # ...and process.
        try:
            self._process_conf()
        except NotImplementedError as err:
            raise RuntimeError(err)

        #  logging.debug(self._runs)

        logging.info("Done.")

    @property
    def runs(self):
        """Runs groupped by node.
        :rtype: dict
        """
        return self._runs
