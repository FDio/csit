"""
Interface to GitHub Actions
===========================

"""


import json
import logging
import requests

from hfr.app_configuration import AppConfiguration


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

    def get_run_status(self, run):
        """
        """
        pass

    def start_run(self, run):
        """
        """
        pass

    def cancel_run(self, run):
        """
        """
        pass
