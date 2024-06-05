---
bookHidden: true
title: "CSIT Test Code Guidelines"
---

# CSIT Test Code Guidelines

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED",
"MAY", and "OPTIONAL" in this document are to be interpreted as
described in [BCP 14](https://tools.ietf.org/html/bcp14),
[RFC2119](https://tools.ietf.org/html/rfc2119),
[RFC8174](https://tools.ietf.org/html/rfc8174)
when, and only when, they appear in all capitals, as shown here.

This document SHALL describe guidelines for writing reliable, maintainable,
reusable and readable code for CSIT.

# RobotFramework test case files and resource files

+ General

  + Contributors SHOULD look at requirements.txt in root CSIT directory
    for the currently used Robot Framework version.
    Contributors SHOULD read
    [Robot Framework User Guide](http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
    for more details.

  + RobotFramework test case files and resource files
    SHALL use special extension .robot

  + Pipe and space separated file format (without trailing pipe
    and without pipe aligning) SHALL be used.
    Tabs are invisible characters, which are error prone.
    4-spaces separation is prone to accidental double space
    acting as a separator.

  + Files SHALL be encoded in UTF-8 (the default Robot source file encoding).
    Usage of non-ASCII characters SHOULD be avoided if possible.
    It is RECOMMENDED to
    [escape](http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#escaping)
    non-ASCII characters.

  + Line length SHALL be limited to 80 characters.

  + There SHALL be licence text present at the beginning of each file.

  + Copy-pasting of the code NOT RECOMMENDED practice, any code that could be
    re-used SHOULD be put into a library (Robot resource, Python library, ...).

+ Test cases

  + It is REQUIRED to use data-driven test case definitions
    anytime suite contains test cases similar in structure.
    Typically, a suite MUST define a Template keyword, and test cases
    MUST only specify tags and argument values

    ```
    *** Settings ***
    | Test Template | Local Template
    ...

    *** Test Cases ***
    | 64B-1c-eth-l2patch-ndrpdr
    | | [Tags] | 64B | 1C
    | | framesize=${64} | phy_cores=${1}
    ```

  + Test case templates (or testcases) SHALL be written in Behavior-driven style
    i.e. in readable English, so that even non-technical project stakeholders
    can understand it

    ```
    *** Keywords ***
    | Local Template
    | | [Documentation]
    | | ... | - **[Cfg]** DUT runs L2 patch config with ${phy_cores} phy \
    | | ... | core(s).
    | | ... | - **[Ver]** Measure NDR and PDR values using MLRsearch algorithm.
    | |
    | | ... | *Arguments:*
    | | ... | - frame_size - Framesize in Bytes in integer or string (IMIX_v4_1).
    | | ... | Type: integer, string
    | | ... | - phy_cores - Number of physical cores. Type: integer
    | | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
    | |
    | | [Arguments] | ${frame_size} | ${phy_cores} | ${rxq}=${None}
    | |
    | | Set Test Variable | \${frame_size}
    | |
    | | Given Set Max Rate And Jumbo
    | | And Add worker threads to all DUTs | ${phy_cores} | ${rxq}
    | | And Pre-initialize layer driver | ${nic_driver}
    | | And Apply Startup configuration on all VPP DUTs
    | | When Initialize layer driver | ${nic_driver}
    | | And Initialize layer interface
    | | And Initialize L2 patch
    | | Then Find NDR and PDR intervals using optimized search
    ```

  + Every suite and test case template (or testcase)
    SHALL contain short documentation.
    Generated CSIT web pages display the documentation.

  + You SHOULD NOT use hard-coded constants.
    It is RECOMMENDED to use the variable table
    (\*\*\*Variables\*\*\*) to define test case specific values.
    You SHALL use the assignment sign = after the variable name
    to make assigning variables slightly more explicit

    ```
    *** Variables ***
    | ${n_tunnels}= | ${100000}
    | ${traffic_profile}= | trex-stl-ethip4-ip4dst${n_tunnels}
    ```

  + Common test case specific settings of the test environment SHALL be done
    in Test Setup keyword defined in the Setting table.

    + Run Keywords construction is RECOMMENDED if it is more readable
      than a keyword.

    + Separate keyword is REQUIRED even if the Run Keywords construction
      would be more readable.

      + This rule is here to prevent unintended subtle differences
        between similar suites.

    + All test setup keywords SHALL be defined in a common resource file.

  + Post-test cleaning and processing actions SHALL be done in Test Teardown
    part of the Setting table (e.g. displaying PAPI history).
    This part is executed even if the test case has failed. On the other hand
    it is possible to disable the tear-down from command line, thus leaving
    the system in “broken” state for investigation.

  + Every testcase SHALL be correctly tagged. List of defined tags is in
    csit/docs/introduction/test_tag_documentation.rst

    + Whenever possible, common tags SHALL be set using Force Tags
      in Settings table.

  + User high-level keywords specific for the particular test suite
    MUST be implemented in the Keywords table of suitable Robot resource file
    to enable readability and code-reuse.

  + All test case names (and suite names) SHALL conform
    to current naming convention.
    https://wiki.fd.io/view/CSIT/csit-test-naming

  + Frequently, different suites use the same test case layout.
    It is REQUIRED to use autogeneration scripts available,
    extending them if their current functionality is not sufficient.

+ Resource files

  + SHALL be used to implement higher-level keywords that are used in test cases
    or other higher-level (or medium-level) keywords.

  + Every keyword SHALL contain Documentation where the purpose and arguments
    of the keyword are described. Also document types, return values,
    and any specific assumptions the particular keyword relies on.

  + A keyword usage example SHALL be the part of the Documentation.
    The example SHALL use pipe and space separated format
    (with escaped pipes and) with a trailing pipe.

    + The reason was possbile usage of Robot's libdoc tool
      to generate tests and resources documentation. In that case
      example keyword usage would be rendered in table.

  + Keyword name SHALL describe what the keyword does,
    specifically and in a reasonable length (“short sentence”).

    + Keyword names SHALL be short enough for call sites
      to fit within line length limit.

  + If a keyword argument has a most commonly used value, it is RECOMMENDED
    to set it as default. This makes keyword code longer,
    but suite code shorter, and readability (and maintainability)
    of suites SHALL always more important.

  + If there is intermediate data (created by one keyword, to be used
    by another keyword) of singleton semantics (it is clear that the test case
    can have at most one instance of such data, even if the instance
    is complex, for example ${nodes}), it is RECOMMENDED to store it
    in test variables. You SHALL document test variables read or written
    by a keyword. This makes the test template code less verbose.
    As soon as the data instance is not unique, you SHALL pass it around
    via arguments and return values explicitly (this makes lower level keywords
    more reusable and less bug prone).

  + It is RECOMMENDED to pass arguments explicitly via [Arguments] line.
    Setting test variables takes more space and is less explicit.
    Using arguments embedded in keyword name makes them less visible,
    and it makes it harder for the line containing the resulting long name
    to fit into the maximum character limit, so you SHOULD NOT use them.

# Python library files

+ General

  + SHALL be used to implement low-level keywords that are called from
    resource files (of higher-level keywords) or from test cases.

  + Medium-level keywords MAY be implemented in python library file too.
    it is RECOMMENDED especially in the case that their implementation
    in resource file would be too difficult or impossible,
    e.g. complex data structures or functional programming.

  + Every keyword, Python module, class, method, enum SHALL contain
    docstring with the short description and used input parameters
    and possible return value(s) or raised exceptions.

    + The docstrings SHOULD conform to
      [PEP 257](https://www.python.org/dev/peps/pep-0257/)
      and other quality standards.

    + CSIT contributions SHALL use a specific formatting for documenting
      arguments, return values and similar.

    + It is RECOMMENDED to use type hints.

  + Keyword usage examples MAY be grouped and used
    in the class/module documentation string, to provide better overview
    of the usage and relationships between keywords.

  + Keyword name SHALL describe what the keyword does,
    specifically and in a reasonable length (“short sentence”).
    See https://wiki.fd.io/view/CSIT/csit-test-naming

  + Python implementation of a keyword is a static method,
    so its name in the python library should be lowercase_with_underscores.
    Robot call sites should usename with first letter capitalized, and spaces.

+ Coding

  + It is RECOMMENDED to use some standard development tool
    (e.g. PyCharm Community Edition) and follow
    [PEP-8](https://www.python.org/dev/peps/pep-0008/) recommendations.

  + All python code (not only Robot libraries) SHALL adhere to PEP-8 standard.
    This is reported by CSIT Jenkins verify job.

  + Indentation: You SHALL NOT use tab for indents!
    Indent is defined as four spaces.

  + Line length: SHALL be limited to 80 characters.

  + CSIT Python code assumes PYTHONPATH is set
    to the root of cloned CSIT git repository, creating a tree of sub-packages.
    You SHALL use that tree for importing, for example

        from resources.libraries.python.ssh import exec_cmd_no_error

  + Imports SHALL be grouped in the following order:

      1. standard library imports,
      2. related third party imports,
      3. local application/library specific imports.

    You SHALL put a blank line between each group of imports.

  + You SHALL use two blank lines between top-level definitions,
    one blank line between method definitions.

  + You SHALL NOT execute any active code on library import.

  + You SHALL NOT use global variables inside library files.

    + You MAY define constants inside library files.

  + It is NOT RECOMMENDED to use hard-coded constants (e.g. numbers,
    paths without any description). It is RECOMMENDED to use
    configuration file(s), like /csit/resources/libraries/python/Constants.py,
    with appropriate comments.

  + The code SHALL log at the lowest possible level of implementation,
    for debugging purposes. You SHALL use same style for similar events.
    You SHALL keep logging as verbose as necessary.

  + You SHALL use the most appropriate exception not general one (Exception)
    if possible. You SHOULD create your own exception
    if necessary and implement there logging, level debug.

    + You MAY use RuntimeError for generally unexpected failures.

    + It is RECOMMENDED to use RuntimeError also for
      infrastructure failures, e.g. losing SSH connection to SUT.

      + You MAY use EnvironmentError and its cublasses instead,
        if the distinction is informative for callers.

    + It is RECOMMENDED to use AssertionError when SUT is at fault.

  + For each class (e.g. exception) it is RECOMMENDED to implement __repr__()
    which SHALL return a string usable as a constructor call
    (including repr()ed arguments).
    When logging, you SHOULD log the repr form, unless the internal structure
    of the object in question would likely result in too long output.
    This is helpful for debugging.

  + For composing and formatting strings, you SHOULD use f-strings.
    Example 1: f"repr() of name: {name!r}"
    Example 2: f"{name=}"

  + It is RECOMMENDED to use "tox -e pylint"
    to get more info in conding style issues with the current code.

# Dead code

+ If a piece of functionality is not expected to get executed in fd.io lab,
  nor in an adjacent infrastructure (e.g. CSIT-DASH running in a cloud),
  the corresponding code MUST be considered to be deprecated.

+ A code CANNOT be considered deprecated if it is still used on occasion,
  albeit rarely (e.g. only when required by some infrastructure upgrade).

+ On the other hand, a piece of code MAY become deprecated
  even if it was used recently
  (e.g. when CSIT decides to stop running tests from some suite).

  + In this case, the deciding factor is whether the code is expected
    to be run at least in some verify runs.

+ Any code that is not deprecated MUST be considered to be a live code.

+ All live code SHOULD be runable.

  + Some code (mostly infra-related) is inherently hard to execute
    without affecting the production environment.
    In this case, the maintainer SHALL decide which code is runable.

  + Any live code MAY stop being runnable due to some bug.

  + If the bug is not fixed quickly enough, it SHALL imply
    the non-runnable code became deprecated.

    + The maintainer decides when this decprecation occurs,
      e.g. when it becomes clear the fix will not arrive quickly enough.

+ Any runable code SHOULD be verifiable.

  + If there is an infrastructure set up to verify similar code
    (e.g. csit-vpp perf verify jobs), runable code MUST be
    publicly verifiable using that infrastructure.

  + If some code is not verifiable, maintainer decides
    whether some edit keeps it runnable or not.

+ Any edits that affect live code SHOULD be verified.

  + If any committer asks for verification, such code MUST be verified,
    publicly or otherwise.

  + If the maintainer decides the risk is minimal,
    the edit MAY be merged even without verification.

+ If a code is both deprecated and unverifiable,
  it MUST be considered a dead code.

  + It is possible for code to be neither dead nor alive,
    e.g. when it is already deprecated but still verifiable.

  + It is recommended to avoid code that is neither dead nor alive,
    e.g. by adding missing verify jobs.

+ It is RECOMMENDED to keep deprecated code in codebase,
  as long as it remains verifiable.

  + Flexibility for resuming testing is usually worth
    the inrease in maintaining and verifying the code.

  + Maintainer MAY decide to delete deprecated code
    even if it is still verifiable, e.g. to simplify some library.

+ It is RECOMMENDED to delete any dead code.

  + Argument 1: Any substantial edits to dead code cannot be verified.

  + Argument 2: Leaving dead code unedited makes the codebase less readable.

  + Argument 3: Frequently, it is easier to write new replacement code
    than trying to fix the issue that made the first code unverifiable.
