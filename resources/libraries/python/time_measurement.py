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

import dateutil.parser


def timestamp_or_now(timestamp=None):
    """Return argument or string formatted current UTC datetime.

    If timestamp is truthy, convert to string and return,
    without checking whether the value is in any way a valid timestamp.
    Else, return the current time as a human readable string.
    One-liner, but still saves line length.

    When getting current time, the format is to pass validate_rfc3339
    to be usable for "date-time" JSON schema format.
    The current implementation adds separator to improve human readability.
    Due to datetime library limitations,
    the time value is rounded to microseconds.

    :param timestamp: Optional user-supplied value.
    :type timestamp: Optional[str]
    :returns: UTC date and time in RFC 3339 compatible format.
    :rtype: str
    """
    if timestamp:
        # TODO: Support more input types, e.g. datetime.datetime.
        return str(timestamp)
    return datetime.datetime.utcnow().strftime(u"%Y-%m-%dT%H:%M:%S.%fZ")


def posix_from_iso(iso_formatted):
    """Convert from ISO formatted string to POSIX timestamp.

    The ISO 8601 permits wider array of formats than RFC 3339.
    Calling posix_from_iso(timestamp_or_now()) should get the same value
    as calling time.time(), except rounded to microseconds.

    This function probably allows non-UTC values, but that has not been tested.

    :param iso_formatted: Date and time in ISO 8601 (including RFC 3339) format.
    :type iso_formatted: str
    :returns: POSIX (epoch) timestamp.
    :rtype: float
    """
    return dateutil.parser.parse(str(iso_formatted)).timestamp()
