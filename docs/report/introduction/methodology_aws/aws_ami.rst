.. _csit_ami:

CSIT Amazon Machine Images
--------------------------

An Amazon Machine Image (AMI) provides the information required to
launch an instance. CSIT is using Amazon Elastic Block Store (EBS) where
the root device for an instance launched from the AMI is a volume
created from an Amazon EBS snapshot.

A the TG and SUT instances have slightly different software
requirements, we are defining two AMIs for TG and SUT separately. AMI
details examples:

- TG:

  - AMI Name: csit_c5n_ubuntu_focal_tg
  - Platform details: Linux/UNIX
  - Architecture: x86_64
  - Usage operation: RunInstances
  - Image Type: machine
  - Virtualization type: hvm
  - Description: CSIT TG image based on Ubuntu Focal
  - Root Device Name: /dev/sda1
  - Root Device Type: ebs

- SUT:

  - AMI Name: csit_c5n_ubuntu_focal_sut
  - Platform details: Linux/UNIX
  - Architecture: x86_64
  - Usage operation: RunInstances
  - Image Type: machine
  - Virtualization type: hvm
  - Description: CSIT SUT image based on Ubuntu Focal
  - Root Device Name: /dev/sda1
  - Root Device Type: ebs

Both TG and SUT AMIs are created manually before launching topology and are not
part of automated scripts.

Building AMIs requires Hashicorp Packer with Amazon plugin installed.

For more information, see
`Amazon Machine Images <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html>`_.
