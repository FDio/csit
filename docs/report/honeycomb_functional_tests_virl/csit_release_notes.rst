CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Naming change for all Honeycomb functional test suites in VIRL

    - Honeycomb functional test case names stayed unchanged

#. Added Honeycomb functional tests

    - NSH_SFC
    - LISP
    - NAT
    - SPAN

Functional Tests Naming
-----------------------

CSIT |release| introduced a common structured naming convention for all
performance and functional tests. This change was driven by substantially
growing number and type of CSIT test cases. Firstly, the original practice did
not always follow any strict naming convention. Secondly test names did not
always clearly capture tested packet encapsulations, and the actual type or
content of the tests. Thirdly HW configurations in terms of NICs, ports and
their locality were not captured either. These were but few reasons that drove
the decision to change and define a new more complete and stricter test naming
convention, and to apply this to all existing and new test cases.

The new naming should be intuitive for majority of the tests. The complete
description of CSIT test naming convention is provided on `CSIT test naming
page <https://wiki.fd.io/view/CSIT/csit-test-naming>`_.

Here few illustrative examples of the new naming usage for functional test
suites:

#. **Physical port to physical port - a.k.a. NIC-to-NIC, Phy-to-Phy, P2P**

    - *eth2p-ethip4-ip4base-func.robot* => 2 ports of Ethernet, IPv4 baseline
      routed forwarding, functional tests.

#. **Physical port to VM (or VM chain) to physical port - a.k.a. NIC2VM2NIC,
   P2V2P, NIC2VMchain2NIC, P2V2V2P**

    - *eth2p-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-func.robot* => 2 ports of
      Ethernet, IPv4 VXLAN Ethernet, L2 bridge-domain switching to/from two vhost
      interfaces and one VM, functional tests.


Known Issues
------------

Here is the list of known issues in CSIT |release| for Honeycomb functional
tests in VIRL:

+-------------------------------------------------+-----------------------------------------------------------------+
| Issue                                           | Description                                                     |
+-------------------------------------------------+-----------------------------------------------------------------+
| Operational data for Vhost-user interfaces      | Honeycomb Operational data reports Vhost-user interfaces        |
| "server" flag                                   | as client, even if they are server.                             |
+-------------------------------------------------+-----------------------------------------------------------------+
| Persistence of VxLAN tunnels                    | Configuration persistence often fails to restore                |
|                                                 | Honeycomb's internal naming context for VxLAN interfaces.       |
|                                                 | The interface is renamed to "vxlan_tunnel0" but is otherwise    |
|                                                 | configured correctly.                                           |
+-------------------------------------------------+-----------------------------------------------------------------+

