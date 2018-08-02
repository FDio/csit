Overview
========

Virtual Topologies
------------------

CSIT VPP functional tests are executed on virtualized topologies created using
:abbr:`VIRL (Virtual Internet Routing Lab)` simulation platform contributed by
Cisco. VIRL runs on physical baremetal servers hosted by LF FD.io project.
Based on the packet path thru server SUTs, two distinct logical topology types
are used for VPP DUT data plane testing:

#. NIC-to-NIC switching topologies.
#. VM service switching topologies.

NIC-to-NIC Switching
~~~~~~~~~~~~~~~~~~~~

The simplest logical topology for software data plane application like
VPP is NIC-to-NIC switching. Tested topologies for 2-Node and 3-Node
testbeds are shown in figures below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/vpp_performance_tests/logical-2n-nic2nic}
            \label{fig:logical-2n-nic2nic}
        \end{figure}

.. only:: html

    .. figure:: ../vpp_performance_tests/logical-2n-nic2nic.svg
        :alt: logical-2n-nic2nic
        :align: center


.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/vpp_performance_tests/logical-3n-nic2nic}
            \label{fig:logical-3n-nic2nic}
        \end{figure}

.. only:: html

    .. figure:: ../vpp_performance_tests/logical-3n-nic2nic.svg
        :alt: logical-3n-nic2nic
        :align: center

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

VM Service Switching
~~~~~~~~~~~~~~~~~~~~

VM service switching topology test cases require VPP DUT to communicate
with Virtual Machines (VMs) over vhost-user virtual interfaces. A nested VM is
created on SUT1 and/or SUT2 for the duration of these particular test cases
only. DUT (VPP) test topology with VM is shown in the figure below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/vpp_performance_tests/logical-2n-vm-vhost}
            \label{fig:logical-2n-vm-vhost}
        \end{figure}

.. only:: html

    .. figure:: ../vpp_performance_tests/logical-2n-vm-vhost.svg
        :alt: logical-2n-vm-vhost
        :align: center


.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/vpp_performance_tests/logical-3n-vm-vhost}
            \label{fig:logical-3n-vm-vhost}
        \end{figure}

.. only:: html

    .. figure:: ../vpp_performance_tests/logical-3n-vm-vhost.svg
        :alt: logical-3n-vm-vhost
        :align: center

Functional Tests Coverage
-------------------------

Following VPP functional test areas are covered in the |csit-release| with
results listed in this report:

- **DHCP - Client and Proxy** - Dynamic Host Control Protocol Client and Proxy
  for IPv4, IPv6.
- **GRE Overlay Tunnels** - Generic Routing Encapsulation for IPv4.
- **L2BD Ethernet Switching** - L2 Bridge-Domain switched-forwarding for
  untagged Ethernet, dot1q and dot1ad tagged.
- **L2XC Ethernet Switching** - L2 Cross-Connect switched-forwarding for
  untagged Ethernet, dot1q and dot1ad tagged.
- **LISP Overlay Tunnels** - Locator/ID Separation Protocol overlay tunnels and
  locator/id mapping control.
- **Softwire Tunnels** - IPv4-in-IPv6 softwire tunnels.
- **Cop Address Security** - address white-list and black-list filtering for
  IPv4, IPv6.
- **IPSec - Tunnels and Transport** - IPSec tunnel and transport modes.
- **IPv6 Routed-Forwarding** - IPv6 routed-forwarding, NS/ND, RA, ICMPv6.
- **uRPF Source Security** - unicast Reverse Path Forwarding security.
- **Tap Interface** - baseline Linux tap interface tests.
- **Telemetry - IPFIX and SPAN** - IPFIX netflow statistics and SPAN port
  mirroring.
- **VRF Routed-Forwarding** - multi-context IPVPN routed-forwarding for IPv4,
  IPv6.
- **iACL Security** - ingress Access Control List security for IPv4, IPv6, MAC.
- **IPv4 Routed-Forwarding** - IPv4 routed-forwarding, RPF, ARP, Proxy ARP,
  ICMPv4.
- **QoS Policer Metering** - ingress packet rate measuring and marking for IPv4,
  IPv6.
- **VLAN Tag Translation** - L2 VLAN tag translation 2to2, 2to1, 1to2, 1to1.
- **VXLAN Overlay Tunnels** - VXLAN tunneling for L2-over-IP, for IPv4, IPv6.

Functional Tests Naming
-----------------------

|csit-release| follows a common structured naming convention for all performance
and system functional tests, introduced in CSIT-17.01.

The naming should be intuitive for majority of the tests. Complete description
of CSIT test naming convention is provided on :ref:`csit_test_naming`.
