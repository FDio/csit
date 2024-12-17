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

source "amazon-ebs" "csit_ubuntu_noble_x86_sut" {
  ami_name        = "csit_ubuntu_noble_x86_sut"
  ami_description = "CSIT SUT image based on Ubuntu noble"
  ena_support     = true
  instance_type   = "c5n.4xlarge"
  launch_block_device_mappings {
    device_name = "/dev/sda1"
    volume_size = 40
    volume_type = "gp2"
  }
  force_deregister = true
  region           = "eu-central-1"
  skip_create_ami  = false
  source_ami       = "ami-0084a47cc718c111a"
  ssh_username     = "ubuntu"
  ssh_timeout      = "30m"
}

source "amazon-ebs" "csit_ubuntu_noble_x86_tg" {
  ami_name        = "csit_ubuntu_noble_x86_tg"
  ami_description = "CSIT TG image based on Ubuntu noble"
  ena_support     = true
  instance_type   = "c5n.4xlarge"
  launch_block_device_mappings {
    device_name = "/dev/sda1"
    volume_size = 40
    volume_type = "gp2"
  }
  force_deregister = true
  region           = "eu-central-1"
  skip_create_ami  = false
  source_ami       = "ami-0084a47cc718c111a"
  ssh_username     = "ubuntu"
  ssh_timeout      = "30m"
}

build {
  name = "csit_ubuntu_noble_x86_sut-packer"
  sources = [
    "source.amazon-ebs.csit_ubuntu_noble_x86_sut"
  ]
  provisioner "shell" {
    inline = var.first_run_commands
  }
  provisioner "ansible" {
    playbook_file = var.ansible_file_path
    user          = "ubuntu"
    use_proxy     = false
    groups        = ["sut_aws"]
    extra_arguments = [
      "--extra-vars", "ansible_ssh_pass=${var.ansible_provision_pwd}",
      "--extra-vars", "aws=true"
    ]
  }
  provisioner "shell" {
    inline = var.last_run_commands
  }
}

build {
  name = "csit_ubuntu_noble_x86_tg-packer"
  sources = [
    "source.amazon-ebs.csit_ubuntu_noble_x86_tg"
  ]
  provisioner "shell" {
    inline = var.first_run_commands
  }
  provisioner "ansible" {
    playbook_file = var.ansible_file_path
    user          = "ubuntu"
    use_proxy     = false
    groups        = ["tg_aws"]
    extra_arguments = [
      "--extra-vars", "ansible_ssh_pass=${var.ansible_provision_pwd}",
      "--extra-vars", "aws=true",
      "--extra-vars", "docker_tg=true"
    ]
  }
  provisioner "shell" {
    inline = var.last_run_commands
  }
}
