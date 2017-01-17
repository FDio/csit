Test Environment
================

To execute performance tests, there are three identical testbeds, each testbed
consists of two SUTs and one TG.

Hardware details (CPU, memory, NIC layout) are described in
[[CSIT/CSIT_LF_testbed]]; in summary:

- All hosts are Cisco UCS C240-M4 (2x Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz,
  18c, 512GB RAM),
- BIOS settings are default except for the following:

  - Hyperthreading disabled,
  - SpeedStep disabled
  - TurboBoost disabled
  - Power Technology: Performance

- Hosts run Ubuntu 14.04.3, kernel 4.2.0-36-generic
- Linux kernel boot command line option "intel_pstate=disable" is applied to
  both SUTs and TG. In addition, on SUTs, only cores 0 and 18 (the first core on
  each socket) are available to the Linux operating system and generic tasks,
  all other CPU cores are isolated and reserved for VPP.
- In addition to CIMC and Management, each TG has 4x Intel X710 10GB NIC
  (=8 ports) and 2x Intel XL710 40GB NIC (=4 ports), whereas each SUT has:

  - 1x Intel X520 NIC (10GB, 2 ports),
  - 1x Cisco VIC 1385 (40GB, 2 ports),
  - 1x Intel XL710 NIC (40GB, 2 ports),
  - 1x Intel X710 NIC (10GB, 2 ports),
  - 1x Cisco VIC 1227 (10GB, 2 ports).
  - This allows for a total of five ring topologies, each using ports on
    specific NIC model, enabling per NIC model benchmarking.

Config: VPP (DUT)
-----------------

**NIC types**

- 0a:00.0 Ethernet controller: Intel Corporation 82599ES 10-Gigabit SFI/SFP+
  Network Connection (rev 01) Subsystem: Intel Corporation Ethernet Server
  Adapter X520-2
- 0a:00.1 Ethernet controller: Intel Corporation 82599ES 10-Gigabit SFI/SFP+
  Network Connection (rev 01) Subsystem: Intel Corporation Ethernet Server
  Adapter X520-2
- 85:00.0 Ethernet controller: Intel Corporation Ethernet Controller XL710
  for 40GbE QSFP+ (rev 01) Subsystem: Intel Corporation Ethernet Converged
  Network Adapter XL710-Q2
- 85:00.1 Ethernet controller: Intel Corporation Ethernet Controller XL710
  for 40GbE QSFP+ (rev 01) Subsystem: Intel Corporation Ethernet Converged
  Network Adapter XL710-Q2

**VPP Version**

vpp-16.09_amd64

**VPP Compile Parameters**

VPP Compile Job: https://jenkins.fd.io/view/vpp/job/vpp-merge-1609-ubuntu1404/

**VPP Install Parameters**

::

    $ dpkg -i --force-all

**VPP Startup Configuration**

VPP startup configuration changes per test case with different settings for CPU
cores, rx-queues and no-multi-seg parameter. Startup config is aligned with
applied test case tag:

Tagged by **1T1C**::

    $ cat /etc/vpp/startup.conf
    unix {
        nodaemon
        log /tmp/vpe.log
        cli-listen localhost:5002
        full-coredump
    }
    api-trace {
        on
    }
    cpu {
        main-core 0 corelist-workers 1
    }
    dpdk {
        socket-mem 1024,1024
        dev default {
            num-rx-queues 1
        }
        dev 0000:0a:00.1
        dev 0000:0a:00.0
        no-multi-seg
    }
    ip6 {
        hash-buckets 2000000
        heap-size 3g
    }

Tagged by **2T1C**::

    $ cat /etc/vpp/startup.conf
    unix {
        nodaemon
        log /tmp/vpe.log
        cli-listen localhost:5002
        full-coredump
    }
    api-trace {
        on
    }
    cpu {
        main-core 0 corelist-workers 1-2
    }
    dpdk {
        socket-mem 1024,1024
        dev default {
            num-rx-queues 1
        }
        dev 0000:0a:00.1
        dev 0000:0a:00.0
        no-multi-seg
    }
    ip6 {
        hash-buckets 2000000
        heap-size 3g
    }

Tagged by **4T4C**::

    $ cat /etc/vpp/startup.conf
    unix {
        nodaemon
        log /tmp/vpe.log
        cli-listen localhost:5002
        full-coredump
    }
    api-trace {
        on
    }
    cpu {
        main-core 0 corelist-workers 1-4
    }
    dpdk {
        socket-mem 1024,1024
        dev default {
            num-rx-queues 1
        }
        dev 0000:0a:00.1
        dev 0000:0a:00.0
        no-multi-seg
    }
    ip6 {
        hash-buckets 2000000
        heap-size 3g
    }


Config: Traffic Generator - TRex
--------------------------------

**TG Version**

TRex v2.09

**DPDK version**

DPDK v16.07 (20e2b6eba13d9eb61b23ea75f09f2aa966fa6325 - in DPDK repo)

**TG Build Script used**

https://gerrit.fd.io/r/gitweb?p=csit.git;a=blob;f=resources/tools/t-rex/t-rex-installer.sh;h=d015015c9275c706d47788cf308aee2a0477231f;hb=refs/heads/rls1609

**TG Startup Configuration**

::

    $ cat /etc/trex_cfg.yaml
    - port_limit      : 2
      version         : 2
      interfaces      : ["0000:0d:00.0","0000:0d:00.1"]
      port_info       :
        - dest_mac        :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf5]
          src_mac         :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf4]
        - dest_mac        :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf4]
          src_mac         :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf5]

**TG common API - pointer to driver**

https://gerrit.fd.io/r/gitweb?p=csit.git;a=blob;f=resources/tools/t-rex/t-rex-stateless.py;h=8a7f34b27aaf86d81540d72f05959b409e2134a5;hb=refs/heads/rls1609
