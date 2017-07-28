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
saves it in XML format. The XML structure is as follows:

<?xml version="1.0" encoding="UTF-8"?>
<build vdevice="17.07-rc0~144">
  <SUITE LONG NAME WITH TEST NAME name="TEST NAME">
    2874921.875
    <name>TEST NAME</name>
    <longname>SUITE LONG NAME WITH TEST NAME</longname>
    <tags>
      <tag>TAG 1</tag>
      <tag>TAG 2</tag>
      <tag>...</tag>
      <tag>TAG N</tag>
    </tags>
    <framesize>64B</framesize>
    <threads>1</threads>
    <cores>1</cores>
    <type>NDR | PDR</type>
    <throughput>
      <value>2874921.875</value>
      <unit>pps | bps | percentage</unit>
    </throughput>
    <losstolerance>0.5</losstolerance>  # Only for PDR
    <latency>
      <direction2>
        <R50>                # Only for NDR
          <max>302</max>
          <avg>94</avg>
          <min>40</min>
        </R50>
        <R100>
          <max>1926</max>
          <avg>1249</avg>
          <min>80</min>
        </R100>
        <R10>                # Only for NDR
          <max>195</max>
          <avg>64</avg>
          <min>40</min>
        </R10>
      </direction2>
      <direction1>
        <R50>                # Only for NDR
          <max>217</max>
          <avg>96</avg>
          <min>40</min>
        </R50>
        <R100>
          <max>2098</max>
          <avg>1445</avg>
          <min>80</min>
        </R100>
        <R10>                # Only for NDR
          <max>182</max>
          <avg>63</avg>
          <min>30</min>
        </R10>
      </direction1>
    </latency>
  </SUITE LONG NAME WITH TEST NAME>

  <SUITE LONG NAME WITH TEST NAME name="TEST NAME">
    Next element
  </SUITE LONG NAME WITH TEST NAME>

</build>

:note:

If the long name or the name includes white spaces, they are removed.

:Example:

run_robot_xml_data.py -i "output.xml" -o "data.xml" -v "17.07-rc0~144"

"""

import argparse
import re
import sys

from xml.etree.ElementTree import Element, SubElement, tostring
from robot.api import ExecutionResult, ResultVisitor


class ExecutionChecker(ResultVisitor):
    """Class to traverse through the test suite structure.

    The functionality implemented in this class generates a json structure.
    """

    REGEX_TC = re.compile(r'^tc\d+-((\d+)B|IMIX)-(\d)t(\d)c-(.*)')

    REGEX_RATE = re.compile(r'^[\D\d]*FINAL_RATE:\s(\d+\.\d+)\s(\w+)')

    REGEX_LAT_NDR = re.compile(r'^[\D\d]*'
                               r'LAT_\d+%NDR:\s\[\'(-?\d+/-?\d+/-?\d+)\','
                               r'\s\'(-?\d+/-?\d+/-?\d+)\'\]\s\n'
                               r'LAT_\d+%NDR:\s\[\'(-?\d+/-?\d+/-?\d+)\','
                               r'\s\'(-?\d+/-?\d+/-?\d+)\'\]\s\n'
                               r'LAT_\d+%NDR:\s\[\'(-?\d+/-?\d+/-?\d+)\','
                               r'\s\'(-?\d+/-?\d+/-?\d+)\'\]')

    REGEX_LAT_PDR = re.compile(r'^[\D\d]*'
                               r'LAT_\d+%PDR:\s\[\'(-?\d+/-?\d+/-?\d+)\','
                               r'\s\'(-?\d+/-?\d+/-?\d+)\'\][\D\d]*')

    REGEX_TOLERANCE = re.compile(r'^[\D\d]*LOSS_ACCEPTANCE:\s(\d*\.\d*)\s'
                                 r'[\D\d]*')

    def __init__(self, args):
        """Initialisation.

        :param args: Arguments passed to the script from CLI.
        :type args: ArgumentParser
        """

        self._root = Element('build', attrib={'vdevice': args.vdevice})

    @property
    def root(self):
        """Getter - return created XML structure.

        :returns: XML structure.
        :rtype: ETree.Element
        """
        return self._root

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
                lat = [item for item in str(groups.group(idx)).split('/')]
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

        latency["direction1"]["R100"] = dict(zip(keys, latencies[0]))
        latency["direction2"]["R100"] = dict(zip(keys, latencies[1]))
        if test_type == "NDR":
            latency["direction1"]["R50"] = dict(zip(keys, latencies[2]))
            latency["direction2"]["R50"] = dict(zip(keys, latencies[3]))
            latency["direction1"]["R10"] = dict(zip(keys, latencies[4]))
            latency["direction2"]["R10"] = dict(zip(keys, latencies[5]))

        return latency

    def _dict_to_xml(self, tag, dictionary, parent=None):
        """Convert a dictionary to XML structure. The values in the dictionary
        to be converted can be only simple data types (int, str, ...)
        convertible to string or another dictionaries.

        :param tag: The root tag in the XML structure which will be created.
        :param dictionary: The dictionary to be converted.
        :param parent: Parent element. Created XML structure in appended to this
        parent.
        :type tag: str
        :type dictionary: dict
        :type parent: ETree.Element
        :returns: XML structure.
        :rtype: ETree.Element
        """

        elem = Element(tag)
        for key, val in dictionary.items():
            if isinstance(val, dict):
                self._dict_to_xml(key, val, elem)
            else:
                child = Element(key)
                child.text = str(val)
                elem.append(child)
        if parent is not None:
            parent.append(elem)
        return elem

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

            xml_test = SubElement(self._root, test.longname.lower().
                                  replace(" ", ""), name=test.name.lower())
            xml_test.text = rate_value
            name = SubElement(xml_test, "name")
            name.text = test.name.lower()
            long_name = SubElement(xml_test, "longname")
            long_name.text = test.longname.lower()
            xml_tags = SubElement(xml_test, "tags")
            for tag in tags:
                xml_tag = SubElement(xml_tags, "tag")
                xml_tag.text = tag
            frame_size = SubElement(xml_test, "framesize")
            frame_size.text = str(re.search(self.REGEX_TC, test.name).group(1))
            threads = SubElement(xml_test, "threads")
            threads.text = str(re.search(self.REGEX_TC, test.name).group(3))
            cores = SubElement(xml_test, "cores")
            cores.text = str(re.search(self.REGEX_TC, test.name).group(4))
            xml_test_type = SubElement(xml_test, "type")
            xml_test_type.text = test_type
            if test_type == "PDR":
                loss_tolerance = SubElement(xml_test, "losstolerance")
                loss_tolerance.text = str(re.search(
                    self.REGEX_TOLERANCE, test.message).group(1))
            throughput = SubElement(xml_test, "throughput")
            value = SubElement(throughput, "value")
            value.text = rate_value
            unit = SubElement(throughput, "unit")
            unit.text = rate_unit
            xml_test.append(self._dict_to_xml("latency", self._get_latency(
                test.message, test_type)))

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
    checker = ExecutionChecker(args)
    result.visit(checker)

    return checker.root


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
    xml_data = parse_tests(args)
    args.output.write(tostring(xml_data))

if __name__ == "__main__":
    sys.exit(main())
