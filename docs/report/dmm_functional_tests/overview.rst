Overview
========

Virtual Topologies
------------------

CSIT DMM functional tests are executed in VM-based virtual topologies
created on demand using :abbr:`VIRL (Virtual Internet Routing Lab)`
simulation platform contributed by Cisco. VIRL runs on physical
baremetal servers hosted by LF FD.io project.

All tests are executed in three-node virtual test topology shown in the
figure below.

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

SUT1 and SUT2 are two VMs (running Ubuntu), TG is a Traffic Generator VM
(running Ubuntu). SUTs run
sample server-client application using the DMM libraries in Linux user-
mode as a Device Under Test (DUT) within the VM. Currently TG node is
not being used in DMM-CSIT. Network connectivity between SUTs and to TG
is provided using virtual NICs and VMs' virtio drivers.

Functional Tests Coverage
-------------------------

|csit-release| includes following DMM functionality tested in virtual VM
environment:

+-----------------------+----------------------------------------------+
| Functionality         |  Description                                 |
+=======================+==============================================+
| DMM basic operation   | The test case demonstrates single            |
|                       | server[DUT1] and single client[DUT2]         |
|                       | scenario using DMM framework and kernel      |
|                       | tcp/ip stack.                                |
+-----------------------+----------------------------------------------+
| DMM lwip integration  |                                              |
+-----------------------+----------------------------------------------+
