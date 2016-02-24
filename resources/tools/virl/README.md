## VIRL scripts

This directory, and subdirectories, contain files required for automated VIRL testing. These files
are based on the following assumptions:

  - Files in this directory are installed on the VIRL server host, and scripts in bin/ directory
    are executable by the user used in the bootstrap.sh script in the root directory of this
    project

  - the VIRL server has a "server" image, as well as a "vPP" image that is accepting a cloud-init
    configuration and is ready to receive a VPP upgrade.

  - the VIRL server has an NFS export that can be mounted by VIRL VMs, or there is an NFS server
    with an export mounted by the VIRL server and mountable by VIRL VMs.

  - the bin/start_testcase script has hardcoded default values both in variable assignments
    near the beginning of the file, as well as in "parser.add_argument", "default=" options.
    These may need to be updated.
