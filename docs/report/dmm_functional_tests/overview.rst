Overview
========

Virtual Topologies
------------------

CSIT DMM functional tests are executed on virtualized topologies created using
:abbr:`VIRL (Virtual Internet Routing Lab)` simulation platform contributed by
Cisco. VIRL runs on physical baremetal servers hosted by LF FD.io project.
Based on the packet path through server SUTs, one logical topology type
is used for DMM DUT data plane testing:

#. NIC-to-NIC switching topologies.

NIC-to-NIC Switching
~~~~~~~~~~~~~~~~~~~~

The simplest logical topology for software data plane application like
DMM is NIC-to-NIC switching. Tested topologies for the 3-Node
testbed is shown in the figure below.

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

SUT1 and SUT2 are two VMs (Ubuntu), TG
is a Traffic Generator (TG, another Ubuntu VM). SUTs run sample server-client
application using the DMM libs in Linux user-mode as a Device Under Test (DUT)
within the VM. Currently TG node is not being used in DMM-CSIT. Logical
connectivity between SUTs is provided using virtual NICs using VMs' virtio
driver.

Virtual testbeds are created on-demand whenever a verification job is started
(e.g. triggered by the gerrit patch submission) and destroyed upon completion
of all functional tests. Each node is a Virtual Machine and each connection
that is drawn on the diagram is available for use in any test case. During the
test execution, all nodes are reachable through the Management network connected
to every node via dedicated virtual NICs and virtual links (not shown above
for clarity).

DMM Functional Tests Coverage
-----------------------------

Following DMM functional test areas are covered in the |csit-release| with
results listed in this report:

- **DMM basic testcase** - DMM has only one test case right now.
  The testcase demonstrates single server[DUT1] and single client[DUT2] scenario
  using DMM framework and kernel tcp/ip stack.

  - Test case count: 1

Total 1 DMM functional test in the |csit-release|.
