provider "aws" {
  region = "eu-central-1"
}

variable "ami_image" {
  type = string
  default = "ami-0b418580298265d5c"
  # eu-central-1
  # bionic-18.04-amd64-hvm-ssd-20200112, kernel ~4.15.0-74
}

variable "testbed_name" {
  type = string
  # Use ENV variable when deploying multiple testbeds???
  default = "testbed1"
}

variable "instance_type" {
  type = string
  default = "c5n.4xlarge"
}

variable "avail_zone" {
  type = string
  default = "eu-central-1a"
}

# Base VPC CIDRs
variable "vpc_cidr_mgmt" {
  type = string
  default = "192.168.0.0/24"
}
variable "vpc_cidr_b" {
  type = string
  default = "192.168.10.0/24"
}
variable "vpc_cidr_c" {
  type = string
  default = "200.0.0.0/24"
}
variable "vpc_cidr_d" {
  type = string
  default = "192.168.20.0/24"
}

# Trex Dummy CIDRs
variable "trex_dummy_cidr_port_0" {
  type = string
  default = "10.0.0.0/24"
}
variable "trex_dummy_cidr_port_1" {
  type = string
  default = "20.0.0.0/24"
}

# IPs
variable "tg_if1_ip" {
  type = string
  default = "192.168.10.254"
}
variable "tg_if2_ip" {
  type = string
  default = "192.168.20.254"
}
variable "dut1_if1_ip" {
  type = string
  default = "192.168.10.11"
}
variable "dut1_if2_ip" {
  type = string
  default = "200.0.0.101"
}
variable "dut2_if1_ip" {
  type = string
  default = "200.0.0.102"
}
variable "dut2_if2_ip" {
  type = string
  default = "192.168.20.11"
}
variable "tg_mgmt_ip" {
  type = string
  default = "192.168.0.10"
}
variable "dut1_mgmt_ip" {
  type = string
  default = "192.168.0.11"
}
variable "dut2_mgmt_ip" {
  type = string
  default = "192.168.0.12"
}

resource "aws_vpc" "CSITVPC" {
  cidr_block = var.vpc_cidr_mgmt

  tags = {
    "Name" = "CSIT_3n_aws_c5n_${var.testbed_name}-VPC"
    "Environment" = "CSIT-AWS"
  }
}

resource "aws_security_group" "CSITSG" {
  name        = "CSIT_3n_aws_c5n_${var.testbed_name}-sg"
  description = "Allow inbound traffic"
  vpc_id = aws_vpc.CSITVPC.id

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 0
    to_port = 0
    protocol = -1
    self = true
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  depends_on = [aws_vpc.CSITVPC]

  tags = {
    "Environment" = "CSIT-AWS"
  }
}

resource "aws_vpc_ipv4_cidr_block_association" "b" {
  vpc_id = aws_vpc.CSITVPC.id
  cidr_block = var.vpc_cidr_b
  depends_on = [aws_vpc.CSITVPC]
}
resource "aws_vpc_ipv4_cidr_block_association" "c" {
  vpc_id = aws_vpc.CSITVPC.id
  cidr_block = var.vpc_cidr_c
  depends_on = [aws_vpc.CSITVPC]
}
resource "aws_vpc_ipv4_cidr_block_association" "d" {
  vpc_id = aws_vpc.CSITVPC.id
  cidr_block = var.vpc_cidr_d
  depends_on = [aws_vpc.CSITVPC]
}

# Subnets
resource "aws_subnet" "mgmt" {
  vpc_id = aws_vpc.CSITVPC.id
  cidr_block = var.vpc_cidr_mgmt
  availability_zone = var.avail_zone
  depends_on = [aws_vpc.CSITVPC]

  tags = {
    "Environment" = "CSIT-AWS"
  }
}
resource "aws_subnet" "b" {
  vpc_id = aws_vpc.CSITVPC.id
  cidr_block = var.vpc_cidr_b
  availability_zone = var.avail_zone
  depends_on = [aws_vpc.CSITVPC, aws_vpc_ipv4_cidr_block_association.b]

  tags = {
    "Environment" = "CSIT-AWS"
  }
}
resource "aws_subnet" "c" {
  vpc_id = aws_vpc.CSITVPC.id
  cidr_block = var.vpc_cidr_c
  availability_zone = var.avail_zone
  depends_on = [aws_vpc.CSITVPC, aws_vpc_ipv4_cidr_block_association.c]

  tags = {
    "Environment" = "CSIT-AWS"
  }
}
resource "aws_subnet" "d" {
  vpc_id = aws_vpc.CSITVPC.id
  cidr_block = var.vpc_cidr_d
  availability_zone = var.avail_zone
  depends_on = [aws_vpc.CSITVPC, aws_vpc_ipv4_cidr_block_association.d]

  tags = {
    "Environment" = "CSIT-AWS"
  }
}

resource "aws_internet_gateway" "CSITGW" {
  vpc_id = aws_vpc.CSITVPC.id
  depends_on = [aws_vpc.CSITVPC]

  tags = {
    "Environment" = "CSIT-AWS"
  }
}

# SSH keypair
# Temporary key for provisioning only
resource "tls_private_key" "CSITTLS" {
  algorithm = "RSA"
  rsa_bits  = 4096
}
resource "aws_key_pair" "CSITKP" {
  key_name = "CSIT_3n_aws_c5n_${var.testbed_name}-key"
  public_key = tls_private_key.CSITTLS.public_key_openssh
}

resource "aws_placement_group" "CSITPG" {
  name = "CSIT_3n_aws_c5n_${var.testbed_name}-pg"
  strategy = "cluster"
}

# Instances
resource "aws_instance" "tg" {
  ami = var.ami_image
  instance_type = var.instance_type
  key_name = aws_key_pair.CSITKP.key_name
  associate_public_ip_address = true
  subnet_id = aws_subnet.mgmt.id

  root_block_device {
    volume_size = 50
  }

  private_ip = var.tg_mgmt_ip
  vpc_security_group_ids = [aws_security_group.CSITSG.id]
  depends_on = [aws_vpc.CSITVPC, aws_placement_group.CSITPG]
  placement_group = aws_placement_group.CSITPG.id
  source_dest_check = false

  tags = {
    "Name" = "CSIT.3n_${var.testbed_name}.tg"
    "Environment" = "CSIT-AWS"
  }
}

resource "aws_instance" "dut1" {
  ami = var.ami_image
  instance_type = var.instance_type
  key_name = aws_key_pair.CSITKP.key_name
  associate_public_ip_address = true
  subnet_id = aws_subnet.mgmt.id

  root_block_device {
    volume_size = 50
  }

  private_ip = var.dut1_mgmt_ip
  vpc_security_group_ids = [aws_security_group.CSITSG.id]
  depends_on = [aws_vpc.CSITVPC, aws_placement_group.CSITPG]
  placement_group = aws_placement_group.CSITPG.id
  source_dest_check = false

  tags = {
    "Name" = "CSIT.3n_${var.testbed_name}.dut1"
    "Environment" = "CSIT-AWS"
  }
}

resource "aws_instance" "dut2" {
  ami = var.ami_image
  instance_type = var.instance_type
  key_name = aws_key_pair.CSITKP.key_name
  associate_public_ip_address = true
  subnet_id = aws_subnet.mgmt.id

  root_block_device {
    volume_size = 50
  }

  private_ip = var.dut2_mgmt_ip
  vpc_security_group_ids = [aws_security_group.CSITSG.id]
  depends_on = [aws_vpc.CSITVPC, aws_placement_group.CSITPG]
  placement_group = aws_placement_group.CSITPG.id
  source_dest_check = false

  tags = {
    "Name" = "CSIT.3n_${var.testbed_name}.dut2"
    "Environment" = "CSIT-AWS"
  }
}

# Routes
resource "aws_route" "CSIT-igw" {
  route_table_id = aws_vpc.CSITVPC.main_route_table_id
  gateway_id = aws_internet_gateway.CSITGW.id
  destination_cidr_block = "0.0.0.0/0"
  depends_on = [aws_vpc.CSITVPC, aws_internet_gateway.CSITGW]
}
resource "aws_route" "dummy-trex-port-0" {
  route_table_id = aws_vpc.CSITVPC.main_route_table_id
  network_interface_id = aws_instance.tg.primary_network_interface_id
  destination_cidr_block = var.trex_dummy_cidr_port_0
  depends_on = [aws_vpc.CSITVPC, aws_instance.dut1]
}
resource "aws_route" "dummy-trex-port-1" {
  route_table_id = aws_vpc.CSITVPC.main_route_table_id
  network_interface_id = aws_instance.tg.primary_network_interface_id
  destination_cidr_block = var.trex_dummy_cidr_port_1
  depends_on = [aws_vpc.CSITVPC, aws_instance.dut1]
}

# Deployment/Ansible
resource "null_resource" "deploy_tg" {
  depends_on = [ aws_instance.tg ]

  connection {
    user = "ubuntu"
    host = aws_instance.tg.public_ip
    private_key = tls_private_key.CSITTLS.private_key_pem
  }

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -qq",
      "sudo sed -i 's/^PasswordAuthentication no/^PasswordAuthentication yes/' /etc/ssh/sshd_config",
      "sudo systemctl restart sshd",
      "sudo useradd --create-home -s /bin/bash provisionuser",
      "echo 'provisionuser:Csit1234' | sudo chpasswd",
      "echo 'provisionuser ALL = (ALL) NOPASSWD: ALL' | sudo tee -a /etc/sudoers",
      # Remove testuser when added to user_add ansible role
      "sudo useradd --create-home -s /bin/bash testuser",
      "echo 'testuser:Csit1234' | sudo chpasswd",
      "echo 'testuser ALL = (ALL) NOPASSWD: ALL' | sudo tee -a /etc/sudoers"
    ]
  }

  provisioner "ansible" {
    plays {
      playbook {
        file_path = "../../resources/tools/testbed-setup/ansible/site_aws.yaml"
        force_handlers = true
      }
      hosts = ["tg_aws"]
      extra_vars = {
        ansible_python_interpreter = "/usr/bin/python3"
        aws = true
      }
    }
  }
}

resource "null_resource" "deploy_dut1" {
  depends_on = [ aws_instance.dut1 ]
  connection {
    user = "ubuntu"
    host = aws_instance.dut1.public_ip
    private_key = tls_private_key.CSITTLS.private_key_pem
    }

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -qq",
      "sudo sed -i 's/^PasswordAuthentication no/^PasswordAuthentication yes/' /etc/ssh/sshd_config",
      "sudo systemctl restart sshd",
      "sudo useradd --create-home -s /bin/bash provisionuser",
      "echo 'provisionuser:Csit1234' | sudo chpasswd",
      "echo 'provisionuser ALL = (ALL) NOPASSWD: ALL' | sudo tee -a /etc/sudoers",
      # Remove testuser when added to user_add ansible role
      "sudo useradd --create-home -s /bin/bash testuser",
      "echo 'testuser:Csit1234' | sudo chpasswd",
      "echo 'testuser ALL = (ALL) NOPASSWD: ALL' | sudo tee -a /etc/sudoers"
    ]
  }

  provisioner "ansible" {
    plays {
      playbook {
        file_path = "../../resources/tools/testbed-setup/ansible/site_aws.yaml"
        force_handlers = true
      }
      hosts = ["sut_aws"]
      extra_vars = {
        ansible_python_interpreter = "/usr/bin/python3"
        aws = true
      }
    }
  }
}

resource "null_resource" "deploy_dut2" {
  depends_on = [ aws_instance.dut2 ]
  connection {
    user = "ubuntu"
    host = aws_instance.dut2.public_ip
    private_key = tls_private_key.CSITTLS.private_key_pem
    }

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -qq",
      "sudo sed -i 's/^PasswordAuthentication no/^PasswordAuthentication yes/' /etc/ssh/sshd_config",
      "sudo systemctl restart sshd",
      "sudo useradd --create-home -s /bin/bash provisionuser",
      "echo 'provisionuser:Csit1234' | sudo chpasswd",
      "echo 'provisionuser ALL = (ALL) NOPASSWD: ALL' | sudo tee -a /etc/sudoers",
      # Remove testuser when added to user_add ansible role
      "sudo useradd --create-home -s /bin/bash testuser",
      "echo 'testuser:Csit1234' | sudo chpasswd",
      "echo 'testuser ALL = (ALL) NOPASSWD: ALL' | sudo tee -a /etc/sudoers"
    ]
  }

  provisioner "ansible" {
    plays {
      playbook {
        file_path = "../../resources/tools/testbed-setup/ansible/site_aws.yaml"
        force_handlers = true
      }
      hosts = ["sut_aws"]
      extra_vars = {
        ansible_python_interpreter = "/usr/bin/python3"
        aws = true
      }
    }
  }
}

resource "null_resource" "deploy_topology" {
  depends_on = [ aws_instance.tg, aws_instance.dut1, aws_instance.dut2 ]
  provisioner "ansible" {
    plays {
      playbook {
        file_path = "../../resources/tools/testbed-setup/ansible/cloud_topology.yaml"
      }
      hosts = ["local"]
      extra_vars = {
        ansible_python_interpreter = "/usr/bin/python3"
        testbed_name = var.testbed_name
        cloud_topology = "3n_aws_c5n"
        tg_if1_mac = data.aws_network_interface.tg_if1.mac_address
        tg_if2_mac = data.aws_network_interface.tg_if2.mac_address
        dut1_if1_mac = data.aws_network_interface.dut1_if1.mac_address
        dut1_if2_mac = data.aws_network_interface.dut1_if2.mac_address
        dut2_if1_mac = data.aws_network_interface.dut2_if1.mac_address
        dut2_if2_mac = data.aws_network_interface.dut2_if2.mac_address
        tg_public_ip = aws_instance.tg.public_ip
        dut1_public_ip = aws_instance.dut1.public_ip
        dut2_public_ip = aws_instance.dut2.public_ip
        public_ip_list = "${aws_instance.tg.public_ip},${aws_instance.dut1.public_ip},${aws_instance.dut2.public_ip}"
      }
    }
  }
}

output "dbg_tg" {
  value = "TG IP: ${aws_instance.tg.public_ip}"
}

output "dbg_dut1" {
  value = "DUT1 IP: ${aws_instance.dut1.public_ip}"
}

output "dbg_dut2" {
  value = "DUT2 IP: ${aws_instance.dut2.public_ip}"
}
