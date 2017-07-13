Overview
========

Tested Virtual Topologies
-------------------------

CSIT NSH_SFC functional tests are executed on virtualized topologies created
using Virtual Internet Routing Lab (VIRL) simulation platform contributed by
Cisco. VIRL runs on physical baremetal servers hosted by LF FD.io project.
Majority,of the tests are executed in the three node logical test topology -
Traffic Generator (TG) node and two Systems Under Test (SUT) nodes connected in
a loop. Some tests use two node logical test topology - TG node and SUT1 node.
Both logical test topologies are shown in the figures below.

::

    +------------------------+           +------------------------+
    |                        |           |                        |
    |  +------------------+  |           |  +------------------+  |
    |  |                  <----------------->                  |  |
    |  |                  |  |           |  |                  |  |
    |  |       DUT1       <----------------->       DUT2       |  |
    |  +--^--^------------+  |           |  +------------^--^--+  |
    |     |  |               |           |               |  |     |
    |     |  |         SUT1  |           |  SUT2         |  |     |
    +------------------------+           +------------------------+
          |  |                                           |  |
          |  |                                           |  |
          |  |               +-----------+               |  |
          |  +--------------->           <---------------+  |
          |                  |    TG     |                  |
          +------------------>           <------------------+
                             +-----------+

                       +------------------------+
                       |                        |
                       |  +------------------+  |
          +--------------->                  <--------------+
          |            |  |                  |  |           |
          |  |------------>       DUT1       <-----------+  |
          |  |         |  +------------------+  |        |  |
          |  |         |                        |        |  |
          |  |         |                  SUT1  |        |  |
          |  |         +------------------------+        |  |
          |  |                                           |  |
          |  |                                           |  |
          |  |               +-----------+               |  |
          |  +--------------->           <---------------+  |
          |                  |    TG     |                  |
          +------------------>           <------------------+
                             +-----------+

SUT1 and SUT2 are two VMs (Ubuntu or Centos, depending on the test suite), TG
is a Traffic Generator (TG, another Ubuntu VM). SUTs run VPP SW application in
Linux user-mode as a Device Under Test (DUT) within the VM. TG runs Scapy SW
application as a packet Traffic Generator. Logical connectivity between SUTs
and to TG is provided using virtual NICs using VMs' virtio driver.

Virtual testbeds are created on-demand whenever a verification job is started
(e.g. triggered by the gerrit patch submission) and destroyed upon completion
of all functional tests. Each node is a Virtual Machine and each connection
that is drawn on the diagram is available for use in any test case. During the
test execution, all nodes are reachable thru the Management network connected
to every node via dedicated virtual NICs and virtual links (not shown above
for clarity).

For the test cases that require DUT (VPP) to communicate with VM over the
vhost-user interfaces, a nested VM is created on SUT1 and/or SUT2 for the
duration of these particular test cases only. DUT (VPP) test topology with VM
is shown in the figure below including the applicable packet flow thru the VM
(marked in the figure with ``***``).

::

    +------------------------+           +------------------------+
    |      +----------+      |           |      +----------+      |
    |      |    VM    |      |           |      |    VM    |      |
    |      |  ******  |      |           |      |  ******  |      |
    |      +--^----^--+      |           |      +--^----^--+      |
    |        *|    |*        |           |        *|    |*        |
    |  +------v----v------+  |           |  +------v----v------+  |
    |  |      *    *      |**|***********|**|      *    *      |  |
    |  |  *****    *******<----------------->*******    *****  |  |
    |  |  *    DUT1       |  |           |  |       DUT2    *  |  |
    |  +--^---------------+  |           |  +---------------^--+  |
    |    *|                  |           |                  |*    |
    |    *|            SUT1  |           |  SUT2            |*    |
    +------------------------+           +------------------^-----+
         *|                                                 |*
         *|                                                 |*
         *|                  +-----------+                  |*
         *|                  |           |                  |*
         *+------------------>    TG     <------------------+*
         ******************* |           |********************
                             +-----------+

NSH_SFC Functional Tests Coverage
---------------------------------

Following NSH_SFC functional test areas are covered in the CSIT |release| with
results listed in this report:

- TODO


