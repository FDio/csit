
.. |br| raw:: html

    <br />

eth2p-ethip4-sfc-classifier-func
````````````````````````````````

**NSH SFC Classifier test cases**  Test the SFC Classifier functional. DUT run the VPP with NSH SFC Plugin TG send a TCP packet to the DUT, if the packet match the SFC Classifier rules, the SFC Classifier will encapsulate this packet to a VxLAN-GPE and NSH packet, then the DUT will loopback the packet to the TG. The TG will capture this encapsulation packet and check the packet field is correct.

+----------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                           | Documentation                                                                                                                   | Status |
+================================================================+=================================================================================================================================+========+
| TC01: NSH SFC Classifier functional test with 72B frame size   | Make TG send 72 Bytes TCP packet to DUT ingress interface. Make TG verify SFC Classifier encapsulation functional is correct.   | PASS   |
+----------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: NSH SFC Classifier functional test with 128B frame size  | Make TG send 128 Bytes TCP packet to DUT ingress interface. Make TG verify SFC Classifier encapsulation functional is correct.  | PASS   |
+----------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: NSH SFC Classifier functional test with 256B frame size  | Make TG send 256 Bytes TCP packet to DUT ingress interface. Make TG verify SFC Classifier encapsulation functional is correct.  | PASS   |
+----------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: NSH SFC Classifier functional test with 512B frame size  | Make TG send 512 Bytes TCP packet to DUT ingress interface. Make TG verify SFC Classifier encapsulation functional is correct.  | PASS   |
+----------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+
| TC05: NSH SFC Classifier functional test with 1024B frame size | Make TG send 1024 Bytes TCP packet to DUT ingress interface. Make TG verify SFC Classifier encapsulation functional is correct. | PASS   |
+----------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+
| TC06: NSH SFC Classifier functional test with 1280B frame size | Make TG send 1280 Bytes TCP packet to DUT ingress interface. Make TG verify SFC Classifier encapsulation functional is correct. | PASS   |
+----------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+
| TC07: NSH SFC Classifier functional test with 1518B frame size | Make TG send 1518 Bytes TCP packet to DUT ingress interface. Make TG verify SFC Classifier encapsulation functional is correct. | PASS   |
+----------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4-nsh-proxy-inbound-func
```````````````````````````````````

**NSH SFC Proxy Inbound test cases**  Test the SFC Proxy Inbound functional. DUT run the VPP with NSH SFC Plugin, TG send a VxLAN-GPE+NSH packet to the DUT, if the packet match the SFC Proxy inbound rules, the SFC Proxy will pop the VxLAN-GPE and NSH protocol, then encapsulate with the VxLAN protocol. DUT will loopback the packet to the TG. The TG will capture this VxLAN packet and check the packet field is correct.

+-------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                              | Documentation                                                                                                                  | Status |
+===================================================================+================================================================================================================================+========+
| TC01: NSH SFC Proxy Inbound functional test with 152B frame size  | Make TG send 152 Bytes VxLAN-GPE+NSH packet to DUT ingress interface. Make TG verify SFC Proxy Inbound functional is correct.  | PASS   |
+-------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: NSH SFC Proxy Inbound functional test with 256B frame size  | Make TG send 256 Bytes VxLAN-GPE+NSH packet to DUT ingress interface. Make TG verify SFC Proxy Inbound functional is correct.  | PASS   |
+-------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: NSH SFC Proxy Inbound functional test with 512B frame size  | Make TG send 512 Bytes VxLAN-GPE+NSH packet to DUT ingress interface. Make TG verify SFC Proxy Inbound functional is correct.  | PASS   |
+-------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: NSH SFC Proxy Inbound functional test with 1024B frame size | Make TG send 1024 Bytes VxLAN-GPE+NSH packet to DUT ingress interface. Make TG verify SFC Proxy Inbound functional is correct. | PASS   |
+-------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+--------+
| TC05: NSH SFC Proxy Inbound functional test with 1280B frame size | Make TG send 1280 Bytes VxLAN-GPE+NSH packet to DUT ingress interface. Make TG verify SFC Proxy Inbound functional is correct. | PASS   |
+-------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+--------+
| TC06: NSH SFC Proxy Inbound functional test with 1518B frame size | Make TG send 1518 Bytes VxLAN-GPE+NSH packet to DUT ingress interface. Make TG verify SFC Proxy Inbound functional is correct. | PASS   |
+-------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4-nsh-proxy-outbound-func
````````````````````````````````````

**NSH SFC Proxy Outbound test cases**  Test the SFC Proxy Outbound functional. DUT run the VPP with NSH SFC Plugin, TG send a VxLAN packet to the DUT, if the packet match the SFC Proxy outbound rules, the SFC Proxy will push the NSH protocol, then encapsulate with the VxLAN-GPE protocol. DUT will loopback the packet to the TG. The TG will capture this VxLAN-GPE+NSH packet and check the packet field is correct.

+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                               | Documentation                                                                                                           | Status |
+====================================================================+=========================================================================================================================+========+
| TC01: NSH SFC Proxy Outbound functional test with 128B frame size  | Make TG send 128 Bytes VxLAN packet to DUT ingress interface. Make TG verify SFC Proxy Outbound functional is correct.  | PASS   |
+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: NSH SFC Proxy Outbound functional test with 256B frame size  | Make TG send 256 Bytes VxLAN packet to DUT ingress interface. Make TG verify SFC Proxy Outbound functional is correct.  | PASS   |
+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: NSH SFC Proxy Outbound functional test with 512B frame size  | Make TG send 512 Bytes VxLAN packet to DUT ingress interface. Make TG verify SFC Proxy Outbound functional is correct.  | PASS   |
+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: NSH SFC Proxy Outbound functional test with 1024B frame size | Make TG send 1024 Bytes VxLAN packet to DUT ingress interface. Make TG verify SFC Proxy Outbound functional is correct. | PASS   |
+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------+--------+
| TC05: NSH SFC Proxy Outbound functional test with 1280B frame size | Make TG send 1280 Bytes VxLAN packet to DUT ingress interface. Make TG verify SFC Proxy Outbound functional is correct. | PASS   |
+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------+--------+
| TC06: NSH SFC Proxy Outbound functional test with 1518B frame size | Make TG send 1518 Bytes VxLAN packet to DUT ingress interface. Make TG verify SFC Proxy Outbound functional is correct. | PASS   |
+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4-sfc-sff-func
`````````````````````````

**NSH SFC SFF test cases**  Test the SFC Service Function Forward functional. DUT run the VPP with NSH SFC Plugin, TG send a VxLAN-GPE+NSH packet to the DUT, if the packet match the SFC SFF rules, the SFC SFF will swap the VxLAN-GPE and NSH protocol. DUT will loopback the packet to the TG. The TG will capture this VxLAN-GPE+NSH packet and check the packet field is correct.

+---------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                    | Documentation                                                                                                        | Status |
+=========================================================+======================================================================================================================+========+
| TC01: NSH SFC SFF functional test with 152B frame size  | Make TG send 152 Bytes VxLAN-GPE+NSH packet to DUT ingress interface. Make TG verify SFC SFF functional is correct.  | PASS   |
+---------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+--------+
| TC02: NSH SFC SFF functional test with 256B frame size  | Make TG send 256 Bytes VxLAN-GPE+NSH packet to DUT ingress interface. Make TG verify SFC SFF functional is correct.  | PASS   |
+---------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+--------+
| TC03: NSH SFC SFF functional test with 512B frame size  | Make TG send 512 Bytes VxLAN-GPE+NSH packet to DUT ingress interface. Make TG verify SFC SFF functional is correct.  | PASS   |
+---------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+--------+
| TC04: NSH SFC SFF functional test with 1024B frame size | Make TG send 1024 Bytes VxLAN-GPE+NSH packet to DUT ingress interface. Make TG verify SFC SFF functional is correct. | PASS   |
+---------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+--------+
| TC05: NSH SFC SFF functional test with 1280B frame size | Make TG send 1280 Bytes VxLAN-GPE+NSH packet to DUT ingress interface. Make TG verify SFC SFF functional is correct. | PASS   |
+---------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+--------+
| TC06: NSH SFC SFF functional test with 1518B frame size | Make TG send 1518 Bytes VxLAN-GPE+NSH packet to DUT ingress interface. Make TG verify SFC SFF functional is correct. | PASS   |
+---------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------+--------+

