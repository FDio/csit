#!/usr/bin/env python3

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

"""Script for mass editing suites to add suite tag there."""

import sys

from io import open
from glob import glob


def edit(text, suite_tag):
    """Return the edited text.

    :param text: Content of .robot file as read.
    :param suite_tag: The value of suite tag to insert if not present.
    :type text: str
    :type suite_tag: str
    :returns: New content to rewrite the file with.
    :rtype: str
    :raises RuntimeError: If something failed during the editing.
    """
    lines_out = list()
    # Using an iterator to allow several loops in sequence.
    lines_in = iter(text.splitlines())
    # Searching where tags begin.
    while 1:
        line = next(lines_in)
        if u"Force Tags" in line:
            break
        lines_out.append(line)
    # The foce tags line has not been written yet.
    # Search for "empty" line after tags.
    while 1:
        line_previous = line
        lines_out.append(line)
        line = next(lines_in)
        if line == u"|":
            break
    # All tags are written, we remember the last one.
    line_suite = u"| ... | " + suite_tag
    if line_suite != line_previous:
        lines_out.append(line_suite)
    # Write the empty line and copy the rest.
    lines_out.append(line)
    for line in lines_in:
        lines_out.append(line)
    # Make sure the last line ends properly.
    lines_out.append(u"")
    while lines_out[-2] == u"":
        lines_out.pop()
    return u"\n".join(lines_out)


def main():
    """Do it all, return return code.

    :returns: 0 as everything works.
    :rtype: int
    """
    for filename in glob(u"*.robot"):
        if u"__init__" in filename:
            continue
        with open(filename, u"rt", encoding="utf8") as file_in:
            text_in = file_in.read()
        dash_split = filename.split(u"-", 1)
        if len(dash_split[0]) <= 4:
            # It was something like "2n1l", we need one more split.
            dash_split = dash_split[1].split(u"-", 1)
        suite_id = dash_split[1].split(u".", 1)[0]
        suite_tag = suite_id.rsplit(u"-", 1)[0]
        text_out = edit(text_in, suite_tag)
        with open(filename, u"wt", encoding="utf8") as file_out:
            file_out.write(text_out)
    return 0


if __name__ == u"__main__":
    sys.exit(main())
