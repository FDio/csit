# Copyright (c) 2021 Cisco and/or its affiliates.
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

"""Algorithms to generate files.
"""

import re

from os.path import join
from collections import OrderedDict

import logging

from pal_utils import get_files, get_rst_title_char


RST_INCLUDE_TABLE = (u"\n.. only:: html\n\n"
                     u"    .. csv-table::\n"
                     u"        :header-rows: 1\n"
                     u"        :widths: auto\n"
                     u"        :align: center\n"
                     u"        :file: {file_html}\n"
                     u"\n.. only:: latex\n\n"
                     u"\n  .. raw:: latex\n\n"
                     u"      \\csvautolongtable{{{file_latex}}}\n\n")

REGEX_NIC_SHORT = re.compile(r'(\d*ge\dp\d)([a-z]*\d*[a-z]*)-')


def generate_files(spec, data):
    """Generate all files specified in the specification file.

    :param spec: Specification read from the specification file.
    :param data: Data to process.
    :type spec: Specification
    :type data: InputData
    """

    generator = {
        u"file_details_split": file_details_split,
        u"file_details_split_html": file_details_split_html,
        u"file_test_results": file_test_results,
        u"file_test_results_html": file_test_results_html
    }

    logging.info(u"Generating the files ...")
    for file_spec in spec.files:
        try:
            generator[file_spec[u"algorithm"]](file_spec, data)
        except (NameError, KeyError) as err:
            logging.error(
                f"Probably algorithm {file_spec[u'algorithm']} is not defined: "
                f"{repr(err)}"
            )
    logging.info(u"Done.")


def _tests_in_suite(suite_name, tests):
    """Check if the suite includes tests.

    :param suite_name: Name of the suite to be checked.
    :param tests: Set of tests
    :type suite_name: str
    :type tests: pandas.Series
    :returns: True if the suite includes tests.
    :rtype: bool
    """

    for key in tests.keys():
        if suite_name == tests[key][u"parent"]:
            return True
    return False


def file_details_split(file_spec, input_data, frmt=u"rst"):
    """Generate the file(s) with algorithms
    - file_details_split
    specified in the specification file.

    :param file_spec: File to generate.
    :param input_data: Data to process.
    :param frmt: Format can be: rst or html
    :type file_spec: pandas.Series
    :type input_data: InputData
    :type frmt: str
    """

    fileset_file_name = f"{file_spec[u'output-file']}"
    rst_header = (
        u"\n"
        u".. |br| raw:: html\n\n    <br />\n\n\n"
        u".. |prein| raw:: html\n\n    <pre>\n\n\n"
        u".. |preout| raw:: html\n\n    </pre>\n\n"
    )
    start_lvl = file_spec.get(u"data-start-level", 4)

    logging.info(f"  Generating the file set {fileset_file_name} ...")

    data_sets = file_spec.get(u"data", None)
    if not data_sets:
        logging.error(
            f"  No data sets specified for {file_spec[u'output-file']}, exit."
        )
        return

    table_sets = file_spec.get(u"dir-tables", None)
    if not table_sets:
        logging.error(
            f"  No table sets specified for {file_spec[u'output-file']}, exit."
        )
        return

    if len(data_sets) != len(table_sets):
        logging.error(
            f"  The number of data sets and the number of table sets for "
            f"{file_spec[u'output-file']} are not equal, exit."
        )
        return

    chapters = OrderedDict()
    for data_set, table_set in zip(data_sets, table_sets):

        logging.info(f"   Processing the table set {table_set}...")

        table_lst = None
        if frmt == u"html":
            table_lst = get_files(table_set, u".rst", full_path=True)
        elif frmt == u"rst":
            table_lst = get_files(table_set, u".csv", full_path=True)

        if not table_lst:
            logging.error(
                f"    No tables to include in {table_set}. Skipping."
            )
            continue

        logging.info(u"    Creating the test data set...")
        tests = input_data.filter_data(
            element=file_spec,
            params=[u"name", u"parent", u"doc", u"type", u"level"],
            data=data_set,
            data_set=u"tests",
            continue_on_error=True
        )
        if tests.empty:
            continue
        tests = input_data.merge_data(tests)
        tests.sort_index(inplace=True)

        logging.info(u"    Creating the suite data set...")
        suites = input_data.filter_data(
            element=file_spec,
            data=data_set,
            continue_on_error=True,
            data_set=u"suites"
        )
        if suites.empty:
            continue
        suites = input_data.merge_data(suites)
        suites.sort_index(inplace=True)

        logging.info(u"    Generating files...")

        chapter_l1 = u""
        chapter_l2 = u"-".join(table_set.split(u"_")[-2:])
        for suite_longname, suite in suites.items():

            suite_lvl = len(suite_longname.split(u"."))
            if suite_lvl < start_lvl:
                # Not interested in this suite
                continue

            if suite_lvl == start_lvl:
                # Our top-level suite
                chapter_l1 = suite_longname.split(u'.')[-1]
                if chapters.get(chapter_l1, None) is None:
                    chapters[chapter_l1] = OrderedDict()
                if chapters[chapter_l1].get(chapter_l2, None) is None:
                    chapters[chapter_l1][chapter_l2] = OrderedDict()
                continue

            if _tests_in_suite(suite[u"name"], tests):
                groups = re.search(REGEX_NIC_SHORT, suite[u"name"])
                nic = groups.group(2) if groups else None
                if nic is None:
                    continue
                if chapters[chapter_l1][chapter_l2].get(nic, None) is None:
                    chapters[chapter_l1][chapter_l2][nic] = dict(
                        rst_file=f"{join(table_set, chapter_l1)}_{nic}.rst".
                        replace(u"2n1l-", u"").replace(u"1n1l-", u""),
                        tables=list()
                    )
                for idx, tbl_file in enumerate(table_lst):
                    if suite[u"name"] in tbl_file:
                        chapters[chapter_l1][chapter_l2][nic][u"tables"].append(
                            (
                                table_lst.pop(idx),
                                suite[u"doc"].replace(u'"', u"'").
                                replace(u'\n', u' ').
                                replace(u'\r', u'').
                                replace(u'*[', u'\n\n - *[').
                                replace(u"*", u"**").
                                replace(u'\n\n - *[', u' - *[', 1)
                            )
                        )
                        break
    titles = {
        # VPP Perf, MRR
        u"container_memif": u"LXC/DRC Container Memif",
        u"crypto": u"IPsec IPv4 Routing",
        u"hoststack": u"Hoststack Testing",
        u"ip4": u"IPv4 Routing",
        u"ip4_tunnels": u"IPv4 Tunnels",
        u"ip6": u"IPv6 Routing",
        u"ip6_tunnels": u"IPv6 Tunnels",
        u"l2": u"L2 Ethernet Switching",
        u"lb": u"LoadBalancer",
        u"nfv_density": u"NFV Service Density",
        u"srv6": u"SRv6 Routing",
        u"vm_vhost": u"KVM VMs vhost-user",
        u"vts": u"Virtual Topology System",
        # VPP Device
        u"interfaces": u"Interfaces",
        u"l2bd": u"L2 Bridge-domain",
        u"l2patch": u"L2 Patch",
        u"l2xc": u"L2 Cross-connect",
    }

    order_chapters = file_spec.get(u"order-chapters", None)

    if order_chapters:
        order_1 = order_chapters.get(u"level-1", None)
        order_2 = order_chapters.get(u"level-2", None)
        order_3 = order_chapters.get(u"level-3", None)
        if not order_1:
            order_1 = chapters.keys()
    else:
        order_1 = None
        order_2 = None
        order_3 = None

    for chapter_l1 in order_1:
        content_l1 = chapters.get(chapter_l1, None)
        if not content_l1:
            continue
        with open(f"{fileset_file_name}/index.rst", u"a") as file_handler:
            file_handler.write(f"    {chapter_l1}\n")
        l1_file_name = f"{join(fileset_file_name, chapter_l1)}.rst"
        title = titles.get(chapter_l1, chapter_l1)
        logging.info(f"   Generating {title} ...")
        with open(l1_file_name, u"w") as file_handler:
            file_handler.write(
                f"{title}\n"
                f"{get_rst_title_char(1) * len(title)}\n\n"
                f".. toctree::\n\n"
            )

        if not order_2:
            order_2 = chapters[chapter_l1].keys()
        for chapter_l2 in order_2:
            content_l2 = content_l1.get(chapter_l2, None)
            if not content_l2:
                continue
            if not order_3:
                order_3 = chapters[chapter_l1][chapter_l2].keys()
            for chapter_l3 in order_3:
                content_l3 = content_l2.get(chapter_l3, None)
                if not content_l3:
                    continue
                with open(l1_file_name, u"a") as file_handler:
                    item = u"/".join(content_l3[u'rst_file'].split(u'/')[-2:])
                    file_handler.write(f"    ../{item}\n")
                logging.info(f"    Writing the file {content_l3[u'rst_file']}")
                with open(content_l3[u'rst_file'], u"w+") as file_handler:
                    title = f"{chapter_l2}-{chapter_l3}"
                    file_handler.write(
                        f"{rst_header}\n"
                        f"{title}\n"
                        f"{get_rst_title_char(2) * len(title)}\n"
                    )
                    for table in content_l3[u'tables']:
                        title = table[0].split(u"/")[-1].split(u".")[0]
                        file_handler.write(
                            f"\n{title}\n"
                            f"{get_rst_title_char(3) * len(title)}\n"
                        )
                        file_handler.write(f"\n{table[1]}\n")
                        if frmt == u"html":
                            file_handler.write(
                                f"\n.. include:: {table[0].split(u'/')[-1]}"
                                f"\n"
                            )
                        elif frmt == u"rst":
                            file_handler.write(
                                RST_INCLUDE_TABLE.format(
                                    file_latex=table[0],
                                    file_html=table[0].split(u"/")[-1])
                            )


def file_details_split_html(file_spec, input_data):
    """Generate the file(s) with algorithms
    - file_details_split_html
    specified in the specification file.

    :param file_spec: File to generate.
    :param input_data: Data to process.
    :type file_spec: pandas.Series
    :type input_data: InputData
    """
    file_details_split(file_spec, input_data, frmt=u"html")


def file_test_results(file_spec, input_data, frmt=u"rst"):
    """Generate the file(s) with algorithms
    - file_test_results
    specified in the specification file.

    :param file_spec: File to generate.
    :param input_data: Data to process.
    :param frmt: Format can be: rst or html
    :type file_spec: pandas.Series
    :type input_data: InputData
    :type frmt: str
    """

    base_file_name = f"{file_spec[u'output-file']}"
    rst_header = (
        u"\n"
        u".. |br| raw:: html\n\n    <br />\n\n\n"
        u".. |prein| raw:: html\n\n    <pre>\n\n\n"
        u".. |preout| raw:: html\n\n    </pre>\n\n"
    )
    start_lvl = file_spec.get(u"data-start-level", 4)

    logging.info(f"  Generating the file {base_file_name} ...")

    if frmt == u"html":
        table_lst = get_files(file_spec[u"dir-tables"], u".rst", full_path=True)
    elif frmt == u"rst":
        table_lst = get_files(file_spec[u"dir-tables"], u".csv", full_path=True)
    else:
        return
    if not table_lst:
        logging.error(
            f"  No tables to include in {file_spec[u'dir-tables']}. Skipping."
        )
        return

    logging.info(
        f"    Creating the tests data set for the "
        f"{file_spec.get(u'type', u'')} {file_spec.get(u'title', u'')}."
    )

    tests = input_data.filter_data(
        file_spec,
        params=[u"name", u"parent", u"doc", u"type", u"level"],
        continue_on_error=True
    )
    if tests.empty:
        return
    tests = input_data.merge_data(tests)

    suites = input_data.filter_data(
        file_spec,
        continue_on_error=True,
        data_set=u"suites"
    )
    if suites.empty:
        return
    suites = input_data.merge_data(suites)
    suites.sort_index(inplace=True)

    file_name = u""
    for suite_longname, suite in suites.items():

        suite_lvl = len(suite_longname.split(u"."))
        if suite_lvl < start_lvl:
            # Not interested in this suite
            continue

        if suite_lvl == start_lvl:
            # Our top-level suite
            chapter = suite_longname.split(u'.')[-1]
            file_name = f"{base_file_name}/{chapter}.rst"
            logging.info(f"    Writing file {file_name}")
            with open(f"{base_file_name}/index.rst", u"a") as file_handler:
                file_handler.write(f"    {chapter}\n")
            with open(file_name, u"a") as file_handler:
                file_handler.write(rst_header)

        title_line = get_rst_title_char(suite[u"level"] - start_lvl + 2) * \
            len(suite[u"name"])
        with open(file_name, u"a") as file_handler:
            if not (u"-ndrpdr" in suite[u"name"] or
                    u"-mrr" in suite[u"name"] or
                    u"-dev" in suite[u"name"]):
                file_handler.write(f"\n{suite[u'name']}\n{title_line}\n")

            if _tests_in_suite(suite[u"name"], tests):
                for tbl_file in table_lst:
                    if suite[u"name"] in tbl_file:
                        file_handler.write(
                            f"\n{suite[u'name']}\n{title_line}\n"
                        )
                        file_handler.write(
                            f"\n{suite[u'doc']}\n".replace(u'|br|', u'\n\n -')
                        )
                        if frmt == u"html":
                            file_handler.write(
                                f"\n.. include:: {tbl_file.split(u'/')[-1]}\n"
                            )
                        elif frmt == u"rst":
                            file_handler.write(
                                RST_INCLUDE_TABLE.format(
                                    file_latex=tbl_file,
                                    file_html=tbl_file.split(u"/")[-1])
                            )
                        break

    logging.info(u"  Done.")


def file_test_results_html(file_spec, input_data):
    """Generate the file(s) with algorithms
    - file_test_results_html
    specified in the specification file.

    :param file_spec: File to generate.
    :param input_data: Data to process.
    :type file_spec: pandas.Series
    :type input_data: InputData
    """
    file_test_results(file_spec, input_data, frmt=u"html")
