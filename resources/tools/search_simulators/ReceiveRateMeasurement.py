# Copyright (c) 2018 Cisco and/or its affiliates.
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


class ReceiveRateMeasurement(object):
    """Structure defining the result of single Rr measurement."""

    def __init__(self, duration, target_tr, transmit_count, drop_count):
        """Constructor, normalize primary and compute secondary quantities."""
        self.duration = float(duration)
        self.target_tr = float(target_tr)
        self.transmit_count = int(transmit_count)
        self.drop_count = int(drop_count)
        self.receive_count = transmit_count - drop_count
        self.transmit_rate = transmit_count / self.duration
        self.drop_rate = drop_count / self.duration
        self.receive_rate = self.receive_count / self.duration
        self.drop_fraction = float(self.drop_count) / self.transmit_count
        # TODO: Do we want to store also the real time (duration + overhead)?

    def __str__(self):
        """Return string reporting Rr."""
        return "d=" + str(self.duration) + ",Tr=" + str(self.target_tr) + ",Df=" + str(self.drop_fraction)

    def __repr__(self):
        """Return string evaluable as a constructor call."""
        return "ReceiveRateMeasurement(duration=" + repr(self.duration) + \
               ",target_tr=" + repr(self.target_tr) + \
               ",transmit_count=" + repr(self.transmit_count) + \
               ",drop_count=" + repr(self.drop_count) + ")"
