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

Getting started:
~~~~~~~~~~~~~~~~
Tested setup:
- Install and configure prerequisities as specified

- OPTIONAL: Enable logging
  Terraform by default does not store any logs, to enable logging one must
  set up environment variables prior to running any Terraform commands:
  Loglevels: TRACE, DEBUG, INFO, WARN, ERROR

    export TF_LOG="LOGLEVEL"
    export TF_LOG_PATH="path/to/logfile"

- Depending on testbed topology (2 or 3 node), run terraform in a given root module
  Terraform will deploy instances and other resources on AWS, all of these
  can be, if need be, identified via Environment tag ("CSIT-AWS" used as default)
  Example:
    cd ./2n_aws_c5n
    terraform init
    terraform apply

  This will deploy envirnoment with default values, you can check the
  defaults in ./2n_aws_c5n/main.tf and ./2n_aws_c5n/variables.tf

  If you would like to change some of these values you can:
  1) Set up TF_VAR_* environment variables prior to running 'terraform apply', e.g:
      export TF_VAR_testbed_name="testbed1"

  2) Use '-var=varname=value' flag when running 'terraform apply', e.g:
      terraform apply -var=testbed_name=testbed1

  Note:
  Only variables defined in variables.tf file of the root module can be changed
  using these methods.

- Run the tests
  1) To run some tests use the VPP performance bootstrap script, e.g:
      cd ../resources/libraries/bash/entry
      ./bootstrap_vpp_perf.sh csit-vpp-perf-mrr-daily-master-2n-aws

  2) To run only selected tests based on TAGS, export environment variables
     before running the test suite and run a verify JOB, e.g:
      export GERRIT_EVENT_TYPE="comment-added"
      export GERRIT_EVENT_COMMENT_TEXT="1cAND64bANDmrrANDethip4-ip4base"
      ./bootstrap_vpp_perf.sh csit-vpp-perf-verify-master-2n-aws

- To clean up the AWS environment and remove all used resources, run:
    terraform destroy


Azure:
----------------------
Testbed deployment - Microsoft Azure
- ./3n_azure_fsv2/
