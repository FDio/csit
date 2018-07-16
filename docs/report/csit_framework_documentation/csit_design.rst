.. _csit-design:

Design
======

FD.io CSIT system design needs to meet continuously expanding
requirements of FD.io projects including VPP, related sub-systems (e.g.
plugin applications, DPDK drivers) and FD.io applications (e.g. DPDK
applications), as well as growing number of compute platforms running
those applications. With CSIT project scope and charter including both
FD.io continuous testing AND performance trending/comparisons, those
evolving requirements further amplify the need for CSIT framework
modularity, flexibility and usability.

Design Hierarchy
----------------

CSIT follows a hierarchical system design with SUTs and DUTs at the
bottom level of the hierarchy, presentation level at the top level and a
number of functional layers in-between. The current CSIT system design
including CSIT framework is depicted in the figure below.

.. only:: latex

    .. raw:: latex

       \begin{figure}[H]
       \centering
           \includesvg[width=0.90\textwidth]{../_tmp/src/csit_framework_documentation/csit_design_picture}
           \label{fig:csit_design_picture}
       \end{figure}

.. only:: html

    .. figure:: csit_design_picture.svg
        :alt: FD.io CSIT system design
        :align: center

   *FD.io CSIT system design*

A brief bottom-up description is provided here:

#. SUTs, DUTs, TGs

   - SUTs - Systems Under Test;
   - DUTs - Devices Under Test;
   - TGs - Traffic Generators;

#. Level-1 libraries - Robot and Python

   - Lowest level CSIT libraries abstracting underlying test environment, SUT,
     DUT and TG specifics;
   - Used commonly across multiple L2 KWs;
   - Performance and functional tests:

     - L1 KWs (KeyWords) are implemented as RF libraries and Python
       libraries;

   - Performance TG L1 KWs:

     - All L1 KWs are implemented as Python libraries:

       - Support for TRex only today;
       - CSIT IXIA drivers in progress;

   - Performance data plane traffic profiles:

     - TG-specific stream profiles provide full control of:

       - Packet definition – layers, MACs, IPs, ports, combinations thereof
         e.g. IPs and UDP ports;
       - Stream definitions - different streams can run together, delayed,
         one after each other;
       - Stream profiles are independent of CSIT framework and can be used
         in any T-rex setup, can be sent anywhere to repeat tests with
         exactly the same setup;
       - Easily extensible – one can create a new stream profile that meets
         tests requirements;
       - Same stream profile can be used for different tests with the same
         traffic needs;

   - Functional data plane traffic scripts:

     - Scapy specific traffic scripts;

#. Level-2 libraries - Robot resource files:

   - Higher level CSIT libraries abstracting required functions for executing
     tests;
   - L2 KWs are classified into the following functional categories:

     - Configuration, test, verification, state report;
     - Suite setup, suite teardown;
     - Test setup, test teardown;

#. Tests - Robot:

   - Test suites with test cases;
   - Functional tests using VIRL environment:

     - VPP;
     - Honeycomb;
     - NSH_SFC;

   - Performance tests using physical testbed environment:

     - VPP;
     - DPDK-Testpmd;
     - DPDK-L3Fwd;
     - Honeycomb;
     - VPP Container K8s orchestrated topologies;

   - Tools:

     - Documentation generator;
     - Report generator;
     - Testbed environment setup ansible playbooks;
     - Operational debugging scripts;

Test Lifecycle Abstraction
--------------------------

A well coded test must follow a disciplined abstraction of the test
lifecycles that includes setup, configuration, test and verification. In
addition to improve test execution efficiency, the commmon aspects of
test setup and configuration shared across multiple test cases should be
done only once. Translating these high-level guidelines into the Robot
Framework one arrives to definition of a well coded RF tests for FD.io
CSIT. Anatomy of Good Tests for CSIT:

#. Suite Setup - Suite startup Configuration common to all Test Cases in suite:
   uses Configuration KWs, Verification KWs, StateReport KWs;
#. Test Setup - Test startup Configuration common to multiple Test Cases: uses
   Configuration KWs, StateReport KWs;
#. Test Case - uses L2 KWs with RF Gherkin style:

   - prefixed with {Given} - Verification of Test setup, reading state: uses
     Configuration KWs, Verification KWs, StateReport KWs;
   - prefixed with {When} - Test execution: Configuration KWs, Test KWs;
   - prefixed with {Then} - Verification of Test execution, reading state: uses
     Verification KWs, StateReport KWs;

#. Test Teardown - post Test teardown with Configuration cleanup and
   Verification common to multiple Test Cases - uses: Configuration KWs,
   Verification KWs, StateReport KWs;
#. Suite Teardown - Suite post-test Configuration cleanup: uses Configuration
   KWs, Verification KWs, StateReport KWs;

RF Keywords Functional Classification
-------------------------------------

CSIT RF KWs are classified into the functional categories matching the test
lifecycle events described earlier. All CSIT RF L2 and L1 KWs have been grouped
into the following functional categories:

#. Configuration;
#. Test;
#. Verification;
#. StateReport;
#. SuiteSetup;
#. TestSetup;
#. SuiteTeardown;
#. TestTeardown;

RF Keywords Naming Guidelines
-----------------------------

Readability counts: "..code is read much more often than it is written."
Hence following a good and consistent grammar practice is important when
writing :abbr:`RF (Robot Framework)` KeyWords and Tests. All CSIT test cases
are coded using Gherkin style and include only L2 KWs references. L2 KWs are
coded using simple style and include L2 KWs, L1 KWs, and L1 python references.
To improve readability, the proposal is to use the same grammar for both
:abbr:`RF (Robot Framework)` KW styles, and to formalize the grammar of English
sentences used for naming the :abbr:`RF (Robot Framework)` KWs. :abbr:`RF (Robot
Framework)` KWs names are short sentences expressing functional description of
the command. They must follow English sentence grammar in one of the following
forms:

#. **Imperative** - verb-object(s): *"Do something"*, verb in base form.
#. **Declarative** - subject–verb–object(s): *"Subject does something"*, verb in
   a third-person singular present tense form.
#. **Affirmative** - modal_verb-verb-object(s): *"Subject should be something"*,
   *"Object should exist"*, verb in base form.
#. **Negative** - modal_verb-Not-verb-object(s): *"Subject should not be
   something"*, *"Object should not exist"*, verb in base form.

Passive form MUST NOT be used. However a usage of past participle as an
adjective is okay. See usage examples provided in the Coding guidelines
section below. Following sections list applicability of the above
grammar forms to different :abbr:`RF (Robot Framework)` KW categories. Usage
examples are provided, both good and bad.

Coding guidelines
-----------------

Coding guidelines can be found on `Design optimizations wiki page
<https://wiki.fd.io/view/CSIT/Design_Optimizations>`_.
