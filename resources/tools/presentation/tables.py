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

"""Algorithms to generate tables.
"""


import pandas as pd
import logging

from errors import PresentationError
from utils import mean, stdev


def generate_tables(config, data):
    """

    :param config:
    :param data:
    :return:
    """

    for table in config.tables:
        eval(table["algorithm"])(table, data)


def table_performance_improvements(table, input_data):
    """

    :param table:
    :param input_data:
    :return:
    """

    logging.info("Generating the table {0} ...".format(table.get("title", "")))

    # Read the template
    file_name = table.get("template", None)
    if file_name:
        try:
            tmpl = _read_csv_template(file_name)
        except PresentationError:
            logging.error("The template '{0}' does not exist. Skipping the "
                          "table.".format(file_name))
            return None
    else:
        logging.error("The template is not defined. Skipping the table.")
        return None

    # Transform the data
    data = input_data.filter_tests_data(table)

    # Prepare the header of the tables
    header = list()
    for column in table["columns"]:
        header.append(column["title"])

    tbl_lst = [header, ]
    for tmpl_item in tmpl:
        tbl_item = list()
        for column in table["columns"]:
            cmd = column["data"].split(" ")[0]
            args = column["data"].split(" ")[1:]
            if cmd == "template":
                tbl_item.append(tmpl_item[int(args[0])])
            elif cmd == "data":
                job = args[0]
                operation = args[1]
                data_lst = list()
                for build in data[job]:
                    try:
                        data_lst.append(build[tmpl_item[0]]["throughput"]["value"])
                    except:
                        pass
                tbl_item.append({"data": data_lst})
                if data_lst:
                    tbl_item[-1][operation] = eval(operation)(data_lst)
            elif cmd == "operation":
                pass
            else:
                logging.error("Not supported command {0}. Skipping the table.".
                              format(cmd))
                return None
        tbl_lst.append(tbl_item)

    print(tbl_lst)

    # Create the tables

    logging.info("Done.")


def _read_csv_template(file_name):
    """Read the template from a .csv file.

    :param file_name: Name / full path / relative path of the file to read.
    :type file_name: str
    :returns: Data from the template as list (lines) of lists (items on line).
    :rtype: list
    :raises: PresentationError if it is not possible to read the file.
    """

    try:
        with open(file_name, 'r') as csv_file:
            tmpl_data = list()
            for line in csv_file:
                tmpl_data.append(line[:-1].split(","))
        return tmpl_data
    except IOError as err:
        raise PresentationError(str(err))
