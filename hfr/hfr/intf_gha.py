"""
Interface to GitHub Actions
===========================

Implements methods to:
- start a run,
- get the status of a run.

"""


import json
import logging
import requests

from hfr.app_configuration import AppConfiguration
from hfr.oper_data import Run


class Gha:
    """Interface to GitHub Actions
    """

    def __init__(self, app_conf: AppConfiguration):
        """Initialization.
        """

        self._gh_conf = app_conf.github

        self._gh_url = (
            f"{self._gh_conf['url']}/"
            f"{self._gh_conf['account']}/"
            f"{self._gh_conf['repo']}"
        )
        self._gh_header = {
            "Authorization": f"token {self._gh_conf['pat']}",
            "Accept": "application/vnd.github+json",
        }

    def _get(self, url: str) -> tuple:
        """Implementation of GET request.

        :param url: url for the GET request.
        :type url: str
        :returns: Status and JSON formated content of the response.
        :rtype: tuple(bool, dict)
        """

        try:
            resp = requests.get(url=url, headers=self._gh_header, timeout=10)
        except requests.exceptions.RequestException as err:
            logging.warning(f"GET requests to '{url}' failed: {err}")
            return False, None

        content = None
        if resp.ok:
            try:
                content = json.loads(resp.text)
            except json.decoder.JSONDecodeError as err:
                logging.warning(
                    f"GET requests to '{url}' failed: "
                    f"Cannot decode the response. {err}"
                )

        return resp.ok, content

    def _post(self, url: str, params: dict) -> tuple:
        """Implementation of POST request.

        :param url: url for the POST request.
        "param params: JSON formatted data transparently passed to the post
            request.
        :type url: str
        :type params: dict
        :returns: Status and JSON formatted content of the response.
        :rtype: tuple(bool, dict)
        """

        try:
            resp = requests.post(
                url=url, json=params, headers=self._gh_header, timeout=10
            )
        except requests.exceptions.RequestException as err:
            logging.warning(f"POST requests to '{url}' failed: {err}")
            return False, None

        content = None
        if resp.ok and resp.text:
            try:
                content = json.loads(resp.text)
            except json.decoder.JSONDecodeError as err:
                logging.warning(
                    f"POST requests to '{url}' failed: "
                    f"Cannot decode the response. {err}"
                )

        return resp.ok, content

    def get_run_status(self, run: Run) -> tuple:
        """Gets the status of the run.

        :param run: The run we are interested in.
        :type run: Run
        :returns: Starus of the GET request and JSON formatted response.
        :rtype: tuple(bool, dict)
        """
        # move to management
        # run.data.gha_id = "21630259111"
        run.data.hfr_id = "2602205"

        if run.data.gha_id:
            # Get directly info about the run
            return self._get(f"{self._gh_url}/actions/runs/{run.data.gha_id}")
        else:
            # Get info about all runs and find the right one based on gha_name
            status, content = self._get((
                f"{self._gh_url}/actions/workflows/{run.conf.workflow}.yaml/"
                f"runs"
            ))
            # Parse the response to find the required run.
            name = f"{run.conf.name}-{run.data.hfr_id}"
            run_data = dict()
            if status:
                for itm in content.get("workflow_runs", dict()):
                    if itm.get("name", "") == name:
                        run_data = itm
                        break

            return status, run_data

    def start_run(self, run: Run) -> tuple:
        """Start the run.

        :param run: The run to start.
        :type run: Run
        :returns: Starus of the POST request and JSON formatted response.
        :rtype: tuple(bool, dict)
        """
        # move to management
        run.data.hfr_id = "2602206"
        run.conf.inputs["my_run_id"] = run.data.hfr_id

        return self._post(
            url = (
                f"{self._gh_url}/actions/workflows/{run.conf.workflow}.yaml/"
                f"dispatches"
            ),
            params = {"ref": run.conf.ref, "inputs": run.conf.inputs}
        )

    def cancel_run(self, run: Run, force=False) -> tuple:
        """Cancel the run.

        :param run: The run to cancel.
        :param force: If True, 'force-cancel' is used.
        :type run: Run
        :type force: bool
        :returns: Starus of the POST request and JSON formatted response.
        :rtype: tuple(bool, dict)
        """

        method = "force-cancel" if force else "cancel"
        return self._post(
            url = (f"{self._gh_url}/actions/runs/{run.data.gha_id}/{method}")
        )
