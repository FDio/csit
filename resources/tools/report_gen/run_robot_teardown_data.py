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
Script extracts interested data (name, documentation, message, VAT command
history or table from Show Runtime command) from robot framework output file
(output.xml) and prints in specified format (wiki, html, rst) to defined output
file.

Supported formats:
 - html
 - rst

:TODO:
 - wiki
 - md

 NOTE: Generation of rst, md, html and wiki files is imported from file
  run_robot_data.py.

:Example:

run_robot_teardown_data.py -i "output.xml" -o "tests.rst" -d "VAT_H" -f "rst"
-s 3 -l 2

The example reads the VAT command history data from "output.xml", writes
the output to "tests.rst" in rst format. It will start on the 3rd level of xml
structure and the generated document hierarchy will start on the 2nd level.
"""

import argparse
import re
import sys
import json
import string

from robot.api import ExecutionResult, ResultVisitor

from run_robot_data import do_html, gen_html_table, do_rst, gen_rst_table, \
    do_md, do_wiki, gen_wiki_table


class ExecutionChecker(ResultVisitor):
    """Class to traverse through the test suite structure.

    The functionality implemented in this class generates a json file. Its
    structure is:

    [
        {
            "level": "Level of the suite, type: str",
            "title": "Title of the suite, type: str",
            "doc": "Documentation of the suite, type: str",
            "table": [
                ["TC name", "TC doc", "message or VAT history or show runtime"],
                ["TC name", "TC doc", "message or VAT history or show runtime"],
                ... other test cases ...
                ["Name", "Documentation", "Message or VAT command history or
                VPP operational data"]
            ]
        },
        ... other test suites ...
    ]

    .. note:: The header of the table with TCs is at the and of the table.
    """

    def __init__(self, args):
        self.formatting = args.formatting
        self.data = args.data
        if self.data == "VAT_H":
            self.lookup_kw = "Show Vat History On All Duts"
            self.column_name = "VAT command history"
        elif self.data == "SH_RUN":
            self.lookup_kw = "Vpp Show Runtime"
            self.column_name = "VPP operational data"
        else:
            raise ValueError("{0} look-up not implemented.".format(self.data))
        self.lookup_kw_nr = 0
        self.lookup_msg_nr = 0

    def visit_suite(self, suite):
        """Implements traversing through the suite and its direct children.

        :param suite: Suite to process.
        :type suite: Suite
        :returns: Nothing.
        """

        if self.start_suite(suite) is not False:
            if suite.tests:
                sys.stdout.write(',"tests":[')
            else:
                sys.stdout.write('},')

            suite.suites.visit(self)
            suite.tests.visit(self)

            if suite.tests:
                hdr = '["Name","Documentation", "' + self.column_name + '"]'
                sys.stdout.write(hdr + ']},')

            self.end_suite(suite)

    def start_suite(self, suite):
        """Called when suite starts.

        :param suite: Suite to process.
        :type suite: Suite
        :returns: Nothing.
        """

        level = len(suite.longname.split("."))
        sys.stdout.write('{')
        sys.stdout.write('"level":"' + str(level) + '",')
        sys.stdout.write('"title":"' + suite.name.replace('"', "'") + '",')
        sys.stdout.write('"doc":"' + suite.doc.replace('"', "'").
                         replace('\n', ' ').replace('\r', '').
                         replace('*[', ' |br| *[') + '"')

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
            test.keywords.visit(self)
            self.end_test(test)

    def start_test(self, test):
        """Called when test starts.

        :param test: Test to process.
        :type test: Test
        :returns: Nothing.
        """

        name = test.name.replace('"', "'")
        doc = test.doc.replace('"', "'").replace('\n', ' ').replace('\r', '').\
            replace('[', ' |br| [')
        sys.stdout.write('["' + name + '","' + doc + '","')

    def end_test(self, test):
        """Called when test ends.

        :param test: Test to process.
        :type test: Test
        :returns: Nothing.
        """
        sys.stdout.write('"],')

    def visit_keyword(self, kw):
        """Implements traversing through the keyword and its child keywords.

        :param kw: Keyword to process.
        :type kw: Keyword
        :returns: Nothing.
        """
        if self.start_keyword(kw) is not False:
            self.end_keyword(kw)

    def start_keyword(self, kw):
        """Called when keyword starts. Default implementation does nothing.

        :param kw: Keyword to process.
        :type kw: Keyword
        :returns: Nothing.
        """
        try:
            if kw.type == "teardown":
                self.lookup_kw_nr = 0
                self.visit_teardown_kw(kw)
        except AttributeError:
            pass

    def end_keyword(self, kw):
        """Called when keyword ends. Default implementation does nothing.

        :param kw: Keyword to process.
        :type kw: Keyword
        :returns: Nothing.
        """
        pass

    def visit_teardown_kw(self, kw):
        """Implements traversing through the teardown keyword and its child
        keywords.

        :param kw: Keyword to process.
        :type kw: Keyword
        :returns: Nothing.
        """
        for keyword in kw.keywords:
            if self.start_teardown_kw(keyword) is not False:
                self.visit_teardown_kw(keyword)
                self.end_teardown_kw(keyword)

    def start_teardown_kw(self, kw):
        """Called when teardown keyword starts. Default implementation does
        nothing.

        :param kw: Keyword to process.
        :type kw: Keyword
        :returns: Nothing.
        """
        if kw.name.count(self.lookup_kw):
            self.lookup_kw_nr += 1
            self.lookup_msg_nr = 0
            kw.messages.visit(self)

    def end_teardown_kw(self, kw):
        """Called when keyword ends. Default implementation does nothing.

        :param kw: Keyword to process.
        :type kw: Keyword
        :returns: Nothing.
        """
        pass

    def visit_message(self, msg):
        """Implements visiting the message.

        :param msg: Message to process.
        :type msg: Message
        :returns: Nothing.
        """
        if self.start_message(msg) is not False:
            self.end_message(msg)

    def start_message(self, msg):
        """Called when message starts. Default implementation does nothing.

        :param msg: Message to process.
        :type msg: Message
        :returns: Nothing.
        """
        if self.data == "VAT_H":
            self.vat_history(msg)
        elif self.data == "SH_RUN":
            self.show_run(msg)

    def end_message(self, msg):
        """Called when message ends. Default implementation does nothing.

        :param msg: Message to process.
        :type msg: Message
        :returns: Nothing.
        """
        pass

    def vat_history(self, msg):
        """Called when extraction of VAT command history is required.

        :param msg: Message to process.
        :type msg: Message
        :returns: Nothing.
        """
        if msg.message.count("VAT command history:"):
            self.lookup_msg_nr += 1
            text = re.sub("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3} "
                          "VAT command history", "", msg.message, count=1).\
                replace('\n', ' |br| ').replace('\r', '').replace('"', "'")
            sys.stdout.write("DUT" + str(self.lookup_msg_nr) + text)

    def show_run(self, msg):
        """Called when extraction of VPP operational data (output of CLI command
        Show Runtime) is required.

        :param msg: Message to process.
        :type msg: Message
        :returns: Nothing.
        """
        if msg.message.count("vat# Thread "):
            self.lookup_msg_nr += 1
            text = msg.message.replace("vat# ", "").\
                replace("return STDOUT ", "").replace('\n', ' |br| ').\
                replace('\r', '').replace('"', "'")
            if self.lookup_msg_nr == 1:
                sys.stdout.write("DUT" + str(self.lookup_kw_nr) +
                                 ": |br| " + text)


def process_robot_file(args):
    """Process data from robot output.xml file and generate defined file type.

    :param args: Parsed arguments.
    :type args: ArgumentParser
    :return: Nothing.
    """

    old_sys_stdout = sys.stdout
    sys.stdout = open(args.output + '.json', 'w')

    result = ExecutionResult(args.input)
    checker = ExecutionChecker(args)

    sys.stdout.write('[')
    result.visit(checker)
    sys.stdout.write('{}]')
    sys.stdout.close()
    sys.stdout = old_sys_stdout

    with open(args.output + '.json', 'r') as json_file:
        data = json.load(json_file)
    data.pop(-1)

    if args.formatting == 'rst':
        do_rst(data, args)
    elif args.formatting == 'wiki':
        do_wiki(data, args)
    elif args.formatting == 'html':
        do_html(data, args)
    elif args.formatting == 'md':
        do_md(data, args)


def parse_args():
    """Parse arguments from cmd line.

    :return: Parsed arguments.
    :rtype ArgumentParser
    """

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.
                                     RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--input",
                        required=True,
                        type=argparse.FileType('r'),
                        help="Robot XML log file")
    parser.add_argument("-o", "--output",
                        type=str,
                        required=True,
                        help="Output file")
    parser.add_argument("-d", "--data",
                        type=str,
                        required=True,
                        help="Required data: VAT (VAT history), RUN (show run)")
    parser.add_argument("-f", "--formatting",
                        required=True,
                        choices=['html', 'wiki', 'rst', 'md'],
                        help="Output file format")
    parser.add_argument("-s", "--start",
                        type=int,
                        default=1,
                        help="The first level to be taken from xml file")
    parser.add_argument("-l", "--level",
                        type=int,
                        default=1,
                        help="The level of the first chapter in generated file")

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(process_robot_file(parse_args()))
