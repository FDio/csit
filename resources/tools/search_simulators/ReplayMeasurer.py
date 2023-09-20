# Copyright (c) 2023 Cisco and/or its affiliates.
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

import math
from numpy import random

from resources.libraries.python.MLRsearch.trial_measurement.abstract_measurer import AbstractMeasurer
from resources.libraries.python.MLRsearch.trial_measurement.measurement_result import MeasurementResult


class ReplayMeasurer(AbstractMeasurer):
    """Repeat pre-prepared results."""

    recipe = [
        # [duration, load, offered_count, loss_count, duration_with_overhead]
        [1.0, 28812908.182865925, 40333438, 35599701, 1.5071470215916634],
        [1.0, 28812908.182865925, 40659204, 35885005, 1.5073414891958237],
        [1.0,  2376912.4317775215, 4753828,   631889, 1.5080324076116085],
        [1.0,  2055481.140575476,  4110966,   554864, 1.5073809213936329],
        [1.0,  1149515.2933531322, 2299032,   306656, 1.5073035918176174],
        [1.0,   112439.72694280349, 224880,        0, 1.5071258544921875],
        [1.0,   318784.2368350702,  637572,        0, 1.5070874392986298],
        [1.0,   605348.9535150945, 1210700,        0, 1.5070664584636688],
        [1.0,   834180.9635090667, 1668366,        0, 1.5072626024484634],
        [1.0,   979236.3223337485, 1958478,        0, 1.508693639189005],
        [1.0,  1060965.1871430662, 2121934,        0, 1.5074080973863602],
        [1.0,  1104353.072317101,  2208708,        0, 1.5074074678122997],
        [1.0,  1126707.9239492475, 2253420,        0, 1.5074902474880219],
        [1.0,  1138054.475726806,  2276112,        0, 1.50728327780962],
        [1.0,  1138054.475726806,  2276112,        0, 1.5073307938873768],
        [1.0,  1149515.2933531322, 2297884,        0, 1.5072832368314266],
#        [1.0,  1143770.5296592254, 2287544,        0, 1.507393952459097],
    ]


    def __init__(self):
        """Reset counter."""
        self.count = 0

    def measure(self, intended_duration, intended_load):
        """Check inputs, return result."""
        data = self.recipe[self.count]
        self.count += 1
        assert intended_duration == data[0]
        assert intended_load == data[1]
        # TODO: Add explicit intended count so unsent packets are correct.
        intended_count = int(data[0] * data[1] * 2)
        if data[2] / intended_count > 0.99:
            intended_count = data[2]
        return MeasurementResult(
            intended_duration=data[0],
            intended_load=data[1],
            offered_count=data[2],
            loss_count=data[3],
            intended_count=intended_count,
            duration_with_overheads=data[4],
        )
