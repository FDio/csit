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
  topology_name             = "1n-c6gn"
  tg_name                   = "${var.resource_prefix}-${var.testbed_name}-tg"
  sut1_name                 = "${var.resource_prefix}-${var.testbed_name}-sut1"
}

# Create VPC
module "vpc" {
  source                   = "../terraform-aws-vpc"
  security_group_name      = local.security_group_name
  subnet_availability_zone = local.availability_zone
  tags_name                = local.name
  tags_environment         = local.environment
}

# Create Subnet
module "subnet_b" {
  source                   = "../terraform-aws-subnet"
  subnet_cidr_block        = "192.168.10.0/24"
  subnet_ipv6_cidr_block   = cidrsubnet(module.vpc.vpc_ipv6_cidr_block, 8, 2)
  subnet_availability_zone = local.availability_zone
  tags_name                = local.name
  tags_environment         = local.environment
  subnet_vpc_id            = module.vpc.vpc_id
}

# Create Private Key
module "private_key" {
  source  = "pmikus/private-key/tls"
  version = "4.0.4"

  private_key_algorithm = var.private_key_algorithm
}

# Create Key Pair
module "key_pair" {
  source  = "pmikus/key-pair/aws"
  version = "5.7.0"

  key_pair_key_name   = local.key_pair_key_name
  key_pair_public_key = module.private_key.public_key_openssh

  key_pair_tags = {
    "Environment" = local.environment
  }
}

# Create Placement Group
resource "aws_placement_group" "placement_group" {
  name     = local.placement_group_name
  strategy = var.placement_group_strategy
}

# Create Instance
resource "aws_instance" "tg" {
  depends_on = [
    module.vpc,
    aws_placement_group.placement_group
  ]
  ami                                  = var.tg_ami
  availability_zone                    = local.availability_zone
  associate_public_ip_address          = var.tg_associate_public_ip_address
  instance_initiated_shutdown_behavior = var.tg_instance_initiated_shutdown_behavior
  instance_type                        = var.tg_instance_type
  key_name                             = module.key_pair.key_pair_key_name
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
  depends_on = [
    module.subnet_b,
    aws_instance.tg
  ]
  private_ips       = [var.tg_if1_private_ip]
  security_groups   = [module.vpc.vpc_security_group_id]
  source_dest_check = var.tg_source_dest_check
  subnet_id         = module.subnet_b.subnet_id

  attachment {
    instance     = aws_instance.tg.id
    device_index = 1
  }

  tags = {
    "Name"        = local.tg_name
    "Environment" = local.environment
  }
}

resource "aws_network_interface" "tg_if2" {
  depends_on = [
    module.subnet_b,
    aws_instance.tg
  ]
  private_ips       = [var.tg_if2_private_ip]
  security_groups   = [module.vpc.vpc_security_group_id]
  source_dest_check = var.tg_source_dest_check
  subnet_id         = module.subnet_b.subnet_id

  attachment {
    instance     = aws_instance.tg.id
    device_index = 2
  }

  tags = {
    "Name"        = local.tg_name
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
    aws_instance.tg
  ]
  destination_cidr_block = var.destination_cidr_block_tg_if1
  network_interface_id   = aws_instance.tg.primary_network_interface_id
  route_table_id         = module.vpc.vpc_main_route_table_id
}

resource "aws_route" "route_tg_if2" {
  depends_on = [
    aws_instance.tg
  ]
  destination_cidr_block = var.destination_cidr_block_tg_if2
  network_interface_id   = aws_instance.tg.primary_network_interface_id
  route_table_id         = module.vpc.vpc_main_route_table_id
}

resource "null_resource" "deploy_tg" {
  depends_on = [
    aws_instance.tg,
    aws_network_interface.tg_if1,
    aws_network_interface.tg_if2
  ]

  connection {
    user        = "ubuntu"
    host        = aws_instance.tg.public_ip
    private_key = module.private_key.private_key_pem
  }

  provisioner "remote-exec" {
    inline = var.first_run_commands
  }
}


resource "null_resource" "deploy_topology" {
  depends_on = [
    aws_instance.tg
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
        tg_public_ip               = aws_instance.tg.public_ip
        public_ip_list             = "${aws_instance.tg.public_ip}"
      }
    }
  }
}