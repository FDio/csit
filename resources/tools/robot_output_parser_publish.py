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

"""Script extracts intersted data (name, documentation, message, status) from
robot framework output file (output.xml) and print in specified format (wiki,
html) to stdout or, if specified by parameter, redirect to file."""

import argparse
import sys

from robot.api import ExecutionResult, ResultVisitor


class ExecutionChecker(ResultVisitor):
    """Abstract class to traverse through the test suite structure."""

    def __init__(self, args):
        self.formatting = args.formatting

    def visit_suite(self, suite):
        """Implements traversing through the suite and its direct children.

        :param suite: Suite to process.
        :type suite: Suite
        :return: Nothing.
        """

        if self.start_suite(suite) is not False:
            if suite.tests:
                if self.formatting == 'html':
                    sys.stdout.write('<table border=1>'+'\n')
                    sys.stdout.write('<tr><th width=32%>Name</th>'+\
                                     '<th width=40%>Documentation</th>'+\
                                     '<th width=24%>Message</th>'+\
                                     '<th width=4%>Status</th><tr/>'+'\n')
                elif self.formatting == 'wiki':
                    sys.stdout.write('{| class="wikitable"'+'\n')
                    sys.stdout.write('!Name!!Documentation!!Message!!Status'+'\n')
                else:
                    pass

            suite.suites.visit(self)
            suite.tests.visit(self)

            if suite.tests:
                if self.formatting == 'html':
                    sys.stdout.write('</table>'+'\n')
                elif self.formatting == 'wiki':
                    sys.stdout.write('|}'+'\n')
                else:
                    pass

            self.end_suite(suite)

    def start_suite(self, suite):
        """Called when suite starts.

        :param suite: Suite to process.
        :type suite: Suite
        :return: Nothing.
        """

        level = len(suite.longname.split("."))

        if self.formatting == 'html':
            mark_l = '<h'+str(level)+'>'
            mark_r = '</h'+str(level)+'>'
            sys.stdout.write(mark_l+suite.name+mark_r+'\n')
        elif self.formatting == 'wiki':
            mark = "=" * (level+2)
            sys.stdout.write(mark+suite.name+mark+'\n')
        else:
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

        if self.formatting == 'html':
            sys.stdout.write('<tr>'+'\n')
            sys.stdout.write('<td>'+test.name+'</td>'+'\n')
            sys.stdout.write('<td>'+test.doc+'</td>'+'\n')
            sys.stdout.write('<td>'+test.message+'</td>'+'\n')
            sys.stdout.write('<td>'+test.status+'</td>'+'\n')
        elif self.formatting == 'wiki':
            sys.stdout.write('|-'+'\n')
            sys.stdout.write('|'+test.name+'\n')
            sys.stdout.write('|'+test.doc+'\n')
            sys.stdout.write('|'+test.message+'\n')
            sys.stdout.write('|'+test.status+'\n')
        else:
            pass

    def end_test(self, test):
        """Called when test ends.

        :param test: Test to process.
        :type test: Test
        :return: Nothing.
        """

        if self.formatting == 'html':
            sys.stdout.write('</tr>'+'\n')
        elif self.formatting == 'wiki':
            pass
        else:
            pass


def process_robot_file(args):
    """Process data from robot output.xml file and return raw data.

    :param args: Parsed arguments.
    :type args: ArgumentParser
    :return: Nothing.
    """

    result = ExecutionResult(args.input)
    checker = ExecutionChecker(args)
    result.visit(checker)


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
    parser.add_argument("-o", "--output",
                        type=argparse.FileType('w'),
                        help="Output file")
    parser.add_argument("-f", "--formatting", required=True,
                        choices=['html', 'wiki'],
                        help="Output file format")

    return parser.parse_args()


def main():
    """Main function."""

    args = parse_args()

    if args.output:
        sys.stdout = args.output

    process_robot_file(args)


if __name__ == "__main__":
    sys.exit(main())
