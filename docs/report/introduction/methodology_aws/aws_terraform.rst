AWS Deployments
---------------

CSIT performance testbed deployments in AWS rely on
Infrastructure-as-a-C (IaaC) Terraform AWS providers. Terraform
providers specified in CSIT interact with resources provided by AWS to
orchestrate virtual environment for running CSIT performance tests.

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

- Required Modules and Providers

  - `Terraform Registry aws <https://registry.terraform.io/providers/hashicorp/aws/latest>`_.
  - `Terraform Registry null <https://registry.terraform.io/providers/hashicorp/null/latest>`_.
  - `Terraform Registry tls <https://registry.terraform.io/providers/hashicorp/tls>`_.
  - `Terraform Registry vault <https://registry.terraform.io/providers/hashicorp/vault>`_.

- Required software

  - `Vault <https://releases.hashicorp.com/vault/>`_ service available
    on specified ip/port.

Deployment Example
~~~~~~~~~~~~~~~~~~

Following is an example of a
`Terraform deploy module <https://git.fd.io/csit/tree/fdio.infra.terraform/2n_aws_c5n/main.tf>`_
for a CSIT 2-Node testbed topology with AWS variables set to default
values. A number of variables is also defined in a
`separate Terraform variable file <https://git.fd.io/csit/tree/fdio.infra.terraform/2n_aws_c5n/variables.tf>`_.

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

To set the credentials manually you first need to tell the module to not
fetch credentials from Vault. To do that, set `provider "aws"`
`access_key` and `secret_key` to custom value or use credentials file
as a source.

::

  provider "aws" {
    region     = var.region
    access_key = data.vault_aws_access_credentials.creds.access_key
    secret_key = data.vault_aws_access_credentials.creds.secret_key
  }
