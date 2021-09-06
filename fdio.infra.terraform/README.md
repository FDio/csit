# Terraform CI Infra

This folder contains configuration for terraform based deployments.

## Nomad

Application orchestration - Nomad
- ./1n_nmd/

## AWS

Testbed deployment - Amazon AWS
- ./2n_aws_c5n/
- ./3n_aws_c5n/

### Getting Started

Tested setup:
- Install and configure prerequisities as specified.

- OPTIONAL: Enable logging
  Terraform does not have logging enabled by default, to enable logging
  to stderr, set up TF_LOG variable with specified loglevel:
  Available loglevels: TRACE, DEBUG, INFO, WARN, ERROR

    export TF_LOG="LOGLEVEL"

  It is also possible to store logged output to a file by setting up
  TF_LOG_PATH variable:
    export TF_LOG_PATH="path/to/logfile"

- Run Terraform in a given root module folder depending on chosen testbed
  topology. Terraform will deploy and configure instances and other resources,
  all of these resources can be later identified on AWS via Environment tag.
  By default, Environment tag "CSIT-AWS" is used.
  Example:
    cd fdio.infra.terraform/2n_aws_c5n/
    terraform init
    terraform apply

  This will deploy environment with default values, you can check the defaults
  in ./2n_aws_c5n/main.tf and ./2n_aws_c5n/variables.tf files

  If you would like to change some of these values, you can:
  1) Set up TF_VAR_* environment variables prior to running 'terraform apply':
      export TF_VAR_testbed_name="testbed1"

  2) Use '-var=varname=value' flag when running 'terraform apply':
      terraform apply -var=testbed_name=testbed1

  Note:
  Only variables defined in variables.tf file of the root module can be
  changed using these methods.

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

## Azure

Testbed deployment - Microsoft Azure
- ./3n_azure_fsv2/
