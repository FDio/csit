#!/usr/bin/python

# Copyright (c) 2017 Cisco and/or its affiliates.
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
Script extracts required data from robot framework output file (output.xml) and
saves it in JSON format. Its structure is:

{
    "metadata": {
        "vdevice": "VPP version",
        "data-length": int
    },
    "data": {
        "ID": {
            "name": "Test name",
            "parent": "Name of the parent of the test",
            "tags": ["tag 1", "tag 2", "tag n"],
            "type": "PDR" | "NDR",
            "throughput": {
                "value": int,
                "unit": "pps" | "bps" | "percentage"
            },
            "latency": {
                "direction1": {
                    "100": {
                        "min": int,
                        "avg": int,
                        "max": int
                    },
                    "50": {  # Only for NDR
                        "min": int,
                        "avg": int,
                        "max": int
                    },
                    "10": {  # Only for NDR
                        "min": int,
                        "avg": int,
                        "max": int
                    }
                },
                "direction2": {
                    "100": {
                        "min": int,
                        "avg": int,
                        "max": int
                    },
                    "50": {  # Only for NDR
                        "min": int,
                        "avg": int,
                        "max": int
                    },
                    "10": {  # Only for NDR
                        "min": int,
                        "avg": int,
                        "max": int
                    }
                }
            },
            "lossTolerance": "lossTolerance"  # Only for PDR
        },
        "ID" {
            # next test
        }
    }
}

.. note:: ID is the lowercase full path to the test.

:Example:

run_robot_json_data.py -i "output.xml" -o "data.json" -v "17.07-rc0~144"

"""

import argparse
import re
import sys
import json

from robot.api import ExecutionResult, ResultVisitor


class ExecutionChecker(ResultVisitor):
    """Class to traverse through the test suite structure.

    The functionality implemented in this class generates a json structure.
    """

    REGEX_RATE = re.compile(r'^[\D\d]*FINAL_RATE:\s(\d+\.\d+)\s(\w+)')

    REGEX_LAT_NDR = re.compile(r'^[\D\d]*'
                               r'LAT_\d+%NDR:\s\[\'(-?\d+\/-?\d+\/-?\d+)\','
                               r'\s\'(-?\d+\/-?\d+\/-?\d+)\'\]\s\n'
                               r'LAT_\d+%NDR:\s\[\'(-?\d+\/-?\d+\/-?\d+)\','
                               r'\s\'(-?\d+\/-?\d+\/-?\d+)\'\]\s\n'
                               r'LAT_\d+%NDR:\s\[\'(-?\d+\/-?\d+\/-?\d+)\','
                               r'\s\'(-?\d+\/-?\d+\/-?\d+)\'\]')

    REGEX_LAT_PDR = re.compile(r'^[\D\d]*'
                               r'LAT_\d+%PDR:\s\[\'(-?\d+\/-?\d+\/-?\d+)\','
                               r'\s\'(-?\d+\/-?\d+\/-?\d+)\'\][\D\d]*')

    REGEX_TOLERANCE = re.compile(r'^[\D\d]*LOSS_ACCEPTANCE:\s(\d*\.\d*)\s'
                                 r'[\D\d]*')

    def __init__(self, **metadata):
        """Initialisation.

        :param metadata: Key-value pairs to be included to "metadata" part of
        JSON structure.
        :type metadata: dict
        """
        self._data = {
            "metadata": {
            },
            "data": {
            }
        }

        for key, val in metadata.items():
            self._data["metadata"][key] = val

    @property
    def data(self):
        return self._data

    def _get_latency(self, msg, test_type):
        """Get the latency data from the test message.

        :param msg: Message to be parsed.
        :param test_type: Type of the test - NDR or PDR.
        :type msg: str
        :type test_type: str
        :returns: Latencies parsed from the message.
        :rtype: dict
        """

        if test_type == "NDR":
            groups = re.search(self.REGEX_LAT_NDR, msg)
            groups_range = range(1, 7)
        elif test_type == "PDR":
            groups = re.search(self.REGEX_LAT_PDR, msg)
            groups_range = range(1, 3)
        else:
            return {}

        latencies = list()
        for idx in groups_range:
            try:
                lat = [int(item) for item in str(groups.group(idx)).split('/')]
            except (AttributeError, ValueError):
                lat = [-1, -1, -1]
            latencies.append(lat)

        keys = ("min", "avg", "max")
        latency = {
            "direction1": {
            },
            "direction2": {
            }
        }

        latency["direction1"]["100"] = dict(zip(keys, latencies[0]))
        latency["direction2"]["100"] = dict(zip(keys, latencies[1]))
        if test_type == "NDR":
            latency["direction1"]["50"] = dict(zip(keys, latencies[2]))
            latency["direction2"]["50"] = dict(zip(keys, latencies[3]))
            latency["direction1"]["10"] = dict(zip(keys, latencies[4]))
            latency["direction2"]["10"] = dict(zip(keys, latencies[5]))

        return latency

    def visit_suite(self, suite):
        """Implements traversing through the suite and its direct children.

        :param suite: Suite to process.
        :type suite: Suite
        :returns: Nothing.
        """
        if self.start_suite(suite) is not False:
            suite.suites.visit(self)
            suite.tests.visit(self)
            self.end_suite(suite)

    def start_suite(self, suite):
        """Called when suite starts.

        :param suite: Suite to process.
        :type suite: Suite
        :returns: Nothing.
        """
        pass

    def end_suite(self, suite):
        """Called when suite ends.

        :param suite: Suite to process.
        :type suite: Suite
        :returns: Nothing.
        """
        pass

    def visit_test(self, test):
        """Implements traversing through the test.

        :param test: Test to process.
        :type test: Test
        :returns: Nothing.
        """
        if self.start_test(test) is not False:
            self.end_test(test)

    def start_test(self, test):
        """Called when test starts.

        :param test: Test to process.
        :type test: Test
        :returns: Nothing.
        """

        tags = [str(tag) for tag in test.tags]
        if test.status == "PASS" and "NDRPDRDISC" in tags:

            if "NDRDISC" in tags:
                test_type = "NDR"
            elif "PDRDISC" in tags:
                test_type = "PDR"
            else:
                return

            try:
                rate_value = str(re.search(
                    self.REGEX_RATE, test.message).group(1))
            except AttributeError:
                rate_value = "-1"
            try:
                rate_unit = str(re.search(
                    self.REGEX_RATE, test.message).group(2))
            except AttributeError:
                rate_unit = "-1"

            test_result = dict()
            test_result["name"] = test.name.lower()
            test_result["parent"] = test.parent.name.lower()
            test_result["tags"] = tags
            test_result["type"] = test_type
            test_result["throughput"] = dict()
            test_result["throughput"]["value"] = int(rate_value.split('.')[0])
            test_result["throughput"]["unit"] = rate_unit
            test_result["latency"] = self._get_latency(test.message, test_type)
            if test_type == "PDR":
                test_result["lossTolerance"] = str(re.search(
                    self.REGEX_TOLERANCE, test.message).group(1))

            self._data["data"][test.longname.lower()] = test_result

    def end_test(self, test):
        """Called when test ends.

        :param test: Test to process.
        :type test: Test
        :returns: Nothing.
        """
        pass


def parse_tests(args):
    """Process data from robot output.xml file and return JSON data.

    :param args: Parsed arguments.
    :type args: ArgumentParser
    :returns: JSON data structure.
    :rtype: dict
    """

    result = ExecutionResult(args.input)
    checker = ExecutionChecker(vdevice=args.vdevice)
    result.visit(checker)

    return checker.data


def parse_args():
    """Parse arguments from cmd line.

    :returns: Parsed arguments.
    :rtype: ArgumentParser
    """

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.
                                     RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--input",
                        required=True,
                        type=argparse.FileType('r'),
                        help="Robot XML log file.")
    parser.add_argument("-o", "--output",
                        required=True,
                        type=argparse.FileType('w'),
                        help="JSON output file")
    parser.add_argument("-v", "--vdevice",
                        required=False,
                        default="",
                        type=str,
                        help="VPP version")

    return parser.parse_args()


def main():
    """Main function."""

    args = parse_args()
    json_data = parse_tests(args)
    json_data["metadata"]["data-length"] = len(json_data["data"])
    json.dump(json_data, args.output)

if __name__ == "__main__":
    sys.exit(main())
