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

"""
Script to convert hdrh coded archive into something human readable.
"""

import hdrh.histogram
import sys

def main():
    """Read coded form from stdin, write readable form to stdout.

    The last number is also the total number in histogram.

    Example call:
    $ echo 'HISTFAAAAEN4nJNpmSzMwMCgzAABzFCaEUzOmNZg/wEiIM1Xso31kOArrTcBDwqfdDMuaGC8EPXC4JnoH/Ye5jZGFRY2JgD6whIu' | python3 tab.py

    Next 7 packets have latency 14 microseconds.
    Next 65 packets have latency 15 microseconds.
    Next 412 packets have latency 16 microseconds.
    Next 1533 packets have latency 17 microseconds.
    Next 4274 packets have latency 18 microseconds.
    Next 9448 packets have latency 19 microseconds.
    Next 16728 packets have latency 20 microseconds.
    Next 25674 packets have latency 21 microseconds.
    Next 33882 packets have latency 22 microseconds.
    Next 39682 packets have latency 23 microseconds.
    Next 42806 packets have latency 24 microseconds.
    Next 44201 packets have latency 25 microseconds.
    Next 44711 packets have latency 26 microseconds.
    Next 44909 packets have latency 27 microseconds.
    Next 44976 packets have latency 28 microseconds.
    Next 44994 packets have latency 29 microseconds.
    Next 44996 packets have latency 30 microseconds.
    Next 44999 packets have latency 31 microseconds.
    Next 45000 packets have latency 32 microseconds.
    """
    code = sys.stdin.read()
    decoded = hdrh.histogram.HdrHistogram.decode(code)
    total = decoded.get_total_count()
    previous = 0
    for item in decoded.get_recorded_iterator():
        value = item.value_iterated_to
        percentile = item.percentile_level_iterated_to
        up_to = round(percentile / 100 * total)
        diff = up_to - previous
        print(f"Next {diff} packets have latency {value} microseconds.")
        previous = up_to
    print(f"{total} packets total.")
    return 0

if __name__ == u"__main__":
    sys.exit(main())
