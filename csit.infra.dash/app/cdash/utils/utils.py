# Copyright (c) 2022 Cisco and/or its affiliates.
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

"""Function used by Dash applications.
"""

import pandas as pd
import dash_bootstrap_components as dbc

from numpy import isnan
from dash import dcc
from datetime import datetime

from ..jumpavg import classify
from ..utils.constants import Constants as C
from ..utils.url_processing import url_encode


def classify_anomalies(data):
    """Process the data and return anomalies and trending values.

    Gather data into groups with average as trend value.
    Decorate values within groups to be normal,
    the first value of changed average as a regression, or a progression.

    :param data: Full data set with unavailable samples replaced by nan.
    :type data: OrderedDict
    :returns: Classification and trend values
    :rtype: 3-tuple, list of strings, list of floats and list of floats
    """
    # NaN means something went wrong.
    # Use 0.0 to cause that being reported as a severe regression.
    bare_data = [0.0 if isnan(sample) else sample for sample in data.values()]
    # TODO: Make BitCountingGroupList a subclass of list again?
    group_list = classify(bare_data).group_list
    group_list.reverse()  # Just to use .pop() for FIFO.
    classification = list()
    avgs = list()
    stdevs = list()
    active_group = None
    values_left = 0
    avg = 0.0
    stdv = 0.0
    for sample in data.values():
        if isnan(sample):
            classification.append("outlier")
            avgs.append(sample)
            stdevs.append(sample)
            continue
        if values_left < 1 or active_group is None:
            values_left = 0
            while values_left < 1:  # Ignore empty groups (should not happen).
                active_group = group_list.pop()
                values_left = len(active_group.run_list)
            avg = active_group.stats.avg
            stdv = active_group.stats.stdev
            classification.append(active_group.comment)
            avgs.append(avg)
            stdevs.append(stdv)
            values_left -= 1
            continue
        classification.append("normal")
        avgs.append(avg)
        stdevs.append(stdv)
        values_left -= 1
    return classification, avgs, stdevs


def get_color(idx: int) -> str:
    """Returns a color from the list defined in Constants.PLOT_COLORS defined by
    its index.

    :param idx: Index of the color.
    :type idx: int
    :returns: Color defined by hex code.
    :trype: str
    """
    return C.PLOT_COLORS[idx % len(C.PLOT_COLORS)]


def show_tooltip(tooltips:dict, id: str, title: str,
        clipboard_id: str=None) -> list:
    """Generate list of elements to display a text (e.g. a title) with a
    tooltip and optionaly with Copy&Paste icon and the clipboard
    functionality enabled.

    :param tooltips: Dictionary with tooltips.
    :param id: Tooltip ID.
    :param title: A text for which the tooltip will be displayed.
    :param clipboard_id: If defined, a Copy&Paste icon is displayed and the
        clipboard functionality is enabled.
    :type tooltips: dict
    :type id: str
    :type title: str
    :type clipboard_id: str
    :returns: List of elements to display a text with a tooltip and
        optionaly with Copy&Paste icon.
    :rtype: list
    """

    return [
        dcc.Clipboard(target_id=clipboard_id, title="Copy URL") \
            if clipboard_id else str(),
        f"{title} ",
        dbc.Badge(
            id=id,
            children="?",
            pill=True,
            color="white",
            text_color="info",
            class_name="border ms-1",
        ),
        dbc.Tooltip(
            children=tooltips.get(id, str()),
            target=id,
            placement="auto"
        )
    ]


def label(key: str) -> str:
    """Returns a label for input elements (dropdowns, ...).

    If the label is not defined, the function returns the provided key.

    :param key: The key to the label defined in Constants.LABELS.
    :type key: str
    :returns: Label.
    :rtype: str
    """
    return C.LABELS.get(key, key)


def sync_checklists(options: list, sel: list, all: list, id: str) -> tuple:
    """Synchronize a checklist with defined "options" with its "All" checklist.

    :param options: List of options for the cheklist.
    :param sel: List of selected options.
    :param all: List of selected option from "All" checklist.
    :param id: ID of a checklist to be used for synchronization.
    :returns: Tuple of lists with otions for both checklists.
    :rtype: tuple of lists
    """
    opts = {v["value"] for v in options}
    if id =="all":
        sel = list(opts) if all else list()
    else:
        all = ["all", ] if set(sel) == opts else list()
    return sel, all


def list_tests(selection: dict) -> list:
    """Transform list of tests to a list of dictionaries usable by checkboxes.

    :param selection: List of tests to be displayed in "Selected tests" window.
    :type selection: list
    :returns: List of dictionaries with "label", "value" pairs for a checkbox.
    :rtype: list
    """
    if selection:
        return [{"label": v["id"], "value": v["id"]} for v in selection]
    else:
        return list()


def get_date(s_date: str) -> datetime:
    """Transform string reprezentation of date to datetime.datetime data type.

    :param s_date: String reprezentation of date.
    :type s_date: str
    :returns: Date as datetime.datetime.
    :rtype: datetime.datetime
    """
    return datetime(int(s_date[0:4]), int(s_date[5:7]), int(s_date[8:10]))


def gen_new_url(url_components: dict, params: dict) -> str:
    """Generate a new URL with encoded parameters.

    :param url_components: Dictionary with URL elements. It should contain
        "scheme", "netloc" and "path".
    :param url_components: URL parameters to be encoded to the URL.
    :type parsed_url: dict
    :type params: dict
    :returns Encoded URL with parameters.
    :rtype: str
    """

    if url_components:
        return url_encode(
            {
                "scheme": url_components.get("scheme", ""),
                "netloc": url_components.get("netloc", ""),
                "path": url_components.get("path", ""),
                "params": params
            }
        )
    else:
        return str()


def get_duts(df: pd.DataFrame) -> list:
    """Get the list of DUTs from the pre-processed information about jobs.

    :param df: DataFrame with information about jobs.
    :type df: pandas.DataFrame
    :returns: Alphabeticaly sorted list of DUTs.
    :rtype: list
    """
    return sorted(list(df["dut"].unique()))


def get_ttypes(df: pd.DataFrame, dut: str) -> list:
    """Get the list of test types from the pre-processed information about
    jobs.

    :param df: DataFrame with information about jobs.
    :param dut: The DUT for which the list of test types will be populated.
    :type df: pandas.DataFrame
    :type dut: str
    :returns: Alphabeticaly sorted list of test types.
    :rtype: list
    """
    return sorted(list(df.loc[(df["dut"] == dut)]["ttype"].unique()))


def get_cadences(df: pd.DataFrame, dut: str, ttype: str) -> list:
    """Get the list of cadences from the pre-processed information about
    jobs.

    :param df: DataFrame with information about jobs.
    :param dut: The DUT for which the list of cadences will be populated.
    :param ttype: The test type for which the list of cadences will be
        populated.
    :type df: pandas.DataFrame
    :type dut: str
    :type ttype: str
    :returns: Alphabeticaly sorted list of cadences.
    :rtype: list
    """
    return sorted(list(df.loc[(
        (df["dut"] == dut) &
        (df["ttype"] == ttype)
    )]["cadence"].unique()))


def get_test_beds(df: pd.DataFrame, dut: str, ttype: str, cadence: str) -> list:
    """Get the list of test beds from the pre-processed information about
    jobs.

    :param df: DataFrame with information about jobs.
    :param dut: The DUT for which the list of test beds will be populated.
    :param ttype: The test type for which the list of test beds will be
        populated.
    :param cadence: The cadence for which the list of test beds will be
        populated.
    :type df: pandas.DataFrame
    :type dut: str
    :type ttype: str
    :type cadence: str
    :returns: Alphabeticaly sorted list of test beds.
    :rtype: list
    """
    return sorted(list(df.loc[(
        (df["dut"] == dut) &
        (df["ttype"] == ttype) &
        (df["cadence"] == cadence)
    )]["tbed"].unique()))


def get_job(df: pd.DataFrame, dut, ttype, cadence, testbed):
    """Get the name of a job defined by dut, ttype, cadence, test bed.
    Input information comes from the control panel.

    :param df: DataFrame with information about jobs.
    :param dut: The DUT for which the job name will be created.
    :param ttype: The test type for which the job name will be created.
    :param cadence: The cadence for which the job name will be created.
    :param testbed: The test bed for which the job name will be created.
    :type df: pandas.DataFrame
    :type dut: str
    :type ttype: str
    :type cadence: str
    :type testbed: str
    :returns: Job name.
    :rtype: str
    """
    return df.loc[(
        (df["dut"] == dut) &
        (df["ttype"] == ttype) &
        (df["cadence"] == cadence) &
        (df["tbed"] == testbed)
    )]["job"].item()


def generate_options(opts: list, sort: bool=True) -> list:
    """Return list of options for radio items in control panel. The items in
    the list are dictionaries with keys "label" and "value".

    :params opts: List of options (str) to be used for the generated list.
    :type opts: list
    :returns: List of options (dict).
    :rtype: list
    """
    if sort:
        opts = sorted(opts)
    return [{"label": i, "value": i} for i in opts]


def set_job_params(df: pd.DataFrame, job: str) -> dict:
    """Create a dictionary with all options and values for (and from) the
    given job.

    :param df: DataFrame with information about jobs.
    :params job: The name of job for and from which the dictionary will be
        created.
    :type df: pandas.DataFrame
    :type job: str
    :returns: Dictionary with all options and values for (and from) the
        given job.
    :rtype: dict
    """

    l_job = job.split("-")
    return {
        "job": job,
        "dut": l_job[1],
        "ttype": l_job[3],
        "cadence": l_job[4],
        "tbed": "-".join(l_job[-2:]),
        "duts": generate_options(get_duts(df)),
        "ttypes": generate_options(get_ttypes(df, l_job[1])),
        "cadences": generate_options(get_cadences(df, l_job[1], l_job[3])),
        "tbeds": generate_options(
            get_test_beds(df, l_job[1], l_job[3], l_job[4]))
    }
