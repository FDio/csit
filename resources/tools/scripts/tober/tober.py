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
Converts a Robot Framework log.html file back into an output.xml file.
Name: tober (rebot, backwards)
Version: 0.1.233
"""

import re
import base64
import zlib
import datetime
import xml.etree.ElementTree as ET
import sys
import ast
import html  # For unescaping entities
import json  # Use the much faster and memory-efficient JSON parser

# --- Data Structure Constants from log.html ---

LEVELS = ['TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FAIL', 'SKIP']
STATUSES = ['FAIL', 'PASS', 'SKIP', 'NOT RUN']
KEYWORD_TYPES = [
    'KEYWORD', 'SETUP', 'TEARDOWN', 'FOR', 'ITERATION', 'IF',
    'ELSE IF', 'ELSE', 'RETURN', 'VAR', 'TRY', 'EXCEPT', 'FINALLY',
    'WHILE', 'CONTINUE', 'BREAK', 'ERROR'
]

# --- Global Storage ---
# 'all_strings' will be populated in main()
all_strings = []
# Re-adding the full cache as requested for performance
decoded_strings_cache = {}
base_millis = 0


# --- Helper Functions ---

def exit_with_error(message):
    """Prints an error message to stderr and exits with code 1."""
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def print_parser_error_context(data_str, e):
    """Prints context around a JSONDecodeError or SyntaxError."""
    print(f"Error: Failed to parse data as literal: {e}", file=sys.stderr)

    pos = None
    if hasattr(e, 'pos'): # json.JSONDecodeError
        pos = e.pos
    elif hasattr(e, 'offset'): # ast.SyntaxError
        pos = e.offset

    if pos is not None:
        context_start = max(0, pos - 80)
        context_end = min(len(data_str), pos + 80)
        print("\n--- Context (char " + str(context_start) + " to " + str(context_end) + ") ---", file=sys.stderr)
        print(data_str[context_start:context_end], file=sys.stderr)
        print("---" + " " * (pos - context_start - 1) + "^", file=sys.stderr)
        print(f"--- Error is at index: {pos} ---", file=sys.stderr)
    else:
        print("\n--- Error Context (unknown position) ---", file=sys.stderr)
        print(data_str[:200] + "...", file=sys.stderr)


def get_string(index):
    """
    Fetches a string by its index, decompressing and caching it on-demand.
    """
    if index is None or not isinstance(index, int) or index < 0:
        return ""

    # Check cache first
    if index in decoded_strings_cache:
        return decoded_strings_cache[index]

    # Check bounds of all_strings
    if index >= len(all_strings):
        return ""

    s = all_strings[index]
    decoded_s = ""

    # Decompress/decode the string
    if s and s.startswith('*'):
        decoded_s = s[1:]
    elif s:
        try:
            b64_bytes = s.encode('ascii')
            compressed_bytes = base64.b64decode(b64_bytes)
            decompressed_bytes = zlib.decompress(compressed_bytes)
            decoded_s = decompressed_bytes.decode('utf-8')
        except Exception as e:
            # Store as-is on failure
            print(f"Warning: Failed to decompress string at index {index} ('{s[:40]}...'): {e}", file=sys.stderr)
            decoded_s = s
    else:
        decoded_s = s # Store empty or None

    # Unescape and store in cache
    final_s = html.unescape(decoded_s)
    decoded_strings_cache[index] = final_s
    return final_s


def clean_html_tags(text_str):
    """Removes common, simple HTML tags from a string."""
    if not text_str:
        return ""

    # Replaces <a href="...">text</a> with just "text"
    text_str = re.sub(r'<a\s+href=".*?">(.*?)</a>', r'\1', text_str)

    # Remove <p> and <b> tags. Use non-greedy match for <b>.
    text_str = re.sub(r'</?p>', '', text_str)
    text_str = re.sub(r'<b>(.*?)</b>', r'*\1*', text_str) # Convert <b> to *...*
    text_str = re.sub(r'</?b>', '', text_str) # Clean up any remaining <b>
    text_str = re.sub(r'<br\s*/?>', '\n', text_str) # Convert <br> to newline
    return text_str


def format_timestamp(offset_millis):
    """Converts an offset timestamp from the log into YYYYMMDD HH:MM:SS.mmm format."""
    if offset_millis is None:
        return "N/A"
    try:
        offset_millis = int(offset_millis)
        ts_seconds = (base_millis + offset_millis) / 1000.0
        # Create datetime object, explicitly interpreting the timestamp as UTC
        dt_aware = datetime.datetime.fromtimestamp(ts_seconds, tz=datetime.timezone.utc)
        # Create a "naive" object (no tzinfo) from the UTC time
        dt_naive = dt_aware.replace(tzinfo=None)
        # Format the naive object, which will not have the +00:00 offset
        return dt_naive.isoformat(timespec='milliseconds')
    except (ValueError, TypeError):
        return "N/A"


def create_status_element(parent_xml, status_arr, failure_message_str=None):
    """
    Creates a <status> element.
    Uses failure_message_str for FAIL, or looks up PASS message.
    """

    status_code = status_arr[0]
    status_text = None

    if status_code == 0: # FAIL
        status_text = failure_message_str
    else: # PASS, SKIP, etc.
        # Use the message from status_arr[3] if it exists
        status_text = clean_html_tags(get_string(status_arr[3] if len(status_arr) > 3 else None))


    status_xml = ET.SubElement(parent_xml, "status")
    # Set attributes in the order they typically appear in output.xml
    status_xml.set("status", STATUSES[status_code])
    status_xml.set("starttime", format_timestamp(status_arr[1]))
    status_xml.set("endtime", format_timestamp(status_arr[1] + status_arr[2]))
    if status_text:
        status_xml.text = status_text


def format_failure_message(failures, preamble=None):
    """Combines a list of failures into a single string."""
    if not failures:
        return None

    if len(failures) == 1:
        msg = failures[0]
    else:
        parts = [f"{i+1}) {msg}" for i, msg in enumerate(failures)]
        msg = "Several failures occurred:\n\n" + "\n\n".join(parts)

    if preamble:
        return f"{preamble}\n{msg}"
    else:
        return msg


# --- XML Parsing Functions ---

def separate_body_items(body_array):
    """Splits a body list into (setups_and_body, teardowns)."""
    setups_and_body = []
    teardowns = []

    if not isinstance(body_array, list):
        return setups_and_body, teardowns

    for item_arr in body_array:
        if len(item_arr) < 5: # It's a message
            setups_and_body.append(item_arr)
        else: # It's a keyword
            kw_type = KEYWORD_TYPES[item_arr[0]]
            if kw_type == 'TEARDOWN':
                teardowns.append(item_arr)
            else:
                setups_and_body.append(item_arr)

    return setups_and_body, teardowns


def parse_item_list(item_list, parent_xml):
    """
    Parses a list of body items (which can be KWs or MSGs).
    Returns a list of failure message strings.
    """
    failures = []
    if not isinstance(item_list, list):
        return failures

    for item_arr in item_list:
        if len(item_arr) < 5: # It's a message
            msg_level = item_arr[1]
            msg_text = get_string(item_arr[2])
            parse_message(item_arr, parent_xml)
            if msg_level == 5: # 5 is 'FAIL'
                failures.append(clean_html_tags(msg_text))
        else: # It's a keyword or control structure
            # This keyword's failure message is the *combined* message of its children
            kw_fail_msg = parse_keyword(item_arr, parent_xml)
            if kw_fail_msg:
                failures.append(kw_fail_msg)

    return failures


def parse_suite(suite_arr, parent_xml, id_index=0):
    """Parses a suite array and appends it to the parent XML element."""
    status_arr = suite_arr[5]

    if parent_xml.tag == "suite":
        suite_id = f"{parent_xml.get('id')}-s{id_index}"
    else:
        suite_id = "s1" # Root suite

    # Create element and set attributes
    suite_xml = ET.SubElement(parent_xml, "suite")
    suite_xml.set("id", suite_id)
    suite_xml.set("name", get_string(suite_arr[0]))
    suite_xml.set("source", get_string(suite_arr[1]))

    (setups, teardowns) = separate_body_items(suite_arr[8])

    setup_failures = parse_item_list(setups, suite_xml)  # Parse Setups

    for i, child_suite_arr in enumerate(suite_arr[6]):
        parse_suite(child_suite_arr, suite_xml, id_index=i + 1)

    for i, test_arr in enumerate(suite_arr[7]):
        parse_test(test_arr, suite_xml, suite_id, i + 1)

    td_failures = parse_item_list(teardowns, suite_xml) # Parse teardowns

    # <doc> elements are no longer created
    # Add metadata (conditionally)
    meta_items = suite_arr[4]
    if meta_items:
        meta_xml = ET.SubElement(suite_xml, "metadata")
        for meta_item in meta_items:
            ET.SubElement(meta_xml, "item", name=get_string(meta_item[0])).text = clean_html_tags(get_string(meta_item[1]))

    # --- Determine Suite Failure Message ---
    my_failure_msg = None
    if status_arr[0] == 0: # FAIL

        setup_fail_msg = format_failure_message(setup_failures)
        td_fail_msg = format_failure_message(td_failures, "teardown failed:")

        if setup_fail_msg and td_fail_msg:
            my_failure_msg = f"{setup_fail_msg}\n\nAlso {td_fail_msg}"
        else:
            my_failure_msg = setup_fail_msg or td_fail_msg

    create_status_element(suite_xml, status_arr, my_failure_msg)


def parse_test(test_arr, parent_xml, parent_id, index):
    """Parses a test array and appends it to the parent XML element."""
    status_arr = test_arr[4]
    test_id = f"{parent_id}-t{index}"
    test_name = get_string(test_arr[0])
    timeout_str_raw = get_string(test_arr[1]) # test_arr[1] is timeout

    test_xml = ET.SubElement(parent_xml, "test")
    # Set attributes
    test_xml.set("id", test_id)
    test_xml.set("name", test_name)

    # Parse Setup/Body KWs
    (setups_and_body, teardowns) = separate_body_items(test_arr[5])
    body_failures = parse_item_list(setups_and_body, test_xml) # Parse Setup/Body

    # Parse teardown KWs
    td_failures = parse_item_list(teardowns, test_xml)      # Parse teardown

    # <doc> elements are no longer created

    # Add <tag> elements (conditionally)
    tag_indices = test_arr[3]
    if tag_indices:
        for tag_idx in tag_indices:
            tag_str = clean_html_tags(get_string(tag_idx))
            if tag_str:
                ET.SubElement(test_xml, "tag").text = tag_str

    # Add <timeout> element (moved here, before status)
    if timeout_str_raw:
        # Use the raw string from log.html directly
        ET.SubElement(test_xml, "timeout").set("value", timeout_str_raw)


    # --- Determine Test Failure Message ---
    my_failure_msg = None
    if status_arr[0] == 0: # FAIL
        body_fail_msg = format_failure_message(body_failures)
        td_fail_msg = format_failure_message(td_failures, "teardown failed:")

        if body_fail_msg and td_fail_msg:
            my_failure_msg = f"{body_fail_msg}\n\nAlso {td_fail_msg}"
        else:
            my_failure_msg = body_fail_msg or td_fail_msg

    create_status_element(test_xml, status_arr, my_failure_msg)


def parse_keyword(kw_arr, parent_xml):
    """
    Parses a keyword array and appends it to the parent XML element.
    Returns its own failure message (if any) for the parent to use.
    """
    status_arr = kw_arr[8]
    kw_type = KEYWORD_TYPES[kw_arr[0]]
    timeout_str_raw = get_string(kw_arr[3]) # kw_arr[3] is for timeout

    # --- Handle special control structures ---

    if kw_type == 'FOR':
        name_str = get_string(kw_arr[1]) # e.g., "${variable}   IN   @{variables}"
        name_parts = re.split(r'\s{2,}', name_str)

        var_name = name_parts[0] if len(name_parts) > 0 else ""
        flavor = name_parts[1] if len(name_parts) > 1 else "IN" # Default to IN
        value_parts = name_parts[2:] if len(name_parts) > 2 else []

        for_xml = ET.SubElement(parent_xml, "for")
        for_xml.set("flavor", flavor)

        (setups_and_body, teardowns) = separate_body_items(kw_arr[9]) # body = <iter> blocks
        body_failures = parse_item_list(setups_and_body, for_xml)
        td_failures = parse_item_list(teardowns, for_xml) # Should be empty

        # Add <var> and <value> tags before status
        if var_name:
            ET.SubElement(for_xml, "var").text = var_name
        for val in value_parts:
            ET.SubElement(for_xml, "value").text = val

        my_failure_msg = None
        if status_arr[0] == 0: # FAIL
            all_failures = body_failures + td_failures
            my_failure_msg = format_failure_message(all_failures)

        create_status_element(for_xml, status_arr, my_failure_msg)
        return my_failure_msg

    if kw_type == 'ITERATION':
        name_str = get_string(kw_arr[1]) # e.g., "${variable} = DUT1"
        name_parts = name_str.split(' = ', 1)
        var_name = ""
        var_value = ""
        if len(name_parts) == 2:
            var_name = name_parts[0].strip()
            var_value = name_parts[1].strip()

        iter_xml = ET.SubElement(parent_xml, "iter")

        (setups_and_body, teardowns) = separate_body_items(kw_arr[9]) # body = kws inside iter
        body_failures = parse_item_list(setups_and_body, iter_xml)
        td_failures = parse_item_list(teardowns, iter_xml)

        # Add the <var> tag at the end, before status
        if var_name:
            var_xml = ET.SubElement(iter_xml, "var")
            var_xml.set("name", var_name)
            var_xml.text = var_value

        my_failure_msg = None
        if status_arr[0] == 0: # FAIL
            all_failures = body_failures + td_failures
            my_failure_msg = format_failure_message(all_failures)

        create_status_element(iter_xml, status_arr, my_failure_msg)
        return my_failure_msg

    # --- Default KW/SETUP/TEARDOWN processing ---

    kw_xml = ET.SubElement(parent_xml, "kw")

    # Set attributes in the order of the original output.xml
    # 1. name
    kw_xml.set("name", get_string(kw_arr[1]))

    # 2. owner (if present)
    if get_string(kw_arr[2]): # library
        kw_xml.set("owner", get_string(kw_arr[2]))

    # 3. type (if not default KEYWORD)
    if kw_type != "KEYWORD":
        kw_xml.set("type", kw_type) # Add type (SETUP, TEARDOWN, FOR, etc.)

    # Parse child items (KWs/Msgs)
    (setups_and_body, teardowns) = separate_body_items(kw_arr[9])

    body_failures = parse_item_list(setups_and_body, kw_xml)
    td_failures = parse_item_list(teardowns, kw_xml)

    # --- Add metadata elements (conditionally) ---

    # Add <var> (was <assign> in 204)
    var_assign_str = clean_html_tags(get_string(kw_arr[6]))
    if var_assign_str:
        # Split variables that are space-separated in log.html
        var_list = re.split(r'\s{2,}', var_assign_str)
        for var_text in var_list:
            if var_text:
                ET.SubElement(kw_xml, "var").text = var_text

    # Add <arg> tags (before <doc>)
    args_str = clean_html_tags(get_string(kw_arr[5]))
    if args_str:
        # log.html stores args as a single string.
        # Robot Framework often separates args with two or more spaces.
        args_list = re.split(r'\s{2,}', args_str)
        for arg_text in args_list:
            # We check `if arg_text is not None` because re.split can return
            # empty strings which are valid arguments (e.g. ${EMPTY})
            if arg_text is not None:
                ET.SubElement(kw_xml, "arg").text = arg_text

    # <doc> elements are no longer created

    # Add <tags>
    tags_text = get_string(kw_arr[7])
    if tags_text:
        tags_xml = ET.SubElement(kw_xml, "tags")
        # Assuming tags are comma-separated
        for tag in tags_text.split(','):
            if tag.strip():
                ET.SubElement(tags_xml, "tag").text = clean_html_tags(tag.strip())

    # Add <timeout> element (moved here, before status)
    if timeout_str_raw:
        # Use the raw string from log.html directly
        ET.SubElement(kw_xml, "timeout").set("value", timeout_str_raw)

    # --- Determine Keyword Failure Message ---
    my_failure_msg = None
    if status_arr[0] == 0: # FAIL
        body_fail_msg = format_failure_message(body_failures)
        td_fail_msg = format_failure_message(td_failures, "keyword teardown failed:")

        if body_fail_msg and td_fail_msg:
            my_failure_msg = f"{body_fail_msg}\n\nAlso {td_fail_msg}"
        else:
            my_failure_msg = body_fail_msg or td_fail_msg

    elif status_arr[0] == 3: # NOT RUN
        # Check if this "NOT RUN" was caused by a propagated timeout
        # by looking for a FAIL message in its own body
        if isinstance(kw_arr[9], list):
            for item in kw_arr[9]:
                if len(item) < 5 and item[1] == 5: # It's a FAIL msg
                    my_failure_msg = clean_html_tags(get_string(item[2]))
                    break

    create_status_element(kw_xml, status_arr, my_failure_msg)
    return my_failure_msg


def parse_message(msg_arr, parent_xml):
    """Parses a message array and appends it to the parent XML element."""
    msg_xml = ET.SubElement(parent_xml, "msg")
    msg_text = get_string(msg_arr[2])
    is_html = False

    # Check for HTML
    if msg_arr[1] == 2 and msg_text.startswith("<b>") and "</b>" in msg_text: # INFO level and bold
         msg_xml.set("html", "true")
         is_html = True

    # Set attributes in output.xml order
    # output.xml uses 'time', not 'timestamp'
    msg_xml.set("time", format_timestamp(msg_arr[0]))
    msg_xml.set("level", LEVELS[msg_arr[1]])

    # Only clean tags if it's not marked as HTML
    if is_html:
        msg_xml.text = msg_text
    else:
        msg_xml.text = clean_html_tags(msg_text)


# --- Main Execution ---

def main():
    global decoded_strings, base_millis, all_strings

    log_file = "log.html"
    output_file = "output_from_log.xml"

    print(f"Reading {log_file}...")
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
    except FileNotFoundError:
        exit_with_error(f"{log_file} not found.")
    except Exception as e:
        exit_with_error(f"Error reading file: {e}")

    print("Parsing data structures...")
    sparts = {}
    for match in re.finditer(r'window\.sPart(\d+)\s*=\s*(\[.*?\]);', log_content, re.DOTALL):
        sparts[match.group(1)] = match.group(2)

    suite_match = re.search(r'window\.output\["suite"\]\s*=\s*(\[.*?\]);', log_content, re.DOTALL)
    base_millis_match = re.search(r'window\.output\["baseMillis"\]\s*=\s*(\d+);', log_content)
    generated_match = re.search(r'window\.output\["generated"\]\s*=\s*(\d+);', log_content)
    strings_matches = re.finditer(r'window\.output\["strings"\]\.concat\((\[.*?\])\);', log_content, re.DOTALL)
    generator_match = re.search(r'<meta content="(Robot Framework.*?)" name="Generator">', log_content)

    if not all([suite_match, base_millis_match, generated_match, generator_match]):
        exit_with_error("Could not find all required window.output.* variables or generator meta tag in log.html.")

    suite_data_str = suite_match.group(1)

    print("Replacing nested sPart variables...")

    def sPart_replacer(match):
        """Callback for re.sub to replace window.sPartX"""
        sPart_num = match.group(1)
        return sparts.get(sPart_num, "null") # "null" is JSON-safe

    # --- MEMORY FIX: Use a small, constant limit for the sPart replacement loop ---
    i = 0
    limit = 10 # A sane, small limit to prevent memory thrashing
    while re.search(r"window\.sPart\d+", suite_data_str) and i < limit:
        suite_data_str = re.sub(r"window\.sPart(\d+)", sPart_replacer, suite_data_str)
        i += 1

    if i == limit:
         exit_with_error("Recursive sPart replacement failed or hit limit.")


    print("Pre-caching all strings...")
    list_str = ""
    try:
        for match in strings_matches:
            list_str = match.group(1)
            # This populates the global all_strings
            all_strings.extend(ast.literal_eval(list_str))
    except (SyntaxError, ValueError) as e:
        print_parser_error_context(list_str, e)
        exit_with_error("Failed to parse window.output[\"strings\"].concat() data.")


    if not all_strings:
        exit_with_error("No strings found. The regex for `window.output[\"strings\"].concat()` might have failed.")

    # Pre-populate the cache as requested
    for i in range(len(all_strings)):
        get_string(i)

    print(f"Cached {len(decoded_strings_cache)} strings.")

    try:
        base_millis = int(base_millis_match.group(1))
        generated_millis = int(generated_match.group(1))
    except Exception as e:
        exit_with_error(f"Could not parse timestamp data: {e}")

    print("Building XML...")

    try:
        print("Converting Python literal string to JSON-compatible string...")
        # Convert any Python-specific literals to JSON-compatible
        suite_data_str = suite_data_str.replace("None", "null")
        suite_data_str = suite_data_str.replace("True", "true")
        suite_data_str = suite_data_str.replace("False", "false")

        print("Parsing data string with json.loads...")
        suite_data = json.loads(suite_data_str)

    except (json.JSONDecodeError, SyntaxError, ValueError) as e:
        print_parser_error_context(suite_data_str, e)
        exit_with_error(f"Failed to parse window.output[\"suite\"] data as JSON: {e}")
    except RecursionError as e:
        exit_with_error(f"Failed to parse data: Exceeded Python's recursion depth. The data is too nested. Error: {e}")


    # Create root <robot> tag
    generated_ts_seconds = (base_millis + generated_millis) / 1000.0
    # Create datetime object, explicitly interpreting the timestamp as UTC
    generated_dt_aware = datetime.datetime.fromtimestamp(generated_ts_seconds, tz=datetime.timezone.utc)
    # Create a "naive" object (no tzinfo) from the UTC time
    generated_dt_naive = generated_dt_aware.replace(tzinfo=None)

    # Format the naive object, which will not have the +00:00 offset
    generated_str = generated_dt_naive.isoformat(timespec='milliseconds')
    generator_str = generator_match.group(1)

    root_xml = ET.Element("robot")
    # Set attributes in original output.xml order
    root_xml.set("generator", generator_str)
    root_xml.set("generated", generated_str)
    root_xml.set("rpa", "false")  # Hardcoded based on provided output.xml
    root_xml.set("schemaversion", "5") # Hardcoded based a_s on provided output.xml

    # Start parsing from the root suite
    parse_suite(suite_data, root_xml)

    # TODO: Parse and add <statistics> and <errors> blocks

    print("Indenting XML...")
    ET.indent(root_xml, space="")

    print(f"Writing {output_file}...")
    try:
        # Serialize to string first
        xml_str = ET.tostring(root_xml, encoding='unicode', method='xml')

        # Create the correct declaration with double quotes
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'

        # Write the declaration and the indented tree
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_declaration)
            f.write(xml_str)

        print(f"Successfully converted {log_file} to {output_file}")

    except Exception as e:
        exit_with_error(f"Error writing XML file: {e}")


if __name__ == "__main__":
    main()
