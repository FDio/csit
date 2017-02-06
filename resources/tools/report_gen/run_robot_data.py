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
Script extracts interested data (name, documentation, message, status) from
robot framework output file (output.xml) and prints in specified format (wiki,
html, rst) to defined output file.

Supported formats:
 - html
 - rst

:TODO:
 - wiki
 - md

:Example:

robot_output_parser_publish.py -i output.xml" -o "tests.rst" -f "rst" -s 3 -l 2

The example reads the data from "output.xml", writes the output to "tests.rst"
in rst format. It will start on the 3rd level of xml structure and the generated
document hierarchy will start on the 2nd level.
"""

import argparse
import re
import sys
import json
import string

from robot.api import ExecutionResult, ResultVisitor


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
                ["TC name", "TC doc", "message or status"],
                ["TC name", "TC doc", "message or status"],
                ... other test cases ...
                ["Name", "Documentation", "Message or Status"]
            ]
        },
        ... other test suites ...
    ]

    .. note:: The header of the table with TCs is at the and of the table.
    """

    def __init__(self, args):
        self.formatting = args.formatting

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
                if "ndrdisc" in suite.longname.lower():
                    hdr = '["Name","Documentation","Message"]'
                else:
                    hdr = '["Name","Documentation","Status"]'
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
        if any("NDRPDRDISC" in tag for tag in test.tags):
            msg = test.message.replace('\n', ' |br| ').replace('\r', ''). \
                replace('"', "'")

            sys.stdout.write('["' + name + '","' + doc + '","' + msg + '"]')
        else:
            sys.stdout.write(
                '["' + name + '","' + doc + '","' + test.status + '"]')

    def end_test(self, test):
        """Called when test ends.

        :param test: Test to process.
        :type test: Test
        :returns: Nothing.
        """
        sys.stdout.write(',')


def do_html(data, args):
    """Generation of a html file from json data.

    :param data: List of suites from json file.
    :param args: Parsed arguments.
    :type data: list of dict
    :type args: ArgumentParser
    :returns: Nothing.
    """

    shift = int(args.level)
    start = int(args.start)

    output = open(args.output, 'w')

    output.write('<html>')
    for item in data:
        if int(item['level']) < start:
            continue
        level = str(int(item['level']) - start + shift)
        output.write('<h' + level + '>' + item['title'].lower() +
                     '</h' + level + '>')
        output.write('<p>' + re.sub(r"(\*)(.*?)(\*)", r"<b>\2</b>", item['doc'],
                                    0, flags=re.MULTILINE).
                     replace(' |br| ', '<br>') + '</p>')
        try:
            output.write(gen_html_table(item['tests']))
        except KeyError:
            continue
    output.write('</html>')
    output.close()


def gen_html_table(data):
    """Generates a table with TCs' names, documentation and messages / statuses
    in html format. There is no css used.

    :param data: Json data representing a table with TCs.
    :type data: str
    :returns: Table with TCs' names, documentation and messages / statuses in
    html format.
    :rtype: str
    """

    table = '<table width=100% border=1><tr>'
    table += '<th width=30%>' + data[-1][0] + '</th>'
    table += '<th width=50%>' + data[-1][1] + '</th>'
    table += '<th width=20%>' + data[-1][2] + '</th></tr>'

    for item in data[0:-1]:
        table += '<tr>'
        for element in item:
            table += '<td>' + element.replace(' |br| ', '<br>') + '</td>'
    table += '</tr></table>'

    return table


def do_rst(data, args):
    """Generation of a rst file from json data.

    :param data: List of suites from json file.
    :param args: Parsed arguments.
    :type data: list of dict
    :type args: ArgumentParser
    :returns: Nothing.
    """

    hdrs = ['=', '-', '`', "'", '.', '~', '*', '+', '^']
    shift = int(args.level)
    start = int(args.start)

    output = open(args.output, 'w')
    output.write('\n.. |br| raw:: html\n\n    <br />\n\n')

    for item in data:
        if int(item['level']) < start:
            continue
        if 'ndrchk' in item['title'].lower():
            continue
        output.write(item['title'].lower() + '\n' +
                     hdrs[int(item['level']) - start + shift] *
                     len(item['title']) + '\n\n')
        output.write(item['doc'].replace('*', '**').replace('|br|', '\n\n -') +
                     '\n\n')
        try:
            output.write(gen_rst_table(item['tests']) + '\n\n')
        except KeyError:
            continue
    output.close()


def gen_rst_table(data):
    """Generates a table with TCs' names, documentation and messages / statuses
    in rst format.

    :param data: Json data representing a table with TCs.
    :type data: str
    :returns: Table with TCs' names, documentation and messages / statuses in
    rst format.
    :rtype: str
    """

    table = []
    # max size of each column
    lengths = map(max, zip(*[[len(str(elt)) for elt in item] for item in data]))

    start_of_line = '| '
    vert_separator = ' | '
    end_of_line = ' |'
    line_marker = '-'

    meta_template = vert_separator.join(['{{{{{0}:{{{0}}}}}}}'.format(i)
                                         for i in range(len(lengths))])
    template = '{0}{1}{2}'.format(start_of_line, meta_template.format(*lengths),
                                  end_of_line)
    # determine top/bottom borders
    to_separator = string.maketrans('| ', '+-')
    start_of_line = start_of_line.translate(to_separator)
    vert_separator = vert_separator.translate(to_separator)
    end_of_line = end_of_line.translate(to_separator)
    separator = '{0}{1}{2}'.format(start_of_line, vert_separator.
                                   join([x * line_marker for x in lengths]),
                                   end_of_line)
    # determine header separator
    th_separator_tr = string.maketrans('-', '=')
    start_of_line = start_of_line.translate(th_separator_tr)
    line_marker = line_marker.translate(th_separator_tr)
    vertical_separator = vert_separator.translate(th_separator_tr)
    end_of_line = end_of_line.translate(th_separator_tr)
    th_separator = '{0}{1}{2}'.format(start_of_line, vertical_separator.
                                      join([x * line_marker for x in lengths]),
                                      end_of_line)
    # prepare table
    table.append(separator)
    # set table header
    titles = data[-1]
    table.append(template.format(*titles))
    table.append(th_separator)
    # generate table rows
    for item in data[0:-2]:
        desc = re.sub(r'(^ \|br\| )', r'', item[1])
        table.append(template.format(item[0], desc, item[2]))
        table.append(separator)
    desc = re.sub(r'(^ \|br\| )', r'', data[-2][1])
    table.append(template.format(data[-2][0], desc, data[-2][2]))
    table.append(separator)
    return '\n'.join(table)


def do_md(data, args):
    """Generation of a rst file from json data.

    :param data: List of suites from json file.
    :param args: Parsed arguments.
    :type data: list of dict
    :type args: ArgumentParser
    :returns: Nothing.
    """
    raise NotImplementedError("Export to 'md' format is not implemented.")


def do_wiki(data, args):
    """Generation of a wiki page from json data.

    :param data: List of suites from json file.
    :param args: Parsed arguments.
    :type data: list of dict
    :type args: ArgumentParser
    :returns: Nothing.
    """

    shift = int(args.level)
    start = int(args.start)

    output = open(args.output, 'w')

    for item in data:
        if int(item['level']) < start:
            continue
        if 'ndrchk' in item['title'].lower():
            continue
        mark = "=" * (int(item['level']) - start + shift) + ' '
        output.write(mark + item['title'].lower() + mark + '\n')
        output.write(item['doc'].replace('*', "'''").replace('|br|', '\n*') +
                     '\n')
        try:
            output.write(gen_wiki_table(item['tests']) + '\n\n')
        except KeyError:
            continue
    output.close()


def gen_wiki_table(data):
    """Generates a table with TCs' names, documentation and messages / statuses
    in wiki format.

    :param data: Json data representing a table with TCs.
    :type data: str
    :returns: Table with TCs' names, documentation and messages / statuses in
    wiki format.
    :rtype: str
    """

    table = '{| class="wikitable"\n'
    header = ""
    for item in data[-1]:
        header += '!{}\n'.format(item)
    table += header
    for item in data[0:-1]:
        desc = re.sub(r'(^ \|br\| )', r'', item[1]).replace(' |br| ', '\n\n')
        msg = item[2].replace(' |br| ', '\n\n')
        table += '|-\n|{}\n|{}\n|{}\n'.format(item[0], desc, msg)
    table += '|}\n'

    return table


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
