CSIT Test Code Guidelines
^^^^^^^^^^^^^^^^^^^^^^^^^

**WORK IN PROGRESS**

Here are some guidelines for writing reliable, maintainable, reusable and readable Robot Framework (RF) test code. There is used Robot Framework version 2.9.2 ([http://robotframework.org/robotframework/2.9.2/RobotFrameworkUserGuide.html user guide]) in CSIT.

RobotFramework test case files and resource files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* General

** RobotFramework test case files and resource files use special extension .robot
** Usage of pipe and space separated file format is strongly recommended. Tabs are invisible characters which is error prone.
** Files should be encoded in ASCII. Non-ASCII characters are allowed but they must be encoded in UTF8 (the default Robot source file encoding).
** Line length is limited to 80 characters.
** There must be included licence (/csit/docs/licence.rst) at the begging of each file.
** Copy-pasting of the code is unwanted practice, any code that could be re-used has to be put into RF keyword (KW) or python library instead of copy-pasted.

* Test cases

** Test cases are written in Behavior-driven style – i.e. in readable English so that even non-technical project stakeholders can understand it::

   *** Test Cases ***
   | VPP can encapsulate L2 in VXLAN over IPv4 over Dot1Q
   | | Given Path for VXLAN testing is set
   | | ...   | ${nodes['TG']} | ${nodes['DUT1']} | ${nodes['DUT2']}
   | | And   Interfaces in path are up
   | | And   Vlan interfaces for VXLAN are created | ${VLAN}
   | |       ...                                   | ${dut1} | ${dut1s_to_dut2}
   | |       ...                                   | ${dut2} | ${dut2s_to_dut1}
   | | And   IP addresses are set on interfaces
   | |       ...         | ${dut1} | ${dut1s_vlan_name} | ${dut1s_vlan_index}
   | |       ...         | ${dut2} | ${dut2s_vlan_name} | ${dut2s_vlan_index}
   | | ${dut1s_vxlan}= | When Create VXLAN interface     | ${dut1} | ${VNI}
   | |                 | ...  | ${dut1s_ip_address} | ${dut2s_ip_address}
   | |                   And  Interfaces are added to BD | ${dut1} | ${BID}
   | |                   ...  | ${dut1s_to_tg} | ${dut1s_vxlan}
   | | ${dut2s_vxlan}= | And  Create VXLAN interface     | ${dut2} | ${VNI}
   | |                 | ...  | ${dut2s_ip_address} | ${dut1s_ip_address}
   | |                   And  Interfaces are added to BD | ${dut2} | ${BID}
   | |                   ...  | ${dut2s_to_tg} | ${dut2s_vxlan}
   | | Then Send and receive ICMPv4 bidirectionally
   | | ... | ${tg} | ${tgs_to_dut1} | ${tgs_to_dut2}

** Every test case should contain short documentation. (example will be added) This documentation will be used by testdoc tool - Robot Framework's built-in tool for generating high level documentation based on test cases.
** Do not use hard-coded constants. It is recommended to use the variable table (***Variables***) to define test case specific values. Use the assignment sign = after the variable name to make assigning variables slightly more explicit::

   *** Variables ***
   | ${VNI}= | 23

** Common test case specific settings of the test environment should be done in Test Setup part of the Setting table ease on (***Settings***).
** Post-test cleaning and processing actions should be done in Test Teardown part of the Setting table (e.g. download statistics from VPP nodes). This part is executed even if the test case has failed. On the other hand it is possible to disable the tear-down from command line, thus leaving the system in “broken” state for investigation.
** Every TC must be correctly tagged. List of defined tags is in /csit/docs/tag_documentation.rst file.
** User high-level keywords specific for the particular test case can be implemented in the keyword table of the test case to enable readability and code-reuse.

* Resource files

** Used to implement higher-level keywords that are used in test cases or other higher-level keywords.
** Every keyword must contains Documentation where the purpose and arguments of the KW are described.
** The best practice is that the KW usage example is the part of the Documentation. It is recommended to use pipe and space separated format for the example.
** Keyword name should describe what the keyword does, specifically and in a reasonable length (“short sentence”).

Python library files
~~~~~~~~~~~~~~~~~~~~

* General

** Used to implement low-level keywords that are used in resource files (to create higher-level keywords) or in test cases.
** Higher-level keywords can be implemented in python library file too, especially in the case that their implementation in resource file would be too difficult or impossible, e.g. nested FOR loops or branching.
** Every keyword, Python module, class, method, enums has to contain documentation string with the short description and used input parameters and possible return value(s).
** The best practice is that the KW usage example is the part of the Documentation. It should contains two parts – RobotFramework example and Python example. It is recommended to use pipe and space separated format in case of RobotFramework example.
** KW usage examples can be grouped and used in the class documentation string to provide better overview of the usage and relationships between KWs.
** Keyword name should describe what the keyword does, specifically and in a reasonable length (“short sentence”).
** There must be included licence (/csit/docs/licence.rst) at the begging of each file.

* Coding

** It is recommended to use some standard development tool (e.g. PyCharm Community Edition) and follow [https://www.python.org/dev/peps/pep-0008/ PEP-8] recommendations.
** All python code (not only RF libraries) must adhere to PEP-8 standard. This is enforced by CSIT Jenkins verify job.
** Indentation – do not use tab for indents! Indent is defined as four spaces.
** Line length – limited to 80 characters.
** Imports - use the full pathname location of the module, e.g. from resources.libraries.python.topology import Topology. Imports should be grouped in the following order: 1. standard library imports, 2. related third party imports, 3. local application/library specific imports. You should put a blank line between each group of imports.
** Blank lines - Two blank lines between top-level definitions, one blank line between method definitions.
** Do not use global variables inside library files.
** Constants – avoid to use hard-coded constants (e.g. numbers, paths without any description). Use configuration file(s), like /csit/resources/libraries/python/constants.py, with appropriate comments.
** Logging – log at the lowest possible level of implementation (debugging purposes). Use same style for similar events. Keep logging as verbose as necessary.
** Exceptions – use the most appropriate exception not general one („Exception“ ) if possible. Create your own exception if necessary and implement there logging, level debug.
