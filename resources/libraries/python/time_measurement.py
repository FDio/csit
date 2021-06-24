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

"""Module with utility functions related to measuring time."""

import datetime


def timstamp_or_now(timestamp=None):
    """Return argument or string formatted current UTC datetime.

    If timestamp is a non-empty string return that, without checking.
    Else, return current time as a human readable string.
    One-liner, but still saves line length.

    :param timestamp: Optional user-supplied value.
    :type timestamp: Optional[str]
    :returns: Current UTC date and time in human readable form.
    :rtype: str
    """
    return timestamp if timestamp else str(datetime.datetime.utcnow())
