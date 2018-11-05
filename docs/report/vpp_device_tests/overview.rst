Overview
========

Virtual Topologies
------------------

CSIT VPP Device tests are executed in Physical containerized topologies
created on demand using set of scripts hosted and developed under CSIT
repository. It runs on physical baremetal servers hosted by LF FD.io project.
Based on the packet path thru SUT Containers, two distinct logical topology
types are used for VPP DUT data plane testing:

#. vfNIC-to-vfNIC switching topologies.
#. Nested-VM service switching topologies. (Planned to be added in rls1901)

vfNIC-to-vfNIC Switching
~~~~~~~~~~~~~~~~~~~~~~~~

The simplest physical topology for software data plane application like
VPP is vfNIC-to-vfNIC switching. Tested virtual topologies for 2-Node testbeds
are shown in figures below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/vpp_device_tests/}}
                \includegraphics[width=0.90\textwidth]{vf-2n-nic2nic}
                \label{fig:vf-2n-nic2nic}
        \end{figure}

.. only:: html

    .. figure:: ../vpp_device_tests/vf-2n-nic2nic.svg
        :alt: vf-2n-nic2nic
        :align: center

SUT1 is Docker Container (running Ubuntu, depending on the test suite), TG is
a Traffic Generator (running Ubuntu Container). SUTs run VPP
SW application in Linux user-mode as a Device Under Test (DUT) within
the container. TG runs Scapy SW application as a packet Traffic Generator.
Network connectivity between SUTs and to TG is provided using virtual function
of physical NICs.

Virtual topologies are created on-demand whenever a verification job is
started (e.g. triggered by the gerrit patch submission) and destroyed
upon completion of all functional tests. Each node is a container running on
physical server. During the test execution, all nodes are reachable thru
the Management (not shown above for clarity).

Functional Tests Coverage
-------------------------

|csit-release| includes following VPP functionality tested in virtual VM
environment:

+-----------------------+----------------------------------------------+
| Functionality         |  Description                                 |
+=======================+==============================================+
| IPv4                  | ICMPv4.                                      |
+-----------------------+----------------------------------------------+
| IPv6                  | ICMPv6.                                      |
+-----------------------+----------------------------------------------+

Tests Naming
------------

|csit-release| follows a common structured naming convention for all
performance and system functional tests, introduced in CSIT-17.01.

The naming should be intuitive for majority of the tests. Complete
description of CSIT test naming convention is provided on
:ref:`csit_test_naming`.
