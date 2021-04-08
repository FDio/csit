variable "region" {
  description = "AWS Region"
  type = string
}

variable "ami_image" {
  description = "AWS AMI image name"
  type = string
}

variable "testbed_name" {
  description = "Testbed name"
  type = string
}

variable "instance_type" {
  description = "AWS instance type"
  type = string
}

variable "avail_zone" {
  description = "AWS availability zone"
  type = string
}

variable "topology_name" {
  description = "Prefix used when creating a topology file"
  type = string
  default = "2n_aws_c5n"
}

variable "environment_name" {
  description = "Environment name - used for Environment tag"
  type = string
  default = "CSIT-AWS"
}

variable "resources_name_prefix" {
  description = "Resource prefix - used for Name tag"
  type = string
  default = "CSIT_2n_aws_c5n"
}

variable "first_run_commands" {
  description = "Commands to run after deployment via remote-exec"
  type        = list(string)
  default     = [""]
}

variable "ansible_file_path" {
  description = "Path to Ansible playbook"
  type = string
  default = "../../fdio.infra.ansible/site.yaml"
}

variable "ansible_python_executable" {
  description = "Path to Python interpreter"
  type = string
  default = "/usr/bin/python3"
}

variable "ansible_topology_path" {
  description = "Path to Ansible playbook which creates a topology file"
  type = string
  default = "../../fdio.infra.ansible/cloud_topology.yaml"
}

variable "ansible_provision_pwd" {
  description = "Password used for ansible provisioning (ansible_ssh_pass)"
  type        = string
  default     = "Csit1234"
}

# Base VPC CIDRs
variable "vpc_cidr_mgmt" {
  description = "Management CIDR block"
  type = string
  default = "192.168.0.0/24"
}
variable "vpc_cidr_b" {
  description = "CIDR block B"
  type = string
  default = "192.168.10.0/24"
}
variable "vpc_cidr_c" {
  description = "CIDR block C"
  type = string
  default = "200.0.0.0/24"
}
variable "vpc_cidr_d" {
  description = "CIDR block D"
  type = string
  default = "192.168.20.0/24"
}

# Trex Dummy CIDRs
variable "trex_dummy_cidr_port_0" {
  description = "TREX dummy CIDR"
  type = string
  default = "10.0.0.0/24"
}
variable "trex_dummy_cidr_port_1" {
  description = "TREX dummy CIDR"
  type = string
  default = "20.0.0.0/24"
}

# IPs
variable "tg_if1_ip" {
  description = "TG IP on interface 1"
  type = string
  default = "192.168.10.254"
}
variable "tg_if2_ip" {
  description = "TG IP on interface 2"
  type = string
  default = "192.168.20.254"
}
variable "dut1_if1_ip" {
  description = "DUT IP on interface 1"
  type = string
  default = "192.168.10.11"
}
variable "dut1_if2_ip" {
  description = "DUT IP on interface 1"
  type = string
  default = "192.168.20.11"
}
variable "tg_mgmt_ip" {
  description = "TG management interface IP"
  type = string
  default = "192.168.0.10"
}
variable "dut1_mgmt_ip" {
  description = "DUT management interface IP"
  type = string
  default = "192.168.0.11"
}
