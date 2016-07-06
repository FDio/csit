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

# Creating and removing interfaces may result in duplicated interface indices.
trigger_105 = u"""
<rpc message-id="m-27" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
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

<rpc message-id="m-72" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<lock>
<target>
<candidate/>
</target>
</lock>
</rpc>
]]>]]>

<rpc message-id="m-38" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
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

<rpc message-id="m-80" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<commit/>
</rpc>
]]>]]>

<rpc message-id="m-74" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<unlock>
<target>
<candidate/>
</target>
</unlock>
</rpc>
]]>]]>

<rpc message-id="m-72" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<lock>
<target>
<candidate/>
</target>
</lock>
</rpc>
]]>]]>

<rpc message-id="m-43" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
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

<rpc message-id="m-80" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<commit/>
</rpc>
]]>]]>

<rpc message-id="m-74" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<unlock>
<target>
<candidate/>
</target>
</unlock>
</rpc>
]]>]]>

<rpc message-id="m-72" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<lock>
<target>
<candidate/>
</target>
</lock>
</rpc>
]]>]]>

<rpc message-id="m-50" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
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

<rpc message-id="m-80" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<commit/>
</rpc>
]]>]]>

<rpc message-id="m-74" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<unlock>
<target>
<candidate/>
</target>
</unlock>
</rpc>
]]>]]>

<rpc message-id="m-72" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<lock>
<target>
<candidate/>
</target>
</lock>
</rpc>
]]>]]>

<rpc message-id="m-57" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
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

<rpc message-id="m-80" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<commit/>
</rpc>
]]>]]>

<rpc message-id="m-74" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<unlock>
<target>
<candidate/>
</target>
</unlock>
</rpc>
]]>]]>

<rpc message-id="m-72" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<lock>
<target>
<candidate/>
</target>
</lock>
</rpc>
]]>]]>

<rpc message-id="m-64" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
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

<rpc message-id="m-80" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<commit/>
</rpc>
]]>]]>

<rpc message-id="m-74" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<unlock>
<target>
<candidate/>
</target>
</unlock>
</rpc>
]]>]]>

<rpc message-id="m-72" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<lock>
<target>
<candidate/>
</target>
</lock>
</rpc>
]]>]]>

<rpc message-id="m-72" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
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

<rpc message-id="m-80" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<commit/>
</rpc>
]]>]]>

<rpc message-id="m-74" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<unlock>
<target>
<candidate/>
</target>
</unlock>
</rpc>
]]>]]>

<rpc message-id="m-72" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<lock>
<target>
<candidate/>
</target>
</lock>
</rpc>
]]>]]>

<rpc message-id="m-75" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<get>
<filter xmlns:ns0="urn:ietf:params:xml:ns:netconf:base:1.0" ns0:type="subtree">
<interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
</filter>
</get>
</rpc>
]]>]]>"""
