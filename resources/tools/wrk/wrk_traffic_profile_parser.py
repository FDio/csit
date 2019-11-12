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


class WrkTrafficProfile:
    """The wrk traffic profile.
    """

    MANDATORY_PARAMS = ("urls",
                        "first-cpu",
                        "cpus",
                        "duration",
                        "nr-of-threads",
                        "nr-of-connections")

    INTEGER_PARAMS = (("cpus", 1),
                      ("first-cpu", 0),
                      ("duration", 1),
                      ("nr-of-threads", 1),
                      ("nr-of-connections", 1))

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
        if not (self._validate_mandatory_structure()
                and self._validate_mandatory_values()
                and self._validate_optional_values()
                and self._validate_dependencies()):
            self.traffic_profile = None

    def _validate_mandatory_structure(self):
        """Validate presence of mandatory parameters in trafic profile dict

        :returns: whether mandatory structure is followed by the profile
        :rtype: bool
        """
        # Level 1: Check if the profile is a dictionary:
        if not isinstance(self.traffic_profile, dict):
            logger.error("The wrk traffic profile must be a dictionary.")
            return False

        # Level 2: Check if all mandatory parameters are present:
        is_valid = True
        for param in self.MANDATORY_PARAMS:
            if self.traffic_profile.get(param, None) is None:
                logger.error("The parameter '{0}' in mandatory.".format(param))
                is_valid = False
        return is_valid

    def _validate_mandatory_values(self):
        """Validate that mandatory profile values satisfy their constraints

        :returns: whether mandatory values are acceptable
        :rtype: bool
        """
        # Level 3: Mandatory params: Check if urls is a list:
        is_valid = True
        if not isinstance(self.traffic_profile["urls"], list):
            logger.error("The parameter 'urls' must be a list.")
            is_valid = False

        # Level 3: Mandatory params: Check if integers are not below minimum
        for param, minimum in self.INTEGER_PARAMS:
            if not self._validate_int_param(param, minimum):
                is_valid = False
        return is_valid

    def _validate_optional_values(self):
        """Validate values for optional parameters, if present

        :returns: whether present optional values are acceptable
        :rtype: bool
        """
        is_valid = True
        # Level 4: Optional params: Check if script is present:
        script = self.traffic_profile.get("script", None)
        if script is not None:
            if not isinstance(script, str):
                logger.error("The path to LuaJIT script in invalid")
                is_valid = False
            else:
                if not isfile(script):
                    logger.error("The file '{0}' does not exist.".
                                 format(script))
                    is_valid = False
        else:
            self.traffic_profile["script"] = None
            logger.debug("The optional parameter 'LuaJIT script' is not "
                         "defined. No problem.")

        # Level 4: Optional params: Check if header is present:
        header = self.traffic_profile.get("header", None)
        if header is not None:
            if isinstance(header, dict):
                header = ", ".join("{0}: {1}".format(*item)
                                   for item in header.items())
                self.traffic_profile["header"] = header
            elif not isinstance(header, str):
                logger.error("The parameter 'header' type is not valid.")
                is_valid = False

            if not header:
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
            if not isinstance(latency, bool):
                logger.error("The parameter 'latency' must be boolean.")
                is_valid = False
        else:
            self.traffic_profile["latency"] = False
            logger.debug("The optional parameter 'latency' is not defined. "
                         "No problem.")

        # Level 4: Optional params: Check if timeout is present:
        if 'timeout' in self.traffic_profile:
            if not self._validate_int_param('timeout', 1):
                is_valid = False
        else:
            self.traffic_profile["timeout"] = None
            logger.debug("The optional parameter 'timeout' is not defined. "
                         "No problem.")

        return is_valid

    def _validate_dependencies(self):
        """Validate dependencies between parameters

        :returns: whether dependencies between parameters are acceptable
        :rtype: bool
        """
        # Level 5: Check urls and cpus:
        if self.traffic_profile["cpus"] % len(self.traffic_profile["urls"]):
            logger.error("The number of CPUs must be a multiple of the "
                         "number of URLs.")
            return False
        return True

    def _validate_int_param(self, param, minimum):
        """Validate that an int parameter is set acceptably
        If it is not an int already but a string, convert and store it as int.

        :param param: Name of a traffic profile parameter
        :param minimum: The minimum value for the named parameter
        :type param: str
        :type minimum: int
        :returns: whether param is set to an int of at least minimum value
        :rtype: bool
        """
        value = self._traffic_profile[param]
        if isinstance(value, (str, unicode)):
            if value.isdigit():
                value = int(value)
            else:
                value = minimum - 1
        if isinstance(value, int) and value >= minimum:
            self.traffic_profile[param] = value
            return True
        logger.error("The parameter '{param}' must be an integer and "
                     "at least {minimum}".format(param=param, minimum=minimum))
        return False

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
