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

from resources.libraries.python.MLRsearch.trial_measurement.abstract_measurer import AbstractMeasurer


class TimeTrackingMeasurer(AbstractMeasurer):
    """Delegating measurer, tracks time spent and measurements."""

    def __init__(self, measurer, overhead=0.5):
        """Inject measurer to delegate to."""
        self.measurer = measurer
        self.overhead = overhead
        """Additional time spent on each trial, imagine SSH delay."""
        self.reset()

    def reset(self):
        """Start tracking anew."""
        self.total_time = 0.0
        """Seconds spent measuring since last zero."""
        self.measurements = 0
        """Number of measurements performed."""

    def measure(self, intended_duration, intended_load):
        """Track and delegate."""
        self.total_time += intended_duration + self.overhead
        self.measurements += 1
        result = self.measurer.measure(intended_duration, intended_load)
        result.duration_with_overheads += self.overhead
        return result
