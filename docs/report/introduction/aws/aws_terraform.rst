Terraform-aws-csit modules
--------------------------

Terraform-aws-csit module is IaaC - infrastructure as a code. Module uses the
Amazon Web Services (AWS) provider to interact with resources provided by AWS
to orchestrate virtual environment for running CSIT tests.

- `aws <https://registry.terraform.io/providers/hashicorp/aws/latest/docs>`_.

Compatibility
~~~~~~~~~~~~~

+-----------+----------------+
| Software  | OSS Version    |
+===========+================+
| Terraform | 1.0.3 or newer |
+-----------+----------------+
| Vault     | 1.8.4 or newer |
+-----------+----------------+

Requirements
~~~~~~~~~~~~

Required modules and provider
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- `aws <https://registry.terraform.io/providers/hashicorp/aws/latest>`_.
- `null <https://registry.terraform.io/providers/hashicorp/null/latest>`_.
- `tls <https://registry.terraform.io/providers/hashicorp/tls>`_.
- `vault <https://registry.terraform.io/providers/hashicorp/vault>`_.

Required software
^^^^^^^^^^^^^^^^^

- `Vault <https://releases.hashicorp.com/vault/>`_ service available on
  specified ip/port.

Usage
~~~~~

- Navigate into root directory of the `CSIT/fdio.infra.terraform/`.

  ::

    cd csit/fdio.infra.terraform/2n_aws_c5n
    cd csit/fdio.infra.terraform/3n_aws_c5n

- OPTIONAL: Enable logging
  Terraform does not have logging enabled by default, to enable logging
  to stderr, set up TF_LOG variable with specified loglevel:
  Available loglevels: TRACE, DEBUG, INFO, WARN, ERROR

  ::

    export TF_LOG="LOGLEVEL"

  It is also possible to store logged output to a file by setting up
  TF_LOG_PATH variable:

  ::

    export TF_LOG_PATH="path/to/logfile"

- Run Terraform in a given root module folder depending on chosen testbed
  topology. Terraform will deploy and configure instances and other resources,
  all of these resources can be later identified on AWS via Environment tag.
  By default, Environment tag "CSIT-AWS" is used.
  Example:

  ::

    cd fdio.infra.terraform/2n_aws_c5n/
    terraform init
    terraform apply

  This will deploy environment with default values, you can check the defaults
  in ./2n_aws_c5n/main.tf and ./2n_aws_c5n/variables.tf files

  If you would like to change some of these values, you can:

  1. Set up TF_VAR_* environment variables prior to running 'terraform apply':

     ::

       export TF_VAR_testbed_name="testbed1"

  2. Use '-var=varname=value' flag when running 'terraform apply':

     ::

       terraform apply -var=testbed_name=testbed1

  Note:
  Only variables defined in variables.tf file of the root module can be
  changed using these methods.

- To clean up the AWS environment and remove all used resources, run:

  ::

    terraform destroy

Example usage
~~~~~~~~~~~~~

These are the default values for the AWS modules. The following example is
2n topology (3n topology variant is very similar). Few variables are defined in
a `variable.tf` file.

::

  module "deploy" {
    source = "./deploy"

    # Parameters starting with var. can be set using "TF_VAR_*" environment
    # variables or -var parameter when running "terraform apply", for default
    # values see ./variables.tf
    testbed_name          = var.testbed_name
    topology_name         = var.topology_name
    environment_name      = var.environment_name
    resources_name_prefix = var.resources_name_prefix

    # AWS general
    region        = var.region
    avail_zone    = var.avail_zone
    instance_type = var.instance_type
    ami_image_tg  = var.ami_image_tg
    ami_image_sut = var.ami_image_sut

    # AWS Network
    vpc_cidr_mgmt = "192.168.0.0/24"
    vpc_cidr_b    = "192.168.10.0/24"
    vpc_cidr_c    = "200.0.0.0/24"
    vpc_cidr_d    = "192.168.20.0/24"

    tg_mgmt_ip   = "192.168.0.10"
    dut1_mgmt_ip = "192.168.0.11"

    tg_if1_ip   = "192.168.10.254"
    tg_if2_ip   = "192.168.20.254"
    dut1_if1_ip = "192.168.10.11"
    dut1_if2_ip = "192.168.20.11"

    trex_dummy_cidr_port_0 = "10.0.0.0/24"
    trex_dummy_cidr_port_1 = "20.0.0.0/24"

    # Ansible
    ansible_python_executable = "/usr/bin/python3"
    ansible_file_path         = "../../fdio.infra.ansible/site.yaml"
    ansible_topology_path     = "../../fdio.infra.ansible/cloud_topology.yaml"
    ansible_provision_pwd     = "Csit1234"

    # First run
    first_run_commands = [
      "sudo sed -i 's/^PasswordAuthentication/#PasswordAuthentication/' /etc/ssh/sshd_config",
      "sudo systemctl restart sshd",
      "sudo useradd --create-home -s /bin/bash provisionuser",
      "echo 'provisionuser:Csit1234' | sudo chpasswd",
      "echo 'provisionuser ALL = (ALL) NOPASSWD: ALL' | sudo tee -a /etc/sudoers",
      "sudo useradd --create-home -s /bin/bash testuser",
      "echo 'testuser:Csit1234' | sudo chpasswd",
      "echo 'testuser ALL = (ALL) NOPASSWD: ALL' | sudo tee -a /etc/sudoers"
    ]
  }

Secrets & Credentials
~~~~~~~~~~~~~~~~~~~~~

Set credentials manually
^^^^^^^^^^^^^^^^^^^^^^^^

To set the credentials manually you first need to tell the module to not fetch
credentials from vault. To do that, set `provider "aws"` `access_key` and
`secret_key` to custom value or use credentials file as a source.

::

  provider "aws" {
    region     = var.region
    access_key = data.vault_aws_access_credentials.creds.access_key
    secret_key = data.vault_aws_access_credentials.creds.secret_key
  }
