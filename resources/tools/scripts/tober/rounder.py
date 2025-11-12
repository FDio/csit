#!/usr/bin/env python3

# Copyright (c) 2025 Cisco and/or its affiliates.
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
Reads a Robot Framework output.xml file and modifies it to match
the data available in a log.html file.

- Rounds all timestamps to 3 decimal places (milliseconds).
- Converts <status> tags from (start, elapsed) to (starttime, endtime).
- Removes all <doc> elements.
- Removes the "line" attribute from all <test> elements.
- Removes the "source_name" attribute from all <kw> elements.
- Removes the <statistics> and <errors> elements.

Name: rounder.py (v0.1.15)
"""

import xml.etree.ElementTree as ET
import datetime
import sys
from typing import Optional


def round_timestamp_dt(ts_str: str) -> Optional[datetime.datetime]:
    """
    Takes an ISO timestamp string and rounds it to the nearest millisecond.

    :param ts_str: The ISO timestamp string to parse.
    :type ts_str: str
    :returns: A datetime object rounded to the nearest millisecond, or None.
    :rtype: Optional[datetime.datetime]
    """
    if not ts_str:
        return None
    try:
        dt = datetime.datetime.fromisoformat(ts_str)
        # Round microsecond to nearest millisecond (1000 us)
        rounded_us = round(dt.microsecond / 1000) * 1000

        # Re-build datetime, handling 1-second rollover
        dt_base = dt.replace(microsecond=0)
        delta = datetime.timedelta(microseconds=rounded_us)
        return dt_base + delta

    except (ValueError, TypeError):
        print(
            f"Warning: Could not parse timestamp '{ts_str}'",
            file=sys.stderr,
        )
        return None


def main() -> None:
    """
    Main execution function.
    Reads, processes, and writes the XML file.

    :returns: None
    :rtype: None
    """
    input_file = "output.xml"
    output_file = "output_rounded.xml"

    print(f"Reading {input_file}...")
    try:
        tree = ET.parse(input_file)
    except FileNotFoundError:
        print(f"Error: {input_file} not found.", file=sys.stderr)
        sys.exit(1)
    except ET.ParseError as e:
        print(f"Error: Failed to parse XML in {input_file}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    root = tree.getroot()

    print(
        "Rounding timestamps, converting <status>, removing <doc>,"
        " <statistics>, <errors>, line numbers, and source_names..."
    )

    docs_to_remove = []

    for el in root.iter():
        try:
            if el.tag == "robot":
                gen_str = el.get("generated")
                if gen_str:
                    rounded_dt = round_timestamp_dt(gen_str)
                    if rounded_dt:
                        el.set(
                            "generated",
                            rounded_dt.isoformat(timespec="milliseconds"),
                        )

            elif el.tag == "msg":
                time_str = el.get("time")
                if time_str:
                    rounded_dt = round_timestamp_dt(time_str)
                    if rounded_dt:
                        el.set(
                            "time",
                            rounded_dt.isoformat(timespec="milliseconds"),
                        )

            elif el.tag == "doc":
                docs_to_remove.append(el)

            elif el.tag == "test":
                if "line" in el.attrib:
                    del el.attrib["line"]

            elif el.tag == "kw":
                if "source_name" in el.attrib:
                    del el.attrib["source_name"]

            elif el.tag == "status":
                start_str = el.get("start")
                elapsed_str = el.get("elapsed")

                # Only process if it has start/elapsed (not starttime/endtime)
                if start_str and elapsed_str:
                    starttime_dt = round_timestamp_dt(start_str)

                    # elapsed is in float seconds (e.g., "0.000331")
                    elapsed_ms = int(round(float(elapsed_str) * 1000))

                    elapsed_delta = datetime.timedelta(milliseconds=elapsed_ms)
                    endtime_dt = starttime_dt + elapsed_delta

                    del el.attrib["start"]
                    del el.attrib["elapsed"]

                    # (Preserve "status" which is already there)
                    el.set(
                        "starttime",
                        starttime_dt.isoformat(timespec="milliseconds"),
                    )
                    el.set(
                        "endtime",
                        endtime_dt.isoformat(timespec="milliseconds"),
                    )

        except Exception as e:
            print(
                f"Warning: Failed to process element <{el.tag}>: {e}",
                file=sys.stderr,
            )

    if docs_to_remove:
        print(f"Removing {len(docs_to_remove)} <doc> elements...")
        # Create a parent map to find who to remove from
        parents = {c: p for p in root.iter() for c in p}
        for el in docs_to_remove:
            if el in parents:
                parents[el].remove(el)

    stats = root.find("statistics")
    if stats is not None:
        print("Removing <statistics> element...")
        root.remove(stats)

    errors = root.find("errors")
    if errors is not None:
        print("Removing <errors> element...")
        root.remove(errors)

    print("Indenting XML...")
    ET.indent(root, space="")

    print(f"Writing {output_file}...")
    try:
        xml_str = ET.tostring(root, encoding="unicode", method="xml")

        # Create the correct declaration with double quotes
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(xml_declaration)
            f.write(xml_str)

        print(f"Successfully created {output_file}")

    except Exception as e:
        print(f"Error writing XML file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
