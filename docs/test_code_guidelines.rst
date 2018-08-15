CSIT Test Code Guidelines
^^^^^^^^^^^^^^^^^^^^^^^^^

FIXME: Replace "is", "are", "should", "it is required" and similar with "shall".
TODO: Consider applying capitalization: https://tools.ietf.org/html/rfc8174

This document describes guidelines for writing reliable, maintainable,
reusable and readable code for CSIT.

RobotFramework test case files and resource files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+ General

  + See requirements.txt in root CSIT directory for the currently used
    Robot Framework version. See `Robot Framework User Guide
    <http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html>`_
    for more details.

  + RobotFramework test case files and resource files
    use special extension .robot

  + Usage of pipe and space separated file format (without trailing pipe
    and without pipe aligning) is required.
    Tabs are invisible characters, which are error prone.
    4-spaces separation is prone to accidental double space acting as a separator.

  + Files should be encoded in UTF-8 (the default Robot source file encoding).
    Avoid usage of non-ASCII characters if possible.
    It is preferred to `escape
    <http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#escaping>`_
    non-ASCII characters.

  + Line length is limited to 80 characters.

  + There must be included licence (FIXME: add link)
    at the beginning of each file.

  + Copy-pasting of the code is unwanted practice, any code that could be
    re-used has to be put into a library (Robot resource, Python library, ...).

+ Test cases

  + It is strongly encouraged to use data-driven test case definitions
    anytime suite contains test cases similar in structure.
    Typically, a suite defines a Template keyword, and test cases
    only specify tags and argument values::

        *** Settings ***
        | Test Template | Local Template
        ...

        *** Test Cases ***
        | tc01-64B-1c-eth-l2patch-mrr
        | | [Tags] | 64B | 1C
        | | framesize=${64} | phy_cores=${1}

  + Test case templates (or testcases) are written in Behavior-driven style
    i.e. in readable English so that even non-technical project stakeholders
    can understand it::

        *** Keywords ***
        | Local Template
        | | [Documentation]
        | | ... | [Cfg] DUT runs L2 patch config with ${phy_cores} phy
        | | ... | core(s).
        | | ... | [Ver] Measure MaxReceivedRate for ${framesize}B frames using single\
        | | ... | trial throughput test.
        | | ...
        | | ... | *Arguments:*
        | | ... | - framesize - Framesize in Bytes in integer or string (IMIX_v4_1).
        | | ... | Type: integer, string
        | | ... | - phy_cores - Number of physical cores. Type: integer
        | | ... | - rxq - Number of RX queues, default value: ${None}. Type: integer
        | | ...
        | | [Arguments] | ${framesize} | ${phy_cores} | ${rxq}=${None}
        | | ...
        | | Given Add worker threads and rxqueues to all DUTs | ${phy_cores} | ${rxq}
        | | And Add PCI devices to all DUTs
        | | ${max_rate} | ${jumbo} = | Get Max Rate And Jumbo And Handle Multi Seg
        | | ... | ${s_24.5G} | ${framesize} | pps_limit=${s_18.75Mpps}
        | | And Apply startup configuration on all VPP DUTs
        | | When Initialize L2 patch
        | | Then Traffic should pass with maximum rate
        | | ... | ${max_rate}pps | ${framesize} | ${traffic_profile}

  + Every suite and test case template (or testcase)
    should contain short documentation.
    Generated CSIT web pages display the documentation.
    For an example generated page, see:
    https://docs.fd.io/csit/rls1807/doc/tests.vpp.perf.tcp.html

  + Do not use hard-coded constants. It is recommended to use the variable table
    (\*\*\*Variables\*\*\*) to define test case specific values.
    Use the assignment sign = after the variable name to make assigning variables
    slightly more explicit::

        *** Variables ***
        | ${traffic_profile}= | trex-sl-2n-ethip4-ip4src254

  + Common test case specific settings of the test environment should be done
    in Test Setup part of the Setting table ease on (\*\*\*Settings\*\*\*).

  + Post-test cleaning and processing actions should be done in Test Teardown
    part of the Setting table (e.g. download statistics from VPP nodes).
    This part is executed even if the test case has failed. On the other hand
    it is possible to disable the tear-down from command line, thus leaving
    the system in “broken” state for investigation.

  + Every testcase must be correctly tagged. List of defined tags is in
    csit/docs/tag_documentation.rst (FIXME: rst-ize the link) file.

  + User high-level keywords specific for the particular test suite
    can be implemented in the keyword table of suitable Robot resource file
    to enable readability and code-reuse.

  + All test case names (and suite names) should conform
    to current naming convention.
    https://wiki.fd.io/view/CSIT/csit-test-naming
    TODO: Migrate the convention document to .rst and re-link.

  + Frequently, different suites us the same test case layout.
    It is recommended to use autogeneration scripts available,
    possibly extending them if their current functionality is not sufficient.

+ Resource files

  + Used to implement higher-level keywords that are used in test cases
    or other higher-level keywords.

  + Every keyword must contain Documentation where the purpose and arguments
    of the keyword are described. Also document types, return values,
    and any specific assumptions the particular keyword relies on.

  + The best practice is that the keyword usage example is the part
    of the Documentation. The example should use pipe and space
    separated format (with escaped pipes and) with a trailing pipe.
    TODO: Figure out why we need the trailing pipe and write the reason here.

  + Keyword name should describe what the keyword does,
    specifically and in a reasonable length (“short sentence”).

  + If a keyword argument has a most commonly used value, set it as default.
    This makes keyword code longer, but suite code shorter,
    and readability (and maintainability) of suites is always more important.

  + If there is intermediate data (created by one keyword, to be used
    by another keyword) of singleton semantics (it is clear that the test case
    can have at most one instance of such data, even if the instance
    is complex, for example ${nodes}), it is better to store it in test variables.
    Be sure to document test variables read or written by a keyword.
    This makes the test template code less verbose.
    As soon as the data instance is not unique, pass it around
    via arguments and return value explicitly (this makes lower level keywords
    more reusable and less bug prone).

  + It is recommended to pass arguments explicitly via [Arguments] line.
    Setting test variables takes more space and is less explicit.
    Using arguments embedded in keyword name makes them less visible,
    and it makes it harder for the line containing the resulting long name
    to fit into the maximum character limit.

Python library files
~~~~~~~~~~~~~~~~~~~~

TODO: Add guidelines for Python scripts (both utilities called by test on nodes
and unrelated ones such as PAL) if there are any (in addition to library ones).

+ General

  + Used to implement low-level keywords that are used in resource files
    (to create higher-level keywords) or in test cases.

  + TODO: Discuss debugability, speed, logging, complexity of logic.

  + Higher-level keywords can be implemented in python library file too,
    especially in the case that their implementation in resource file
    would be too difficult or impossible, e.g. complex data structures
    or functional programming.

  + Every keyword, Python module, class, method, enums has to contain
    documentation string with the short description and used input parameters
    and possible return value(s) or raised exceptions.

  + Keyword usage examples can be grouped and used
    in the class/module documentation string, to provide better overview
    of the usage and relationships between keywords.

  + Keyword name should describe what the keyword does,
    specifically and in a reasonable length (“short sentence”).
    See https://wiki.fd.io/view/CSIT/csit-test-naming

+ Coding

  + It is recommended to use some standard development tool
    (e.g. PyCharm Community Edition) and follow
    `PEP-8 <https://www.python.org/dev/peps/pep-0008/>`_ recommendations.

  + All python code (not only Robot libraries) must adhere to PEP-8 standard.
    This is reported by CSIT Jenkins verify job.

  + Indentation – do not use tab for indents! Indent is defined as four spaces.

  + Line length – limited to 80 characters.

  + CSIT Python code assumes PYTHONPATH is set
    to the root of cloned CSIT git repository, creating a tree of sub-packages.

  + Imports - use the full package location of the module,
    e.g. from resources.libraries.python.topology import Topology.
    Imports should be grouped in the following order:

      #. standard library imports,
      #. related third party imports,
      #. local application/library specific imports.

    You should put a blank line between each group of imports.

  + Blank lines - Two blank lines between top-level definitions,
    one blank line between method definitions.

  + Do not use global variables inside library files.

  + Constants – avoid to use hard-coded constants (e.g. numbers,
    paths without any description). Use configuration file(s),
    like /csit/resources/libraries/python/constants.py,
    with appropriate comments.

  + Logging – log at the lowest possible level of implementation
    (debugging purposes). Use same style for similar events.
    Keep logging as verbose as necessary.

  + Exceptions – use the most appropriate exception
    not general one („Exception“ ) if possible. Create your own exception
    if necessary and implement there logging, level debug.

  + For each class (e.g. exception) consider implementing __repr__()
    which should return a string usable as a constructor call
    (including repr()ed arguments).
    When logging, log the repr form, unless the internal structure
    of the object in question would likely result in too long output.
    This is helpful for debugging.

  + For composing and formatting strings, prefer .format() with named arguments.
    Example: "repr() of name: {name!r}".format(name=name)

Bash scripts and libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~

FIXME.
