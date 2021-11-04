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


def timestamp_or_now(timestamp=None):
    """Return argument or string formatted current UTC datetime.

    If timestamp is truthy, convert to string and return,
    without checking whether the value is in any way a valid timestamp.
    Else, return current time as a human readable string.
    One-liner, but still saves line length.

    :param timestamp: Optional user-supplied value.
    :type timestamp: Optional[str]
    :returns: UTC date and time in ISO format.
    :rtype: str
    """
    return str(timestamp) if timestamp else str(datetime.datetime.utcnow())


def posix_from_iso(iso_formatted):
    """Convert from ISO formatted string to POSIX timestamp.

    posix_from_iso(timestamp_or_now()) should be the same as time.time(),
    except maybe some small rounding error at nanosecond level.

    This function probably allows non-UTC values, but that has not been tested.

    :param iso_formatted: Date and time in ISO format, ideally for UTC.
    :type iso_formatted: str
    :returns: POSIX (epoch) timestamp.
    :rtype: float
    """
    return datetime.datetime.fromisoformat(iso_formatted).timestamp()
