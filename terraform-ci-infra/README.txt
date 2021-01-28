This folder contains configuration for terraform based deployments.

AWS
======================
Prerequisities:
ansible >= 2.9

aws-cli >= 2.1.21
  - Configured with personal "AWS Access Key ID" and "AWS Secret Access Key"
  - See: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html

terraform >= v0.14.5
  - Terraform's Ansible provisioner requires manual installation
  - see: https://github.com/radekg/terraform-provisioner-ansible
  - Tested on v2.5.0
