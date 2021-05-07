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

"""Module with keywords that publish parts of result structure.
"""

from robot.libraries.BuiltIn import BuiltIn


def append_mrr_value(value):
    """Store mrr value to proper place so it is dumped into json.

    The inner node "value" may or may not exist before calling this.
    Test type is overwritten to MRR.

    :param values: Forwarding rate from MRR test, unit specified elsewhere.
    :type values: float
    """
    data = BuiltIn().get_library_instance(
        u"resources.libraries.python.model.export_json"
    )
    test = data.get_subdata([u"test"])
    test[u"test-type"] = u"MRR"
    test = data.get_subdata([u"test", u"results", u"test"])
    if u"value" not in test:
        test[u"value"] = dict()
    value = test[u"value"]
    if u"receive-rate" not in value:
        value[u"receive-rate"] = list()
    receive_rate = value[u"receive-rate"]
    receive_rate.append(float(value))


def export_mrr_unit(unit):
    """Store MRR unit so it is dumped into json.

    If a previous value exists, it is overwritten silently.

    :param unit: Unit of MRR forwarding rate, either cps or pps.
    :type unit: str
    """
    data = BuiltIn().get_library_instance(
        u"resources.libraries.python.model.export_json"
    )
    test = data.get_subdata([u"test", u"results", u"test"])
    test[u"unit"] = str(unit)
