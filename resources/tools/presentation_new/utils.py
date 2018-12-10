# Copyright (c) 2018 Cisco and/or its affiliates.
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

import multiprocessing
import subprocess
import numpy as np
import logging
import csv
import prettytable

from os import walk, makedirs, environ
from os.path import join, isdir
from shutil import move, Error
from math import sqrt

from errors import PresentationError
from jumpavg.BitCountingClassifier import BitCountingClassifier


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

    avg = mean(items)
    variance = [(x - avg) ** 2 for x in items]
    stddev = sqrt(mean(variance))
    return stddev


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
    chars = ('=', '-', '`', "'", '.', '~', '*', '+', '^')
    if level < len(chars):
        return chars[level]
    else:
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
        logging.info(stdout)
    if stderr:
        logging.info(stderr)

    if proc.returncode != 0:
        logging.error("    Command execution failed.")
    return proc.returncode, stdout, stderr


def get_last_successful_build_number(jenkins_url, job_name):
    """Get the number of the last successful build of the given job.

    :param jenkins_url: Jenkins URL.
    :param job_name: Job name.
    :type jenkins_url: str
    :type job_name: str
    :returns: The build number as a string.
    :rtype: str
    """

    url = "{}/{}/lastSuccessfulBuild/buildNumber".format(jenkins_url, job_name)
    cmd = "wget -qO- {url}".format(url=url)

    return execute_command(cmd)


def get_last_completed_build_number(jenkins_url, job_name):
    """Get the number of the last completed build of the given job.

    :param jenkins_url: Jenkins URL.
    :param job_name: Job name.
    :type jenkins_url: str
    :type job_name: str
    :returns: The build number as a string.
    :rtype: str
    """

    url = "{}/{}/lastCompletedBuild/buildNumber".format(jenkins_url, job_name)
    cmd = "wget -qO- {url}".format(url=url)

    return execute_command(cmd)


def archive_input_data(spec):
    """Archive the report.

    :param spec: Specification read from the specification file.
    :type spec: Specification
    :raises PresentationError: If it is not possible to archive the input data.
    """

    logging.info("    Archiving the input data files ...")

    extension = spec.input["file-format"]
    data_files = get_files(spec.environment["paths"]["DIR[WORKING,DATA]"],
                           extension=extension)
    dst = spec.environment["paths"]["DIR[STATIC,ARCH]"]
    logging.info("      Destination: {0}".format(dst))

    try:
        if not isdir(dst):
            makedirs(dst)

        for data_file in data_files:
            logging.info("      Moving the file: {0} ...".format(data_file))
            move(data_file, dst)

    except (Error, OSError) as err:
        raise PresentationError("Not possible to archive the input data.",
                                str(err))

    logging.info("    Done.")


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
    # Nan mean something went wrong.
    # Use 0.0 to cause that being reported as a severe regression.
    bare_data = [0.0 if np.isnan(sample.avg) else sample
                 for _, sample in data.iteritems()]
    # TODO: Put analogous iterator into jumpavg library.
    groups = BitCountingClassifier().classify(bare_data)
    groups.reverse()  # Just to use .pop() for FIFO.
    classification = []
    avgs = []
    active_group = None
    values_left = 0
    avg = 0.0
    for _, sample in data.iteritems():
        if np.isnan(sample.avg):
            classification.append("outlier")
            avgs.append(sample.avg)
            continue
        if values_left < 1 or active_group is None:
            values_left = 0
            while values_left < 1:  # Ignore empty groups (should not happen).
                active_group = groups.pop()
                values_left = len(active_group.values)
            avg = active_group.metadata.avg
            classification.append(active_group.metadata.classification)
            avgs.append(avg)
            values_left -= 1
            continue
        classification.append("normal")
        avgs.append(avg)
        values_left -= 1
    return classification, avgs


def convert_csv_to_pretty_txt(csv_file, txt_file):
    """Convert the given csv table to pretty text table.

    :param csv_file: The path to the input csv file.
    :param txt_file: The path to the output pretty text file.
    :type csv_file: str
    :type txt_file: str
    """

    txt_table = None
    with open(csv_file, 'rb') as csv_file:
        csv_content = csv.reader(csv_file, delimiter=',', quotechar='"')
        for row in csv_content:
            if txt_table is None:
                txt_table = prettytable.PrettyTable(row)
            else:
                txt_table.add_row(row)
        txt_table.align["Test case"] = "l"
    if txt_table:
        with open(txt_file, "w") as txt_file:
            txt_file.write(str(txt_table))


class Worker(multiprocessing.Process):
    """Worker class used to process tasks in separate parallel processes.
    """

    def __init__(self, work_queue, data_queue, func):
        """Initialization.

        :param work_queue: Queue with items to process.
        :param data_queue: Shared memory between processes. Queue which keeps
            the result data. This data is then read by the main process and used
            in further processing.
        :param func: Function which is executed by the worker.
        :type work_queue: multiprocessing.JoinableQueue
        :type data_queue: multiprocessing.Manager().Queue()
        :type func: Callable object
        """
        super(Worker, self).__init__()
        self._work_queue = work_queue
        self._data_queue = data_queue
        self._func = func

    def run(self):
        """Method representing the process's activity.
        """

        while True:
            try:
                self.process(self._work_queue.get())
            finally:
                self._work_queue.task_done()

    def process(self, item_to_process):
        """Method executed by the runner.

        :param item_to_process: Data to be processed by the function.
        :type item_to_process: tuple
        """
        self._func(self.pid, self._data_queue, *item_to_process)
