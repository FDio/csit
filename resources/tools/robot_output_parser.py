#!/usr/bin/python

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

"""Script parses the data taken by robot framework (output.xml) and dumps
intereted values into JSON output file."""

import json
import re
import sys, getopt

from robot.api import ExecutionResult, ResultVisitor


class ExecutionTestChecker(ResultVisitor):
    """Iterates through test cases."""

    def __init__(self, vDeviceVersion):
        self.vDeviceVersion = vDeviceVersion
        self.out = []

    def visit_test(self, test):
        """Overloaded function. Called when test is found to process data.

        :param test: Test to process.
        :type test: ExecutionTestChecker
        """

        test_id = test.longname
        test_status = 'Failed'
        framesize = ''
        throughput = ''
        throughput_units = ''
        workers_per_nic = ''
        workers = ''

        if any("PERFTEST" in tag for tag in test.tags):
            if test.status == 'PASS':
                test_status = 'Passed'
                if any("PERFTEST_LONG" in tag for tag in test.tags):
                    throughput = test.message.split(' ')[1]
                    throughput_units = test.message.split(' ')[2]
                elif any("PERFTEST_SHORT" in tag for tag in test.tags):
                    for keyword in test.keywords:
                        for assign in keyword.assign:
                            if assign == '${rate}':
                                temp = re.findall(r"(\d*\.\d+|\d+)([A-Za-z]*)",
                                                  keyword.args[0])
                                throughput = temp[0][0]
                                throughput_units = temp[0][1]

                for keyword in test.keywords:
                    for assign in keyword.assign:
                        if assign == '${framesize}':
                            framesize = keyword.args[0]
                    if 'worker threads' in keyword.name:
                        workers = keyword.name.split('\'')[1]
                        workers_per_nic = keyword.name.split('\'')[3]

            self.out.append({'testCase': {
                'testId': test_id,
                'testStatus': test_status,
                'workerThreads': workers,
                'workerThreadsPerNic': workers_per_nic,
                'testTags': [tag for tag in test.tags],
                'l2FrameSize': {'value': framesize,
                                'units': 'Bytes'},
                'throughput': {'value': throughput,
                               'units': throughput_units},
                'vDevice': {'version': self.vDeviceVersion}}})


def parse_tests(xml_file, vDeviceVersion):
    """Parser result of robot output file and return.

    :param xml_file: Output.xml from robot run.
    :param vDeviceVersion: vDevice version.
    :type xml_file: file
    :type vDeviceVersion: str

    :return: JSON formatted output.
    :rtype: dict
    """

    result = ExecutionResult(xml_file)
    checker = ExecutionTestChecker(vDeviceVersion)
    result.visit(checker)

    return checker.out


def print_help():
    """Print help on stdout."""

    print "args: [-h] -i <input_log_file> -o <output_json_file>" + \
          " -v <vpp_version>"


def print_error(msg):
    """Print error message on stderr.

    :param msg: Error message to print.
    :type msg: str
    :return: nothing
    """

    sys.stderr.write(msg+'\n')


def main(argv):
    """Main function."""

    _log_file = None
    _json_file = None
    _vpp = None

    try:
        opts, _ = getopt.getopt(argv, "hi:o:v:", ["help"])
    except getopt.GetoptError:
        print_help()
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print_help()
            sys.exit()
        elif opt == '-i':
            _log_file = arg
        elif opt == '-o':
            _json_file = arg
        elif opt == '-v':
            _vpp = arg

    if _log_file is None or _json_file is None or _vpp is None:
        print_help()
        sys.exit(1)

    try:
        with open(_log_file, 'r') as input_file:
            with open(_json_file, 'w') as output_file:
                out = parse_tests(input_file, _vpp)
                json.dump(out, fp=output_file, sort_keys=True,
                          indent=4, separators=(',', ': '))
    except IOError as ex_error:
        print_error(str(ex_error))
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
