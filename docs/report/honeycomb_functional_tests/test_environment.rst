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

In CSIT terminology, the VM operating system for both DUTs and TG that
|vpp-release| has been tested with, is the following:

  |virl-image-ubuntu|

This image implies Ubuntu 16.04.1 LTS, current as of yyyy-mm-dd (that is,
package versions are those that would have been installed by a "apt-get update",
"apt-get upgrade" on that day), produced by CSIT disk image build scripts.

The exact list of installed packages and their versions (including the Linux
kernel package version) are included in `VIRL images lists`_.

A replica of this VM image can be built by running the "build.sh" script in
`VIRL nested`_.

