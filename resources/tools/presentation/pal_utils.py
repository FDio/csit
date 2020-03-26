# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""General purpose utilities.
"""

import subprocess
import math
import logging
import csv

from os import walk, makedirs, environ
from os.path import join, isdir
from shutil import move, Error
from datetime import datetime

import numpy as np
import prettytable

from pandas import Series

from resources.libraries.python import jumpavg

from pal_errors import PresentationError


def mean(items):
    """Calculate mean value from the items.

    :param items: Mean value is calculated from these items.
    :type items: list
    :returns: MEan value.
    :rtype: float
    """

    return float(sum(items)) / len(items)


def stdev(items):
    """Calculate stdev from the items.

    :param items: Stdev is calculated from these items.
    :type items: list
    :returns: Stdev.
    :rtype: float
    """
    return Series.std(Series(items))


def relative_change(nr1, nr2):
    """Compute relative change of two values.

    :param nr1: The first number.
    :param nr2: The second number.
    :type nr1: float
    :type nr2: float
    :returns: Relative change of nr1.
    :rtype: float
    """

    return float(((nr2 - nr1) / nr1) * 100)


def relative_change_stdev(mean1, mean2, std1, std2):
    """Compute relative standard deviation of change of two values.

    The "1" values are the base for comparison.
    Results are returned as percentage (and percentual points for stdev).
    Linearized theory is used, so results are wrong for relatively large stdev.

    :param mean1: Mean of the first number.
    :param mean2: Mean of the second number.
    :param std1: Standard deviation estimate of the first number.
    :param std2: Standard deviation estimate of the second number.
    :type mean1: float
    :type mean2: float
    :type std1: float
    :type std2: float
    :returns: Relative change and its stdev.
    :rtype: float
    """
    mean1, mean2 = float(mean1), float(mean2)
    quotient = mean2 / mean1
    first = std1 / mean1
    second = std2 / mean2
    std = quotient * math.sqrt(first * first + second * second)
    return (quotient - 1) * 100, std * 100


def get_files(path, extension=None, full_path=True):
    """Generates the list of files to process.

    :param path: Path to files.
    :param extension: Extension of files to process. If it is the empty string,
        all files will be processed.
    :param full_path: If True, the files with full path are generated.
    :type path: str
    :type extension: str
    :type full_path: bool
    :returns: List of files to process.
    :rtype: list
    """

    file_list = list()
    for root, _, files in walk(path):
        for filename in files:
            if extension:
                if filename.endswith(extension):
                    if full_path:
                        file_list.append(join(root, filename))
                    else:
                        file_list.append(filename)
            else:
                file_list.append(join(root, filename))

    return file_list


def get_rst_title_char(level):
    """Return character used for the given title level in rst files.

    :param level: Level of the title.
    :type: int
    :returns: Character used for the given title level in rst files.
    :rtype: str
    """
    chars = (u'=', u'-', u'`', u"'", u'.', u'~', u'*', u'+', u'^')
    if level < len(chars):
        return chars[level]
    return chars[-1]


def execute_command(cmd):
    """Execute the command in a subprocess and log the stdout and stderr.

    :param cmd: Command to execute.
    :type cmd: str
    :returns: Return code of the executed command, stdout and stderr.
    :rtype: tuple(int, str, str)
    """

    env = environ.copy()
    proc = subprocess.Popen(
        [cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        env=env)

    stdout, stderr = proc.communicate()

    if stdout:
        logging.info(stdout.decode())
    if stderr:
        logging.info(stderr.decode())

    if proc.returncode != 0:
        logging.error(u"    Command execution failed.")
    return proc.returncode, stdout.decode(), stderr.decode()


def get_last_successful_build_nr(jenkins_url, job_name):
    """Get the number of the last successful build of the given job.

    :param jenkins_url: Jenkins URL.
    :param job_name: Job name.
    :type jenkins_url: str
    :type job_name: str
    :returns: The build number as a string.
    :rtype: str
    """
    return execute_command(
        f"wget -qO- {jenkins_url}/{job_name}/lastSuccessfulBuild/buildNumber"
    )


def get_last_completed_build_number(jenkins_url, job_name):
    """Get the number of the last completed build of the given job.

    :param jenkins_url: Jenkins URL.
    :param job_name: Job name.
    :type jenkins_url: str
    :type job_name: str
    :returns: The build number as a string.
    :rtype: str
    """
    return execute_command(
        f"wget -qO- {jenkins_url}/{job_name}/lastCompletedBuild/buildNumber"
    )


def get_build_timestamp(jenkins_url, job_name, build_nr):
    """Get the timestamp of the build of the given job.

    :param jenkins_url: Jenkins URL.
    :param job_name: Job name.
    :param build_nr: Build number.
    :type jenkins_url: str
    :type job_name: str
    :type build_nr: int
    :returns: The timestamp.
    :rtype: datetime.datetime
    """
    timestamp = execute_command(
        f"wget -qO- {jenkins_url}/{job_name}/{build_nr}"
    )
    return datetime.fromtimestamp(timestamp/1000)


def archive_input_data(spec):
    """Archive the report.

    :param spec: Specification read from the specification file.
    :type spec: Specification
    :raises PresentationError: If it is not possible to archive the input data.
    """

    logging.info(u"    Archiving the input data files ...")

    extension = spec.input[u"arch-file-format"]
    data_files = list()
    for ext in extension:
        data_files.extend(get_files(
            spec.environment[u"paths"][u"DIR[WORKING,DATA]"], extension=ext))
    dst = spec.environment[u"paths"][u"DIR[STATIC,ARCH]"]
    logging.info(f"      Destination: {dst}")

    try:
        if not isdir(dst):
            makedirs(dst)

        for data_file in data_files:
            logging.info(f"      Moving the file: {data_file} ...")
            move(data_file, dst)

    except (Error, OSError) as err:
        raise PresentationError(
            u"Not possible to archive the input data.",
            repr(err)
        )

    logging.info(u"    Done.")


def classify_anomalies(data):
    """Process the data and return anomalies and trending values.

    Gather data into groups with average as trend value.
    Decorate values within groups to be normal,
    the first value of changed average as a regression, or a progression.

    :param data: Full data set with unavailable samples replaced by nan.
    :type data: OrderedDict
    :returns: Classification and trend values
    :rtype: 2-tuple, list of strings and list of floats
    """
    # Nan means something went wrong.
    # Use 0.0 to cause that being reported as a severe regression.
    bare_data = [0.0 if np.isnan(sample) else sample
                 for sample in data.values()]
    # TODO: Make BitCountingGroupList a subclass of list again?
    group_list = jumpavg.classify(bare_data).group_list
    group_list.reverse()  # Just to use .pop() for FIFO.
    classification = []
    avgs = []
    active_group = None
    values_left = 0
    avg = 0.0
    for sample in data.values():
        if np.isnan(sample):
            classification.append(u"outlier")
            avgs.append(sample)
            continue
        if values_left < 1 or active_group is None:
            values_left = 0
            while values_left < 1:  # Ignore empty groups (should not happen).
                active_group = group_list.pop()
                values_left = len(active_group.run_list)
            avg = active_group.stats.avg
            classification.append(active_group.comment)
            avgs.append(avg)
            values_left -= 1
            continue
        classification.append(u"normal")
        avgs.append(avg)
        values_left -= 1
    return classification, avgs


def convert_csv_to_pretty_txt(csv_file_name, txt_file_name, delimiter=u","):
    """Convert the given csv table to pretty text table.

    :param csv_file_name: The path to the input csv file.
    :param txt_file_name: The path to the output pretty text file.
    :param delimiter: Delimiter for csv file.
    :type csv_file_name: str
    :type txt_file_name: str
    :type delimiter: str
    """

    txt_table = None
    with open(csv_file_name, u"rt") as csv_file:
        csv_content = csv.reader(csv_file, delimiter=delimiter, quotechar=u'"')
        for row in csv_content:
            if txt_table is None:
                txt_table = prettytable.PrettyTable(row)
            else:
                txt_table.add_row(row)
    txt_table.align[u"Test case"] = u"l"
    txt_table.align[u"RCA"] = u"l"
    if txt_table:
        with open(txt_file_name, u"wt") as txt_file:
            txt_file.write(str(txt_table))
