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


def datetime_utc_str():
    """Return string formatted current UTC datetime.

    Suitable for creating string timestamps.
    One-liner, but saves line length in some call sites,
    especially when renamed to "now" upon import.

    :returns: Current UTC date and time in human readable form.
    :rtype: str
    """
    return str(datetime.datetime.utcnow())
