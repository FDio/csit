Test Environment
================

CSIT functional tests are currently executed in FD.IO VIRL testbed. The physical
VIRL testbed infrastructure consists of three VIRL hosts:

- All hosts are Cisco UCS C240-M4 (2x Intel(R) Xeon(R) CPU E5-2699 v3 @2.30GHz,
  18c, 512GB RAM)

- tb4-virl1:

  - Status: Production
  - OS: Ubuntu 16.04.2
  - STD server version 0.10.32.16
  - UWM server version 0.10.32.16

- tb4-virl2:

  - Status: Production
  - OS: Ubuntu 16.04.2
  - STD server version 0.10.32.16
  - UWM server version 0.10.32.16

- tb4-virl3:

  - Status: Testing
  - OS: Ubuntu 16.04.2
  - STD server version 0.10.32.19
  - UWM server version 0.10.32.19

Whenever a patch is submitted to gerrit for review, parallel VIRL simulations
are started to reduce the time of execution of all functional tests. The number
of parallel VIRL simulations is equal to number of test groups defined by
TEST_GROUPS variable in :file:`csit/bootstrap.sh` file. The VIRL host to run
VIRL simulation is selected based on least load algorithm per VIRL simulation.

Every VIRL simulation uses the same three-node - Traffic Generator (TG node) and
two Systems Under Test (SUT1 and SUT2) - "double-ring" topology. The appropriate
pre-built VPP packages built by Jenkins for the patch under review are then
installed on the two SUTs, along with their :file:`/etc/vpp/startup.conf` file,
in all VIRL simulations.

SUT Configuration - VIRL Guest VM
---------------------------------

Configurations of the SUT VMs is defined in `VIRL topologies directory`_

- List of SUT VM interfaces:::

    <interface id="0" name="GigabitEthernet0/4/0"/>
    <interface id="1" name="GigabitEthernet0/5/0"/>
    <interface id="2" name="GigabitEthernet0/6/0"/>
    <interface id="3" name="GigabitEthernet0/7/0"/>

- Number of 2MB hugepages: 1024

- Maximum number of memory map areas: 20000

- Kernel Shared Memory Max: 2147483648 (vm.nr_hugepages * 2 * 1024 * 1024)

SUT Configuration - VIRL Guest OS Linux
---------------------------------------

In CSIT terminology, the VM operating system for both SUTs that |vpp-release| has
been tested with, is the following:

#. **Ubuntu VIRL image**

   This image implies Ubuntu 16.04.1 LTS, current as of yyyy-mm-dd (that is,
   package versions are those that would have been installed by a
   :command:`apt-get update`, :command:`apt-get upgrade` on that day), produced
   by CSIT disk image build scripts.

   The exact list of installed packages and their versions (including the Linux
   kernel package version) are included in `VIRL ubuntu images lists`_.

   A replica of this VM image can be built by running the :command:`build.sh`
   script in CSIT repository.

#. **CentOS VIRL image**

   This image implies Centos 7.4-1711, current as of yyyy-mm-dd (that is,
   package versions are those that would have been installed by a
   :command:`yum update`, :command:`yum upgrade` on that day), produced
   by CSIT disk image build scripts.

   The exact list of installed packages and their versions (including the Linux
   kernel package version) are included in `VIRL centos images lists`_.

   A replica of this VM image can be built by running the :command:`build.sh`
   script in CSIT repository.

#. **Nested VM image**

   In addition to the "main" VM image, tests which require VPP to communicate to
   a VM over a vhost-user interface, utilize a "nested" VM image.

   This "nested" VM is dynamically created and destroyed as part of a test case,
   and therefore the "nested" VM image is optimized to be small, lightweight and
   have a short boot time. The "nested" VM image is not built around any
   established Linux distribution, but is based on `BuildRoot
   <https://buildroot.org/>`_, a tool for building embedded Linux systems. Just
   as for the "main" image, scripts to produce an identical replica of the
   "nested" image are included in CSIT GIT repository, and the image can be
   rebuilt using the "build.sh" script at `VIRL nested`_.

DUT Configuration - VPP
-----------------------

Every System Under Test runs VPP SW application in Linux user-mode as a Device
Under Test (DUT) node.

**DUT port configuration**

Port configuration of DUTs is defined in topology file that is generated per
VIRL simulation based on the definition stored in `VIRL topologies directory`_.

Example of DUT nodes configuration:::

    DUT1:
        type: DUT
        host: "10.30.51.157"
        port: 22
        username: cisco
        honeycomb:
          user: admin
          passwd: admin
          port: 8183
          netconf_port: 2831
        priv_key: |
          -----BEGIN RSA PRIVATE KEY-----
          MIIEpgIBAAKCAQEAwUDlTpzSHpwLQotZOFS4AgcPNEWCnP1AB2hWFmvI+8Kah/gb
          v8ruZU9RqhPs56tyKzxbhvNkY4VbH5F1GilHZu3mLqzM4KfghMmaeMEjO1T7BYYd
          vuBfTvIluljfQ2vAlnYrDwn+ClxJk81m0pDgvrLEX4qVVh2sGh7UEkYy5r82DNa2
          4VjzPB1J/c8a9zP8FoZUhYIzF4FLvRMjUADpbMXgJMsGpaZLmz95ap0Eot7vb1Cc
          1LvF97iyBCrtIOSKRKA50ZhLGjMKmOwnYU+cP5718tbproDVi6VJOo7zeuXyetMs
          8YBl9kWblWG9BqP9jctFvsmi5G7hXgq1Y8u+DwIDAQABAoIBAQC/W4E0DHjLMny7
          0bvw2YKzD0Zw3fttdB94tkm4PdZv5MybooPnsAvLaXVV0hEdfVi5kzSWNl/LY/tN
          EP1BgGphc2QgB59/PPxGwFIjDCvUzlsZpynBHe+B/qh5ExNQcVvsIOqWI7DXlXaN
          0i/khOzmJ6HncRRah1spKimYRsaUUDskyg7q3QqMWVaqBbbMvLs/w7ZWd/zoDqCU
          MY/pCI6hkB3QbRo0OdiZLohphBl2ShABTwjvVyyKL5UA4jAEneJrhH5gWVLXnfgD
          p62W5CollKEYblC8mUkPxpP7Qo277zw3xaq+oktIZhc5SUEUd7nJZtNqVAHqkItW
          79VmpKyxAoGBAPfU+kqNPaTSvp+x1n5sn2SgipzDtgi9QqNmC4cjtrQQaaqI57SG
          OHw1jX8i7L2G1WvVtkHg060nlEVo5n65ffFOqeVBezLVJ7ghWI8U+oBiJJyQ4boD
          GJVNsoOSUQ0rtuGd9eVwfDk3ol9aCN0KK53oPfIYli29pyu4l095kg11AoGBAMef
          bPEMBI/2XmCPshLSwhGFl+dW8d+Klluj3CUQ/0vUlvma3dfBOYNsIwAgTP0iIUTg
          8DYE6KBCdPtxAUEI0YAEAKB9ry1tKR2NQEIPfslYytKErtwjAiqSi0heM6+zwEzu
          f54Z4oBhsMSL0jXoOMnu+NZzEc6EUdQeY4O+jhjzAoGBAIogC3dtjMPGKTP7+93u
          UE/XIioI8fWg9fj3sMka4IMu+pVvRCRbAjRH7JrFLkjbUyuMqs3Arnk9K+gbdQt/
          +m95Njtt6WoFXuPCwgbM3GidSmZwYT4454SfDzVBYScEDCNm1FuR+8ov9bFLDtGT
          D4gsngnGJj1MDFXTxZEn4nzZAoGBAKCg4WmpUPaCuXibyB+rZavxwsTNSn2lJ83/
          sYJGBhf/raiV/FLDUcM1vYg5dZnu37RsB/5/vqxOLZGyYd7x+Jo5HkQGPnKgNwhn
          g8BkdZIRF8uEJqxOo0ycdOU7n/2O93swIpKWo5LIiRPuqqzj+uZKnAL7vuVdxfaY
          qVz2daMPAoGBALgaaKa3voU/HO1PYLWIhFrBThyJ+BQSQ8OqrEzC8AnegWFxRAM8
          EqrzZXl7ACUuo1dH0Eipm41j2+BZWlQjiUgq5uj8+yzy+EU1ZRRyJcOKzbDACeuD
          BpWWSXGBI5G4CppeYLjMUHZpJYeX1USULJQd2c4crLJKb76E8gz3Z9kN
          -----END RSA PRIVATE KEY-----

        interfaces:
          port1:
            mac_address: "fa:16:3e:9b:89:52"
            pci_address: "0000:00:04.0"
            link: link1
          port2:
            mac_address: "fa:16:3e:7a:33:60"
            pci_address: "0000:00:05.0"
            link: link4
          port3:
            mac_address: "fa:16:3e:29:b7:ae"
            pci_address: "0000:00:06.0"
            link: link3
          port4:
            mac_address: "fa:16:3e:76:8d:ff"
            pci_address: "0000:00:07.0"
            link: link6
      DUT2:
        type: DUT
        host: "10.30.51.156"
        port: 22
        username: cisco
        honeycomb:
          user: admin
          passwd: admin
          port: 8183
          netconf_port: 2831
        priv_key: |
          -----BEGIN RSA PRIVATE KEY-----
          MIIEpgIBAAKCAQEAwUDlTpzSHpwLQotZOFS4AgcPNEWCnP1AB2hWFmvI+8Kah/gb
          v8ruZU9RqhPs56tyKzxbhvNkY4VbH5F1GilHZu3mLqzM4KfghMmaeMEjO1T7BYYd
          vuBfTvIluljfQ2vAlnYrDwn+ClxJk81m0pDgvrLEX4qVVh2sGh7UEkYy5r82DNa2
          4VjzPB1J/c8a9zP8FoZUhYIzF4FLvRMjUADpbMXgJMsGpaZLmz95ap0Eot7vb1Cc
          1LvF97iyBCrtIOSKRKA50ZhLGjMKmOwnYU+cP5718tbproDVi6VJOo7zeuXyetMs
          8YBl9kWblWG9BqP9jctFvsmi5G7hXgq1Y8u+DwIDAQABAoIBAQC/W4E0DHjLMny7
          0bvw2YKzD0Zw3fttdB94tkm4PdZv5MybooPnsAvLaXVV0hEdfVi5kzSWNl/LY/tN
          EP1BgGphc2QgB59/PPxGwFIjDCvUzlsZpynBHe+B/qh5ExNQcVvsIOqWI7DXlXaN
          0i/khOzmJ6HncRRah1spKimYRsaUUDskyg7q3QqMWVaqBbbMvLs/w7ZWd/zoDqCU
          MY/pCI6hkB3QbRo0OdiZLohphBl2ShABTwjvVyyKL5UA4jAEneJrhH5gWVLXnfgD
          p62W5CollKEYblC8mUkPxpP7Qo277zw3xaq+oktIZhc5SUEUd7nJZtNqVAHqkItW
          79VmpKyxAoGBAPfU+kqNPaTSvp+x1n5sn2SgipzDtgi9QqNmC4cjtrQQaaqI57SG
          OHw1jX8i7L2G1WvVtkHg060nlEVo5n65ffFOqeVBezLVJ7ghWI8U+oBiJJyQ4boD
          GJVNsoOSUQ0rtuGd9eVwfDk3ol9aCN0KK53oPfIYli29pyu4l095kg11AoGBAMef
          bPEMBI/2XmCPshLSwhGFl+dW8d+Klluj3CUQ/0vUlvma3dfBOYNsIwAgTP0iIUTg
          8DYE6KBCdPtxAUEI0YAEAKB9ry1tKR2NQEIPfslYytKErtwjAiqSi0heM6+zwEzu
          f54Z4oBhsMSL0jXoOMnu+NZzEc6EUdQeY4O+jhjzAoGBAIogC3dtjMPGKTP7+93u
          UE/XIioI8fWg9fj3sMka4IMu+pVvRCRbAjRH7JrFLkjbUyuMqs3Arnk9K+gbdQt/
          +m95Njtt6WoFXuPCwgbM3GidSmZwYT4454SfDzVBYScEDCNm1FuR+8ov9bFLDtGT
          D4gsngnGJj1MDFXTxZEn4nzZAoGBAKCg4WmpUPaCuXibyB+rZavxwsTNSn2lJ83/
          sYJGBhf/raiV/FLDUcM1vYg5dZnu37RsB/5/vqxOLZGyYd7x+Jo5HkQGPnKgNwhn
          g8BkdZIRF8uEJqxOo0ycdOU7n/2O93swIpKWo5LIiRPuqqzj+uZKnAL7vuVdxfaY
          qVz2daMPAoGBALgaaKa3voU/HO1PYLWIhFrBThyJ+BQSQ8OqrEzC8AnegWFxRAM8
          EqrzZXl7ACUuo1dH0Eipm41j2+BZWlQjiUgq5uj8+yzy+EU1ZRRyJcOKzbDACeuD
          BpWWSXGBI5G4CppeYLjMUHZpJYeX1USULJQd2c4crLJKb76E8gz3Z9kN
          -----END RSA PRIVATE KEY-----

        interfaces:
          port1:
            mac_address: "fa:16:3e:ad:6c:7d"
            pci_address: "0000:00:04.0"
            link: link2
          port2:
            mac_address: "fa:16:3e:94:a4:99"
            pci_address: "0000:00:05.0"
            link: link5
          port3:
            mac_address: "fa:16:3e:75:92:da"
            pci_address: "0000:00:06.0"
            link: link3
          port4:
            mac_address: "fa:16:3e:2c:b1:2a"
            pci_address: "0000:00:07.0"
            link: link6

**VPP Version**

|vpp-release|

**VPP Installed Packages - Ubuntu**
::

    $ dpkg -l vpp\*
    Desired=Unknown/Install/Remove/Purge/Hold
    | Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
    |/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)
    ||/ Name           Version       Architecture Description
    +++-==============-=============-============-=================================================
    ii  vpp                                 18.07-release                              amd64        Vector Packet Processing--executables
    ii  vpp-dbg                             18.07-release                              amd64        Vector Packet Processing--debug symbols
    ii  vpp-dev                             18.07-release                              amd64        Vector Packet Processing--development support
    ii  vpp-dpdk-dkms                       18.05-vpp2                                 amd64        DPDK Development Package for VPP - Kernel Modules
    ii  vpp-lib                             18.07-release                              amd64        Vector Packet Processing--runtime libraries
    ii  vpp-plugins                         18.07-release                              amd64        Vector Packet Processing--runtime plugins

**VPP Installed Packages - Centos**
::

    $ rpm -qai vpp*
    Name        : vpp
    Version     : 18.07
    Release     : release
    Architecture: x86_64
    Install Date: Tue 31 Jul 2018 02:59:45 AM EDT
    Group       : Unspecified
    Size        : 2396993
    License     : ASL 2.0
    Signature   : (none)
    Source RPM  : vpp-18.07-release.src.rpm
    Build Date  : Mon 30 Jul 2018 08:20:19 PM EDT
    Build Host  : c3de88e7d43c
    Relocations : (not relocatable)
    Summary     : Vector Packet Processing
    Description :
    This package provides VPP executables: vpp, vpp_api_test, vpp_json_test
    vpp - the vector packet engine
    vpp_api_test - vector packet engine API test tool
    vpp_json_test - vector packet engine JSON test tool
    Name        : vpp-lib
    Version     : 18.07
    Release     : release
    Architecture: x86_64
    Install Date: Tue 31 Jul 2018 02:59:45 AM EDT
    Group       : System Environment/Libraries
    Size        : 27134058
    License     : ASL 2.0
    Signature   : (none)
    Source RPM  : vpp-18.07-release.src.rpm
    Build Date  : Mon 30 Jul 2018 08:20:19 PM EDT
    Build Host  : c3de88e7d43c
    Relocations : (not relocatable)
    Summary     : VPP libraries
    Description :
    This package contains the VPP shared libraries, including:
    vppinfra - foundation library supporting vectors, hashes, bitmaps, pools, and string formatting.
    svm - vm library
    vlib - vector processing library
    vlib-api - binary API library
    vnet -  network stack library
    Name        : vpp-selinux-policy
    Version     : 18.07
    Release     : release
    Architecture: x86_64
    Install Date: Tue 31 Jul 2018 02:59:44 AM EDT
    Group       : System Environment/Base
    Size        : 86709
    License     : ASL 2.0
    Signature   : (none)
    Source RPM  : vpp-18.07-release.src.rpm
    Build Date  : Mon 30 Jul 2018 08:20:19 PM EDT
    Build Host  : c3de88e7d43c
    Relocations : (not relocatable)
    Summary     : VPP Security-Enhanced Linux (SELinux) policy
    Description :
    This package contains a tailored VPP SELinux policy
    Name        : vpp-devel
    Version     : 18.07
    Release     : release
    Architecture: x86_64
    Install Date: Tue 31 Jul 2018 02:59:47 AM EDT
    Group       : Development/Libraries
    Size        : 11452203
    License     : ASL 2.0
    Signature   : (none)
    Source RPM  : vpp-18.07-release.src.rpm
    Build Date  : Mon 30 Jul 2018 08:20:19 PM EDT
    Build Host  : c3de88e7d43c
    Relocations : (not relocatable)
    Summary     : VPP header files, static libraries
    Description :
    This package contains the header files for VPP.
    Install this package if you want to write a
    program for compilation and linking with vpp lib.
    vlib
    vlibmemory
    vnet - devices, classify, dhcp, ethernet flow, gre, ip, etc.
    vpp-api
    vppinfra
    Name        : vpp-plugins
    Version     : 18.07
    Release     : release
    Architecture: x86_64
    Install Date: Tue 31 Jul 2018 02:59:47 AM EDT
    Group       : System Environment/Libraries
    Size        : 52282610
    License     : ASL 2.0
    Signature   : (none)
    Source RPM  : vpp-18.07-release.src.rpm
    Build Date  : Mon 30 Jul 2018 08:20:19 PM EDT
    Build Host  : c3de88e7d43c
    Relocations : (not relocatable)
    Summary     : Vector Packet Processing--runtime plugins
    Description :
    This package contains VPP plugins

**VPP Startup Configuration**

VPP startup configuration is common for all test cases except test cases related
to SW Crypto device.

**Default**

::

    $ cat /etc/vpp/startup.conf
    unix {
      nodaemon
      log /var/log/vpp/vpp.log
      full-coredump
      cli-listen /run/vpp/cli.sock
      gid vpp
    }

    api-trace {
    ## This stanza controls binary API tracing. Unless there is a very strong reason,
    ## please leave this feature enabled.
      on
    ## Additional parameters:
    ##
    ## To set the number of binary API trace records in the circular buffer, configure nitems
    ##
    ## nitems <nnn>
    ##
    ## To save the api message table decode tables, configure a filename. Results in /tmp/<filename>
    ## Very handy for understanding api message changes between versions, identifying missing
    ## plugins, and so forth.
    ##
    ## save-api-table <filename>
    }

    api-segment {
      gid vpp
    }

    socksvr {
      default
    }

    cpu {
        ## In the VPP there is one main thread and optionally the user can create worker(s)
        ## The main thread and worker thread(s) can be pinned to CPU core(s) manually or automatically

        ## Manual pinning of thread(s) to CPU core(s)

        ## Set logical CPU core where main thread runs, if main core is not set
        ## VPP will use core 1 if available
        # main-core 1

        ## Set logical CPU core(s) where worker threads are running
        # corelist-workers 2-3,18-19

        ## Automatic pinning of thread(s) to CPU core(s)

        ## Sets number of CPU core(s) to be skipped (1 ... N-1)
        ## Skipped CPU core(s) are not used for pinning main thread and working thread(s).
        ## The main thread is automatically pinned to the first available CPU core and worker(s)
        ## are pinned to next free CPU core(s) after core assigned to main thread
        # skip-cores 4

        ## Specify a number of workers to be created
        ## Workers are pinned to N consecutive CPU cores while skipping "skip-cores" CPU core(s)
        ## and main thread's CPU core
        # workers 2

        ## Set scheduling policy and priority of main and worker threads

        ## Scheduling policy options are: other (SCHED_OTHER), batch (SCHED_BATCH)
        ## idle (SCHED_IDLE), fifo (SCHED_FIFO), rr (SCHED_RR)
        # scheduler-policy fifo

        ## Scheduling priority is used only for "real-time policies (fifo and rr),
        ## and has to be in the range of priorities supported for a particular policy
        # scheduler-priority 50
    }

    # dpdk {
        ## Change default settings for all intefaces
        # dev default {
            ## Number of receive queues, enables RSS
            ## Default is 1
            # num-rx-queues 3

            ## Number of transmit queues, Default is equal
            ## to number of worker threads or 1 if no workers treads
            # num-tx-queues 3

            ## Number of descriptors in transmit and receive rings
            ## increasing or reducing number can impact performance
            ## Default is 1024 for both rx and tx
            # num-rx-desc 512
            # num-tx-desc 512

            ## VLAN strip offload mode for interface
            ## Default is off
            # vlan-strip-offload on
        # }

        ## Whitelist specific interface by specifying PCI address
        # dev 0000:02:00.0

        ## Whitelist specific interface by specifying PCI address and in
        ## addition specify custom parameters for this interface
        # dev 0000:02:00.1 {
        #	num-rx-queues 2
        # }

        ## Specify bonded interface and its slaves via PCI addresses
        ##
        ## Bonded interface in XOR load balance mode (mode 2) with L3 and L4 headers
        # vdev eth_bond0,mode=2,slave=0000:02:00.0,slave=0000:03:00.0,xmit_policy=l34
        # vdev eth_bond1,mode=2,slave=0000:02:00.1,slave=0000:03:00.1,xmit_policy=l34
        ##
        ## Bonded interface in Active-Back up mode (mode 1)
        # vdev eth_bond0,mode=1,slave=0000:02:00.0,slave=0000:03:00.0
        # vdev eth_bond1,mode=1,slave=0000:02:00.1,slave=0000:03:00.1

        ## Change UIO driver used by VPP, Options are: igb_uio, vfio-pci,
        ## uio_pci_generic or auto (default)
        # uio-driver vfio-pci

        ## Disable mutli-segment buffers, improves performance but
        ## disables Jumbo MTU support
        # no-multi-seg

        ## Increase number of buffers allocated, needed only in scenarios with
        ## large number of interfaces and worker threads. Value is per CPU socket.
        ## Default is 16384
        # num-mbufs 128000

        ## Change hugepages allocation per-socket, needed only if there is need for
        ## larger number of mbufs. Default is 256M on each detected CPU socket
        # socket-mem 2048,2048

        ## Disables UDP / TCP TX checksum offload. Typically needed for use
        ## faster vector PMDs (together with no-multi-seg)
        # no-tx-checksum-offload
    # }


    # plugins {
        ## Adjusting the plugin path depending on where the VPP plugins are
        #	path /home/bms/vpp/build-root/install-vpp-native/vpp/lib64/vpp_plugins

        ## Disable all plugins by default and then selectively enable specific plugins
        # plugin default { disable }
        # plugin dpdk_plugin.so { enable }
        # plugin acl_plugin.so { enable }

        ## Enable all plugins by default and then selectively disable specific plugins
        # plugin dpdk_plugin.so { disable }
        # plugin acl_plugin.so { disable }
    # }

        ## Alternate syntax to choose plugin path
        # plugin_path /home/bms/vpp/build-root/install-vpp-native/vpp/lib64/vpp_plugins

**SW Crypto Device**

::

    $ cat /etc/vpp/startup.conf
    unix
    {
      cli-listen /run/vpp/cli.sock
      gid vpp
      nodaemon
      full-coredump
      log /tmp/vpp.log
    }
    api-segment
    {
      gid vpp
    }
    dpdk
    {
      vdev cryptodev_aesni_gcm_pmd,socket_id=0
      vdev cryptodev_aesni_mb_pmd,socket_id=0
    }

TG Configuration
----------------

Traffic Generator node is VM running the same OS Linux as SUTs. Ports of this
VM are used as source (Tx) and destination (Rx) ports for the traffic.

Traffic scripts of test cases are executed on this VM.

**TG VM configuration**

Configuration of the TG VMs is defined in `VIRL topologies directory`_.

   /csit/resources/tools/virl/topologies/double-ring-nested.xenial.virl

- List of TG VM interfaces:::

    <interface id="0" name="eth1"/>
    <interface id="1" name="eth2"/>
    <interface id="2" name="eth3"/>
    <interface id="3" name="eth4"/>
    <interface id="4" name="eth5"/>
    <interface id="5" name="eth6"/>

**TG node port configuration**

Port configuration of TG is defined in topology file that is generated per VIRL
simulation based on the definition stored in `VIRL topologies directory`_.

Example of TG node configuration:::

    TG:
        type: TG
        host: "10.30.51.155"
        port: 22
        username: cisco
        priv_key: |
          -----BEGIN RSA PRIVATE KEY-----
          MIIEpgIBAAKCAQEAwUDlTpzSHpwLQotZOFS4AgcPNEWCnP1AB2hWFmvI+8Kah/gb
          v8ruZU9RqhPs56tyKzxbhvNkY4VbH5F1GilHZu3mLqzM4KfghMmaeMEjO1T7BYYd
          vuBfTvIluljfQ2vAlnYrDwn+ClxJk81m0pDgvrLEX4qVVh2sGh7UEkYy5r82DNa2
          4VjzPB1J/c8a9zP8FoZUhYIzF4FLvRMjUADpbMXgJMsGpaZLmz95ap0Eot7vb1Cc
          1LvF97iyBCrtIOSKRKA50ZhLGjMKmOwnYU+cP5718tbproDVi6VJOo7zeuXyetMs
          8YBl9kWblWG9BqP9jctFvsmi5G7hXgq1Y8u+DwIDAQABAoIBAQC/W4E0DHjLMny7
          0bvw2YKzD0Zw3fttdB94tkm4PdZv5MybooPnsAvLaXVV0hEdfVi5kzSWNl/LY/tN
          EP1BgGphc2QgB59/PPxGwFIjDCvUzlsZpynBHe+B/qh5ExNQcVvsIOqWI7DXlXaN
          0i/khOzmJ6HncRRah1spKimYRsaUUDskyg7q3QqMWVaqBbbMvLs/w7ZWd/zoDqCU
          MY/pCI6hkB3QbRo0OdiZLohphBl2ShABTwjvVyyKL5UA4jAEneJrhH5gWVLXnfgD
          p62W5CollKEYblC8mUkPxpP7Qo277zw3xaq+oktIZhc5SUEUd7nJZtNqVAHqkItW
          79VmpKyxAoGBAPfU+kqNPaTSvp+x1n5sn2SgipzDtgi9QqNmC4cjtrQQaaqI57SG
          OHw1jX8i7L2G1WvVtkHg060nlEVo5n65ffFOqeVBezLVJ7ghWI8U+oBiJJyQ4boD
          GJVNsoOSUQ0rtuGd9eVwfDk3ol9aCN0KK53oPfIYli29pyu4l095kg11AoGBAMef
          bPEMBI/2XmCPshLSwhGFl+dW8d+Klluj3CUQ/0vUlvma3dfBOYNsIwAgTP0iIUTg
          8DYE6KBCdPtxAUEI0YAEAKB9ry1tKR2NQEIPfslYytKErtwjAiqSi0heM6+zwEzu
          f54Z4oBhsMSL0jXoOMnu+NZzEc6EUdQeY4O+jhjzAoGBAIogC3dtjMPGKTP7+93u
          UE/XIioI8fWg9fj3sMka4IMu+pVvRCRbAjRH7JrFLkjbUyuMqs3Arnk9K+gbdQt/
          +m95Njtt6WoFXuPCwgbM3GidSmZwYT4454SfDzVBYScEDCNm1FuR+8ov9bFLDtGT
          D4gsngnGJj1MDFXTxZEn4nzZAoGBAKCg4WmpUPaCuXibyB+rZavxwsTNSn2lJ83/
          sYJGBhf/raiV/FLDUcM1vYg5dZnu37RsB/5/vqxOLZGyYd7x+Jo5HkQGPnKgNwhn
          g8BkdZIRF8uEJqxOo0ycdOU7n/2O93swIpKWo5LIiRPuqqzj+uZKnAL7vuVdxfaY
          qVz2daMPAoGBALgaaKa3voU/HO1PYLWIhFrBThyJ+BQSQ8OqrEzC8AnegWFxRAM8
          EqrzZXl7ACUuo1dH0Eipm41j2+BZWlQjiUgq5uj8+yzy+EU1ZRRyJcOKzbDACeuD
          BpWWSXGBI5G4CppeYLjMUHZpJYeX1USULJQd2c4crLJKb76E8gz3Z9kN
          -----END RSA PRIVATE KEY-----

        interfaces:
          port3:
            mac_address: "fa:16:3e:b9:e1:27"
            pci_address: "0000:00:06.0"
            link: link1
            driver: virtio-pci
          port4:
            mac_address: "fa:16:3e:e9:c8:68"
            pci_address: "0000:00:07.0"
            link: link4
            driver: virtio-pci
          port5:
            mac_address: "fa:16:3e:e8:d3:47"
            pci_address: "0000:00:08.0"
            link: link2
            driver: virtio-pci
          port6:
            mac_address: "fa:16:3e:cf:ca:58"
            pci_address: "0000:00:09.0"
            link: link5
            driver: virtio-pci

**Traffic generator**

Functional tests utilize Scapy as a traffic generator. There was used Scapy
v2.3.1 for |vpp-release| tests.

