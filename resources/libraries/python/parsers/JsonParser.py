# Copyright (c) 2016 Cisco and/or its affiliates.
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


class JsonParser(object):
    """Parses JSON data string or files containing JSON data strings"""
    def __init__(self):
        pass

    @staticmethod
    def parse_data(json_data):
        """Return list parsed from json data string.

        Translates json data into list of values/dictionaries/lists
        :param json_data: Data in json format.
        :return: JSON data parsed as python list.
        """
        parsed_data = json.loads(json_data)
        return parsed_data

    def parse_file(self, json_file):
        """Return list parsed from file containing json string.

        Translates json data found in file into list of
        values/dictionaries/lists
        :param json_file: File with json type data.
        :return: JSON data parsed as python list.
        """
        input_data = open(json_file).read()
        parsed_data = self.parse_data(input_data)
        return parsed_data
