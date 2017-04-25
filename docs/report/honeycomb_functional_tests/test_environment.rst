Test Environment
================

CSIT Honeycomb tests are currently executed in VIRL, as mentioned above. The
physical VIRL testbed infrastructure consists of three identical VIRL hosts,
each host being a Cisco UCS C240-M4 (2x Intel(R) Xeon(R) CPU E5-2699 v3 @
2.30GHz, 18c, 512GB RAM) running Ubuntu 14.04.3 and the following VIRL software
versions:

  STD server version 0.10.24.7
  UWM server version 0.10.24.7

Current VPP tests have been executed on a single VM operating system and
version only, as described in the following paragraphs.

In CSIT terminology, the VM operating system for both SUTs and TG that VPP 17.04
has been tested with, is the following:

  ubuntu-16.04.1_2017-02-23_1.8

This image implies Ubuntu 16.04.1 LTS, current as of 2017/02/23 (that is,
package versions are those that would have been installed by a "apt-get update",
"apt-get upgrade" on February 23), produced by CSIT disk image build scripts
version 1.8.

The exact list of installed packages and their versions (including the Linux
kernel package version) are included in CSIT source repository:

  resources/tools/disk-image-builder/ubuntu/lists/ubuntu-16.04.1_2017-02-23_1.8

A replica of this VM image can be built by running the "build.sh" script in CSIT
repository resources/tools/disk-image-builder/ubuntu.

