TODO: Maybe move somwhere to docs?

This folder contains configuration for terraform based deployments.

AWS
======================
Requirements:
aws-cli >= 2.1.21
    - Configured with personal "AWS Access Key ID" and "AWS Secret Access Key"
    - See: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html

terraform >= v0.14.5
    - Ansible provisioner is needed
    - Although "terraform-provisioner-ansible" is in the terraform registry, it cannot be installed using a module terraform stanza
    - Manual install required, see: https://github.com/radekg/terraform-provisioner-ansible

Public and private keys in ./ssh folder for remote access to deployed topology
