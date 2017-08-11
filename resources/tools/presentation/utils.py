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

"""General purpose utilities.
"""

from os import walk
from os.path import join
from math import sqrt


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

    return (nr1 - nr2) / nr1 * 100


def get_files(path, extension):
    """Generates the list of files to process.

    :param path: Path to files.
    :param extension: Extension of files to process. If it is the empty string,
    all files will be processed.
    :type path: str
    :type extension: str
    :returns: List of files to process.
    :rtype: list
    """

    file_list = list()
    for root, _, files in walk(path):
        for filename in files:
            if extension:
                if filename.endswith(extension):
                    file_list.append(join(root, filename))
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
