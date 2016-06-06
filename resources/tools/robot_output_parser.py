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
intereted values into XML output file."""

import argparse
import sys
import xml.etree.ElementTree as ET

from robot.api import ExecutionResult, ResultVisitor


class ExecutionTestChecker(ResultVisitor):
    """Iterates through test cases."""

    def __init__(self, args):
        self.root = ET.Element('build',
                               attrib={'vdevice': args.vdevice})

    def visit_test(self, test):
        """Overloaded function. Called when test is found to process data.

        :param test: Test to process.
        :type test: ExecutionTestChecker
        """

        if any("PERFTEST_LONG" in tag for tag in test.tags):
            if test.status == 'PASS':
                tags = []
                for tag in test.tags:
                    tags.append(tag)
                for keyword in test.keywords:
                    for assign in keyword.assign:
                        if assign == '${framesize}':
                            framesize = keyword.args[0]
                    if 'worker threads' in keyword.name:
                        workers = keyword.name.split('\'')[1]
                        workers_per_nic = keyword.name.split('\'')[3]

                test_elem = ET.SubElement(self.root,
                    test.longname.split('.')[3].replace(" ",""))
                test_elem.attrib['name'] = test.longname.split('.')[3]
                test_elem.attrib['workerthreads'] = workers
                test_elem.attrib['workerspernic'] = workers_per_nic
                test_elem.attrib['framesize'] = framesize
                test_elem.attrib['tags'] = ', '.join(tags)
                test_elem.text = test.message.split(' ')[1]


def parse_tests(args):
    """Parser result of robot output file and return.

    :param args: Parsed arguments.
    :type args: ArgumentParser

    :return: XML formatted output.
    :rtype: ElementTree
    """

    result = ExecutionResult(args.input)
    checker = ExecutionTestChecker(args)
    result.visit(checker)

    return checker.root


def print_error(msg):
    """Print error message on stderr.

    :param msg: Error message to print.
    :type msg: str
    :return: nothing
    """

    sys.stderr.write(msg+'\n')


def parse_args():
    """Parse arguments from cmd line.

    :return: Parsed arguments.
    :rtype ArgumentParser
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True,
                        type=argparse.FileType('r'),
                        help="Robot XML log file")
    parser.add_argument("-o", "--output", required=True,
                        type=argparse.FileType('w'),
                        help="XML output file")
    parser.add_argument("-v", "--vdevice", required=True,
                        help="VPP version")

    return parser.parse_args()


def main():
    """Main function."""

    args = parse_args()

    root = parse_tests(args)
    ET.ElementTree.write(ET.ElementTree(root), args.output)


if __name__ == "__main__":
    sys.exit(main())
