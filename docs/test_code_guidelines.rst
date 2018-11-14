CSIT Test Code Guidelines
^^^^^^^^^^^^^^^^^^^^^^^^^

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED",
"MAY", and "OPTIONAL" in this document are to be interpreted as
described in `BCP 14 <https://tools.ietf.org/html/bcp14>`_
`[RFC2119] <https://tools.ietf.org/html/rfc2119>`_
`[RFC8174] <https://tools.ietf.org/html/rfc8174>`_
when, and only when, they appear in all capitals, as shown here.

This document SHALL describe guidelines for writing reliable, maintainable,
reusable and readable code for CSIT.

TODO: Decide whether to use "you SHALL", "contributors SHALL",
or "code SHALL be"; convert other forms to the chosen one.

RobotFramework test case files and resource files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+ General

  + Contributors SHOULD look at requirements.txt in root CSIT directory
    for the currently used Robot Framework version.
    Contributors SHOULD read `Robot Framework User Guide
    <http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html>`_
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
    It is RECOMMENDED to `escape
    <http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#escaping>`_
    non-ASCII characters.

  + Line length SHALL be limited to 80 characters.

  + There SHALL be licence text (FIXME: add link) present
    at the beginning of each file.

  + Copy-pasting of the code NOT RECOMMENDED practice, any code that could be
    re-used SHOULD be put into a library (Robot resource, Python library, ...).

+ Test cases

  + It is RECOMMENDED to use data-driven test case definitions
    anytime suite contains test cases similar in structure.
    Typically, a suite SHOULD define a Template keyword, and test cases
    SHOULD only specify tags and argument values::

        *** Settings ***
        | Test Template | Local Template
        ...

        *** Test Cases ***
        | tc01-64B-1c-eth-l2patch-mrr
        | | [Tags] | 64B | 1C
        | | framesize=${64} | phy_cores=${1}

  + Test case templates (or testcases) SHALL be written in Behavior-driven style
    i.e. in readable English, so that even non-technical project stakeholders
    can understand it::

        *** Keywords ***
        | Local Template
        | | [Documentation]
        | | ... | [Cfg] DUT runs L2 patch config with ${phy_cores} phy
        | | ... | core(s).
        | | ... | [Ver] Measure MaxReceivedRate for ${framesize}B frames\
        | | ... | using single trial throughput test.
        | | ...
        | | ... | *Arguments:*
        | | ... | - framesize - Framesize in Bytes in integer\
        | | ... |   or string (IMIX_v4_1). Type: integer, string
        | | ... | - phy_cores - Number of physical cores. Type: integer
        | | ... | - rxq - Number of RX queues, default value: ${None}.\
        | | ... |   Type: integer
        | | ...
        | | [Arguments] | ${framesize} | ${phy_cores} | ${rxq}=${None}
        | | ...
        | | Given Add worker threads and rxqueues to all DUTs
        | | ... | ${phy_cores} | ${rxq}
        | | And Add PCI devices to all DUTs
        | | ${max_rate} | ${jumbo} = | Run Keyword
        | | ... | Get Max Rate And Jumbo And Handle Multi Seg
        | | ... | ${s_24.5G} | ${framesize} | pps_limit=${s_18.75Mpps}
        | | And Apply startup configuration on all VPP DUTs
        | | When Initialize L2 patch
        | | Then Traffic should pass with maximum rate
        | | ... | ${max_rate}pps | ${framesize} | ${traffic_profile}

  + Every suite and test case template (or testcase)
    SHALL contain short documentation.
    Generated CSIT web pages display the documentation.
    For an example generated page, see:
    https://docs.fd.io/csit/rls1807/doc/tests.vpp.perf.tcp.html

  + You SHOULD NOT use hard-coded constants.
    It is RECOMMENDED to use the variable table
    (\*\*\*Variables\*\*\*) to define test case specific values.
    You SHALL use the assignment sign = after the variable name
    to make assigning variables slightly more explicit::

        *** Variables ***
        | ${traffic_profile}= | trex-sl-2n-ethip4-ip4src254

  + Common test case specific settings of the test environment SHALL be done
    in Test Setup keyword defined in the Setting table.

    + Run Keywords construction is RECOMMENDED if it is more readable
      than a keyword.

    + Separate keyword is RECOMMENDED if the construction is less readable.

  + Post-test cleaning and processing actions SHALL be done in Test Teardown
    part of the Setting table (e.g. download statistics from VPP nodes).
    This part is executed even if the test case has failed. On the other hand
    it is possible to disable the tear-down from command line, thus leaving
    the system in “broken” state for investigation.

  + Every testcase SHALL be correctly tagged. List of defined tags is in
    csit/docs/tag_documentation.rst (FIXME: rst-ize the link) file.

    + Whenever possible, common tags SHALL be set using Force Tags
      in Settings table.

  + User high-level keywords specific for the particular test suite
    SHOULD be implemented in the Keywords table of suitable Robot resource file
    to enable readability and code-reuse.

    + Such keywords MAY be implemented in Keywords table of the suite instead,
      if the contributor believes no other test will use such keywords.
      But this is NOT RECOMMENDED in general, as keywords in Resources
      are easier to maintain.

  + All test case names (and suite names) SHALL conform
    to current naming convention.
    https://wiki.fd.io/view/CSIT/csit-test-naming
    TODO: Migrate the convention document to .rst and re-link.

  + Frequently, different suites use the same test case layout.
    It is RECOMMENDED to use autogeneration scripts available,
    possibly extending them if their current functionality is not sufficient.

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

    + TODO: We should adapt it for current tool
      used to generate the documentation.

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

Python library files
~~~~~~~~~~~~~~~~~~~~

TODO: Add guidelines for Python scripts (both utilities called by test on nodes
and unrelated ones such as PAL) if there are any (in addition to library ones).

+ General

  + SHALL be used to implement low-level keywords that are called from
    resource files (of higher-level keywords) or from test cases.

  + TODO: Discuss debugability, speed, logging, complexity of logic.

  + Higher-level keywords MAY be implemented in python library file too.
    it is RECOMMENDED especially in the case that their implementation
    in resource file would be too difficult or impossible,
    e.g. complex data structures or functional programming.

  + Every keyword, Python module, class, method, enum SHALL contain
    docstring with the short description and used input parameters
    and possible return value(s) or raised exceptions.

    + The docstrings SHOULD conform to
      `PEP 257 <https://www.python.org/dev/peps/pep-0257/>`_
      and other quality standards.

    + CSIT contributions SHALL use a specific formatting for documenting
      arguments, return values and similar.

      + FIXME: Find a link which documents sthis style.
        it is based on Sphinx, but very different from
        `Napoleon style
        <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html>`_.

  + Keyword usage examples MAY be grouped and used
    in the class/module documentation string, to provide better overview
    of the usage and relationships between keywords.

  + Keyword name SHALL describe what the keyword does,
    specifically and in a reasonable length (“short sentence”).
    See https://wiki.fd.io/view/CSIT/csit-test-naming

  + Python implementation of a keyword is a function,
    so its name in the python library should be lowercase_with_underscores.
    Robot call sites should usename with first letter capitalized, and spaces.

    + FIXME: create Robot keyword naming item in proper place.

+ Coding

  + It is RECOMMENDED to use some standard development tool
    (e.g. PyCharm Community Edition) and follow
    `PEP-8 <https://www.python.org/dev/peps/pep-0008/>`_ recommendations.

  + All python code (not only Robot libraries) SHALL adhere to PEP-8 standard.
    This is reported by CSIT Jenkins verify job.

  + Indentation: You SHALL NOT use tab for indents!
    Indent is defined as four spaces.

  + Line length: SHALL be limited to 80 characters.

  + CSIT Python code assumes PYTHONPATH is set
    to the root of cloned CSIT git repository, creating a tree of sub-packages.
    You SHALL use that tree for importing, for example::

       from resources.libraries.python.ssh import exec_cmd_no_error

  + Imports SHALL be grouped in the following order:

      #. standard library imports,
      #. related third party imports,
      #. local application/library specific imports.

    You SHALL put a blank line between each group of imports.

  + You SHALL use two blank lines between top-level definitions,
    one blank line between method definitions.

  + You SHALL NOT execute any active code on library import.

  + You SHALL NOT use global variables inside library files.

    + You MAY define constants inside library files.

  + It is NOT RECOMMENDED to use hard-coded constants (e.g. numbers,
    paths without any description). It is RECOMMENDED to use
    configuration file(s), like /csit/resources/libraries/python/constants.py,
    with appropriate comments.

  + The code SHALL log at the lowest possible level of implementation,
    for debugging purposes. You SHALL use same style for similar events.
    You SHALL keep logging as verbose as necessary.

  + You SHALL use the most appropriate exception not general one (Exception)
    if possible. You SHOULD create your own exception
    if necessary and implement there logging, level debug.

    + You MAY use RuntimeException for generally unexpected failures.

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

  + For composing and formatting strings, you SHOULD use .format()
    with named arguments.
    Example: "repr() of name: {name!r}".format(name=name)

Bash scripts and libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO: Link here when document for this is ready.
