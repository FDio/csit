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

from robot.api import ExecutionResult, ResultVisitor


class ExecutionTestChecker(ResultVisitor):
    """Iterates through test cases."""

    def __init__(self, args):
        self.table = ''

    def visit_test(self, test):
        """Overloaded function. Called when test is found to process data.

        :param test: Test to process.
        :type test: ExecutionTestChecker
        """

        self.table += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            test.longname, test.doc, test.status, test.message)


def parse_tests(args):
    """Parser result of robot output file and return.

    :param args: Parsed arguments.
    :type args: ArgumentParser

    :return: HTML formatted output.
    :rtype: str
    """

    result = ExecutionResult(args.input)
    checker = ExecutionTestChecker(args)
    result.visit(checker)

    return checker.table


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
                        help="HTML output file")

    return parser.parse_args()


def main():
    """Main function."""

    args = parse_args()

    table = parse_tests(args)
    args.output.write('<html><body><table>'+table+'</table></body></html>')
    args.output.close()


if __name__ == "__main__":
    sys.exit(main())
