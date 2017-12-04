# Copyright (c) 2018 Cisco and / or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.

"""wrk traffic profile parser.

See LLD for the structure of a wrk traffic profile.
"""


from os.path import isfile
from pprint import pformat

from yaml import load, YAMLError
from robot.api import logger

from resources.tools.wrk.wrk_errors import WrkError


class WrkTrafficProfile(object):
    """The wrk traffic profile.
    """

    MANDATORY_PARAMS = ("urls",
                        "first-cpu",
                        "cpus",
                        "duration",
                        "nr-of-threads",
                        "nr-of-connections")

    def __init__(self, profile_name):
        """Read the traffic profile from the yaml file.

        :param profile_name: Path to the yaml file with the profile.
        :type profile_name: str
        :raises: WrkError if it is not possible to parse the profile.
        """

        self._profile_name = None
        self._traffic_profile = None

        self.profile_name = profile_name

        try:
            with open(self.profile_name, 'r') as profile_file:
                self.traffic_profile = load(profile_file)
        except IOError as err:
            raise WrkError(msg="An error occurred while opening the file '{0}'."
                           .format(self.profile_name),
                           details=str(err))
        except YAMLError as err:
            raise WrkError(msg="An error occurred while parsing the traffic "
                               "profile '{0}'.".format(self.profile_name),
                           details=str(err))

        self._validate_traffic_profile()

        if self.traffic_profile:
            logger.debug("\nThe wrk traffic profile '{0}' is valid.\n".
                         format(self.profile_name))
            logger.debug("wrk traffic profile '{0}':".format(self.profile_name))
            logger.debug(pformat(self.traffic_profile))
        else:
            logger.debug("\nThe wrk traffic profile '{0}' is invalid.\n".
                         format(self.profile_name))
            raise WrkError("\nThe wrk traffic profile '{0}' is invalid.\n".
                           format(self.profile_name))

    def __repr__(self):
        return pformat(self.traffic_profile)

    def __str__(self):
        return pformat(self.traffic_profile)

    def _validate_traffic_profile(self):
        """Validate the traffic profile.

        The specification, the structure and the rules are described in
        doc/wrk_lld.rst
        """

        logger.debug("\nValidating the wrk traffic profile '{0}'...\n".
                     format(self.profile_name))

        # Level 1: Check if the profile is a dictionary:
        if not isinstance(self.traffic_profile, dict):
            logger.error("The wrk traffic profile must be a dictionary.")
            self.traffic_profile = None
            return

        # Level 2: Check if all mandatory parameters are present:
        is_valid = True
        for param in self.MANDATORY_PARAMS:
            if self.traffic_profile.get(param, None) is None:
                logger.error("The parameter '{0}' in mandatory.".format(param))
                is_valid = False
        if not is_valid:
            self.traffic_profile = None
            return

        # Level 3: Mandatory params: Check if urls is a list:
        is_valid = True
        if not isinstance(self.traffic_profile["urls"], list):
            logger.error("The parameter 'urls' must be a list.")
            is_valid = False

        # Level 3: Mandatory params: Check if cpus is a valid integer:
        try:
            cpus = int(self.traffic_profile["cpus"])
            if cpus < 1:
                raise ValueError
            self.traffic_profile["cpus"] = cpus
        except ValueError:
            logger.error("The parameter 'cpus' must be an integer greater than "
                         "1.")
            is_valid = False

        # Level 3: Mandatory params: Check if first-cpu is a valid integer:
        try:
            first_cpu = int(self.traffic_profile["first-cpu"])
            if first_cpu < 0:
                raise ValueError
            self.traffic_profile["first-cpu"] = first_cpu
        except ValueError:
            logger.error("The parameter 'first-cpu' must be an integer greater "
                         "than 1.")
            is_valid = False

        # Level 3: Mandatory params: Check if duration is a valid integer:
        try:
            duration = int(self.traffic_profile["duration"])
            if duration < 1:
                raise ValueError
            self.traffic_profile["duration"] = duration
        except ValueError:
            logger.error("The parameter 'duration' must be an integer "
                         "greater than 1.")
            is_valid = False

        # Level 3: Mandatory params: Check if nr-of-threads is a valid integer:
        try:
            nr_of_threads = int(self.traffic_profile["nr-of-threads"])
            if nr_of_threads < 1:
                raise ValueError
            self.traffic_profile["nr-of-threads"] = nr_of_threads
        except ValueError:
            logger.error("The parameter 'nr-of-threads' must be an integer "
                         "greater than 1.")
            is_valid = False

        # Level 3: Mandatory params: Check if nr-of-connections is a valid
        # integer:
        try:
            nr_of_connections = int(self.traffic_profile["nr-of-connections"])
            if nr_of_connections < 1:
                raise ValueError
            self.traffic_profile["nr-of-connections"] = nr_of_connections
        except ValueError:
            logger.error("The parameter 'nr-of-connections' must be an integer "
                         "greater than 1.")
            is_valid = False

        # Level 4: Optional params: Check if script is present:
        script = self.traffic_profile.get("script", None)
        if script is not None:
            if not isinstance(script, str):
                logger.error("The path to LuaJIT script in invalid")
                is_valid = False
            else:
                if not isfile(script):
                    logger.error("The file '{0}' in not present.".
                                 format(script))
                    is_valid = False
        else:
            self.traffic_profile["script"] = None
            logger.debug("The optional parameter 'LuaJIT script' is not "
                         "defined. No problem.")

        # Level 4: Optional params: Check if header is present:
        header = self.traffic_profile.get("header", None)
        if header:
            if not (isinstance(header, dict) or isinstance(header, str)):
                logger.error("The parameter 'header' is not valid.")
                is_valid = False
            else:
                if isinstance(header, dict):
                    header_lst = list()
                    for key, val in header.items():
                        header_lst.append("{0}: {1}".format(key, val))
                    if header_lst:
                        self.traffic_profile["header"] = ", ".join(header_lst)
                    else:
                        logger.error("The parameter 'header' is defined but "
                                     "empty.")
                        is_valid = False
        else:
            self.traffic_profile["header"] = None
            logger.debug("The optional parameter 'header' is not defined. "
                         "No problem.")

        # Level 4: Optional params: Check if latency is present:
        latency = self.traffic_profile.get("latency", None)
        if latency is not None:
            try:
                latency = bool(latency)
                self.traffic_profile["latency"] = latency
            except ValueError:
                logger.error("The parameter 'latency' must be boolean.")
                is_valid = False
        else:
            self.traffic_profile["latency"] = False
            logger.debug("The optional parameter 'latency' is not defined. "
                         "No problem.")

        # Level 4: Optional params: Check if timeout is present:
        timeout = self.traffic_profile.get("timeout", None)
        if timeout:
            try:
                timeout = int(timeout)
                if timeout < 1:
                    raise ValueError
                self.traffic_profile["timeout"] = timeout
            except ValueError:
                logger.error("The parameter 'timeout' must be integer greater "
                             "than 1.")
                is_valid = False
        else:
            self.traffic_profile["timeout"] = None
            logger.debug("The optional parameter 'timeout' is not defined. "
                         "No problem.")

        if not is_valid:
            self.traffic_profile = None
            return

        # Level 5: Check dependencies between parameters:
        # Level 5: Check urls and cpus:
        if self.traffic_profile["cpus"] % len(self.traffic_profile["urls"]):
            logger.error("The number of CPUs must be a multiplication of the "
                         "number of URLs.")
            self.traffic_profile = None

    @property
    def profile_name(self):
        """Getter - Profile name.

        :returns: The traffic profile file path
        :rtype: str
        """
        return self._profile_name

    @profile_name.setter
    def profile_name(self, profile_name):
        """

        :param profile_name:
        :type profile_name: str
        """
        self._profile_name = profile_name

    @property
    def traffic_profile(self):
        """Getter: Traffic profile.

        :returns: The traffic profile.
        :rtype: dict
        """
        return self._traffic_profile

    @traffic_profile.setter
    def traffic_profile(self, profile):
        """Setter - Traffic profile.

        :param profile: The new traffic profile.
        :type profile: dict
        """
        self._traffic_profile = profile
