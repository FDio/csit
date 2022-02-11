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

  trex_dummy_cidr_port_0 = "10.0.0.0/16"
  trex_dummy_cidr_port_1 = "20.0.0.0/16"

  # Ansible
  ansible_python_executable = "/usr/bin/python3"
  ansible_file_path         = "../../fdio.infra.ansible/site.yaml"
  ansible_topology_path     = "../../fdio.infra.ansible/cloud_topology.yaml"
  ansible_provision_pwd     = "Csit1234"

  # First run
  # TODO: Remove the testuser creation when added to user_add ansible role
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
