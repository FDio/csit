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
    :type idex: int
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


def gen_new_url(parsed_url: dict, params: dict) -> str:
    """Generate a new URL with encoded parameters.

    :param parsed_url: Dictionary with URL elements. It should contain "scheme",
        "netloc" and "path".
    :param params: URL parameters to be encoded to the URL.
    :type parsed_url: dict
    :type params: dict
    :returns Encoded URL with parameters.
    :rtype: str
    """

    if parsed_url:
        return url_encode(
            {
                "scheme": parsed_url.get("scheme", ""),
                "netloc": parsed_url.get("netloc", ""),
                "path": parsed_url.get("path", ""),
                "params": params
            }
        )
    else:
        return str()
