packer {
  required_plugins {
    amazon = {
      version = ">= 1.2.6"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

variable "first_run_commands" {
  description = "Commands to run before deployment via remote-exec"
  type        = list(string)
  default = [
    ""
  ]
}

variable "last_run_commands" {
  description = "Commands to run after deployment via remote-exec"
  type        = list(string)
  default = [
    "sudo sed -i 's/Unattended-Upgrade \"1\"/Unattended-Upgrade \"0\"/g' /etc/apt/apt.conf.d/20auto-upgrades"
  ]
}

variable "ansible_file_path" {
  description = "Path to Ansible playbook"
  type        = string
  default     = "../../fdio.infra.ansible/site.yaml"
}

variable "ansible_python_executable" {
  description = "Path to Python interpreter"
  type        = string
  default     = "/usr/bin/python3"
}

variable "ansible_topology_path" {
  description = "Path to Ansible playbook which creates a topology file"
  type        = string
  default     = "../../fdio.infra.ansible/cloud_topology.yaml"
}

variable "ansible_provision_pwd" {
  description = "Password used for ansible provisioning (ansible_ssh_pass)"
  type        = string
  default     = "Csit1234"
}

source "amazon-ebs" "csit_ubuntu_noble_arm_sut" {
  ami_name        = "csit_ubuntu_noble_arm_sut"
  ami_description = "CSIT SUT image based on Ubuntu noble"
  ena_support     = true
  instance_type   = "c7gn.4xlarge"
  launch_block_device_mappings {
    device_name = "/dev/sda1"
    volume_size = 40
    volume_type = "gp2"
  }
  force_deregister = true
  region           = "eu-west-1"
  skip_create_ami  = false
  source_ami       = "ami-099a546c02844706e"
  ssh_username     = "ubuntu"
}

build {
  name = "csit_ubuntu_noble_arm_sut-packer"
  sources = [
    "source.amazon-ebs.csit_ubuntu_noble_arm_sut"
  ]
  provisioner "shell" {
    inline = var.first_run_commands
  }
  provisioner "ansible" {
    playbook_file = var.ansible_file_path
    user          = "ubuntu"
    groups        = ["sut_aws"]
    extra_arguments = [
      "--extra-vars", "ansible_ssh_pass=${var.ansible_provision_pwd}",
      "--extra-vars", "ansible_python_interpreter=${var.ansible_python_executable}",
      "--extra-vars", "aws=true"
    ]
  }
  provisioner "shell" {
    inline = var.last_run_commands
  }
}
