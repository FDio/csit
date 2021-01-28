provider "aws" {
  region = var.region
}

resource "aws_vpc" "CSITVPC" {
  cidr_block = var.vpc_cidr_mgmt

  tags = {
    "Name" = "${var.resources_name_prefix}_${var.testbed_name}-VPC"
    "Environment" = var.environment_name
  }
}

resource "aws_security_group" "CSITSG" {
  name        = "${var.resources_name_prefix}_${var.testbed_name}-sg"
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
    "Environment" = var.environment_name
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
    "Environment" = var.environment_name
  }
}
resource "aws_subnet" "b" {
  vpc_id = aws_vpc.CSITVPC.id
  cidr_block = var.vpc_cidr_b
  availability_zone = var.avail_zone
  depends_on = [aws_vpc.CSITVPC, aws_vpc_ipv4_cidr_block_association.b]

  tags = {
    "Environment" = var.environment_name
  }
}
resource "aws_subnet" "c" {
  vpc_id = aws_vpc.CSITVPC.id
  cidr_block = var.vpc_cidr_c
  availability_zone = var.avail_zone
  depends_on = [aws_vpc.CSITVPC, aws_vpc_ipv4_cidr_block_association.c]

  tags = {
    "Environment" = var.environment_name
  }
}
resource "aws_subnet" "d" {
  vpc_id = aws_vpc.CSITVPC.id
  cidr_block = var.vpc_cidr_d
  availability_zone = var.avail_zone
  depends_on = [aws_vpc.CSITVPC, aws_vpc_ipv4_cidr_block_association.d]

  tags = {
    "Environment" = var.environment_name
  }
}

resource "aws_internet_gateway" "CSITGW" {
  vpc_id = aws_vpc.CSITVPC.id
  depends_on = [aws_vpc.CSITVPC]

  tags = {
    "Environment" = var.environment_name
  }
}

# SSH keypair
# Temporary key for provisioning only
resource "tls_private_key" "CSITTLS" {
  algorithm = "RSA"
  rsa_bits  = 4096
}
resource "aws_key_pair" "CSITKP" {
  key_name = "${var.resources_name_prefix}_${var.testbed_name}-key"
  public_key = tls_private_key.CSITTLS.public_key_openssh
}

resource "aws_placement_group" "CSITPG" {
  name = "${var.resources_name_prefix}_${var.testbed_name}-pg"
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
  # host_id = "1"
  source_dest_check = false

  tags = {
    "Name" = "${var.resources_name_prefix}_${var.testbed_name}-tg"
    "Environment" = var.environment_name
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
  # host_id = "2"
  source_dest_check = false

  tags = {
    "Name" = "${var.resources_name_prefix}_${var.testbed_name}-dut1"
    "Environment" = var.environment_name
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
    inline = var.first_run_commands
  }

  provisioner "ansible" {
    plays {
      playbook {
        file_path = var.ansible_file_path
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
    inline = var.first_run_commands
  }

  provisioner "ansible" {
    plays {
      playbook {
        file_path = var.ansible_file_path
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
  depends_on = [ aws_instance.tg, aws_instance.dut1 ]
  provisioner "ansible" {
    plays {
      playbook {
        file_path = "../../resources/tools/testbed-setup/ansible/cloud_topology.yaml"
      }
      hosts = ["local"]
      extra_vars = {
        ansible_python_interpreter = "/usr/bin/python3"
        testbed_name = var.testbed_name
        cloud_topology = "aws_2n_c5n"
        tg_if1_mac = data.aws_network_interface.tg_if1.mac_address
        tg_if2_mac = data.aws_network_interface.tg_if2.mac_address
        dut1_if1_mac = data.aws_network_interface.dut1_if1.mac_address
        dut1_if2_mac = data.aws_network_interface.dut1_if2.mac_address
        tg_public_ip = aws_instance.tg.public_ip
        dut1_public_ip = aws_instance.dut1.public_ip
        public_ip_list = "${aws_instance.tg.public_ip},${aws_instance.dut1.public_ip}"
      }
    }
  }
}
