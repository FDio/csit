Overview
========

Virtual Topologies
------------------

CSIT VPP Device tests are executed in Physical containerized topologies
created on demand using set of scripts hosted and developed under CSIT
repository. It runs on physical baremetal servers hosted by LF FD.io project.
Based on the packet path thru SUT Containers, three distinct logical topology
types are used for VPP DUT data plane testing:

#. vfNIC-to-vfNIC switching topologies.
#. vfNIC-to-vhost-user switching topologies.
#. vfNIC-to-memif switching topologies.

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

vfNIC-to-vhost-user Switching
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

vfNIC-to-vhost-user switching topology test cases require VPP DUT to communicate
with Virtual Machine (VM) over Vhost-user virtual interfaces. VM is created on
SUT1 for the duration of these particular test cases only. Virtual test topology
with VM is shown in the figure below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/vpp_device_tests/}}
                \includegraphics[width=0.90\textwidth]{vf-2n-nic2vhost}
                \label{fig:vf-2n-nic2vhost}
        \end{figure}

.. only:: html

    .. figure:: ../vpp_device_tests/vf-2n-nic2vhost.svg
        :alt: vf-2n-nic2vhost
        :align: center

vfNIC-to-memif Switching
~~~~~~~~~~~~~~~~~~~~~~~~

vfNIC-to-memif switching topology test cases require VPP DUT to communicate
with another Docker Container over memif interfaces. Container is created for
the duration of these particular test cases only and it is running the same VPP
version as running on DUT. Virtual test topology with Memif is shown in
the figure below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/vpp_device_tests/}}
                \includegraphics[width=0.90\textwidth]{vf-2n-nic2memif}
                \label{fig:vf-2n-nic2memif}
        \end{figure}

.. only:: html

    .. figure:: ../vpp_device_tests/vf-2n-nic2memif.svg
        :alt: vf-2n-nic2memif
        :align: center

Functional Tests Coverage
-------------------------

|csit-release| includes following VPP functionality tested in VPP Device
environment:

+-----------------------+----------------------------------------------+
| Functionality         |  Description                                 |
+=======================+==============================================+
| ACL                   | Ingress Access Control List security for L2  |
|                       | Bridge-Domain MAC switching, IPv4 routing,   |
|                       | IPv6 routing.                                |
+-----------------------+----------------------------------------------+
| ADL                   | ADL address allow-list and block-list        |
|                       | filtering for IPv4 and IPv6 routing.         |
+-----------------------+----------------------------------------------+
| IPSec                 | IPSec tunnel and transport modes.            |
+-----------------------+----------------------------------------------+
| IPv4                  | IPv4 routing, ICMPv4.                        |
+-----------------------+----------------------------------------------+
| IPv6                  | IPv4 routing, ICMPv6.                        |
+-----------------------+----------------------------------------------+
| L2BD                  | L2 Bridge-Domain switching for untagged      |
|                       | Ethernet.                                    |
+-----------------------+----------------------------------------------+
| L2XC                  | L2 Cross-Connect switching for untagged      |
|                       | Ethernet.                                    |
+-----------------------+----------------------------------------------+
| Memif Interface       | Baseline VPP memif interface tests.          |
+-----------------------+----------------------------------------------+
| NAT44                 | Network Address and Port Translation         |
|                       | deterministic mode and endpoint-dependent    |
|                       | mode tests for IPv4.                         |
+-----------------------+----------------------------------------------+
| QoS Policer Metering  | Ingress packet rate metering and marking for |
|                       | IPv4, IPv6.                                  |
+-----------------------+----------------------------------------------+
| SRv6                  | Segment routing over IPv6, base and proxy.   |
+-----------------------+----------------------------------------------+
| Tap Interface         | Baseline Linux tap interface tests.          |
+-----------------------+----------------------------------------------+
| VLAN Tag              | L2 VLAN subinterfaces.                       |
+-----------------------+----------------------------------------------+
| Vhost-user Interface  | Baseline VPP vhost-user interface tests.     |
+-----------------------+----------------------------------------------+
| VXLAN                 | VXLAN overlay tunneling for L2-over-IPv4 and |
|                       | -over-IPv6.                                  |
+-----------------------+----------------------------------------------+

Tests Naming
------------

|csit-release| follows a common structured naming convention for all
performance and system functional tests, introduced in CSIT-17.01.

The naming should be intuitive for majority of the tests. Complete
description of CSIT test naming convention is provided on
:ref:`csit_test_naming`.
