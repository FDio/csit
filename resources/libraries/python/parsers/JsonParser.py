# Copyright (c) 2018 Cisco and/or its affiliates.
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

"""Used to parse JSON files or JSON data strings to dictionaries"""

import json
from os import uname


class JsonParser(object):
    """Parses JSON data string or files containing JSON data strings"""
    def __init__(self):
        pass

    @staticmethod
    def parse_data(json_data):
        """Return list parsed from JSON data string.

        Translates JSON data into list of values/dictionaries/lists.

        :param json_data: Data in JSON format.
        :type json_data: str
        :returns: JSON data parsed as python list.
        :rtype: list
        """
        if "4.2.0-42-generic" in uname():
            # TODO: remove ugly workaround
            # On Ubuntu14.04 the VAT console returns "error:misc" even after
            # some commands execute correctly. This causes problems
            # with parsing JSON data.
            known_errors = ["sw_interface_dump error: Misc",
                            "lisp_eid_table_dump error: Misc",
                            "show_lisp_status error: Misc",
                            "lisp_map_resolver_dump error: Misc",
                            "show_lisp_pitr error: Misc",
                            "snat_static_mapping_dump error: Misc",
                           ]
            for item in known_errors:
                if item in json_data:
                    json_data = json_data.replace(item, "")
                    print("Removing API error: *{0}* "
                          "from JSON output.".format(item))
        parsed_data = json.loads(json_data)
        return parsed_data

    @staticmethod
    def parse_file(json_file):
        """Return list parsed from file containing JSON string.

        Translates JSON data found in file into list of
        values/dictionaries/lists.

        :param json_file: File with JSON type data.
        :type json_file: str
        :returns: JSON data parsed as python list.
        :rtype: list
        """
        input_data = open(json_file).read()
        parsed_data = JsonParser.parse_data(input_data)
        return parsed_data
