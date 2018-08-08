Overview
========

Virtual Topologies
------------------

CSIT NSH_SFC functional tests are executed on virtualized topologies created
using :abbr:`VIRL (Virtual Internet Routing Lab)` simulation platform
contributed by Cisco. VIRL runs on physical baremetal servers hosted by LF FD.io
project. Based on the packet path thru server SUTs, one logical
topology type is used for VPP DUT data plane testing:

#. NIC-to-NIC switching topologies.

NIC-to-NIC Switching
~~~~~~~~~~~~~~~~~~~~

The simplest logical topology for software data plane application like
VPP is NIC-to-NIC switching. Tested topology for the 3-Node
testbeds is shown in the figure below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/vpp_performance_tests/}}
                \includegraphics[width=0.90\textwidth]{logical-3n-nic2nic}
                \label{fig:logical-3n-nic2nic}
        \end{figure}

.. only:: html

    .. figure:: ../vpp_performance_tests/logical-3n-nic2nic.svg
        :alt: logical-3n-nic2nic
        :align: center

SUT1 and SUT2 are two VMs (Ubuntu or Centos, depending on the test suite), TG
is a Traffic Generator (TG, another Ubuntu VM). SUTs run NSH_SFC SW application
in Linux user-mode as a Device Under Test (DUT) within the VM. TG runs Scapy SW
application as a packet Traffic Generator. Logical connectivity between SUTs
and to TG is provided using virtual NICs using VMs' virtio driver.

Virtual testbeds are created on-demand whenever a verification job is started
(e.g. triggered by the gerrit patch submission) and destroyed upon completion
of all functional tests. Each node is a Virtual Machine and each connection
that is drawn on the diagram is available for use in any test case. During the
test execution, all nodes are reachable thru the Management network connected
to every node via dedicated virtual NICs and virtual links (not shown above
for clarity).

NSH_SFC Functional Tests Coverage
---------------------------------

Following NSH_SFC functional test areas are covered in the |csit-release| with
results listed in this report:

- **NSH SFC Classifier** - TG sends some TCP packets to test NSH SFC
  Classifier functional. DUT1 will receive these packets from one NIC and
  loopback the VXLAN-GPE-NSH encapsulated packets to the TG from other NIC.

  - Test case count: 7

- **NSH SFC Proxy Inbound** - TG sends some VXLAN-GPE-NSH encapsulated packets
  to test NSH SFC Proxy Inbound functional. DUT1 will receive these packets from
  one NIC and loopback the VXLAN encapsulated packets to the TG from other NIC.

  - Test case count: 6

- **NSH SFC Proxy Outbound** - TG sends some VXLAN encapsulated packets to test
  NSH SFC Proxy Outbound functional. DUT1 will receive these packets from one
  NIC and loopback the VXLAN-GPE-NSH encapsulated packets to the TG from other
  NIC.

  - Test case count: 6

- **NSH SFC Service Function Forward** - TG sends some VXLAN-GPE-NSH
  encapsulated packets to test NSH SFC Service Function Forward functional. DUT1
  will receive these packets from one NIC and swap the VXLAN-GPE-NSH header,
  after that DUT1 loopback the VXLAN-GPE-NSH encapsulated packtes to the TG from
  other NIC.

  - Test case count: 6

Total 25 NSH SFC functional tests in the |csit-release|.
