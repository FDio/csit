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
interested values into XML output file."""

import argparse
import re
import sys
import xml.etree.ElementTree as ET

from robot.api import ExecutionResult, ResultVisitor


class ExecutionChecker(ResultVisitor):
    """Iterates through test cases."""

    tc_regexp = re.compile(ur'^tc\d+-((\d+)B|IMIX)-(\d)t(\d)c-(.*)')
    rate_regexp = re.compile(ur'^[\D\d]*FINAL_RATE:\s(\d+\.\d+)[\D\d]*')
    lat_regexp = re.compile(ur'^[\D\d]*'\
        ur'LAT_\d+%NDR:\s\[\'(-?\d+\/-?\d+\/-?\d+)\','\
        ur'\s\'(-?\d+\/-?\d+\/-?\d+)\'\]\s\n'\
        ur'LAT_\d+%NDR:\s\[\'(-?\d+\/-?\d+\/-?\d+)\','\
        ur'\s\'(-?\d+\/-?\d+\/-?\d+)\'\]\s\n'\
        ur'LAT_\d+%NDR:\s\[\'(-?\d+\/-?\d+\/-?\d+)\','\
        ur'\s\'(-?\d+\/-?\d+\/-?\d+)\'\]')

    def __init__(self, args):
        self.root = ET.Element('build',
                               attrib={'vdevice': args.vdevice})

    def visit_suite(self, suite):
        """Implements traversing through the suite and its direct children.

        :param suite: Suite to process.
        :type suite: Suite
        :return: Nothing.
        """
        if self.start_suite(suite) is not False:
            suite.suites.visit(self)
            suite.tests.visit(self)
            self.end_suite(suite)

    def start_suite(self, suite):
        """Called when suite starts.

        :param suite: Suite to process.
        :type suite: Suite
        :return: Nothing.
        """
        pass

    def end_suite(self, suite):
        """Called when suite ends.

        :param suite: Suite to process.
        :type suite: Suite
        :return: Nothing.
        """
        pass

    def visit_test(self, test):
        """Implements traversing through the test.

        :param test: Test to process.
        :type test: Test
        :return: Nothing.
        """
        if self.start_test(test) is not False:
            self.end_test(test)

    def start_test(self, test):
        """Called when test starts.

        :param test: Test to process.
        :type test: Test
        :return: Nothing.
        """
        if any("NDRPDRDISC" in tag for tag in test.tags):
            if test.status == 'PASS':
                tags = []
                for tag in test.tags:
                    tags.append(tag)

                test_elem = ET.SubElement(
                    self.root, "S" + test.parent.name.replace(" ", ""))
                test_elem.attrib['name'] = test.parent.name
                test_elem.attrib['framesize'] = str(re.search(
                    self.tc_regexp, test.name).group(1))
                test_elem.attrib['threads'] = str(re.search(
                    self.tc_regexp, test.name).group(3))
                test_elem.attrib['cores'] = str(re.search(
                    self.tc_regexp, test.name).group(4))
                if any("NDRDISC" in tag for tag in test.tags):
                    try:
                        test_elem.attrib['lat_100'] = str(re.search(
                            self.lat_regexp, test.message).group(1)) + '/' +\
                            str(re.search(self.lat_regexp, test.message).
                                group(2))
                    except AttributeError:
                        test_elem.attrib['lat_100'] = "-1/-1/-1/-1/-1/-1"
                    try:
                        test_elem.attrib['lat_50'] = str(re.search(
                            self.lat_regexp, test.message).group(3)) + '/' +\
                            str(re.search(self.lat_regexp, test.message).
                                group(4))
                    except AttributeError:
                        test_elem.attrib['lat_50'] = "-1/-1/-1/-1/-1/-1"
                    try:
                        test_elem.attrib['lat_10'] = str(re.search(
                            self.lat_regexp, test.message).group(5)) + '/' +\
                            str(re.search(self.lat_regexp, test.message).
                                group(6))
                    except AttributeError:
                        test_elem.attrib['lat_10'] = "-1/-1/-1/-1/-1/-1"
                test_elem.attrib['tags'] = ', '.join(tags)
                try:
                    test_elem.text = str(re.search(
                        self.rate_regexp, test.message).group(1))
                except AttributeError:
                    test_elem.text = "-1"

    def end_test(self, test):
        """Called when test ends.

        :param test: Test to process.
        :type test: Test
        :return: Nothing.
        """
        pass


def parse_tests(args):
    """Process data from robot output.xml file and return XML data.

    :param args: Parsed arguments.
    :type args: ArgumentParser

    :return: XML formatted output.
    :rtype: ElementTree
    """

    result = ExecutionResult(args.input)
    checker = ExecutionChecker(args)
    result.visit(checker)

    return checker.root


def print_error(msg):
    """Print error message on stderr.

    :param msg: Error message to print.
    :type msg: str
    :return: nothing
    """

    sys.stderr.write(msg + '\n')


def parse_args():
    """Parse arguments from cmd line.

    :return: Parsed arguments.
    :rtype ArgumentParser
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input",
                        required=True,
                        type=argparse.FileType('r'),
                        help="Robot XML log file")
    parser.add_argument("-o", "--output",
                        required=True,
                        type=argparse.FileType('w'),
                        help="XML output file")
    parser.add_argument("-v", "--vdevice",
                        required=False,
                        default="",
                        type=str,
                        help="VPP version")

    return parser.parse_args()


def main():
    """Main function."""

    args = parse_args()

    root = parse_tests(args)
    ET.ElementTree.write(ET.ElementTree(root), args.output)


if __name__ == "__main__":
    sys.exit(main())
