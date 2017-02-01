
.. |br| raw:: html

    <br />

.. note::

    Data sources for reported test results: i) FD.io test executor jobs
    `hc2vpp-csit-integration-1701-ubuntu1404
    <https://jenkins.fd.io/view/hc2vpp/job/hc2vpp-csit-integration-1701-ubuntu1404/>`_
    , ii) archived FD.io jobs test result `output files
    <../../_static/archive/>`_.

mgmt-cfg-acl-apihc-apivat-func
``````````````````````````````

**Honeycomb access control lists test suite.**

+----------------------------------------------------------------+-------------------------------------------------------------------------------+--------+
| Name                                                           | Documentation                                                                 | Status |
+================================================================+===============================================================================+========+
| TC01: Honeycomb can create ACL classify table                  | Check if Honeycomb API can create an ACL table.                               | PASS   |
+----------------------------------------------------------------+-------------------------------------------------------------------------------+--------+
| TC02: Honeycomb can remove ACL table                           | Check if Honeycomb API can delete an ACL table.                               | PASS   |
+----------------------------------------------------------------+-------------------------------------------------------------------------------+--------+
| TC03: Honeycomb manages more than one ACL table                | Check if Honeycomb API can create another ACL table.                          | PASS   |
+----------------------------------------------------------------+-------------------------------------------------------------------------------+--------+
| TC04: Honeycomb can add ACL session to table                   | Check if Honeycomb API can add an ACL session to a table.                     | PASS   |
+----------------------------------------------------------------+-------------------------------------------------------------------------------+--------+
| TC05: Honeycomb can remove ACL session                         | Check if Honeycomb API can remove an ACL session.                             | PASS   |
+----------------------------------------------------------------+-------------------------------------------------------------------------------+--------+
| TC06: Honeycomb manages more than one ACL session on one table | Check if Honeycomb API can add another ACL session to a table.                | PASS   |
+----------------------------------------------------------------+-------------------------------------------------------------------------------+--------+
| TC07: Honeycomb enables ACL on interface                       | Check if Honeycomb API can enable ACL on an interface.                        | PASS   |
+----------------------------------------------------------------+-------------------------------------------------------------------------------+--------+
| TC08: Honeycomb disables ACL on interface                      | Check if Honeycomb API can disable ACL on an interface.                       | PASS   |
+----------------------------------------------------------------+-------------------------------------------------------------------------------+--------+
| TC09: Honeycomb can remove one out of multiple ACL tables      | Check if Honeycomb API can delete an ACL table if more than one table exists. | PASS   |
+----------------------------------------------------------------+-------------------------------------------------------------------------------+--------+

mgmt-cfg-int-apihcnc-func
`````````````````````````

**Netconf test suite. Contains test cases that need to bypass REST API.**

+--------------------------------------------------+-----------------------------------------------------------------------------------------------+--------+
| Name                                             | Documentation                                                                                 | Status |
+==================================================+===============================================================================================+========+
| TC01: Honeycomb can create and delete interfaces | Repeatedly create and delete an interface through Netconf and check the reply for any errors. | PASS   |
+--------------------------------------------------+-----------------------------------------------------------------------------------------------+--------+
| TC02: Transaction revert test case 1             | Configure two conflicting VxLAN tunnels, then verify that neither tunnel exists.              | PASS   |
+--------------------------------------------------+-----------------------------------------------------------------------------------------------+--------+
| TC03: Transaction revert test case 2             | Configure two conflicting TAP interfaces, then verify that neither interface exists.          | PASS   |
+--------------------------------------------------+-----------------------------------------------------------------------------------------------+--------+

mgmt-cfg-int-subint-apihc-apivat-func
`````````````````````````````````````

**Honeycomb sub-interface management test suite.**

+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                            | Documentation                                                                                                             | Status |
+=================================================================================+===========================================================================================================================+========+
| TC01: Honycomb creates sub-interface                                            | Check if Honeycomb creates a sub-interface.                                                                               | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: Honeycomb sets interface and sub-interface up                             | Honeycomb changes the state of interface and of its sub-interface to up.                                                  | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: Honeycomb sets sub-interface down while its super-interface is up         | Honeycomb sets the sub-interface down while its  super-interface is up. It must be possible.                              | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: Honeycomb sets interface and sub-interface down                           | Honeycomb changes the state of interface down and then  changes the state of its sub-interface down, in this order.       | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC05: Honeycomb fails to set sub-interface up while its super-interface is down | Honeycomb tries to set the sub-interface up while its  super-interface is down. It must not be possible.                  | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC06: Honeycomb fails to delete sub-interface                                   | Check if Honeycomb can delete an existing sub-interface.                                                                  | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC07: Honeycomb adds sub-interface to new bridge domain                         | Check if Honeycomb adds a sub-interface to bridge domain.                                                                 | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC08: Honeycomb enables tag-rewrite pop 1                                       | Check if Honeycomb enables tag-rewrite and sets its  parameters correctly. Case: pop 1.                                   | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC09: Honeycomb enables tag-rewrite push                                        | Check if Honeycomb enables tag-rewrite and sets its  parameters correctly. Case: push.                                    | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC10: Honeycomb enables tag-rewrite translate 1-2                               | Check if Honeycomb enables tag-rewrite and sets its  parameters correctly. Case: translate 1-2.                           | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC11: Honeycomb disables tag-rewrite                                            | Check if Honeycomb disables the tag-rewrite.                                                                              | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC12: Honeycomb enables tag-rewrite pop 1 again                                 | Check if Honeycomb can enable tag-rewrite again, once it  was disabled by Honeycomb.                                      | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC13: Honeycomb modifies the tag-rewrite                                        | Honeycomb sets the tag-rewrite: 1. pop 1, then 2. push, then 3. translate 1 - 2 Then Honeycomb disables the tag-rewrite.  | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC14: Honeycomb fails to set wrong vlan-type in tag-rewrite                     | Check that Honeycomb does not accept wrong values of  vlan-type in tag-rewrite.                                           | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC15: Honeycomb configures sub-interface ipv4 address                           | Check if Honeycomb can configure an ipv4 address on the sub-interface.                                                    | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC16: Honeycomb removes sub-interface ipv4 address                              | Check if Honeycomb can remove configured ipv4 addresses from the sub-interface.                                           | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+
| TC17: Honeycomb modifies existing sub-interface ipv4 address                    | Check if Honeycomb can modify an ipv4 address already configured on the sub-interface.                                    | PASS   |
+---------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------+

mgmt-cfg-intip4-intip6-apihc-apivat-func
````````````````````````````````````````

**Honeycomb interface management test suite.**

+--------------------------------------------------------------+---------------------------------------------------------------------------------------------+--------+
| Name                                                         | Documentation                                                                               | Status |
+==============================================================+=============================================================================================+========+
| TC01: Honeycomb configures and reads interface state         | Check if Honeycomb API can modify the admin state of VPP interfaces.                        | PASS   |
+--------------------------------------------------------------+---------------------------------------------------------------------------------------------+--------+
| TC02: Honeycomb modifies interface IPv4 address with netmask | Check if Honeycomb API can configure interfaces for ipv4 with address and netmask provided. | PASS   |
+--------------------------------------------------------------+---------------------------------------------------------------------------------------------+--------+
| TC03: Honeycomb removes IPv4 address from interface          | Check if Honeycomb API can remove configured ipv4 addresses from interface.                 | PASS   |
+--------------------------------------------------------------+---------------------------------------------------------------------------------------------+--------+
| TC04: Honeycomb modifies interface IPv4 address with prefix  | Check if Honeycomb API can configure interfaces for ipv4 with address and prefix provided.  | PASS   |
+--------------------------------------------------------------+---------------------------------------------------------------------------------------------+--------+
| TC05: Honeycomb modifies IPv4 neighbor table                 | Check if Honeycomb API can add and remove ARP entries.                                      | PASS   |
+--------------------------------------------------------------+---------------------------------------------------------------------------------------------+--------+
| TC06: Honeycomb modifies interface configuration - IPv6      | Check if Honeycomb API can configure interfaces for ipv6.                                   | PASS   |
+--------------------------------------------------------------+---------------------------------------------------------------------------------------------+--------+
| TC07: Honeycomb modifies interface configuration - MTU       | Check if Honeycomb API can configure interface MTU value.                                   | PASS   |
+--------------------------------------------------------------+---------------------------------------------------------------------------------------------+--------+

mgmt-cfg-inttap-apihc-apivat-func
`````````````````````````````````

**Honeycomb TAP management test suite.**

+---------------------------------------------------------------+---------------------------------------------------------------------------------------+--------+
| Name                                                          | Documentation                                                                         | Status |
+===============================================================+=======================================================================================+========+
| TC01: Honeycomb configures TAP interface                      | Check if Honeycomb API can configure a TAP interface.                                 | PASS   |
+---------------------------------------------------------------+---------------------------------------------------------------------------------------+--------+
| TC02: Honeycomb modifies existing TAP interface configuration | Check if Honeycomb API can re-configure and existing TAP interface with new settings. | PASS   |
+---------------------------------------------------------------+---------------------------------------------------------------------------------------+--------+
| TC03: Honeycomb removes TAP interface                         | Check if Honeycomb API can remove TAP interface.                                      | PASS   |
+---------------------------------------------------------------+---------------------------------------------------------------------------------------+--------+

mgmt-cfg-intvhost-apihc-apivat-func
```````````````````````````````````

**Honeycomb vhost-user interface management test suite.**

+---------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                            | Documentation                                                                                                | Status |
+=================================================================================+==============================================================================================================+========+
| TC01: Honeycomb creates vhost-user interface - server                           | Check if Honeycomb creates a vhost-user interface, role: server.                                             | FAIL   |
+---------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------+--------+
| TC02: Honeycomb modifies vhost-user interface - server                          | Check if Honeycomb can modify properties of existing vhost-user interface, role: server.                     | FAIL   |
+---------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------+--------+
| TC03: Honeycomb deletes vhost-user interface - server                           | Check if Honeycomb can delete an existing vhost-user interface, role: server.                                | FAIL   |
+---------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------+--------+
| TC04: Honeycomb creates vhost-user interface - client                           | Check if Honeycomb creates a vhost-user interface, role: client.                                             | FAIL   |
+---------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------+--------+
| TC05: Honeycomb modifies vhost-user interface - client                          | Check if Honeycomb can modify properties of existing vhost-user interface, role: client.                     | FAIL   |
+---------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------+--------+
| TC06: Honeycomb deletes vhost-user interface - client                           | Check if Honeycomb can delete an existing vhost-user interface, role: client.                                | FAIL   |
+---------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------+--------+
| TC07: Honeycomb does not set vhost-user configuration on another interface type | Check if Honeycomb refuses to set vhost-user configuration for interface which is not v3po:vhost-user type.  | FAIL   |
+---------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------+--------+
| TC08: Honeycomb does not set invalid vhost-user configuration                   | Check if Honeycomb refuses to set invalid parameters to vhost-user interface.                                | FAIL   |
+---------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------+--------+

mgmt-cfg-l2bd-apihc-apivat-func
```````````````````````````````

**Honeycomb bridge domain management test suite.**

+------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                   | Documentation                                                                                                     | Status |
+========================================================================+===================================================================================================================+========+
| TC01: Honeycomb sets up l2 bridge domain                               | Check if Honeycomb can create bridge domains on VPP node.                                                         | PASS   |
+------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------+--------+
| TC02: Honeycomb manages multiple bridge domains on node                | Check if Honeycomb can manage multiple bridge domains on a single node.                                           | PASS   |
+------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------+--------+
| TC03: Honeycomb removes bridge domains                                 | Check if Honeycomb can remove bridge domains from a VPP node.                                                     | PASS   |
+------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------+--------+
| TC04: Honeycomb assigns interfaces to bridge domain                    | Check if Honeycomb can assign VPP interfaces to an existing bridge domain.                                        | PASS   |
+------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------+--------+
| TC05: Honeycomb cannot remove bridge domain with an interface assigned | Check if Honeycomb can remove a bridge domain that has an interface assigned to it. Expect to fail with code 500. | PASS   |
+------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------+--------+

mgmt-cfg-l2fib-apihc-apivat-func
````````````````````````````````

**Honeycomb L2 FIB management test suite.**

+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                    | Documentation                                                                                                                   | Status |
+=========================================================+=================================================================================================================================+========+
| TC01: Honeycomb adds L2 FIB entry (forward)             | Honeycomb creates a bridge domain and assignes an  interface to it. Then adds an L2 FIB entry (forward) to the bridge  domain.  | PASS   |
+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: Honeycomb adds L2 FIB entry (static, forward)     | Honeycomb adds an L2 FIB entry (static, forward) to the  bridge domain.                                                         | PASS   |
+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: Honeycomb adds L2 FIB entry (static, filter)      | Honeycomb adds an L2 FIB entry (static, filter) to the  bridge domain.                                                          | PASS   |
+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: Honeycomb adds and removes L2 FIB entry (forward) | Honeycomb adds an L2 FIB entry (forward) to the bridge  domain and then Honeycomb removes it from the bridge domain.            | PASS   |
+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+
| TC05: Honeycomb adds more than one L2 FIB entry         | Honeycomb adds three L2 FIB entries to the bridge domain.                                                                       | PASS   |
+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+
| TC06: Honeycomb fails to set wrong L2 FIB entry         | Honeycomb tries to add an L2 FIB entry with wrong  parameters to the bridge domain. It must fail.                               | PASS   |
+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+
| TC07: Honeycomb fails to modify existing L2 FIB entry   | Honeycomb tries to modify an existing L2 FIB entry. It  must fail.                                                              | PASS   |
+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+

mgmt-cfg-lisp-apihc-apivat-func
```````````````````````````````

**Honeycomb Lisp test suite.**

+------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+
| Name                                                             | Documentation                                                                                      | Status |
+==================================================================+====================================================================================================+========+
| TC01: Honeycomb enables Lisp feature                             | Check if Honeycomb can enable the Lisp feature.                                                    | PASS   |
+------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+
| TC02: Honeycomb adds locator set and locator                     | Check if Honeycomb can configure a locator set.                                                    | PASS   |
+------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+
| TC03: Honeycomb configures Lisp - remote mapping - Bridge Domain | Check if Honeycomb can configure a remote Lisp mapping with a bridge domain.                       | PASS   |
+------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+
| TC04: Honeycomb can remove Lisp mapping                          | Check if Honeycomb can remove a configured Lisp mapping.                                           | PASS   |
+------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+
| TC05: Honeycomb configures Lisp - remote mapping - VRF           | Check if Honeycomb can configure a remote Lisp mapping with VRF.                                   | PASS   |
+------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+
| TC06: Honeycomb configures Lisp - local mapping - Bridge Domain  | Check if Honeycomb can configure a local Lisp mapping with a bridge domain.                        | PASS   |
+------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+
| TC07: Honeycomb configures Lisp - local mapping - VRF            | Check if Honeycomb can configure a local Lisp mapping with VRF.                                    | PASS   |
+------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+
| TC08: Honeycomb configures Lisp mapping with adjacency           | Check if Honeycomb can configure local and remote Lisp mappings with VRF, and configure adjacency. | PASS   |
+------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+
| TC09: Honeycomb configures Lisp map resolver                     | Check if Honeycomb can configure a Lisp map resolver.                                              | PASS   |
+------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+
| TC10: Honeycomb enabled Lisp PITR feature                        | Check if Honeycomb can configure the Lisp PITR feature.                                            | PASS   |
+------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+
| TC11: Honeycomb can remove configuration of Lisp features        | Check if Honeycomb can disable all Lisp features.                                                  | PASS   |
+------------------------------------------------------------------+----------------------------------------------------------------------------------------------------+--------+

mgmt-cfg-nsh-apihc-apivat-func
``````````````````````````````

**Honeycomb NSH test suite.**

+---------------------------------------------------------------------+---------------------------------------------------------------------------+--------+
| Name                                                                | Documentation                                                             | Status |
+=====================================================================+===========================================================================+========+
| TC01: Honeycomb can configure NSH entry                             | Check if Honeycomb can configure an NSH entry.                            | PASS   |
+---------------------------------------------------------------------+---------------------------------------------------------------------------+--------+
| TC02: Honeycomb can remove NSH entry                                | Check if Honeycomb can remove an existing NSH entry.                      | PASS   |
+---------------------------------------------------------------------+---------------------------------------------------------------------------+--------+
| TC03: Honeycomb can configure new NSH entry                         | Check if Honeycomb can configure an NSH antry after one has been deleted. | PASS   |
+---------------------------------------------------------------------+---------------------------------------------------------------------------+--------+
| TC04: Honeycomb can configure multiple NSH entries at the same time | Check if Honeycomb can configure an NSH entry when one already exists.    | PASS   |
+---------------------------------------------------------------------+---------------------------------------------------------------------------+--------+
| TC05: Honeycomb can configure NSH map                               | Check if Honeycomb can configure an NSH map.                              | PASS   |
+---------------------------------------------------------------------+---------------------------------------------------------------------------+--------+
| TC06: Honeycomb can remove NSH map                                  | Check if Honeycomb can remove an existing NSH map.                        | PASS   |
+---------------------------------------------------------------------+---------------------------------------------------------------------------+--------+
| TC07: Honeycomb can modify existing NSH map                         | Check if Honeycomb can configure an NSH map after one has been deleted.   | PASS   |
+---------------------------------------------------------------------+---------------------------------------------------------------------------+--------+
| TC08: Honeycomb can configure multiple NSH maps at the same time    | Check if Honeycomb can configure and NSH map when one already exists.     | PASS   |
+---------------------------------------------------------------------+---------------------------------------------------------------------------+--------+

mgmt-cfg-pbb-apihc-apivat-func
``````````````````````````````

**Honeycomb provider backbone bridge test suite.**

+----------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                             | Documentation                                                                                                                                  | Status |
+==================================================================================+================================================================================================================================================+========+
| TC01: Honeycomb sets PBB sub-interface                                           | Honeycomb creates a new PBB sub-interface.                                                                                                     | PASS   |
+----------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: Honeycomb modifies existing PBB sub-interface                              | Honeycomb modifies an existing PBB sub-interface.                                                                                              | PASS   |
+----------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: Honeycomb deletes existing PBB sub-interface                               | Honeycomb deletes an existing PBB sub-interface.                                                                                               | PASS   |
+----------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: Honeycomb fails to set wrong destination-address for new PBB sub-interface | Honeycomb fails to create a new PBB sub-interface with wrong value of parameter destination-address, type yang:mac-address.                    | PASS   |
+----------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC05: Honeycomb fails to set wrong source-address for new PBB sub-interface      | Honeycomb fails to create a new PBB sub-interface with wrong value of parameter source-address, type yang:mac-address.                         | PASS   |
+----------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC06: Honeycomb fails to set wrong b-vlan-tag-vlan-id for new PBB sub-interface  | Honeycomb fails to create a new PBB sub-interface with wrong value of parameter b-vlan-tag-vlan-id, type uint16, 12 bit range, range 1..4095.  | PASS   |
+----------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC07: Honeycomb fails to set wrong i-tag-isid for new PBB sub-interface          | Honeycomb fails to create a new PBB sub-interface with wrong value of parameter i-tag-isid, type uint32, 24 bit range, range 1..16777215.      | PASS   |
+----------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC08: Honeycomb fails to create new PBB sub-interface without vlan tag           | Honeycomb fails to create a new PBB sub-interface without parameter b-vlan-tag-vlan-id.                                                        | PASS   |
+----------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------+--------+

mgmt-cfg-snat44-apihc-apivat-func
`````````````````````````````````

**Honeycomb NAT test suite.**

+-----------------------------------------------------+-----------------------------------------------------------------+--------+
| Name                                                | Documentation                                                   | Status |
+=====================================================+=================================================================+========+
| TC01: Honeycomb configures NAT entry                | Honeycomb configures a static NAT entry.                        | PASS   |
+-----------------------------------------------------+-----------------------------------------------------------------+--------+
| TC02: Honeycomb removes NAT entry                   | Honeycomb removes a configured static NAT entry.                | PASS   |
+-----------------------------------------------------+-----------------------------------------------------------------+--------+
| TC03: Honeycomb configures multiple NAT entries     | Honeycomb configures two static NAT entries.                    | PASS   |
+-----------------------------------------------------+-----------------------------------------------------------------+--------+
| TC04: Honeycomb enables NAT on interface - inbound  | Honeycomb configures NAT on an interface in inbound direction.  | PASS   |
+-----------------------------------------------------+-----------------------------------------------------------------+--------+
| TC05: Honeycomb removes NAT interface configuration | Honeycomb removes NAT configuration from an interface.          | PASS   |
+-----------------------------------------------------+-----------------------------------------------------------------+--------+
| TC06: Honeycomb enables NAT on interface - outbound | Honeycomb configures NAT on an interface in outbound direction. | PASS   |
+-----------------------------------------------------+-----------------------------------------------------------------+--------+

mgmt-cfg-vxlan-apihc-apivat-func
````````````````````````````````

**Honeycomb VxLAN management test suite.**

+----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------+--------+
| Name                                                                       | Documentation                                                                                        | Status |
+============================================================================+======================================================================================================+========+
| TC01: Honeycomb configures VxLAN tunnel                                    | Check if Honeycomb API can configure VxLAN settings.                                                 | PASS   |
+----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------+--------+
| TC02: Honeycomb disables VxLAN tunnel                                      | Check if Honeycomb API can reset VxLAN configuration.                                                | PASS   |
+----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------+--------+
| TC03: Honeycomb can configure VXLAN tunnel after one has been disabled     | Check if Honeycomb API can configure VxLAN settings again after previous settings have been removed. | PASS   |
+----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------+--------+
| TC04: Honeycomb does not set VxLAN configuration on another interface type | Check if Honeycomb API prevents setting VxLAN on incorrect interface.                                | PASS   |
+----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------+--------+
| TC05: Honeycomb does not set invalid VxLAN configuration                   | Check if Honeycomb API prevents setting incorrect VxLAN settings.                                    | PASS   |
+----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------+--------+
| TC06: Honeycomb configures VxLAN tunnel with ipv6                          | Check if Honeycomb API can configure VxLAN with ipv6 settings.                                       | PASS   |
+----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------+--------+

mgmt-cfg-vxlangpe-apihc-apivat-func
```````````````````````````````````

**Honeycomb VxLAN-GPE management test suite.**

+-----------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+--------+
| Name                                                                        | Documentation                                                                                   | Status |
+=============================================================================+=================================================================================================+========+
| TC01: Honeycomb creates VxLAN GPE tunnel                                    | Check if Honeycomb API can configure a VxLAN GPE tunnel.                                        | PASS   |
+-----------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+--------+
| TC02: Honeycomb removes VxLAN GPE tunnel                                    | Check if Honeycomb API can remove VxLAN GPE tunnel.                                             | PASS   |
+-----------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+--------+
| TC03: Honeycomb sets wrong interface type while creating VxLAN GPE tunnel   | Check if Honeycomb refuses to create a VxLAN GPE tunnel with a wrong interface type set.        | PASS   |
+-----------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+--------+
| TC04: Honeycomb sets wrong protocol while creating VxLAN GPE tunnel         | Check if Honeycomb refuses to create a VxLAN GPE tunnel with a wrong next-protocol set.         | PASS   |
+-----------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+--------+
| TC05: Honeycomb sets VxLAN GPE tunnel on existing interface with wrong type | Check if Honeycomb refuses to create a VxLAN GPE tunnel on existing interface with wrong type.  | PASS   |
+-----------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+--------+
| TC06: Honeycomb creates VxLAN GPE tunnel with ipv6                          | Check if Honeycomb API can configure a VxLAN GPE tunnel with IPv6 addresses.                    | PASS   |
+-----------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+--------+
| TC07: Honeycomb creates a second VxLAN GPE tunnel with ipv6                 | Check if Honeycomb API can configure another VxLAN GPE tunnel with IPv6 addresses.              | PASS   |
+-----------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------+--------+

mgmt-notif-apihcnc-func
```````````````````````

**Honeycomb notifications test suite.**

+--------------------------------------------------------------+--------------------------------------------------------------------------------------------------+--------+
| Name                                                         | Documentation                                                                                    | Status |
+==============================================================+==================================================================================================+========+
| TC01: Honeycomb sends notification on interface state change | Check if Honeycomb sends a state-changed notification when the state of an interface is changed. | PASS   |
+--------------------------------------------------------------+--------------------------------------------------------------------------------------------------+--------+
| TC02: Honeycomb sends notification on interface deletion     | Check if Honeycomb sends an interface-deleted notification when an interface is deleted.         | PASS   |
+--------------------------------------------------------------+--------------------------------------------------------------------------------------------------+--------+

mgmt-statepersist-apihc-func
````````````````````````````

**Honeycomb configuration persistence test suite.**

+----------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------+--------+
| Name                                                                             | Documentation                                                                                       | Status |
+==================================================================================+=====================================================================================================+========+
| TC01: Honeycomb persists configuration through restart of both Honeycomb and VPP | Checks if Honeycomb maintains configuration after both Honeycomb and VPP are restarted.             | FAIL   |
+----------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------+--------+
| TC02: Honeycomb persists configuration through restart of Honeycomb              | Checks if Honeycomb maintains configuration after it is restarted.                                  | FAIL   |
+----------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------+--------+
| TC03: Honeycomb persists configuration through restart of VPP                    | Checks if Honeycomb updates VPP settings after VPP is restarted.                                    | FAIL   |
+----------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------+--------+
| TC04: Honeycomb reverts to defaults if persistence files are invalid             | Checks if Honeycomb reverts to default configuration when persistence files are damaged or invalid. | PASS   |
+----------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------+--------+
