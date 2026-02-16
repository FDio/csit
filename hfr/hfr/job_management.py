"""

"""


import logging

from datetime import datetime, timezone

class JobManagement:
    """
    Docstring for JobManagement
    """

    def __init__(self, oper, tbs):
        """
        """
        self._oper = oper
        self._tbs = tbs

        logging.info("Job management started successfully.")

    @staticmethod
    def _generate_id():
        """Based on timestamp.

        :returns: Last ten digits of the timestamp.
        :rtype: str
        """
        id = str(int(datetime.now(timezone.utc).timestamp() * 1e6))
        return id[-10:]

    def manage(self):
        logging.info(f"I am still alive! {JobManagement._generate_id()}")
