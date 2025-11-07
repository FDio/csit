# Tober: The Robot Framework `log.html` to `output.xml` Converter

**Tober** (named as a reversal of "rebot") is a Python script that reconstructs a Robot Framework `output.xml` file by parsing a `log.html` file.

This tool is designed for a specific scenario: **you have `log.html` files but have lost or did not archive the original `output.xml` files.**

## The Problem

Robot Framework is designed to generate a `log.html` file *from* an `output.xml` file. The standard workflow is:
1.  `robot` runs tests -> `output.xml`
2.  `rebot` combines/parses `output.xml` -> `log.html` & `report.html`

The `output.xml` is the primary source of truth. However, `log.html` contains *most* of the same data, just embedded as JavaScript variables.
If you only have the `log.html` file, you can't use standard Robot tools (like `rebot` or `testdoc`) to re-process, filter, or query the results.

## The Solution

**Tober** reads the JavaScript data embedded in `log.html` and uses it to build a new `output.xml` file that is structurally similar to the original.

This allows you to:
* Run `rebot` on the generated `output.xml` to create new reports.
* Parse the XML with your own scripts (e.g., using XPath) to find failing tests or keywords.
* Automate the analysis of old test runs for which you only have `log.html`.

### How to Use

1.  Place `tober.py` in your directory.
2.  Place the `log.html` file you want to convert in the same directory.
3.  Run the script: `python3 tober.py`
4.  The script will read `log.html` and produce `output_from_log.xml` in the same directory.

**Requirements:**
* Python 3.x
* No external libraries are needed (uses standard `json`, `xml`, `zlib`, etc.)

## Limitations & Discrepancies

The `log.html` file *does not* contain 100% of the original data. Some information is permanently lost.
This tool attempts to create a file that is *functionally* equivalent, but it will not be a byte-for-byte match with the original.

Known limitations include:
* **Missing `<doc>` Content:** All documentation strings for suites, tests, and keywords are rendered as HTML in `log.html`,
  and the original markup (like newlines and indentation) is lost. To avoid creating messy, escaped HTML, this tool removes all `<doc>` tags entirely.
* **Missing Test `line` Numbers:** The line number of a test case in its `.robot` file is not stored in `log.html` and cannot be recovered.
* **Missing `source_name`:** The original name of a keyword (before argument embedding) is not stored and will not be present.
* **Missing Statistics:** The `<statistics>` and `<errors>` blocks at the end of `output.xml` are built from different data structures.
  This tool does not (yet) parse that data and omits these blocks.
