Test Environment
================

CSIT functional tests are currently executed in VIRL, as mentioned above. The
physical VIRL testbed infrastructure consists of three identical VIRL hosts,
each host being a Cisco UCS C240-M4 (2x Intel(R) Xeon(R) CPU E5-2699 v3 @
2.30GHz, 18c, 512GB RAM) running Ubuntu 14.04.3 and the following VIRL software
versions:

  STD server version 0.10.24.7
  UWM server version 0.10.24.7

Whenever a patch is submitted to gerrit for review, parallel VIRL simulations
are started to reduce the time of execution of all functional tests. The number
of parallel VIRL simulations is equal to number of test groups defined by
TEST_GROUPS variable in csit/bootstrap.sh file. The VIRL host to run VIRL
simulation is selected randomly per VIRL simulation. Every VIRL simulation uses
the same three-node (TG+SUT1+SUT2), "double-ring" topology. The appropriate
pre-built VPP packages built by Jenkins for the patch under review are then
installed on the two SUTs, along with their /etc/vpp/startup.conf file, in all
VIRL simulations.

Current VPP tests have been executed on a single VM operating system and
version only, as described in the following paragraphs.

In CSIT terminology, the VM operating system for both SUTs and TG that VPP 17.01
has been tested with, is the following:

  ubuntu-16.04.1_2016-12-19_1.6

which implies Ubuntu 16.04.1 LTS, current as of 2016/12/19 (that is, package
versions are those that would have been installed by a "apt-get update",
"apt-get upgrade" on December 19), produced by CSIT disk image build scripts
version 1.6.

The exact list of installed packages and their versions (including the Linux
kernel package version) are included in CSIT source repository:

  resources/tools/disk-image-builder/ubuntu/lists/ubuntu-16.04.1_2016-12-19_1.6

A replica of this VM image can be built by running the "build.sh" script in CSIT
repository resources/tools/disk-image-builder/.

In addition to this "main" VM image, tests which require VPP to communicate to a
VM over a vhost-user interface, utilize a "nested" VM image.

This "nested" VM is dynamically created and destroyed as part of a test case,
and therefore the "nested" VM image is optimized to be small, lightweight and
have a short boot time. The "nested" VM image is not built around any
established Linux distribution, but is based on BuildRoot
(https://buildroot.org/), a tool for building embedded Linux systems. Just as
for the "main" image, scripts to produce an identical replica of the "nested"
image are included in CSIT GIT repository, and the image can be rebuilt using
the "build.sh" script at:

   resources/tools/disk-image-builder/ubuntu/lists/nested

Functional tests utilize Scapy as a traffic generator.  All of the python
libraries used by CSIT are specified in csit/requirements.txt.
