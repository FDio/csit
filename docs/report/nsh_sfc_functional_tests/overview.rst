Overview
========

Virtual Topologies
------------------

CSIT NSH_SFC functional tests are executed in VM-based virtual
topologies created on demand using :abbr:`VIRL (Virtual Internet Routing
Lab)` simulation platform contributed by Cisco. VIRL runs on physical
baremetal servers hosted by LF FD.io project. All tests are executed in
three-node virtual test topology shown in the figure below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/vpp_functional_tests/}}
                \includegraphics[width=0.90\textwidth]{virtual-3n-nic2nic}
                \label{fig:virtual-3n-nic2nic}
        \end{figure}

.. only:: html

    .. figure:: ../vpp_functional_tests/virtual-3n-nic2nic.svg
        :alt: virtual-3n-nic2nic
        :align: center

SUT1 and SUT2 are two VMs (running Ubuntu or Centos, depending on the
test suite), TG is a Traffic Generator (running Ubuntu VM). SUTs run VPP
with nsh-plugin in Linux user-mode as a Device Under Test (DUT) within
the VM. TG runs Scapy SW application as a packet Traffic Generator.
Network connectivity between SUTs and to TG is provided using virtual
NICs and VMs' virtio drivers.

Functional Tests Coverage
-------------------------

|csit-release| includes following NSH_SFC functionality tested in
virtual VM environment:

+-----------------------+----------------------------------------------+
| Functionality         |  Description                                 |
+=======================+==============================================+
| NSH SFC Classifier    | TG sends some TCP packets to test NSH SFC    |
|                       | Classifier functional. DUT1 will receive     |
|                       | these packets from one NIC and loopback the  |
|                       | VXLAN-GPE-NSH encapsulated packets to the TG |
|                       | from other NIC.                              |
|                       | Test case count: 7.                          |
+-----------------------+----------------------------------------------+
| NSH SFC Proxy Inbound | TG sends some VXLAN-GPE-NSH encapsulated     |
|                       | packets to test NSH SFC Proxy Inbound        |
|                       | functional. DUT1 will receive these packets  |
|                       | from one NIC and loopback the VXLAN          |
|                       | encapsulated packets to the TG from other    |
|                       | NIC.                                         |
|                       | Test case count: 6.                          |
+-----------------------+----------------------------------------------+
| NSH SFC Proxy         | TG sends some VXLAN encapsulated packets to  |
| Outbound              | test NSH SFC Proxy Outbound functional. DUT1 |
|                       | will receive these packets from one NIC and  |
|                       | loopback the VXLAN-GPE-NSH encapsulated      |
|                       | packets to the TG from other NIC.            |
|                       | Test case count: 6.                          |
+-----------------------+----------------------------------------------+
| NSH SFC Service       | TG sends some VXLAN-GPE-NSH                  |
| Function Forward      | encapsulated packets to test NSH SFC Service |
|                       | Function Forward functional. DUT1 will       |
|                       | receive these packets from one NIC and swap  |
|                       | the VXLAN-GPE-NSH header, after that DUT1    |
|                       | loopback the VXLAN-GPE-NSH encapsulated      |
|                       | packets to the TG from other NIC.            |
|                       | Test case count: 6.                          |
+-----------------------+----------------------------------------------+

Total 25 NSH_SFC functional tests in the |csit-release|.
