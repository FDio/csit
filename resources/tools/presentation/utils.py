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

import numpy as np
import pandas as pd

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

    return float(((nr2 - nr1) / nr1) * 100)


def find_outliers(input_data, outlier_const=1.5):
    """Go through the input data and generate two pandas series:
    - input data without outliers
    - outliers.
    The function uses IQR to detect outliers.

    :param input_data: Data to be examined for outliers.
    :param outlier_const: Outlier constant.
    :type input_data: pandas.Series
    :type outlier_const: float
    :returns: Tuple: input data with outliers removed; Outliers.
    :rtype: tuple (trimmed_data, outliers)
    """

    upper_quartile = input_data.quantile(q=0.75)
    lower_quartile = input_data.quantile(q=0.25)
    iqr = (upper_quartile - lower_quartile) * outlier_const
    low = lower_quartile - iqr
    high = upper_quartile + iqr
    trimmed_data = pd.Series()
    outliers = pd.Series()
    for item in input_data.items():
        item_pd = pd.Series([item[1], ], index=[item[0], ])
        if low <= item[1] <= high:
            trimmed_data = trimmed_data.append(item_pd)
        else:
            trimmed_data = trimmed_data.append(pd.Series([np.nan, ],
                                                         index=[item[0], ]))
            outliers = outliers.append(item_pd)

    return trimmed_data, outliers


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
