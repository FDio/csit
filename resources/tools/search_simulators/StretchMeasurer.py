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

import math
from numpy import random

from resources.libraries.python.MLRsearch.trial_measurement.abstract_measurer import AbstractMeasurer
from resources.libraries.python.MLRsearch.trial_measurement.measurement_result import MeasurementResult
from resources.libraries.python.PLRsearch.PLRsearch import PLRsearch


class StretchMeasurer(AbstractMeasurer):
    """Use PLR stretch function for average, Poisson for randomness."""

    def __init__(
        self,
        mrr=21e5,
        spread=2e5,
        offsets=None,
    ):
        """Constructor, stores parameters to use."""
        self.mrr = mrr
        self.spread = spread
        self.offsets = dict() if offsets is None else offsets

    def measure(self, intended_duration, intended_load):
        """Compute Dx according to Poisson stretch model.

        TODO: Document the model in more detail."""
        offset = self.offsets.get(intended_duration, 0.0)
        log_lossrate_avg = PLRsearch.lfit_stretch(
            trace=lambda x, y: None,
            load=intended_load,
            mrr=self.mrr + offset,
            spread=self.spread,
        )
        loss_probability = math.exp(log_lossrate_avg) / intended_load
        send_count = int(intended_duration * intended_load)
        loss_count = random.binomial(send_count, loss_probability)
        return MeasurementResult(
            intended_duration=intended_duration,
            intended_load=intended_load,
            offered_count=send_count,
            loss_count=loss_count,
        )
