locals {
   availability_zone     = "eu-central-1a"
   name                  = "csit-vpc"
   environment           = "csit-vpc-environment"
   key_pair_key_name     = "csit-key-name"
   placement_group_name  = "csit-pg"
   resources_name_prefix = "csit_2n_aws_c5n"
   security_group_name   = "csit-sg"
   testbed_name          = "testbed1"
   tg_name               = "${var.resources_name_prefix}_${var.testbed_name}-tg"
   sut1_name             = "${var.resources_name_prefix}_${var.testbed_name}-sut1"
}

module "vpc" {
  source                   = "../terraform-aws-vpc"
  security_group_name      = local.security_group_name
  subnet_availability_zone = local.availability_zone
  tags_name                = local.name
  tags_environment         = local.environment
}

module "subnet_b" {
  source                   = "../terraform-aws-subnet"
  subnet_cidr_block        = "192.168.10.0/24"
  subnet_ipv6_cidr_block   = cidrsubnet(module.vpc.vpc_ipv6_cidr_block, 8, 2)
  subnet_availability_zone = local.availability_zone
  tags_name                = local.name
  tags_environment         = local.environment
  subnet_vpc_id            = module.vpc.vpc_id
}

module "subnet_d" {
  source                   = "../terraform-aws-subnet"
  subnet_cidr_block        = "192.168.20.0/24"
  subnet_ipv6_cidr_block   = cidrsubnet(module.vpc.vpc_ipv6_cidr_block, 8, 4)
  subnet_availability_zone = local.availability_zone
  tags_name                = local.name
  tags_environment         = local.environment
  subnet_vpc_id            = module.vpc.vpc_id
}

resource "tls_private_key" "private_key" {
  algorithm   = var.private_key_algorithm
  ecdsa_curve = var.private_key_ecdsa_curve
  rsa_bits    = var.private_key_rsa_bits
}

resource "aws_key_pair" "key_pair" {
  depends_on        = [
    tls_private_key.private_key
  ]
  key_name   = local.key_pair_key_name
  public_key = "${tls_private_key.private_key.public_key_openssh}"
}

resource "aws_placement_group" "placement_group" {
  name     = local.placement_group_name
  strategy = var.placement_group_strategy
}

resource "aws_instance" "tg" {
  depends_on                           = [
    module.vpc,
    aws_placement_group.placement_group
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
  subnet_id                            = module.vpc.vpc_subnet_id
  vpc_security_group_ids               = [module.vpc.vpc_security_group_id]
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
  depends_on        = [
    module.subnet_b,
    aws_instance.tg
  ]
  private_ip        = var.tg_if1_private_ip
  private_ips       = [var.tg_if1_private_ip]
  security_groups   = [module.vpc.vpc_security_group_id]
  source_dest_check = var.tg_source_dest_check
  subnet_id         = module.subnet_b.subnet_id

  attachment {
    instance     = aws_instance.tg.id
    device_index = 1
  }

  tags = {
    "Environment" = local.environment
  }
}

resource "aws_network_interface" "tg_if2" {
  depends_on        = [
    module.subnet_d,
    aws_instance.tg
  ]
  private_ip        = var.tg_if2_ip
  private_ips       = [var.tg_if2_ip]
  security_groups   = [module.vpc.vpc_security_group_id]
  source_dest_check = var.tg_source_dest_check
  subnet_id         = module.subnet_d.subnet_id

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

resource "aws_route" "dummy_tg_route_interface_0" {
  depends_on             = [
    aws_instance.tg
  ]
  destination_cidr_block = var.destination_cidr_block_tg_if1
  network_interface_id   = aws_instance.tg.primary_network_interface_id
  route_table_id         = module.vpc.vpc_main_route_table_id
}

resource "aws_route" "traffic_tg_route_interface_1" {
  depends_on             = [
    aws_instance.tg
  ]
  destination_cidr_block = var.trex_dummy_cidr_port_1
  network_interface_id   = aws_instance.tg.primary_network_interface_id
  route_table_id         = module.vpc.vpc_main_route_table_id
}

resource "aws_instance" "sut1" {
  depends_on                           = [
    module.vpc,
    aws_placement_group.placement_group
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
  subnet_id                            = module.vpc.vpc_subnet_id
  vpc_security_group_ids               = [module.vpc.vpc_security_group_id]
  # host_id                            = "2"

  root_block_device {
    delete_on_termination = true
    volume_size           = 50
  }

  tags = {
    "Name"        = local.sut1_name
    "Environment" = local.environment
  }
}

resource "aws_network_interface" "sut1_if1" {
  depends_on        = [
    module.subnet_b,
    aws_instance.sut1
  ]
  private_ip        = var.sut1_if1_ip
  private_ips       = [var.sut1_if1_ip]
  security_groups   = [module.vpc.vpc_security_group_id]
  source_dest_check = var.sut1_source_dest_check
  subnet_id         = module.subnet_b.subnet_id

  attachment {
    instance     = aws_instance.sut1.id
    device_index = 1
  }

  tags = {
    "Environment" = local.environment
  }
}

resource "aws_network_interface" "sut1_if2" {
  depends_on        = [
    module.subnet_d,
    aws_instance.sut1
  ]
  private_ip        = var.sut1_if2_private_ip
  private_ips       = [var.sut1_if2_private_ip]
  security_groups   = [module.vpc.vpc_security_group_id]
  source_dest_check = var.sut1_source_dest_check
  subnet_id         = module.subnet_d.subnet_id

  attachment {
    instance     = aws_instance.sut1.id
    device_index = 2
  }

  tags = {
    "Environment" = var.environment_name
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
        ansible_python_interpreter = var.ansible_python_executable
        testbed_name               = var.testbed_name
        cloud_topology             = var.topology_name
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