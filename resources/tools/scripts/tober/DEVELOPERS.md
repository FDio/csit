# Tober Developer Notes

This document explains the design decisions, trade-offs, and utilities (like `rounder.py`) used in the `tober` project.

## The `rounder.py` Utility

During development, we discovered that comparing `tober`'s output to an original `output.xml` was difficult
due to data that is intentionally dropped by `rebot` during `log.html` generation.

To create a stable "target" for `tober` to aim for, we created the `rounder.py` script.
This script *downgrades* a high-fidelity, original `output.xml` file into a new file (`output_rounded.xml`)
that represents the best-case-scenario output `tober` can generate.

**The `rounder.py` script does the following:**
1.  **Rounds Timestamps:** `log.html` only stores millisecond-precision timestamps.
    The rounder script parses all timestamps and rounds them to the nearest millisecond to match.
2.  **Removes Lost Data:** It removes elements and attributes that are confirmed to be absent from `log.html`'s data:
    * All `<doc>` elements. Rebot renders markdown source into html that is not possible to reliably revert back to markdown.
    * The `line` attribute from all `<test>` elements.
    * The `source_name` attribute from all `<kw>` elements.
    * The final `<statistics>` and `<errors>` blocks (not yet supported by tober).

By diffing `output_from_log.xml` against `output_rounded.xml`, we can get a true picture of `tober`'s accuracy.

## Design Decisions & Implementation Details

* **`json.loads` vs. `ast.literal_eval`**: The primary data structure in `log.html` is a massive, nested list assigned to `window.output["suite"]`.
  Our first attempts used `ast.literal_eval` to parse this, as it's a Python literal.
  However, this proved to be a severe memory bottleneck, as `ast` builds a full Abstract Syntax Tree in memory.
  We switched to `json.loads` after confirming the data structure is JSON-compatible
  (once `None`, `True`, `False` are replaced with `null`, `true`, `false`). This dramatically reduced peak memory usage.
* **`sPart` Replacement**: Large `log.html` files split their data into `window.sPartX` variables, which are nested.
  Our replacement loop uses `re.sub` with a callback and has a fixed limit (`limit = 10`)
  to prevent runaway memory consumption from creating thousands of copies of the multi-gigabyte data string.
* **String Caching**: The script pre-populates an in-memory dictionary (`decoded_strings_cache`) with all decompressed strings.
  While this uses memory, our debugging showed the *parsing* of the suite data was the true bottleneck, and this cache provides a good performance trade-off.
* **Failure Message Reconstruction**: This was the most complex part. `log.html` does not store the final, combined failure messages in the `<status>` tag.
  We had to reimplement Robot Framework's logic:
    * Failure messages are "bubbled up" from child keywords.
    * A `FAIL` in a test body and a `FAIL` in its teardown are combined with `\n\nAlso teardown failed:\n`.
    * A `FAIL` in a keyword body and a `FAIL` in its *own* teardown are combined with `\n\nAlso keyword teardown failed:\n`.
    * Multiple failures within a single teardown are combined into a "Several failures occurred:" list.
    * `NOT RUN` keywords are inspected for a `FAIL` message in their body, which indicates a propagated timeout message.
* **Message Truncation**: We discovered that `output.xml` may truncate long, repeated failure messages with `[ Message content over the limit has been removed. ]`.
  `log.html` does not do this, as it stores the full string once and re-uses it by index.
  `tober` also re-uses the full string, so its output is actually *more complete* in this specific scenario.
  We've accepted this as a minor, beneficial difference.
