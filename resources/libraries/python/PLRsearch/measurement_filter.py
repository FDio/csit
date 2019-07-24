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

"""Module holding MeasurementFilter class."""


class MeasurementFilter(object):
    """Class for filtering measurement results.

    An instance of this class acts as a stateful container.
    Each new result needs to be added.
    On demand, list of subset of results is returned.

    Internally, three lists are tracked.
    The output list is an union of roughly half of each tracked lists.
    The ordering is assumed to increase by time of measurement end,
    internally the order of insertion is preserved.

    The intended use is for PLRsearch, hoping to discard early results
    which probably lie outside critical region,
    thus avoiding systematic errors from fitting function shape."""

    def __init__(self, plr_target, list_less=[], list_equal=[], list_more=[]):
        """Initialize new filtered container instance, empty by default.

        Shallow copy (slice) of argument list values is used,
        (and list items are never edited by this class)
        so the original values are not affected (and [] is viable as default).

        :param plr_target: Packet loss ratio for classifying into lists.
        :param list_less: List of results of loss ratio less than the target.
        :param list_equal: List of results of loss ratio equal to the target.
        :param list_more: List of results of loss ratio more than the target.
        :type plr_target: float
        :type list_less: list of MLRsearch.ReceiveRateMeasurement
        :type list_equal: list of MLRsearch.ReceiveRateMeasurement
        :type list_more: list of MLRsearch.ReceiveRateMeasurement
        """
        self.plr_target = plr_target
        self.list_less = list_less[:]
        self.list_equal = list_equal[:]
        self.list_more = list_more[:]

    def __repr__(self):
        """Return string, which interpreted constructs state of self."""
        return ("MeasurementFilter(plr_target={pt!r},list_less={ll!r},"
                "list_equal={le!r},list_more={lm!r})".format(
                    pt=self.plr_target, ll=self.list_less, le=self.list_equal,
                    lm=self.list_more))

    def insert(self, result):
        """Insert next result, return self.

        :param result: The next measurement result to insert.
        :type result: MLRsearch.ReceiveRateMeasurement
        :returns: Updated self.
        :rtype: MeasurementFilter
        """
        plr = result.loss_fraction
        if plr < self.plr_target:
            self.list_less.append(result)
        elif plr > self.plr_target:
            self.list_more.append(result)
        else:
            self.list_equal.append(result)
        return self

    @staticmethod
    def _extend(extend_to, extend_from):
        """Internal utility method. Extend list by subset of list. Return None.

        :param extend_to: The list to extend, edited in place.
        :param extend_from: The list to add from, latter ~half used, not edited.
        :type extend_to: list of object
        :type extend_from: list of object
        """
        if len(extend_from) <= 2:
            extend_to.extend(extend_from)
        else:
            extend_to.extend(extend_from[(len(extend_from) - 1) // 2:])

    def get_list(self):
        """Return list of (near) latter half of result of appropriate plr.

        Results are missing only if more than two results are in a sublist.

        :returns: Filtered list of measurements.
        :rtype: list of MLRsearch.ReceiveRateMeasurement
        """
        list_return = list()
        self._extend(list_return, self.list_less)
        self._extend(list_return, self.list_equal)
        self._extend(list_return, self.list_more)
        return list_return
