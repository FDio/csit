# Copyright (c) 2021 Cisco and/or its affiliates.
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

"""Module supporting structure-unaware json in-memory data.
"""

from collections.abc import Mapping, Iterable
import json
import os

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.robot_interaction import get_variable
from resources.libraries.python.time_measurement import datetime_utc_str as now


class CsitEncoder(json.JSONEncoder):
    """JSON encoder extension class, handling all CSIT export needs."""

    # Pylint wants to keep "o", to match the parent class method argument name.
    # Otherwise, it would be too short a name.
    def default(self, o):
        """Recursively convert to a more serializable form.

        VPP PAPI code can give data with its own MACAddres type.
        The default json.JSONEncoder method raises TypeError on that.
        First point of CsitEncoder is to expect that and apply str().

        But PAPI responses are namedtuples, which confuses
        the json.JSONEncoder method (so it does not recurse).

        Dictization (see PapiExecutor) helps somewhat, but it turns namedtuple
        into a UserDict, which also confuses json.JSONEncoder.
        Therefore, we recursively convert any Mapping into an ordinary dict,
        which finally makes json.JSONEncoder str() apply to the leaf value.
        We also convert iterables to list,
        and prevent numbers from getting converted to strings.

        :param o: Object to make serializable, dictized when applicable.
        :type o: object
        :returns: Serializable equivalent of the argument.
        :rtype: object
        :raises ValueError: If the argument does not support string conversion.
        """
        # Recursion ends at scalar values, do not change the known ones.
        if isinstance(o, (str, bytes, int, float, bool)):
            return o
        # Recurse over and convert mappings.
        if isinstance(o, Mapping):
            return {key: self.default(o[key]) for key in o}
        # Recurse over and convert iterables.
        if isinstance(o, Iterable):
            return [self.default(item) for item in o]
        try:
            # Allow siblings in diamond inheritance to do their thing.
            return super().default(o)
        except TypeError:
            return str(o)


class export_json():
    """Class handling the json data setting and export.
    """

    ROBOT_LIBRARY_SCOPE = u"TEST"

    def __init__(self):
        """Declare data field, do not reset data yet.
        """
        self.data = None

    def reset_test_timer(self):
        """Reset the mutable state to minimal initial tree.

        This has to be called explicitly from test setup,
        otherwise Robot likes to postpone initialization
        until first call by a data-adding keyword.
        """
        start_time = now()
        data = dict()
        data[u"version"] = Constants.MODEL_VERSION
        # TODO: "ci".
        # TODO: "job".
        # TODO: "build-number".
        # TODO: "testbed".
        data[u"suite-id"] = get_variable(u"${SUITE_NAME}")
        data[u"suite-doc"] = get_variable(u"${SUITE_DOCUMENTATION}")
        # "sut-version" is set by a separate keyword.
        # "test-id" is added on flush.
        # "test-type" is set by keyword setting results.
        data[u"test-doc"] = get_variable(u"${TEST_DOCUMENTATION}", u"")
        # "tags" is detected and added on flush.
        data[u"start_time"] = start_time
        # "end-time" is added on flush.
        # "status" is added on flush.
        # "message" is added on flush.
        data[u"results"] = dict()
        # TODO: "resource"
        # TODO: "network"
        data[u"log"] = list()
        self.data = data

    def flush_test(self):
        """Write serialized data to file based on test name.

        Should be run from test teardown, as the implementation
        reads various Robot variables, some of them only available at teardown.
        """
        end_time = now()
        data = self.data
        suite_name = get_variable(u"${SUITE_NAME}")
        suite_path_part = os.path.join(*suite_name.split(u"."))
        test_name = get_variable(u"${TEST_NAME}")
        data[u"test-id"] = suite_name + u"." + test_name
        test_tags = get_variable(u"${TEST_TAGS}")
        data[u"tags"] = [str(tag) for tag in test_tags]
        data[u"end_time"] = end_time
        data[u"status"] = get_variable(u"${TEST_STATUS}")
        data[u"message"] = get_variable(u"${TEST_MESSAGE}")
        log_dir = get_variable(u"${OUTPUT_DIR}", ".")
        file_path = os.path.join(
            log_dir, suite_path_part, test_name + u".json.log"
        )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        logger.debug(u"Debugging a circular reference.")
        logger.debug(f"data str {data}")
        logger.debug(f"data repr {data!r}")
        with open(file_path, u"w") as file_out:
            json.dump(data, file_out, indent=1, cls=CsitEncoder)
        # Not explicitly forgetting data here, so accidental double flush
        # does not lose information.
        # We rely on explicit "time reset" at start of test setup,
        # coupled with library import scope set to "test".
