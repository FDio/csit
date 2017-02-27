# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Contains RPC sequences to trigger specific issues through Netconf."""

# Test data for issue: https://jira.fd.io/browse/HONEYCOMB-105
# Creating and removing interfaces may result in duplicated interface indices.
trigger_105 = u"""
<rpc message-id="m-1" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<get-config>
<source>
<running/>
</source>
<filter xmlns:ns0="urn:ietf:params:xml:ns:netconf:base:1.0" ns0:type="subtree">
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
<interface>
<name>4fe335c8-6fdc-4654-b12c-d256e9b39229</name>
</interface>
</interfaces>
</filter>
</get-config>
</rpc>
]]>]]>

<rpc message-id="m-2" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<lock>
<target>
<candidate/>
</target>
</lock>
</rpc>
]]>]]>

<rpc message-id="m-3" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<edit-config>
<target>
<candidate/>
</target>
<default-operation>none</default-operation>
<config>
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
<interface xmlns:a="urn:ietf:params:xml:ns:netconf:base:1.0"
a:operation="replace">
<name>4fe335c8-6fdc-4654-b12c-d256e9b39229</name>
<description>neutron port</description>
<link-up-down-trap-enable>enabled</link-up-down-trap-enable>
<vhost-user xmlns="urn:opendaylight:params:xml:ns:yang:v3po">
<role>client</role>
<socket>/tmp/socket_4fe335c8-6fdc-4654-b12c-d256e9b39229</socket>
</vhost-user>
<type xmlns:x="urn:opendaylight:params:xml:ns:yang:v3po">x:vhost-user</type>
<enabled>true</enabled>
</interface>
</interfaces>
</config>
</edit-config>
</rpc>
]]>]]>

<rpc message-id="m-4" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<commit/>
</rpc>
]]>]]>

<rpc message-id="m-5" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<unlock>
<target>
<candidate/>
</target>
</unlock>
</rpc>
]]>]]>

<rpc message-id="m-6" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<lock>
<target>
<candidate/>
</target>
</lock>
</rpc>
]]>]]>

<rpc message-id="m-7" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<edit-config>
<target>
<candidate/>
</target>
<default-operation>none</default-operation>
<config>
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
<interface xmlns:a="urn:ietf:params:xml:ns:netconf:base:1.0"
a:operation="delete">
<name>4fe335c8-6fdc-4654-b12c-d256e9b39229</name>
</interface>
</interfaces>
</config>
</edit-config>
</rpc>
]]>]]>

<rpc message-id="m-8" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<commit/>
</rpc>
]]>]]>

<rpc message-id="m-9" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<unlock>
<target>
<candidate/>
</target>
</unlock>
</rpc>
]]>]]>

<rpc message-id="m-10" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<lock>
<target>
<candidate/>
</target>
</lock>
</rpc>
]]>]]>

<rpc message-id="m-11" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<edit-config>
<target>
<candidate/>
</target>
<default-operation>none</default-operation>
<config>
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
<interface xmlns:a="urn:ietf:params:xml:ns:netconf:base:1.0"
a:operation="replace">
<name>4fe335c8-6fdc-4654-b12c-d256e9b39229</name>
<description>neutron port</description>
<link-up-down-trap-enable>enabled</link-up-down-trap-enable>
<vhost-user xmlns="urn:opendaylight:params:xml:ns:yang:v3po">
<role>client</role>
<socket>/tmp/socket_4fe335c8-6fdc-4654-b12c-d256e9b39229</socket>
</vhost-user>
<type xmlns:x="urn:opendaylight:params:xml:ns:yang:v3po">x:vhost-user</type>
<enabled>true</enabled>
</interface>
</interfaces>
</config>
</edit-config>
</rpc>
]]>]]>

<rpc message-id="m-12" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<commit/>
</rpc>
]]>]]>

<rpc message-id="m-13" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<unlock>
<target>
<candidate/>
</target>
</unlock>
</rpc>
]]>]]>

<rpc message-id="m-14" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<lock>
<target>
<candidate/>
</target>
</lock>
</rpc>
]]>]]>

<rpc message-id="m-15" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<edit-config>
<target>
<candidate/>
</target>
<default-operation>none</default-operation>
<config>
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
<interface xmlns:a="urn:ietf:params:xml:ns:netconf:base:1.0"
a:operation="replace">
<name>d7611278-88ff-40e1-81e2-602e94e96fc7</name>
<description>neutron port</description>
<link-up-down-trap-enable>enabled</link-up-down-trap-enable>
<vhost-user xmlns="urn:opendaylight:params:xml:ns:yang:v3po">
<role>client</role>
<socket>/tmp/socket_d7611278-88ff-40e1-81e2-602e94e96fc7</socket>
</vhost-user>
<type xmlns:x="urn:opendaylight:params:xml:ns:yang:v3po">x:vhost-user</type>
<enabled>true</enabled>
</interface>
</interfaces>
</config>
</edit-config>
</rpc>
]]>]]>

<rpc message-id="m-16" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<commit/>
</rpc>
]]>]]>

<rpc message-id="m-17" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<unlock>
<target>
<candidate/>
</target>
</unlock>
</rpc>
]]>]]>

<rpc message-id="m-18" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<lock>
<target>
<candidate/>
</target>
</lock>
</rpc>
]]>]]>

<rpc message-id="m-19" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<edit-config>
<target>
<candidate/>
</target>
<default-operation>none</default-operation>
<config>
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
<interface xmlns:a="urn:ietf:params:xml:ns:netconf:base:1.0"
a:operation="replace">
<name>1f96a665-4351-4984-b1a8-dc6f54683123</name>
<description>neutron port</description>
<link-up-down-trap-enable>enabled</link-up-down-trap-enable>
<vhost-user xmlns="urn:opendaylight:params:xml:ns:yang:v3po">
<role>client</role>
<socket>/tmp/socket_1f96a665-4351-4984-b1a8-dc6f54683123</socket>
</vhost-user>
<type xmlns:x="urn:opendaylight:params:xml:ns:yang:v3po">x:vhost-user</type>
<enabled>true</enabled>
</interface>
</interfaces>
</config>
</edit-config>
</rpc>
]]>]]>

<rpc message-id="m-20" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<commit/>
</rpc>
]]>]]>

<rpc message-id="m-21" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<unlock>
<target>
<candidate/>
</target>
</unlock>
</rpc>
]]>]]>

<rpc message-id="m-22" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<lock>
<target>
<candidate/>
</target>
</lock>
</rpc>
]]>]]>

<rpc message-id="m-23" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<edit-config>
<target>
<candidate/>
</target>
<default-operation>none</default-operation>
<config>
<vpp xmlns="urn:opendaylight:params:xml:ns:yang:v3po">
<bridge-domains>
<bridge-domain xmlns:a="urn:ietf:params:xml:ns:netconf:base:1.0"
a:operation="replace">
<name>e86740a2-042c-4e64-a43b-cc224e0d5240</name>
<unknown-unicast-flood>true</unknown-unicast-flood>
<forward>true</forward>
<learn>true</learn>
<flood>true</flood>
<arp-termination>false</arp-termination>
</bridge-domain>
</bridge-domains>
</vpp>
</config>
</edit-config>
</rpc>
]]>]]>

<rpc message-id="m-24" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<commit/>
</rpc>
]]>]]>

<rpc message-id="m-25" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<unlock>
<target>
<candidate/>
</target>
</unlock>
</rpc>
]]>]]>

<rpc message-id="m-26" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<lock>
<target>
<candidate/>
</target>
</lock>
</rpc>
]]>]]>

<rpc message-id="m-27" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<get>
<filter xmlns:ns0="urn:ietf:params:xml:ns:netconf:base:1.0" ns0:type="subtree">
<interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
</filter>
</get>
</rpc>
]]>]]>"""

# Test data for issue: https://jira.fd.io/browse/HONEYCOMB-255
# Reverting transaction fails with "missing writer"
trigger_revert1 = u"""
<rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<edit-config>
<target>
<candidate/>
</target>
<config>
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
<interface>
<name>vxlan3</name>
<type xmlns:v3po="urn:opendaylight:params:xml:ns:yang:v3po">
    v3po:vxlan-tunnel</type>
<enabled>true</enabled>
<vxlan xmlns="urn:opendaylight:params:xml:ns:yang:v3po">
<src>192.168.1.6</src>
<dst>192.168.1.7</dst>
<vni>9</vni>
<encap-vrf-id>0</encap-vrf-id>
</vxlan>
</interface>
</interfaces>
</config>
</edit-config>
</rpc>
]]>]]>

<rpc message-id="102" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<edit-config>
<target>
<candidate/>
</target>
<config>
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
<interface>
<name>vxlan4</name>
<type xmlns:v3po="urn:opendaylight:params:xml:ns:yang:v3po">
    v3po:vxlan-tunnel</type>
<enabled>true</enabled>
<vxlan xmlns="urn:opendaylight:params:xml:ns:yang:v3po">
<src>192.168.1.6</src>
<dst>192.168.1.7</dst>
<vni>9</vni>
<encap-vrf-id>0</encap-vrf-id>
</vxlan>
</interface>
</interfaces>
</config>
</edit-config>
</rpc>
]]>]]>

 <rpc message-id="103"
      xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
   <commit/>
 </rpc>
 ]]>]]>"""

# Test data for issue: https://jira.fd.io/browse/HONEYCOMB-255, part 2
# Reverting transaction fails with "transaction has been closed"
trigger_revert2 = u"""
<rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<edit-config>
<target>
<candidate/>
</target>
<config>
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
<interface>
<name>tap</name>
<type xmlns:v3po="urn:opendaylight:params:xml:ns:yang:v3po">v3po:tap</type>
<enabled>true</enabled>
<tap xmlns="urn:opendaylight:params:xml:ns:yang:v3po">
<tap-name>tap</tap-name>
</tap>
</interface>
</interfaces>
</config>
</edit-config>
</rpc>
]]>]]>

<rpc message-id="102" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<edit-config>
<target>
<candidate/>
</target>
<config>
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
<interface>
<name>tap2</name>
<type xmlns:v3po="urn:opendaylight:params:xml:ns:yang:v3po">v3po:tap</type>
<enabled>true</enabled>
<tap xmlns="urn:opendaylight:params:xml:ns:yang:v3po">
<tap-name>tap</tap-name>
</tap>
</interface>
</interfaces>
</config>
</edit-config>
</rpc>
]]>]]>

<rpc message-id="103" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<commit/>
</rpc>
]]>]]>"""


# Test data for issue HC2VPP-60
# Creating Vlan sub-interface over netconf fails due to ODL bug
trigger_vlan = u"""
<rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<edit-config>
<target>
<candidate/>
</target>
<config>
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
<interface>
<name>{interface}</name>
<sub-interfaces xmlns="urn:opendaylight:params:xml:ns:yang:vpp:vlan"/>
</interface>
</interfaces>
</config>
</edit-config>
</rpc>
]]>]]>

<rpc message-id="102" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<edit-config>
<target>
<candidate/>
</target>
<config>
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
<interface>
<name>{interface}</name>
<sub-interfaces xmlns="urn:opendaylight:params:xml:ns:yang:vpp:vlan">
<sub-interface>
<identifier>2420</identifier>
</sub-interface>
</sub-interfaces>
</interface>
</interfaces>
</config>
</edit-config>
</rpc>
]]>]]>

<rpc message-id="103" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<edit-config>
<target>
<candidate/>
</target>
<default-operation>none</default-operation>
<config>
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
<interface>
<name>{interface}</name>
<sub-interfaces xmlns="urn:opendaylight:params:xml:ns:yang:vpp:vlan">
<sub-interface xmlns:a="urn:ietf:params:xml:ns:netconf:base:1.0" a:operation="replace">
<identifier>2420</identifier>
<match>
<vlan-tagged>
<match-exact-tags>true</match-exact-tags>
</vlan-tagged>
</match>
<vlan-type>802dot1q</vlan-type>
<enabled>false</enabled>
<tags>
<tag>
<index>0</index>
<dot1q-tag>
<tag-type xmlns:x="urn:ieee:params:xml:ns:yang:dot1q-types">x:s-vlan</tag-type>
<vlan-id>2420</vlan-id>
</dot1q-tag>
</tag>
</tags>
</sub-interface>
</sub-interfaces>
</interface>
</interfaces>
</config>
</edit-config>
</rpc>
]]>]]>

<rpc message-id="104" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<commit/>
</rpc>
]]>]]>
"""