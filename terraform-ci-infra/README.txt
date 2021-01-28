Terraform CI Infra
==================
This folder contains configuration for terraform based deployments.


Nomad:
----------------------
Application orchestration - Nomad
- ./1n_nmd/


AWS:
----------------------
Testbed deployment - Amazon AWS
- ./2n_aws_c5n/
- ./3n_aws_c5n/

Prerequisities:
~~~~~~~~~~~~~~~
aws-cli >= 2.1.21
  - Configured with personal "AWS Access Key ID" and "AWS Secret Access Key"
  - See: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html

terraform >= v0.13
  - Terraform's Ansible provisioner requires manual installation
  - see: https://github.com/radekg/terraform-provisioner-ansible
  - Tested on v2.5.0


Azure:
----------------------
Testbed deployment - Microsoft Azure
- ./3n_azure_fsv2/
