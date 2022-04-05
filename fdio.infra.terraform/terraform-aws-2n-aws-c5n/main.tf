data "vault_aws_access_credentials" "creds" {
  backend = "${var.vault-name}-path"
  role    = "${var.vault-name}-role"
}

locals {
  ansible_python_executable = "/usr/bin/python3"
  availability_zone         = "eu-central-1a"
  name                      = "csit-vpc"
  environment               = "csit-vpc-environment"
  key_pair_key_name         = "${var.resource_prefix}-${var.testbed_name}-pk"
  placement_group_name      = "${var.resource_prefix}-${var.testbed_name}-pg"
  security_group_name       = "${var.resource_prefix}-${var.testbed_name}-sg"
  testbed_name              = "testbed1"
  topology_name             = "2n-aws-c5n"
  tg_name                   = "${var.resource_prefix}-${var.testbed_name}-tg"
  sut1_name                 = "${var.resource_prefix}-${var.testbed_name}-sut1"
}

resource "aws_vpc" "vpc" {
  assign_generated_ipv6_cidr_block = true
  enable_dns_hostnames             = false
  enable_dns_support               = true
  cidr_block                       = "192.168.0.0/24"
  instance_tenancy                 = "default"

  tags = {
    "Name"        = "${var.resource_prefix}-${var.testbed_name}-vpc"
    "Environment" = local.environment
  }
}

resource "aws_security_group" "security_group" {
  depends_on                       = [
    aws_vpc.vpc
  ]
  description                      = "Allow inbound traffic"
  name                             = "${var.resource_prefix}-${var.testbed_name}-sg"
  revoke_rules_on_delete           = false
  vpc_id                           = aws_vpc.vpc.id

  ingress {
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    from_port        = 0
    to_port          = 0
    protocol         = -1
    self             = true
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    "Name"        = "${var.resource_prefix}-${var.testbed_name}-sg"
    "Environment" = local.environment
  }
}

resource "aws_internet_gateway" "internet_gateway" {
  depends_on = [
    aws_vpc.vpc
  ]
  vpc_id     = aws_vpc.vpc.id

  tags = {
    "Environment" = local.environment
  }
}

resource "aws_route" "route" {
  depends_on             = [
    aws_vpc.vpc,
    aws_internet_gateway.internet_gateway
  ]
  destination_cidr_block      = "0.0.0.0/0"
  destination_ipv6_cidr_block = "::/0"
  gateway_id                  = aws_internet_gateway.internet_gateway.id
  route_table_id              = aws_vpc.vpc.main_route_table_id
}

# Create Subnet
resource "aws_vpc_ipv4_cidr_block_association" "b" {
  depends_on = [
    aws_vpc.vpc
  ]
  cidr_block = "192.168.10.0/24"
  vpc_id     = aws_vpc.vpc.id
}

resource "aws_vpc_ipv4_cidr_block_association" "c" {
  depends_on = [
    aws_vpc.vpc
  ]
  cidr_block = "200.0.0.0/24"
  vpc_id     = aws_vpc.vpc.id
}

resource "aws_vpc_ipv4_cidr_block_association" "d" {
  depends_on = [
    aws_vpc.vpc.id
  ]
  cidr_block = "192.168.20.0/24"
  vpc_id     = aws_vpc.vpc.id
}

resource "aws_subnet" "b" {
  availability_zone               = local.availability_zone
  assign_ipv6_address_on_creation = true
  cidr_block                      = "192.168.10.0/24"
  depends_on = [
    aws_vpc.vpc,
    aws_vpc_ipv4_cidr_block_association.b
  ]
  ipv6_cidr_block                 = cidrsubnet(aws_vpc.vpc.ipv6_cidr_block, 8, 2)
  map_public_ip_on_launch         = false
  vpc_id                          = aws_vpc.vpc.id
  tags = {
    "Environment" = local.environment
  }
}

resource "aws_subnet" "c" {
  availability_zone               = local.availability_zone
  assign_ipv6_address_on_creation = true
  cidr_block                      = "200.0.0.0/24"
  depends_on = [
    aws_vpc.vpc,
    aws_vpc_ipv4_cidr_block_association.c
  ]
  ipv6_cidr_block                 = cidrsubnet(aws_vpc.vpc.ipv6_cidr_block, 8, 3)
  map_public_ip_on_launch         = false
  vpc_id                          = aws_vpc.vpc.id
  tags = {
    "Environment" = local.environment
  }
}

resource "aws_subnet" "d" {
  availability_zone               = local.availability_zone
  assign_ipv6_address_on_creation = true
  cidr_block                      = "192.168.20.0/24"
  depends_on = [
    aws_vpc.vpc,
    aws_vpc_ipv4_cidr_block_association.d
  ]
  ipv6_cidr_block                 = cidrsubnet(aws_vpc.vpc.ipv6_cidr_block, 8, 4)
  map_public_ip_on_launch         = false
  vpc_id                          = aws_vpc.vpc.id
  tags = {
    "Environment" = local.environment
  }
}

# Create Private Key
resource "tls_private_key" "private_key" {
  algorithm   = var.private_key_algorithm
  ecdsa_curve = var.private_key_ecdsa_curve
  rsa_bits    = var.private_key_rsa_bits
}

# Create Key Pair
resource "aws_key_pair" "key_pair" {
  depends_on = [
    tls_private_key.private_key
  ]
  key_name   = local.key_pair_key_name
  public_key = tls_private_key.private_key.public_key_openssh
}

# Create Placement Group
resource "aws_placement_group" "placement_group" {
  name     = local.placement_group_name
  strategy = var.placement_group_strategy
}

# Create Instance
resource "aws_instance" "tg" {
  depends_on = [
    aws_vpc.vpc,
    aws_placement_group.placement_group,
    aws_security_group.security_group.id,
  ]
  ami                                  = var.tg_ami
  availability_zone                    = local.availability_zone
  associate_public_ip_address          = var.tg_associate_public_ip_address
  instance_initiated_shutdown_behavior = var.tg_instance_initiated_shutdown_behavior
  instance_type                        = var.tg_instance_type
  key_name                             = aws_key_pair.key_pair.key_name
  placement_group                      = aws_placement_group.placement_group.id
  private_ip                           = var.tg_private_ip
  source_dest_check                    = var.tg_source_dest_check
  subnet_id                            = aws_subnet.subnet.id
  vpc_security_group_ids               = [aws_security_group.security_group.id]
  # host_id                            = "1"

  root_block_device {
    delete_on_termination = true
    volume_size           = 50
  }

  tags = {
    "Name"        = local.tg_name
    "Environment" = local.environment
  }
}

resource "aws_network_interface" "tg_if1" {
  depends_on = [
    aws_vpc.vpc,
    aws_subnet.b,
    aws_instance.tg
  ]
  private_ip        = var.tg_if1_private_ip
  private_ips       = [var.tg_if1_private_ip]
  security_groups   = [aws_security_group.security_group.id]
  source_dest_check = var.tg_source_dest_check
  subnet_id         = aws_subnet.b.id

  attachment {
    instance     = aws_instance.tg.id
    device_index = 1
  }

  tags = {
    "Environment" = local.environment
  }
}

resource "aws_network_interface" "tg_if2" {
  depends_on = [
    aws_vpc.vpc,
    aws_subnet.d,
    aws_instance.tg
  ]
  private_ip        = var.tg_if2_private_ip
  private_ips       = [var.tg_if2_private_ip]
  security_groups   = [aws_security_group.security_group.id]
  source_dest_check = var.tg_source_dest_check
  subnet_id         = aws_subnet.d.id

  attachment {
    instance     = aws_instance.tg.id
    device_index = 2
  }

  tags = {
    "Environment" = local.environment
  }
}

data "aws_network_interface" "tg_if1" {
  id = aws_network_interface.tg_if1.id
}

data "aws_network_interface" "tg_if2" {
  id = aws_network_interface.tg_if2.id
}

resource "aws_route" "route_tg_if1" {
  depends_on = [
    aws_vpc.vpc,
    aws_instance.sut1
  ]
  destination_cidr_block = var.destination_cidr_block_tg_if1
  network_interface_id   = aws_instance.tg.primary_network_interface_id
  route_table_id         = aws_vpc.vpc.main_route_table_id
}

resource "aws_route" "route_tg_if2" {
  depends_on = [
    aws_vpc.vpc,
    aws_instance.sut1
  ]
  destination_cidr_block = var.destination_cidr_block_tg_if2
  network_interface_id   = aws_instance.tg.primary_network_interface_id
  route_table_id         = aws_vpc.vpc.main_route_table_id
}

resource "aws_instance" "sut1" {
  depends_on = [
    aws_vpc.vpc,
    aws_placement_group.placement_group,
    aws_security_group.security_group.id,
    aws_instance.tg
  ]
  ami                                  = var.sut1_ami
  availability_zone                    = local.availability_zone
  associate_public_ip_address          = var.sut1_associate_public_ip_address
  instance_initiated_shutdown_behavior = var.sut1_instance_initiated_shutdown_behavior
  instance_type                        = var.sut1_instance_type
  key_name                             = aws_key_pair.key_pair.key_name
  placement_group                      = aws_placement_group.placement_group.id
  private_ip                           = var.sut1_private_ip
  source_dest_check                    = var.sut1_source_dest_check
  subnet_id                            = aws_subnet.subnet.id
  vpc_security_group_ids               = [aws_security_group.security_group.id]
  # host_id                            = "2"

  root_block_device {
    delete_on_termination = true
    volume_size           = 50
  }

  tags = {
    "Environment" = local.environment
  }
}

resource "aws_network_interface" "sut1_if1" {
  depends_on = [
    aws_vpc.vpc,
    aws_subnet.b,
    aws_instance.sut1
  ]
  private_ip        = var.sut1_if1_private_ip
  private_ips       = [var.sut1_if1_private_ip]
  security_groups   = [aws_security_group.security_group.id]
  source_dest_check = var.sut1_source_dest_check
  subnet_id         = aws_subnet.b.id

  attachment {
    instance     = aws_instance.sut1.id
    device_index = 1
  }

  tags = {
    "Environment" = local.environment
  }
}

resource "aws_network_interface" "sut1_if2" {
  depends_on = [
    aws_vpc.vpc,
    aws_subnet.d,
    aws_instance.sut1
  ]
  private_ip        = var.sut1_if2_private_ip
  private_ips       = [var.sut1_if2_private_ip]
  security_groups   = [aws_security_group.security_group.id]
  source_dest_check = var.sut1_source_dest_check
  subnet_id         = aws_subnet.d.id

  attachment {
    instance     = aws_instance.sut1.id
    device_index = 2
  }

  tags = {
    "Environment" = local.environment
  }
}

data "aws_network_interface" "sut1_if1" {
  id = aws_network_interface.sut1_if1.id
}

data "aws_network_interface" "sut1_if2" {
  id = aws_network_interface.sut1_if2.id
}

resource "null_resource" "deploy_tg" {
  depends_on = [
    aws_instance.tg,
    aws_network_interface.tg_if1,
    aws_network_interface.tg_if2,
    aws_instance.sut1,
    aws_network_interface.sut1_if1,
    aws_network_interface.sut1_if2
  ]

  connection {
    user        = "ubuntu"
    host        = aws_instance.tg.public_ip
    private_key = tls_private_key.private_key.private_key_pem
  }

  provisioner "remote-exec" {
    inline = var.first_run_commands
  }
}

resource "null_resource" "deploy_sut1" {
  depends_on = [
    aws_instance.tg,
    aws_network_interface.tg_if1,
    aws_network_interface.tg_if2,
    aws_instance.sut1,
    aws_network_interface.sut1_if1,
    aws_network_interface.sut1_if2
  ]

  connection {
    user        = "ubuntu"
    host        = aws_instance.sut1.public_ip
    private_key = tls_private_key.private_key.private_key_pem
  }

  provisioner "remote-exec" {
    inline = var.first_run_commands
  }
}

resource "null_resource" "deploy_topology" {
  depends_on = [
    aws_instance.tg,
    aws_instance.sut1
  ]

  provisioner "ansible" {
    plays {
      playbook {
        file_path = var.ansible_topology_path
      }
      hosts = ["local"]
      extra_vars = {
        ansible_python_interpreter = local.ansible_python_executable
        testbed_name               = local.testbed_name
        cloud_topology             = local.topology_name
        tg_if1_mac                 = data.aws_network_interface.tg_if1.mac_address
        tg_if2_mac                 = data.aws_network_interface.tg_if2.mac_address
        dut1_if1_mac               = data.aws_network_interface.sut1_if1.mac_address
        dut1_if2_mac               = data.aws_network_interface.sut1_if2.mac_address
        tg_public_ip               = aws_instance.tg.public_ip
        dut1_public_ip             = aws_instance.sut1.public_ip
        public_ip_list             = "${aws_instance.tg.public_ip},${aws_instance.sut1.public_ip}"
      }
    }
  }
}