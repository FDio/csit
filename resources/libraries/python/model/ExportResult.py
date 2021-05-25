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

from resources.libraries.python.jumpavg.AvgStdevStats import AvgStdevStats


def append_mrr_value(mrr_value):
    """Store mrr value to proper place so it is dumped into json.

    The inner node "value" may or may not exist before calling this.
    Test type is not overwritten here, but when setting unit.

    :param mrr_value: Forwarding rate from MRR trial, unit specified elsewhere.
    :type mrr_value: float
    """
    lib = BuiltIn().get_library_instance(
        u"resources.libraries.python.model.export_json"
    )
    results_node = lib.data[u"test"][u"results"]
    if u"samples" not in results_node:
        results_node[u"samples"] = list()
    samples = results_node[u"samples"]
    samples.append(float(mrr_value))
    # TODO: Implement incremental udates.
    # That means storing starts somewhere json does not export.
    stats = AvgStdevStats.for_runs(samples)
    results_node[u"avg"] = stats.avg
    results_node[u"stdev"] = stats.stdev

def export_mrr_unit(unit):
    """Store MRR unit so it is dumped into json.

    If a previous value exists, it is overwritten silently.
    test type is set (overwritten) to MRR.

    :param unit: Unit of MRR forwarding rate, either cps or pps.
    :type unit: str
    """
    lib = BuiltIn().get_library_instance(
        u"resources.libraries.python.model.export_json"
    )
    lib.data[u"test"][u"test-type"] = u"MRR"
    lib.data[u"test"][u"results"][u"unit"] = str(unit)
