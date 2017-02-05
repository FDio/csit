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

In CSIT terminology, the VM operating system for both SUTs and TG that VPP 17.01
has been tested with, is the following:

  ubuntu-14.04.4_2016-10-07_1.3

which implies Ubuntu 14.04.3 LTS, current as of 2016/10/07 (that is, package
versions are those that would have been installed by a "apt-get update",
"apt-get upgrade" on October 7), produced by CSIT disk image build scripts
version 1.6.

The exact list of installed packages and their versions (including the Linux
kernel package version) are included in CSIT source repository:

  resources/tools/disk-image-builder/ubuntu/lists/ubuntu-14.04.4_2016-10-07_1.3

A replica of this VM image can be built by running the "build.sh" script in CSIT
repository resources/tools/disk-image-builder/.

