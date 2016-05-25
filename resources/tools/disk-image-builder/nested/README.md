# Nested VM builder

## Summary

The files in this directory are used to build CSIT's "nested VM" image.
The Nested VM image is a mini Linux image that gets spun up inside the
main CSIT test VM for selected test cases.

Considering that this VM is:

- Very purpose-built; the ONLY thing it needs to do is run a bridge group,
- spun up and torn down repeatedly by an automated test case,
- is bundled within another VM image where resources are already limited,

this VM is designed to be minimalistic, small and efficient. For that reason
it is NOT build around any established Linux distribution (Ubuntu,
Red Hat, ...), but around "buildroot" (https://buildroot.org/) which is
aimed at building small Linux images for embedded systems.

Scripts in this directory are aimed at producing functionally identical VM
images each time they are run. That is, a given version of this package
will consistenly download the same buildroot version, and install the same
packages and the same kernel version with the same config.


### Prerequisites

This scripts have been tested on Ubuntu Linux. They should run on any platform
supported by buildroot, and where a standard bourne shell and Linux toolchain
are available.

## Files

### requirements.sh

(One-time) installs required Ubuntu packages for buildroot


### build.sh

Downloads all required packages source code and builds the nested VM image.
Is NOT intended to be run as root, but requires "sudo" privileges for a
handful of commands.

### clean.sh

Remove any object files and compiled files. Keep the downloaded source
packages, both of buildroot itself as well as any packages downloaded by
buildroot.

### deepclean.sh

Remove any compiled or downloaded files.

### CHANGELOG

A change log. This will also be copied onto the image itself.
Versions in the changelog MUST be tagged as follows:

~~~
## [MAJOR.MINOR] YYYY-MM-DD
~~~
eg.

~~~
## [1.0] 2016-05-16
~~~

This format will be used for auto-extracting the version
number, which will become part of the target image filename
and will also be copied onto the image itself.
