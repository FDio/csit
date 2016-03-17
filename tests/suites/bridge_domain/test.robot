*** Settings ***
Suite Setup       Setup all TGs before traffic script
Test Setup        Setup all DUTs before test
Force Tags        HW_ENV    VM_ENV
Resource          resources/libraries/robot/default.robot
Resource          resources/libraries/robot/interfaces.robot
Resource          resources/libraries/robot/bridge_domain.robot
Resource          resources/libraries/robot/l2_traffic.robot
Library           resources.libraries.python.topology.Topology
Library           resources.libraries.python.NodePath
Variables         resources/libraries/python/topology.py

*** Test Cases ***
VPP reports interfaces
    VPP reports interfaces on    ${nodes['DUT1']}

Vpp forwards packets via L2 bridge domain 2 ports
    [Tags]    3_NODE_DOUBLE_LINK_TOPO
    Append Nodes    ${nodes['TG']}    ${nodes['DUT1']}    ${nodes['TG']}
    Compute Path    always_same_link=${FALSE}
    ${tg_if1}    ${tmp}=    First Interface
    ${tg_if2}    ${tmp}=    Last Interface
    ${bd_if1}    ${tmp}=    First Ingress Interface
    ${bd_if2}    ${tmp}=    Last Egress Interface
    Vpp l2bd forwarding setup    ${nodes['DUT1']}    ${bd_if1}    ${bd_if2}
    Send and receive ICMPv4    ${nodes['TG']}    ${tg_if1}    ${tg_if2}
    Send and receive ICMPv4    ${nodes['TG']}    ${tg_if2}    ${tg_if1}

Vpp forwards packets via L2 bridge domain in circular topology
    [Tags]    3_NODE_SINGLE_LINK_TOPO
    Append Nodes    ${nodes['TG']}    ${nodes['DUT1']}    ${nodes['DUT2']}    ${nodes['TG']}
    Compute Path
    ${tg_if1}    ${tg}=    Next Interface
    ${dut1_if1}    ${dut1}=    Next Interface
    ${dut1_if2}    ${dut1}=    Next Interface
    ${dut2_if1}    ${dut2}=    Next Interface
    ${dut2_if2}    ${dut2}=    Next Interface
    ${tg_if2}    ${tg}=    Next Interface
    Vpp l2bd forwarding setup    ${dut1}    ${dut1_if1}    ${dut1_if2}
    Vpp l2bd forwarding setup    ${dut2}    ${dut2_if1}    ${dut2_if2}
    Send and receive ICMPv4    ${tg}    ${tg_if1}    ${tg_if2}
    Send and receive ICMPv4    ${tg}    ${tg_if2}    ${tg_if1}

Vpp forwards packets via L2 bridge domain in circular topology with static L2FIB entries
    [Tags]    3_NODE_SINGLE_LINK_TOPO
    Append Nodes    ${nodes['TG']}    ${nodes['DUT1']}    ${nodes['DUT2']}    ${nodes['TG']}
    Compute Path
    ${tg_if1}    ${tg}=    Next Interface
    ${dut1_if1}    ${dut1}=    Next Interface
    ${dut1_if2}    ${dut1}=    Next Interface
    ${dut2_if1}    ${dut2}=    Next Interface
    ${dut2_if2}    ${dut2}=    Next Interface
    ${tg_if2}    ${tg}=    Next Interface
    ${mac}=    Get Interface Mac    ${tg}    ${tg_if2}
    Vpp l2bd forwarding setup    ${dut1}    ${dut1_if1}    ${dut1_if2}    ${FALSE}    ${mac}
    Vpp l2bd forwarding setup    ${dut2}    ${dut2_if1}    ${dut2_if2}    ${FALSE}    ${mac}
    Send and receive ICMPv4    ${tg}    ${tg_if1}    ${tg_if2}
    Send and receive ICMPv4    ${tg}    ${tg_if2}    ${tg_if1}

Sends 1 packet via L2 BD in circular topology to modify L2FIB table and verify the table
    [Tags]    3_NODE_SINGLE_LINK_TOPO
    Append Nodes    ${nodes['TG']}    ${nodes['DUT1']}    ${nodes['TG']}
    Compute Path
    ${tg_if1}    ${tg}=    Next Interface
    ${dut1_if1}    ${dut1}=    Next Interface
    ${dut1_if2}    ${dut1}=    Next Interface
    ${tg_if2}    ${tg}=    Next Interface
    Vpp l2bd forwarding setup    ${dut1}    ${dut1_if1}    ${dut1_if2}
    Vpp clear l2fib table    ${dut1}
    Fill l2fib table    ${tg}    ${tg_if1}    ${tg_if2}    1
    ${bridge_ip}    Vpp dump bridge domain    ${dut1}
    Vpp verify l2fib table    ${dut1}    ${bridge_ip}    1

Sends 65536 packet via L2 BD in circular topology to modify L2FIB table and verify the table
    [Tags]    3_NODE_SINGLE_LINK_TOPO
    Append Nodes    ${nodes['TG']}    ${nodes['DUT1']}    ${nodes['TG']}
    Compute Path
    ${tg_if1}    ${tg}=    Next Interface
    ${dut1_if1}    ${dut1}=    Next Interface
    ${dut1_if2}    ${dut1}=    Next Interface
    ${tg_if2}    ${tg}=    Next Interface
    Vpp l2bd forwarding setup    ${dut1}    ${dut1_if1}    ${dut1_if2}
    Vpp clear l2fib table    ${dut1}
    Fill l2fib table    ${tg}    ${tg_if1}    ${tg_if2}    65536
    ${bridge_ip}    Vpp dump bridge domain    ${dut1}
    Vpp verify l2fib table    ${dut1}    ${bridge_ip}    65536

Sends 65537 packet via L2 BD in circular topology to modify L2FIB table and verify the table
    [Tags]    3_NODE_SINGLE_LINK_TOPO
    Append Nodes    ${nodes['TG']}    ${nodes['DUT1']}    ${nodes['TG']}
    Compute Path
    ${tg_if1}    ${tg}=    Next Interface
    ${dut1_if1}    ${dut1}=    Next Interface
    ${dut1_if2}    ${dut1}=    Next Interface
    ${tg_if2}    ${tg}=    Next Interface
    Vpp l2bd forwarding setup    ${dut1}    ${dut1_if1}    ${dut1_if2}
    Vpp clear l2fib table    ${dut1}
    Fill l2fib table    ${tg}    ${tg_if1}    ${tg_if2}    65537
    ${bridge_ip}    Vpp dump bridge domain    ${dut1}
    Vpp verify l2fib table    ${dut1}    ${bridge_ip}    65536
