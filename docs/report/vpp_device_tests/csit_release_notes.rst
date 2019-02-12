Release Notes
=============

Changes in |csit-release|
-------------------------

#. TEST FRAMEWORK

   - **VM and "nested" container support**: Framework has been extended to
     allow to run Virtual Machine (VM) on SUT1 and to start another Docker
     Container from SUT1.

#. NEW TESTS

   - **L2BD and L2XC**: L2 Cross-Connect switching and L2 Bridge-Domain
     switching between vfNICs for untagged ethernet.

   - **VM_Vhost**: VPP DUT is configured with IPv4/IPv6 routing or L2
     cross-connect/bridge-domain switching between vfNICs and Vhost-user
     interfaces. VM - Qemu Guest is connected to VPP via Vhost-user interfaces.
     Guest is configured with linux bridge interconnecting vhost-user
     interfaces.

   - **Container_Memif**: VPP DUT is configured with IPv4/IPv6 routing or L2
     cross-connect/bridge-domain switching between vfNICs and Memif interfaces.
     Container is connected to VPP via Memif interface. Container is running the
     same VPP version as running on DUT.

Known Issues
------------

List of known issues in |csit-release| for VPP functional tests in VPP Device:

+---+----------------------------------------+---------------------+
| # | JiraID                                 | Issue Description   |
+===+========================================+=====================+
| 1 |                                        |                     |
+---+----------------------------------------+---------------------+
